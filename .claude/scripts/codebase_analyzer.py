#!/usr/bin/env python3
"""
Codebase Analysis Engine for Claude Code Multi-Agent System
Analyzes existing codebases to generate steering context documents and specifications

---
name: codebase-analyzer
version: 1.0.0
created: 2025-08-04
updated: 2025-08-04
changelog:
  - "1.0.0: Initial codebase analysis engine"
dependencies:
  - python>=3.7
  - gitpython>=3.1.0 (optional)
  - python-magic (optional)
tags:
  - analysis
  - documentation
  - reverse-engineering
---
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import hashlib
import mimetypes

class CodebaseAnalyzer:
    """Main engine for analyzing codebases and generating documentation"""
    
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path).resolve()
        self.claude_dir = self._find_claude_dir()
        self.analysis_data = {
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'repo_path': str(self.repo_path),
                'total_files': 0,
                'total_lines': 0
            },
            'technology_stack': {},
            'file_structure': {},
            'features': [],
            'apis': [],
            'database_schemas': [],
            'configurations': {},
            'dependencies': {},
            'business_logic': {},
            'user_flows': [],
            'integrations': []
        }
        
        # Initialize file type patterns
        self.file_patterns = {
            'frontend': {
                'javascript': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
                'stylesheets': ['.css', '.scss', '.sass', '.less', '.styl'],
                'templates': ['.html', '.htm', '.ejs', '.hbs', '.pug', '.twig'],
                'assets': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']
            },
            'backend': {
                'python': ['.py'],
                'javascript': ['.js', '.ts'],
                'java': ['.java', '.class', '.jar'],
                'csharp': ['.cs', '.csx'],
                'ruby': ['.rb', '.rake'],
                'php': ['.php', '.phtml'],
                'go': ['.go'],
                'rust': ['.rs'],
                'scala': ['.scala'],
                'kotlin': ['.kt', '.kts']
            },
            'config': {
                'package_managers': ['package.json', 'requirements.txt', 'Gemfile', 'composer.json', 'pom.xml', 'build.gradle', 'Cargo.toml'],
                'docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
                'ci_cd': ['.github/workflows/', '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile'],
                'env': ['.env', '.env.example', 'config.json', 'settings.py']
            },
            'database': {
                'sql': ['.sql'],
                'migrations': ['migrations/', 'migrate/', 'db/migrate/'],
                'schemas': ['schema.sql', 'schema.json', 'models.py', 'entities/']
            }
        }
    
    def _find_claude_dir(self):
        """Find or create .claude directory"""
        current = self.repo_path
        while current != current.parent:
            claude_dir = current / '.claude'
            if claude_dir.exists():
                return claude_dir
            current = current.parent
        
        # Create .claude directory in the repo root
        claude_dir = self.repo_path / '.claude'
        claude_dir.mkdir(exist_ok=True)
        return claude_dir
    
    def analyze(self, deep=False):
        """Perform comprehensive codebase analysis"""
        print(f"Starting analysis of {self.repo_path}")
        
        # Phase 1: File system analysis
        self._analyze_file_structure()
        self._detect_technology_stack()
        self._analyze_dependencies()
        
        # Phase 2: Code analysis
        self._extract_features()
        self._analyze_apis()
        self._extract_business_logic()
        
        # Phase 3: Configuration analysis
        self._analyze_configurations()
        self._detect_integrations()
        
        if deep:
            # Phase 4: Deep analysis (optional)
            self._analyze_git_history()
            self._analyze_performance_patterns()
        
        print(f"Analysis complete. Analyzed {self.analysis_data['metadata']['total_files']} files")
        return self.analysis_data
    
    def _analyze_file_structure(self):
        """Analyze repository file structure and organization"""
        print("Analyzing file structure...")
        
        structure = {}
        total_files = 0
        total_lines = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'vendor', 'dist', 'build']]
            
            root_path = Path(root)
            relative_path = root_path.relative_to(self.repo_path)
            
            if relative_path != Path('.'):
                structure[str(relative_path)] = []
            
            for file in files:
                if not file.startswith('.'):
                    file_path = root_path / file
                    try:
                        # Count lines in text files
                        mime_type, _ = mimetypes.guess_type(str(file_path))
                        if mime_type and mime_type.startswith('text'):
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = sum(1 for _ in f)
                                total_lines += lines
                        
                        total_files += 1
                        
                        if str(relative_path) != '.':
                            structure[str(relative_path)].append(file)
                        else:
                            if 'root' not in structure:
                                structure['root'] = []
                            structure['root'].append(file)
                    
                    except Exception:
                        pass  # Skip files that can't be read
        
        self.analysis_data['file_structure'] = structure
        self.analysis_data['metadata']['total_files'] = total_files
        self.analysis_data['metadata']['total_lines'] = total_lines
    
    def _detect_technology_stack(self):
        """Detect technologies used in the codebase"""
        print("Detecting technology stack...")
        
        tech_stack = defaultdict(list)
        file_counts = defaultdict(int)
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'vendor']]
            
            for file in files:
                file_path = Path(root) / file
                extension = file_path.suffix.lower()
                
                # Categorize by file extension
                for category, languages in self.file_patterns.items():
                    for lang, extensions in languages.items():
                        if extension in extensions or file in extensions:
                            tech_stack[category].append(lang)
                            file_counts[f"{category}:{lang}"] += 1
        
        # Convert to regular dict and remove duplicates
        self.analysis_data['technology_stack'] = {
            category: list(set(languages)) 
            for category, languages in tech_stack.items()
        }
        
        # Add file counts for technology importance
        self.analysis_data['technology_importance'] = dict(file_counts)
    
    def _analyze_dependencies(self):
        """Analyze project dependencies from package files"""
        print("Analyzing dependencies...")
        
        dependencies = {}
        
        # Check common dependency files
        dependency_files = {
            'package.json': self._parse_package_json,
            'requirements.txt': self._parse_requirements_txt,
            'Gemfile': self._parse_gemfile,
            'composer.json': self._parse_composer_json,
            'pom.xml': self._parse_pom_xml,
            'Cargo.toml': self._parse_cargo_toml
        }
        
        for filename, parser in dependency_files.items():
            file_path = self.repo_path / filename
            if file_path.exists():
                try:
                    deps = parser(file_path)
                    if deps:
                        dependencies[filename] = deps
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
        
        self.analysis_data['dependencies'] = dependencies
    
    def _parse_package_json(self, file_path):
        """Parse Node.js package.json"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                'dependencies': data.get('dependencies', {}),
                'devDependencies': data.get('devDependencies', {}),
                'name': data.get('name'),
                'version': data.get('version'),
                'scripts': data.get('scripts', {})
            }
    
    def _parse_requirements_txt(self, file_path):
        """Parse Python requirements.txt"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            deps = {}
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '>=' in line:
                        name, version = line.split('>=', 1)
                        deps[name] = f">={version}"
                    elif '==' in line:
                        name, version = line.split('==', 1)
                        deps[name] = version
                    else:
                        deps[line] = "latest"
            return deps
    
    def _parse_gemfile(self, file_path):
        """Parse Ruby Gemfile (basic parsing)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            gems = re.findall(r"gem ['\"]([^'\"]+)['\"]", content)
            return {gem: "latest" for gem in gems}
    
    def _parse_composer_json(self, file_path):
        """Parse PHP composer.json"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                'require': data.get('require', {}),
                'require-dev': data.get('require-dev', {}),
                'name': data.get('name')
            }
    
    def _parse_pom_xml(self, file_path):
        """Parse Java pom.xml (basic parsing)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Basic regex parsing for dependencies
            deps = {}
            dep_pattern = r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?<version>(.*?)</version>.*?</dependency>'
            matches = re.findall(dep_pattern, content, re.DOTALL)
            for group, artifact, version in matches:
                deps[f"{group}:{artifact}"] = version
            return deps
    
    def _parse_cargo_toml(self, file_path):
        """Parse Rust Cargo.toml (basic parsing)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            deps = {}
            # Simple parsing - would need proper TOML parser for production
            in_dependencies = False
            for line in content.split('\n'):
                line = line.strip()
                if line == '[dependencies]':
                    in_dependencies = True
                elif line.startswith('[') and line != '[dependencies]':
                    in_dependencies = False
                elif in_dependencies and '=' in line:
                    name, version = line.split('=', 1)
                    deps[name.strip()] = version.strip().strip('"')
            return deps
    
    def _extract_features(self):
        """Extract features from codebase analysis"""
        print("Extracting features...")
        
        features = []
        
        # Look for feature indicators in different file types
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                file_path = Path(root) / file
                
                try:
                    if file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cs', '.rb', '.php']:
                        features.extend(self._extract_features_from_file(file_path))
                except Exception:
                    pass
        
        # Deduplicate and categorize features
        unique_features = list(set(features))
        self.analysis_data['features'] = unique_features
    
    def _extract_features_from_file(self, file_path):
        """Extract feature indicators from a single file"""
        features = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Look for common feature patterns
                patterns = [
                    r'class (\w+)(?:Controller|Service|Manager|Handler)',
                    r'def (\w+)(?:_handler|_service|_controller)',
                    r'function (\w+)(?:Handler|Service|Controller)',
                    r'@app\.route\([\'"]([^\'\"]+)',
                    r'@RequestMapping\([\'"]([^\'\"]+)',
                    r'router\.(?:get|post|put|delete)\([\'"]([^\'\"]+)',
                    r'<!-- Feature: ([^-]+) -->',
                    r'# Feature: ([^\n]+)',
                    r'// Feature: ([^\n]+)'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    features.extend(matches)
        
        except Exception:
            pass
        
        return features
    
    def _analyze_apis(self):
        """Analyze API endpoints and interfaces"""
        print("Analyzing APIs...")
        
        apis = []
        
        # Look for API definitions
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                file_path = Path(root) / file
                
                try:
                    if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cs', '.rb', '.php']:
                        apis.extend(self._extract_apis_from_file(file_path))
                    elif file_path.name in ['openapi.yaml', 'swagger.yaml', 'api.yaml']:
                        apis.extend(self._parse_openapi_spec(file_path))
                except Exception:
                    pass
        
        self.analysis_data['apis'] = apis
    
    def _extract_apis_from_file(self, file_path):
        """Extract API endpoints from code files"""
        apis = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Common API patterns
                patterns = [
                    r'@app\.route\([\'"]([^\'\"]+)[\'"].*?methods=\[([^\]]+)\]',
                    r'@RequestMapping\([\'"]([^\'\"]+)[\'"].*?method.*?=.*?RequestMethod\.(\w+)',
                    r'router\.(\w+)\([\'"]([^\'\"]+)[\'"]',
                    r'app\.(\w+)\([\'"]([^\'\"]+)[\'"]',
                    r'@(\w+)Mapping\([\'"]([^\'\"]+)[\'"]'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if len(match) == 2:
                            method, path = match
                            apis.append({
                                'method': method.upper(),
                                'path': path,
                                'file': str(file_path.relative_to(self.repo_path))
                            })
        
        except Exception:
            pass
        
        return apis
    
    def _parse_openapi_spec(self, file_path):
        """Parse OpenAPI/Swagger specification"""
        # This would require PyYAML for full implementation
        # For now, return placeholder
        return [{'method': 'GET', 'path': '/api/docs', 'file': str(file_path)}]
    
    def _extract_business_logic(self):
        """Extract business logic patterns and rules"""
        print("Extracting business logic...")
        
        business_logic = {
            'validation_rules': [],
            'business_rules': [],
            'workflows': [],
            'calculations': []
        }
        
        # This would be expanded based on specific patterns
        # For now, placeholder implementation
        self.analysis_data['business_logic'] = business_logic
    
    def _analyze_configurations(self):
        """Analyze configuration files and settings"""
        print("Analyzing configurations...")
        
        configs = {}
        
        # Common config files
        config_files = [
            '.env', '.env.example', 'config.json', 'config.yaml',
            'settings.py', 'application.properties', 'web.config'
        ]
        
        for config_file in config_files:
            file_path = self.repo_path / config_file
            if file_path.exists():
                try:
                    configs[config_file] = self._parse_config_file(file_path)
                except Exception:
                    pass
        
        self.analysis_data['configurations'] = configs
    
    def _parse_config_file(self, file_path):
        """Parse configuration file based on type"""
        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Basic key-value parsing for other formats
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                config = {}
                for line in lines:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
                return config
    
    def _detect_integrations(self):
        """Detect external service integrations"""
        print("Detecting integrations...")
        
        integrations = []
        
        # Look for common integration patterns
        integration_patterns = [
            r'https?://api\.([^/]+)',
            r'@(\w+)\.com',
            r'CLIENT_ID.*?(\w+)',
            r'API_KEY.*?(\w+)',
            r'import.*?(\w+).*?client'
        ]
        
        # This would be expanded to scan files for integration patterns
        self.analysis_data['integrations'] = integrations
    
    def _analyze_git_history(self):
        """Analyze git history for insights (requires GitPython)"""
        print("Analyzing git history...")
        
        try:
            import git
            repo = git.Repo(self.repo_path)
            
            commits = list(repo.iter_commits(max_count=100))
            
            history_data = {
                'total_commits': len(commits),
                'contributors': len(set(commit.author.name for commit in commits)),
                'recent_activity': [
                    {
                        'message': commit.message.strip(),
                        'author': commit.author.name,
                        'date': commit.committed_datetime.isoformat()
                    }
                    for commit in commits[:10]
                ]
            }
            
            self.analysis_data['git_history'] = history_data
            
        except ImportError:
            print("GitPython not available, skipping git history analysis")
        except Exception as e:
            print(f"Git analysis failed: {e}")
    
    def _analyze_performance_patterns(self):
        """Analyze performance patterns in the code"""
        print("Analyzing performance patterns...")
        
        # Placeholder for performance analysis
        self.analysis_data['performance_patterns'] = {
            'caching_used': False,
            'database_optimizations': [],
            'async_patterns': [],
            'potential_bottlenecks': []
        }
    
    def generate_steering_documents(self):
        """Generate steering context documents from analysis"""
        print("Generating steering documents...")
        
        # Ensure directories exist
        steering_dir = self.claude_dir / 'steering'
        steering_dir.mkdir(exist_ok=True)
        
        # Generate product steering document
        self._generate_product_steering()
        
        # Generate technology steering document
        self._generate_tech_steering()
        
        # Generate structure steering document
        self._generate_structure_steering()
        
        print("Steering documents generated successfully")
    
    def _generate_product_steering(self):
        """Generate product steering document"""
        tech_stack = self.analysis_data.get('technology_stack', {})
        features = self.analysis_data.get('features', [])
        apis = self.analysis_data.get('apis', [])
        
        # Infer product type from technology stack
        product_type = self._infer_product_type(tech_stack)
        
        content = f"""---
