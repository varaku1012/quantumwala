# Spec Status Command

Get organized overview of all specifications and their lifecycle status.

## Usage
```
/spec-status [--detailed] [--stage=backlog|scope|completed]
```

## What it does

📊 **Shows structured spec organization**  
🎯 **Clear status visibility for active development**  
📋 **Backlog planning and prioritization**  
✅ **Completion tracking and metrics**

## Examples

### Full Overview (Default)
```
/spec-status
```

**Output:**
```
📊 SPECS OVERVIEW
═══════════════════

📋 BACKLOG (3 specs)
├── payment-integration     [Idea stage]
├── mobile-app             [Concept ready]  
└── advanced-analytics     [Research needed]

🎯 IN SCOPE (2 specs)
├── user-authentication    [75% complete - 6/8 tasks done]
└── analytics-dashboard    [40% complete - 4/10 tasks done]

✅ COMPLETED (1 spec)
├── basic-dashboard        [Deployed 2025-01-15]

🧪 SANDBOX (2 specs)
├── test-demo              [Testing only]
└── proof-of-concept       [Experimental]

📈 VELOCITY: 2.3 specs/month | ⏱️ AVG COMPLETION: 3.2 weeks
```

### Specific Stage
```
/spec-status --stage=scope
```

**Shows only active development specs with detailed progress**

### Detailed View
```
/spec-status --detailed
```

**Includes:**
- Task breakdown and completion rates
- Requirements and design status
- Last updated timestamps
- Priority levels

## Implementation

```bash
python .claude/scripts/spec_manager.py status [--detailed]
```

## New Structured Organization

Instead of flat `.claude/specs/` directory, specs are now organized by lifecycle stage:

```
.claude/specs/
├── 📋 backlog/     # Ideas & future features  
├── 🎯 scope/       # Active development
├── ✅ completed/   # Finished features
├── 🧪 sandbox/     # Test/experimental specs
├── ❄️ archived/    # Old/deprecated specs
└── 📊 _meta/       # Status dashboard & roadmap
```

## Benefits

### For Developers
- **Clear Focus**: See exactly what's in progress vs completed
- **No Clutter**: Test specs separated from real work
- **Priority Guidance**: Know what to work on next

### For Teams  
- **Status Meetings**: Quick overview of all work
- **Planning**: Backlog management and sprint planning
- **Metrics**: Track velocity and bottlenecks

### For Managers
- **Visibility**: Complete project status at a glance
- **Resource Planning**: Understand current workload
- **Progress Reports**: Data for stakeholder updates
