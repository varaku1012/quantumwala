#!/usr/bin/env python3
"""
Context Engineering Layer - Implements the four core context strategies
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import tiktoken
import re

@dataclass
class ContextRequirements:
    """Defines what context an agent needs"""
    agent_type: str
    required_files: List[str]
    required_sections: List[str]
    max_tokens: int = 4000
    
class ContextCompressor:
    """Compresses context to fit within token limits"""
    
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        
    def compress(self, context: Dict[str, Any], max_tokens: int = 4000) -> Dict[str, Any]:
        """Compress context to fit within token limit"""
        # Count current tokens
        context_str = json.dumps(context)
        current_tokens = len(self.encoder.encode(context_str))
        
        if current_tokens <= max_tokens:
            return context
            
        # Progressive compression strategies
        compressed = context.copy()
        
        # 1. Remove redundant whitespace
        compressed = self._compress_whitespace(compressed)
        
        # 2. Summarize long sections
        if self._count_tokens(compressed) > max_tokens:
            compressed = self._summarize_sections(compressed, max_tokens)
            
        # 3. Remove low-priority sections
        if self._count_tokens(compressed) > max_tokens:
            compressed = self._remove_low_priority(compressed, max_tokens)
            
        return compressed
        
    def _compress_whitespace(self, context: Dict) -> Dict:
        """Remove unnecessary whitespace"""
        if isinstance(context, dict):
            return {k: self._compress_whitespace(v) for k, v in context.items()}
        elif isinstance(context, list):
            return [self._compress_whitespace(item) for item in context]
        elif isinstance(context, str):
            # Compress multiple spaces/newlines
            return re.sub(r'\s+', ' ', context).strip()
        return context
        
    def _summarize_sections(self, context: Dict, max_tokens: int) -> Dict:
        """Summarize long text sections"""
        compressed = context.copy()
        
        # Find longest strings and summarize
        for key, value in context.items():
            if isinstance(value, str) and len(value) > 1000:
                # Keep first and last parts, summarize middle
                parts = value.split('\n')
                if len(parts) > 10:
                    compressed[key] = '\n'.join(parts[:3] + ['[... summarized ...]'] + parts[-3:])
                    
        return compressed
        
    def _remove_low_priority(self, context: Dict, max_tokens: int) -> Dict:
        """Remove low-priority context sections"""
        priority_order = ['requirements', 'current_task', 'recent_results', 'steering', 'history']
        compressed = {}
        
        tokens_used = 0
        for priority in priority_order:
            if priority in context:
                section_tokens = self._count_tokens({priority: context[priority]})
                if tokens_used + section_tokens <= max_tokens:
                    compressed[priority] = context[priority]
                    tokens_used += section_tokens
                    
        return compressed
        
    def _count_tokens(self, obj: Any) -> int:
        """Count tokens in object"""
        return len(self.encoder.encode(json.dumps(obj)))

class ContextSelector:
    """Selects relevant context based on agent and task"""
    
    def __init__(self):
        self.agent_requirements = {
            'developer': {
                'needs': ['requirements', 'design', 'current_task', 'file_structure'],
                'exclude': ['market_research', 'competitor_analysis']
            },
            'architect': {
                'needs': ['requirements', 'tech_stack', 'constraints', 'existing_architecture'],
                'exclude': ['ui_mockups', 'user_interviews']
            },
            'business-analyst': {
                'needs': ['product_vision', 'user_research', 'requirements', 'acceptance_criteria'],
                'exclude': ['implementation_details', 'code_snippets']
            },
            'qa-engineer': {
                'needs': ['requirements', 'acceptance_criteria', 'test_scenarios', 'implementation'],
                'exclude': ['market_research', 'architecture_details']
            }
        }
        
    def select_for_agent(self, agent_type: str, task: Dict, full_context: Dict) -> Dict:
        """Select only relevant context for specific agent"""
        requirements = self.agent_requirements.get(agent_type, {'needs': [], 'exclude': []})
        
        selected = {}
        
        # Always include current task
        selected['current_task'] = task
        
        # Include needed sections
        for section in requirements['needs']:
            if section in full_context:
                selected[section] = full_context[section]
                
        # Include task-specific context
        if 'task_context' in task:
            for key in task['task_context']:
                if key in full_context and key not in requirements['exclude']:
                    selected[key] = full_context[key]
                    
        return selected

class ContextValidator:
    """Validates context for safety and consistency"""
    
    def __init__(self):
        self.max_depth = 10
        self.max_size_mb = 10
        
    def validate(self, context: Dict) -> Dict:
        """Validate context for poisoning and consistency"""
        # Check for circular references
        self._check_circular_refs(context)
        
        # Check size limits
        self._check_size_limits(context)
        
        # Sanitize inputs
        sanitized = self._sanitize_context(context)
        
        # Validate required fields
        self._validate_required_fields(sanitized)
        
        return sanitized
        
    def _check_circular_refs(self, obj: Any, seen: Optional[set] = None, depth: int = 0):
        """Check for circular references"""
        if seen is None:
            seen = set()
            
        if depth > self.max_depth:
            raise ValueError("Context depth exceeds maximum")
            
        if isinstance(obj, dict):
            obj_id = id(obj)
            if obj_id in seen:
                raise ValueError("Circular reference detected")
            seen.add(obj_id)
            
            for value in obj.values():
                self._check_circular_refs(value, seen, depth + 1)
                
        elif isinstance(obj, list):
            for item in obj:
                self._check_circular_refs(item, seen, depth + 1)
                
    def _check_size_limits(self, context: Dict):
        """Check context doesn't exceed size limits"""
        size_bytes = len(json.dumps(context).encode('utf-8'))
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > self.max_size_mb:
            raise ValueError(f"Context size {size_mb:.2f}MB exceeds limit of {self.max_size_mb}MB")
            
    def _sanitize_context(self, context: Dict) -> Dict:
        """Remove potentially harmful content"""
        sanitized = {}
        
        for key, value in context.items():
            # Skip keys that might contain sensitive data
            if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'token', 'key']):
                continue
                
            if isinstance(value, str):
                # Remove potential code injection
                value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.DOTALL)
                value = re.sub(r'javascript:', '', value)
                
            sanitized[key] = value
            
        return sanitized
        
    def _validate_required_fields(self, context: Dict):
        """Ensure required fields are present"""
        required = ['current_task']
        
        for field in required:
            if field not in context:
                raise ValueError(f"Required field '{field}' missing from context")

