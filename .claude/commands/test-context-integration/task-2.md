# Task 2: Build cross-agent consistency demo

Execute implementation task 2 for test-context-integration specification.

## Process

1. **Load Task Context**
   ```bash
   # Get specific task details:
   python .claude/scripts/get_tasks.py test-context-integration 2 --mode single
   
   # Load relevant specifications:
   python .claude/scripts/get_content.py .claude/specs/test-context-integration/requirements.md
   python .claude/scripts/get_content.py .claude/specs/test-context-integration/design.md
   
   # Load technical context:
   python .claude/scripts/get_content.py .claude/steering/tech.md
   ```

2. **Pre-Implementation Research** (if needed)
   Use spec-design-web-researcher agent to verify modern patterns for:
      - - Multiple agents reference same context
   - - Verify aligned understanding
   - - No context drift between agents

3. **Implementation**
   Use spec-task-executor agent to:
   - Write tests first (TDD approach)
   - Implement the functionality
   - Follow project conventions
   - Add appropriate documentation

4. **Validation**
   Use spec-implementation-reviewer agent to:
   - Verify all acceptance criteria met
   - Check test coverage
   - Validate code quality
   - Ensure documentation complete

5. **Mark Complete**
   ```bash
   python .claude/scripts/get_tasks.py test-context-integration 2 --mode complete
   ```

## Task Details
- - Multiple agents reference same context
- - Verify aligned understanding
- - No context drift between agents

## Dependencies
No dependencies

## Context Engineering
- Loads only task-specific context
- Uses ~3,000 tokens instead of ~15,000
- Automated completion tracking

## Usage
```
/test-context-integration-task-2
```