name: product
version: 1.0.0
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
changelog:
  - "1.0.0: Generated from codebase analysis"
analysis_metadata:
  confidence_level: medium
  source_files_analyzed: {self.analysis_data['metadata']['total_files']}
  analysis_date: {self.analysis_data['metadata']['analyzed_at']}
---

# Product Steering Context - [PRODUCT NAME]

*Generated from codebase analysis on {datetime.now().strftime('%Y-%m-%d')}*

## Product Overview

Based on the codebase analysis, this appears to be a **{product_type}** with the following characteristics:

- **Technology Stack**: {', '.join(tech_stack.get('backend', []))} backend, {', '.join(tech_stack.get('frontend', []))} frontend
- **Scale**: {self.analysis_data['metadata']['total_files']} files, {self.analysis_data['metadata']['total_lines']} lines of code
- **API Endpoints**: {len(apis)} identified endpoints

## Identified Features

Based on code analysis, the following features were identified:

"""
        
        # Add top features
        for i, feature in enumerate(features[:10], 1):
            content += f"{i}. **{feature.replace('_', ' ').title()}**\n"
        
        content += f"""

## Technology Architecture

### Backend Technologies
{self._format_tech_list(tech_stack.get('backend', []))}

### Frontend Technologies  
{self._format_tech_list(tech_stack.get('frontend', []))}

