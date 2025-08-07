#!/usr/bin/env python3
"""Custom context management tool for agents"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import hashlib
import re

class ContextTool:
    def __init__(self):
        self.project_root = self._find_project_root()
        self.context_cache = {}
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def compress(self, text: str, max_tokens: int = 4000) -> Dict:
        """Compress text to fit within token limit"""
        # Simple token estimation (1 token ≈ 4 chars)
        estimated_tokens = len(text) // 4
        
        if estimated_tokens <= max_tokens:
            return {
                'compressed': False,
                'text': text,
                'original_tokens': estimated_tokens,
                'compressed_tokens': estimated_tokens
            }
        
        # Progressive compression
        compressed_text = text
        
        # Level 1: Remove excess whitespace
        compressed_text = re.sub(r'\s+', ' ', compressed_text)
        compressed_text = re.sub(r'\n\s*\n', '\n', compressed_text)
        
        # Level 2: Remove comments
        compressed_text = re.sub(r'#.*?\n', '\n', compressed_text)
        compressed_text = re.sub(r'//.*?\n', '\n', compressed_text)
        compressed_text = re.sub(r'/\*.*?\*/', '', compressed_text, flags=re.DOTALL)
        
        # Level 3: Truncate if still too long
        if len(compressed_text) // 4 > max_tokens:
            max_chars = max_tokens * 4
            compressed_text = compressed_text[:max_chars] + "...[truncated]"
        
        return {
            'compressed': True,
            'text': compressed_text,
            'original_tokens': estimated_tokens,
            'compressed_tokens': len(compressed_text) // 4,
            'compression_ratio': f"{(1 - len(compressed_text)/len(text))*100:.1f}%"
        }
    
    def extract(self, text: str, query: str) -> Dict:
        """Extract relevant sections from text based on query"""
        query_terms = query.lower().split()
        lines = text.split('\n')
        relevant_lines = []
        context_window = 3  # Lines before/after match
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(term in line_lower for term in query_terms):
                # Add context window
                start = max(0, i - context_window)
                end = min(len(lines), i + context_window + 1)
                relevant_lines.extend(lines[start:end])
                relevant_lines.append('---')
        
        extracted = '\n'.join(relevant_lines)
        
        return {
            'query': query,
            'extracted_text': extracted,
            'lines_extracted': len(relevant_lines),
            'total_lines': len(lines),
            'relevance_ratio': f"{(len(relevant_lines)/len(lines))*100:.1f}%"
        }
    
    def merge(self, context1: str, context2: str) -> Dict:
        """Merge two contexts intelligently"""
        # Create sections
        sections1 = self._parse_sections(context1)
        sections2 = self._parse_sections(context2)
        
        # Merge sections
        merged_sections = {}
        all_keys = set(sections1.keys()) | set(sections2.keys())
        
        for key in all_keys:
            if key in sections1 and key in sections2:
                # Both have this section - merge content
                merged_sections[key] = f"{sections1[key]}\n\n{sections2[key]}"
            elif key in sections1:
                merged_sections[key] = sections1[key]
            else:
                merged_sections[key] = sections2[key]
        
        # Reconstruct merged context
        merged_text = '\n\n'.join([f"## {k}\n{v}" for k, v in merged_sections.items()])
        
        return {
            'merged_text': merged_text,
            'sections_from_context1': len(sections1),
            'sections_from_context2': len(sections2),
            'total_sections': len(merged_sections),
            'merged_sections': list(merged_sections.keys())
        }
    
    def validate(self, context: str) -> Dict:
        """Validate context structure and content"""
        issues = []
        warnings = []
        
        # Check for required sections
        required_sections = ['requirements', 'objectives', 'constraints']
        context_lower = context.lower()
        
        for section in required_sections:
            if section not in context_lower:
                warnings.append(f"Missing recommended section: {section}")
        
        # Check for issues
        if len(context) < 100:
            issues.append("Context too short (< 100 chars)")
        
        if len(context) > 50000:
            issues.append("Context too long (> 50000 chars)")
        
        # Check for sensitive information
        sensitive_patterns = [
            r'api[_-]?key\s*=\s*["\'][\w]+["\']',
            r'password\s*=\s*["\'][\w]+["\']',
            r'secret\s*=\s*["\'][\w]+["\']'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                issues.append(f"Potential sensitive information detected: {pattern}")
        
        # Check structure
        lines = context.split('\n')
        if all(len(line) > 100 for line in lines[:10] if line):
            warnings.append("No line breaks in first 10 lines - poor formatting")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'stats': {
                'length': len(context),
                'lines': len(lines),
                'estimated_tokens': len(context) // 4
            }
        }
    
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Parse text into sections based on headers"""
        sections = {}
        current_section = 'main'
        current_content = []
        
        for line in text.split('\n'):
            # Check if line is a header
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def summarize(self, text: str, max_length: int = 500) -> Dict:
        """Create a summary of the context"""
        lines = text.split('\n')
        
        # Extract key information
        summary_lines = []
        
        # Get headers
        headers = [line for line in lines if line.startswith('#')]
        summary_lines.extend(headers[:5])
        
        # Get lines with key terms
        key_terms = ['must', 'should', 'required', 'important', 'critical']
        for line in lines:
            if any(term in line.lower() for term in key_terms):
                summary_lines.append(line)
                if len('\n'.join(summary_lines)) > max_length:
                    break
        
        summary = '\n'.join(summary_lines[:max_length])
        
        return {
            'summary': summary,
            'original_length': len(text),
            'summary_length': len(summary),
            'compression_ratio': f"{(1 - len(summary)/len(text))*100:.1f}%"
        }


def main():
    """CLI interface for context tool"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        print("Commands: compress, extract, merge, validate, summarize")
        sys.exit(1)
    
    tool = ContextTool()
    command = sys.argv[1]
    
    try:
        if command == "compress":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: compress <text> [max_tokens]"}))
                sys.exit(1)
            
            text = sys.argv[2]
            max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
            
            # Handle file input
            if Path(text).exists():
                with open(text, 'r') as f:
                    text = f.read()
            
            result = tool.compress(text, max_tokens)
            
        elif command == "extract":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "Usage: extract <text/file> <query>"}))
                sys.exit(1)
            
            text = sys.argv[2]
            query = sys.argv[3]
            
            # Handle file input
            if Path(text).exists():
                with open(text, 'r') as f:
                    text = f.read()
            
            result = tool.extract(text, query)
            
        elif command == "merge":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "Usage: merge <context1> <context2>"}))
                sys.exit(1)
            
            context1 = sys.argv[2]
            context2 = sys.argv[3]
            
            # Handle file inputs
            if Path(context1).exists():
                with open(context1, 'r') as f:
                    context1 = f.read()
            if Path(context2).exists():
                with open(context2, 'r') as f:
                    context2 = f.read()
            
            result = tool.merge(context1, context2)
            
        elif command == "validate":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: validate <context>"}))
                sys.exit(1)
            
            context = sys.argv[2]
            
            # Handle file input
            if Path(context).exists():
                with open(context, 'r') as f:
                    context = f.read()
            
            result = tool.validate(context)
            
        elif command == "summarize":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: summarize <text> [max_length]"}))
                sys.exit(1)
            
            text = sys.argv[2]
            max_length = int(sys.argv[3]) if len(sys.argv) > 3 else 500
            
            # Handle file input
            if Path(text).exists():
                with open(text, 'r') as f:
                    text = f.read()
            
            result = tool.summarize(text, max_length)
            
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()