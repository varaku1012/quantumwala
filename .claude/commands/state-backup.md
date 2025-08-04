# State Backup Command

Create and manage backups of the unified state system.

## Usage
```
/state-backup [backup-name]
```

## What it does

1. **Create State Backup**
   - Backs up unified state file
   - Includes all workflow progress
   - Adds timestamp and metadata

2. **List Available Backups**
   ```
   /state-backup --list
   ```

3. **Restore from Backup**
   ```
   /state-backup --restore "backup-name"
   ```

## Implementation

```bash
python .claude/scripts/workflow_recovery.py backup [options]
```

## Backup Contents

- **Unified State**: Complete workflow state
- **Agent Performance**: Execution history and metrics
- **Resource Usage**: System resource tracking
- **Error History**: Previous errors and recoveries
- **Command History**: Recent command executions

## Automatic Backups

The system automatically creates backups:
- Before major workflow phases
- Before state corruption recovery
- Before workflow resets
- Daily (if activity detected)

## Management Commands

### List Backups
```
/state-backup --list

Output:
Available State Backups:
- state_backup_20250804_143022.json (2.3MB) - 2 hours ago
- pre_restore_backup.json (2.1MB) - 1 day ago  
- daily_backup_20250803.json (1.9MB) - 1 day ago
```

### Restore Backup
```
/state-backup --restore "state_backup_20250804_143022.json"

Output:  
✓ Creating pre-restore backup...
✓ Validating backup integrity...
✓ Restoring state from backup...
✓ State restored successfully!
```

### Clean Old Backups
```
/state-backup --clean --days 7

Output:
✓ Cleaned 3 backups older than 7 days
✓ Storage saved: 6.2MB
```

## Safety Features

- **Integrity Validation**: Backups validated before restore
- **Pre-Restore Backup**: Current state backed up before restore
- **Atomic Operations**: Restore operations are atomic
- **Corruption Detection**: Detects and handles corrupted backups

## Storage Management

- **Location**: `.claude/backups/state/`
- **Compression**: Large backups automatically compressed
- **Retention**: Configurable retention policy
- **Size Limits**: Prevents excessive disk usage

## Use Cases

- Before risky operations
- System migration
- Disaster recovery  
- Development experimentation
- Performance regression testing