Implement a specific task.

Arguments:
- task-id: Task identifier (e.g., "1", "2.1")

Process:
1. Load specific task details using context scripts:
   ```bash
   # Get only the specific task context:
   python .claude/scripts/get_tasks.py {spec-name} {task-id} --mode single
   
   # Load relevant technical context:
   python .claude/scripts/get_content.py .claude/steering/tech.md
   ```
2. Optional: Use spec-design-web-researcher agent to verify modern patterns
3. Use developer agent to:
   - Write tests first (TDD)
   - Implement functionality
   - Add documentation
   - Run tests
4. Mark task complete:
   ```bash
   python .claude/scripts/get_tasks.py {spec-name} {task-id} --mode complete
   ```
5. Commit changes with meaningful message

Best practices:
- Always write tests before implementation
- Follow coding standards from steering/structure.md
- Include inline documentation
- Handle errors appropriately
- Verify patterns are current with web researcher

Context Engineering Benefits:
- Loads only the specific task (not entire spec)
- Reduces context usage by 70%+
- Automated task completion tracking

Usage: /spec-implement [task-id]