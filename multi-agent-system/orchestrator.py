"""
Claude Code Orchestrator with Unified Documentation Support
Main orchestration system for multi-agent development
"""

import subprocess
import json
import os
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml
from unified_doc_server import UnifiedDocumentationServer, DocResult
import hashlib


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    task_id: str
    agent_type: str
    description: str
    input_data: Dict
    dependencies: List[str] = None
    status: str = "pending"  # pending, running, completed, failed
    output: Optional[Dict] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    

class ClaudeCodeOrchestrator:
    """
    Orchestrates multiple Claude Code agents with unified documentation support
    """
    
    def __init__(self, project_dir: str = ".", enable_docs: bool = True):
        self.project_dir = Path(project_dir)
        self.context_file = self.project_dir / "context/state.json"
        self.agents_dir = self.project_dir / "agents"
        self.logs_dir = self.project_dir / "logs"
        self.artifacts_dir = self.project_dir / "artifacts"
        
        # Initialize directories
        self._init_directories()
        
        # Load or create context
        self.context = self._load_context()
        
        # Initialize documentation server if enabled
        self.doc_server = None
        if enable_docs:
            config_path = self.project_dir / "configs/documentation-config.yaml"
            if config_path.exists():
                self.doc_server = UnifiedDocumentationServer(str(config_path))
                
        # Task queue and tracking
        self.task_queue = []
        self.completed_tasks = []
        self.running_tasks = {}
        
        # Agent performance metrics
        self.agent_metrics = {}
        
    def _init_directories(self):
        """Initialize required directories"""
        for dir_path in [self.agents_dir, self.logs_dir, self.artifacts_dir, 
                         self.project_dir / "context"]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def _load_context(self) -> Dict:
        """Load or create project context"""
        if self.context_file.exists():
            with open(self.context_file, 'r') as f:
                return json.load(f)
        else:
            initial_context = {
                "project_state": "initialized",
                "created_at": datetime.now().isoformat(),
                "agents": {},
                "features": {},
                "tasks": {}
            }
            self._save_context(initial_context)
            return initial_context
            
    def _save_context(self, context: Optional[Dict] = None):
        """Save project context"""
        if context:
            self.context = context
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2)
            
    def update_context(self, updates: Dict):
        """Update project context"""
        self.context.update(updates)
        self._save_context()
        
    async def run_agent(self, agent_type: str, task: str, input_data: Dict, 
                       use_docs: bool = True) -> Dict:
        """
        Run a Claude Code agent with optional documentation support
        
        Args:
            agent_type: Type of agent (developer, architect, qa, etc.)
            task: Task description
            input_data: Input data for the task
            use_docs: Whether to use documentation server
            
        Returns:
            Agent output dictionary
        """
        task_id = self._generate_task_id(agent_type, task)
        
        # Log task start
        self._log_task_start(task_id, agent_type, task)
        
        # Enhance task with documentation if available
        if use_docs and self.doc_server:
            input_data = await self._enhance_with_docs(task, input_data, agent_type)
            
        # Prepare input file
        input_file = self.agents_dir / f"{task_id}_input.json"
        with open(input_file, 'w') as f:
            json.dump(input_data, f, indent=2)
            
        # Prepare task with documentation context
        enhanced_task = self._prepare_task_with_context(task, input_data, agent_type)
        
        # Run Claude Code
        output = await self._execute_claude_code(agent_type, enhanced_task, input_file, task_id)
        
        # Validate output if documentation server is available
        if use_docs and self.doc_server and 'code' in output:
            validation_results = await self._validate_with_docs(output['code'], agent_type)
            output['validation'] = validation_results
            
        # Log task completion
        self._log_task_completion(task_id, agent_type, output)
        
        # Update metrics
        self._update_agent_metrics(agent_type, task_id, output)
        
        return output
        
    async def _enhance_with_docs(self, task: str, input_data: Dict, agent_type: str) -> Dict:
        """Enhance input data with relevant documentation"""
        async with self.doc_server as docs:
            # Extract key terms from task
            key_terms = self._extract_key_terms(task)
            
            # Query documentation for each term
            doc_results = {}
            for term in key_terms:
                results = await docs.query(term, {'agent_type': agent_type})
                if results:
                    doc_results[term] = [
                        {
                            'title': r.title,
                            'content': r.content[:500],  # Limit content size
                            'url': r.url,
                            'deprecated': r.deprecated,
                            'alternative': r.alternative
                        }
                        for r in results[:3]  # Top 3 results per term
                    ]
                    
            # Add documentation to input data
            input_data['documentation'] = doc_results
            input_data['doc_guidelines'] = self._get_agent_doc_guidelines(agent_type)
            
        return input_data
        
    def _extract_key_terms(self, task: str) -> List[str]:
        """Extract key technical terms from task description"""
        # Simple extraction - can be enhanced with NLP
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                       'to', 'for', 'with', 'as', 'by', 'from', 'using', 'create',
                       'implement', 'build', 'make', 'add', 'update', 'fix'}
        
        words = task.lower().split()
        key_terms = [w for w in words if w not in common_words and len(w) > 2]
        
        # Add common technical combinations
        if 'react' in words and 'component' in words:
            key_terms.append('react component')
        if 'api' in words and 'rest' in words:
            key_terms.append('rest api')
            
        return list(set(key_terms))[:5]  # Limit to 5 terms
        
    def _get_agent_doc_guidelines(self, agent_type: str) -> Dict:
        """Get documentation guidelines for specific agent type"""
        guidelines = {
            'developer': {
                'check_deprecated': True,
                'require_examples': True,
                'validate_apis': True,
                'include_types': True
            },
            'architect': {
                'include_patterns': True,
                'check_best_practices': True,
                'validate_performance': True,
                'include_alternatives': True
            },
            'qa': {
                'include_test_patterns': True,
                'check_edge_cases': True,
                'validate_security': True,
                'check_accessibility': True
            },
            'code_reviewer': {
                'check_standards': True,
                'validate_conventions': True,
                'include_improvements': True,
                'check_complexity': True
            }
        }
        return guidelines.get(agent_type, {})
        
    def _prepare_task_with_context(self, task: str, input_data: Dict, agent_type: str) -> str:
        """Prepare task with documentation context"""
        enhanced_task = f"""
{task}

IMPORTANT: You have access to documentation in the input data. Please:
1. Follow all documented best practices
2. Avoid any deprecated APIs (use alternatives provided)
3. Ensure code follows the latest standards
4. Include error handling as documented
5. Add type annotations where applicable

Context:
- Project State: {self.context.get('project_state', 'unknown')}
- Previous Tasks: {len(self.completed_tasks)} completed
- Agent Type: {agent_type}
"""
        
        if 'documentation' in input_data:
            enhanced_task += "\n\nRelevant Documentation Available - use it to ensure correctness."
            
        return enhanced_task
        
    async def _execute_claude_code(self, agent_type: str, task: str, 
                                   input_file: Path, task_id: str) -> Dict:
        """Execute Claude Code with the specified parameters"""
        output_file = self.agents_dir / f"{task_id}_output.json"
        
        # Construct command
        cmd = [
            "claude-code",  # Assumes claude-code is in PATH
            "--task", agent_type,
            "--context-file", str(self.context_file),
            "--input-file", str(input_file),
            "--output", str(output_file)
        ]
        
        # Add workspace if it exists
        workspace = self.project_dir / "workspace"
        if workspace.exists():
            cmd.extend(["--workspace", str(workspace)])
            
        try:
            # Run Claude Code
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send task description
            stdout, stderr = await process.communicate(task.encode())
            
            if process.returncode == 0:
                # Read output
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        return json.load(f)
                else:
                    return {
                        'status': 'completed',
                        'output': stdout.decode(),
                        'task_id': task_id
                    }
            else:
                return {
                    'status': 'failed',
                    'error': stderr.decode(),
                    'task_id': task_id
                }
                
        except FileNotFoundError:
            # Claude Code not installed, create mock response
            return self._create_mock_response(agent_type, task, input_file)
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'task_id': task_id
            }
            
    def _create_mock_response(self, agent_type: str, task: str, input_file: Path) -> Dict:
        """Create mock response when Claude Code is not available"""
        # This helps with testing the orchestrator without Claude Code installed
        
        with open(input_file, 'r') as f:
            input_data = json.load(f)
            
        mock_responses = {
            'developer': {
                'status': 'completed',
                'code': '// Mock implementation\nfunction implement() { return "TODO"; }',
                'files_created': ['mock_implementation.js'],
                'tests_passed': True
            },
            'architect': {
                'status': 'completed',
                'architecture': {
                    'stack': ['React', 'Node.js', 'PostgreSQL'],
                    'patterns': ['MVC', 'Repository'],
                    'components': ['Frontend', 'API', 'Database']
                }
            },
            'qa': {
                'status': 'completed',
                'tests_run': 10,
                'tests_passed': 8,
                'coverage': 85.5,
                'issues': ['Missing error handling', 'No input validation']
            }
        }
        
        response = mock_responses.get(agent_type, {'status': 'completed', 'output': 'Mock output'})
        response['task'] = task
        response['input_summary'] = f"Processed with {len(input_data.get('documentation', {}))} documentation references"
        
        return response
        
    async def _validate_with_docs(self, code: str, agent_type: str) -> Dict:
        """Validate generated code against documentation"""
        if not self.doc_server:
            return {'status': 'skipped', 'reason': 'Documentation server not available'}
            
        # Detect language from agent type or code
        language = self._detect_language(code, agent_type)
        
        async with self.doc_server as docs:
            validation = await docs.validate_code(code, language)
            
            # Add severity levels
            for issue in validation.get('deprecated_apis', []):
                issue['severity'] = 'high'
                
            for issue in validation.get('security_issues', []):
                issue['severity'] = 'critical'
                
            # Calculate validation score
            total_issues = (
                len(validation.get('errors', [])) * 3 +
                len(validation.get('deprecated_apis', [])) * 2 +
                len(validation.get('warnings', [])) * 1
            )
            
            validation['score'] = max(0, 100 - (total_issues * 5))
            validation['passed'] = validation['score'] >= 70
            
        return validation
        
    def _detect_language(self, code: str, agent_type: str) -> str:
        """Detect programming language from code or agent type"""
        # Simple detection based on common patterns
        if 'import React' in code or 'jsx' in agent_type.lower():
            return 'javascript'
        elif 'def ' in code or 'import ' in code or 'python' in agent_type.lower():
            return 'python'
        elif 'func ' in code or 'go' in agent_type.lower():
            return 'go'
        elif 'fn ' in code or 'rust' in agent_type.lower():
            return 'rust'
        elif 'class ' in code and 'public' in code:
            return 'java'
        else:
            return 'javascript'  # Default
            
    def _generate_task_id(self, agent_type: str, task: str) -> str:
        """Generate unique task ID"""
        timestamp = int(time.time() * 1000)
        task_hash = hashlib.md5(f"{agent_type}:{task}".encode()).hexdigest()[:8]
        return f"{agent_type}_{timestamp}_{task_hash}"
        
    def _log_task_start(self, task_id: str, agent_type: str, task: str):
        """Log task start"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'task_start',
            'task_id': task_id,
            'agent_type': agent_type,
            'task': task[:200]  # Truncate long tasks
        }
        
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y%m%d')}_tasks.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def _log_task_completion(self, task_id: str, agent_type: str, output: Dict):
        """Log task completion"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'task_complete',
            'task_id': task_id,
            'agent_type': agent_type,
            'status': output.get('status', 'unknown'),
            'validation_score': output.get('validation', {}).get('score', None)
        }
        
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y%m%d')}_tasks.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def _update_agent_metrics(self, agent_type: str, task_id: str, output: Dict):
        """Update agent performance metrics"""
        if agent_type not in self.agent_metrics:
            self.agent_metrics[agent_type] = {
                'tasks_completed': 0,
                'tasks_failed': 0,
                'avg_validation_score': 0,
                'total_validation_scores': 0
            }
            
        metrics = self.agent_metrics[agent_type]
        
        if output.get('status') == 'completed':
            metrics['tasks_completed'] += 1
        else:
            metrics['tasks_failed'] += 1
            
        if 'validation' in output and 'score' in output['validation']:
            score = output['validation']['score']
            total = metrics['total_validation_scores']
            current_avg = metrics['avg_validation_score']
            
            metrics['total_validation_scores'] = total + 1
            metrics['avg_validation_score'] = (current_avg * total + score) / (total + 1)
            
    async def run_parallel_agents(self, tasks: List[Tuple[str, str, Dict]]) -> List[Dict]:
        """
        Run multiple agents in parallel
        
        Args:
            tasks: List of (agent_type, task_description, input_data) tuples
            
        Returns:
            List of results from all agents
        """
        async_tasks = [
            self.run_agent(agent_type, task, input_data)
            for agent_type, task, input_data in tasks
        ]
        
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 'error',
                    'error': str(result),
                    'agent_type': tasks[i][0],
                    'task': tasks[i][1]
                })
            else:
                processed_results.append(result)
                
        return processed_results
        
    def get_metrics_report(self) -> str:
        """Generate metrics report"""
        report = "\n=== Agent Performance Metrics ===\n"
        
        for agent_type, metrics in self.agent_metrics.items():
            report += f"\n{agent_type.upper()}:\n"
            report += f"  Tasks Completed: {metrics['tasks_completed']}\n"
            report += f"  Tasks Failed: {metrics['tasks_failed']}\n"
            
            if metrics['total_validation_scores'] > 0:
                report += f"  Avg Validation Score: {metrics['avg_validation_score']:.1f}/100\n"
                
        return report


