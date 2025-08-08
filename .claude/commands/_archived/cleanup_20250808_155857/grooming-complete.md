# Grooming Complete Command

Finalize grooming session and generate feature specification.

## Usage
```
/grooming-complete "feature-name"
```

## Process

1. **Compile Grooming Outputs**
   - Research and discovery findings
   - Technical analysis results
   - Prioritization decisions
   - Development roadmap

2. **Generate Specification**
   - Creates `.claude/specs/{feature-name}/` directory
   - Generates initial requirements.md from grooming
   - Prepares for development workflow

3. **Archive Session**
   - Moves session from active to completed
   - Preserves all grooming artifacts
   - Creates grooming summary report

## Output

- Feature specification at `.claude/specs/{feature-name}/`
- Archived grooming at `.claude/grooming/completed/{feature-name}/`
- Suggestion to continue with `/spec-create {feature-name}`

## Example
```
/grooming-complete "payment-integration"
```

This finalizes the grooming and prepares the feature for development.