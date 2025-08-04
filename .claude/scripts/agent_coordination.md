# Sub-Agent Coordination in Claude Code

## How Sub-Agents Communicate

### 1. Claude Code's Automatic Delegation
Claude Code automatically selects the appropriate sub-agent based on the task context and the agent's description field:

```markdown
---
name: product-manager
description: Use for product vision, feature prioritization, roadmap planning
tools: Read, Write
---
```

When you ask about product features, Claude Code will automatically delegate to the product-manager agent.

### 2. Suggesting Next Agents in Output
Sub-agents can suggest which agent should handle the next step:

```markdown
# Product Manager Agent
---
name: product-manager
description: Product vision and feature planning
---

You are a Product Manager. When you complete your analysis:

## Integration Points
At the end of your output, always include:
- "Next: Use business-analyst agent to create detailed requirements"
- "Next: Use architect agent to assess technical feasibility"

Example output format:
"""
## Product Vision
[Your analysis here]

## Recommended Next Steps
→ Use **business-analyst** agent to detail these requirements
→ Use **architect** agent to validate technical approach
"""
```

### 3. Workflow Commands that Chain Agents
Create slash commands that orchestrate multiple agents in sequence:

```markdown
# commands/full-analysis.md
Perform complete analysis using multiple agents.

Process:
1. First, I'll use the product-manager agent to understand the vision
2. Then, I'll use the business-analyst agent for requirements
3. Finally, I'll use the architect agent for technical design

When you run this command, I'll coordinate between all three agents and compile their outputs.
```

### 4. Explicit Agent Invocation in Prompts
You can explicitly request specific agents in your prompts:

```bash
# Direct invocation
> Use product-manager agent to analyze this feature idea

# Sequential invocation
> Use product-manager to create vision, then use business-analyst for requirements

# Conditional invocation
> If this involves UI changes, use uiux-designer agent
```

### 5. Task Tool for Parallel Agent Execution
Use Claude Code's Task Tool to run multiple agents simultaneously:

```bash
> Analyze this feature using 3 parallel tasks:
  Task 1: Use product-manager for business value
  Task 2: Use architect for technical feasibility  
  Task 3: Use uiux-designer for user experience
```

## Practical Examples

### Example 1: Product Manager Suggesting Next Agents

**Product Manager Agent Output:**
```markdown
## Feature Analysis: Real-time Collaboration

### Business Value
- Increases user engagement by 40%
- Differentiates from competitors
- Enables new pricing tier

### Initial Requirements
- Multi-user cursors
- Conflict resolution
- Activity indicators

### 🔄 Recommended Next Actions:
**For Requirements**: Please use the `business-analyst` agent to:
- Create detailed user stories
- Define acceptance criteria
- Document edge cases

**For Technical Design**: Please use the `architect` agent to:
- Evaluate WebSocket vs SSE
- Design conflict resolution
- Plan database changes

**For UI/UX**: Please use the `uiux-designer` agent to:
- Design cursor indicators
- Create presence UI
- Define interaction patterns
```

### Example 2: Workflow Command Orchestration

```markdown
# commands/feature-workflow.md
Execute complete feature development workflow.

I'll coordinate the following agents in sequence:

```bash
# Step 1: Product Analysis
echo "=== PRODUCT VISION ==="
# Invoke product-manager agent

# Step 2: Requirements (based on Step 1 output)
echo "=== DETAILED REQUIREMENTS ==="
# Invoke business-analyst agent with context from Step 1

# Step 3: Technical Design (based on Steps 1 & 2)
echo "=== ARCHITECTURE ==="
# Invoke architect agent with accumulated context

# Step 4: Task Breakdown
echo "=== IMPLEMENTATION TASKS ==="
# Generate tasks based on all previous outputs
```

This creates a natural flow where each agent builds on the previous agent's work.
```

### Example 3: Context Passing Between Agents

```markdown
# Enhanced Product Manager Agent
---
name: product-manager
description: Product vision and planning
---

When completing analysis, structure your output to facilitate handoff:

## Output Template
```yaml
feature_analysis:
  name: "Feature Name"
  priority: "P0|P1|P2"
  
  # For business-analyst agent
  requirements_context:
    user_types: ["admin", "user", "guest"]
    key_workflows: 
      - "Workflow 1"
      - "Workflow 2"
    acceptance_criteria_hints:
      - "Must work offline"
      - "Must sync in real-time"
  
  # For architect agent  
  technical_context:
    scale_requirements: "1000 concurrent users"
    performance_targets: "<200ms response"
    integration_points: ["API", "Database", "Cache"]
  
  # For uiux-designer agent
  design_context:
    user_personas: ["Power User", "Casual User"]
    ui_priorities: ["Speed", "Clarity", "Mobile-first"]
```

This structured output helps the next agents understand what to focus on.
```

### Example 4: Conditional Agent Selection

```markdown
# commands/smart-review.md
Intelligently review code using appropriate agents.

Based on the changes detected:
- If UI files modified → use uiux-designer to review design consistency
- If API files modified → use architect to review API design
- If test files modified → use qa-engineer to review test coverage
- Always → use code-reviewer for general quality

The review will adapt based on what was actually changed.
```

## Best Practices for Agent Coordination

### 1. Clear Handoff Points
```markdown
## Handoff to Next Agent
**Agent**: business-analyst
**Context**: Focus on the real-time sync requirements
**Deliverables Needed**: 
- User stories for conflict resolution
- Data model for collaborative state
```

### 2. Structured Output for Easy Parsing
```markdown
## Requirements Summary
KEY_REQUIREMENTS:
- REQ001: User authentication required
- REQ002: Real-time sync within 100ms
- REQ003: Offline capability

NEXT_AGENT_FOCUS:
- architect: Evaluate WebSocket scalability for REQ002
- developer: Implement auth flow for REQ001
```

### 3. Use Claude Code's Native Intelligence
Instead of complex coordination logic, leverage Claude Code's ability to understand context:

```bash
> "Analyze this feature idea and create a complete implementation plan"

# Claude Code will automatically:
# 1. Use product-manager for vision
# 2. Use business-analyst for requirements  
# 3. Use architect for design
# 4. Create a cohesive plan
```

### 4. Workflow Commands for Complex Coordination
```markdown
# commands/epic-planning.md
Plan an epic using all relevant agents.

Coordination flow:
1. product-manager: Break epic into features
2. For each feature:
   - business-analyst: Create requirements
   - architect: Assess complexity
   - uiux-designer: Scope UI work
3. Compile unified epic plan with:
   - Timeline
   - Dependencies  
   - Resource needs
```

## Important Notes

1. **No Direct API Calls**: Sub-agents cannot programmatically invoke other agents
2. **Context-Driven**: Claude Code decides which agent to use based on context
3. **User Control**: You maintain control over agent flow through prompts
4. **Flexible Orchestration**: Use commands and explicit requests for complex workflows
5. **Natural Language**: Agents communicate through their markdown output, not code

## Example: Complete Feature Flow

```bash
# Initial request
> Create a notification system feature

# Claude Code automatically:
# 1. Recognizes this is a product feature
# 2. Invokes product-manager agent
# 3. Sees recommendation for business-analyst
# 4. Asks: "Should I continue with detailed requirements?"

> Yes, continue with all necessary agents

# Claude Code then:
# 1. Uses business-analyst for requirements
# 2. Uses architect for system design
# 3. Uses uiux-designer for UI specs
# 4. Compiles comprehensive feature plan
```

This approach maintains the simplicity and flexibility that makes Claude Code powerful while enabling sophisticated multi-agent workflows.