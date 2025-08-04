# Status Command

Simple status overview for developers to understand the current state of their projects and workflows.

## Usage
```
/status
```

## What it shows

🔍 **PROJECT STATUS**
- Current project name and location
- Active specifications and their progress
- Current workflow phase

⚡ **SYSTEM STATUS**  
- Environment health (Python, dependencies, permissions)
- Development mode status
- System resources (CPU, memory, disk)

🤖 **AGENT ACTIVITY**
- Recently used agents and their performance
- Active tasks and their status
- Completed vs failed executions

📊 **RECENT ACTIVITY**
- Last 5 commands executed
- Recent workflow completions
- Any errors or issues

## Implementation

```bash
python .claude/scripts/developer_status.py
```

## Sample Output

```
🔍 QUANTUMWALA STATUS
====================================================

📁 PROJECT INFORMATION
   Name: user-authentication
   Location: /path/to/project
   Created: 2 hours ago
   Last activity: 5 minutes ago

⚡ ENVIRONMENT STATUS
   ✅ Python 3.9.2 (ready)
   ✅ Dependencies installed
   ✅ Permissions OK
   🔧 Development mode: ENABLED
   💾 Available disk: 15.2GB
   🧠 Available memory: 4.1GB

📊 CURRENT WORKFLOW
   Phase: Implementation (Phase 5/7)
   Progress: ████████░░ 80% complete
   
   Active Tasks:
   • Task 2.1: Create login API endpoint (developer) - In Progress
   • Task 2.2: Add password validation (security-engineer) - Queued
   
   Completed: 6/8 tasks
   Estimated time remaining: 15 minutes

🤖 AGENT PERFORMANCE (Last 24h)
   developer: 8 tasks, 87% success rate, avg 12min
   qa-engineer: 3 tasks, 100% success rate, avg 8min
   security-engineer: 2 tasks, 100% success rate, avg 15min

📈 RECENT ACTIVITY
   15:42 - /spec-tasks completed ✅
   15:35 - /spec-design completed ✅  
   15:28 - /spec-requirements completed ✅
   15:20 - /spec-create "user-authentication" completed ✅
   15:15 - /dev-mode on completed ✅

🚨 ISSUES & ALERTS
   No current issues ✅

🎯 NEXT STEPS
   1. Wait for current implementation tasks to complete
   2. Review generated code in src/auth/
   3. Ready for testing phase in ~15 minutes
```

## Quick Status Checks

### Check Environment Only
```
/status --env
```

### Check Current Workflow Only  
```
/status --workflow
```

### Check Agent Performance
```
/status --agents
```

### Check for Issues
```
/status --issues
```

## Status for Different Scenarios

### **New Project (Nothing Running)**
```
🔍 QUANTUMWALA STATUS
====================================================

📁 PROJECT INFORMATION
   No active project
   Location: /path/to/project
   Ready to start new workflow

⚡ ENVIRONMENT STATUS
   ✅ All systems ready
   🎯 Next: Try /dev-workflow "describe what you want to build"
```

### **Workflow In Progress**
```
📊 CURRENT WORKFLOW
   Project: payment-integration
   Phase: Implementation (Phase 5/7)
   Progress: ██████░░░░ 60% complete
   
   Running: 2 agents active
   ETA: 25 minutes remaining
```

### **Environment Issues**
```
⚡ ENVIRONMENT STATUS
   ❌ Missing dependency: psutil
   ⚠️  Low disk space: 0.8GB remaining
   
   🔧 Fix these issues:
      pip install psutil
      Free up disk space
```

### **Recent Errors**
```
🚨 ISSUES & ALERTS
   ❌ Task 3.1 failed: Permission denied writing to src/
   ⚠️  Agent timeout: qa-engineer (task took 45min)
   
   💡 Suggested actions:
      Fix file permissions: chmod u+w src/
      Check system resources: /status --env
```

## Integration with Development Tools

### Terminal Prompt Integration
Add to your `.bashrc` or `.zshrc`:
```bash
function quantumwala_prompt() {
    if [ -d ".claude" ]; then
        local status=$(python .claude/scripts/developer_status.py --prompt 2>/dev/null)
        echo "$status"
    fi
}

# Example usage in PS1
PS1='$(quantumwala_prompt)\$ '
```

### VS Code Status Bar
Create a VS Code extension or use a task:
```json
{
  "label": "Quantumwala Status", 
  "type": "shell",
  "command": "python .claude/scripts/developer_status.py --json",
  "group": "build"
}
```

### Watch Mode (Auto-Refresh)
```bash
# Continuously monitor status
python .claude/scripts/developer_status.py --watch

# Updates every 10 seconds
python .claude/scripts/developer_status.py --watch --interval 10
```

## Troubleshooting Status Issues

### Status Command Fails
```bash
# Check environment first
python .claude/scripts/dev_environment_validator.py

# Then try status
python .claude/scripts/developer_status.py
```

### Slow Status Updates
```bash
# Use fast mode (skips detailed analysis)
/status --fast

# Or check specific components
/status --workflow --no-agents
```

### No Project Information Shown
```bash
# Initialize project context
/steering-setup

# Or start a new workflow
/dev-workflow "describe your project"
```

## Use Cases

### **Daily Development**
- Quick check before starting work
- Monitor long-running workflows  
- Verify environment health

### **Debugging Issues**
- Identify failed tasks
- Check system resources
- Review recent error messages

### **Team Coordination**
- Share current project status
- Check if environment is ready
- Verify workflow progress

### **Performance Monitoring**
- Track agent performance over time
- Identify slow or failing components
- Monitor system resource usage

## Related Commands

- `/dev-setup validate` - Full environment validation
- `/dev-mode status` - Development mode details
- `/dashboard` - Full monitoring dashboard
- `/state-backup --list` - Check available backups