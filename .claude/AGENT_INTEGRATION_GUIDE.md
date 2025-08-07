# Agent Integration Guide - Proper Claude Code Architecture

## Overview

This guide explains the CORRECT way to implement sub-agents in Claude Code using the Task tool for delegation.

## Core Concepts

### 1. Agents Have Tools, Not Commands
- Agents use **tools** defined in their YAML frontmatter
- The **Task tool** is how agents delegate to other agents
- Commands are workflows that can be triggered, but agents shouldn't call them directly

### 2. Proper Agent Definition
```markdown
---
name: agent-name
description: What this agent does
tools: Task, Read, Write, Shell, CreateDirectory, ListDirectory
---
```

### 3. Task Tool Usage
When an agent needs to delegate:
```
Use Task tool to delegate to [agent-name]:
- Description: "What needs to be done"
- Context: {relevant data for the task}
```

## Architecture Flow

```
User Request
    ↓
Chief Product Manager (orchestrator)
    ↓ (uses Task tool)
Specialized Agents (workers)
    ↓ (return results)
Chief PM consolidates
    ↓
User gets result
```

## Implementation Layers

### Layer 1: Agent Definitions (.claude/agents/)
- Simple, focused agent definitions
- Clear tool access (Task, Read, Write, etc.)
- Delegation instructions using Task tool

### Layer 2: Tool Bridge (.claude/scripts/agent_tool_bridge.py)
- Intercepts Task tool calls
- Routes to appropriate execution
- Manages context and memory
- Handles parallel execution

### Layer 3: Command Execution (.claude/scripts/)
- Actual implementation logic
- Can be complex Python scripts
- Handles the heavy lifting

### Layer 4: Commands (.claude/commands/)
- User-facing workflows
- Can be triggered manually
- Compose multiple operations

## Proper Agent Patterns

### Pattern 1: Orchestrator Agent
```markdown
---
name: chief-product-manager
tools: Task, Read, Write
---

When given a request:
1. Analyze what's needed
2. Use Task tool to delegate to business-analyst
3. Use Task tool to delegate to architect
4. Consolidate results
```

### Pattern 2: Worker Agent
```markdown
---
name: developer
tools: Read, Write, Shell
---

When given a task:
1. Read relevant files
2. Write implementation
3. Run tests with Shell
4. Return results
```

### Pattern 3: Specialist Agent
```markdown
---
name: security-engineer
tools: Read, Shell, Task
---

When security analysis needed:
1. Read code with Read tool
2. Run security scans with Shell
3. If issues found, use Task to delegate fixes to developer
```

## Integration Points

### 1. Task Delegation
```python
# When chief-PM uses Task tool:
Task(agent="developer", description="implement user model")
    ↓
# agent_tool_bridge.py intercepts:
async def handle_task_call(agent, description, context):
    # Route to appropriate execution
    # Manage context
    # Return results
```

### 2. Context Flow
```python
# Context is compressed and passed:
Original Context (20KB)
    ↓ (compression)
Optimized Context (4KB)
    ↓ (add memories)
Enriched Context (5KB)
    ↓
Target Agent receives
```

### 3. Parallel Execution
```python
# Bridge identifies parallel opportunities:
parallel_tasks = [
    Task("developer", "frontend"),
    Task("developer", "backend"),
    Task("qa-engineer", "tests")
]
results = await execute_parallel(parallel_tasks)
```

## Development Workflow

### Step 1: Define Your Agent
Create `.claude/agents/my-agent.md`:
```markdown
---
name: my-agent
description: What it does
tools: Task, Read, Write
---
Instructions for the agent...
```

### Step 2: Add to Bridge
Update `agent_tool_bridge.py`:
```python
self.agent_strategies = {
    'my-agent': self._execute_my_agent,
    ...
}

async def _execute_my_agent(self, description, context):
    # Implementation
```

### Step 3: Test Integration
```python
# Test the delegation:
handler = TaskToolHandler()
result = await handler.handle_task_call(
    agent="my-agent",
    description="do something",
    context={...}
)
```

## Best Practices

### DO:
- ✅ Use Task tool for agent-to-agent delegation
- ✅ Keep agent definitions simple and focused
- ✅ Implement complex logic in Python scripts
- ✅ Pass rich context when delegating
- ✅ Track all delegations for learning

### DON'T:
- ❌ Have agents call commands directly
- ❌ Put complex logic in agent definitions
- ❌ Skip context optimization
- ❌ Forget to handle parallel execution
- ❌ Mix orchestration and execution in one agent

## Common Patterns

### 1. Phased Execution
```python
phases = [
    ("analysis", ["business-analyst", "architect"]),
    ("design", ["uiux-designer", "data-engineer"]),
    ("implementation", ["developer"]),
    ("validation", ["qa-engineer", "security-engineer"])
]
```

### 2. Conditional Delegation
```python
if "api" in description:
    delegate_to = "api-integration-specialist"
elif "ui" in description:
    delegate_to = "uiux-designer"
else:
    delegate_to = "developer"
```

### 3. Result Aggregation
```python
results = await gather_all_delegations()
consolidated = merge_results(results)
return consolidated
```

## Troubleshooting

### Issue: Agent not delegating properly
- Check tools list includes "Task"
- Verify agent_tool_bridge.py has strategy for target agent
- Ensure context is being passed correctly

### Issue: Context too large
- Context engine should compress automatically
- Check compression settings in context_engine.py
- Consider splitting into multiple delegations

### Issue: Parallel tasks not executing
- Verify parallel_group is set in TaskRequest
- Check execute_parallel_group implementation
- Ensure no dependencies between parallel tasks

## Next Steps

1. Refactor existing agents to use Task tool
2. Implement missing strategies in agent_tool_bridge.py
3. Add performance tracking for delegations
4. Create integration tests for common workflows
5. Document agent capabilities for team

Remember: The power is in the Task tool delegation, not in complex agent definitions!