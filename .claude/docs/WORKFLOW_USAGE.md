# Workflow System Usage Guide

## 🚀 Quick Start

### Starting a Workflow

The standard way to start any workflow is using the `start_workflow.py` launcher:

```bash
# From project root
python .claude/scripts/start_workflow.py [spec-name] [options]

# Or use the convenience scripts:
./workflow.sh [spec-name] [options]     # Linux/Mac
workflow.bat [spec-name] [options]      # Windows
```

---

## 📋 Common Commands

### 1. Check Spec Status
View all specs across backlog, in-progress, and completed:

```bash
python .claude/scripts/start_workflow.py --status
```

Output:
```
📋 SPEC STATUS OVERVIEW
======================================================================

📥 BACKLOG (Ready to implement):
----------------------------------------------------------------------
  ✅ Ready user-authentication          Files: overview, requirements, design
  ⚠️  Incomplete analytics-dashboard    Files: requirements, design
  ✅ Ready payment-processing          Files: overview, requirements

🔄 IN PROGRESS (Currently being implemented):
----------------------------------------------------------------------
  ▶️  user-profile                     Started: 2025-08-07

✅ COMPLETED:
----------------------------------------------------------------------
  ✓  user-auth-test                   Location: implementations/user-auth-test
```

### 2. List Available Specs
Quick list of specs ready to implement:

```bash
python .claude/scripts/start_workflow.py --list
```

### 3. Run Basic Workflow
Fastest option with template generation:

```bash
python .claude/scripts/start_workflow.py user-auth
```

### 4. Run with Full Logging (Recommended)
Complete logging with all outputs:

```bash
python .claude/scripts/start_workflow.py user-auth --mode logged
```

### 5. Run with Full Integration
Complete Context Engineering System:

```bash
python .claude/scripts/start_workflow.py user-auth --mode full --log-level DEBUG
```

### 6. Resume In-Progress Spec
Continue work on a spec already in scope:

```bash
python .claude/scripts/start_workflow.py my-spec --resume
# Or explicitly:
python .claude/scripts/start_workflow.py my-spec --source scope
```

### 7. Dry Run
See what would happen without making changes:

```bash
python .claude/scripts/start_workflow.py test-spec --dry-run
```

---

## 🎯 Workflow Modes

### 1. **Basic Mode** (Fastest)
```bash
python .claude/scripts/start_workflow.py spec-name --mode basic
```
- Simple template generation
- No agent calls
- Basic folder structure
- Good for quick prototypes

### 2. **Enhanced Mode** (Structured)
```bash
python .claude/scripts/start_workflow.py spec-name --mode enhanced
```
- Proper folder structure per steering docs
- Spec lifecycle management (backlog → scope → completed)
- Organized code generation
- No logging

### 3. **Logged Mode** (Recommended) ⭐
```bash
python .claude/scripts/start_workflow.py spec-name --mode logged
```
- Everything from Enhanced mode
- Comprehensive logging to files
- JSON structured logs
- Markdown summaries
- Real-time console output
- Performance metrics

### 4. **Full Mode** (Most Complete)
```bash
python .claude/scripts/start_workflow.py spec-name --mode full
```
- Full Context Engineering System integration
- Real agent delegation
- Context compression
- Memory persistence
- Token optimization
- Complete AI-powered generation

---

## 📊 Log Levels

Control the verbosity of output:

```bash
# Minimal output - only warnings and errors
python .claude/scripts/start_workflow.py spec-name --log-level WARNING

# Normal output (default)
python .claude/scripts/start_workflow.py spec-name --log-level INFO

# Detailed output with debug information
python .claude/scripts/start_workflow.py spec-name --log-level DEBUG

# Only critical errors
python .claude/scripts/start_workflow.py spec-name --log-level ERROR
```

---

## 📁 Output Locations

After running a workflow, find your outputs here:

