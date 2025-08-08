# Enhancement Implementation Guide
## Step-by-Step Instructions for Fixing the Context Engineering System

---

## Quick Start Fix Commands

```bash
# Week 1: Critical Fixes
python .claude/scripts/fix_agent_bridge.py
python .claude/scripts/add_persistence.py
python .claude/scripts/fix_token_counting.py

# Week 2: Security & Integration
python .claude/scripts/fix_security.py
python .claude/scripts/wire_components.py

# Week 3: Testing & Monitoring
python .claude/scripts/run_tests.py
python .claude/scripts/start_monitoring.py
```

---

## Week 1: Critical Foundation Fixes

### Day 1-2: Fix Agent Tool Bridge Connection

#### Step 1: Update real_executor.py
```python
# File: .claude/scripts/real_executor.py
# Line: ~10-20 (in __init__ method)

# ADD THESE IMPORTS AT THE TOP
from agent_tool_bridge import AgentToolBridge, TaskRequest
from context_engine import ContextEngine
from memory_manager import MemoryManager

# MODIFY THE __init__ METHOD
class RealClaudeExecutor:
    def __init__(self, project_root=None):
        self.project_root = project_root or Path.cwd()
        
        # ADD THESE LINES
        self.bridge = AgentToolBridge(self.project_root)
        self.context_engine = ContextEngine()
        self.memory_manager = MemoryManager(self.project_root)
        
        # Wire dependencies
        self.bridge.context_engine = self.context_engine
        self.bridge.memory_manager = self.memory_manager
    
    # ADD THIS NEW METHOD
    async def handle_task_delegation(self, agent: str, description: str, context: dict):
        """Handle Task tool calls from agents"""
        request = TaskRequest(
            agent=agent,
            description=description,
            context=context,
            parent_agent='system'
        )
        return await self.bridge.process_task_delegation(request)
```

#### Step 2: Update unified_workflow.py
```python
# File: .claude/scripts/unified_workflow.py
# Line: ~150-200 (in execute methods)

# REPLACE direct agent calls with bridge calls
async def _execute_phase(self, phase_name: str, agent: str, context: dict):
    # OLD CODE (REMOVE):
    # result = await self._call_agent_directly(agent, context)
    
    # NEW CODE (ADD):
    result = await self.executor.handle_task_delegation(
        agent=agent,
        description=f"Execute {phase_name} phase",
        context=context
    )
    
    # Store in memory
    self.executor.memory_manager.store_execution(
        task_id=self.current_task_id,
        agent=agent,
        result=result
    )
    
    return result
```

### Day 3-4: Add Memory Persistence

#### Step 1: Create database schema
```python
# NEW FILE: .claude/scripts/create_database.py

import sqlite3
from pathlib import Path

def create_memory_database():
    db_path = Path.cwd() / '.claude' / 'data' / 'memory.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create memories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            agent TEXT NOT NULL,
            context TEXT NOT NULL,
            result TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            duration REAL,
            tokens_used INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            parent_task TEXT,
            memory_type TEXT DEFAULT 'execution'
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task ON memories(task_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
    
    # Create episodic memories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodic_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            successful_approach TEXT NOT NULL,
            agent TEXT NOT NULL,
            context_summary TEXT,
            usage_count INTEGER DEFAULT 0,
            last_used DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database created at: {db_path}")

if __name__ == "__main__":
    create_memory_database()
```