### Database & Storage
{self._format_tech_list(tech_stack.get('database', ['Not detected']))}

## API Endpoints Detected

"""
        
        # Add API endpoints
        for api in apis[:10]:
            content += f"- **{api.get('method', 'GET')}** `{api.get('path', '/')}` (in {api.get('file', 'unknown')})\n"
        
        content += f"""

## Inferred User Personas

*Note: These are inferred from codebase patterns and should be validated*

### Primary User Type
- **Role**: [Inferred from UI patterns and feature complexity]
- **Technical Level**: [Based on interface complexity]
- **Use Cases**: [Derived from feature analysis]

## Success Metrics (Recommendations)

Based on the identified features, consider tracking:

1. **User Engagement**: Feature usage, session duration
2. **Performance**: API response times, error rates  
3. **Business Impact**: [Specific to your domain]

## Validation Required

⚠️ **Human Review Needed** - Please validate and refine:

1. Product name and description
2. Target user personas
3. Business goals and metrics
4. Feature priorities
5. Competitive positioning

---

*This document was generated automatically from codebase analysis. Please review and customize based on your specific product requirements.*
"""
        
        # Write to file
        product_file = self.claude_dir / 'steering' / 'product.md'
        with open(product_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_tech_steering(self):
        """Generate technology steering document"""
        tech_stack = self.analysis_data.get('technology_stack', {})
        dependencies = self.analysis_data.get('dependencies', {})
        
        content = f"""---
