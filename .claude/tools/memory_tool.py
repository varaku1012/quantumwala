#!/usr/bin/env python3
"""Custom memory tool for agents"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import hashlib
from typing import Any, Dict, List

class MemoryTool:
    def __init__(self):
        self.db_path = Path('.claude/data/memory.db')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize memory database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    agent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_key ON memories(key)
            """)
    
    def store(self, key: str, value: Any, agent: str = None) -> Dict:
        """Store a memory"""
        memory_id = hashlib.md5(f"{key}{datetime.now()}".encode()).hexdigest()
        value_json = json.dumps(value)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (id, key, value, agent)
                VALUES (?, ?, ?, ?)
            """, (memory_id, key, value_json, agent))
        
        return {"stored": True, "id": memory_id, "key": key}
    
    def retrieve(self, key: str) -> Dict:
        """Retrieve a memory by key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT value, timestamp, access_count 
                FROM memories 
                WHERE key = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (key,))
            
            row = cursor.fetchone()
            if row:
                # Update access count
                conn.execute("""
                    UPDATE memories 
                    SET access_count = access_count + 1 
                    WHERE key = ?
                """, (key,))
                
                return {
                    "found": True,
                    "value": json.loads(row[0]),
                    "timestamp": row[1],
                    "access_count": row[2]
                }
        
        return {"found": False, "key": key}
    
    def search(self, query: str, limit: int = 10) -> Dict:
        """Search memories by query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, value, timestamp 
                FROM memories 
                WHERE key LIKE ? OR value LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            results = []
            for row in cursor:
                results.append({
                    "key": row[0],
                    "value": json.loads(row[1]),
                    "timestamp": row[2]
                })
        
        return {"results": results, "count": len(results)}
    
    def get_recent(self, limit: int = 10) -> Dict:
        """Get recent memories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, value, timestamp, agent 
                FROM memories 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor:
                results.append({
                    "key": row[0],
                    "value": json.loads(row[1]),
                    "timestamp": row[2],
                    "agent": row[3]
                })
        
        return {"recent": results}

def main():
    """CLI interface for memory tool"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)
    
    tool = MemoryTool()
    command = sys.argv[1]
    
    try:
        if command == "store":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "Usage: store <key> <value> [agent]"}))
                sys.exit(1)
            
            key = sys.argv[2]
            value = json.loads(sys.argv[3]) if sys.argv[3].startswith('{') else sys.argv[3]
            agent = sys.argv[4] if len(sys.argv) > 4 else None
            result = tool.store(key, value, agent)
            
        elif command == "retrieve":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: retrieve <key>"}))
                sys.exit(1)
            
            result = tool.retrieve(sys.argv[2])
            
        elif command == "search":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: search <query>"}))
                sys.exit(1)
            
            result = tool.search(sys.argv[2])
            
        elif command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = tool.get_recent(limit)
            
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()