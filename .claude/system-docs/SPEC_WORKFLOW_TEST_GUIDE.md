# Spec Workflow Test Guide
## Testing the Enhanced Context Engineering System

---

## Overview

This guide provides step-by-step instructions for testing the newly enhanced Context Engineering System with a real specification workflow.

---

## Prerequisites Checklist

### System Setup
- [x] Database initialized (`python .claude/scripts/create_database.py`)
- [x] Health check passed (`python .claude/scripts/system_health_check.py`)
- [x] Integration test successful (`python .claude/scripts/integrated_system.py`)

### Required Components
- [x] AgentToolBridge connected
- [x] MemoryManager with SQLite persistence
- [x] ContextEngine with tiktoken
- [x] IntegratedSystem orchestrator

---

## Test Scenario: User Authentication Feature

We'll test the system by implementing a complete user authentication feature spec.

### Spec Details
- **Name**: user-auth
- **Description**: Secure user authentication with JWT
- **Components**: Login, Register, Password Reset, MFA
- **Expected Outcomes**: Requirements, Design, Tasks, Implementation

---

## Step-by-Step Testing Process

### Step 1: Initialize the Integrated System
```python
from integrated_system import IntegratedSystem
import asyncio

async def test_workflow():
    # Initialize system
    system = IntegratedSystem()
    
    # Verify health
    health = system.health_check()
    assert health['system_healthy'], "System not healthy!"
    
    print("System initialized and healthy")
```

### Step 2: Create a Test Spec
```python
from spec_manager import SpecManager

# Create spec manager
spec_mgr = SpecManager()

# Create new spec
spec_mgr.create_spec(
    name="user-auth",
    description="Secure user authentication system with JWT, MFA, and password reset",
    stage=SpecStage.SCOPE
)

print("Spec created: user-auth")
```

### Step 3: Execute Workflow Through Integrated System
```python
# Execute the workflow
result = await system.execute_workflow(
    description="Implement user authentication with JWT and MFA",
    spec_name="user-auth"
)

print(f"Workflow result: {result}")
```

### Step 4: Verify Memory Persistence
```python
# Check if memories were stored
memories = system.memory_manager.get_relevant_memories({
    'type': 'authentication',
    'agent': 'architect'
})

print(f"Stored memories: {len(memories['long_term'])} long-term")
print(f"Episodic patterns: {len(memories['episodic'])}")
```

### Step 5: Test Context Compression
```python
# Test context engine
test_context = {
    'requirements': "Long requirements text" * 100,
    'design': "Detailed design document" * 50,
    'current_task': {'id': 'task-1', 'description': 'Implement login'}
}

# Compress context
compressed = system.context_engine.prepare_context(
    agent_type='developer',
    task={'description': 'Implement login endpoint'},
    full_context=test_context
)

# Verify token count
tokens = system.context_engine.compressor._count_tokens(compressed)
print(f"Compressed to {tokens} tokens")
assert tokens <= 4000, "Context not properly compressed!"
```

### Step 6: Test Task Delegation
```python
# Test task delegation through bridge
delegation_result = await system.executor.handle_task_delegation(
    agent='business-analyst',
    description='Generate detailed requirements for MFA',
    context={'spec_name': 'user-auth', 'component': 'mfa'}
)

print(f"Delegation success: {delegation_result.success}")
print(f"Duration: {delegation_result.duration}s")
```

### Step 7: Verify Database Storage
```python
import sqlite3

# Connect to database
conn = sqlite3.connect('.claude/data/memory.db')
cursor = conn.cursor()

# Check memories table
cursor.execute("SELECT COUNT(*) FROM memories")
memory_count = cursor.fetchone()[0]
print(f"Memories stored: {memory_count}")

# Check workflows table
cursor.execute("SELECT * FROM workflows ORDER BY start_time DESC LIMIT 1")
latest_workflow = cursor.fetchone()
print(f"Latest workflow: {latest_workflow}")

conn.close()
```

---

## Expected Test Results

### Successful Test Indicators
1. ✅ System health check: All components green
2. ✅ Spec created in correct directory
3. ✅ Workflow executes without errors
4. ✅ Memories persisted to database
5. ✅ Context compressed below 4000 tokens
6. ✅ Task delegation returns results
7. ✅ Database contains execution records

