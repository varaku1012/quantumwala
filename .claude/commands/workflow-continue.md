# Workflow Continue Command

Automatically continues workflow execution without manual intervention.

## Usage
```
/workflow-continue
```

## Purpose
This command ensures workflow continuity by:
1. Detecting current workflow state
2. Identifying next required action
3. Executing next phase automatically
4. Continuing until completion

## Workflow State Detection

```python
# Check current state
state = detect_workflow_state()

if state.phase == "steering_complete":
    execute("/spec-create")
elif state.phase == "spec_created":
    execute("/spec-requirements")
elif state.phase == "requirements_done":
    execute("/spec-design")
elif state.phase == "design_done":
    execute("/spec-tasks")
elif state.phase == "tasks_generated":
    execute("/spec-orchestrate")
```

## Auto-Execution Logic

When this command is invoked:

1. **Load State**
   ```bash
   python .claude/scripts/workflow_state.py --get-current
   ```

2. **Execute Next Phase**
   - Automatically runs the appropriate command
   - No user confirmation needed
   - Logs progress to session file

3. **Chain Execution**
   - After completing current phase
   - Automatically invokes `/workflow-continue` again
   - Continues until workflow complete

## Integration Points

Works with:
- All spec-* commands
- Task execution commands
- Validation commands
- Logging system

## Usage in Agents

Agents should invoke this command after completing their phase:
```
After completing the specification, I'll continue the workflow:
/workflow-continue
```

## Benefits

- Zero manual intervention
- Consistent execution
- Automatic error recovery
- Complete audit trail