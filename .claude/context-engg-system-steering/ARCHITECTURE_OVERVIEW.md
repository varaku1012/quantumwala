# Context Engineering System Architecture Overview

## Core Architecture Principle

The Claude Code multi-agent system follows a **Tool-Based Delegation Architecture** where agents use tools (especially the Task tool) to delegate work, rather than calling commands directly.

## System Layers

### Layer 1: Agent Definitions
- **Location**: `.claude/agents/`
- **Purpose**: Define agent capabilities and delegation patterns
- **Key Tool**: Task (for agent-to-agent delegation)
- **Design**: Simple, focused definitions (30-60 lines max)

### Layer 2: Tool Bridge
- **Location**: `.claude/scripts/agent_tool_bridge.py`
- **Purpose**: Intercept and route Task tool calls
- **Functions**:
  - Context optimization (70% token reduction)
  - Memory integration
  - Parallel execution management
  - Command/script routing

### Layer 3: Execution Scripts
- **Location**: `.claude/scripts/`
- **Purpose**: Actual implementation logic
- **Examples**:
  - `planning_executor.py` - Task planning and batching
  - `context_engine.py` - Context compression
  - `memory_manager.py` - Learning system
  - `real_executor.py` - Command execution

### Layer 4: User Commands
- **Location**: `.claude/commands/`
- **Purpose**: User-triggered workflows
- **Design**: Compose multiple operations into workflows

## Data Flow

```
User Request
    ↓
Chief Product Manager (Orchestrator)
    ↓ [Task tool delegation]
Agent Tool Bridge (Router)
    ↓ [Context optimization + Memory]
Specialized Agents (Workers)
    ↓ [Execution via scripts]
Results Aggregation
    ↓
User Response
```

## Key Components

### 1. Task Tool
- Primary delegation mechanism
- Passes agent name, description, and context
- Enables parallel execution groups

### 2. Context Engine
- Compresses context to fit windows (4000 tokens)
- Selects relevant information per agent
- Isolates contexts to prevent contamination
- Validates context integrity

### 3. Memory Manager
- Three-tier architecture (short/long/episodic)
- Learns from past executions
- Provides few-shot examples
- Enables performance optimization

### 4. Planning Executor
- Analyzes tasks for dependencies
- Creates parallel execution batches
- Optimizes workflow timing
- Generates execution strategies

## Performance Characteristics

- **Token Reduction**: 70% through compression
- **Execution Speed**: 50% faster with parallelization
- **Memory Learning**: Improves with each execution
- **Resource Management**: CPU 80%, Memory 75% limits
- **Parallel Tasks**: Maximum 8 concurrent

## Integration Points

### Agent → Bridge
```python
Task(agent="developer", description="task", context={})
    ↓
agent_tool_bridge.handle_task_call()
```

### Bridge → Executor
```python
executor.execute_agent_task(agent, description, context)
    ↓
Real Claude Code command execution
```

### Context Flow
```python
Raw Context → Compression → Selection → Isolation → Delivery
```

### Memory Integration
```python
Task → Retrieve Memories → Enrich Context → Execute → Store Result
```

## Critical Success Factors

1. **Agents use Task tool** for delegation (not commands)
2. **Bridge layer** routes and optimizes all delegations
3. **Context engineering** reduces tokens by 70%
4. **Memory system** learns from executions
5. **Parallel execution** when dependencies allow
6. **Resource management** prevents system overload

## Version Information

- **System Version**: 4.1
- **Architecture Pattern**: Tool-Based Delegation
- **Context Engineering**: Four-strategy approach
- **Memory Architecture**: Three-tier system
- **Parallel Execution**: Batch-based with dependency analysis