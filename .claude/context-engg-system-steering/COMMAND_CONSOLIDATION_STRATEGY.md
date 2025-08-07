# Command Consolidation Strategy

## Current State Analysis

### Statistics
- **Total Commands**: 50+
- **Workflow Orchestrators**: 8 (HIGH REDUNDANCY)
- **Spec Management**: 12 (MODERATE REDUNDANCY)
- **Grooming/Planning**: 6 (LOW REDUNDANCY)
- **Bug Management**: 5 (NO REDUNDANCY)
- **Others**: ~19 (NO REDUNDANCY)

### Critical Issues
1. **8 different ways** to run the same workflow
2. **Duplicate commands** for task generation
3. **Overlapping spec execution** commands
4. **User confusion** from too many choices
5. **Maintenance burden** of similar code

## Proposed Consolidation

### Phase 1: Consolidate Workflow Commands

#### REPLACE These 8 Commands:
```
/master-orchestrate
/workflow-orchestrator
/workflow-auto
/dev-workflow
/dev-workflow-run
/parallel-workflow
/optimized-execution
/workflow-start
```

#### WITH These 3 Commands:

##### 1. `/workflow` (Primary Interface)
```bash
# Simple usage
/workflow "build user authentication"

# With options
/workflow "build user authentication" --mode=parallel --auto=true

# Modes:
--mode=sequential  # Traditional sequential execution
--mode=parallel    # Intelligent parallelization (default)
--mode=optimized   # Maximum optimization with context engineering

# Automation:
--auto=true        # Fully autonomous (no stops)
--auto=false       # Manual confirmation at each phase
--auto=smart       # Stop only on errors (default)

# Monitoring:
--monitor=none     # No monitoring
--monitor=basic    # Simple progress updates (default)  
--monitor=full     # Real-time dashboard
```

##### 2. `/workflow-control` (Manual Control)
```bash
/workflow-control start "feature-name"    # Start new workflow
/workflow-control continue                # Continue from last point
/workflow-control pause                   # Pause execution
/workflow-control reset                   # Reset workflow state
/workflow-control status                  # Check current status
```

##### 3. `/task` (Single Task Execution)
```bash
# Execute single task with optimization
/task "developer" "implement user model" --optimize=true
/task "qa-engineer" "write tests" --context=minimal
```

### Phase 2: Consolidate Spec Commands

#### REMOVE Duplicates:
- `/spec-generate-tasks` (duplicate of `/spec-tasks`)
- `/spec-implement` (covered by `/spec-orchestrate`)
- `/spec-execute` (covered by `/spec-orchestrate`)

#### KEEP These Essential Commands:
```bash
/spec-create "name" "description"     # Create new spec
/spec-requirements                    # Generate requirements
/spec-design                          # Create design
/spec-tasks                           # Generate tasks
/spec-orchestrate                     # Execute all tasks
/spec-review                          # Review implementation
/spec-status                          # Check status
/spec-list                            # List all specs
```

### Phase 3: Create Command Categories

#### Core Workflows (3 commands)
```bash
/workflow          # Main workflow execution
/workflow-control  # Manual workflow control
/task              # Single task execution
```

#### Specification Management (8 commands)
```bash
/spec-create       # Create specification
/spec-requirements # Generate requirements
/spec-design       # Design phase
/spec-tasks        # Task generation
/spec-orchestrate  # Execute tasks
/spec-review       # Review results
/spec-status       # Check status
/spec-list         # List specs
```

#### Feature Grooming (5 commands)
```bash
/groom             # Full grooming workflow
/groom-start       # Start grooming
/groom-prioritize  # Set priorities
/groom-roadmap     # Create roadmap
/groom-complete    # Finalize grooming
```

#### Bug Management (5 commands)
```bash
/bug-create        # Report bug
/bug-analyze       # Analyze cause
/bug-fix           # Implement fix
/bug-verify        # Verify fix
/bug-status        # Check status
```

#### System Management (6 commands)
```bash
/setup             # Initial setup
/status            # System status
/dashboard         # Monitoring dashboard
/logs              # Log management
/backup            # State backup
/version           # Version info
```

