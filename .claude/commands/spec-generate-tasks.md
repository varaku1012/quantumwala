# Spec Generate Tasks Command

Auto-generate task commands from tasks.md for a specification.

## Usage
```
/spec-generate-tasks [spec-name]
```

## Process

1. **Parse Tasks**
   ```bash
   # Analyze all tasks in the specification:
   python .claude/scripts/task-generator.py {spec-name}
   ```

2. **Generate Commands**
   For each pending task:
   - Creates `/spec-name-task-X` command
   - Includes context loading
   - Adds validation steps
   - Integrates completion tracking

3. **Dependency Analysis**
   ```bash
   # Optional: Analyze dependencies only:
   python .claude/scripts/task-generator.py {spec-name} --analyze-deps
   ```

4. **Create Orchestration Script**
   Generates `orchestrate-{spec-name}.py` with:
   - Dependency order execution
   - Parallel group identification
   - Progress tracking

## Generated Commands

Each task command includes:
- Efficient context loading (only what's needed)
- Pre-implementation research step
- TDD implementation approach
- Validation with reviewer agent
- Automatic completion marking

## Benefits

### Before (Manual)
- Create each command file by hand
- Copy/paste boilerplate
- Track dependencies manually
- Risk of inconsistency

### After (Generated)
- All commands created instantly
- Consistent structure
- Dependencies analyzed
- Parallel opportunities identified

## Example Output
```
Found 8 tasks for user-authentication
✓ Generated: /user-authentication-task-1
✓ Generated: /user-authentication-task-2
✓ Generated: /user-authentication-task-2-1
✓ Generated: /user-authentication-task-3

Parallel Execution Opportunities:
  Group 1: Tasks 2.1, 2.2, 2.3 can run in parallel
  
Task commands ready to use!
Try: /user-authentication-task-1
```

## Integration

Works with:
- `/spec-tasks` - Creates initial tasks.md
- `/spec-orchestrate` - Can use generated commands
- Context engineering scripts
- Validation workflow

## Automation Benefits
- Zero manual command creation
- Consistent implementation approach
- Built-in best practices
- Scales to any number of tasks