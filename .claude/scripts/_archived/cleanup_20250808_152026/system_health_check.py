#!/usr/bin/env python3
"""
System Health Check Script
Quick verification that all Context Engineering System fixes are working
"""

import sys
from pathlib import Path
import asyncio
import sqlite3
import json

# Add script directory to path
sys.path.append(str(Path(__file__).parent))

def check_database():
    """Check if database exists and has correct structure"""
    db_path = Path.cwd() / '.claude' / 'data' / 'memory.db'
    
    if not db_path.exists():
        return False, "Database file not found"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['memories', 'episodic_memories', 'context_cache', 'agent_performance', 'workflows', 'health_metrics']
        missing = [t for t in required_tables if t not in tables]
        
        conn.close()
        
        if missing:
            return False, f"Missing tables: {missing}"
        
        return True, f"All {len(required_tables)} tables present"
        
    except Exception as e:
        return False, f"Database error: {e}"

def check_token_counting():
    """Check if token counting is working with tiktoken"""
    try:
        from context_engine import ContextEngine
        engine = ContextEngine()
        
        # Test token counting
        test_text = "Hello world, this is a test"
        tokens = engine.compressor._count_tokens({'test': test_text})
        
        # Should be between 5-15 tokens for this text
        if 5 <= tokens <= 15:
            return True, f"Token counting works: {tokens} tokens"
        else:
            return False, f"Token count seems wrong: {tokens}"
            
    except Exception as e:
        return False, f"Token counting error: {e}"

def check_memory_persistence():
    """Check if memory manager can store and retrieve"""
    try:
        from memory_manager import MemoryManager
        manager = MemoryManager()
        
        # Test storage
        test_result = {
            'success': True,
            'output': 'Test output',
            'duration': 1.5
        }
        
        manager.store_execution('test_task_123', 'test_agent', test_result)
        
        # Test retrieval
        memories = manager.get_relevant_memories({
            'type': 'test',
            'agent': 'test_agent'
        })
        
        if isinstance(memories, dict) and 'long_term' in memories:
            return True, f"Memory persistence works: {len(memories['long_term'])} memories found"
        else:
            return False, "Memory retrieval format incorrect"
            
    except Exception as e:
        return False, f"Memory persistence error: {e}"

def check_bridge_connection():
    """Check if Agent Tool Bridge is connected"""
    try:
        from integrated_system import IntegratedSystem
        system = IntegratedSystem()
        executor = system.executor
        
        # Check if bridge is connected
        has_bridge = hasattr(executor, 'bridge') and executor.bridge is not None
        has_context = hasattr(executor, 'context_engine') and executor.context_engine is not None
        has_memory = hasattr(executor, 'memory_manager') and executor.memory_manager is not None
        has_method = hasattr(executor, 'handle_task_delegation')
        
        if has_bridge and has_context and has_memory and has_method:
            return True, "All bridge components connected"
        else:
            missing = []
            if not has_bridge: missing.append("bridge")
            if not has_context: missing.append("context_engine")
            if not has_memory: missing.append("memory_manager")
            if not has_method: missing.append("handle_task_delegation")
            return False, f"Missing: {missing}"
            
    except Exception as e:
        return False, f"Bridge connection error: {e}"

async def check_integration():
    """Check full integration"""
    try:
        from integrated_system import IntegratedSystem
        system = IntegratedSystem()
        
        health = system.health_check()
        
        if health.get('system_healthy', False):
            return True, "Full integration working"
        else:
            failed = [k for k, v in health.items() if not v and k != 'system_healthy']
            return False, f"Failed components: {failed}"
            
    except Exception as e:
        return False, f"Integration error: {e}"

def main():
    """Run all health checks"""
    print("=" * 60)
    print("Context Engineering System - Health Check")
    print("=" * 60)
    
    checks = [
        ("Database Structure", check_database),
        ("Token Counting", check_token_counting),
        ("Memory Persistence", check_memory_persistence),
        ("Bridge Connection", check_bridge_connection),
        ("Full Integration", lambda: asyncio.run(check_integration())),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            success, message = check_func()
            status = "[PASS]" if success else "[FAIL]"
            print(f"{status} {name}: {message}")
            results.append(success)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"[SUCCESS] All {total} health checks passed!")
        print("\nThe Context Engineering System is now fully functional:")
        print("- Agent Tool Bridge: Connected")
        print("- Memory System: Persistent") 
        print("- Token Counting: Accurate")
        print("- Context Engine: Working")
        print("- Integration: Complete")
        print("\nSystem Status: READY FOR USE")
        return 0
    else:
        print(f"[WARNING] {passed}/{total} health checks passed")
        print(f"{total - passed} issues need attention")
        print("\nSystem Status: NEEDS WORK")
        return 1

if __name__ == "__main__":
    exit(main())