#### Analysis Tools (3 commands)
```bash
/analyze           # Analyze codebase/feature
/planning          # Planning and dependencies
/performance       # Performance metrics
```

## Migration Strategy

### Step 1: Create New Unified Commands
```python
# workflow.py - Unified workflow command
class WorkflowCommand:
    def __init__(self, mode='parallel', auto='smart', monitor='basic'):
        self.mode = mode
        self.auto = auto
        self.monitor = monitor
    
    def execute(self, description):
        # Route to appropriate executor based on mode
        if self.mode == 'parallel':
            return ParallelWorkflowOrchestrator().execute(description)
        elif self.mode == 'optimized':
            return OptimizedExecutor().execute(description)
        else:
            return SequentialWorkflow().execute(description)
```

### Step 2: Create Deprecation Wrappers
```python
# deprecated_commands.py
def deprecated_command(old_name, new_command, params):
    print(f"⚠️ '{old_name}' is deprecated. Use '{new_command}' instead.")
    print(f"   Equivalent: {new_command} {params}")
    # Execute using new command
    return execute_new_command(new_command, params)
```

### Step 3: Update Documentation
Create migration guide showing old → new mappings:

| Old Command | New Command | Parameters |
|-------------|-------------|------------|
| `/workflow-auto` | `/workflow` | `--auto=true` |
| `/parallel-workflow` | `/workflow` | `--mode=parallel` |
| `/optimized-execution` | `/task` | `--optimize=true` |
| `/spec-implement` | `/spec-orchestrate` | (no change) |

## Benefits of Consolidation

### For Users
1. **Clearer Choices**: 25 commands instead of 50+
2. **Logical Grouping**: Commands organized by purpose
3. **Consistent Interface**: Similar commands work similarly
4. **Better Discovery**: Easier to find the right command

### For Maintainers
1. **Less Code Duplication**: Single implementation per feature
2. **Easier Testing**: Fewer code paths to test
3. **Simpler Documentation**: Fewer commands to document
4. **Faster Bug Fixes**: Fix once, works everywhere

### For Performance
1. **Shared Optimization**: All workflows benefit from improvements
2. **Better Caching**: Unified execution path enables better caching
3. **Resource Management**: Single point for resource control
4. **Monitoring**: Unified metrics collection

## Implementation Priority

### Week 1: Core Consolidation
- [ ] Create `/workflow` command with all modes
- [ ] Create `/workflow-control` for manual control
- [ ] Create `/task` for single task execution
- [ ] Add deprecation warnings to old commands

### Week 2: Spec Consolidation
- [ ] Remove duplicate spec commands
- [ ] Enhance `/spec-orchestrate` to cover all execution modes
- [ ] Update spec documentation

### Week 3: Testing & Migration
- [ ] Test all command mappings
- [ ] Update all documentation
- [ ] Create migration scripts
- [ ] Notify users of changes

### Week 4: Cleanup
- [ ] Remove deprecated commands (keep for 30 days first)
- [ ] Archive old implementations
- [ ] Update all agent references
- [ ] Final documentation review

## Success Metrics

### Quantitative
- Reduce command count from 50+ to ~25
- Reduce code duplication by 60%
- Improve execution time by 20% (shared optimizations)
- Reduce bug reports by 40% (fewer code paths)

### Qualitative
- User satisfaction (easier to find commands)
- Developer velocity (faster to add features)
- System reliability (fewer edge cases)
- Documentation clarity (simpler to explain)

## Rollback Plan

If consolidation causes issues:
1. Keep old commands as aliases temporarily
2. Provide detailed migration guide
3. Support both old and new for transition period
4. Gather feedback and adjust

## Next Steps

1. **Get Approval**: Review this strategy with team
2. **Create Prototype**: Build `/workflow` command first
3. **Test Thoroughly**: Ensure no functionality lost
4. **Gradual Rollout**: Start with power users
5. **Monitor & Adjust**: Track usage and issues