### Generated Code
```
services/
├── {spec-name}-api/          # Backend services
frontend/
├── {spec-name}-web/          # Frontend apps
ml-services/
├── {spec-name}-ml/           # ML services
implementations/
└── {spec-name}/              # Feature documentation
```

### Logs (Logged/Full modes)
```
.claude/logs/workflows/
├── {timestamp}_{spec}_summary.md       # Human-readable summary
├── {timestamp}_{spec}_{id}.log         # Detailed text log
└── {timestamp}_{spec}_{id}.json        # Structured JSON data
```

### Specs
```
.claude/specs/
├── backlog/          # Specs waiting to be implemented
├── scope/            # Specs currently being worked on
└── completed/        # Finished specs with metadata
```

---

## 🔄 Complete Workflow Example

Here's a typical workflow from start to finish:

```bash
# 1. Check what specs are available
python .claude/scripts/start_workflow.py --status

# 2. Choose a spec and run with logging
python .claude/scripts/start_workflow.py user-authentication --mode logged

# 3. Monitor the output
# ... workflow executes with real-time updates ...

# 4. Check the generated code
ls services/user-authentication-api/
ls frontend/user-authentication-web/

# 5. Review the logs
cat .claude/logs/workflows/*user-authentication*summary.md

# 6. If needed, resume later
python .claude/scripts/start_workflow.py user-authentication --resume
```

---

## 🛠️ Advanced Usage

### Custom Spec Location
If you have specs in a custom location:

```bash
# Move spec to backlog first
cp -r my-custom-spec/ .claude/specs/backlog/

# Then run workflow
python .claude/scripts/start_workflow.py my-custom-spec
```

### Batch Processing
Process multiple specs:

```bash
# Create a simple batch script
for spec in user-auth payment-gateway analytics; do
    python .claude/scripts/start_workflow.py $spec --mode logged
    sleep 2
done
```

### Integration with CI/CD
```yaml
# GitHub Actions example
- name: Run Workflow
  run: |
    python .claude/scripts/start_workflow.py ${{ env.SPEC_NAME }} \
      --mode logged \
      --log-level INFO
```

---

## 🐛 Troubleshooting

### Spec Not Found
```
❌ ERROR: Spec 'my-spec' not found in backlog
```
**Solution:** Check spec exists with `--status` or `--list`

### Incomplete Spec Warning
```
⚠️  WARNING: Spec 'my-spec' appears incomplete
   Missing: overview.md and requirements.md
```
**Solution:** Add missing files or continue anyway when prompted

### Workflow Fails
Check the logs:
```bash
# Find the latest log
ls -la .claude/logs/workflows/

# View the summary
cat .claude/logs/workflows/*summary.md

# Check detailed log for errors
grep ERROR .claude/logs/workflows/*.log
```

### Clean Up Failed Workflow
```bash
# Remove spec from scope if stuck
rm -rf .claude/specs/scope/problematic-spec

# Move back to backlog
mv .claude/specs/scope/problematic-spec .claude/specs/backlog/
```

---

## 📈 Performance Tips

1. **Use Logged Mode by default** - Best balance of features and performance
2. **Use DEBUG only when troubleshooting** - Generates large logs
3. **Run specs individually** - Better error isolation
4. **Check status before running** - Avoid conflicts
5. **Clean up scope regularly** - Remove stuck specs

---

## 🔗 Related Documentation

- [Spec Creation Guide](SPEC_CREATION.md)
- [Agent Documentation](../agents/README.md)
- [Context Engineering System](CONTEXT_ENGINEERING.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

## 💡 Pro Tips

1. **Always use `--status` first** to understand the current state
2. **Start with `--dry-run`** for new specs to verify setup
3. **Use `--mode logged`** for production work (best logging)
4. **Save summaries** - They're great for documentation
5. **Check logs immediately** if something fails
6. **Use `--resume`** to continue interrupted work

---

*Last Updated: August 2025*
*Version: 2.0*