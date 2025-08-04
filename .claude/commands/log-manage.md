# Log Management Command

Manage logs and documentation in an organized structure.

## Usage
```
/log-manage [action] [options]
```

## Actions

### Clean Root Directory
```
/log-manage clean
```
Moves all markdown files from root to organized log directories:
- Session summaries → `.claude/logs/sessions/`
- Phase completions → `.claude/logs/phases/`
- Test reports → `.claude/logs/reports/`
- Analysis docs → `.claude/logs/analysis/`

### Create Log Index
```
/log-manage index
```
Creates an index of all logs for easy navigation.

### Archive Old Logs
```
/log-manage archive [--days 30]
```
Moves logs older than specified days to archive.

### Create New Log
```
/log-manage create --type [session|report|phase|analysis] --title "Title"
```

## Log Directory Structure

```
.claude/logs/
├── sessions/       # Daily work sessions & conversations
├── reports/        # Test reports, implementation reports
├── analysis/       # Analysis documents, comparisons
├── phases/         # Phase completion documentation
├── archive/        # Old logs (auto-organized)
├── temp/          # Temporary working logs
├── README.md      # Auto-generated index
└── index.json     # Machine-readable index
```

## Automated Usage

### For Agents
Agents should create logs using:
```bash
python .claude/scripts/log_manager.py create --type report --title "test results" --content "..."
```

### For Workflows
Workflows should log sessions:
```bash
echo "Workflow completed successfully" | python .claude/scripts/log_manager.py create --type session --title "workflow-name"
```

## Benefits

- **No Root Clutter**: All logs organized in `.claude/logs/`
- **Easy Navigation**: Categorized by type
- **Auto-Archive**: Old logs moved automatically
- **Searchable**: Index makes finding logs easy
- **Consistent**: All agents use same structure

## Integration

Update agents and workflows to use log manager:

### Instead of:
```markdown
Save to PROJECT_SUMMARY.md in root
```

### Use:
```markdown
Log results using:
python .claude/scripts/log_manager.py create --type report --title "project summary"
```

## Quick Clean

To immediately clean your root directory:
```bash
python .claude/scripts/log_manager.py clean
```

This will move all documentation files to appropriate log directories.