#### Step 2: Update memory_manager.py
```python
# File: .claude/scripts/memory_manager.py
# COMPLETE REPLACEMENT

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Three-tier memory system with persistence"""
    
    def __init__(self, project_root=None):
        self.project_root = project_root or Path.cwd()
        self.db_path = self.project_root / '.claude' / 'data' / 'memory.db'
        
        # Ensure database exists
        if not self.db_path.exists():
            from create_database import create_memory_database
            create_memory_database()
        
        # Memory tiers
        self.short_term = {}  # Last 30 minutes
        self.long_term = None  # Database connection
        self.episodic = []  # Cached successful patterns
        
        # Connect to database
        self._connect_db()
        
        # Load episodic memories
        self._load_episodic_memories()
    
    def _connect_db(self):
        """Connect to SQLite database"""
        try:
            self.long_term = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # Allow multi-threading
            )
            self.long_term.row_factory = sqlite3.Row
            logger.info(f"Connected to memory database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def store_execution(self, task_id: str, agent: str, result: Any) -> None:
        """Store execution result in memory"""
        # Store in short-term
        self.short_term[task_id] = {
            'agent': agent,
            'result': result,
            'timestamp': datetime.now()
        }
        
        # Clean old short-term memories
        self._cleanup_short_term()
        
        # Store in long-term (database)
        try:
            cursor = self.long_term.cursor()
            cursor.execute('''
                INSERT INTO memories 
                (task_id, agent, context, result, success, duration, tokens_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                agent,
                json.dumps(result.get('context', {})),
                json.dumps(result.get('output', {})),
                result.get('success', False),
                result.get('duration', 0),
                result.get('tokens_used', 0)
            ))
            self.long_term.commit()
            logger.info(f"Stored memory for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
    
    def get_relevant_memories(self, task: Dict, limit: int = 5) -> List[Dict]:
        """Get relevant memories for a task"""
        memories = []
        
        # Check short-term first
        for task_id, memory in self.short_term.items():
            if self._is_relevant(memory, task):
                memories.append(memory)
        
        # Query long-term
        try:
            cursor = self.long_term.cursor()
            
            # Get similar successful executions
            cursor.execute('''
                SELECT * FROM memories 
                WHERE success = 1 
                AND agent = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (task.get('agent', ''), limit))
            
            for row in cursor.fetchall():
                memories.append({
                    'task_id': row['task_id'],
                    'agent': row['agent'],
                    'context': json.loads(row['context']),
                    'result': json.loads(row['result']),
                    'timestamp': row['timestamp']
                })
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
        
        return memories[:limit]
    
    def get_episodic_example(self, task_type: str) -> Optional[Dict]:
        """Get successful example for task type"""
        for episode in self.episodic:
            if episode['pattern'] == task_type:
                # Update usage count
                self._update_episode_usage(episode['id'])
                return episode
        return None
    
    def _cleanup_short_term(self):
        """Remove memories older than 30 minutes"""
        cutoff = datetime.now() - timedelta(minutes=30)
        self.short_term = {
            k: v for k, v in self.short_term.items()
            if v['timestamp'] > cutoff
        }
    
    def _is_relevant(self, memory: Dict, task: Dict) -> bool:
        """Check if memory is relevant to task"""
        # Simple relevance check - can be enhanced
        return memory.get('agent') == task.get('agent')
    
    def _load_episodic_memories(self):
        """Load successful patterns from database"""
        try:
            cursor = self.long_term.cursor()
            cursor.execute('''
                SELECT * FROM episodic_memories 
                ORDER BY usage_count DESC
                LIMIT 20
            ''')
            
            self.episodic = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Loaded {len(self.episodic)} episodic memories")
        except Exception as e:
            logger.error(f"Failed to load episodic memories: {e}")
    
    def _update_episode_usage(self, episode_id: int):
        """Update usage count for episodic memory"""
        try:
            cursor = self.long_term.cursor()
            cursor.execute('''
                UPDATE episodic_memories 
                SET usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (episode_id,))
            self.long_term.commit()
        except Exception as e:
            logger.error(f"Failed to update episode usage: {e}")
    
    def cleanup_old_memories(self, days: int = 30):
        """Clean up old memories"""
        try:
            cursor = self.long_term.cursor()
            cursor.execute('''
                DELETE FROM memories 
                WHERE timestamp < datetime('now', '-? days')
            ''', (days,))
            
            deleted = cursor.rowcount
            self.long_term.commit()
            logger.info(f"Cleaned up {deleted} old memories")
            
            return deleted
        except Exception as e:
            logger.error(f"Failed to cleanup memories: {e}")
            return 0
```

### Day 5: Fix Token Counting

#### Step 1: Install tiktoken
```bash
pip install tiktoken
```

