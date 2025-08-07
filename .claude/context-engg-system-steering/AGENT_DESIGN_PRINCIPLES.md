# Agent Design Principles

## Core Principles

### 1. Single Responsibility
Each agent should have ONE clear area of expertise and responsibility.

### 2. Tool-Based Delegation
Agents use tools (especially Task) for all operations, not direct command calls.

### 3. Context Awareness
Agents receive and pass optimized context through the bridge layer.

### 4. Simplicity First
Agent definitions should be 30-60 lines maximum. Complex logic belongs in scripts.

## Agent Types

### Orchestrators
- **Purpose**: Break down complex requests and delegate
- **Tools**: Task, Read, Write, CreateDirectory, ListDirectory
- **Examples**: chief-product-manager, product-manager
- **Pattern**:
  ```markdown
  1. Analyze request
  2. Identify required expertise
  3. Use Task tool to delegate
  4. Aggregate results
  5. Report to user
  ```

### Workers
- **Purpose**: Execute specific technical tasks
- **Tools**: Read, Write, Shell, specific to role
- **Examples**: developer, qa-engineer, business-analyst
- **Pattern**:
  ```markdown
  1. Receive task with context
  2. Execute using available tools
  3. Return structured results
  ```

### Specialists
- **Purpose**: Handle specialized domains requiring deep expertise
- **Tools**: Domain-specific tools + Task for sub-delegation
- **Examples**: security-engineer, performance-optimizer, genai-engineer
- **Pattern**:
  ```markdown
  1. Analyze specialized requirements
  2. Apply domain expertise
  3. May delegate specific fixes
  4. Provide expert recommendations
  ```

## Tool Access Matrix

| Agent Type | Task | Read | Write | Shell | CreateDirectory | ListDirectory |
|------------|------|------|-------|-------|-----------------|---------------|
| Orchestrators | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Workers | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Specialists | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

## Agent Definition Template

```markdown
---
name: agent-name
description: Clear, concise description of agent's purpose
tools: [List of allowed tools]
---

You are a [Role] specializing in [Domain].

## Core Responsibilities
1. [Primary responsibility]
2. [Secondary responsibility]
3. [Tertiary responsibility]

## Execution Protocol
[Step-by-step process the agent follows]

## Delegation Pattern (if has Task tool)
When to delegate:
- [Condition 1]: Delegate to [agent]
- [Condition 2]: Delegate to [agent]

## Output Format
[Expected structure of results]

## Quality Standards
[Specific quality criteria for this agent]
```

## Delegation Best Practices

### DO:
- ✅ Pass rich context when delegating
- ✅ Specify clear deliverables
- ✅ Include relevant constraints
- ✅ Provide examples when helpful
- ✅ Set success criteria

### DON'T:
- ❌ Delegate without context
- ❌ Create delegation chains > 3 deep
- ❌ Duplicate work across agents
- ❌ Skip result validation
- ❌ Ignore parallel opportunities

## Context Management

### What to Include in Delegation Context:
1. **Task Description**: Clear, specific ask
2. **Requirements**: Constraints and criteria
3. **Dependencies**: What this depends on
4. **Previous Results**: Relevant prior work
5. **Examples**: Few-shot examples if available

### Context Size Guidelines:
- **Minimum**: 100 tokens (too little context)
- **Optimal**: 1000-2000 tokens (balanced)
- **Maximum**: 4000 tokens (after compression)

## Parallel Execution Patterns

### Independent Tasks (Can Parallelize):
```python
parallel_group = [
    Task("developer", "frontend work"),
    Task("developer", "backend work"),
    Task("qa-engineer", "test planning")
]
```

### Dependent Tasks (Must Sequence):
```python
sequence = [
    Task("architect", "design system"),  # First
    Task("developer", "implement design"),  # Depends on design
    Task("qa-engineer", "test implementation")  # Depends on implementation
]
```

### Mixed Pattern:
```python
phase1 = [parallel_tasks]  # Run together
wait_for_completion()
phase2 = [dependent_tasks]  # Run after phase1
```

## Error Handling

### Agent Failures:
1. Capture error in result
2. Log for learning system
3. Consider fallback agent
4. Report issue clearly

### Delegation Failures:
1. Retry with enriched context
2. Try alternative agent
3. Escalate to orchestrator
4. Provide actionable error

## Performance Optimization

### Token Usage:
- Compress context before delegation
- Remove redundant information
- Use references instead of full content
- Batch related delegations

### Execution Time:
- Identify parallel opportunities
- Minimize delegation depth
- Cache frequent operations
- Use memory for similar tasks

## Evolution Guidelines

### When to Create New Agent:
- New domain expertise needed
- Current agents overloaded
- Specialization would improve quality
- Clear separation of concerns

### When to Modify Existing Agent:
- Minor capability addition
- Clarification of instructions
- Performance optimization
- Bug fixes in delegation logic

### When to Retire Agent:
- Functionality moved to another agent
- No longer used in workflows
- Replaced by better approach
- Maintenance burden too high