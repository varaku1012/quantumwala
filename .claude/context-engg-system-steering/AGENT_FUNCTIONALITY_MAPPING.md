# Agent Functionality Mapping - How Agents Achieve Command Functionality

## The Problem
Commands are user-facing workflows, but agents need to achieve the same functionality. Since agents shouldn't call commands directly, how do they do it?

## The Solution: Three Mechanisms

### 1. **Task Tool for Agent-to-Agent Delegation**
### 2. **Shell Tool for Script Execution**  
### 3. **Custom Tools via Shell Wrapper**

## Detailed Mapping: Command → Agent Approach

### Specification Management

#### User Command: `/spec-create "feature" "description"`
#### Agent Approach:
```markdown
# Option 1: Using Task tool to delegate
Use Task tool to delegate to product-manager:
- Description: "Create specification for {feature}"
- Context: {description, requirements}

# Option 2: Using Shell tool with custom tool
Shell: python .claude/tools/spec_tool.py create "feature" "description"

# Option 3: Using Shell tool with script directly
Shell: python .claude/scripts/spec_manager.py create "feature"
```

#### User Command: `/spec-requirements`
#### Agent Approach:
```markdown
# Using Task tool
Use Task tool to delegate to business-analyst:
- Description: "Generate detailed requirements for {spec}"
- Context: {spec_overview, user_needs}

# OR using Shell tool
Shell: python .claude/scripts/spec_manager.py requirements {spec_name}
```

#### User Command: `/spec-tasks`
#### Agent Approach:
```markdown
# Using custom tool
Shell: python .claude/tools/spec_tool.py generate_tasks {spec_name}

# OR using Task delegation
Use Task tool to delegate to architect:
- Description: "Break down {feature} into implementation tasks"
- Context: {requirements, design}
```

### Workflow Orchestration

#### User Command: `/workflow "build feature" --mode=parallel`
#### Agent Approach:
```markdown
# Chief-PM uses Task tool to orchestrate:

1. Delegate requirements gathering:
   Task: business-analyst
   Description: "Analyze requirements for {feature}"

2. Delegate design (parallel):
   Task: architect
   Description: "Design architecture for {feature}"
   
   Task: uiux-designer
   Description: "Design UI for {feature}"

3. Delegate implementation:
   Task: developer
   Description: "Implement {specific_task}"
```

### Bug Management

#### User Command: `/bug-fix`
#### Agent Approach:
```markdown
# Developer agent approach:
1. Read bug report: Read: .claude/bugs/{bug_id}/report.md
2. Analyze code: Read: {affected_files}
3. Implement fix: Write: {fixed_code}
4. Run tests: Shell: npm test
5. Update status: Shell: python .claude/tools/bug_tool.py update_status {bug_id} "fixed"
```

### Analysis Operations

#### User Command: `/analyze-codebase`
#### Agent Approach:
```markdown
# Using Task delegation
Task: codebase-analyst
Description: "Analyze and document the codebase structure"
Context: {project_root, focus_areas}

# OR using Shell for specific analysis
Shell: python .claude/scripts/codebase_analyzer.py --output analysis.md
```

### Grooming Operations

#### User Command: `/grooming-workflow "feature"`
#### Agent Approach:
```markdown
# Product-manager orchestrates via Task tool:

Phase 1 (Parallel):
- Task: business-analyst → "Analyze market needs"
- Task: architect → "Assess technical feasibility"
- Task: security-engineer → "Security implications"

Phase 2:
- Task: product-manager → "Prioritize features"
- Task: architect → "Create technical roadmap"
```

## Implementation Pattern: Agent Tool Bridge

The `agent_tool_bridge.py` handles the translation:

```python
class AgentToolBridge:
    """Translates Task tool calls to actual functionality"""
    
    def process_task_delegation(self, task_request):
        # Map agent + description to actual execution
        
        if task_request.agent == "business-analyst":
            if "requirements" in task_request.description:
                # Execute spec requirements generation
                return self.execute_script("spec_manager.py requirements")
                
        elif task_request.agent == "developer":
            if "implement" in task_request.description:
                # Execute implementation
                return self.execute_script("task_orchestrator.py implement")
```

