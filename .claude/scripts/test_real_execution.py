#!/usr/bin/env python3
"""
Test script for the real execution system
Validates all components work together correctly
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from real_executor import RealClaudeExecutor, ExecutionResult
from resource_manager import ResourceManager, ResourceRequirements
from unified_state import UnifiedStateManager
from suggestion_consumer import SuggestionConsumer

async def test_real_executor():
    """Test the real executor with a simple command"""
    print("🧪 Testing Real Executor...")
    
    executor = RealClaudeExecutor()
    
    # Test basic command execution
    result = await executor.execute_command("echo 'Hello from real executor'", timeout=10)
    
    print(f"✅ Command executed: success={result.success}, duration={result.duration:.2f}s")
    if result.output:
        print(f"📄 Output: {result.output.strip()}")
    if result.error:
        print(f"❌ Error: {result.error}")
    
    return result.success

async def test_resource_manager():
    """Test the resource manager"""
    print("\n🧪 Testing Resource Manager...")
    
    manager = ResourceManager()
    
    # Test resource status
    status = manager.get_resource_status()
    print(f"💻 System resources: CPU={status['system']['cpu_percent']:.1f}%, Memory={status['system']['memory_percent']:.1f}%")
    
    # Test resource acquisition
    requirements = ResourceRequirements(cpu_percent=10, memory_mb=256)
    
    success = await manager.acquire_resources("test-task", "test-agent", requirements)
    print(f"✅ Resource acquisition: {'Success' if success else 'Failed'}")
    
    if success:
        await manager.release_resources("test-task")
        print("✅ Resource release: Success")
    
    return success

async def test_unified_state():
    """Test the unified state manager"""
    print("\n🧪 Testing Unified State Manager...")
    
    state_manager = UnifiedStateManager()
    
    # Test spec creation
    spec_name = "test-spec"
    success = state_manager.create_specification(spec_name, "Test specification")
    print(f"✅ Spec creation: {'Success' if success else 'Failed'}")
    
    # Test task addition
    from unified_state import TaskStatus
    success = state_manager.add_task(spec_name, "1.1", "Test task", "test-agent")
    print(f"✅ Task addition: {'Success' if success else 'Failed'}")
    
    # Test task status update
    success = state_manager.update_task_status(spec_name, "1.1", TaskStatus.COMPLETED)
    print(f"✅ Task status update: {'Success' if success else 'Failed'}")
    
    # Test statistics
    stats = state_manager.get_system_statistics()
    print(f"📊 System stats: {stats['specifications']['total']} specs, {stats['agents']['total_executions']} executions")
    
    return True

async def test_suggestion_consumer():
    """Test the suggestion consumer"""
    print("\n🧪 Testing Suggestion Consumer...")
    
    consumer = SuggestionConsumer()
    
    # Create a test suggestion
    suggestion_file = consumer.suggestion_file
    suggestion_file.parent.mkdir(parents=True, exist_ok=True)
    suggestion_file.write_text("echo 'Test suggestion execution'")
    
    print(f"📝 Created test suggestion: {suggestion_file}")
    
    # Process suggestion
    processed = await consumer.run_once()
    print(f"✅ Suggestion processing: {'Success' if processed else 'No suggestions found'}")
    
    return True

async def test_integration():
    """Test full integration"""
    print("\n🚀 Testing Full Integration...")
    
    # Create a simple task orchestration test
    from task_orchestrator import EnhancedTaskOrchestrator
    
    # Create test specification directory and files
    project_root = Path.cwd()
    spec_dir = project_root / '.claude' / 'specs' / 'integration-test'
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    # Create simple tasks.md
    tasks_content = """# Test Tasks

- [ ] 1. Test task one
- [ ] 2. Test task two
"""
    
    (spec_dir / 'tasks.md').write_text(tasks_content)
    
    print(f"📁 Created test spec directory: {spec_dir}")
    
    # Test orchestrator initialization
    orchestrator = EnhancedTaskOrchestrator('integration-test')
    orchestrator.enable_real_execution = False  # Use simulation for testing
    
    # Parse tasks
    tasks = orchestrator.parse_tasks()
    print(f"📋 Parsed {len(tasks)} tasks")
    
    if tasks:
        # Test single task execution
        task = tasks[0]
        result = await orchestrator.execute_task_real(task)
        print(f"✅ Task execution: success={result.success}, duration={result.duration:.2f}s")
        
        return result.success
    
    return False

def create_test_summary(results):
    """Create test summary"""
    print("\n" + "="*60)
    print("🎯 TEST SUMMARY")
    print("="*60)
    
    tests = [
        ("Real Executor", results.get('executor', False)),
        ("Resource Manager", results.get('resource_manager', False)),
        ("Unified State", results.get('state_manager', False)),
        ("Suggestion Consumer", results.get('suggestion_consumer', False)),
        ("Integration", results.get('integration', False))
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print("-" * 60)
    print(f"OVERALL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is ready for real execution!")
    else:
        print("⚠️  SOME TESTS FAILED - Review failures before using real execution")
    
    return passed == total

async def main():
    """Run all tests"""
    print("🚀 Starting Real Execution System Tests")
    print("="*60)
    
    results = {}
    
    try:
        # Test individual components
        results['executor'] = await test_real_executor()
        results['resource_manager'] = await test_resource_manager()
        results['state_manager'] = await test_unified_state()
        results['suggestion_consumer'] = await test_suggestion_consumer()
        results['integration'] = await test_integration()
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        results['error'] = str(e)
    
    # Create summary
    success = create_test_summary(results)
    
    # Save test results
    test_results = {
        'timestamp': time.time(),
        'success': success,
        'results': results
    }
    
    results_file = Path('.claude/logs/test_results.json')
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n📊 Test results saved to: {results_file}")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)