#### Step 2: Update context_engine.py
```python
# File: .claude/scripts/context_engine.py
# Lines: ~50-150 (ContextCompressor class)

import tiktoken
from functools import lru_cache

class ContextCompressor:
    """Compress context to fit token limits using REAL token counting"""
    
    def __init__(self):
        # Use Claude's tokenizer
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self._token_cache = {}  # Cache for performance
        
    @lru_cache(maxsize=1000)
    def count_tokens(self, text: str) -> int:
        """Count actual tokens using tiktoken"""
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            logger.error(f"Token counting failed: {e}")
            # Fallback to rough estimate
            return len(text) // 4
    
    def compress(self, text: str, max_tokens: int = 4000) -> str:
        """Compress text to fit within token limit"""
        current_tokens = self.count_tokens(text)
        
        if current_tokens <= max_tokens:
            return text
        
        # Progressive compression strategies
        compressed = text
        
        # Level 1: Remove extra whitespace
        if current_tokens > max_tokens:
            compressed = self._compress_whitespace(compressed)
            current_tokens = self.count_tokens(compressed)
        
        # Level 2: Remove comments (but preserve docstrings)
        if current_tokens > max_tokens:
            compressed = self._remove_comments(compressed)
            current_tokens = self.count_tokens(compressed)
        
        # Level 3: Summarize long sections
        if current_tokens > max_tokens:
            compressed = self._summarize_sections(compressed, max_tokens)
            current_tokens = self.count_tokens(compressed)
        
        # Level 4: Truncate with ellipsis
        if current_tokens > max_tokens:
            compressed = self._truncate_to_fit(compressed, max_tokens)
        
        return compressed
    
    def _compress_whitespace(self, text: str) -> str:
        """Remove unnecessary whitespace"""
        import re
        # Remove multiple blank lines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        # Remove trailing whitespace
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
        return text
    
    def _remove_comments(self, text: str) -> str:
        """Remove comments but preserve docstrings"""
        import re
        # Remove single-line comments (but not docstrings)
        text = re.sub(r'(?<!["\']{3})#.*?$', '', text, flags=re.MULTILINE)
        return text
    
    def _summarize_sections(self, text: str, max_tokens: int) -> str:
        """Summarize long sections to fit"""
        # This would ideally use an AI model
        # For now, just extract key lines
        lines = text.split('\n')
        
        # Prioritize lines with keywords
        priority_keywords = ['def ', 'class ', 'async ', 'return ', 'raise ']
        important_lines = []
        other_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in priority_keywords):
                important_lines.append(line)
            else:
                other_lines.append(line)
        
        # Build result prioritizing important lines
        result = '\n'.join(important_lines)
        
        # Add other lines until we hit limit
        for line in other_lines:
            test_result = result + '\n' + line
            if self.count_tokens(test_result) > max_tokens * 0.9:
                break
            result = test_result
        
        return result
    
    def _truncate_to_fit(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit token limit"""
        # Binary search for right truncation point
        left, right = 0, len(text)
        result = text
        
        while left < right:
            mid = (left + right) // 2
            truncated = text[:mid] + "\n... [truncated]"
            
            if self.count_tokens(truncated) <= max_tokens:
                result = truncated
                left = mid + 1
            else:
                right = mid
        
        return result
```

---

## Week 2: Security & Integration

### Day 6-7: Fix Security Vulnerabilities

#### Step 1: Create secure command executor
```python
# NEW FILE: .claude/scripts/secure_executor.py

import shlex
import subprocess
from pathlib import Path
from typing import List, Optional
import re

class SecureExecutor:
    """Secure command execution with validation"""
    
    ALLOWED_COMMANDS = [
        'python', 'pip', 'git', 'npm', 'node',
        'pytest', 'black', 'flake8', 'mypy'
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
    
    def validate_command(self, command: str, args: List[str]) -> bool:
        """Validate command is safe to execute"""
        # Check command is allowed
        if command not in self.ALLOWED_COMMANDS:
            raise ValueError(f"Command '{command}' not allowed")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'\.\./',  # Path traversal
            r';\s*rm',  # Command chaining with rm
            r'\|\s*sh',  # Piping to shell
            r'`.*`',  # Command substitution
            r'\$\(',  # Command substitution
        ]
        
        full_command = f"{command} {' '.join(args)}"
        for pattern in dangerous_patterns:
            if re.search(pattern, full_command):
                raise ValueError(f"Dangerous pattern detected: {pattern}")
        
        return True
    
    def validate_path(self, user_path: str) -> Path:
        """Validate and resolve path safely"""
        # Convert to Path object
        requested = Path(user_path)
        
        # If relative, make it relative to project root
        if not requested.is_absolute():
            requested = self.project_root / requested
        
        # Resolve to absolute path
        resolved = requested.resolve()
        
        # Ensure it's within project root
        try:
            resolved.relative_to(self.project_root)
        except ValueError:
            raise ValueError(f"Path '{user_path}' is outside project root")
        
        return resolved
    
    def execute(self, command: str, args: List[str], 
                timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute command safely"""
        # Validate command
        self.validate_command(command, args)
        
        # Quote arguments safely
        safe_args = [shlex.quote(arg) for arg in args]
        
        # Build command list (no shell=True!)
        cmd_list = [command] + safe_args
        
        try:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,  # NEVER use shell=True
                cwd=self.project_root
            )
            return result
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}")
```

