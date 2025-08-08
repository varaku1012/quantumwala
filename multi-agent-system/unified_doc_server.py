"""
Unified Documentation Server for Claude Code Multi-Agent System
Aggregates multiple documentation sources into a single interface
"""

import asyncio
import json
import hashlib
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from functools import lru_cache
import yaml
import aiohttp
from collections import defaultdict
import re


@dataclass
class DocResult:
    """Documentation search result"""
    source: str
    title: str
    content: str
    url: Optional[str] = None
    relevance_score: float = 0.0
    version: Optional[str] = None
    deprecated: bool = False
    alternative: Optional[str] = None
    security_warning: Optional[str] = None
    min_version: Optional[str] = None
    examples: List[str] = None
    

class DocumentationCache:
    """Intelligent caching for documentation"""
    
    def __init__(self, cache_dir: str = ".cache/docs", max_size_gb: float = 2.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.cache_index = self._load_index()
        
    def _load_index(self) -> Dict:
        """Load cache index"""
        index_file = self.cache_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_index(self):
        """Save cache index"""
        index_file = self.cache_dir / "index.json"
        with open(index_file, 'w') as f:
            json.dump(self.cache_index, f)
            
    def get(self, key: str) -> Optional[Any]:
        """Get cached item"""
        if key in self.cache_index:
            entry = self.cache_index[key]
            if time.time() < entry['expires']:
                cache_file = self.cache_dir / entry['file']
                if cache_file.exists():
                    with open(cache_file, 'r') as f:
                        return json.load(f)
        return None
        
    def set(self, key: str, value: Any, ttl: int = 86400):
        """Set cached item"""
        file_hash = hashlib.md5(key.encode()).hexdigest()
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(value, f)
            
        self.cache_index[key] = {
            'file': f"{file_hash}.json",
            'expires': time.time() + ttl,
            'size': cache_file.stat().st_size
        }
        self._save_index()
        self._cleanup_if_needed()
        
    def _cleanup_if_needed(self):
        """Remove old cache entries if size exceeded"""
        total_size = sum(entry['size'] for entry in self.cache_index.values())
        
        if total_size > self.max_size_bytes:
            # Remove expired entries first
            current_time = time.time()
            expired_keys = [k for k, v in self.cache_index.items() 
                          if v['expires'] < current_time]
            
            for key in expired_keys:
                self._remove_entry(key)
                
    def _remove_entry(self, key: str):
        """Remove a cache entry"""
        if key in self.cache_index:
            entry = self.cache_index[key]
            cache_file = self.cache_dir / entry['file']
            if cache_file.exists():
                cache_file.unlink()
            del self.cache_index[key]


class UnifiedDocumentationServer:
    """
    Single entry point for all documentation needs
    Aggregates multiple documentation sources
    """
    
    def __init__(self, config_path: str = "configs/documentation-config.yaml"):
        self.config = self._load_config(config_path)
        self.cache = DocumentationCache(
            cache_dir=self.config['cache']['location'],
            max_size_gb=float(self.config['cache']['size'].rstrip('GB'))
        )
        self.session = None
        self.source_handlers = self._initialize_handlers()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)['documentation']
            
    def _initialize_handlers(self) -> Dict:
        """Initialize documentation source handlers"""
        handlers = {}
        
        if self.config['sources'].get('devdocs', {}).get('enabled'):
            handlers['devdocs'] = DevDocsHandler(self.config['sources']['devdocs'])
            
        if self.config['sources'].get('mdn', {}).get('enabled'):
            handlers['mdn'] = MDNHandler(self.config['sources']['mdn'])
            
        if self.config['sources'].get('npm', {}).get('enabled'):
            handlers['npm'] = NPMHandler(self.config['sources']['npm'])
            
        if self.config['sources'].get('python', {}).get('enabled'):
            handlers['python'] = PythonDocsHandler(self.config['sources']['python'])
            
        if self.config['sources'].get('internal', {}).get('enabled'):
            handlers['internal'] = InternalDocsHandler(self.config['sources']['internal'])
            
        return handlers
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def query(self, topic: str, context: Optional[Dict] = None) -> List[DocResult]:
        """
        Query documentation across all sources
        
        Args:
            topic: The topic to search for
            context: Optional context (file type, language, etc.)
            
        Returns:
            List of documentation results ranked by relevance
        """
        # Check cache first
        cache_key = f"query:{topic}:{json.dumps(context or {})}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return [DocResult(**r) for r in cached_result]
            
        # Determine relevant sources based on context
        relevant_sources = self._get_relevant_sources(topic, context)
        
        # Query all relevant sources in parallel
        tasks = []
        for source_name, handler in self.source_handlers.items():
            if source_name in relevant_sources:
                tasks.append(self._query_source(handler, topic, context))
                
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors and flatten results
        all_results = []
        for result in results:
            if not isinstance(result, Exception) and result:
                all_results.extend(result)
                
        # Rank and merge results
        ranked_results = self._rank_results(all_results, topic)
        
        # Cache the results
        self.cache.set(cache_key, [r.__dict__ for r in ranked_results])
        
        return ranked_results
        
    def _get_relevant_sources(self, topic: str, context: Optional[Dict]) -> List[str]:
        """Determine relevant documentation sources"""
        relevant = []
        
        # Check if specific source is requested
        if ":" in topic:
            source_prefix = topic.split(":")[0]
            if source_prefix in self.source_handlers:
                return [source_prefix]
                
        # Use auto-routing based on file pattern
        if context and 'file_pattern' in context:
            for route in self.config['auto_routing']:
                if re.match(route['pattern'], context['file_pattern']):
                    relevant.extend(route['sources'])
                    
        # If no specific routing, use all sources
        if not relevant:
            relevant = list(self.source_handlers.keys())
            
        return relevant
        
    async def _query_source(self, handler, topic: str, context: Optional[Dict]) -> List[DocResult]:
        """Query a specific documentation source"""
        try:
            return await handler.search(topic, context)
        except Exception as e:
            print(f"Error querying {handler.__class__.__name__}: {e}")
            return []
            
    def _rank_results(self, results: List[DocResult], query: str) -> List[DocResult]:
        """Rank documentation results by relevance"""
        # Simple relevance scoring based on title and content matching
        query_terms = query.lower().split()
        
        for result in results:
            score = 0.0
            
            # Title matching (higher weight)
            title_lower = result.title.lower()
            for term in query_terms:
                if term in title_lower:
                    score += 2.0
                    
            # Content matching
            content_lower = result.content.lower()
            for term in query_terms:
                if term in content_lower:
                    score += 0.5
                    
            # Boost for exact matches
            if query.lower() in title_lower:
                score += 5.0
                
            # Penalty for deprecated items
            if result.deprecated:
                score *= 0.3
                
            result.relevance_score = score
            
        # Sort by relevance score
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
        
    async def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Validate code against documentation
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'deprecated_apis': [],
            'security_issues': []
        }
        
        # Extract API calls from code
        api_calls = self._extract_api_calls(code, language)
        
        # Validate each API call
        for api_call in api_calls:
            result = await self.query(api_call, {'language': language})
            
            if result:
                top_result = result[0]
                
                if top_result.deprecated:
                    validation_results['deprecated_apis'].append({
                        'api': api_call,
                        'alternative': top_result.alternative,
                        'source': top_result.source
                    })
                    
                if top_result.security_warning:
                    validation_results['security_issues'].append({
                        'api': api_call,
                        'warning': top_result.security_warning,
                        'source': top_result.source
                    })
                    
        return validation_results
        
    def _extract_api_calls(self, code: str, language: str) -> List[str]:
        """Extract API calls from code"""
        api_calls = []
        
        if language in ['javascript', 'typescript']:
            # Extract function calls and method calls
            pattern = r'\b(\w+(?:\.\w+)*)\s*\('
            api_calls = re.findall(pattern, code)
            
        elif language == 'python':
            # Extract imports and function calls
            import_pattern = r'(?:from\s+(\S+)\s+)?import\s+(\S+)'
            call_pattern = r'\b(\w+(?:\.\w+)*)\s*\('
            
            imports = re.findall(import_pattern, code)
            calls = re.findall(call_pattern, code)
            
            api_calls = [i[1] if i[1] else i[0] for i in imports] + calls
            
        return list(set(api_calls))  # Remove duplicates


