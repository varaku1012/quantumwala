# Code Objects Inventory
## Complete Listing of All Code Objects, Methods, and Functions

---

## 1. AgentToolBridge Module
**Path**: `.claude/scripts/agent_tool_bridge.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `AgentToolBridge` | Main bridge for Task tool delegation | ❌ Not Connected |
| `TaskRequest` | Data structure for task requests | ✅ Defined |
| `TaskToolHandler` | Handles Task tool calls | ❌ Not Used |
| `ExecutionResult` | Result data structure | ✅ Defined |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `__init__` | AgentToolBridge | `project_root: Path` | None | Initialize bridge | Add context_engine, memory_manager |
| `process_task_delegation` | AgentToolBridge | `task: TaskRequest` | `ExecutionResult` | Process task from agent | Connect to executor |
| `handle_task_call` | AgentToolBridge | `agent: str, description: str, context: Dict` | `Dict` | Handle Task tool call | Wire to real execution |
| `execute_parallel_group` | AgentToolBridge | `tasks: List[TaskRequest]` | `List[ExecutionResult]` | Execute tasks in parallel | Add thread safety |
| `_validate_request` | AgentToolBridge | `request: TaskRequest` | `bool` | Validate task request | Add validation logic |
| `_enrich_context` | AgentToolBridge | `context: Dict` | `Dict` | Add memories to context | Connect to memory_manager |

---

## 2. ContextEngine Module
**Path**: `.claude/scripts/context_engine.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `ContextEngine` | Main context orchestrator | ⚠️ Partial |
| `ContextCompressor` | Token reduction | ❌ Fake Tokens |
| `ContextSelector` | Relevance filtering | ✅ Works |
| `ContextValidator` | Input validation | ✅ Works |
| `ContextIsolator` | Isolation (NOT IMPLEMENTED) | ❌ Missing |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `prepare_context` | ContextEngine | `agent_type: str, task: Dict, full_context: Dict` | `Dict` | Prepare optimized context | None |
| `compress` | ContextCompressor | `text: str, max_tokens: int` | `str` | Compress text | Use real tiktoken |
| `count_tokens` | ContextCompressor | `text: str` | `int` | Count tokens | Replace len(text)//4 |
| `select_relevant` | ContextSelector | `context: Dict, agent_type: str` | `Dict` | Filter relevant context | None |
| `validate` | ContextValidator | `context: Dict` | `bool` | Validate context structure | None |
| `isolate` | ContextIsolator | `context: Dict` | `Dict` | Isolate sensitive data | Implement method |
| `_compress_whitespace` | ContextCompressor | `text: str` | `str` | Remove extra whitespace | None |
| `_remove_comments` | ContextCompressor | `text: str` | `str` | Remove code comments | Preserve docstrings |
| `_summarize_sections` | ContextCompressor | `text: str, max_tokens: int` | `str` | Summarize long text | Add AI summarization |
| `_truncate_to_fit` | ContextCompressor | `text: str, max_tokens: int` | `str` | Truncate to token limit | None |

---

