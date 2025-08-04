# Dashboard Command

Launch the real-time Claude Code multi-agent system dashboard.

## Usage
```
/dashboard [mode]
```

Where mode can be:
- `simple` (default) - Basic dashboard with core metrics
- `enhanced` - Advanced dashboard with analytics and timeline

## Features

### Simple Dashboard
The simple dashboard provides:
- Project status and phase
- System metrics (agents, commands, scripts)
- Active specifications with progress bars
- Auto-refresh every 5 seconds

### Enhanced Dashboard
The enhanced dashboard includes everything from simple plus:
- **Performance Metrics**: Tasks completed in 24h, active sessions, efficiency score
- **Agent Activity**: Track which agents are being used most
- **Task Timeline**: Recent task completions with timestamps
- **Log Analysis**: Error/warning counts and recent error messages
- **Steering Context Status**: Visual indicators for each document
- **Interactive UI**: Hover effects and modern styling
- Auto-refresh every 10 seconds

## Launch Examples

### Simple Dashboard (Default)
```
/dashboard
```

### Enhanced Dashboard
```
/dashboard enhanced
```

## Dashboard Benefits

### Visibility
- See everything at a glance
- Track multiple specs simultaneously
- Monitor agent activity
- Identify performance trends

### Planning
- Understand what's complete
- See what's pending
- Plan next actions
- Track velocity

### Debugging
- Monitor error rates
- View recent errors
- Check agent usage patterns
- Validate steering status

## Integration

The dashboard reads from:
- `.claude/project-state.json`
- `.claude/steering/*`
- `.claude/specs/*/tasks.md`
- `.claude/logs/*`
- `.claude/agents/*`
- `.claude/commands/*`

## Stop Dashboard

Press `Ctrl+C` in the terminal to stop the dashboard.

## Notes

- Dashboard is read-only
- No authentication required (localhost only)
- Minimal resource usage
- Works cross-platform
- Enhanced dashboard provides deeper insights for complex projects