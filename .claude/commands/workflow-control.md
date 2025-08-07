# Workflow Control Command

**Manual control over workflow execution**  
Replaces: workflow-start, workflow-continue, workflow-reset

## Usage

```bash
/workflow-control <action> [options]
```

## Actions

### start - Begin new workflow
```bash
/workflow-control start "build shopping cart" [--spec-name="cart-v2"] [--mode=parallel]
```

### continue - Continue paused workflow
```bash
/workflow-control continue
```

### pause - Pause current workflow  
```bash
/workflow-control pause
```

### reset - Reset workflow state
```bash
/workflow-control reset
```

### status - Check workflow status
```bash
/workflow-control status
```

## Examples

### Starting a Controlled Workflow
```bash
# Start with manual control
/workflow-control start "user authentication system"

# Output:
✅ Workflow started: workflow_20240106_143022
📋 Spec: user-authentication-system
🎯 Description: user authentication system

Use 'workflow-control continue' to proceed to next phase
```

### Stepping Through Phases
```bash
# Continue to next phase
/workflow-control continue

# Output:
📍 Current phase: spec_creation
✅ Completed phases: initialization
⏳ Executing phase: spec_creation...
✅ Phase spec_creation completed successfully

⏭️ Next phase: requirements
Use 'workflow-control continue' to proceed
```

### Checking Progress
```bash
/workflow-control status

# Output:
============================================================
WORKFLOW STATUS
============================================================
ID: workflow_20240106_143022
Spec: user-authentication-system
Status: in_progress
Current Phase: requirements
Duration: 125.3 seconds

✅ Completed Phases (2):
  - initialization
  - spec_creation

⏳ Remaining Phases (5):
  - requirements
  - design
  - tasks
  - implementation
  - testing
  - review
============================================================
```

### Pausing Work
```bash
# Need to stop for a meeting
/workflow-control pause

# Output:
⏸️ Workflow paused
Use 'workflow-control continue' to resume
```

### Resetting After Error
```bash
# Something went wrong, start over
/workflow-control reset

# Output:
📦 Current workflow archived to: .claude/workflow_archive/workflow_20240106_143022.json
🔄 Workflow state reset
Use 'workflow-control start' to begin new workflow
```

## Workflow Phases

The workflow proceeds through these phases:

1. **initialization** - Setup and preparation
2. **spec_creation** - Create specification structure
3. **requirements** - Generate requirements
4. **design** - Create technical design
5. **tasks** - Generate task list
6. **implementation** - Implement features
7. **testing** - Run tests
8. **review** - Final review

## Phase Control

At each phase you can:
- **Continue** - Proceed to next phase
- **Pause** - Stop and resume later
- **Reset** - Start over from beginning
- **Status** - Check current progress

## Error Handling

If a phase fails:
```bash
❌ Phase requirements failed: Missing context

Options:
- Retry: /workflow-control continue
- Skip: (not yet implemented)
- Reset: /workflow-control reset
```

## State Management

Workflow state is saved in:
```
.claude/workflow_state.json
```

Archived workflows are stored in:
```
.claude/workflow_archive/
```

## Integration with Main Workflow

This provides manual control over the unified workflow:

```bash
# Start with control
/workflow-control start "feature"

# Or use automatic workflow
/workflow "feature" --auto=manual

# Both give you phase-by-phase control
```

## Benefits

1. **Inspection** - Review outputs between phases
2. **Debugging** - Stop when something looks wrong  
3. **Learning** - Understand what each phase does
4. **Collaboration** - Pause for team input
5. **Safety** - Prevent runaway execution

## Tips

- Use for first-time features to understand the process
- Pause before implementation to review design
- Check status regularly to track progress
- Reset saves your work before clearing state
- Continue retries the last failed phase

## Implementation

```bash
python .claude/scripts/workflow_control.py <action> [options]
```

## Migration from Old Commands

| Old Command | New Command |
|-------------|-------------|
| `/workflow-start` | `/workflow-control start` |
| `/workflow-continue` | `/workflow-control continue` |
| `/workflow-reset` | `/workflow-control reset` |
| `/status` | `/workflow-control status` |

## Next Steps

- After starting, use `continue` to step through
- Check `status` to see where you are
- Review generated files in `.claude/specs/`
- Use `/task` for specific corrections