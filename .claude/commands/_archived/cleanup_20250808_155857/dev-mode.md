# Development Mode Command

Enable enhanced development mode with verbose logging, debugging, and safety features.

## Usage
```
/dev-mode [on|off|status]
```

## What it does

### Enable Development Mode
```
/dev-mode on
```

Activates:
- **Verbose Logging**: Detailed execution logs
- **Debug Hooks**: Enhanced hook debugging
- **Fail Fast**: Stop on first error instead of continuing
- **Resource Monitoring**: Real-time system monitoring
- **Command Validation**: Enhanced command safety checks
- **Performance Profiling**: Execution time analysis

### Disable Development Mode
```
/dev-mode off
```

Returns to production-optimized settings:
- Normal logging levels
- Silent error recovery
- Optimized performance
- Minimal validation overhead

### Check Status
```
/dev-mode status
```

Shows current development mode configuration and active features.

## Implementation

```bash
python .claude/scripts/dev_mode_manager.py [on|off|status]
```

## Development Features

### Enhanced Logging
- **Execution Traces**: Step-by-step command execution
- **Resource Usage**: CPU, memory, disk I/O tracking
- **Agent Performance**: Individual agent timing and success rates
- **Error Context**: Full stack traces and system state

### Debug Tools
- **Interactive Breakpoints**: Pause workflow for inspection
- **State Inspection**: Real-time state file viewing
- **Command Simulation**: Test commands without execution
- **Workflow Visualization**: ASCII workflow diagrams

### Safety Features
- **Backup Before Actions**: Auto-backup before risky operations
- **Rollback Points**: Create restore points at each phase
- **Confirmation Prompts**: Require confirmation for destructive actions
- **Resource Limits**: Stricter resource limits to prevent system overload

## Configuration

Development mode settings are stored in `.claude/settings.local.json`:

```json
{
  "development_mode": {
    "enabled": true,
    "verbose_logging": true,
    "fail_fast": true,
    "debug_hooks": true,
    "resource_monitoring": true,
    "auto_backup": true,
    "confirmation_prompts": true,
    "performance_profiling": true
  }
}
```

## Quick Start

```bash
# Enable dev mode
/dev-mode on

# Run a workflow with debugging
/workflow-auto "test-feature" "Simple test feature"

# Monitor in real-time (separate terminal)
python .claude/scripts/enhanced_dashboard.py --dev-mode

# When done developing
/dev-mode off
```

## Development Dashboard

When dev mode is active, enhanced dashboard shows:
- Real-time resource usage graphs
- Agent execution timeline
- Error rate tracking
- Command success rates
- Performance bottlenecks
- State change history

## Use Cases

- **New Feature Development**: Test new agents and commands safely
- **Performance Optimization**: Identify bottlenecks and optimize
- **Debugging Workflows**: Trace issues through complex workflows
- **System Monitoring**: Understand resource usage patterns
- **Team Onboarding**: Learn system behavior with detailed logs