## 3. MemoryManager Module
**Path**: `.claude/scripts/memory_manager.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `MemoryManager` | Three-tier memory system | ❌ No Persistence |
| `MemoryTier` | Memory tier enum | ✅ Defined |
| `MemoryEntry` | Memory data structure | ✅ Defined |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `__init__` | MemoryManager | `project_root: Path` | None | Initialize manager | Add database connection |
| `store_execution` | MemoryManager | `task_id: str, agent: str, result: Any` | `None` | Store execution result | Add persistence |
| `get_relevant_memories` | MemoryManager | `task: Dict, limit: int` | `List[Dict]` | Get relevant memories | Add indexing |
| `get_recent` | MemoryManager | `limit: int` | `List[Dict]` | Get recent memories | Query database |
| `get_episodic_example` | MemoryManager | `task_type: str` | `Optional[Dict]` | Get successful example | Load from database |
| `cleanup_old_memories` | MemoryManager | `days: int` | `int` | Clean old memories | Implement deletion |
| `_init_db` | MemoryManager | None | None | Initialize database | Create tables |
| `_cleanup_short_term` | MemoryManager | None | None | Clean short-term memory | Implement |
| `_is_relevant` | MemoryManager | `memory: Dict, task: Dict` | `bool` | Check relevance | Enhance logic |
| `_load_episodic_memories` | MemoryManager | None | None | Load episodic memories | Query database |

---

## 4. RealExecutor Module
**Path**: `.claude/scripts/real_executor.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `RealClaudeExecutor` | Execute commands | ❌ No Bridge |
| `ExecutionContext` | Execution context | ✅ Defined |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `__init__` | RealClaudeExecutor | `project_root: Path` | None | Initialize executor | Add bridge |
| `execute_command` | RealClaudeExecutor | `command: str, context: Dict` | `Dict` | Execute command | Add error handling |
| `handle_task_delegation` | RealClaudeExecutor | `agent: str, description: str, context: Dict` | `Dict` | Handle Task tool | Implement |
| `_prepare_environment` | RealClaudeExecutor | `context: Dict` | `Dict` | Prepare execution env | None |
| `_validate_command` | RealClaudeExecutor | `command: str` | `bool` | Validate command safety | Add validation |
| `_execute_python` | RealClaudeExecutor | `script: str, args: List` | `Dict` | Execute Python script | Use SecureExecutor |
| `_execute_shell` | RealClaudeExecutor | `command: str` | `Dict` | Execute shell command | Remove shell=True |

---

## 5. UnifiedWorkflow Module
**Path**: `.claude/scripts/unified_workflow.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `UnifiedWorkflow` | Main workflow controller | ⚠️ Partial |
| `WorkflowMode` | Execution mode enum | ✅ Defined |
| `AutomationLevel` | Automation level enum | ✅ Defined |
| `MonitoringLevel` | Monitoring level enum | ✅ Defined |
| `WorkflowState` | Workflow state | ✅ Defined |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `execute` | UnifiedWorkflow | `description: str, spec_name: str` | `Dict` | Execute workflow | Use bridge |
| `_sequential_workflow` | UnifiedWorkflow | None | `Dict` | Sequential execution | Connect to bridge |
| `_parallel_workflow` | UnifiedWorkflow | None | `Dict` | Parallel execution | Add thread safety |
| `_optimized_workflow` | UnifiedWorkflow | None | `Dict` | Optimized execution | Implement optimization |
| `_execute_phase` | UnifiedWorkflow | `phase_name: str, agent: str, context: Dict` | `Dict` | Execute single phase | Use bridge |
| `_prepare_phase_context` | UnifiedWorkflow | `phase: str` | `Dict` | Prepare phase context | Use ContextEngine |
| `_store_phase_result` | UnifiedWorkflow | `phase: str, result: Dict` | None | Store phase result | Use MemoryManager |
| `_should_continue` | UnifiedWorkflow | None | `bool` | Check if should continue | Add logic |
| `_handle_error` | UnifiedWorkflow | `error: Exception` | `Dict` | Handle workflow error | Implement recovery |

---

## 6. ParallelWorkflowOrchestrator Module
**Path**: `.claude/scripts/parallel_workflow_orchestrator.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `ParallelWorkflowOrchestrator` | Parallel task execution | ❌ Thread Issues |
| `PhaseTask` | Task definition | ✅ Defined |
| `WorkflowPhase` | Phase grouping | ✅ Defined |
| `DependencyGraph` | Task dependencies | ✅ Defined |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `execute_workflow` | ParallelWorkflowOrchestrator | `phases: List[WorkflowPhase]` | `Dict` | Execute workflow | Add thread safety |
| `_execute_phase` | ParallelWorkflowOrchestrator | `phase: WorkflowPhase` | `Dict` | Execute phase | Use ThreadPoolExecutor |
| `_execute_task` | ParallelWorkflowOrchestrator | `task: PhaseTask` | `Dict` | Execute single task | Add error handling |
| `_can_execute` | ParallelWorkflowOrchestrator | `task: PhaseTask` | `bool` | Check dependencies | None |
| `_build_dependency_graph` | ParallelWorkflowOrchestrator | `tasks: List[PhaseTask]` | `DependencyGraph` | Build dependency graph | None |
| `_topological_sort` | ParallelWorkflowOrchestrator | `graph: DependencyGraph` | `List[PhaseTask]` | Sort by dependencies | None |
| `_wait_for_dependencies` | ParallelWorkflowOrchestrator | `task: PhaseTask` | None | Wait for dependencies | Add timeout |

