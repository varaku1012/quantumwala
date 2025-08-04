# Master Orchestrate Command

The ultimate autonomous workflow executor that runs the entire development lifecycle without stopping.

## Usage
```
/master-orchestrate "project-name" "project description"
```

## CRITICAL: Autonomous Execution

This command will:
1. Execute the ENTIRE workflow from start to finish
2. NOT stop between phases for user input
3. Handle all transitions automatically
4. Only stop when everything is complete

## Execution Flow

```python
# Pseudo-code for the execution flow
def master_orchestrate(project_name, description):
    # Phase 1: Initialize
    if not steering_exists():
        execute_steering_setup()
    
    # Phase 2: Create Specification
    create_spec(project_name, description)
    
    # Phase 3: Generate Requirements (AUTOMATIC)
    generate_requirements()
    
    # Phase 4: Create Design (AUTOMATIC)
    create_design()
    
    # Phase 5: Generate Tasks (AUTOMATIC)
    generate_tasks()
    
    # Phase 6: Implement All Tasks (AUTOMATIC)
    for task in get_all_tasks():
        implement_task(task)
        mark_complete(task)
    
    # Phase 7: Validate (AUTOMATIC)
    run_validation()
    
    # Phase 8: Generate Report
    generate_completion_report()
```

## Implementation Protocol

When this command is invoked:

1. **Execute via Master Orchestrator Script**
   ```bash
   python .claude/scripts/master_orchestrator_fix.py "{project-name}" "{description}"
   ```

2. **Fallback: Use Chief Product Manager V2**
   If the script is unavailable, use the agent:
   ```
   Use the chief-product-manager-v2 agent to orchestrate the complete development of {project-name}.
   
   The agent should:
   1. Execute ALL phases without stopping
   2. Progress automatically from phase to phase
   3. Use /planning commands for parallel execution
   4. Call integration scripts for logging and state
   5. Implement all generated tasks
   6. Only stop when fully complete
   
   Project: {project-name}
   Description: {description}
   
   Integration hooks to use:
   - After each phase: python .claude/scripts/workflow_state.py --complete-phase PHASE_NAME
   - For planning: /planning [phase] {project-name}
   - For logging: python .claude/scripts/log_manager.py create --type session --title {project-name}
   
   CRITICAL: Do not stop between phases. Execute the complete workflow autonomously.
   ```

2. **Automatic Phase Progression**
   - After steering → Create spec
   - After spec → Generate requirements
   - After requirements → Create design
   - After design → Generate tasks
   - After tasks → Implement each task
   - After implementation → Validate

3. **Task Implementation Loop**
   ```
   For each task in tasks.md:
   1. Load task details
   2. Implement using spec-task-executor
   3. Mark complete in tasks.md
   4. Log progress
   5. Continue to next task
   ```

## Error Handling

If any phase fails:
1. Log the error with details
2. Attempt recovery if possible
3. Skip to next viable phase
4. Report all issues at end

## Progress Tracking

Continuous updates in format:
```
[Phase 1/7] ✓ Steering context initialized
[Phase 2/7] ⚡ Creating specification...
[Phase 2/7] ✓ Specification created
[Phase 3/7] ⚡ Generating requirements...
```

## Parallel Execution

When possible, execute in parallel:
- Multiple independent tasks
- Design components (UI + Architecture)
- Test creation alongside implementation

## Completion Criteria

Only stop when:
- All phases completed
- All tasks implemented
- All tests passing
- Final report generated

## Benefits

- **Zero Manual Steps**: Fully autonomous
- **Continuous Execution**: No stopping between phases
- **Smart Recovery**: Handles errors gracefully
- **Complete Visibility**: Real-time progress updates
- **Faster Delivery**: Parallel execution where possible

## Example

```
/master-orchestrate "user-auth" "Complete authentication system with 2FA"

Output:
[Phase 1/7] ✓ Steering context loaded
[Phase 2/7] ✓ Specification created: user-auth
[Phase 3/7] ✓ Requirements generated (15 user stories)
[Phase 4/7] ✓ Design completed (UI + Architecture)
[Phase 5/7] ✓ Tasks generated (12 implementation tasks)
[Phase 6/7] ⚡ Implementing tasks...
  ✓ Task 1.1: Create user model
  ✓ Task 1.2: Add password hashing
  ✓ Task 2.1: Create login endpoint
  ... (continues automatically)
[Phase 7/7] ✓ Validation complete
✅ Project complete! All 12 tasks implemented successfully.
```