#!/usr/bin/env python3
"""
Enhanced workflow automation with parallel execution and comprehensive logging
"""

import asyncio
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class Phase(Enum):
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    TASKS = "tasks"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    REVIEW = "review"
    COMPLETION = "completion"

@dataclass
class Task:
    id: str
    name: str
    command: str
    agent: str
    dependencies: List[str]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class WorkflowState:
    feature: str
    description: str
    current_phase: Phase
    tasks: List[Task]
    completed_phases: List[Phase]
    logs: Dict[str, str]
    start_time: datetime
    end_time: Optional[datetime] = None

class WorkflowOrchestrator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.claude_dir = project_root / '.claude'
        self.workflow_dir = self.claude_dir / 'workflow'
        self.logs_dir = self.claude_dir / 'logs'
        self.state_file = self.workflow_dir / 'state.json'
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure comprehensive logging"""
        log_file = self.logs_dir / 'workflow' / f'workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def save_state(self, state: WorkflowState):
        """Save workflow state to disk"""
        state_dict = {
            'feature': state.feature,
            'description': state.description,
            'current_phase': state.current_phase.value,
            'completed_phases': [p.value for p in state.completed_phases],
            'tasks': [
                {
                    'id': t.id,
                    'name': t.name,
                    'command': t.command,
                    'agent': t.agent,
                    'dependencies': t.dependencies,
                    'status': t.status.value,
                    'result': t.result,
                    'error': t.error,
                    'start_time': t.start_time.isoformat() if t.start_time else None,
                    'end_time': t.end_time.isoformat() if t.end_time else None
                }
                for t in state.tasks
            ],
            'logs': state.logs,
            'start_time': state.start_time.isoformat(),
            'end_time': state.end_time.isoformat() if state.end_time else None
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state_dict, f, indent=2)
            
    def load_state(self) -> Optional[WorkflowState]:
        """Load workflow state from disk"""
        if not self.state_file.exists():
            return None
            
        with open(self.state_file) as f:
            data = json.load(f)
            
        tasks = []
        for task_data in data['tasks']:
            task = Task(
                id=task_data['id'],
                name=task_data['name'],
                command=task_data['command'],
                agent=task_data['agent'],
                dependencies=task_data['dependencies'],
                status=TaskStatus(task_data['status']),
                result=task_data.get('result'),
                error=task_data.get('error'),
                start_time=datetime.fromisoformat(task_data['start_time']) if task_data.get('start_time') else None,
                end_time=datetime.fromisoformat(task_data['end_time']) if task_data.get('end_time') else None
            )
            tasks.append(task)
            
        return WorkflowState(
            feature=data['feature'],
            description=data['description'],
            current_phase=Phase(data['current_phase']),
            tasks=tasks,
            completed_phases=[Phase(p) for p in data['completed_phases']],
            logs=data['logs'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None
        )
        
    async def execute_command(self, command: str, agent: str = None) -> Tuple[bool, str]:
        """Execute a Claude Code command"""
        self.logger.info(f"Executing: {command}")
        
        try:
            # For now, simulate command execution
            # In real implementation, this would call Claude Code
            await asyncio.sleep(1)  # Simulate work
            result = f"Completed: {command}"
            self.logger.info(result)
            return True, result
        except Exception as e:
            error = f"Failed: {command} - {str(e)}"
            self.logger.error(error)
            return False, error
            
    async def execute_task(self, task: Task, state: WorkflowState):
        """Execute a single task"""
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = datetime.now()
        self.save_state(state)
        
        success, result = await self.execute_command(task.command, task.agent)
        
        task.end_time = datetime.now()
        if success:
            task.status = TaskStatus.COMPLETED
            task.result = result
        else:
            task.status = TaskStatus.FAILED
            task.error = result
            
        self.save_state(state)
        
    async def execute_parallel_tasks(self, tasks: List[Task], state: WorkflowState):
        """Execute multiple tasks in parallel"""
        # Group tasks by dependencies
        task_groups = self.group_tasks_by_dependencies(tasks)
        
        for group in task_groups:
            # Execute tasks in group parallel
            await asyncio.gather(*[
                self.execute_task(task, state)
                for task in group
            ])
            
    def group_tasks_by_dependencies(self, tasks: List[Task]) -> List[List[Task]]:
        """Group tasks that can be executed in parallel"""
        groups = []
        remaining = tasks.copy()
        completed_ids = set()
        
        while remaining:
            # Find tasks with satisfied dependencies
            ready = []
            for task in remaining:
                if all(dep in completed_ids for dep in task.dependencies):
                    ready.append(task)
                    
            if not ready:
                # Circular dependency or error
                self.logger.error("Circular dependency detected")
                break
                
            groups.append(ready)
            
            # Mark as completed for dependency purposes
            for task in ready:
                completed_ids.add(task.id)
                remaining.remove(task)
                
        return groups
        
    async def run_phase(self, phase: Phase, state: WorkflowState):
        """Execute a workflow phase"""
        self.logger.info(f"Starting phase: {phase.value}")
        state.current_phase = phase
        self.save_state(state)
        
        # Phase-specific logic
        if phase == Phase.INITIALIZATION:
            await self.phase_initialization(state)
        elif phase == Phase.PLANNING:
            await self.phase_planning(state)
        elif phase == Phase.REQUIREMENTS:
            await self.phase_requirements(state)
        elif phase == Phase.DESIGN:
            await self.phase_design(state)
        elif phase == Phase.TASKS:
            await self.phase_tasks(state)
        elif phase == Phase.IMPLEMENTATION:
            await self.phase_implementation(state)
        elif phase == Phase.TESTING:
            await self.phase_testing(state)
        elif phase == Phase.REVIEW:
            await self.phase_review(state)
        elif phase == Phase.COMPLETION:
            await self.phase_completion(state)
            
        state.completed_phases.append(phase)
        self.save_state(state)
        
    async def phase_initialization(self, state: WorkflowState):
        """Initialize the workflow"""
        tasks = [
            Task(
                id="init-1",
                name="Check steering context",
                command="/steering-setup",
                agent="steering-context-manager",
                dependencies=[]
            ),
            Task(
                id="init-2",
                name="Initialize logging",
                command=f"python {self.claude_dir}/scripts/log_manager.py create --type session --title workflow-{state.feature}",
                agent="system",
                dependencies=[]
            ),
            Task(
                id="init-3",
                name="Analyze codebase",
                command="Analyze project structure and patterns",
                agent="architect",
                dependencies=[]
            )
        ]
        
        await self.execute_parallel_tasks(tasks, state)
        
    async def phase_planning(self, state: WorkflowState):
        """Planning phase"""
        task = Task(
            id="plan-1",
            name="Create feature specification",
            command=f'/spec-create "{state.feature}" "{state.description}"',
            agent="product-manager",
            dependencies=[]
        )
        
        await self.execute_task(task, state)
        
    async def phase_requirements(self, state: WorkflowState):
        """Requirements gathering phase"""
        task = Task(
            id="req-1",
            name="Generate requirements",
            command="/spec-requirements",
            agent="business-analyst",
            dependencies=[]
        )
        
        await self.execute_task(task, state)
        
    async def phase_design(self, state: WorkflowState):
        """Design phase - parallel UI/UX and architecture"""
        tasks = [
            Task(
                id="design-1",
                name="UI/UX Design",
                command="/spec-design uiux",
                agent="uiux-designer",
                dependencies=[]
            ),
            Task(
                id="design-2",
                name="Technical Architecture",
                command="/spec-design architecture",
                agent="architect",
                dependencies=[]
            )
        ]
        
        await self.execute_parallel_tasks(tasks, state)
        
    async def phase_tasks(self, state: WorkflowState):
        """Task generation and validation phase"""
        tasks = [
            Task(
                id="tasks-1",
                name="Generate implementation tasks",
                command="/spec-tasks",
                agent="spec-task-validator",
                dependencies=[]
            ),
            Task(
                id="tasks-2",
                name="Validate task atomicity",
                command="Validate generated tasks",
                agent="spec-task-validator",
                dependencies=["tasks-1"]
            )
        ]
        
        await self.execute_parallel_tasks(tasks, state)
        
    async def phase_implementation(self, state: WorkflowState):
        """Implementation phase - execute generated tasks"""
        # In real implementation, this would read tasks from spec
        # and execute them in parallel based on dependencies
        self.logger.info("Executing implementation tasks in parallel...")
        
        # Simulate parallel task execution
        implementation_tasks = [
            Task(
                id=f"impl-{i}",
                name=f"Implementation task {i}",
                command=f"/{state.feature}-task-{i}",
                agent="developer",
                dependencies=[] if i == 1 else [f"impl-{i-1}"]
            )
            for i in range(1, 4)
        ]
        
        await self.execute_parallel_tasks(implementation_tasks, state)
        
    async def phase_testing(self, state: WorkflowState):
        """Testing phase"""
        tasks = [
            Task(
                id="test-1",
                name="Unit tests",
                command="Run unit tests",
                agent="qa-engineer",
                dependencies=[]
            ),
            Task(
                id="test-2",
                name="Integration tests",
                command="Run integration tests",
                agent="qa-engineer",
                dependencies=[]
            ),
            Task(
                id="test-3",
                name="Security scan",
                command="Run security analysis",
                agent="security-engineer",
                dependencies=[]
            )
        ]
        
        await self.execute_parallel_tasks(tasks, state)
        
    async def phase_review(self, state: WorkflowState):
        """Code review phase"""
        task = Task(
            id="review-1",
            name="Code review",
            command="/spec-review 1",
            agent="code-reviewer",
            dependencies=[]
        )
        
        await self.execute_task(task, state)
        
    async def phase_completion(self, state: WorkflowState):
        """Completion phase"""
        tasks = [
            Task(
                id="complete-1",
                name="Generate final report",
                command=f"Generate completion report for {state.feature}",
                agent="product-manager",
                dependencies=[]
            ),
            Task(
                id="complete-2",
                name="Archive logs",
                command=f"python {self.claude_dir}/scripts/log_manager.py archive",
                agent="system",
                dependencies=[]
            )
        ]
        
        await self.execute_parallel_tasks(tasks, state)
        
    async def orchestrate(self, feature: str, description: str):
        """Main orchestration method"""
        # Check for existing state
        state = self.load_state()
        
        if state:
            self.logger.info(f"Resuming workflow from phase: {state.current_phase.value}")
            start_phase_index = list(Phase).index(state.current_phase)
        else:
            # New workflow
            state = WorkflowState(
                feature=feature,
                description=description,
                current_phase=Phase.INITIALIZATION,
                tasks=[],
                completed_phases=[],
                logs={},
                start_time=datetime.now()
            )
            start_phase_index = 0
            
        # Execute phases
        phases = list(Phase)
        for phase in phases[start_phase_index:]:
            if phase not in state.completed_phases:
                await self.run_phase(phase, state)
                
        # Mark completion
        state.end_time = datetime.now()
        self.save_state(state)
        
        # Generate summary
        duration = state.end_time - state.start_time
        self.logger.info(f"Workflow completed in {duration}")
        self.logger.info(f"Total tasks executed: {len([t for t in state.tasks if t.status == TaskStatus.COMPLETED])}")
        
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow orchestrator')
    parser.add_argument('feature', help='Feature name')
    parser.add_argument('description', help='Feature description')
    parser.add_argument('--resume', action='store_true', help='Resume from saved state')
    
    args = parser.parse_args()
    
    orchestrator = WorkflowOrchestrator(Path.cwd())
    asyncio.run(orchestrator.orchestrate(args.feature, args.description))
    
if __name__ == "__main__":
    main()