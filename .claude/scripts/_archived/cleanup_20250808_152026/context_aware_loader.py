#!/usr/bin/env python3
"""
Context-Aware Agent Loader
Enhanced agent loading with context engineering and memory integration
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from context_engine import ContextEngine
from memory_manager import MemoryManager
from steering_loader import SteeringLoader
from unified_state import UnifiedStateManager

class ContextAwareAgentLoader:
    """Loads agents with optimized context and relevant memories"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.agents_dir = self.project_root / '.claude' / 'agents'
        
        # Initialize components
        self.context_engine = ContextEngine()
        self.memory_manager = MemoryManager(self.project_root)
        self.steering_loader = SteeringLoader(self.project_root)
        self.state_manager = UnifiedStateManager(self.project_root)
        
        # Load agent hierarchy
        self.agent_hierarchy = self._load_agent_hierarchy()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
        
    def _load_agent_hierarchy(self) -> Dict:
        """Load agent hierarchy configuration"""
        hierarchy_file = self.agents_dir / 'restructure.yaml'
        if hierarchy_file.exists():
            with open(hierarchy_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
        
    def load_agent_with_context(self, agent_name: str, task: Dict) -> Dict:
        """Load agent with optimized context and memories"""
        # Load base agent definition
        agent = self._load_agent_definition(agent_name)
        
        # Determine agent type from hierarchy
        agent_type = self._get_agent_type(agent_name)
        
        # Get current state
        current_state = self._get_current_state()
        
        # Prepare optimized context
        context = self.context_engine.prepare_context(
            agent_type=agent_name,
            task=task,
            full_context=current_state
        )
        
        # Get relevant memories
        memories = self.memory_manager.get_relevant_memories(task)
        
        # Inject context and memories into agent
        agent['context'] = context
        agent['memories'] = memories
        agent['metadata'] = {
            'agent_type': agent_type,
            'context_stats': self.context_engine.get_context_stats(context),
            'memory_count': {
                'short_term': len(memories['short_term']),
                'long_term': len(memories['long_term']),
                'episodic': len(memories['episodic'])
            }
        }
        
        # Add few-shot examples if available
        if memories['episodic']:
            agent['few_shot_examples'] = memories['episodic']
            
        return agent
        
    def _load_agent_definition(self, agent_name: str) -> Dict:
        """Load base agent definition from file"""
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            raise ValueError(f"Agent {agent_name} not found")
            
        content = agent_file.read_text()
        
        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                instructions = parts[2].strip()
            else:
                frontmatter = {}
                instructions = content
        else:
            frontmatter = {}
            instructions = content
            
        return {
            'name': agent_name,
            'metadata': frontmatter,
            'instructions': instructions,
            'type': self._get_agent_type(agent_name)
        }
        
    def _get_agent_type(self, agent_name: str) -> str:
        """Determine agent type from hierarchy"""
        if not self.agent_hierarchy:
            return 'worker'  # Default
            
        for agent_type in ['orchestrators', 'workers', 'specialists']:
            if agent_name in self.agent_hierarchy.get(agent_type, {}):
                return agent_type
                
        return 'worker'  # Default
        
    def _get_current_state(self) -> Dict:
        """Get current system state for context"""
        state = {}
        
        # Load steering documents
        steering_docs = self.steering_loader.load_all()
        state['steering'] = steering_docs
        
        # Get workflow state
        workflow_state = self.state_manager.get_workflow_state()
        state['workflow'] = workflow_state
        
        # Get recent task results
        recent_results = self.memory_manager.short_term.get_context_window()
        state['recent_results'] = recent_results
        
        return state
        
    def validate_agent_context(self, agent: Dict) -> bool:
        """Validate agent has required context"""
        if 'context' not in agent:
            return False
            
        context = agent['context']
        
        # Check isolation
        if not self.context_engine.isolator.verify_isolation(
            context, 
            agent.get('metadata', {}).get('agent_id')
        ):
            return False
            
        # Check required fields based on agent type
        agent_type = agent.get('type', 'worker')
        required_fields = {
            'orchestrators': ['steering', 'workflow'],
            'workers': ['current_task'],
            'specialists': ['current_task', 'specialized_context']
        }
        
        for field in required_fields.get(agent_type, ['current_task']):
            if field not in context:
                return False
                
        return True
        
    def get_agent_context_requirements(self, agent_name: str) -> Dict:
        """Get context requirements for an agent"""
        hierarchy = self.agent_hierarchy
        
        # Find agent in hierarchy
        for agent_type in ['orchestrators', 'workers', 'specialists']:
            agents = hierarchy.get(agent_type, {})
            if agent_name in agents:
                agent_config = agents[agent_name]
                return {
                    'type': agent_type,
                    'context_needs': agent_config.get('context_needs', []),
                    'max_context_tokens': hierarchy.get('context_limits', {}).get(agent_type, 4000)
                }
                
        # Default requirements
        return {
            'type': 'worker',
            'context_needs': ['current_task'],
            'max_context_tokens': 4000
        }
        
    def store_agent_execution(self, agent_name: str, task_id: str, result: Dict):
        """Store agent execution result in memory"""
        self.memory_manager.store_execution(
            task_id=task_id,
            agent=agent_name,
            result=result
        )
        
    def get_agent_performance(self, agent_name: str) -> Dict:
        """Get agent performance metrics from memory"""
        # Search for agent's past executions
        memories = self.memory_manager.long_term.search({
            'type': 'task_result',
            'max_age_days': 30
        }, limit=100)
        
        # Filter for this agent
        agent_memories = [m for m in memories if m.metadata.get('agent') == agent_name]
        
        # Calculate metrics
        total = len(agent_memories)
        successful = sum(1 for m in agent_memories if m.metadata.get('success'))
        
        return {
            'total_executions': total,
            'success_rate': successful / total if total > 0 else 0,
            'recent_tasks': [m.metadata.get('task_id') for m in agent_memories[:5]]
        }

# Example usage
if __name__ == "__main__":
    loader = ContextAwareAgentLoader()
    
    # Load developer agent with context
    task = {
        'id': 'task-123',
        'type': 'implementation',
        'description': 'Implement user authentication',
        'keywords': ['auth', 'login', 'security']
    }
    
    agent = loader.load_agent_with_context('developer', task)
    
    print(f"Loaded agent: {agent['name']}")
    print(f"Agent type: {agent['type']}")
    print(f"Context stats: {agent['metadata']['context_stats']}")
    print(f"Memory stats: {agent['metadata']['memory_count']}")
    
    # Validate context
    is_valid = loader.validate_agent_context(agent)
    print(f"Context valid: {is_valid}")