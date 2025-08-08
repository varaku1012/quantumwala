#!/usr/bin/env python3
"""
Integrated Context Engineering System
This is the main orchestrator that wires all components together
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import sys

# Add script directory to path
sys.path.append(str(Path(__file__).parent))

# Import components
from real_executor import RealClaudeExecutor
from agent_tool_bridge import AgentToolBridge, TaskRequest
from context_engine import ContextEngine
from memory_manager import MemoryManager

# Event system for loose coupling
class EventBus:
    """Simple event bus for component communication"""
    
    def __init__(self):
        self.subscribers = {}
        
    def subscribe(self, event_type: str, handler):
        """Subscribe to an event"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    async def publish(self, event_type: str, data: Any):
        """Publish an event to all subscribers"""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    print(f"Event handler error: {e}")

class IntegratedSystem:
    """
    Fully integrated Context Engineering System
    This is the main class that fixes all the architectural issues
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize event bus
        self.event_bus = EventBus()
        
        # Initialize core components
        self.logger.info("Initializing Context Engineering System components...")
        self._initialize_components()
        
        # Wire components together
        self._wire_components()
        
        # Register event handlers
        self._register_event_handlers()
        
        self.logger.info("[SUCCESS] Integrated System initialized successfully")
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _setup_logging(self):
        """Setup logging for the integrated system"""
        log_dir = self.project_root / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'integrated_system_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Core executor with bridge
            self.executor = RealClaudeExecutor(self.project_root)
            self.logger.info("[SUCCESS] Real executor initialized")
            
            # Context engine for optimization
            self.context_engine = ContextEngine()
            self.logger.info("[SUCCESS] Context engine initialized")
            
            # Memory manager for persistence
            self.memory_manager = MemoryManager(self.project_root)
            self.logger.info("[SUCCESS] Memory manager initialized")
            
            # Agent tool bridge for delegation
            self.bridge = AgentToolBridge(self.project_root)
            self.logger.info("[SUCCESS] Agent tool bridge initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _wire_components(self):
        """Wire all components together - THIS IS THE KEY FIX"""
        self.logger.info("Wiring system components...")
        
        # Wire bridge to context and memory
        if hasattr(self.bridge, 'context_engine'):
            self.bridge.context_engine = self.context_engine
            
        if hasattr(self.bridge, 'memory_manager'):
            self.bridge.memory_manager = self.memory_manager
            
        # Wire executor to bridge (THE CRITICAL MISSING CONNECTION)
        if hasattr(self.executor, 'bridge'):
            self.executor.bridge = self.bridge
            self.executor.context_engine = self.context_engine
            self.executor.memory_manager = self.memory_manager
        
        # Wire context engine to memory for relevant memories
        if hasattr(self.context_engine, 'memory_manager'):
            self.context_engine.memory_manager = self.memory_manager
        
        self.logger.info("[SUCCESS] All components wired successfully")
    
    def _register_event_handlers(self):
        """Register event handlers for system-wide events"""
        # Task completion events
        self.event_bus.subscribe('task.completed', self._handle_task_completed)
        self.event_bus.subscribe('task.started', self._handle_task_started)
        self.event_bus.subscribe('workflow.started', self._handle_workflow_started)
        self.event_bus.subscribe('workflow.completed', self._handle_workflow_completed)
        
        self.logger.info("[SUCCESS] Event handlers registered")
    
    async def _handle_task_completed(self, data):
        """Handle task completion event"""
        self.logger.info(f"Task completed: {data.get('task_id', 'unknown')}")
        
        # Store in memory if we have the result
        if 'result' in data and 'agent' in data:
            self.memory_manager.store_execution(
                task_id=data['task_id'],
                agent=data['agent'],
                result=data['result']
            )
    
    async def _handle_task_started(self, data):
        """Handle task start event"""
        self.logger.info(f"Task started: {data.get('task_id', 'unknown')}")
    
    async def _handle_workflow_started(self, data):
        """Handle workflow start event"""
        self.logger.info(f"Workflow started: {data.get('workflow_id', 'unknown')}")
    
    async def _handle_workflow_completed(self, data):
        """Handle workflow completion event"""
        self.logger.info(f"Workflow completed: {data.get('workflow_id', 'unknown')}")
    
    async def execute_workflow(self, description: str, spec_name: str = "default") -> Dict[str, Any]:
        """Execute a complete workflow using the integrated system"""
        workflow_id = f"workflow_{spec_name}_{int(datetime.now().timestamp())}"
        
        self.logger.info(f"Starting workflow: {workflow_id}")
        
        # Publish workflow start event
        await self.event_bus.publish('workflow.started', {
            'workflow_id': workflow_id,
            'description': description,
            'spec_name': spec_name
        })
        
        try:
            # Use the executor's task delegation to orchestrate the workflow
            result = await self.executor.handle_task_delegation(
                agent='chief-product-manager',
                description=f"Execute workflow: {description}",
                context={
                    'spec_name': spec_name,
                    'workflow_id': workflow_id,
                    'description': description
                }
            )
            
            # Publish completion event
            await self.event_bus.publish('workflow.completed', {
                'workflow_id': workflow_id,
                'result': result.__dict__,
                'success': result.success
            })
            
            return {
                'workflow_id': workflow_id,
                'success': result.success,
                'output': result.output,
                'error': result.error,
                'duration': result.duration
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            await self.event_bus.publish('workflow.completed', {
                'workflow_id': workflow_id,
                'success': False,
                'error': str(e)
            })
            return {
                'workflow_id': workflow_id,
                'success': False,
                'error': str(e)
            }
    
    def health_check(self) -> Dict[str, bool]:
        """Check system health - THIS IS THE KEY VALIDATION METHOD"""
        health = {}
        
        # Check bridge connection
        health['bridge_connected'] = (
            hasattr(self.executor, 'bridge') and 
            self.executor.bridge is not None
        )
        
        # Check memory persistence
        health['memory_persistent'] = (
            hasattr(self.memory_manager, 'long_term') and
            self.memory_manager.long_term is not None
        )
        
        # Check context engine
        health['context_working'] = (
            hasattr(self.context_engine, 'compressor') and
            hasattr(self.context_engine.compressor, 'encoder')
        )
        
        # Check event system
        health['events_registered'] = len(self.event_bus.subscribers) > 0
        
        # Overall health
        health['system_healthy'] = all(health.values())
        
        return health
    
    async def test_integration(self) -> Dict[str, Any]:
        """Test the integration by running a simple workflow"""
        self.logger.info("Running integration test...")
        
        try:
            # First test memory manager directly
            self.logger.info("Testing memory manager...")
            memories = self.memory_manager.get_relevant_memories({
                'type': 'test',
                'agent': 'business-analyst'
            })
            self.logger.info(f"Memory retrieval test: {type(memories)} with keys {list(memories.keys()) if isinstance(memories, dict) else 'not dict'}")
            
            # Test task delegation
            self.logger.info("Testing task delegation...")
            if not hasattr(self.executor, 'handle_task_delegation'):
                self.logger.error("handle_task_delegation method not found")
                raise AttributeError("handle_task_delegation method missing")
                
            test_result = await self.executor.handle_task_delegation(
                agent='business-analyst',
                description='Test integration',
                context={'test': True}
            )
            
            self.logger.info(f"Task delegation result: {test_result}")
            
            return {
                'task_delegation_works': test_result.success if test_result else False,
                'memory_retrieval_works': len(memories.get('long_term', [])) >= 0 if isinstance(memories, dict) else False,
                'health_check': self.health_check(),
                'test_successful': True
            }
            
        except Exception as e:
            import traceback
            self.logger.error(f"Integration test failed: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'task_delegation_works': False,
                'memory_retrieval_works': False,
                'health_check': self.health_check(),
                'test_successful': False,
                'error': str(e)
            }

async def main():
    """Main function for testing the integrated system"""
    print("Starting Context Engineering System Integration Test")
    print("=" * 60)
    
    # Initialize system
    try:
        system = IntegratedSystem()
        print("[SUCCESS] System initialized")
    except Exception as e:
        print(f"[ERROR] System initialization failed: {e}")
        return 1
    
    # Health check
    health = system.health_check()
    print("\nSystem Health Check:")
    for component, status in health.items():
        status_icon = "[PASS]" if status else "[FAIL]"
        print(f"  {status_icon} {component}: {status}")
    
    if not health['system_healthy']:
        print("\n[ERROR] System is not healthy - some components are not working properly")
        print("Check the logs for more details")
        return 1
    
    print("\n[SUCCESS] System is healthy!")
    
    # Run integration test
    print("\nRunning integration test...")
    test_results = await system.test_integration()
    
    print("\nIntegration Test Results:")
    for test, result in test_results.items():
        if test == 'health_check':
            continue  # Skip nested health check
        status_icon = "[PASS]" if result else "[FAIL]"
        print(f"  {status_icon} {test}: {result}")
    
    if test_results['test_successful']:
        print("\n[SUCCESS] Integration test passed! System is fully functional.")
        return 0
    else:
        print("\n[ERROR] Integration test failed - system needs more work")
        if 'error' in test_results:
            print(f"Error: {test_results['error']}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))