class DevDocsHandler:
    """Handler for DevDocs.io documentation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config.get('url', 'https://devdocs.io')
        
    async def search(self, topic: str, context: Optional[Dict]) -> List[DocResult]:
        """Search DevDocs for documentation"""
        # Implement actual DevDocs API integration
        # This is a placeholder implementation
        return [
            DocResult(
                source="devdocs",
                title=f"DevDocs: {topic}",
                content=f"Documentation for {topic} from DevDocs",
                url=f"{self.base_url}/{topic}",
                relevance_score=0.8
            )
        ]


class MDNHandler:
    """Handler for MDN Web Docs"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config.get('url', 'https://developer.mozilla.org')
        
    async def search(self, topic: str, context: Optional[Dict]) -> List[DocResult]:
        """Search MDN for documentation"""
        # Implement actual MDN search
        return [
            DocResult(
                source="mdn",
                title=f"MDN: {topic}",
                content=f"Web standards documentation for {topic}",
                url=f"{self.base_url}/search?q={topic}",
                relevance_score=0.9
            )
        ]


class NPMHandler:
    """Handler for NPM package documentation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.registry_url = config.get('registry', 'https://registry.npmjs.org')
        self.docs_url = config.get('docs_url', 'https://www.npmjs.com/package')
        
    async def search(self, topic: str, context: Optional[Dict]) -> List[DocResult]:
        """Search NPM for package documentation"""
        # Implement actual NPM registry search
        return [
            DocResult(
                source="npm",
                title=f"NPM Package: {topic}",
                content=f"Package documentation for {topic}",
                url=f"{self.docs_url}/{topic}",
                relevance_score=0.7
            )
        ]


class PythonDocsHandler:
    """Handler for Python documentation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.version = config.get('version', '3.11')
        self.base_url = config.get('url', f'https://docs.python.org/{self.version}')
        
    async def search(self, topic: str, context: Optional[Dict]) -> List[DocResult]:
        """Search Python documentation"""
        return [
            DocResult(
                source="python",
                title=f"Python: {topic}",
                content=f"Python {self.version} documentation for {topic}",
                url=f"{self.base_url}/search.html?q={topic}",
                relevance_score=0.8
            )
        ]


