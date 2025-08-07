# Grooming Start Command

Initialize a new grooming session for a feature.

## Usage
```
/grooming-start "feature-name"
```

## Process

1. Creates grooming session directory at `.claude/grooming/active/{feature-name}/`
2. Initializes session manifest
3. Prepares templates for grooming activities
4. Sets up tracking for grooming phases

## Next Steps

After starting grooming, use:
- `/grooming-workflow` for automated workflow
- Individual grooming commands for manual process
- `/grooming-complete` to finalize and generate spec

## Example
```
/grooming-start "payment-integration"
```

This creates the grooming workspace for analyzing the payment integration feature.