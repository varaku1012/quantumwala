#!/usr/bin/env python3
"""
Planning command executor - analyzes tasks and creates parallel execution plans
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from enum import Enum

class PlanningPhase(Enum):
    ANALYSIS = "analysis"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"

@dataclass
class Task:
    id: str
    description: str
    agent: str
    dependencies: List[str]
    command: str = ""

@dataclass
class ExecutionBatch:
    batch_number: int
    tasks: List[Task]
    can_parallel: bool

class PlanningExecutor:
    def __init__(self, phase: str, spec_name: str):
        self.phase = PlanningPhase(phase.lower())
        self.spec_name = spec_name
        self.project_root = self._find_project_root()
        self.spec_dir = self.project_root / '.claude' / 'specs' / spec_name
        
    def _find_project_root(self):
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def plan_analysis(self) -> str:
        """Plan parallel analysis tasks"""
        agents = [
            ("business-analyst", "Detailed requirements and user stories"),
            ("architect", "Technical feasibility and system design"),
            ("uiux-designer", "UI/UX wireframes and user flows"),
            ("security-engineer", "Security implications and threat model"),
            ("data-engineer", "Data requirements and pipeline needs"),
        ]
        
        output = "## Parallel Analysis Plan\n\n"
        output += "### Batch 1 (Can run simultaneously):\n"
        
        for agent, description in agents:
            output += f"- **{agent}**: {description}\n"
            output += f"  - Command: `Use {agent} agent to analyze {self.spec_name}`\n"
        
        output += "\n### Coordination:\n"
        output += "After all analysis complete, synthesize findings into unified requirements.\n"
        
        return output
    
    def plan_design(self) -> str:
        """Plan parallel design tasks"""
        # Load requirements to understand what needs design
        req_file = self.spec_dir / 'requirements.md'
        has_ui = False
        has_api = False
        has_data = False
        
        if req_file.exists():
            content = req_file.read_text()
            has_ui = 'interface' in content.lower() or 'ui' in content.lower()
            has_api = 'api' in content.lower() or 'endpoint' in content.lower()
            has_data = 'database' in content.lower() or 'data' in content.lower()
        
        output = "## Parallel Design Plan\n\n"
        output += "### Batch 1 (Can run simultaneously):\n"
        
        if has_ui:
            output += "- **uiux-designer**: Frontend component design\n"
            output += "  - Command: `/spec-design uiux`\n"
        
        output += "- **architect**: Backend architecture and API design\n"
        output += "  - Command: `/spec-design architecture`\n"
        
        if has_data:
            output += "- **data-engineer**: Data model and pipeline design\n"
            output += "  - Command: `Use data-engineer agent for data design`\n"
        
        output += "- **security-engineer**: Security architecture\n"
        output += "  - Command: `Use security-engineer agent for security design`\n"
        
        if has_api:
            output += "\n### Batch 2 (After architecture):\n"
            output += "- **developer**: API specification and contracts\n"
            output += "  - Command: `Create OpenAPI specification`\n"
        
        return output
    
    def parse_tasks_file(self) -> List[Task]:
        """Parse tasks from tasks.md file"""
        tasks_file = self.spec_dir / 'tasks.md'
        if not tasks_file.exists():
            return []
        
        tasks = []
        current_section = None
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Section headers
                if line.startswith('### '):
                    current_section = line.strip('# \n')
                
                # Task items
                if line.strip().startswith('- [ ] '):
                    # Extract task ID and description
                    match = re.match(r'- \[ \] (\d+\.?\d*)\.\s+(.+)', line.strip())
                    if match:
                        task_id = match.group(1)
                        description = match.group(2)
                        
                        # Determine agent based on task type
                        agent = self._determine_agent(description, current_section)
                        
                        # Determine dependencies based on ID
                        deps = self._determine_dependencies(task_id, tasks)
                        
                        # Create command
                        command = f"/{self.spec_name}-task-{task_id.replace('.', '-')}"
                        
                        tasks.append(Task(
                            id=task_id,
                            description=description,
                            agent=agent,
                            dependencies=deps,
                            command=command
                        ))
        
        return tasks
    
    def _determine_agent(self, description: str, section: str) -> str:
        """Determine which agent should handle a task"""
        desc_lower = description.lower()
        
        # Keywords for different agents
        if any(word in desc_lower for word in ['model', 'schema', 'database', 'table']):
            return 'developer'
        elif any(word in desc_lower for word in ['api', 'endpoint', 'service', 'controller']):
            return 'developer'
        elif any(word in desc_lower for word in ['ui', 'component', 'screen', 'page', 'frontend']):
            return 'developer'
        elif any(word in desc_lower for word in ['test', 'testing', 'spec']):
            return 'qa-engineer'
        elif any(word in desc_lower for word in ['auth', 'security', 'permission']):
            return 'security-engineer'
        elif any(word in desc_lower for word in ['pipeline', 'etl', 'data flow']):
            return 'data-engineer'
        elif any(word in desc_lower for word in ['deploy', 'ci/cd', 'infrastructure']):
            return 'devops-engineer'
        else:
            return 'developer'  # Default
    
    def _determine_dependencies(self, task_id: str, existing_tasks: List[Task]) -> List[str]:
        """Determine task dependencies based on ID hierarchy"""
        deps = []
        
        # If it's a subtask (e.g., 1.2), it depends on parent (1.1)
        if '.' in task_id:
            parent_base = task_id.split('.')[0]
            parent_num = int(task_id.split('.')[1])
            
            # Depends on previous subtask if exists
            if parent_num > 1:
                prev_id = f"{parent_base}.{parent_num - 1}"
                if any(t.id == prev_id for t in existing_tasks):
                    deps.append(prev_id)
        else:
            # Top-level tasks depend on previous top-level
            task_num = int(task_id)
            if task_num > 1:
                prev_id = str(task_num - 1)
                # Only add if no subtasks exist for previous
                if any(t.id == prev_id for t in existing_tasks):
                    deps.append(prev_id)
        
        return deps
    
    def create_execution_batches(self, tasks: List[Task]) -> List[ExecutionBatch]:
        """Group tasks into execution batches based on dependencies"""
        batches = []
        completed: Set[str] = set()
        remaining = tasks.copy()
        batch_num = 1
        
        while remaining:
            # Find tasks that can be executed (dependencies satisfied)
            ready = []
            for task in remaining:
                if all(dep in completed for dep in task.dependencies):
                    ready.append(task)
            
            if not ready:
                # Circular dependency or error
                print(f"Warning: Cannot resolve dependencies for {len(remaining)} tasks")
                break
            
            # Group by whether they can run in parallel
            # Tasks with no dependencies on each other can run in parallel
            batch_tasks = []
            task_ids = [t.id for t in ready]
            
            for task in ready:
                # Check if this task is a dependency for any other ready task
                is_dependency = any(
                    task.id in other.dependencies 
                    for other in ready 
                    if other.id != task.id
                )
                
                if not is_dependency:
                    batch_tasks.append(task)
            
            # If no parallel tasks found, just take the first ready task
            if not batch_tasks:
                batch_tasks = [ready[0]]
            
            can_parallel = len(batch_tasks) > 1
            
            batches.append(ExecutionBatch(
                batch_number=batch_num,
                tasks=batch_tasks,
                can_parallel=can_parallel
            ))
            
            # Mark as completed and remove from remaining
            for task in batch_tasks:
                completed.add(task.id)
                remaining.remove(task)
            
            batch_num += 1
        
        return batches
    
    def plan_implementation(self) -> str:
        """Plan implementation task execution"""
        tasks = self.parse_tasks_file()
        
        if not tasks:
            return "## No tasks found\n\nPlease generate tasks first using `/spec-tasks`"
        
        batches = self.create_execution_batches(tasks)
        
        output = f"## Implementation Execution Plan\n\n"
        output += f"Total tasks: {len(tasks)}\n"
        output += f"Execution batches: {len(batches)}\n\n"
        
        for batch in batches:
            if batch.can_parallel:
                output += f"### Batch {batch.batch_number} (Can run simultaneously):\n"
            else:
                output += f"### Batch {batch.batch_number} (Sequential):\n"
            
            for task in batch.tasks:
                output += f"- **Task {task.id}**: {task.description}\n"
                output += f"  - Agent: `{task.agent}`\n"
                output += f"  - Command: `{task.command}`\n"
                if task.dependencies:
                    output += f"  - Dependencies: {', '.join(task.dependencies)}\n"
            output += "\n"
        
        # Add execution summary
        output += "### Execution Strategy:\n"
        parallel_count = sum(1 for b in batches if b.can_parallel)
        if parallel_count > 0:
            output += f"- {parallel_count} batches can run in parallel\n"
            time_saved = sum(len(b.tasks) - 1 for b in batches if b.can_parallel)
            output += f"- Estimated time savings: {time_saved} task durations\n"
        else:
            output += "- All tasks must run sequentially\n"
        
        return output
    
    def plan_testing(self) -> str:
        """Plan parallel testing tasks"""
        output = "## Parallel Testing Plan\n\n"
        output += "### Batch 1 (Can run simultaneously):\n"
        
        test_types = [
            ("Unit Tests", "qa-engineer", "Create and run unit tests"),
            ("Integration Tests", "qa-engineer", "Create and run integration tests"),
            ("Security Scan", "security-engineer", "Run SAST/DAST security analysis"),
            ("Performance Tests", "architect", "Run load and performance tests"),
        ]
        
        for test_name, agent, description in test_types:
            output += f"- **{test_name}** ({agent}): {description}\n"
            output += f"  - Command: `Use {agent} agent for {test_name.lower()}`\n"
        
        output += "\n### Batch 2 (After all tests):\n"
        output += "- **Test Report**: Consolidate all test results\n"
        output += "- **Quality Gate**: Verify all tests pass before deployment\n"
        
        return output
    
    def execute(self) -> str:
        """Execute planning based on phase"""
        if self.phase == PlanningPhase.ANALYSIS:
            return self.plan_analysis()
        elif self.phase == PlanningPhase.DESIGN:
            return self.plan_design()
        elif self.phase == PlanningPhase.IMPLEMENTATION:
            return self.plan_implementation()
        elif self.phase == PlanningPhase.TESTING:
            return self.plan_testing()
        else:
            return f"Unknown planning phase: {self.phase}"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Planning executor for parallel task coordination')
    parser.add_argument('phase', choices=['analysis', 'design', 'implementation', 'testing'],
                       help='Planning phase')
    parser.add_argument('spec_name', help='Specification name')
    parser.add_argument('--output', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    planner = PlanningExecutor(args.phase, args.spec_name)
    result = planner.execute()
    
    if args.output == 'text':
        print(result)
    else:
        # JSON output for programmatic use
        if args.phase == 'implementation':
            tasks = planner.parse_tasks_file()
            batches = planner.create_execution_batches(tasks)
            
            json_output = {
                'phase': args.phase,
                'spec_name': args.spec_name,
                'total_tasks': len(tasks),
                'batches': []
            }
            
            for batch in batches:
                json_output['batches'].append({
                    'batch_number': batch.batch_number,
                    'can_parallel': batch.can_parallel,
                    'tasks': [
                        {
                            'id': task.id,
                            'description': task.description,
                            'agent': task.agent,
                            'command': task.command,
                            'dependencies': task.dependencies
                        }
                        for task in batch.tasks
                    ]
                })
            
            print(json.dumps(json_output, indent=2))

if __name__ == "__main__":
    main()