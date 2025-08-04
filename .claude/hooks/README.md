# Workflow Hooks

Automated hooks for workflow progression and logging.

## Available Hooks

### phase-complete
Automatically triggered when a workflow phase completes.

**Files:**
- `phase-complete.sh` - Unix/Linux/macOS version
- `phase-complete.bat` - Windows version

**What it does:**
1. Detects current workflow phase and spec name
2. Logs phase completion to session logs
3. Determines next command in workflow
4. Creates suggestion file for Claude Code
5. Updates workflow state

## Setup

### For Claude Code Integration

**RECOMMENDED (Cross-Platform)**:
```json
{
  "hooks": {
    "post_command": {
      "enabled": true,
      "script": "python .claude/hooks/phase_complete.py"
    }
  }
}
```

**Legacy (Platform-Specific)**:
Unix/Linux/macOS:
```json
{
  "hooks": {
    "post_command": {
      "enabled": true,
      "script": ".claude/hooks/phase-complete.sh"
    }
  }
}
```

Windows:
```json
{
  "hooks": {
    "post_command": {
      "enabled": true,
      "script": ".claude/hooks/phase-complete.bat"
    }
  }
}
```

### Manual Testing

To test the hook manually:

**Unix/Linux/macOS:**
```bash
./.claude/hooks/phase-complete.sh
```

**Windows:**
```batch
.claude\hooks\phase-complete.bat
```

## Hook Flow

```
Phase Complete → Hook Triggered → 
Log Completion → Determine Next Phase → 
Create Suggestion → Update State
```

## Output Files

- `.claude/next_command.txt` - Contains suggested next command
- `.claude/logs/sessions/auto_progression.log` - Progression history
- `.claude/logs/sessions/phase-complete-*.md` - Phase completion logs

## Phase Progression Map

1. **steering_setup** → `/spec-create`
2. **spec_creation** → `/spec-requirements`
3. **requirements_generation** → `/planning design`
4. **design_creation** → `/spec-tasks`
5. **task_generation** → `/planning implementation`
6. **implementation** → `/planning testing`
7. **validation** → `/spec-review`
8. **complete** → End

## Benefits

- **Automatic Progression**: No manual intervention between phases
- **Comprehensive Logging**: Full audit trail of workflow
- **Error Recovery**: Graceful handling of missing dependencies
- **Cross-Platform**: Works on all operating systems