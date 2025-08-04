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
        # Find project root by looking for .claude directory
        if project_root:
            self.project_root = Path(project_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.claude').exists():
                    self.project_root = current
                    break
                current = current.parent
            else:
                self.project_root = Path.cwd()
        
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
        try:
            print(f"✓ Task {task_id} marked as complete")
        except UnicodeEncodeError:
            print(f"[DONE] Task {task_id} marked as complete")

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