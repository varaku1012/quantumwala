# Developer Environment Setup

Validate and setup your development environment for Quantumwala.

## Quick Setup (New Developers)
```bash
# 1. Validate your environment
python .claude/scripts/dev_environment_validator.py

# 2. Fix any issues found
# (Follow the suggestions from step 1)

# 3. Enable development mode
/dev-mode on

# 4. Test the system
/workflow-auto "hello-world" "Simple test feature"
```

## Usage
```
/dev-setup [validate|fix|status]
```

## Commands

### Validate Environment
```
/dev-setup validate
```
**or**
```
python .claude/scripts/dev_environment_validator.py
```

Checks:
- ✅ Python version (3.7+ required, 3.8+ recommended)
- ✅ Required packages (psutil, asyncio)
- ✅ File permissions (.claude directory)
- ✅ Claude Code CLI installation
- ✅ Project directory structure
- ✅ System resources (memory, disk space)
- ✅ Configuration files

### Get Status
```
/dev-setup status
```

Shows current environment status without full validation.

### Auto-Fix Issues (Future)
```
/dev-setup fix
```

Attempts to fix common setup issues automatically.

## Common Issues & Solutions

### **Error: python .claude/scripts/dev_environment_validator.py fails**
```bash
# Windows
python .claude\scripts\dev_environment_validator.py

# Or specify full path
C:\Python39\python.exe .claude\scripts\dev_environment_validator.py
```

### **Error: Missing psutil package**
```bash
pip install psutil
```

### **Error: No write permission to .claude directory**
```bash
# Windows (run as administrator if needed)
icacls .claude /grant %USERNAME%:F /T

# Unix/Linux/macOS
chmod -R u+w .claude
```

### **Error: claude-code command not found**
This is a warning, not an error. The system will work without Claude Code CLI, but some features will be limited.

To install Claude Code CLI:
1. Visit https://docs.anthropic.com/claude-code
2. Follow installation instructions for your platform
3. Ensure `claude-code` is in your PATH

### **Error: Low available memory**
- Close other applications
- Consider upgrading RAM
- Reduce concurrent task limits in settings

## Platform-Specific Notes

### Windows Developers
- Use PowerShell or Command Prompt
- Python hooks work better than bash scripts
- Ensure Python is in PATH
- May need to run as administrator for first setup

### macOS/Linux Developers
- All features should work out of the box
- bash hooks work natively
- Standard Unix permissions apply

## Development Mode Setup

After validation passes:
```bash
# Enable development mode for enhanced debugging
/dev-mode on

# This configures:
# - Verbose logging
# - Enhanced error messages  
# - Resource monitoring
# - Automatic backups
# - Development-friendly settings
```

## Team Setup

For development teams:
1. **First developer** sets up the environment
2. **Team members** clone and run validation
3. **Share settings** through version control (optional)
4. **Use development mode** for enhanced debugging

## Troubleshooting

### Validation fails with import errors
```bash
# Check Python installation
python --version

# Check pip installation
pip --version

# Install requirements
pip install psutil

# Retry validation
python .claude/scripts/dev_environment_validator.py
```

### Permission errors on Windows
```cmd
# Run as administrator
# Or fix permissions
icacls .claude /grant %USERNAME%:F /T
```

### Hook execution fails
```bash
# Test Python hook directly
python .claude/hooks/phase_complete.py

# Check file permissions
ls -la .claude/hooks/
```

## Integration with IDEs

### VS Code
Add to your workspace settings:
```json
{
  "python.defaultInterpreterPath": "python",
  "python.terminal.activateEnvironment": true,
  "files.watcherExclude": {
    "**/.claude/logs/**": true,
    "**/.claude/backups/**": true
  }
}
```

### PyCharm
1. Set Python interpreter to your system Python
2. Mark `.claude` as excluded from indexing (for performance)
3. Add run configuration for dev_environment_validator.py

## Next Steps

Once setup is complete:
1. **Enable dev mode**: `/dev-mode on`
2. **Try a simple workflow**: `/workflow-auto "test" "Test feature"`
3. **Explore the system**: `/dashboard` for monitoring
4. **Read documentation**: Check `.claude/system-docs/` for detailed guides

## Getting Help

If setup continues to fail:
1. Check the validation output carefully
2. Follow all suggested fixes
3. Check logs in `.claude/logs/` for detailed errors
4. Ensure you have a clean Python environment