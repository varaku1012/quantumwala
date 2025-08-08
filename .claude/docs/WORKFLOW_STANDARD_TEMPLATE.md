# Standard Workflow Template

## 🎯 Overview

This document provides the standard template and commands for starting workflows in the Claude Code Context Engineering System.

---

## 🚀 Quick Start Template

### Basic Command Structure
```bash
python .claude/scripts/start_workflow.py [SPEC_NAME] [OPTIONS]
```

### Recommended Standard Command
```bash
# This is the recommended default for most workflows:
python .claude/scripts/start_workflow.py [spec-name] --mode logged --log-level INFO
```

---

## 📋 Standard Workflow Process

### Step 1: Check Current Status
Always start by understanding what specs are available and their current state:

```bash
python .claude/scripts/start_workflow.py --status
```

### Step 2: Choose Your Spec
Select a spec from the backlog that shows as ready:

```bash
python .claude/scripts/start_workflow.py --list
```

### Step 3: Run the Workflow
Execute with appropriate mode and logging:

```bash
# Standard execution with logging
python .claude/scripts/start_workflow.py user-authentication --mode logged

# With debug information if needed
python .claude/scripts/start_workflow.py user-authentication --mode logged --log-level DEBUG

# Dry run first to verify
python .claude/scripts/start_workflow.py user-authentication --dry-run
```

### Step 4: Monitor Progress
The workflow will show real-time progress:
- Phase transitions
- Agent calls
- File creation
- Error messages

### Step 5: Review Results
After completion:

```bash
# Check the summary
cat .claude/logs/workflows/*[spec-name]*summary.md

# Review generated code
ls services/[spec-name]-api/
ls frontend/[spec-name]-web/

# Check spec status
python .claude/scripts/start_workflow.py --status
```

### Step 6: Automated Validation (Final Step)
The workflow automatically validates execution and provides insights:

```bash
# Validation runs automatically at the end of workflow
# Or run manually:
python .claude/scripts/start_workflow.py [spec-name] --validate

# Check validation report
cat .claude/logs/workflows/*[spec-name]*validation.md
```

**What Gets Validated:**
- ✅ Log file generation
- ✅ Spec lifecycle (backlog → scope → completed)
- ✅ Code generation completeness
- ✅ Project structure compliance
- ✅ Phase execution success
- ✅ Agent interactions
- ✅ Performance metrics
- ✅ Error detection

**Health Score Interpretation:**
- **90-100**: EXCELLENT - All checks passed
- **70-89**: GOOD - Minor issues, safe to proceed
- **50-69**: FAIR - Review recommendations
- **0-49**: POOR - Manual intervention needed

---

## 🎨 Workflow Modes Reference

| Mode | Command | Use Case | Features |
|------|---------|----------|----------|
| **Logged** (Recommended) | `--mode logged` | Production work | Full logging, proper structure, lifecycle management |
| **Enhanced** | `--mode enhanced` | Quick implementation | Proper structure, no logging |
| **Full** | `--mode full` | AI-powered generation | Complete Context Engineering, agent delegation |
| **Basic** | `--mode basic` | Prototypes | Fast templates, minimal features |

---

## 📊 Logging Levels

| Level | Command | Output |
|-------|---------|--------|
| **INFO** (Default) | `--log-level INFO` | Normal operational messages |
| **DEBUG** | `--log-level DEBUG` | Detailed diagnostic information |
| **WARNING** | `--log-level WARNING` | Only warnings and errors |
| **ERROR** | `--log-level ERROR` | Only error messages |

---

## 🔄 Common Workflows

### New Feature Implementation
```bash
# 1. Check status
python .claude/scripts/start_workflow.py --status

# 2. Dry run
python .claude/scripts/start_workflow.py new-feature --dry-run

# 3. Execute with logging
python .claude/scripts/start_workflow.py new-feature --mode logged

# 4. Review summary
cat .claude/logs/workflows/*new-feature*summary.md
```

### Resume Interrupted Work
```bash
# Resume a spec that's already in scope
python .claude/scripts/start_workflow.py my-spec --resume

# Or explicitly from scope
python .claude/scripts/start_workflow.py my-spec --source scope
```

### Debug Failed Workflow
```bash
# Run with debug logging
python .claude/scripts/start_workflow.py problematic-spec --mode logged --log-level DEBUG

# Check detailed logs
grep ERROR .claude/logs/workflows/*problematic-spec*.log
```

---

## 📁 Output Structure

After running a workflow, your code will be organized as:

```
project-root/
├── services/
│   └── [spec-name]-api/          # Backend service
│       ├── src/
│       ├── tests/
│       └── package.json
├── frontend/
│   └── [spec-name]-web/          # Frontend application
│       ├── src/
│       ├── public/
│       └── package.json
├── ml-services/
│   └── [spec-name]-ml/           # ML service (if applicable)
│       ├── app/
│       ├── models/
│       └── requirements.txt
├── infrastructure/
│   ├── k8s/[spec-name]/          # Kubernetes configs
│   └── docker/[spec-name]/       # Docker configs
└── implementations/
    └── [spec-name]/               # Feature documentation
        └── README.md
```

---

## 🛠️ Convenience Scripts

### Windows (workflow.bat)
```batch
workflow user-authentication --mode logged
```

### Linux/Mac (workflow.sh)
```bash
./workflow.sh user-authentication --mode logged
```

---

## 📝 Environment Variables

You can set defaults via environment variables:

```bash
# Set default log level
export WORKFLOW_LOG_LEVEL=DEBUG

# Set default mode
export WORKFLOW_MODE=logged

# Set default source
export WORKFLOW_SOURCE=backlog
```

---

## 🎯 Best Practices

1. **Always check status first** - Avoid conflicts and understand current state
2. **Use logged mode by default** - Best balance of features and visibility
3. **Start with dry-run for new specs** - Verify everything is set up correctly
4. **Review summaries** - They provide quick insights into what happened
5. **Keep specs organized** - Move completed specs out of scope
6. **Use descriptive spec names** - Makes tracking easier
7. **Save important logs** - Especially for production deployments

---

## 🚨 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Spec not found | Check with `--status` or `--list` |
| Workflow fails | Check logs in `.claude/logs/workflows/` |
| Spec stuck in scope | Manually move to backlog or completed |
| Missing files | Verify spec has overview.md and requirements.md |
| Permission errors | Check file/folder permissions |

---

## 📚 Further Reading

- [Complete Workflow Usage Guide](WORKFLOW_USAGE.md)
- [Spec Execution Trace](SPEC_EXECUTION_TRACE.md)
- [Logging System Documentation](WORKFLOW_LOGGER.md)
- [Context Engineering System](CONTEXT_ENGINEERING.md)

---

## 💡 Quick Reference Card

```bash
# Most common commands you'll use:

# Check what's available
python .claude/scripts/start_workflow.py --status

# Run a workflow with logging
python .claude/scripts/start_workflow.py [spec-name] --mode logged

# Debug a problem
python .claude/scripts/start_workflow.py [spec-name] --mode logged --log-level DEBUG

# Resume work
python .claude/scripts/start_workflow.py [spec-name] --resume

# Test without changes
python .claude/scripts/start_workflow.py [spec-name] --dry-run
```

---

*This is your standard template for starting any workflow in the Claude Code Context Engineering System.*

*Version: 2.0 | Last Updated: August 2025*