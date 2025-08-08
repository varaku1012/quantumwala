#!/usr/bin/env python3
"""
Create and initialize the Context Engineering System database
This ensures all required tables and indexes are created
"""

import sqlite3
from pathlib import Path
import json
from datetime import datetime

def create_memory_database():
    """Create the main memory database with all required tables"""
    # Ensure data directory exists
    db_path = Path.cwd() / '.claude' / 'data' / 'memory.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable WAL mode for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL")
    
    print(f"Creating database at: {db_path}")
    
    # Create main memories table
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
            memory_type TEXT DEFAULT 'execution',
            relevance_score REAL DEFAULT 1.0,
            access_count INTEGER DEFAULT 0,
            last_accessed DATETIME
        )
    ''')
    
    # Create indexes for efficient querying
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task ON memories(task_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_success ON memories(success)')
    
    # Create episodic memories table for successful patterns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodic_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            successful_approach TEXT NOT NULL,
            agent TEXT NOT NULL,
            context_summary TEXT,
            usage_count INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 1.0,
            last_used DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create context cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS context_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context_hash TEXT UNIQUE NOT NULL,
            compressed_context TEXT NOT NULL,
            original_tokens INTEGER,
            compressed_tokens INTEGER,
            compression_ratio REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_accessed DATETIME,
            access_count INTEGER DEFAULT 0
        )
    ''')
    
    # Create agent performance tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            task_type TEXT,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            total_duration REAL DEFAULT 0,
            average_duration REAL DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            last_execution DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create workflow tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id TEXT UNIQUE NOT NULL,
            description TEXT,
            spec_name TEXT,
            status TEXT DEFAULT 'running',
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            duration REAL,
            total_tasks INTEGER DEFAULT 0,
            completed_tasks INTEGER DEFAULT 0,
            failed_tasks INTEGER DEFAULT 0,
            metadata TEXT
        )
    ''')
    
    # Create system health metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_unit TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            component TEXT,
            status TEXT DEFAULT 'normal'
        )
    ''')
    
    # Create indexes for performance tables
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_perf ON agent_performance(agent)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflow_id ON workflows(workflow_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflows(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_context_hash ON context_cache(context_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_metrics(timestamp)')
    
    # Insert initial health check
    cursor.execute('''
        INSERT INTO health_metrics (metric_name, metric_value, metric_unit, component, status)
        VALUES ('database_initialized', 1, 'boolean', 'database', 'healthy')
    ''')
    
    # Commit changes
    conn.commit()
    
    print("[SUCCESS] Database created successfully!")
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Created {len(tables)} tables:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count} rows")
    
    # Close connection
    conn.close()
    
    return db_path

def verify_database_integrity(db_path: Path):
    """Verify database integrity and structure"""
    if not db_path.exists():
        print(f"[ERROR] Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] != 'ok':
            print(f"[ERROR] Database integrity check failed: {result}")
            return False
        
        # Check required tables exist
        required_tables = [
            'memories', 'episodic_memories', 'context_cache',
            'agent_performance', 'workflows', 'health_metrics'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = set(required_tables) - set(existing_tables)
        if missing_tables:
            print(f"[ERROR] Missing tables: {missing_tables}")
            return False
        
        print("[SUCCESS] Database integrity check passed")
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database verification failed: {e}")
        return False

def migrate_existing_database(db_path: Path):
    """Migrate existing database to new schema if needed"""
    if not db_path.exists():
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='memories'")
        schema = cursor.fetchone()
        
        if schema and 'relevance_score' not in schema[0]:
            print("Migrating database to new schema...")
            
            # Add missing columns
            try:
                cursor.execute("ALTER TABLE memories ADD COLUMN relevance_score REAL DEFAULT 1.0")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE memories ADD COLUMN access_count INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE memories ADD COLUMN last_accessed DATETIME")
            except sqlite3.OperationalError:
                pass
            
            conn.commit()
            print("[SUCCESS] Database migration completed")
    
    except Exception as e:
        print(f"Migration error (non-critical): {e}")
    
    finally:
        conn.close()

def main():
    """Main execution function"""
    print("=" * 50)
    print("Context Engineering System - Database Setup")
    print("=" * 50)
    
    # Create database
    db_path = create_memory_database()
    
    # Verify integrity
    if verify_database_integrity(db_path):
        print("\n[SUCCESS] Database setup complete and verified!")
        print(f"Location: {db_path}")
        
        # Try migration if needed
        migrate_existing_database(db_path)
        
        print("\nYou can now run the system with persistent memory!")
    else:
        print("\n[ERROR] Database setup failed - please check errors above")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())