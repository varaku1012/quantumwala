# Grooming Prioritize Command

Analyze and prioritize a feature during grooming.

## Usage
```
/grooming-prioritize "feature-name"
```

## Process

Coordinates multiple agents to assess:
1. **Business Value** (chief-product-manager)
   - Revenue impact
   - User satisfaction impact
   - Market differentiation

2. **Technical Complexity** (architect)
   - Architecture changes required
   - Integration effort
   - Risk assessment

3. **Resource Requirements** (product-manager)
   - Team composition
   - Time estimates
   - Dependencies

## Output

Creates `.claude/grooming/active/{feature-name}/priority.md` with:
- Business value score (1-10)
- Technical complexity rating (Low/Medium/High)
- Priority ranking (P0/P1/P2/P3)
- Resource requirements
- Implementation recommendation

## Example
```
/grooming-prioritize "payment-integration"
```