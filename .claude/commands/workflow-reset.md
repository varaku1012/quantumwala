# Workflow Reset Command

Reset a corrupted or stuck workflow to a clean state.

## Usage
```
/workflow-reset "spec-name"
```

## What it does

1. **Backup Current State**
   - Creates timestamped backup of current workflow state
   - Saves all progress and task completion data

2. **Reset Workflow State**
   - Clears workflow progression markers
   - Resets task completion status
   - Preserves spec files (requirements, design, etc.)

3. **Clean Temporary Files**
   - Removes suggestion files
   - Clears execution logs (with backup)
   - Resets resource allocation

## Implementation

```bash
python .claude/scripts/workflow_recovery.py reset "spec-name"
```

## Recovery Options

### Soft Reset (Default)
- Preserves all spec files
- Resets only execution state
- Keeps backups for rollback

### Hard Reset
```
/workflow-reset "spec-name" --hard
```
- Removes all generated files
- Keeps only original requirements
- Fresh start from requirements phase

## Safety Features

- **Automatic Backup**: All state backed up before reset
- **Rollback Support**: Can restore previous state
- **Confirmation Required**: Prompts for confirmation on hard reset
- **Preserve Steering**: Never touches steering context

## Example

```
/workflow-reset "user-auth"

Output:
✓ Backing up workflow state...
✓ Resetting task execution state...  
✓ Clearing temporary files...
✓ Workflow reset complete!

Next: Run /spec-requirements to restart workflow
```

## Use Cases

- Workflow stuck in infinite loop
- Corrupted task state
- Need to restart implementation phase
- Testing workflow improvements
- Recovering from system crashes