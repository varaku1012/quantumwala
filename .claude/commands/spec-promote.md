# Spec Promote Command

Move specifications through the development lifecycle stages.

## Usage
```
/spec-promote "spec-name" [--to=scope|completed|archived] [--reason="reason"]
```

## What it does

🔄 **Manages spec lifecycle transitions**  
📋 **Promotes specs through development stages**  
✅ **Validates promotion requirements**  
📊 **Updates status tracking automatically**

## Lifecycle Stages

```
💡 Idea → 📋 Backlog → 🎯 Scope → ✅ Completed
                              ↘️ 🧪 Sandbox (for testing)
                              ↘️ ❄️ Archived (if cancelled)
```

## Examples

### Start Development (Backlog → Scope)
```
/spec-promote "user-authentication" --to=scope --reason="Ready for sprint 3"
```

**What happens:**
1. Moves spec from `backlog/` to `scope/`
2. Triggers detailed requirements generation
3. Creates task breakdown
4. Updates status dashboard
5. Notifies team of new active work

### Mark Complete (Scope → Completed)
```
/spec-promote "user-authentication" --to=completed --reason="All tests passing, deployed to prod"
```

**Validation checks:**
- ✅ All tasks marked complete (>90% completion required)
- ✅ Requirements and design documents exist
- ✅ Implementation verified

**What happens:**
1. Validates completion requirements
2. Moves to `completed/` directory
3. Creates completion report
4. Updates team metrics
5. Archives active development files

### Archive Spec (Any → Archived)
```
/spec-promote "old-feature" --to=archived --reason="Superseded by new design"
```

**What happens:**
1. Safely moves spec to `archived/`
2. Maintains history and documentation
3. Updates roadmap
4. Clears from active tracking

## Validation Rules

### To Scope (Start Development)
- ✅ Clear problem statement exists
- ✅ Basic requirements defined
- ⚠️ Warns if conflicting active specs

### To Completed (Finish Feature)
- ✅ Tasks file exists with defined tasks
- ✅ >90% of tasks marked complete
- ✅ No blocking issues remain
- 🚫 **Blocks promotion if validation fails**

### To Archived (Cancel/Deprecate)
- ✅ Always allowed with reason
- ℹ️ Preserves all history and documentation

## Implementation

```bash
python .claude/scripts/spec_manager.py promote "spec-name" --to=stage --reason="reason"
```

## Integration

- **Auto-updates** status dashboard
- **Triggers** appropriate agents for stage requirements
- **Logs** all transitions for audit trail
- **Notifies** team of status changes

## Benefits

### Clear Workflow
- **Structured Process**: Defined stages with clear criteria
- **Validation Gates**: Prevents premature progression
- **Audit Trail**: Complete history of decisions

### Team Coordination
- **Visibility**: Everyone knows current stage of all work
- **Accountability**: Clear ownership and progression rules
- **Planning**: Better sprint and resource planning

### Quality Control
- **Requirements**: Ensures proper completion before marking done
- **Documentation**: Maintains complete project records
- **Metrics**: Tracks team velocity and bottlenecks