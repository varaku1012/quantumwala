#!/usr/bin/env python3
"""
Agent Tool Bridge - Connects agent Task tool calls to actual command execution
This bridges the gap between agent tools and command implementations
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from real_executor import RealClaudeExecutor, ExecutionResult
from context_engine import ContextEngine
from memory_manager import MemoryManager
from planning_executor import PlanningExecutor

@dataclass
class TaskRequest:
    """Represents a task delegation from an agent"""
    agent: str
    description: str
    context: Dict[str, Any]
    parent_agent: str
    parallel_group: Optional[str] = None

class AgentToolBridge:
    """
    Bridges agent Task tool calls to actual command/script execution
    This is the KEY integration layer that was missing
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.executor = RealClaudeExecutor(self.project_root)
        self.context_engine = ContextEngine(self.project_root)
        self.memory_manager = MemoryManager(self.project_root)
        
        # Map agent types to their execution strategies
        self.agent_strategies = {
            'business-analyst': self._execute_analyst,
            'architect': self._execute_architect,
            'developer': self._execute_developer,
            'qa-engineer': self._execute_qa,
            'uiux-designer': self._execute_designer,
            'security-engineer': self._execute_security,
            'data-engineer': self._execute_data,
            'code-reviewer': self._execute_reviewer,
            'product-manager': self._execute_product_manager,
            'chief-product-manager': self._execute_chief_pm
        }
        
        # Command mappings for different workflows
        self.command_mappings = {
            'create_spec': 'python .claude/scripts/spec_manager.py create',
            'generate_requirements': 'python .claude/scripts/spec_manager.py requirements',
            'create_design': 'python .claude/scripts/spec_manager.py design',
            'generate_tasks': 'python .claude/scripts/spec_manager.py tasks',
            'plan_execution': 'python .claude/scripts/planning_executor.py',
            'execute_task': 'python .claude/scripts/task_orchestrator.py'
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    async def process_task_delegation(self, task: TaskRequest) -> ExecutionResult:
        """
        Process a Task tool delegation from an agent
        This is called when an agent uses: Task(agent="...", description="...", context={})
        """
        self.logger.info(f"Processing task delegation: {task.agent} - {task.description}")
        
        # 1. Prepare context for target agent
        optimized_context = self.context_engine.prepare_context(
            agent_type=task.agent,
            task={'description': task.description},
            full_context=task.context
        )
        
        # 2. Get relevant memories
        memories = self.memory_manager.get_relevant_memories({
            'description': task.description,
            'agent': task.agent
        })
        
        # 3. Merge context with memories
        enriched_context = {
            **optimized_context,
            'memories': memories,
            'parent_agent': task.parent_agent,
            'parallel_group': task.parallel_group
        }
        
        # 4. Execute using appropriate strategy
        strategy = self.agent_strategies.get(task.agent, self._execute_generic)
        result = await strategy(task.description, enriched_context)
        
        # 5. Store execution in memory
        self.memory_manager.store_execution(
            task_id=f"{task.parent_agent}_{task.agent}_{hash(task.description)}",
            agent=task.agent,
            result=result
        )
        
        return result
    
    async def _execute_analyst(self, description: str, context: Dict) -> ExecutionResult:
        """Execute business analyst tasks"""
        # Check if this is requirements generation
        if 'requirements' in description.lower():
            spec_name = self._extract_spec_name(context)
            command = f"{self.command_mappings['generate_requirements']} {spec_name}"
            return await self.executor.execute_command(command, context)
        
        # Otherwise delegate to actual agent
        return await self.executor.execute_agent_task('business-analyst', description, context)
    
    async def _execute_architect(self, description: str, context: Dict) -> ExecutionResult:
        """Execute architect tasks"""
        # Check if this is design phase
        if 'design' in description.lower() or 'architecture' in description.lower():
            spec_name = self._extract_spec_name(context)
            command = f"{self.command_mappings['create_design']} {spec_name}"
            return await self.executor.execute_command(command, context)
        
        # Check if this is planning
        if 'plan' in description.lower():
            spec_name = self._extract_spec_name(context)
            phase = 'implementation' if 'implementation' in description else 'design'
            command = f"{self.command_mappings['plan_execution']} {phase} {spec_name}"
            return await self.executor.execute_command(command, context)
        
        return await self.executor.execute_agent_task('architect', description, context)
    
    async def _execute_developer(self, description: str, context: Dict) -> ExecutionResult:
        """Execute developer tasks"""
        # Check if this is a specific task implementation
        if 'task' in description.lower() and any(char.isdigit() for char in description):
            # Extract task number and execute
            spec_name = self._extract_spec_name(context)
            task_num = self._extract_task_number(description)
            command = f"{self.command_mappings['execute_task']} {spec_name} {task_num}"
            return await self.executor.execute_command(command, context)
        
        return await self.executor.execute_agent_task('developer', description, context)
    
    async def _execute_qa(self, description: str, context: Dict) -> ExecutionResult:
        """Execute QA engineer tasks"""
        return await self.executor.execute_agent_task('qa-engineer', description, context)
    
    async def _execute_designer(self, description: str, context: Dict) -> ExecutionResult:
        """Execute UI/UX designer tasks"""
        return await self.executor.execute_agent_task('uiux-designer', description, context)
    
    async def _execute_security(self, description: str, context: Dict) -> ExecutionResult:
        """Execute security engineer tasks"""
        return await self.executor.execute_agent_task('security-engineer', description, context)
    
    async def _execute_data(self, description: str, context: Dict) -> ExecutionResult:
        """Execute data engineer tasks"""
        return await self.executor.execute_agent_task('data-engineer', description, context)
    
    async def _execute_reviewer(self, description: str, context: Dict) -> ExecutionResult:
        """Execute code reviewer tasks"""
        return await self.executor.execute_agent_task('code-reviewer', description, context)
    
    async def _execute_product_manager(self, description: str, context: Dict) -> ExecutionResult:
        """Execute product manager tasks"""
        # Check if creating spec
        if 'create spec' in description.lower():
            spec_name = self._extract_spec_name(context)
            command = f"{self.command_mappings['create_spec']} {spec_name}"
            return await self.executor.execute_command(command, context)
        
        return await self.executor.execute_agent_task('product-manager', description, context)
    
    async def _execute_chief_pm(self, description: str, context: Dict) -> ExecutionResult:
        """Execute chief product manager orchestration"""
        # Chief PM primarily delegates, so this is recursive
        return await self.executor.execute_agent_task('chief-product-manager', description, context)
    
    async def _execute_generic(self, description: str, context: Dict) -> ExecutionResult:
        """Generic execution for unknown agents"""
        self.logger.warning(f"No specific strategy for agent, using generic execution")
        return await self.executor.execute_command(f"echo 'Generic execution: {description}'", context)
    
    def _extract_spec_name(self, context: Dict) -> str:
        """Extract spec name from context"""
        if 'spec_name' in context:
            return context['spec_name']
        if 'feature_name' in context:
            return context['feature_name']
        # Try to extract from description
        return 'default-spec'
    
    def _extract_task_number(self, description: str) -> str:
        """Extract task number from description"""
        import re
        match = re.search(r'task[- ]?(\d+(?:\.\d+)?)', description.lower())
        if match:
            return match.group(1)
        return '1'
    
    async def execute_parallel_group(self, tasks: List[TaskRequest]) -> List[ExecutionResult]:
        """Execute a group of tasks in parallel"""
        self.logger.info(f"Executing {len(tasks)} tasks in parallel")
        
        # Create coroutines for all tasks
        coroutines = [
            self.process_task_delegation(task) 
            for task in tasks
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ExecutionResult(
                    success=False,
                    error=str(result),
                    agent_used=tasks[i].agent
                ))
            else:
                processed_results.append(result)
        
        return processed_results


# Integration with Claude Code's Task tool
class TaskToolHandler:
    """
    Handles Task tool calls from agents
    This would be integrated with Claude Code's internal Task tool
    """
    
    def __init__(self):
        self.bridge = AgentToolBridge()
    
    async def handle_task_call(self, 
                               agent: str, 
                               description: str, 
                               context: Dict = None,
                               parent_agent: str = None) -> Dict:
        """
        Handle a Task tool call from an agent
        
        This is what gets called when an agent uses:
        Task(agent="developer", description="implement user model", context={...})
        """
        task_request = TaskRequest(
            agent=agent,
            description=description,
            context=context or {},
            parent_agent=parent_agent or 'user'
        )
        
        result = await self.bridge.process_task_delegation(task_request)
        
        return {
            'success': result.success,
            'output': result.output,
            'error': result.error,
            'duration': result.duration,
            'agent_used': result.agent_used
        }


if __name__ == "__main__":
    # Example usage
    async def test():
        handler = TaskToolHandler()
        
        # Simulate chief-PM delegating to business-analyst
        result = await handler.handle_task_call(
            agent="business-analyst",
            description="Generate requirements for user authentication feature",
            context={'spec_name': 'user-auth'},
            parent_agent="chief-product-manager"
        )
        
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())