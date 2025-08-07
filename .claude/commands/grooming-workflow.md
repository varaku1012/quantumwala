# Grooming Workflow Command

Automated grooming workflow for feature analysis and prioritization before development.

## Usage
```
/grooming-workflow "feature-name" "feature description"
```

## Workflow Phases

### Phase 1: Research & Discovery (Parallel)
- **business-analyst**: User needs and requirements gathering
- **chief-product-manager**: Market research and competitor analysis
- **architect**: Technical feasibility study

### Phase 2: Technical Analysis
- **architect**: Architecture impact and integration requirements
- **security-engineer**: Security implications
- **performance-optimizer**: Performance considerations

### Phase 3: Prioritization
- **chief-product-manager**: Business value scoring
- **architect**: Technical complexity assessment
- **product-manager**: Resource requirements and priority ranking

### Phase 4: Development Roadmap
- **chief-product-manager**: Phase breakdown and timeline
- **architect**: Task sequencing and dependencies
- **business-analyst**: Acceptance criteria refinement

### Phase 5: Spec Generation
- Compile all grooming outputs
- Generate feature specification
- Transition to dev-workflow with `/spec-create`

## Automation
This command automatically:
1. Creates grooming session directory
2. Coordinates agents through all phases
3. Generates consolidated outputs
4. Archives completed session
5. Triggers spec creation

## Example
```
/grooming-workflow "payment-integration" "Add Stripe payment processing with subscription management"
```

This will create:
- `.claude/grooming/active/payment-integration/`
- Run all grooming phases
- Generate `.claude/specs/payment-integration/`
- Archive to `.claude/grooming/completed/`