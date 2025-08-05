# Spec Create Command

Create a new feature specification with proper lifecycle management.

## Usage
```
/spec-create "spec-name" "description" [--stage=backlog|scope]
```

## What it does

📋 **Creates structured specification**  
🎯 **Places in appropriate lifecycle stage**  
📊 **Updates status tracking automatically**  
🔄 **Integrates with workflow management**

## Examples

### Create Idea for Future (Default)
```
/spec-create "mobile-app" "Native mobile application for iOS and Android"
```

**What happens:**
- Creates in `backlog/` stage
- Basic overview and success criteria
- Ready for future prioritization

### Create for Immediate Development
```
/spec-create "user-auth" "Authentication system with 2FA" --stage=scope
```

**What happens:**
- Creates in `scope/` stage
- Triggers detailed requirements generation
- Creates task breakdown automatically
- Updates status dashboard

## Process

### Backlog Stage (Default)
1. **Create Directory**: `.claude/specs/backlog/{spec-name}/`
2. **Load Context**: Cross-platform steering context loading
3. **Generate Overview**: Product-manager creates high-level vision
4. **Set Metadata**: Stage tracking and creation timestamp

### Scope Stage (Immediate Development)  
1. **Create Directory**: `.claude/specs/scope/{spec-name}/`
2. **Load Context**: Full steering documents
3. **Generate Spec**: Business-analyst creates detailed requirements
4. **Create Tasks**: Architect breaks down implementation
5. **Update Tracking**: Status dashboard and roadmap

## Output Structure

```
.claude/specs/{stage}/{spec-name}/
├── overview.md          # Feature overview and vision
├── requirements.md      # Detailed requirements (scope stage)
├── _meta.json          # Spec metadata and tracking
└── README.md           # Quick reference
```

## Implementation

```bash
python .claude/scripts/spec_manager.py create "spec-name" "description" [--stage=backlog|scope]
```

## Integration

- **Auto-updates** status dashboard
- **Follows** steering document guidelines
- **Uses** context engineering for efficiency
- **Triggers** appropriate agents based on stage

## Benefits

### Organized Development  
- **Clear Stages**: Know what's idea vs active development
- **No Clutter**: Test specs separated from real work
- **Status Tracking**: Always know current state

### Efficient Process
- **Stage-Appropriate**: Right level of detail for each stage
- **Context-Aware**: Uses steering documents effectively
- **Automated**: Updates tracking and status automatically

Usage: `/spec-create "feature-name" "Feature description" [--stage=backlog|scope]`