name: tech
version: 1.0.0
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
changelog:
  - "1.0.0: Generated from codebase analysis"
---

# Technology Steering Context

*Generated from codebase analysis on {datetime.now().strftime('%Y-%m-%d')}*

## Technology Stack

### Backend Technologies
{self._format_tech_details(tech_stack.get('backend', []))}

### Frontend Technologies
{self._format_tech_details(tech_stack.get('frontend', []))}

### Configuration Management
{self._format_tech_details(tech_stack.get('config', []))}

## Dependencies Analysis

"""
        
        # Add dependencies from different package managers
        for pkg_file, deps in dependencies.items():
            content += f"### {pkg_file}\n"
            if isinstance(deps, dict):
                dep_count = sum(len(v) if isinstance(v, dict) else 1 for v in deps.values())
                content += f"- Total dependencies: {dep_count}\n"
                content += f"- Package manager: {pkg_file}\n\n"
        
        content += f"""

## Architecture Principles (Inferred)

Based on the codebase structure and patterns:

1. **Modularity**: [Assessment based on file organization]
2. **Separation of Concerns**: [Based on directory structure]
3. **Configuration Management**: [Based on config files found]
4. **Testing Strategy**: [Based on test files/directories]

## Performance Considerations

- **File Count**: {self.analysis_data['metadata']['total_files']} files
- **Code Volume**: {self.analysis_data['metadata']['total_lines']} lines
- **Complexity**: [Based on technology diversity]

