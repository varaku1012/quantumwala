# Spec Orchestrate Command

Automated execution of specification tasks with validation gates.

## Usage
```
/spec-orchestrate [spec-name]
```

## Process

### Step 1: Load Specification
```bash
# Check if agents are enabled:
python .claude/scripts/check_agents.py

# Get all tasks:
python .claude/scripts/get_tasks.py {spec-name}
```

### Step 2: Task Execution Loop
For each pending task:

1. **Get Next Task**
   ```bash
   python .claude/scripts/get_tasks.py {spec-name} --mode next-pending
   ```

2. **Load Task Context**
   ```bash
   # Get specific task details:
   python .claude/scripts/get_tasks.py {spec-name} {task-id} --mode single
   
   # Load minimal steering context:
   python .claude/scripts/get_content.py .claude/steering/tech.md
   ```

3. **Execute Task**
   - Use spec-task-executor agent for implementation
   - Apply TDD approach
   - Follow project conventions

4. **Validate Implementation**
   - Use spec-implementation-reviewer agent
   - Check against acceptance criteria
   - Verify tests pass

5. **Mark Complete**
   ```bash
   python .claude/scripts/get_tasks.py {spec-name} {task-id} --mode complete
   ```

### Step 3: Final Review
After all tasks complete:
- Generate implementation summary
- Run all tests
- Create completion report

## Quality Gates

### Pre-Implementation
- Task must have clear acceptance criteria
- Dependencies must be resolved
- Context must be loaded successfully

### Post-Implementation
- All tests must pass
- Code review must approve
- Documentation must be complete

## Stateless Design
- Tasks.md is single source of truth
- Can resume from any point
- No hidden state dependencies

## Error Handling
- Failed tasks remain pending
- Clear error messages
- Suggested remediation steps

## Context Engineering Benefits
- Each task uses minimal context
- 70%+ reduction in token usage
- Faster execution per task
- Can handle larger specs

## Example Output
```
Starting orchestration for: user-authentication
✓ Task 1.1 completed: Create user model
✓ Task 1.2 completed: Add password hashing
⚡ Task 2.1 in progress: Implement login endpoint
...
Orchestration complete: 8/8 tasks done
```

## Integration
Works with:
- spec-task-executor agent
- spec-implementation-reviewer agent
- Context engineering scripts
- Validation agents (Phase 2)