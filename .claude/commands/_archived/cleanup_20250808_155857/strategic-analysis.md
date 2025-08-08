---
command: strategic-analysis  
description: Conduct comprehensive market and strategic analysis for a feature
arguments:
  - name: feature-name
    description: Feature to analyze
    required: true
  - name: depth
    description: Analysis depth (quick/standard/comprehensive)
    required: false
    default: standard
---

Conduct strategic analysis including market research, competitive analysis, and business value assessment.

## Usage
```
/strategic-analysis "feature-name" [depth]
```

## Analysis Components

### 1. Market Research
- Industry trends and opportunities
- Target user segments
- Market size and growth potential
- Regulatory considerations

### 2. Competitive Analysis  
- Direct competitor features
- Market positioning
- Differentiation opportunities
- Pricing strategies

### 3. Business Value Assessment
- Revenue potential
- Cost-benefit analysis
- Risk assessment
- Success metrics definition

### 4. Technical Feasibility
- Architecture implications
- Resource requirements
- Timeline estimates
- Integration considerations

## Execution Flow

1. **Parallel Research** (5-10 min)
   - product-manager: Market analysis
   - business-analyst: User research
   - architect: Technical feasibility
   - data-engineer: Data requirements

2. **Synthesis** (5 min)
   - Combine findings
   - Score opportunities
   - Define recommendations

3. **Output Generation**
   - Strategic recommendation document
   - Feature prioritization matrix
   - Risk mitigation plan

## Output Location
```
.claude/analysis/{feature-name}/
├── market-research.md
├── competitive-analysis.md
├── business-value.md
├── technical-feasibility.md
└── strategic-recommendation.md
```

## Integration
Results automatically feed into:
- `/grooming-workflow` for prioritization
- `/spec-create` for specification
- `/planning` for execution strategy

## Example
```
/strategic-analysis "ai-powered-search" comprehensive
```

This analyzes the AI search feature opportunity across all dimensions.