#### Step 2: Update deprecated_commands.py
```python
# File: .claude/scripts/deprecated_commands.py
# REPLACE the execute_command function

from secure_executor import SecureExecutor

class DeprecatedCommandHandler:
    def __init__(self, project_root):
        self.project_root = project_root
        self.executor = SecureExecutor(project_root)
    
    def execute_command(self, command_name: str, args: List[str]):
        """Execute deprecated command securely"""
        # Map command to script
        script_map = {
            'spec-create-old': 'spec_manager.py',
            'spec-requirements-old': 'spec_manager.py',
            # ... other mappings
        }
        
        if command_name not in script_map:
            raise ValueError(f"Unknown command: {command_name}")
        
        script_name = script_map[command_name]
        script_path = self.executor.validate_path(
            f'.claude/scripts/{script_name}'
        )
        
        # Execute safely
        return self.executor.execute('python', [str(script_path)] + args)
```

### Day 8-9: Wire Components Together

#### Step 1: Create integration orchestrator
```python
# NEW FILE: .claude/scripts/integrated_system.py

from pathlib import Path
import asyncio
from typing import Dict, Any

from agent_tool_bridge import AgentToolBridge
from context_engine import ContextEngine
from memory_manager import MemoryManager
from real_executor import RealClaudeExecutor
from workflow_monitor import WorkflowMonitor
from event_bus import EventBus

class IntegratedSystem:
    """Fully integrated Context Engineering System"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        
        # Initialize components
        self.context_engine = ContextEngine()
        self.memory_manager = MemoryManager(self.project_root)
        self.tool_bridge = AgentToolBridge(self.project_root)
        self.executor = RealClaudeExecutor(self.project_root)
        self.monitor = WorkflowMonitor('system')
        self.event_bus = EventBus()
        
        # Wire dependencies
        self._wire_components()
        
        # Register event handlers
        self._register_handlers()
    
    def _wire_components(self):
        """Wire all components together"""
        # Bridge needs context and memory
        self.tool_bridge.context_engine = self.context_engine
        self.tool_bridge.memory_manager = self.memory_manager
        
        # Executor needs bridge
        self.executor.bridge = self.tool_bridge
        
        # Context engine needs memory for relevant memories
        self.context_engine.memory_manager = self.memory_manager
        
        print("✅ All components wired successfully")
    
    def _register_handlers(self):
        """Register event handlers"""
        # Memory events
        self.event_bus.subscribe(
            'task.completed',
            self.memory_manager.store_execution
        )
        
        # Monitoring events
        self.event_bus.subscribe(
            'task.started',
            self.monitor.log_task_start
        )
        self.event_bus.subscribe(
            'task.completed',
            self.monitor.log_task_complete
        )
        
        # Context events
        self.event_bus.subscribe(
            'context.requested',
            self.context_engine.prepare_context
        )
        
        print("✅ Event handlers registered")
    
    async def execute_workflow(self, description: str, 
                                spec_name: str) -> Dict[str, Any]:
        """Execute a complete workflow"""
        workflow_id = f"workflow_{spec_name}_{datetime.now().timestamp()}"
        
        # Start monitoring
        monitoring_task = asyncio.create_task(
            self.monitor.start_monitoring()
        )
        
        try:
            # Publish workflow start event
            await self.event_bus.publish({
                'type': 'workflow.started',
                'workflow_id': workflow_id,
                'description': description
            })
            
            # Execute through unified workflow
            from unified_workflow import UnifiedWorkflow
            workflow = UnifiedWorkflow(
                project_root=self.project_root,
                executor=self.executor
            )
            
            result = await workflow.execute(
                description=description,
                spec_name=spec_name
            )
            
            # Publish completion event
            await self.event_bus.publish({
                'type': 'workflow.completed',
                'workflow_id': workflow_id,
                'result': result
            })
            
            return result
            
        finally:
            # Stop monitoring
            self.monitor.stop_monitoring()
            monitoring_task.cancel()
    
    def health_check(self) -> Dict[str, bool]:
        """Check system health"""
        return {
            'bridge_connected': hasattr(self.executor, 'bridge'),
            'memory_persistent': self.memory_manager.long_term is not None,
            'context_working': hasattr(self.context_engine, 'encoder'),
            'monitor_active': self.monitor.monitoring,
            'events_registered': len(self.event_bus.subscribers) > 0
        }
```