### Performance Benchmarks
- System initialization: < 2 seconds
- Workflow execution: < 30 seconds
- Context compression: < 1 second
- Memory retrieval: < 100ms
- Task delegation: < 5 seconds

---

## Common Issues & Solutions

### Issue: "AgentToolBridge not found"
**Solution**: The warning is expected in testing environment. Bridge is still functional through IntegratedSystem.

### Issue: "TaskRequest not callable"
**Solution**: This occurs when running outside integrated environment. Use IntegratedSystem for testing.

### Issue: Database locked
**Solution**: Close any open database connections or restart the test.

### Issue: Token counting fails
**Solution**: Ensure tiktoken is installed: `pip install tiktoken`

---

## Advanced Testing

### Parallel Task Execution
```python
# Test parallel execution
tasks = [
    {'agent': 'developer', 'description': 'Implement login'},
    {'agent': 'developer', 'description': 'Implement register'},
    {'agent': 'qa-engineer', 'description': 'Write tests'}
]

results = await asyncio.gather(*[
    system.executor.handle_task_delegation(**task)
    for task in tasks
])

print(f"Completed {len(results)} tasks in parallel")
```

### Stress Testing
```python
# Create multiple workflows
for i in range(5):
    result = await system.execute_workflow(
        description=f"Test workflow {i}",
        spec_name=f"test-{i}"
    )
    print(f"Workflow {i}: {'Success' if result['success'] else 'Failed'}")
```

---

## Monitoring & Validation

### Real-time Monitoring
```python
# Monitor system during execution
import threading
import time

def monitor():
    while monitoring:
        health = system.health_check()
        print(f"System health: {health}")
        time.sleep(5)

monitoring = True
monitor_thread = threading.Thread(target=monitor)
monitor_thread.start()

# Run workflow
result = await system.execute_workflow(...)

monitoring = False
monitor_thread.join()
```

### Validation Queries
```sql
-- Check task execution history
SELECT agent, COUNT(*) as tasks, AVG(duration) as avg_duration
FROM memories
GROUP BY agent;

-- Check successful patterns
SELECT pattern, usage_count
FROM episodic_memories
ORDER BY usage_count DESC;

-- Check system health metrics
SELECT * FROM health_metrics
ORDER BY timestamp DESC
LIMIT 10;
```

---

## Complete Test Script

Save this as `test_integrated_system.py`:

```python
#!/usr/bin/env python3
"""Complete test of the integrated Context Engineering System"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / '.claude' / 'scripts'))

from integrated_system import IntegratedSystem
from spec_manager import SpecManager, SpecStage

async def complete_test():
    print("Starting Context Engineering System Test")
    print("=" * 60)
    
    # 1. Initialize
    system = IntegratedSystem()
    health = system.health_check()
    print(f"System Health: {health['system_healthy']}")
    
    if not health['system_healthy']:
        print("System not healthy! Aborting test.")
        return False
    
    # 2. Create spec
    spec_mgr = SpecManager()
    spec_created = spec_mgr.create_spec(
        "test-auth",
        "Test authentication system",
        SpecStage.SCOPE
    )
    print(f"Spec Created: {spec_created}")
    
    # 3. Execute workflow
    result = await system.execute_workflow(
        description="Test authentication implementation",
        spec_name="test-auth"
    )
    print(f"Workflow Success: {result.get('success', False)}")
    
    # 4. Verify persistence
    memories = system.memory_manager.get_relevant_memories({
        'type': 'test',
        'agent': 'any'
    })
    print(f"Memories Stored: {len(memories.get('long_term', []))}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    return True

if __name__ == "__main__":
    success = asyncio.run(complete_test())
    sys.exit(0 if success else 1)
```

---

## Conclusion

The Context Engineering System is now ready for comprehensive testing. Follow this guide to validate:

1. **Integration**: All components work together
2. **Persistence**: Data survives restarts
3. **Optimization**: Context fits token limits
4. **Delegation**: Tasks route correctly
5. **Performance**: System meets benchmarks

After successful testing, the system can be used for production workflows with confidence.

---

*Test Guide Created: January 2025*
*For System Version: 1.0.0 (Beta)*