# Integration Matrix - Component Relationships
## System Component Dependencies and Data Flow

---

## 1. Component Dependency Matrix

### Legend
- ✅ = Connected and Working
- ⚠️ = Partial Connection
- ❌ = Not Connected (Should Be)
- ➖ = Not Required
- 🔄 = Circular Dependency (Problem)

| Component | Bridge | Context | Memory | Executor | Workflow | Monitor | Tools | Agents |
|-----------|--------|---------|--------|----------|----------|---------|-------|--------|
| **AgentToolBridge** | - | ❌ | ❌ | ❌ | ❌ | ➖ | ❌ | ❌ |
| **ContextEngine** | ❌ | - | 🔄 | ❌ | ❌ | ➖ | ⚠️ | ❌ |
| **MemoryManager** | ❌ | 🔄 | - | ❌ | ❌ | ➖ | ⚠️ | ❌ |
| **RealExecutor** | ❌ | ❌ | ❌ | - | ⚠️ | ➖ | ❌ | ❌ |
| **UnifiedWorkflow** | ❌ | ❌ | ❌ | ⚠️ | - | ⚠️ | ❌ | ⚠️ |
| **WorkflowMonitor** | ➖ | ➖ | ➖ | ➖ | ⚠️ | - | ➖ | ➖ |
| **CustomTools** | ❌ | ⚠️ | ⚠️ | ❌ | ❌ | ➖ | - | ❌ |
| **Agents** | ❌ | ❌ | ❌ | ❌ | ⚠️ | ➖ | ❌ | - |

---

## 2. Data Flow Paths

### 2.1 Current (Broken) Flow
```
User Input
    ↓
/workflow command
    ↓
unified_workflow.py
    ↓ [BROKEN - No Bridge]
    ✗ agent_tool_bridge.py (not connected)
    ↓
real_executor.py (executes without context)
    ↓
Agent Execution (no memory persistence)
    ↓
Result (no monitoring data)
```

### 2.2 Intended (Fixed) Flow
```
User Input
    ↓
/workflow command
    ↓
unified_workflow.py
    ↓
agent_tool_bridge.py ← context_engine.py
    ↓                    ← memory_manager.py
real_executor.py
    ↓
Agent Execution → workflow_monitor.py
    ↓             → memory_manager.py (store)
Result → Dashboard
```

---

## 3. Critical Integration Points

### 3.1 AgentToolBridge Integration

**Current State**: Completely disconnected

**Required Connections**:
```python
# In real_executor.py
from agent_tool_bridge import AgentToolBridge

class RealClaudeExecutor:
    def __init__(self):
        self.bridge = AgentToolBridge()
        self.bridge.context_engine = ContextEngine()
        self.bridge.memory_manager = MemoryManager()
```

**Data Flow**:
1. Receives Task tool calls from agents
2. Enriches with context from ContextEngine
3. Logs to MemoryManager
4. Executes via RealExecutor
5. Returns results to agent

### 3.2 ContextEngine Integration

**Current State**: Isolated, fake token counting

**Required Connections**:
```python
# In agent_tool_bridge.py
self.context_engine = ContextEngine()
context = self.context_engine.prepare_context(
    agent_type=request.agent,
    task=request.task,
    full_context=self.memory_manager.get_context()
)
```

**Data Flow**:
1. Receives raw context from various sources
2. Compresses using real tiktoken
3. Selects relevant portions
4. Isolates sensitive data
5. Returns optimized context

### 3.3 MemoryManager Integration

**Current State**: In-memory only, no persistence

**Required Connections**:
```python
# In memory_manager.py
import sqlite3

class MemoryManager:
    def __init__(self):
        self.db = sqlite3.connect('.claude/data/memory.db')
        
    def store_execution(self, task_id, agent, result):
        # Store in database
        
    def get_relevant_memories(self, task):
        # Query database
```

**Data Flow**:
1. Receives execution results
2. Stores in SQLite/PostgreSQL
3. Indexes for fast retrieval
4. Provides context for future tasks
5. Maintains episodic examples

---

## 4. Component Communication Patterns

### 4.1 Event Bus Pattern (Recommended)
```python
class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, event_type, handler):
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event):
        for handler in self.subscribers[event.type]:
            await handler(event)

# Usage
bus = EventBus()
bus.subscribe('task.completed', memory_manager.store_execution)
bus.subscribe('task.completed', monitor.log_metric)
bus.subscribe('context.needed', context_engine.prepare)
```

### 4.2 Dependency Injection Pattern
```python
class SystemOrchestrator:
    def __init__(self, 
                 bridge: AgentToolBridge,
                 context: ContextEngine,
                 memory: MemoryManager,
                 executor: RealClaudeExecutor):
        self.bridge = bridge
        self.context = context
        self.memory = memory
        self.executor = executor
        
        # Wire dependencies
        self.bridge.context_engine = context
        self.bridge.memory_manager = memory
        self.executor.bridge = bridge
```

---

## 5. API Contracts

### 5.1 Task Delegation Contract
```python
@dataclass
class TaskRequest:
    agent: str
    description: str
    context: Dict
    parent_agent: Optional[str]
    priority: int = 1
    timeout: int = 300

@dataclass
class TaskResult:
    success: bool
    output: Any
    error: Optional[str]
    metrics: Dict
    duration: float
```