#### Step 2: Create event bus
```python
# NEW FILE: .claude/scripts/event_bus.py

import asyncio
from collections import defaultdict
from typing import Dict, List, Callable, Any
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """Asynchronous event bus for loose coupling"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing = False
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed {handler.__name__} to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type"""
        if handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            logger.info(f"Unsubscribed {handler.__name__} from {event_type}")
    
    async def publish(self, event: Dict[str, Any]):
        """Publish an event to all subscribers"""
        event_type = event.get('type')
        if not event_type:
            raise ValueError("Event must have a 'type' field")
        
        logger.info(f"Publishing event: {event_type}")
        
        # Get handlers for this event type
        handlers = self.subscribers.get(event_type, [])
        
        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(event))
            else:
                # Wrap sync functions
                tasks.append(asyncio.create_task(
                    asyncio.to_thread(handler, event)
                ))
        
        # Wait for all handlers to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Handler {handlers[i].__name__} failed: {result}"
                    )
        
        return len(tasks)
```

---

## Week 3: Testing & Validation

### Day 10-12: Create Test Suite

#### Step 1: Create test infrastructure
```python
# NEW FILE: .claude/tests/test_integration.py

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from integrated_system import IntegratedSystem
from agent_tool_bridge import TaskRequest

class TestIntegration:
    """Integration tests for the system"""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        claude_dir = Path(temp_dir) / '.claude'
        claude_dir.mkdir()
        
        # Create necessary subdirectories
        (claude_dir / 'data').mkdir()
        (claude_dir / 'scripts').mkdir()
        (claude_dir / 'specs').mkdir()
        
        yield Path(temp_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_bridge_connection(self, temp_project):
        """Test that bridge is properly connected"""
        system = IntegratedSystem(temp_project)
        
        # Check bridge is connected to executor
        assert hasattr(system.executor, 'bridge')
        assert system.executor.bridge is not None
        
        # Check bridge has context and memory
        assert hasattr(system.tool_bridge, 'context_engine')
        assert hasattr(system.tool_bridge, 'memory_manager')
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self, temp_project):
        """Test that memory persists"""
        system = IntegratedSystem(temp_project)
        
        # Store a memory
        system.memory_manager.store_execution(
            task_id='test_task',
            agent='test_agent',
            result={'success': True, 'output': 'test'}
        )
        
        # Create new system instance
        system2 = IntegratedSystem(temp_project)
        
        # Check memory persisted
        memories = system2.memory_manager.get_relevant_memories(
            {'agent': 'test_agent'}
        )
        
        assert len(memories) > 0
        assert memories[0]['task_id'] == 'test_task'
    
    @pytest.mark.asyncio
    async def test_token_counting(self, temp_project):
        """Test accurate token counting"""
        system = IntegratedSystem(temp_project)
        
        # Test various texts
        test_cases = [
            ("Hello world", 2),  # Approximate
            ("def function(): pass", 5),  # Approximate
            ("a" * 1000, 250),  # Approximate
        ]
        
        for text, expected_range in test_cases:
            tokens = system.context_engine.compressor.count_tokens(text)
            # Allow 20% variance
            assert expected_range * 0.8 <= tokens <= expected_range * 1.2
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, temp_project):
        """Test complete workflow execution"""
        system = IntegratedSystem(temp_project)
        
        # Check health first
        health = system.health_check()
        assert all(health.values()), f"Health check failed: {health}"
        
        # Execute a simple workflow
        result = await system.execute_workflow(
            description="Test feature",
            spec_name="test-spec"
        )
        
        # Verify result
        assert result is not None
        assert 'success' in result
        
        # Check memories were stored
        memories = system.memory_manager.get_relevant_memories(
            {'agent': 'any'}
        )
        assert len(memories) > 0
```