---

## 7. WorkflowMonitor Module
**Path**: `.claude/scripts/workflow_monitor.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `WorkflowMonitor` | Performance monitoring | ✅ Works |
| `PerformanceMetric` | Metric data | ✅ Defined |
| `WorkflowBottleneck` | Bottleneck info | ✅ Defined |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `start_monitoring` | WorkflowMonitor | None | None | Start monitoring | None |
| `stop_monitoring` | WorkflowMonitor | None | None | Stop monitoring | None |
| `log_metric` | WorkflowMonitor | `metric: PerformanceMetric` | None | Log metric | None |
| `_monitor_file_changes` | WorkflowMonitor | None | None | Monitor files | None |
| `_monitor_system_resources` | WorkflowMonitor | None | None | Monitor CPU/memory | None |
| `_monitor_agent_executions` | WorkflowMonitor | None | None | Monitor agents | None |
| `_analyze_performance` | WorkflowMonitor | None | None | Analyze metrics | None |
| `_identify_bottlenecks` | WorkflowMonitor | None | `List[WorkflowBottleneck]` | Find bottlenecks | None |
| `_generate_report` | WorkflowMonitor | None | `str` | Generate report | None |
| `_save_analysis` | WorkflowMonitor | None | None | Save analysis | None |

---

## 8. GroomingWorkflow Module
**Path**: `.claude/scripts/grooming_workflow.py`

### Classes
| Class | Purpose | Status |
|-------|---------|--------|
| `GroomingWorkflow` | Feature grooming | ✅ Works |
| `GroomingPhase` | Grooming phase enum | ✅ Defined |

### Methods
| Method | Class | Parameters | Returns | Purpose | Fix Required |
|--------|-------|------------|---------|---------|--------------|
| `start_grooming` | GroomingWorkflow | `feature_name: str` | `Dict` | Start grooming | None |
| `prioritize_feature` | GroomingWorkflow | `feature_name: str` | `Dict` | Prioritize feature | None |
| `create_roadmap` | GroomingWorkflow | `feature_name: str` | `Dict` | Create roadmap | None |
| `complete_grooming` | GroomingWorkflow | `feature_name: str` | `Dict` | Complete grooming | None |
| `_save_grooming_state` | GroomingWorkflow | `state: Dict` | None | Save state | None |
| `_load_grooming_state` | GroomingWorkflow | `feature_name: str` | `Dict` | Load state | None |

---

## 9. Custom Tools

### MemoryTool (`memory_tool.py`)
| Function | Parameters | Returns | Purpose | Fix Required |
|----------|-----------|---------|---------|--------------|
| `store` | `key: str, value: str, agent: str` | None | Store memory | Use MemoryManager |
| `retrieve` | `key: str` | `str` | Retrieve memory | Query database |
| `search` | `query: str` | `List[Dict]` | Search memories | Add indexing |
| `recent` | `limit: int` | `List[Dict]` | Get recent | Query database |

### SpecTool (`spec_tool.py`)
| Function | Parameters | Returns | Purpose | Fix Required |
|----------|-----------|---------|---------|--------------|
| `create` | `name: str, description: str` | `Dict` | Create spec | None |
| `validate` | `spec_name: str` | `bool` | Validate spec | None |
| `generate_tasks` | `spec_name: str` | `List[Dict]` | Generate tasks | None |
| `update_status` | `spec_name: str, phase: str` | None | Update status | None |
| `list` | None | `List[str]` | List specs | None |

### ContextTool (`context_tool.py`)
| Function | Parameters | Returns | Purpose | Fix Required |
|----------|-----------|---------|---------|--------------|
| `compress` | `text: str, max_tokens: int` | `str` | Compress text | Use ContextEngine |
| `extract` | `text: str, query: str` | `str` | Extract relevant | None |
| `merge` | `context1: Dict, context2: Dict` | `Dict` | Merge contexts | None |
| `validate` | `context: Dict` | `bool` | Validate context | None |
| `summarize` | `text: str, max_length: int` | `str` | Summarize text | Add AI model |

---

## 10. Critical Functions to Fix

### Priority 0 (Immediate)
1. **AgentToolBridge.process_task_delegation** - Connect to executor
2. **ContextCompressor.count_tokens** - Use real tiktoken
3. **MemoryManager.__init__** - Add database connection
4. **RealClaudeExecutor.__init__** - Add bridge initialization

### Priority 1 (Week 1)
5. **UnifiedWorkflow._execute_phase** - Use bridge for delegation
6. **MemoryManager.store_execution** - Add persistence
7. **SecureExecutor.execute** - Replace all shell=True
8. **ContextCompressor.compress** - Fix compression logic

### Priority 2 (Week 2)
9. **ParallelWorkflowOrchestrator._execute_phase** - Add thread safety
10. **ContextIsolator.isolate** - Implement isolation
11. **EventBus.publish** - Implement event system
12. **IntegratedSystem._wire_components** - Wire all components

---

## 11. New Functions to Create

### EventBus System
```python
class EventBus:
    def subscribe(event_type: str, handler: Callable)
    def unsubscribe(event_type: str, handler: Callable)
    async def publish(event: Dict)
    def _process_event_queue()
