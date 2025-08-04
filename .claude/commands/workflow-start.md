# Workflow Start Command

Start an automated workflow from project inception to implementation.

## Usage
```
/workflow-start "project-name" "project description"
```

## Automated Process

This command orchestrates the entire development workflow:

### 1. Project Initialization
- Creates project structure
- Initializes steering context
- Sets up tracking

### 2. Specification Creation
```bash
# Automatically runs:
/spec-create {project-name} "{description}"
```

### 3. Requirements Generation
- Uses business-analyst agent
- Creates detailed requirements
- Validates with steering context

### 4. Design Phase
- Uses architect agent
- Uses uiux-designer agent
- Validates against requirements

### 5. Task Generation
```bash
# Automatically runs:
python .claude/scripts/task-generator.py {project-name}
```

### 6. Implementation
- Executes tasks in order
- Respects dependencies
- Validates each step

## Workflow Features

### Smart Routing
- Automatically selects appropriate agents
- Follows optimal workflow path
- Adapts based on project type

### Context Awareness
- All agents use steering context
- Minimal token usage throughout
- Consistent understanding

### Quality Gates
- Requirements validation
- Design validation
- Implementation review
- Automated testing

### Progress Tracking
- Real-time updates
- Dashboard integration
- Completion notifications

## Example

```
/workflow-start "user-authentication" "Secure login system with 2FA support"

Output:
✓ Project initialized
✓ Steering context created
✓ Specification created
✓ Requirements generated (12 user stories)
✓ Design completed (UI + Architecture)
✓ Tasks generated (8 implementation tasks)
⚡ Starting implementation...
  ✓ Task 1 complete: Create user model
  ✓ Task 2 complete: Add password hashing
  ... continues automatically ...
```

## Workflow Customization

### Skip Phases
```
/workflow-start "project" "description" --skip design
```

### Parallel Execution
```
/workflow-start "project" "description" --parallel
```

### Custom Agents
```
/workflow-start "project" "description" --agents "product-manager,architect"
```

## Integration Points

- Uses all Phase 1-3 features
- Leverages context engineering
- Employs validation agents
- Utilizes task automation

## Monitoring

While workflow runs:
1. Check `/dashboard` for progress
2. View logs in terminal
3. Interrupt with Ctrl+C if needed

## Benefits

- **Zero Manual Steps**: Fully automated
- **Consistent Quality**: Same process every time
- **Fast Execution**: Parallel where possible
- **Context Efficient**: Uses minimal tokens
- **Error Handling**: Graceful failure recovery