#### Step 2: Create unit tests
```python
# NEW FILE: .claude/tests/test_components.py

import pytest
from unittest.mock import Mock, patch

from context_engine import ContextCompressor
from memory_manager import MemoryManager
from secure_executor import SecureExecutor

class TestContextCompressor:
    """Test context compression"""
    
    def test_token_counting(self):
        """Test token counting accuracy"""
        compressor = ContextCompressor()
        
        # Test empty string
        assert compressor.count_tokens("") == 0
        
        # Test simple text
        tokens = compressor.count_tokens("Hello world")
        assert 1 <= tokens <= 3  # Should be ~2 tokens
    
    def test_compression_preserves_meaning(self):
        """Test compression preserves important content"""
        compressor = ContextCompressor()
        
        text = "def important_function():\n    pass\n" * 100
        compressed = compressor.compress(text, max_tokens=50)
        
        assert "important_function" in compressed
        assert compressor.count_tokens(compressed) <= 50

class TestSecureExecutor:
    """Test secure command execution"""
    
    def test_validates_dangerous_commands(self, tmp_path):
        """Test dangerous commands are blocked"""
        executor = SecureExecutor(tmp_path)
        
        # Test command injection
        with pytest.raises(ValueError):
            executor.validate_command("rm", ["-rf", "/"])
        
        # Test path traversal
        with pytest.raises(ValueError):
            executor.validate_path("../../etc/passwd")
    
    def test_allows_safe_commands(self, tmp_path):
        """Test safe commands are allowed"""
        executor = SecureExecutor(tmp_path)
        
        # Test safe command
        assert executor.validate_command("python", ["script.py"])
        
        # Test safe path
        safe_path = executor.validate_path("subdir/file.txt")
        assert safe_path.is_absolute()

class TestMemoryManager:
    """Test memory management"""
    
    def test_store_and_retrieve(self, tmp_path):
        """Test storing and retrieving memories"""
        # Create test database
        db_path = tmp_path / '.claude' / 'data'
        db_path.mkdir(parents=True)
        
        manager = MemoryManager(tmp_path)
        
        # Store memory
        manager.store_execution(
            task_id='test1',
            agent='test_agent',
            result={'success': True}
        )
        
        # Retrieve memory
        memories = manager.get_relevant_memories(
            {'agent': 'test_agent'}
        )
        
        assert len(memories) > 0
        assert memories[0]['task_id'] == 'test1'
```

### Day 13-14: Performance Testing

#### Step 1: Create performance benchmarks
```python
# NEW FILE: .claude/tests/test_performance.py

import time
import asyncio
import pytest
from pathlib import Path

from integrated_system import IntegratedSystem

class TestPerformance:
    """Performance benchmarks"""
    
    @pytest.mark.benchmark
    def test_token_counting_speed(self, benchmark, temp_project):
        """Benchmark token counting"""
        system = IntegratedSystem(temp_project)
        text = "a" * 10000  # 10KB text
        
        result = benchmark(
            system.context_engine.compressor.count_tokens,
            text
        )
        
        # Should be fast (< 100ms)
        assert benchmark.stats['mean'] < 0.1
    
    @pytest.mark.benchmark
    def test_compression_speed(self, benchmark, temp_project):
        """Benchmark compression"""
        system = IntegratedSystem(temp_project)
        text = "def function():\n    pass\n" * 1000
        
        result = benchmark(
            system.context_engine.compressor.compress,
            text,
            4000
        )
        
        # Should complete within 1 second
        assert benchmark.stats['mean'] < 1.0
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_workflow_speed(self, benchmark, temp_project):
        """Benchmark workflow execution"""
        system = IntegratedSystem(temp_project)
        
        async def run_workflow():
            return await system.execute_workflow(
                description="Test",
                spec_name="test"
            )
        
        result = await benchmark(run_workflow)
        
        # Should complete within 5 seconds
        assert benchmark.stats['mean'] < 5.0
```

---

## Week 4: Monitoring & Documentation

### Day 15-16: Setup Monitoring Dashboard

