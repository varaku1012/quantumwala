#!/usr/bin/env python3
"""
Memory Management System - Short-term, long-term, and episodic memory
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pickle
import sqlite3

@dataclass
class Memory:
    """Individual memory unit"""
    id: str
    type: str  # task, decision, result, error
    content: Any
    metadata: Dict
    timestamp: float
    relevance_score: float = 1.0

class ShortTermMemory:
    """In-context window memory for current workflow"""
    
    def __init__(self, max_items: int = 50):
        self.memory = {}
        self.max_items = max_items
        self.access_count = {}
        
    def store(self, key: str, value: Any, metadata: Dict = None):
        """Store in short-term memory"""
        self.memory[key] = {
            'value': value,
            'metadata': metadata or {},
            'timestamp': time.time(),
            'access_count': 0
        }
        
        # Evict least recently used if over limit
        if len(self.memory) > self.max_items:
            self._evict_lru()
            
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from short-term memory"""
        if key in self.memory:
            self.memory[key]['access_count'] += 1
            self.memory[key]['last_accessed'] = time.time()
            return self.memory[key]['value']
        return None
        
    def get_context_window(self, max_age_minutes: int = 30) -> Dict:
        """Get recent memories for context window"""
        cutoff_time = time.time() - (max_age_minutes * 60)
        recent = {}
        
        for key, item in self.memory.items():
            if item['timestamp'] > cutoff_time:
                recent[key] = {
                    'value': item['value'],
                    'age_minutes': (time.time() - item['timestamp']) / 60
                }
                
        return recent
        
    def _evict_lru(self):
        """Evict least recently used item"""
        lru_key = min(self.memory.keys(), 
                     key=lambda k: self.memory[k].get('last_accessed', self.memory[k]['timestamp']))
        del self.memory[lru_key]