## Custom Tools Available to Agents

### 1. SpecTool (via Shell)
```bash
# Agents can use:
Shell: python .claude/tools/spec_tool.py create|validate|generate_tasks|update_status
```

### 2. MemoryTool (via Shell)
```bash
# Agents can use:
Shell: python .claude/tools/memory_tool.py store|retrieve|search|get_recent
```

### 3. ContextTool (via Shell)
```bash
# Agents can use:
Shell: python .claude/tools/context_tool.py compress|extract|merge|validate
```

### 4. PlanningTool (via Shell)
```bash
# Agents can use:
Shell: python .claude/tools/planning_tool.py analyze|create_batches|estimate_time
```

## Agent Capabilities Matrix

| Agent | Tools Available | Can Achieve |
|-------|----------------|--------------|
| chief-product-manager | Task, Read, Write, CreateDirectory | Full orchestration via delegation |
| product-manager | Task, Read, Write | Strategy, planning, specs via delegation |
| business-analyst | Read, Write, Shell | Requirements via scripts/tools |
| architect | Read, Write, Shell, Task | Design, planning via scripts + delegation |
| developer | Read, Write, Shell | Implementation via direct code + scripts |
| qa-engineer | Read, Write, Shell | Testing via test runners |
| security-engineer | Read, Shell, Task | Security scans + delegate fixes |

## Key Principles

### 1. Orchestrators Use Task Tool
Agents with orchestration responsibilities (chief-PM, PM) primarily use Task tool to delegate work.

### 2. Workers Use Shell + Custom Tools
Worker agents (developer, QA) use Shell to execute scripts and custom tools.

### 3. Bridge Handles Translation
The agent_tool_bridge.py translates high-level Task delegations into specific script executions.

### 4. No Direct Command Calls
Agents never directly call user commands like `/spec-create`. Instead they:
- Use Task to delegate to another agent
- Use Shell to execute the underlying script
- Use custom tools via Shell wrapper

## Example: Complete Feature Development

### User Approach:
```bash
/workflow "user authentication"
```

### Chief-PM Agent Approach:
```markdown
# Phase 1: Delegate Analysis
Task: business-analyst
Description: "Analyze requirements for user authentication"
Context: {project_info, user_needs}

# Phase 2: Delegate Design (Parallel)
Task: architect
Description: "Design authentication architecture"

Task: uiux-designer
Description: "Design login/signup UI"

# Phase 3: Create Tasks
Shell: python .claude/tools/spec_tool.py generate_tasks "user-auth"

# Phase 4: Delegate Implementation
For each task in tasks.md:
  Task: developer
  Description: "Implement {task_description}"
  Context: {design, requirements}

# Phase 5: Delegate Testing
Task: qa-engineer
Description: "Test authentication implementation"
```

## Benefits of This Approach

1. **Separation of Concerns**: User commands vs agent tools
2. **Flexibility**: Agents can achieve functionality multiple ways
3. **Maintainability**: Single implementation in scripts
4. **Testability**: Can test scripts independently
5. **Scalability**: Easy to add new tools and capabilities

## Implementation Checklist

- [x] Create custom tools in `.claude/tools/`
- [x] Implement agent_tool_bridge.py
- [x] Map Task delegations to script executions
- [ ] Create missing tools (context_tool, planning_tool, bug_tool)
- [ ] Test agent delegations end-to-end
- [ ] Document tool usage in each agent definition
- [ ] Add tool discovery mechanism

## Conclusion

Agents achieve command functionality through:
1. **Task tool** for delegation (orchestrators)
2. **Shell tool** for script/tool execution (workers)
3. **Custom tools** via Shell wrapper (all agents)
4. **Agent Tool Bridge** for intelligent routing

This maintains clean separation between user-facing commands and agent capabilities while providing full functionality.