## Security Analysis

⚠️ **Security Review Recommended**

Based on the codebase scan:
- Configuration files detected: {len(self.analysis_data.get('configurations', {}))}
- Environment files found: [List any .env files]
- API endpoints exposed: {len(self.analysis_data.get('apis', []))}

## Recommendations

1. **Documentation**: Add inline code documentation
2. **Testing**: Implement comprehensive test coverage
3. **Security**: Review configuration management
4. **Performance**: Consider caching strategies

---

*This document was generated automatically. Please review and customize based on your specific requirements.*
"""
        
        # Write to file
        tech_file = self.claude_dir / 'steering' / 'tech.md'
        with open(tech_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_structure_steering(self):
        """Generate structure steering document"""
        file_structure = self.analysis_data.get('file_structure', {})
        
        content = f"""---
name: structure
version: 1.0.0
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
changelog:
  - "1.0.0: Generated from codebase analysis"
---

# Structure Steering Context

*Generated from codebase analysis on {datetime.now().strftime('%Y-%m-%d')}*

## Project Structure

```
{self._format_file_structure(file_structure)}
```

## Organization Patterns

Based on the directory structure analysis:

### Code Organization
- **Main directories**: {len(file_structure)} directories analyzed
- **File distribution**: Varies by directory
- **Naming conventions**: [Analyzed from file/directory names]