# Example usage and testing
async def main():
    """Example usage of the orchestrator"""
    
    # Initialize orchestrator
    orchestrator = ClaudeCodeOrchestrator(
        project_dir="C:/Users/varak/repos/quantumwala/multi-agent-system",
        enable_docs=True
    )
    
    # Example 1: Run a single agent with documentation support
    print("Running Developer Agent with Documentation Support...")
    result = await orchestrator.run_agent(
        agent_type="developer",
        task="Implement user authentication with JWT tokens and OAuth support",
        input_data={
            "requirements": {
                "auth_types": ["email/password", "google", "github"],
                "security": "JWT with refresh tokens",
                "database": "PostgreSQL"
            }
        },
        use_docs=True
    )
    
    print(f"Developer Agent Result: {result.get('status')}")
    if 'validation' in result:
        print(f"Code Validation Score: {result['validation'].get('score', 'N/A')}/100")
        
    # Example 2: Run multiple agents in parallel
    print("\nRunning Multiple Agents in Parallel...")
    parallel_tasks = [
        ("architect", "Design microservices architecture for e-commerce platform", 
         {"requirements": "scalable, cloud-native"}),
        
        ("qa", "Create test plan for authentication module",
         {"module": "authentication", "coverage_target": 90}),
         
        ("code_reviewer", "Review the authentication implementation",
         {"files": ["auth.py", "auth_test.py"], "standards": ["PEP8", "security"]})
    ]
    
    parallel_results = await orchestrator.run_parallel_agents(parallel_tasks)
    
    for result in parallel_results:
        print(f"- {result.get('agent_type', 'Unknown')}: {result.get('status', 'unknown')}")
        
    # Print metrics report
    print(orchestrator.get_metrics_report())
    
    
if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