class InternalDocsHandler:
    """Handler for internal/company documentation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.docs_path = Path(config.get('path', 'documentation/internal'))
        self.index = self._build_index() if config.get('auto_index') else {}
        
    def _build_index(self) -> Dict:
        """Build index of internal documentation"""
        index = {}
        if self.docs_path.exists():
            for doc_file in self.docs_path.rglob('*.md'):
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    index[doc_file.stem] = {
                        'path': str(doc_file),
                        'content': content[:500],  # First 500 chars
                        'full_content': content
                    }
        return index
        
    async def search(self, topic: str, context: Optional[Dict]) -> List[DocResult]:
        """Search internal documentation"""
        results = []
        topic_lower = topic.lower()
        
        for doc_name, doc_info in self.index.items():
            if topic_lower in doc_name.lower() or topic_lower in doc_info['content'].lower():
                results.append(DocResult(
                    source="internal",
                    title=f"Internal: {doc_name}",
                    content=doc_info['content'],
                    url=f"file:///{doc_info['path']}",
                    relevance_score=1.0  # Internal docs get highest priority
                ))
                
        return results


# Quality validation functions
async def validate_with_unified_docs(code: str, language: str, doc_server: UnifiedDocumentationServer) -> Dict:
    """
    Validate code using unified documentation server
    
    Returns validation results with specific issues found
    """
    validation = await doc_server.validate_code(code, language)
    
    # Additional checks based on configuration
    config = doc_server.config
    
    if config['validation']['require_types'] and language in ['typescript', 'python']:
        validation['warnings'].append("Type annotations recommended") if not _has_type_annotations(code, language) else None
        
    if config['validation']['accessibility_check'] and language in ['javascript', 'typescript']:
        validation['warnings'].extend(_check_accessibility(code))
        
    return validation


def _has_type_annotations(code: str, language: str) -> bool:
    """Check if code has proper type annotations"""
    if language == 'typescript':
        return ': ' in code  # Simple check for TypeScript types
    elif language == 'python':
        return '->' in code or ': ' in code  # Check for Python type hints
    return False


def _check_accessibility(code: str) -> List[str]:
    """Check for accessibility issues in frontend code"""
    warnings = []
    
    if '<img' in code and 'alt=' not in code:
        warnings.append("Images should have alt attributes for accessibility")
        
    if 'onClick' in code and 'onKeyPress' not in code:
        warnings.append("Interactive elements should support keyboard navigation")
        
    return warnings


if __name__ == "__main__":
    # Example usage
    async def test_unified_docs():
        async with UnifiedDocumentationServer() as doc_server:
            # Search for React hooks documentation
            results = await doc_server.query("React useState hook")
            for result in results[:3]:
                print(f"{result.source}: {result.title} (score: {result.relevance_score})")
                
            # Validate some code
            sample_code = """
            import React, { useState } from 'react';
            
            function MyComponent() {
                const [count, setCount] = useState(0);
                return <div onClick={() => setCount(count + 1)}>{count}</div>;
            }
            """
            
            validation = await doc_server.validate_code(sample_code, "javascript")
            print("\nValidation Results:", validation)
    
    # Run the test
    asyncio.run(test_unified_docs())