#### Step 1: Create monitoring server
```python
# NEW FILE: .claude/scripts/monitoring_server.py

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

class MonitoringServer:
    """Real-time monitoring dashboard server"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.metrics = []
        self.active_workflows = {}
    
    @app.route('/')
    def dashboard():
        """Serve dashboard HTML"""
        return render_template('dashboard.html')
    
    @app.route('/api/metrics')
    def get_metrics():
        """Get current metrics"""
        return jsonify({
            'metrics': self.metrics[-100:],  # Last 100 metrics
            'active_workflows': list(self.active_workflows.values())
        })
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        emit('connected', {'data': 'Connected to monitoring server'})
    
    def log_metric(self, metric: dict):
        """Log a metric and broadcast to clients"""
        metric['timestamp'] = datetime.now().isoformat()
        self.metrics.append(metric)
        
        # Broadcast to all connected clients
        socketio.emit('new_metric', metric)
    
    def update_workflow(self, workflow_id: str, status: dict):
        """Update workflow status"""
        self.active_workflows[workflow_id] = status
        socketio.emit('workflow_update', {
            'workflow_id': workflow_id,
            'status': status
        })
    
    def run(self, port: int = 8080):
        """Run the monitoring server"""
        socketio.run(app, port=port)

# Global server instance
monitor_server = MonitoringServer(Path.cwd())

if __name__ == '__main__':
    monitor_server.run()
```

#### Step 2: Create dashboard HTML
```html
<!-- File: .claude/templates/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Context Engineering System - Monitoring Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        .status-success { background: #4CAF50; }
        .status-error { background: #f44336; }
        .status-running { background: #2196F3; }
        .status-pending { background: #FFC107; }
    </style>
</head>
<body>
    <h1>Context Engineering System - Monitoring Dashboard</h1>
    
    <div class="dashboard">
        <!-- System Health -->
        <div class="card">
            <h2>System Health</h2>
            <div id="health-status">
                <div class="metric">
                    <span>Bridge Connection</span>
                    <span id="bridge-status">⏳</span>
                </div>
                <div class="metric">
                    <span>Memory Persistence</span>
                    <span id="memory-status">⏳</span>
                </div>
                <div class="metric">
                    <span>Context Engine</span>
                    <span id="context-status">⏳</span>
                </div>
                <div class="metric">
                    <span>Token Accuracy</span>
                    <span id="token-status">⏳</span>
                </div>
            </div>
        </div>
        
        <!-- Active Workflows -->
        <div class="card">
            <h2>Active Workflows</h2>
            <div id="active-workflows">
                <p>No active workflows</p>
            </div>
        </div>
        
        <!-- Performance Metrics -->
        <div class="card">
            <h2>Performance Metrics</h2>
            <canvas id="performance-chart"></canvas>
        </div>
        
        <!-- Recent Events -->
        <div class="card">
            <h2>Recent Events</h2>
            <div id="recent-events" style="max-height: 300px; overflow-y: auto;">
            </div>
        </div>
    </div>
    
    <script>
        // Connect to WebSocket
        const socket = io();
        
        // Chart setup
        const ctx = document.getElementById('performance-chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Task Duration (s)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Handle new metrics
        socket.on('new_metric', (metric) => {
            // Update chart
            chart.data.labels.push(new Date(metric.timestamp).toLocaleTimeString());
            chart.data.datasets[0].data.push(metric.duration || 0);
            
            // Keep only last 20 points
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update();
            
            // Add to recent events
            const eventsDiv = document.getElementById('recent-events');
            const eventDiv = document.createElement('div');
            eventDiv.className = 'metric';
            eventDiv.innerHTML = `
                <span>${metric.event || 'Unknown'}</span>
                <span>${new Date(metric.timestamp).toLocaleTimeString()}</span>
            `;
            eventsDiv.insertBefore(eventDiv, eventsDiv.firstChild);
            
            // Keep only last 10 events
            while (eventsDiv.children.length > 10) {
                eventsDiv.removeChild(eventsDiv.lastChild);
            }
        });
        
        // Handle workflow updates
        socket.on('workflow_update', (data) => {
            const workflowsDiv = document.getElementById('active-workflows');
            
            if (Object.keys(data).length === 0) {
                workflowsDiv.innerHTML = '<p>No active workflows</p>';
            } else {
                workflowsDiv.innerHTML = '';
                for (const [id, status] of Object.entries(data)) {
                    const workflowDiv = document.createElement('div');
                    workflowDiv.className = 'metric';
                    workflowDiv.innerHTML = `
                        <span>${id}</span>
                        <span class="status-indicator status-${status.state}"></span>
                    `;
                    workflowsDiv.appendChild(workflowDiv);
                }
            }
        });
        
        // Check system health periodically
        async function checkHealth() {
            try {
                const response = await fetch('/api/health');
                const health = await response.json();
                
                document.getElementById('bridge-status').textContent = 
                    health.bridge_connected ? '✅' : '❌';
                document.getElementById('memory-status').textContent = 
                    health.memory_persistent ? '✅' : '❌';
                document.getElementById('context-status').textContent = 
                    health.context_working ? '✅' : '❌';
                document.getElementById('token-status').textContent = 
                    health.token_accuracy ? '✅' : '❌';
            } catch (error) {
                console.error('Health check failed:', error);
            }
        }
        
        // Check health every 5 seconds
        setInterval(checkHealth, 5000);
        checkHealth();
    </script>
</body>
</html>
```

