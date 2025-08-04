# Task 3: Create login endpoint

Execute implementation task 3 for auth-test specification.

## Process

1. **Load Task Context**
   ```bash
   # Get specific task details:
   python .claude/scripts/get_tasks.py auth-test 3 --mode single
   
   # Load relevant specifications:
   python .claude/scripts/get_content.py .claude/specs/auth-test/requirements.md
   python .claude/scripts/get_content.py .claude/specs/auth-test/design.md
   
   # Load technical context:
   python .claude/scripts/get_content.py .claude/steering/tech.md
   ```

2. **Pre-Implementation Research** (if needed)
   Use spec-design-web-researcher agent to verify modern patterns for:
      - - POST /auth/login
   - - Validate credentials

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
   python .claude/scripts/get_tasks.py auth-test 3 --mode complete
   ```

## Task Details
- - POST /auth/login
- - Validate credentials

## Dependencies
This task depends on: 2

## Context Engineering
- Loads only task-specific context
- Uses ~3,000 tokens instead of ~15,000
- Automated completion tracking

## Usage
```
/auth-test-task-3
```
