# Phase 2.5: Context Engineering Implementation Plan

## Overview
Before proceeding to Phase 3, we need to implement critical Context Engineering features from claude-code-spec-workflow v1.5.x that fundamentally improve how agents work.

## What is Context Engineering?

### The Problem (Current Approach)
```
Agent: "Load requirements.md, design.md, tasks.md, all steering docs..."
Result: 🔴 80% of context window used before starting work
```

### The Solution (Context Engineering)
```
Agent: "Load ONLY task 1.2 details and relevant tech.md section"
Result: ✅ 20% of context window used, room for complex reasoning
```

## Implementation Tasks

### Task 1: Create Context Scripts (1 hour)

#### 1.1 get_content.py
```python
#!/usr/bin/env python3
"""
Efficiently load file contents for agents
Usage: python get_content.py <file-path>
"""

import sys
import os
from pathlib import Path

def get_content(file_path):
    """Load and output file content"""
    try:
        # Normalize path for cross-platform
        path = Path(file_path).resolve()
        
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        # Output content to stdout for agent consumption
        print(path.read_text(encoding='utf-8'))
        
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide a file path", file=sys.stderr)
        print("Usage: get_content.py <file-path>", file=sys.stderr)
        sys.exit(1)
    
    get_content(sys.argv[1])
```

#### 1.2 get_tasks.py
```python
#!/usr/bin/env python3
"""
Task management for specifications
Usage: python get_tasks.py <spec-name> [task-id] --mode <mode>
"""

import sys
import json
import re
from pathlib import Path
import argparse

class TaskManager:
    def __init__(self, spec_name, project_root=None):
        self.spec_name = spec_name
        self.project_root = Path(project_root or Path.cwd())
        self.tasks_file = self.project_root / '.claude' / 'specs' / spec_name / 'tasks.md'
    
    def parse_tasks(self):
        """Parse tasks from markdown"""
        if not self.tasks_file.exists():
            print(f"Error: tasks.md not found at {self.tasks_file}", file=sys.stderr)
            sys.exit(1)
        
        content = self.tasks_file.read_text(encoding='utf-8')
        tasks = []
        
        # Parse task format: - [ ] 1.2. Task description
        pattern = r'^-\s*\[([ x])\]\s*(\d+(?:\.\d+)*)\s*\.?\s*(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            completed = match.group(1).lower() == 'x'
            task_id = match.group(2)
            description = match.group(3).strip()
            
            tasks.append({
                'id': task_id,
                'description': description,
                'completed': completed
            })
        
        return tasks
    
    def get_all_tasks(self):
        """Get all tasks"""
        return self.parse_tasks()
    
    def get_single_task(self, task_id):
        """Get specific task"""
        tasks = self.parse_tasks()
        for task in tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def get_next_pending(self):
        """Get next uncompleted task"""
        tasks = self.parse_tasks()
        for task in tasks:
            if not task['completed']:
                return task
        return None
    
    def mark_complete(self, task_id):
        """Mark task as complete"""
        content = self.tasks_file.read_text(encoding='utf-8')
        
        # Replace - [ ] with - [x] for specific task
        pattern = rf'^(-\s*\[)\s*(\]\s*{re.escape(task_id)}\s*\.?\s*.+)$'
        updated = re.sub(pattern, r'\1x\2', content, flags=re.MULTILINE)
        
        if updated == content:
            print(f"Error: Task {task_id} not found", file=sys.stderr)
            sys.exit(1)
        
        self.tasks_file.write_text(updated, encoding='utf-8')
        print(f"✓ Task {task_id} marked as complete")

def main():
    parser = argparse.ArgumentParser(description='Task management for specs')
    parser.add_argument('spec_name', help='Specification name')
    parser.add_argument('task_id', nargs='?', help='Task ID (optional)')
    parser.add_argument('--mode', choices=['all', 'single', 'next-pending', 'complete'],
                       default='all', help='Operation mode')
    
    args = parser.parse_args()
    
    manager = TaskManager(args.spec_name)
    
    if args.mode == 'all':
        tasks = manager.get_all_tasks()
        print(json.dumps(tasks, indent=2))
    
    elif args.mode == 'single':
        if not args.task_id:
            print("Error: Task ID required for single mode", file=sys.stderr)
            sys.exit(1)
        task = manager.get_single_task(args.task_id)
        if task:
            print(json.dumps(task, indent=2))
        else:
            print(f"Error: Task {args.task_id} not found", file=sys.stderr)
            sys.exit(1)
    
    elif args.mode == 'next-pending':
        task = manager.get_next_pending()
        if task:
            print(json.dumps(task, indent=2))
        else:
            print("No pending tasks found")
    
    elif args.mode == 'complete':
        if not args.task_id:
            print("Error: Task ID required for complete mode", file=sys.stderr)
            sys.exit(1)
        manager.mark_complete(args.task_id)

if __name__ == "__main__":
    main()
```

#### 1.3 check_agents.py
```python
#!/usr/bin/env python3
"""
Check if agents are enabled
Usage: python check_agents.py
"""

import json
from pathlib import Path

def check_agents_enabled():
    """Check if agents are enabled in spec-config.json"""
    config_path = Path.cwd() / '.claude' / 'spec-config.json'
    
    if not config_path.exists():
        print("false")
        return
    
    try:
        config = json.loads(config_path.read_text())
        enabled = config.get('spec_workflow', {}).get('agents_enabled', False)
        print("true" if enabled else "false")
    except:
        print("false")

if __name__ == "__main__":
    check_agents_enabled()
```

### Task 2: Add Web Research Agent (30 min)

Copy spec-design-web-researcher.md to our agents directory with description:
"Design research specialist. Use PROACTIVELY during design phase to search for latest framework documentation, API changes, and best practices."

### Task 3: Update Commands (1 hour)

Update all commands to use context scripts:

#### Example Update for spec-create.md:
```markdown
# OLD:
Load .claude/steering/product.md

# NEW:
Load steering documents using the get-content script:

**Cross-platform examples:**
```bash
# Windows:
python .claude\scripts\get_content.py .claude\steering\product.md

# macOS/Linux:
python .claude/scripts/get_content.py .claude/steering/product.md
```
```

### Task 4: Update Orchestration (30 min)

Add implementation review step and automated completion:
```markdown
**Step 4 - Implementation Review:**
After task completion, review the implementation...

**Step 5 - Mark Complete:**
```bash
python .claude/scripts/get_tasks.py {spec-name} {task-id} --mode complete
```
```

## Benefits After Implementation

### Before (Current):
- Agent loads 5-10 files completely
- Uses 15,000+ tokens before starting
- Manual task editing prone to errors
- Platform-specific paths

### After (With Context Engineering):
- Agent loads only needed sections
- Uses 3,000-5,000 tokens
- Automated task management
- Cross-platform compatibility

## Testing Plan

1. Create test specification
2. Measure token usage before/after
3. Verify cross-platform scripts
4. Test task automation
5. Validate web researcher catches outdated patterns

## Success Metrics

- [ ] 50%+ reduction in context usage
- [ ] Zero manual tasks.md edits
- [ ] Works on Windows/Mac/Linux
- [ ] Catches at least one outdated pattern

## Timeline

- Implementation: 2-3 hours
- Testing: 1 hour
- Documentation: 30 minutes

Total: ~4 hours for complete implementation

## Next Steps After Phase 2.5

With Context Engineering in place:
1. Phase 3 (Automation) becomes much more efficient
2. Phase 4 (TMUX) can handle larger projects
3. System scales to enterprise-level codebases

---

Ready to implement Phase 2.5? This foundation will make everything else work better.
