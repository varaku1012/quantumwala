#!/usr/bin/env python3
"""
Task orchestration for parallel and sequential execution with real Claude Code integration
"""

import os
import json
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from real_executor import RealClaudeExecutor, ExecutionResult
    from resource_manager import ResourceManager, ResourceRequirements, ResourceContext
    from unified_state import UnifiedStateManager, TaskStatus
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

class EnhancedTaskOrchestrator:
    def __init__(self, spec_name):
        self.spec_name = spec_name
        self.project_root = self._find_project_root()
        self.spec_dir = self.project_root / '.claude' / 'specs' / spec_name
        self.tasks_file = self.spec_dir / 'tasks.md'
        self.log_file = self.project_root / '.claude' / 'logs' / 'sessions' / f'{spec_name}_execution.log'
        
        # Initialize core components
        self.executor = RealClaudeExecutor(self.project_root)
        self.resource_manager = ResourceManager(self.project_root)
        self.state_manager = UnifiedStateManager()
        
        # Execution settings
        self.max_concurrent_tasks = 6
        self.enable_real_execution = True
        
    def _find_project_root(self):
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def parse_tasks(self):
        """Parse tasks from markdown file"""
        if not self.tasks_file.exists():
            return []
        
        tasks = []
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('- [ ]'):
                    # Extract task ID and description
                    parts = line.strip()[6:].split('.', 1)
                    if len(parts) == 2:
                        task_id = parts[0].strip()
                        description = parts[1].strip()
                        # Check for sub-task
                        is_subtask = '.' in task_id
                        parent_id = task_id.split('.')[0] if is_subtask else None
                        
                        tasks.append({
                            'id': task_id,
                            'description': description,
                            'status': 'pending',
                            'is_subtask': is_subtask,
                            'parent_id': parent_id,
                            'command': f'/{self.spec_name}-task-{task_id.replace(".", "-")}'
                        })
        
        return tasks
    
    def identify_dependencies(self, tasks):
        """Identify task dependencies"""
        # Group tasks by dependency
        task_groups = []
        current_group = []
        
        for task in tasks:
            if task['is_subtask']:
                # Subtasks depend on parent
                if current_group and current_group[-1]['id'] == task['parent_id']:
                    current_group.append(task)
                else:
                    if current_group:
                        task_groups.append(current_group)
                    current_group = [task]
            else:
                # New parent task starts new group
                if current_group:
                    task_groups.append(current_group)
                current_group = [task]
        
        if current_group:
            task_groups.append(current_group)
        
        return task_groups
    
    def can_run_parallel(self, task_group):
        """Check if tasks in group can run in parallel"""
        # Tasks at same level with no interdependencies can run parallel
        if len(task_group) <= 1:
            return False
        
        # Check if all tasks are at same level (no subtasks)
        parent_ids = set(task.get('parent_id') for task in task_group)
        if None not in parent_ids:
            # All are subtasks of same parent - can parallelize
            return len(parent_ids) == 1
        
        # Top-level independent tasks can parallelize
        return all(not task['is_subtask'] for task in task_group)
    
    async def execute_task_real(self, task: Dict) -> ExecutionResult:
        """Execute a single task with real Claude Code integration"""
        task_id = task['id']
        description = task['description']
        agent = task.get('agent', 'developer')
        
        self.log(f"Starting task {task_id}: {description}")
        
        # Update task status to in_progress
        self.state_manager.update_task_status(
            self.spec_name, task_id, TaskStatus.IN_PROGRESS
        )
        
        try:
            # Estimate resource requirements
            requirements = self._estimate_task_requirements(task)
            
            # Acquire resources
            async with ResourceContext(self.resource_manager, task_id, agent, requirements):
                
                # Load minimal context for task
                context = await self._load_task_context(task)
                
                # Construct agent command
                agent_command = f"Use {agent} agent to implement task {task_id}: {description}"
                
                # Execute with real Claude Code
                if self.enable_real_execution:
                    result = await self.executor.execute_agent_task(
                        agent_name=agent,
                        task_description=f"Task {task_id}: {description}",
                        context=context,
                        timeout=600
                    )
                else:
                    # Fallback simulation mode
                    result = ExecutionResult(
                        success=True,
                        output=f"Simulated execution of task {task_id}",
                        duration=2.0,
                        command=agent_command,
                        agent_used=agent
                    )
                
                # Update task status based on result  
                if result.success:
                    self.state_manager.update_task_status(
                        self.spec_name, task_id, TaskStatus.COMPLETED
                    )
                    self.log(f"✅ Completed task {task_id} successfully in {result.duration:.2f}s")
                    
                    # Mark task complete in tasks.md file
                    self._mark_task_complete_in_file(task_id)
                    
                else:
                    self.state_manager.update_task_status(
                        self.spec_name, task_id, TaskStatus.FAILED, result.error
                    )
                    self.log(f"❌ Task {task_id} failed: {result.error}")
                
                return result
                
        except Exception as e:
            error_msg = str(e)
            self.log(f"❌ Task {task_id} execution error: {error_msg}")
            
            self.state_manager.update_task_status(
                self.spec_name, task_id, TaskStatus.FAILED, error_msg
            )
            
            return ExecutionResult(
                success=False,
                error=error_msg,
                command=f"Task {task_id}",
                agent_used=agent
            )
    
    def _estimate_task_requirements(self, task: Dict) -> ResourceRequirements:
        """Estimate resource requirements based on task type"""
        description = task['description'].lower()
        
        # Heuristics for resource estimation
        if any(keyword in description for keyword in ['database', 'migration', 'schema']):
            return ResourceRequirements(cpu_percent=30, memory_mb=512, estimated_duration=600)
        elif any(keyword in description for keyword in ['api', 'service', 'endpoint']):
            return ResourceRequirements(cpu_percent=25, memory_mb=256, estimated_duration=450)
        elif any(keyword in description for keyword in ['component', 'ui', 'frontend']):
            return ResourceRequirements(cpu_percent=20, memory_mb=256, estimated_duration=400)
        elif any(keyword in description for keyword in ['test', 'spec', 'testing']):
            return ResourceRequirements(cpu_percent=15, memory_mb=128, estimated_duration=300)
        else:
            return ResourceRequirements(cpu_percent=20, memory_mb=256, estimated_duration=350)
    
    async def _load_task_context(self, task: Dict) -> Dict:
        """Load minimal context needed for task execution"""
        context = {
            'spec_name': self.spec_name,
            'task_id': task['id'],
            'project_root': str(self.project_root),
            'spec_directory': str(self.spec_dir)
        }
        
        # Load requirements if available
        requirements_file = self.spec_dir / 'requirements.md'
        if requirements_file.exists():
            context['requirements'] = requirements_file.read_text(encoding='utf-8')[:2000]  # First 2000 chars
        
        # Load design if available
        design_file = self.spec_dir / 'design.md'
        if design_file.exists():
            context['design'] = design_file.read_text(encoding='utf-8')[:2000]  # First 2000 chars
        
        # Load steering context
        steering_tech = self.project_root / '.claude' / 'steering' / 'tech.md'
        if steering_tech.exists():
            context['tech_standards'] = steering_tech.read_text(encoding='utf-8')[:1000]
        
        steering_structure = self.project_root / '.claude' / 'steering' / 'structure.md'
        if steering_structure.exists():
            context['project_structure'] = steering_structure.read_text(encoding='utf-8')[:1000]
        
        return context
    
    def _mark_task_complete_in_file(self, task_id: str):
        """Mark task as complete in tasks.md file"""
        try:
            content = self.tasks_file.read_text(encoding='utf-8')
            
            # Replace - [ ] with - [x] for specific task
            import re
            pattern = rf'^(-\s*\[)\s*(\]\s*{re.escape(task_id)}\s*\..*?)$'
            updated_content = re.sub(pattern, r'\1x\2', content, flags=re.MULTILINE)
            
            if updated_content != content:
                self.tasks_file.write_text(updated_content, encoding='utf-8')
                self.log(f"Marked task {task_id} as complete in tasks.md")
            
        except Exception as e:
            self.log(f"Error updating tasks.md for task {task_id}: {e}")
    
    def execute_task(self, task):
        """Legacy synchronous wrapper for backward compatibility"""
        return asyncio.run(self.execute_task_real(task))
    
    async def execute_parallel_real(self, tasks: List[Dict]) -> List[ExecutionResult]:
        """Execute tasks in parallel with real Claude Code integration"""
        self.log(f"🚀 Executing {len(tasks)} tasks in parallel")
        
        # Limit concurrent tasks based on resource manager settings
        max_concurrent = min(self.max_concurrent_tasks, len(tasks))
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await self.execute_task_real(task)
        
        # Execute all tasks concurrently
        task_coroutines = [execute_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        successful_tasks = 0
        failed_tasks = 0
        
        for i, result in enumerate(results):
            task = tasks[i]
            if isinstance(result, Exception):
                self.log(f"❌ Task {task['id']} failed with exception: {result}")
                failed_tasks += 1
            elif result.success:
                successful_tasks += 1
            else:
                failed_tasks += 1
        
        self.log(f"✅ Parallel execution complete: {successful_tasks} successful, {failed_tasks} failed")
        return results
    
    def execute_parallel(self, tasks):
        """Legacy synchronous wrapper for parallel execution"""
        return asyncio.run(self.execute_parallel_real(tasks))
    
    def execute_sequential(self, tasks):
        """Execute tasks sequentially"""
        for task in tasks:
            if self.execute_task(task):
                self.mark_complete(task['id'])
    
    def mark_complete(self, task_id):
        """Mark task as complete in tasks.md"""
        if not self.tasks_file.exists():
            return
        
        lines = self.tasks_file.read_text().split('\n')
        for i, line in enumerate(lines):
            if f"- [ ] {task_id}." in line:
                lines[i] = line.replace('- [ ]', '- [x]')
                break
        
        self.tasks_file.write_text('\n'.join(lines))
    
    def log(self, message):
        """Log execution progress"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
        
        print(log_message.strip())
    
    def orchestrate(self):
        """Main orchestration logic"""
        self.log(f"Starting task orchestration for {self.spec_name}")
        
        # Parse all tasks
        tasks = self.parse_tasks()
        if not tasks:
            self.log("No tasks found")
            return
        
        self.log(f"Found {len(tasks)} tasks")
        
        # Group by dependencies
        task_groups = self.identify_dependencies(tasks)
        
        # Execute each group
        for i, group in enumerate(task_groups):
            self.log(f"Processing group {i+1}/{len(task_groups)}")
            
            if self.can_run_parallel(group):
                self.execute_parallel(group)
            else:
                self.execute_sequential(group)
        
        self.log("Task orchestration complete")
    
    async def orchestrate_real(self):
        """Main orchestration logic with real execution"""
        self.log(f"🚀 Starting enhanced task orchestration for {self.spec_name}")
        
        # Ensure specification exists in state manager
        if not self.state_manager.get_specification(self.spec_name):
            self.state_manager.create_specification(self.spec_name, f"Specification for {self.spec_name}")
        
        # Parse all tasks
        tasks = self.parse_tasks()
        if not tasks:
            self.log("❌ No tasks found")
            return False
        
        self.log(f"📋 Found {len(tasks)} tasks")
        
        # Add all tasks to state manager
        for task in tasks:
            self.state_manager.add_task(
                self.spec_name, 
                task['id'], 
                task['description'], 
                task.get('agent', 'developer')
            )
        
        # Group by dependencies
        task_groups = self.identify_dependencies(tasks)
        
        # Execute each group
        total_successful = 0
        total_failed = 0
        
        for i, group in enumerate(task_groups):
            self.log(f"🔄 Processing group {i+1}/{len(task_groups)} ({len(group)} tasks)")
            
            if self.can_run_parallel(group):
                results = await self.execute_parallel_real(group)
            else:
                results = []
                for task in group:
                    result = await self.execute_task_real(task)
                    results.append(result)
            
            # Count results
            group_successful = sum(1 for r in results if isinstance(r, ExecutionResult) and r.success)
            group_failed = len(results) - group_successful
            
            total_successful += group_successful
            total_failed += group_failed
            
            self.log(f"✅ Group {i+1} complete: {group_successful} successful, {group_failed} failed")
        
        # Final summary
        success_rate = (total_successful / (total_successful + total_failed)) * 100 if (total_successful + total_failed) > 0 else 0
        
        self.log(f"🎯 Task orchestration completed for {self.spec_name}")
        self.log(f"📊 Final results: {total_successful} successful, {total_failed} failed ({success_rate:.1f}% success rate)")
        
        # Update workflow phase if all tasks completed successfully
        if total_failed == 0:
            self.state_manager.update_workflow_phase('implementation', self.spec_name)
            self.log(f"🎉 All tasks completed successfully! Updated phase to 'implementation'")
        
        return total_failed == 0

# Backward compatibility alias
TaskOrchestrator = EnhancedTaskOrchestrator

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Enhanced Task Orchestrator with Real Execution')
    parser.add_argument('spec_name', help='Specification name')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel execution')
    parser.add_argument('--real', action='store_true', default=True, help='Use real Claude Code execution')
    parser.add_argument('--simulate', action='store_true', help='Use simulation mode')
    parser.add_argument('--max-concurrent', type=int, default=6, help='Maximum concurrent tasks')
    
    args = parser.parse_args()
    
    orchestrator = EnhancedTaskOrchestrator(args.spec_name)
    
    # Configure execution mode
    orchestrator.enable_real_execution = args.real and not args.simulate
    orchestrator.max_concurrent_tasks = args.max_concurrent
    
    if args.real and not args.simulate:
        print(f"🚀 Starting REAL execution for {args.spec_name}")
        success = asyncio.run(orchestrator.orchestrate_real())
        if success:
            print("✅ All tasks completed successfully!")
        else:
            print("❌ Some tasks failed. Check logs for details.")
            sys.exit(1)
    else:
        print(f"🎭 Starting simulation mode for {args.spec_name}")
        orchestrator.orchestrate()

if __name__ == '__main__':
    main()