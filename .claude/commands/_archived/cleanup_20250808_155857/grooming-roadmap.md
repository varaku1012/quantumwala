# Grooming Roadmap Command

Create development roadmap during grooming.

## Usage
```
/grooming-roadmap "feature-name"
```

## Process

Generates comprehensive development roadmap including:

1. **Phase Breakdown** (chief-product-manager)
   - Logical development phases
   - Milestone definitions
   - Timeline estimates

2. **Task Dependencies** (architect)
   - Technical task sequencing
   - Dependency mapping
   - Critical path identification

3. **Success Criteria** (business-analyst)
   - Acceptance criteria refinement
   - Testing requirements
   - Definition of done

## Output

Creates `.claude/grooming/active/{feature-name}/roadmap.md` with:
- Development phases with timelines
- Task dependencies and sequencing
- Resource allocation plan
- Risk mitigation strategies
- Success metrics

## Example
```
/grooming-roadmap "payment-integration"
```

This creates a detailed implementation roadmap for the payment integration feature.