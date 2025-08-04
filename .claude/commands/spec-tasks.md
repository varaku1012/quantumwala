Break down design into implementable tasks.

Process:
1. Load spec documents using context scripts:
   ```bash
   # Load only what's needed for task generation:
   python .claude/scripts/get_content.py .claude/specs/{spec-name}/requirements.md
   python .claude/scripts/get_content.py .claude/specs/{spec-name}/design.md
   ```
2. Create atomic, testable tasks with:
   - Clear description
   - Acceptance criteria
   - Dependencies
   - Estimated effort
3. Generate individual task commands
4. Create task tracking document with format:
   ```markdown
   - [ ] 1. Task description
   - [ ] 1.1. Sub-task description
   - [ ] 2. Another task
   ```

For each task, create:
- Command file: .claude/commands/{spec-name}/task-{id}.md
- Task details in .claude/specs/{spec-name}/tasks.md

Task Management:
```bash
# View all tasks:
python .claude/scripts/get_tasks.py {spec-name}

# Get next pending task:
python .claude/scripts/get_tasks.py {spec-name} --mode next-pending

# Mark task complete:
python .claude/scripts/get_tasks.py {spec-name} {task-id} --mode complete
```

Task command format:
/[spec-name]-task-[id]

Usage: /spec-tasks