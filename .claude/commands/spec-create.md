Create a new feature specification.

Arguments:
1. spec-name: Identifier for the specification (kebab-case)
2. description: Brief description of the feature

Process:
1. Create directory .claude/specs/{spec-name}/
2. Load steering documents using context scripts:
   ```bash
   # Cross-platform context loading:
   python .claude/scripts/get_content.py .claude/steering/product.md
   python .claude/scripts/get_content.py .claude/steering/tech.md
   ```
3. Use product-manager to define feature scope with steering context
4. Use business-analyst for initial requirements
5. Create spec document with:
   - Feature overview
   - User value proposition
   - High-level requirements
   - Success criteria

Output files:
- .claude/specs/{spec-name}/overview.md
- .claude/specs/{spec-name}/requirements.md

Context Engineering Note:
- Agents now load only relevant steering sections
- Reduces token usage by 50-70%
- Cross-platform compatible paths

Usage: /spec-create "user-authentication" "Secure login with 2FA"