### 5.2 Context Contract
```python
@dataclass
class ContextRequest:
    agent_type: str
    task: Dict
    max_tokens: int = 4000
    include_memories: bool = True
    compression_level: int = 2

@dataclass
class ContextResponse:
    context: Dict
    token_count: int
    compression_ratio: float
    memories_included: List[str]
```

### 5.3 Memory Contract
```python
@dataclass
class MemoryEntry:
    id: str
    task_id: str
    agent: str
    timestamp: datetime
    context: Dict
    result: Any
    success: bool
    duration: float
    tokens_used: int
```

---

## 6. Integration Testing Requirements

### 6.1 Unit Integration Tests
```python
# Test Bridge-Context Integration
def test_bridge_uses_context_engine():
    bridge = AgentToolBridge()
    context_engine = Mock(ContextEngine)
    bridge.context_engine = context_engine
    
    bridge.process_task_delegation(task_request)
    context_engine.prepare_context.assert_called_once()

# Test Bridge-Memory Integration
def test_bridge_stores_in_memory():
    bridge = AgentToolBridge()
    memory = Mock(MemoryManager)
    bridge.memory_manager = memory
    
    result = bridge.process_task_delegation(task_request)
    memory.store_execution.assert_called_with(
        task_id=ANY, agent=ANY, result=result
    )
```

### 6.2 End-to-End Integration Tests
```python
@pytest.mark.integration
async def test_full_workflow():
    # Setup integrated system
    system = IntegratedSystem()
    
    # Execute workflow
    result = await system.execute_workflow(
        description="test feature",
        spec_name="test-spec"
    )
    
    # Verify all components worked together
    assert result['success']
    assert system.memory_manager.get_recent(1)
    assert system.monitor.metrics
```

---

## 7. Integration Priority Order

### Phase 1: Critical Connections (Week 1)
1. **Connect AgentToolBridge to RealExecutor**
   - File: `real_executor.py`
   - Import and initialize bridge
   
2. **Add Database to MemoryManager**
   - File: `memory_manager.py`
   - SQLite connection and schema

3. **Fix Token Counting in ContextEngine**
   - File: `context_engine.py`
   - Use real tiktoken

### Phase 2: Core Integration (Week 2)
4. **Wire Bridge to Context and Memory**
   - File: `agent_tool_bridge.py`
   - Add dependencies

5. **Connect Workflow to Bridge**
   - File: `unified_workflow.py`
   - Use bridge for delegation

6. **Add Error Handling**
   - All files
   - Try-catch, recovery

### Phase 3: Advanced Integration (Week 3)
7. **Implement Event Bus**
   - New file: `event_bus.py`
   - Loose coupling

8. **Connect Monitoring**
   - File: `workflow_monitor.py`
   - Subscribe to events

9. **Wire Dashboard**
   - File: `dashboard.html`
   - WebSocket connection

---

## 8. Monitoring Integration Health

### 8.1 Health Check Endpoints
```python
class IntegrationHealthCheck:
    async def check_all(self) -> Dict:
        return {
            'bridge_connected': self._check_bridge(),
            'context_working': self._check_context(),
            'memory_persistent': self._check_memory(),
            'executor_ready': self._check_executor(),
            'workflow_functional': self._check_workflow(),
            'monitor_active': self._check_monitor()
        }
    
    def _check_bridge(self) -> bool:
        # Verify bridge is wired to executor
        return hasattr(self.executor, 'bridge')
    
    def _check_memory(self) -> bool:
        # Verify database connection
        return self.memory.db is not None
```

### 8.2 Integration Metrics
```python
integration_metrics = {
    'bridge_calls': Counter('bridge_task_calls_total'),
    'context_compressions': Counter('context_compressions_total'),
    'memory_operations': Counter('memory_operations_total'),
    'integration_errors': Counter('integration_errors_total'),
    'circular_dependencies': Gauge('circular_dependencies_detected')
}
```

---

## 9. Breaking Changes to Fix

### 9.1 Circular Dependencies
**Problem**: `context_engine.py` ↔ `memory_manager.py`

**Solution**:
```python
# Create interface/protocol
from typing import Protocol

class MemoryProvider(Protocol):
    def get_relevant_memories(self, task: Dict) -> List[Dict]:
        ...

class ContextProvider(Protocol):
    def prepare_context(self, agent: str, task: Dict) -> Dict:
        ...
```

### 9.2 Shell Tool Usage in Agents
**Problem**: Agents can't execute Python scripts via Shell

**Solution**:
1. Create proper custom tools
2. Register tools with Claude Code
3. Update agent definitions

---

## 10. Success Criteria

### Integration is successful when:
1. ✅ All components in matrix show ✅ or ➖
2. ✅ No circular dependencies (🔄)
3. ✅ End-to-end test passes
4. ✅ Health checks all green
5. ✅ No integration errors in 24 hours
6. ✅ Memory persists across restarts
7. ✅ Token counting accurate within 5%
8. ✅ Dashboard shows real-time data
9. ✅ All security vulnerabilities fixed
10. ✅ Performance meets targets

---

**Current Integration Score**: 35/100
**Target Integration Score**: 95/100
**Estimated Time to Fix**: 3 weeks with focused effort