class LongTermMemory:
    """Persistent memory using SQLite for efficiency"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path('.claude/memory/long_term.db')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    content TEXT,
                    metadata TEXT,
                    embedding TEXT,
                    timestamp REAL,
                    relevance_score REAL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_type ON memories(type)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
            ''')
            
    def store(self, memory: Memory):
        """Store memory in long-term storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO memories 
                (id, type, content, metadata, timestamp, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                memory.id,
                memory.type,
                json.dumps(memory.content),
                json.dumps(memory.metadata),
                memory.timestamp,
                memory.relevance_score
            ))
            
    def retrieve(self, memory_id: str) -> Optional[Memory]:
        """Retrieve specific memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                'SELECT * FROM memories WHERE id = ?', (memory_id,)
            ).fetchone()
            
            if row:
                # Update access count
                conn.execute('''
                    UPDATE memories 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                ''', (time.time(), memory_id))
                
                return Memory(
                    id=row['id'],
                    type=row['type'],
                    content=json.loads(row['content']),
                    metadata=json.loads(row['metadata']),
                    timestamp=row['timestamp'],
                    relevance_score=row['relevance_score']
                )
        return None
        
    def search(self, query: Dict, limit: int = 10) -> List[Memory]:
        """Search memories based on criteria"""
        conditions = []
        params = []
        
        if 'type' in query:
            conditions.append('type = ?')
            params.append(query['type'])
            
        if 'min_relevance' in query:
            conditions.append('relevance_score >= ?')
            params.append(query['min_relevance'])
            
        if 'max_age_days' in query:
            cutoff = time.time() - (query['max_age_days'] * 86400)
            conditions.append('timestamp > ?')
            params.append(cutoff)
            
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(f'''
                SELECT * FROM memories 
                WHERE {where_clause}
                ORDER BY relevance_score DESC, timestamp DESC
                LIMIT ?
            ''', params + [limit]).fetchall()
            
            return [
                Memory(
                    id=row['id'],
                    type=row['type'],
                    content=json.loads(row['content']),
                    metadata=json.loads(row['metadata']),
                    timestamp=row['timestamp'],
                    relevance_score=row['relevance_score']
                )
                for row in rows
            ]

class EpisodicMemory:
    """Few-shot examples and patterns"""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path('.claude/memory/episodic')
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.episodes = self._load_episodes()
        
    def _load_episodes(self) -> Dict[str, List[Dict]]:
        """Load existing episodes from disk"""
        episodes = {}
        
        for file in self.storage_path.glob('*.json'):
            task_type = file.stem
            with open(file, 'r') as f:
                episodes[task_type] = json.load(f)
                
        return episodes
        
    def add_episode(self, task_type: str, example: Dict):
        """Add a new episode example"""
        if task_type not in self.episodes:
            self.episodes[task_type] = []
            
        # Keep only best examples (by success and recency)
        self.episodes[task_type].append({
            'example': example,
            'timestamp': time.time(),
            'success': example.get('success', True)
        })
        
        # Keep top 10 examples
        self.episodes[task_type] = sorted(
            self.episodes[task_type],
            key=lambda x: (x['success'], x['timestamp']),
            reverse=True
        )[:10]
        
        # Save to disk
        self._save_episodes(task_type)
        
    def get_examples(self, task_type: str, count: int = 3) -> List[Dict]:
        """Get few-shot examples for task type"""
        if task_type not in self.episodes:
            # Try to find similar task types
            similar = [t for t in self.episodes.keys() if task_type in t or t in task_type]
            if similar:
                task_type = similar[0]
            else:
                return []
                
        examples = self.episodes.get(task_type, [])
        return [e['example'] for e in examples[:count]]
        
    def _save_episodes(self, task_type: str):
        """Save episodes to disk"""
        file_path = self.storage_path / f"{task_type}.json"
        with open(file_path, 'w') as f:
            json.dump(self.episodes[task_type], f, indent=2)

class MemoryManager:
    """Unified memory management interface"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.memory_dir = self.project_root / '.claude' / 'memory'
        
        # Initialize memory systems
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(self.memory_dir / 'long_term.db')
        self.episodic = EpisodicMemory(self.memory_dir / 'episodic')
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
        
    def store_execution(self, task_id: str, agent: str, result: Dict):
        """Store task execution result in all appropriate memories"""
        # Short-term for current workflow
        self.short_term.store(
            key=f"{task_id}_result",
            value=self._compress_result(result),
            metadata={'agent': agent, 'task_id': task_id}
        )
        
        # Long-term for future reference
        memory = Memory(
            id=f"{task_id}_{int(time.time())}",
            type='task_result',
            content=result,
            metadata={
                'task_id': task_id,
                'agent': agent,
                'success': result.get('success', False)
            },
            timestamp=time.time(),
            relevance_score=self._calculate_relevance(result)
        )
        self.long_term.store(memory)
        
        # Episodic if it's a good example
        if result.get('success') and result.get('quality_score', 0) > 0.8:
            self.episodic.add_episode(
                task_type=result.get('task_type', 'general'),
                example={
                    'task': result.get('task'),
                    'approach': result.get('approach'),
                    'output': result.get('output')
                }
            )
            
    def get_relevant_memories(self, task: Dict, limit: int = 5) -> Dict:
        """Get memories relevant to current task"""
        relevant = {
            'short_term': {},
            'long_term': [],
            'episodic': []
        }
        
        # Recent short-term memories
        recent = self.short_term.get_context_window(max_age_minutes=30)
        task_type = task.get('type', 'general')
        
        # Filter relevant short-term
        for key, memory in recent.items():
            if task_type in key or any(keyword in str(memory) for keyword in task.get('keywords', [])):
                relevant['short_term'][key] = memory
                
        # Search long-term memories
        relevant['long_term'] = self.long_term.search({
            'type': 'task_result',
            'max_age_days': 30,
            'min_relevance': 0.7
        }, limit=limit)
        
        # Get episodic examples
        relevant['episodic'] = self.episodic.get_examples(task_type, count=3)
        
        return relevant
        
    def _compress_result(self, result: Dict) -> Dict:
        """Compress result for short-term storage"""
        compressed = {
            'success': result.get('success'),
            'summary': result.get('output', '')[:200],  # First 200 chars
            'key_points': result.get('key_points', [])
        }
        return compressed
        
    def _calculate_relevance(self, result: Dict) -> float:
        """Calculate relevance score for memory"""
        score = 0.5  # Base score
        
        if result.get('success'):
            score += 0.2
            
        if result.get('quality_score'):
            score += result['quality_score'] * 0.3
            
        return min(score, 1.0)
        
    def cleanup_old_memories(self, days: int = 90):
        """Clean up old memories"""
        cutoff = time.time() - (days * 86400)
        
        with sqlite3.connect(self.long_term.db_path) as conn:
            conn.execute('''
                DELETE FROM memories 
                WHERE timestamp < ? AND relevance_score < 0.8
            ''', (cutoff,))
            
    def get_memory_stats(self) -> Dict:
        """Get memory system statistics"""
        with sqlite3.connect(self.long_term.db_path) as conn:
            total_memories = conn.execute('SELECT COUNT(*) FROM memories').fetchone()[0]
            
        return {
            'short_term_count': len(self.short_term.memory),
            'long_term_count': total_memories,
            'episodic_types': list(self.episodic.episodes.keys()),
            'episodic_count': sum(len(eps) for eps in self.episodic.episodes.values())
        }

# Example usage
if __name__ == "__main__":
    manager = MemoryManager()
    
    # Store execution result
    manager.store_execution(
        task_id='task-123',
        agent='developer',
        result={
            'success': True,
            'output': 'Implemented authentication',
            'quality_score': 0.9,
            'task_type': 'implementation'
        }
    )
    
    # Get relevant memories
    memories = manager.get_relevant_memories({
        'type': 'implementation',
        'keywords': ['auth', 'login']
    })
    
    print("Memory stats:", manager.get_memory_stats())
    print("Relevant memories:", len(memories['long_term']))