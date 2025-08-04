# Steering Setup Command

Initialize comprehensive project context through steering documents.

## Usage
```
/steering-setup
```

## Process

1. **Analyze Existing Project**
   - Scan codebase for patterns
   - Identify technology stack
   - Extract coding conventions
   - Review existing documentation

2. **Create Steering Documents**
   - `product.md` - Vision, goals, target users
   - `tech.md` - Technology stack, standards
   - `structure.md` - Conventions, patterns

3. **Use Steering Context Manager**
   Use the steering-context-manager agent to create comprehensive steering documents:
   ```
   Use the steering-context-manager agent to initialize project steering documents.
   
   The agent should:
   1. Analyze the current codebase to identify patterns
   2. Create product.md with vision and goals
   3. Create tech.md with technical standards
   4. Create structure.md with project conventions
   5. Ensure all documents are comprehensive and actionable
   ```

## Manual Process (if agent unavailable)

### Step 1: Analyze Project
```bash
# Check for package.json, requirements.txt, etc.
# Identify frameworks and libraries
# Review folder structure
# Examine coding patterns
```

### Step 2: Create Product Document
Create `.claude/steering/product.md`:
```markdown
# Product Steering Document

## Vision Statement
[Define the product's purpose and impact]

## Target Users
- **Primary**: [Who are they and what do they need?]
- **Secondary**: [Additional user groups]

## Core Features
[List main features with purpose]

## Success Metrics
[How will you measure success?]
```

### Step 3: Create Technical Document
Create `.claude/steering/tech.md`:
```markdown
# Technical Steering Document

## Technology Stack
[List all technologies used]

## Development Standards
[Coding standards, testing requirements]

## Architecture Patterns
[Design patterns, API approach]
```

### Step 4: Create Structure Document
Create `.claude/steering/structure.md`:
```markdown
# Structure Steering Document

## Directory Organization
[Project structure explanation]

## Naming Conventions
[File, function, variable naming]

## Code Organization
[How code should be organized]
```

## Integration Points

After setup, all agents will:
1. Load steering documents automatically
2. Align their work with documented standards
3. Suggest updates when patterns evolve
4. Maintain consistency across features

## Next Steps

After steering setup:
1. Run `/spec-create` for new features
2. All agents will use steering context
3. Update steering docs as project evolves
4. Review quarterly for major updates
