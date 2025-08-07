# Unified Workflow Command

**The ONE command for all workflow execution needs**  
Replaces: workflow-auto, parallel-workflow, dev-workflow, master-orchestrate, and 4 others

## Usage

### Simple (Uses intelligent defaults)
```bash
/workflow "build user authentication system"
```

### With Options
```bash
/workflow "build shopping cart" --mode=parallel --auto=true --monitor=full
```

## Options

### Execution Mode (--mode)
- `sequential` - Traditional step-by-step execution
- `parallel` - Intelligent parallelization (DEFAULT)
- `optimized` - Maximum optimization with context engineering

### Automation Level (--auto)
- `manual` - Stop at each phase for confirmation  
- `smart` - Stop only on errors (DEFAULT)
- `auto` - Fully autonomous, no stops

### Monitoring Level (--monitor)
- `none` - No monitoring output
- `basic` - Simple progress updates (DEFAULT)
- `full` - Real-time dashboard at http://localhost:8080

## Examples

### Quick Development
```bash
# Fast, parallel execution with basic monitoring
/workflow "create todo app"
```

### Careful Development
```bash
# Sequential with manual confirmation at each step
/workflow "payment integration" --mode=sequential --auto=manual
```

### Production Build
```bash
# Fully optimized, autonomous with dashboard
/workflow "enterprise dashboard" --mode=optimized --auto=auto --monitor=full
```

### With Custom Spec Name
```bash
/workflow "user profile system" --spec-name="user-profile-v2"
```

## What It Does

1. **Creates specification** structure in `.claude/specs/`
2. **Generates requirements** using business-analyst
3. **Creates design** using architect and uiux-designer
4. **Generates tasks** from requirements and design
5. **Implements features** using developer
6. **Tests everything** using qa-engineer
7. **Reviews implementation** using code-reviewer

## Mode Comparison

| Mode | Speed | Token Usage | Best For |
|------|-------|-------------|----------|
| Sequential | Slow | High (~20K) | Learning, debugging |
| Parallel | Fast | Medium (~10K) | Most projects |
| Optimized | Fastest | Low (~6K) | Production, large projects |

## Automation Comparison

| Level | User Interaction | Best For |
|-------|------------------|----------|
| Manual | High - confirms each phase | First-time features |
| Smart | Medium - only on errors | Development |
| Auto | None - fully autonomous | Trusted workflows |

## Monitoring Comparison

| Level | Output | Best For |
|-------|--------|----------|
| None | Silent | Scripts, CI/CD |
| Basic | Console progress | Development |
| Full | Web dashboard | Team collaboration |

## Advanced Usage

### Combining Options
```bash
# Maximum speed for trusted workflow
/workflow "api endpoints" --mode=optimized --auto=auto --monitor=none

# Maximum control for critical feature
/workflow "payment system" --mode=sequential --auto=manual --monitor=full

# Balanced for everyday development
/workflow "new feature" --mode=parallel --auto=smart --monitor=basic
```

### Integration with CI/CD
```bash
# In GitHub Actions or Jenkins
/workflow "$FEATURE_DESCRIPTION" --mode=optimized --auto=auto --monitor=none
```

### Team Collaboration
```bash
# Share progress with team via dashboard
/workflow "team feature" --monitor=full
# Team can view at http://localhost:8080
```

## Migration from Old Commands

| If you used... | Now use... |
|----------------|------------|
| `/workflow-auto` | `/workflow --auto=auto` |
| `/parallel-workflow` | `/workflow --mode=parallel` |
| `/dev-workflow` | `/workflow --auto=smart` |
| `/master-orchestrate` | `/workflow --mode=optimized --auto=auto` |
| `/optimized-execution` | `/workflow --mode=optimized` |
| `/workflow-start` | `/workflow --auto=manual` |

## Output

The command provides:
- Progress updates based on monitoring level
- Phase completion status
- Execution time per phase
- Token usage (in optimized mode)
- Error details if any
- Final summary

## Files Created

```
.claude/specs/{spec-name}/
├── overview.md
├── requirements.md
├── design.md
├── tasks.md
├── implementation/
├── tests/
└── status.md
```

## Performance

- **Sequential Mode**: ~60 seconds for medium feature
- **Parallel Mode**: ~30 seconds (50% faster)
- **Optimized Mode**: ~20 seconds (66% faster)

## Error Handling

- **Manual mode**: Asks what to do on error
- **Smart mode**: Attempts retry, then asks
- **Auto mode**: Attempts recovery, skips if failed

## Implementation

```bash
python .claude/scripts/unified_workflow.py "description" \
  --mode=parallel \
  --auto=smart \
  --monitor=basic
```

## Benefits Over Old Commands

1. **Single Interface**: One command with options instead of 8 commands
2. **Flexible**: Adjust behavior without changing commands
3. **Discoverable**: Clear options make capabilities obvious
4. **Maintainable**: Single codebase for all workflows
5. **Optimized**: Shared improvements benefit all modes

## Tips

- Start with defaults (parallel, smart, basic)
- Use `--mode=optimized` for production features
- Use `--auto=manual` when learning
- Use `--monitor=full` for team collaboration
- Spec name is auto-generated from description

## Next Steps

After workflow completes:
- Review generated specs in `.claude/specs/{spec-name}/`
- Check implementation in project directories
- Run `/workflow-control status` to see current state
- Use `/task` for specific fixes or additions