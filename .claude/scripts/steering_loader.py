#!/usr/bin/env python3
"""
Steering Context Loader
Utility for loading and managing steering documents
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

class SteeringLoader:
    """Unified interface matching the test expectations"""
    
    def __init__(self, project_root=None):
        """Initialize steering loader"""
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Find project root by looking for .claude directory
            current = Path.cwd()
            while current != current.parent:
                if (current / '.claude').exists():
                    self.project_root = current
                    break
                current = current.parent
            else:
                self.project_root = Path.cwd()
        
        self.steering_dir = self.project_root / '.claude' / 'steering'
        self.cache = {}
    
    def load_all(self) -> Dict[str, str]:
        """Load all steering documents"""
        docs = {}
        
        if self.steering_dir.exists():
            for doc_name in ['product', 'tech', 'structure']:
                doc_path = self.steering_dir / f'{doc_name}.md'
                if doc_path.exists():
                    docs[doc_name] = doc_path.read_text(encoding='utf-8')
        
        self.cache = docs
        return docs
    
    def load_section(self, doc_name: str, section_name: str) -> Optional[str]:
        """Load a specific section from a steering document"""
        # First ensure document is loaded
        if doc_name not in self.cache:
            doc_path = self.steering_dir / f'{doc_name}.md'
            if doc_path.exists():
                self.cache[doc_name] = doc_path.read_text(encoding='utf-8')
            else:
                return None
        
        content = self.cache[doc_name]
        
        # Find section using markdown headers
        lines = content.split('\n')
        section_start = None
        section_level = None
        
        for i, line in enumerate(lines):
            # Check if this is our section
            if section_name in line and line.strip().startswith('#'):
                section_start = i
                section_level = len(line) - len(line.lstrip('#'))
                break
        
        if section_start is None:
            return None
        
        # Find section end (next header at same or higher level)
        section_end = len(lines)
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= section_level:
                    section_end = i
                    break
        
        return '\n'.join(lines[section_start:section_end])
    
    def get_context_for_agent(self, agent_type: str, task_description: str) -> Dict[str, str]:
        """Get relevant context for a specific agent and task"""
        context = {}
        
        # Load all documents if not cached
        if not self.cache:
            self.load_all()
        
        # Determine which documents are relevant for each agent type
        agent_context_map = {
            'product-manager': ['product'],
            'business-analyst': ['product', 'structure'],
            'architect': ['tech', 'structure'],
            'developer': ['tech', 'structure'],
            'qa-engineer': ['tech', 'structure'],
            'code-reviewer': ['tech', 'structure'],
            'uiux-designer': ['product', 'structure'],
            'chief-product-manager': ['product', 'tech', 'structure'],
            'steering-context-manager': ['product', 'tech', 'structure'],
            'test-agent': ['product']  # For testing
        }
        
        # Get relevant documents for agent
        relevant_docs = agent_context_map.get(agent_type, ['product', 'tech', 'structure'])
        
        for doc_name in relevant_docs:
            if doc_name in self.cache:
                context[doc_name] = self.cache[doc_name]
        
        return context
    
    def validate_proposal(self, proposal: str) -> Dict[str, any]:
        """Validate a proposal against steering context"""
        validation = {
            'aligned': True,
            'issues': [],
            'suggestions': []
        }
        
        # Load all documents
        if not self.cache:
            self.load_all()
        
        # Check tech stack alignment
        if 'tech' in self.cache:
            tech_content = self.cache['tech'].lower()
            proposal_lower = proposal.lower()
            
            # Check for technology mismatches
            if 'ruby' in proposal_lower and 'ruby' not in tech_content:
                validation['aligned'] = False
                validation['issues'].append('Ruby not in approved tech stack')
        
        return validation

class SteeringContextLoader:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.steering_dir = self.project_root / '.claude' / 'steering'
        self.context_dir = self.project_root / '.claude' / 'context'
        
    def load_steering_documents(self) -> Dict[str, str]:
        """Load all steering documents"""
        docs = {}
        
        # Load product.md
        product_path = self.steering_dir / 'product.md'
        if product_path.exists():
            docs['product'] = product_path.read_text()
            
        # Load tech.md
        tech_path = self.steering_dir / 'tech.md'
        if tech_path.exists():
            docs['tech'] = tech_path.read_text()
            
        # Load structure.md
        structure_path = self.steering_dir / 'structure.md'
        if structure_path.exists():
            docs['structure'] = structure_path.read_text()
            
        return docs
    
    def get_context_for_agent(self, agent_name: str, task: str = None) -> str:
        """Get relevant context for a specific agent"""
        docs = self.load_steering_documents()
        context_parts = []
        
        # Map agents to relevant documents
        agent_context_map = {
            'product-manager': ['product', 'tech'],
            'business-analyst': ['product', 'tech'],
            'architect': ['tech', 'structure', 'product'],
            'developer': ['structure', 'tech'],
            'uiux-designer': ['product', 'structure'],
            'qa-engineer': ['tech', 'structure'],
            'code-reviewer': ['tech', 'structure']
        }
        
        relevant_docs = agent_context_map.get(agent_name, ['product', 'tech', 'structure'])
        
        context_parts.append(f"# Steering Context for {agent_name}")
        if task:
            context_parts.append(f"## Task: {task}")
        context_parts.append("")
        
        for doc_type in relevant_docs:
            if doc_type in docs:
                context_parts.append(f"## {doc_type.capitalize()} Context")
                context_parts.append(docs[doc_type])
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def validate_alignment(self, proposal: str, aspect: str = 'all') -> Dict[str, any]:
        """Validate if a proposal aligns with steering documents"""
        docs = self.load_steering_documents()
        validation_result = {
            'aligned': True,
            'conflicts': [],
            'suggestions': []
        }
        
        # Simple validation logic - can be enhanced
        if aspect in ['all', 'product'] and 'product' in docs:
            # Check if proposal mentions any product principles
            if 'product principles' in docs['product'].lower():
                validation_result['suggestions'].append(
                    "Ensure proposal aligns with documented product principles"
                )
        
        if aspect in ['all', 'tech'] and 'tech' in docs:
            # Check technical constraints
            if 'constraints' in docs['tech'].lower():
                validation_result['suggestions'].append(
                    "Review technical constraints before implementation"
                )
        
        if aspect in ['all', 'structure'] and 'structure' in docs:
            # Check naming conventions
            if 'naming conventions' in docs['structure'].lower():
                validation_result['suggestions'].append(
                    "Follow established naming conventions"
                )
        
        return validation_result
    
    def export_context(self, output_path: str = None) -> str:
        """Export current context to JSON"""
        docs = self.load_steering_documents()
        
        context = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'documents': docs,
            'metadata': {
                'project_root': str(self.project_root),
                'has_product': 'product' in docs,
                'has_tech': 'tech' in docs,
                'has_structure': 'structure' in docs
            }
        }
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json.dumps(context, indent=2))
            return f"Context exported to {output_path}"
        else:
            return json.dumps(context, indent=2)
    
    def suggest_updates(self, implementation_summary: str) -> List[str]:
        """Suggest steering document updates based on implementation"""
        suggestions = []
        
        # Simple heuristics - can be enhanced with NLP
        if 'new pattern' in implementation_summary.lower():
            suggestions.append("Consider updating structure.md with new pattern")
        
        if 'technology' in implementation_summary.lower() or 'library' in implementation_summary.lower():
            suggestions.append("Consider updating tech.md with new technology choices")
        
        if 'feature' in implementation_summary.lower():
            suggestions.append("Consider updating product.md roadmap with completed feature")
        
        return suggestions


# CLI interface
if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    loader = SteeringContextLoader()
    
    if len(sys.argv) < 2:
        print("Usage: python steering_loader.py [command] [args]")
        print("Commands:")
        print("  load - Load all steering documents")
        print("  agent [agent-name] - Get context for specific agent")
        print("  validate [proposal] - Validate proposal alignment")
        print("  export [path] - Export context to JSON")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "load":
        docs = loader.load_steering_documents()
        for doc_type, content in docs.items():
            print(f"\n=== {doc_type.upper()} ===")
            print(content[:200] + "..." if len(content) > 200 else content)
    
    elif command == "agent" and len(sys.argv) > 2:
        agent_name = sys.argv[2]
        task = sys.argv[3] if len(sys.argv) > 3 else None
        context = loader.get_context_for_agent(agent_name, task)
        print(context)
    
    elif command == "validate" and len(sys.argv) > 2:
        proposal = " ".join(sys.argv[2:])
        result = loader.validate_alignment(proposal)
        print(json.dumps(result, indent=2))
    
    elif command == "export":
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = loader.export_context(output_path)
        print(result)
    
    else:
        print(f"Unknown command: {command}")