### Development Workflow (Inferred)

1. **Source Code**: Located in [main source directories]
2. **Configuration**: Centralized in config files
3. **Testing**: [Based on test directory presence]
4. **Build Process**: [Based on build files detected]

## Conventions Analysis

### File Naming
- **Pattern consistency**: [Based on file name analysis]
- **Extension usage**: [Based on file type distribution]

### Directory Structure
- **Logical grouping**: [Assessment of organization]
- **Separation of concerns**: [Based on directory purposes]

---

*This document was generated automatically. Please customize based on your team's specific conventions.*
"""
        
        # Write to file
        structure_file = self.claude_dir / 'steering' / 'structure.md'
        with open(structure_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _infer_product_type(self, tech_stack):
        """Infer product type from technology stack"""
        backend = tech_stack.get('backend', [])
        frontend = tech_stack.get('frontend', [])
        
        if 'javascript' in frontend and any(b in backend for b in ['python', 'javascript', 'java']):
            return "Web Application"
        elif 'python' in backend and not frontend:
            return "API Service"
        elif any(mobile in str(tech_stack) for mobile in ['react-native', 'flutter', 'swift', 'kotlin']):
            return "Mobile Application"
        else:
            return "Software Application"
    
    def _format_tech_list(self, tech_list):
        """Format technology list for markdown"""
        if not tech_list:
            return "- Not detected\n"
        return '\n'.join(f"- {tech.title()}" for tech in tech_list) + '\n'
    
    def _format_tech_details(self, tech_list):
        """Format technology details for markdown"""
        if not tech_list:
            return "- None detected\n"
        
        details = ""
        for tech in tech_list:
            importance = self.analysis_data.get('technology_importance', {}).get(f"backend:{tech}", 0)
            details += f"- **{tech.title()}**: {importance} files\n"
        return details
    
    def _format_file_structure(self, structure, indent=0):
        """Format file structure for display"""
        result = ""
        for path, files in sorted(structure.items()):
            result += "  " * indent + f"{path}/\n"
            if files:
                for file in sorted(files)[:5]:  # Show first 5 files
                    result += "  " * (indent + 1) + f"{file}\n"
                if len(files) > 5:
                    result += "  " * (indent + 1) + f"... and {len(files) - 5} more files\n"
        return result
    
    def export_analysis(self, output_file=None):
        """Export analysis data to JSON file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.claude_dir / 'analysis' / f'codebase_analysis_{timestamp}.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_data, f, indent=2, default=str)
        
        print(f"Analysis exported to: {output_file}")
        return output_file


def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python codebase_analyzer.py <repository_path> [--deep] [--export]")
        return
    
    repo_path = sys.argv[1]
    deep_analysis = '--deep' in sys.argv
    export_analysis = '--export' in sys.argv
    
    analyzer = CodebaseAnalyzer(repo_path)
    
    # Perform analysis
    analysis_data = analyzer.analyze(deep=deep_analysis)
    
    # Generate steering documents
    analyzer.generate_steering_documents()
    
    if export_analysis:
        analyzer.export_analysis()
    
    print("Analysis complete!")
    print(f"Generated steering documents in: {analyzer.claude_dir / 'steering'}")


if __name__ == "__main__":
    main()