class ContextIsolator:
    """Isolates context between agents"""
    
    def __init__(self):
        self.isolation_namespaces = {}
        
    def create_isolated_context(self, context: Dict, agent_id: str = None) -> Dict:
        """Create isolated context copy for agent"""
        # Deep copy to prevent modifications
        import copy
        isolated = copy.deepcopy(context)
        
        # Add isolation metadata
        isolated['_metadata'] = {
            'agent_id': agent_id or self._generate_agent_id(),
            'isolation_level': 'strict',
            'created_at': str(Path().cwd()),
            'checksum': self._calculate_checksum(context)
        }
        
        # Track in namespace
        if agent_id:
            self.isolation_namespaces[agent_id] = isolated['_metadata']['checksum']
            
        return isolated
        
    def verify_isolation(self, context: Dict, agent_id: str) -> bool:
        """Verify context hasn't been tampered with"""
        if '_metadata' not in context:
            return False
            
        metadata = context['_metadata']
        
        # Check agent ownership
        if metadata.get('agent_id') != agent_id:
            return False
            
        # Verify checksum
        original_checksum = metadata.get('checksum')
        current_checksum = self._calculate_checksum({
            k: v for k, v in context.items() if k != '_metadata'
        })
        
        return original_checksum == current_checksum
        
    def _generate_agent_id(self) -> str:
        """Generate unique agent ID"""
        import uuid
        return str(uuid.uuid4())
        
    def _calculate_checksum(self, context: Dict) -> str:
        """Calculate context checksum"""
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()

class ContextEngine:
    """Main context engineering interface"""
    
    def __init__(self):
        self.compressor = ContextCompressor()
        self.selector = ContextSelector()
        self.validator = ContextValidator()
        self.isolator = ContextIsolator()
        
    def prepare_context(self, agent_type: str, task: Dict, full_context: Dict) -> Dict:
        """Prepare optimized context for agent"""
        try:
            # 1. Select relevant context
            selected = self.selector.select_for_agent(agent_type, task, full_context)
            
            # 2. Compress to fit window
            compressed = self.compressor.compress(selected, max_tokens=4000)
            
            # 3. Validate for poisoning
            validated = self.validator.validate(compressed)
            
            # 4. Isolate from other agents
            isolated = self.isolator.create_isolated_context(validated, f"{agent_type}_{task.get('id', 'unknown')}")
            
            return isolated
            
        except Exception as e:
            print(f"Context preparation failed: {e}")
            # Return minimal safe context
            return {
                'current_task': task,
                'error': str(e),
                '_metadata': {
                    'fallback': True,
                    'agent_type': agent_type
                }
            }
            
    def get_context_stats(self, context: Dict) -> Dict:
        """Get statistics about context"""
        return {
            'total_tokens': self.compressor._count_tokens(context),
            'sections': list(context.keys()),
            'is_compressed': context.get('_metadata', {}).get('compressed', False),
            'is_isolated': '_metadata' in context,
            'checksum': context.get('_metadata', {}).get('checksum', 'none')
        }

# Example usage
if __name__ == "__main__":
    engine = ContextEngine()
    
    # Sample full context
    full_context = {
        'requirements': 'Long requirements document...',
        'design': 'Architecture design...',
        'market_research': 'Competitor analysis...',
        'current_implementation': 'Existing code...',
        'test_results': 'Previous test runs...'
    }
    
    # Prepare context for developer
    task = {'id': 'task-123', 'description': 'Implement user authentication'}
    dev_context = engine.prepare_context('developer', task, full_context)
    
    print("Developer context stats:", engine.get_context_stats(dev_context))
    print("Context keys:", list(dev_context.keys()))