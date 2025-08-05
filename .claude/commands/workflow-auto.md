# Automated Workflow Orchestrator

Executes complete development workflow without manual intervention.

## Usage
```
/workflow-auto "feature-name" "feature description"
```

## Process

1. **Check Prerequisites**
   - Verify steering context exists
   - If not, run steering-setup first

2. **Create Feature Specification**
   ```
   /spec-create {feature-name} "{description}"
   ```

3. **Generate Requirements** (automatic)
   ```
   /spec-requirements
   ```

4. **Create Design** (automatic)
   ```
   /spec-design
   ```

5. **Generate Tasks** (automatic)
   ```
   /spec-tasks
   ```

6. **Execute Implementation** (automatic)
   - Execute all generated tasks sequentially
   - Log progress after each task
   - Mark tasks complete in tracking

7. **Quality Assurance** (automatic)
   - Run tests if available
   - Generate completion report

## Auto-logging
- Session log created at start
- Progress logged after each phase
- Final report generated on completion

## Error Handling
- Continues on non-critical errors
- Logs all issues for review
- Suggests fixes for common problems

## Example
```
/workflow-auto "user-auth" "Secure authentication with 2FA and OAuth support"
```

This will automatically:
1. Create the spec
2. Generate all documentation
3. Create implementation tasks
4. Execute the implementation
5. Run validation
6. Generate reports