```

### IntegratedSystem
```python
class IntegratedSystem:
    def __init__(project_root: Path)
    def _wire_components()
    def _register_handlers()
    async def execute_workflow(description: str, spec_name: str)
    def health_check() -> Dict[str, bool]
```

### SecureExecutor
```python
class SecureExecutor:
    def validate_command(command: str, args: List[str]) -> bool
    def validate_path(user_path: str) -> Path
    def execute(command: str, args: List[str], timeout: int)
```

---

## 12. Function Call Graph

### Main Execution Flow
```
user_command
    ↓
/workflow
    ↓
UnifiedWorkflow.execute()
    ↓
UnifiedWorkflow._execute_phase()
    ↓
RealClaudeExecutor.handle_task_delegation()  [BROKEN]
    ↓
AgentToolBridge.process_task_delegation()  [NOT CONNECTED]
    ├── ContextEngine.prepare_context()
    ├── MemoryManager.get_relevant_memories()
    ├── Execute task
    └── MemoryManager.store_execution()
```

### Context Processing Flow
```
raw_context
    ↓
ContextEngine.prepare_context()
    ├── ContextValidator.validate()
    ├── ContextSelector.select_relevant()
    ├── ContextCompressor.compress()
    │   ├── count_tokens()  [BROKEN - fake count]
    │   ├── _compress_whitespace()
    │   ├── _remove_comments()
    │   └── _truncate_to_fit()
    └── ContextIsolator.isolate()  [NOT IMPLEMENTED]
```

### Memory Flow
```
task_result
    ↓
MemoryManager.store_execution()
    ├── Store in short_term{}  [In-memory only]
    ├── Store in long_term  [NO DATABASE]
    └── Update episodic  [NOT IMPLEMENTED]
```

---

## Summary Statistics

### Total Code Objects
- **Classes**: 35
- **Methods/Functions**: 150+
- **Critical Fixes Required**: 40
- **New Functions Needed**: 15

### Fix Priority Distribution
- **P0 (Immediate)**: 4 functions
- **P1 (Week 1)**: 8 functions  
- **P2 (Week 2)**: 12 functions
- **P3 (Week 3)**: 16 functions

### Estimated Fix Time
- **Per P0 Function**: 1-2 hours
- **Per P1 Function**: 2-4 hours
- **Per P2 Function**: 1-3 hours
- **Per P3 Function**: 0.5-2 hours

**Total Estimated Time**: 80-120 hours of development

---

**Next Action**: Start with fixing the 4 P0 functions in this order:
1. RealClaudeExecutor.__init__ (add bridge)
2. AgentToolBridge.process_task_delegation (connect)
3. MemoryManager.__init__ (add database)
4. ContextCompressor.count_tokens (use tiktoken)