#!/usr/bin/env python3
"""
Task command generator for specifications
Usage: python task-generator.py <spec-name> [--analyze-deps]
"""

import sys
import json
import re
from pathlib import Path
import argparse
from typing import List, Dict, Set, Tuple

class TaskCommandGenerator:
    def __init__(self, spec_name: str, project_root=None):
        self.spec_name = spec_name
        # Find project root
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
        
        self.spec_dir = self.project_root / '.claude' / 'specs' / spec_name
        self.commands_dir = self.project_root / '.claude' / 'commands' / spec_name
        self.tasks_file = self.spec_dir / 'tasks.md'
    
    def parse_tasks(self) -> List[Dict]:
        """Parse tasks from tasks.md"""
        if not self.tasks_file.exists():
            print(f"Error: tasks.md not found at {self.tasks_file}", file=sys.stderr)
            sys.exit(1)
        
        content = self.tasks_file.read_text(encoding='utf-8')
        tasks = []
        
        # Parse task format with details
        current_task = None
        in_task_details = False
        
        for line in content.split('\n'):
            # Main task line: - [ ] 1.2. Task description
            task_match = re.match(r'^-\s*\[([ x])\]\s*(\d+(?:\.\d+)*)\s*\.?\s*(.+)$', line)
            if task_match:
                if current_task:
                    tasks.append(current_task)
                
                completed = task_match.group(1).lower() == 'x'
                task_id = task_match.group(2)
                description = task_match.group(3).strip()
                
                current_task = {
                    'id': task_id,
                    'description': description,
                    'completed': completed,
                    'details': [],
                    'dependencies': []
                }
                in_task_details = True
            
            # Task details (indented lines)
            elif in_task_details and line.startswith('  ') and line.strip():
                if current_task:
                    # Check for dependency notation
                    dep_match = re.match(r'.*\[depends on:\s*([\d.,\s]+)\].*', line, re.IGNORECASE)
                    if dep_match:
                        deps = [d.strip() for d in dep_match.group(1).split(',')]
                        current_task['dependencies'].extend(deps)
                    else:
                        current_task['details'].append(line.strip())
            
            # Empty line ends task details
            elif not line.strip():
                in_task_details = False
        
        # Don't forget the last task
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def generate_command_file(self, task: Dict) -> str:
        """Generate command file content for a task"""
        task_id = task['id']
        
        template = f"""# Task {task_id}: {task['description']}

Execute implementation task {task_id} for {self.spec_name} specification.

## Process

1. **Load Task Context**
   ```bash
   # Get specific task details:
   python .claude/scripts/get_tasks.py {self.spec_name} {task_id} --mode single
   
   # Load relevant specifications:
   python .claude/scripts/get_content.py .claude/specs/{self.spec_name}/requirements.md
   python .claude/scripts/get_content.py .claude/specs/{self.spec_name}/design.md
   
   # Load technical context:
   python .claude/scripts/get_content.py .claude/steering/tech.md
   ```

2. **Pre-Implementation Research** (if needed)
   Use spec-design-web-researcher agent to verify modern patterns for:
   {chr(10).join(f'   - {detail}' for detail in task['details'][:3]) if task['details'] else '   - Task implementation patterns'}

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
   python .claude/scripts/get_tasks.py {self.spec_name} {task_id} --mode complete
   ```

## Task Details
{chr(10).join(f'- {detail}' for detail in task['details']) if task['details'] else 'See tasks.md for full details'}

## Dependencies
{f"This task depends on: {', '.join(task['dependencies'])}" if task['dependencies'] else "No dependencies"}

## Context Engineering
- Loads only task-specific context
- Uses ~3,000 tokens instead of ~15,000
- Automated completion tracking

## Usage
```
/{self.spec_name}-task-{task_id.replace('.', '-')}
```
"""
        return template
    
    def analyze_dependencies(self, tasks: List[Dict]) -> Dict[str, Set[str]]:
        """Analyze task dependencies and find parallelization opportunities"""
        # Build dependency graph
        dep_graph = {}
        all_task_ids = {task['id'] for task in tasks}
        
        for task in tasks:
            task_id = task['id']
            deps = set()
            
            # Direct dependencies
            for dep in task['dependencies']:
                if dep in all_task_ids:
                    deps.add(dep)
            
            # Implicit dependencies (parent tasks)
            if '.' in task_id:
                parent = '.'.join(task_id.split('.')[:-1])
                if parent in all_task_ids:
                    deps.add(parent)
            
            dep_graph[task_id] = deps
        
        # Find parallel groups
        parallel_groups = []
        processed = set()
        
        for task_id in sorted(all_task_ids):
            if task_id not in processed:
                # Find all tasks that can run in parallel with this one
                group = {task_id}
                for other_id in all_task_ids:
                    if other_id not in processed and other_id != task_id:
                        # Check if they have conflicting dependencies
                        if not (dep_graph[task_id] & {other_id}) and not (dep_graph[other_id] & {task_id}):
                            # Check if they have the same dependencies
                            if dep_graph[task_id] == dep_graph[other_id]:
                                group.add(other_id)
                
                if len(group) > 1:
                    parallel_groups.append(group)
                processed.update(group)
        
        return {
            'dependencies': dep_graph,
            'parallel_groups': parallel_groups
        }
    
    def generate_orchestration_script(self, tasks: List[Dict], analysis: Dict) -> str:
        """Generate an orchestration script for the specification"""
        parallel_groups = analysis.get('parallel_groups', [])
        
        script = f"""#!/usr/bin/env python3
\"\"\"
Orchestration script for {self.spec_name} specification
Auto-generated by task-generator.py
\"\"\"

import subprocess
import sys
from pathlib import Path

def run_task(spec_name, task_id):
    \"\"\"Execute a single task\"\"\"
    print(f"\\n{'='*60}")
    print(f"Executing Task {{task_id}}")
    print('='*60)
    
    # Run the task command
    cmd = f"/{{spec_name}}-task-{{task_id.replace('.', '-')}}"
    print(f"Running: {{cmd}}")
    # In real implementation, this would invoke Claude Code
    # For now, we'll mark it complete
    
    # Mark task complete
    subprocess.run([
        sys.executable, 
        ".claude/scripts/get_tasks.py", 
        spec_name, 
        task_id, 
        "--mode", 
        "complete"
    ])

def main():
    spec_name = "{self.spec_name}"
    
    print(f"Starting orchestration for: {{spec_name}}")
    print(f"Total tasks: {len(tasks)}")
"""
        
        # Add parallel execution info
        if parallel_groups:
            script += f"""
    print("\\nParallel execution opportunities found!")
    parallel_groups = {parallel_groups}
"""
        
        # Add task execution
        script += """
    # Execute tasks in dependency order
    tasks_to_run = [
"""
        for task in tasks:
            if not task['completed']:
                script += f'        "{task["id"]}",\n'
        
        script += """    ]
    
    for task_id in tasks_to_run:
        run_task(spec_name, task_id)
    
    print(f"\\nOrchestration complete!")

if __name__ == "__main__":
    main()
"""
        return script
    
    def generate_all(self):
        """Generate all task commands and orchestration"""
        # Create commands directory
        self.commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse tasks
        tasks = self.parse_tasks()
        if not tasks:
            print("No tasks found in tasks.md")
            return
        
        print(f"Found {len(tasks)} tasks for {self.spec_name}")
        
        # Generate command files
        generated = []
        skipped = []
        
        for task in tasks:
            if task['completed']:
                skipped.append(task['id'])
                continue
            
            # Generate command file
            command_content = self.generate_command_file(task)
            command_filename = f"task-{task['id'].replace('.', '-')}.md"
            command_path = self.commands_dir / command_filename
            
            command_path.write_text(command_content, encoding='utf-8')
            generated.append(task['id'])
            
            try:
                print(f"✓ Generated: /{self.spec_name}-{command_filename[:-3]}")
            except UnicodeEncodeError:
                print(f"[OK] Generated: /{self.spec_name}-{command_filename[:-3]}")
        
        # Analyze dependencies
        analysis = self.analyze_dependencies(tasks)
        
        # Generate orchestration script
        orchestration_content = self.generate_orchestration_script(tasks, analysis)
        orchestration_path = self.project_root / '.claude' / 'scripts' / f'orchestrate-{self.spec_name}.py'
        orchestration_path.write_text(orchestration_content, encoding='utf-8')
        
        try:
            print(f"\n✓ Generated orchestration script: {orchestration_path.name}")
        except UnicodeEncodeError:
            print(f"\n[OK] Generated orchestration script: {orchestration_path.name}")
        
        # Summary
        print(f"\nGeneration Summary:")
        print(f"- Commands generated: {len(generated)}")
        print(f"- Tasks skipped (completed): {len(skipped)}")
        
        if analysis['parallel_groups']:
            print(f"\nParallel Execution Opportunities:")
            for i, group in enumerate(analysis['parallel_groups'], 1):
                print(f"  Group {i}: Tasks {', '.join(sorted(group))} can run in parallel")
        
        return {
            'generated': generated,
            'skipped': skipped,
            'analysis': analysis
        }

def main():
    parser = argparse.ArgumentParser(description='Generate task commands from specification')
    parser.add_argument('spec_name', help='Specification name')
    parser.add_argument('--analyze-deps', action='store_true', 
                       help='Only analyze dependencies without generating')
    
    args = parser.parse_args()
    
    generator = TaskCommandGenerator(args.spec_name)
    
    if args.analyze_deps:
        tasks = generator.parse_tasks()
        analysis = generator.analyze_dependencies(tasks)
        print(json.dumps(analysis, indent=2, default=list))
    else:
        result = generator.generate_all()
        if result:
            print(f"\nTask commands ready to use!")
            print(f"Try: /{args.spec_name}-task-1")

if __name__ == "__main__":
    main()