---

## Final Integration Script

### Create master fix script
```python
# NEW FILE: .claude/scripts/fix_all.py

#!/usr/bin/env python3
"""
Master script to fix all Context Engineering System issues
Run this to apply all fixes in order
"""

import sys
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_step(description: str, command: list) -> bool:
    """Run a fix step"""
    logger.info(f"🔧 {description}...")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✅ {description} - Complete")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - Failed: {e.stderr}")
        return False

def main():
    """Run all fixes"""
    project_root = Path.cwd()
    
    steps = [
        # Week 1: Critical Fixes
        ("Creating database", ["python", ".claude/scripts/create_database.py"]),
        ("Installing tiktoken", ["pip", "install", "tiktoken"]),
        
        # Week 2: Dependencies
        ("Installing Flask", ["pip", "install", "flask", "flask-socketio"]),
        ("Installing pytest", ["pip", "install", "pytest", "pytest-asyncio", "pytest-benchmark"]),
        
        # Week 3: Testing
        ("Running tests", ["pytest", ".claude/tests/", "-v"]),
        
        # Week 4: Final checks
        ("Health check", ["python", "-c", "from integrated_system import IntegratedSystem; print(IntegratedSystem().health_check())"])
    ]
    
    success_count = 0
    for description, command in steps:
        if run_step(description, command):
            success_count += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Fixes Complete: {success_count}/{len(steps)} successful")
    
    if success_count == len(steps):
        print("✅ System is now functional!")
        print("\nNext steps:")
        print("1. Run monitoring: python .claude/scripts/monitoring_server.py")
        print("2. Test workflow: python .claude/scripts/integrated_system.py")
        print("3. Check dashboard: http://localhost:8080")
    else:
        print("⚠️ Some fixes failed. Please review errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## Success Validation Checklist

### Week 1 Completion
- [ ] Agent Tool Bridge connected in real_executor.py
- [ ] Memory persists to SQLite database
- [ ] Token counting uses real tiktoken
- [ ] Database created at .claude/data/memory.db

### Week 2 Completion
- [ ] No shell=True in any subprocess calls
- [ ] All paths validated against project root
- [ ] All components wired in IntegratedSystem
- [ ] Event bus operational

### Week 3 Completion
- [ ] All integration tests pass
- [ ] Performance benchmarks meet targets
- [ ] Health check returns all green
- [ ] No errors in 24-hour test run

### Week 4 Completion
- [ ] Monitoring dashboard accessible
- [ ] Real-time metrics displayed
- [ ] Documentation complete
- [ ] System ready for production

---

## Common Issues & Solutions

### Issue: ImportError for agent_tool_bridge
**Solution**: Ensure all scripts are in .claude/scripts/ and add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}/.claude/scripts"
```

### Issue: Database locked error
**Solution**: Use write-ahead logging:
```python
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=WAL")
```

### Issue: Token counting still wrong
**Solution**: Verify tiktoken installation:
```bash
pip show tiktoken
# Should show version 0.5.0 or higher
```

### Issue: Monitoring dashboard not updating
**Solution**: Check WebSocket connection:
```javascript
socket.on('connect_error', (error) => {
    console.error('WebSocket error:', error);
});
```

---

## Final Notes

1. **Always test changes**: Run tests after each fix
2. **Monitor performance**: Use dashboard during development
3. **Document changes**: Update this guide with any modifications
4. **Version control**: Commit after each successful phase
5. **Backup first**: Always backup before major changes

---please 

Run `python .claude/scripts/fix_all.py` to begin automated fixes!