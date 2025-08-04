Generate detailed requirements for the current spec.

Process:
1. Identify current spec from context or ask user
2. Use business-analyst to create:
   - User stories with acceptance criteria
   - Use cases with actors and flows
   - Data models and schemas
   - Business rules and constraints
   - Non-functional requirements
3. Save structured documentation

Output:
- Update .claude/specs/{spec-name}/requirements.md
- Create .claude/specs/{spec-name}/user-stories.md
- Create .claude/specs/{spec-name}/use-cases.md
- Create .claude/specs/{spec-name}/data-models.md

Usage: /spec-requirements