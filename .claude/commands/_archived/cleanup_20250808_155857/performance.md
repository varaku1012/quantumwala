# Performance Command

Monitor and analyze system performance metrics

## Usage
```
/performance [action]
```

Actions:
- `report` - Generate performance report
- `monitor` - Start real-time monitoring
- `export` - Export metrics to JSON

## Examples

### Generate Performance Report
```
/performance report
```
Creates a detailed markdown report with:
- Agent execution statistics
- Command performance metrics
- Task completion times
- Resource usage analysis
- Error summary
- Performance recommendations

### Start Monitoring
```
/performance monitor
```
Starts continuous resource monitoring that tracks:
- CPU usage
- Memory consumption
- Disk usage
- Agent/command execution times

### Export Metrics
```
/performance export
```
Exports all collected metrics to a JSON file for:
- External analysis
- Historical tracking
- Integration with other tools

## Metrics Tracked

### Agent Metrics
- Execution count
- Average/max duration
- Success rate
- Token usage

### Command Metrics
- Execution frequency
- Performance timing
- Success/failure rates

### Resource Metrics
- CPU utilization
- Memory usage
- Disk space
- Peak usage times

### Error Tracking
- Error types and frequency
- Component-specific errors
- Error patterns

## Integration

Performance data integrates with:
- Enhanced dashboard
- Log analysis
- Steering context optimization
- Agent efficiency tuning

## Benefits

1. **Optimization**: Identify slow agents/commands
2. **Debugging**: Track error patterns
3. **Planning**: Understand resource needs
4. **Monitoring**: Real-time system health