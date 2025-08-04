#!/usr/bin/env python3
"""
Version management system for Claude Code multi-agent components
Tracks, validates, and manages component versions across the system

---
name: version-manager
version: 1.0.0
created: 2025-08-03
updated: 2025-08-03
changelog:
  - "1.0.0: Initial version management system"
dependencies:
  - python>=3.7
  - pyyaml (optional)
---
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

class VersionManager:
    """Manages component versions across the Claude Code system"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.version_registry = self.claude_dir / 'version-registry.json'
        self.components = {}
        
        # Load existing registry
        self._load_registry()
    
    def _find_project_root(self):
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_registry(self):
        """Load version registry from file"""
        if self.version_registry.exists():
            try:
                with open(self.version_registry, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.components = data.get('components', {})
            except Exception as e:
                print(f"Error loading version registry: {e}")
                self.components = {}
    
    def _save_registry(self):
        """Save version registry to file"""
        try:
            registry_data = {
                'system_version': '1.0.0',
                'last_updated': datetime.now().isoformat(),
                'components': self.components
            }
            
            with open(self.version_registry, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2)
        except Exception as e:
            print(f"Error saving version registry: {e}")
    
    def _extract_metadata(self, file_path):
        """Extract metadata from component files"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Look for YAML frontmatter
            yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.MULTILINE | re.DOTALL)
            if yaml_match:
                return self._parse_yaml_metadata(yaml_match.group(1))
            
            # Look for comment block metadata
            comment_match = re.search(r'---\s*\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
            if comment_match:
                return self._parse_yaml_metadata(comment_match.group(1))
            
            return None
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return None
    
    def _parse_yaml_metadata(self, yaml_content):
        """Parse YAML-like metadata"""
        metadata = {}
        lines = yaml_content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle quoted strings
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Handle lists
                if key in ['changelog', 'dependencies', 'tags']:
                    metadata[key] = []
                    # Check if it's inline list or multiline
                    if value.startswith('[') and value.endswith(']'):
                        # Inline list
                        items = value[1:-1].split(',')
                        metadata[key] = [item.strip().strip('"\'') for item in items]
                    elif value == '' or value == '-':
                        # Multiline list
                        i += 1
                        while i < len(lines):
                            next_line = lines[i].strip()
                            if next_line.startswith('- '):
                                item = next_line[2:].strip().strip('"\'')
                                metadata[key].append(item)
                                i += 1
                            elif next_line and not next_line.startswith(' ') and ':' in next_line:
                                i -= 1
                                break
                            else:
                                i += 1
                else:
                    metadata[key] = value
            
            i += 1
        
        return metadata
    
    def scan_components(self):
        """Scan all components and extract their versions"""
        print("Scanning components for version information...")
        
        # Scan agents
        agents_dir = self.claude_dir / 'agents'
        if agents_dir.exists():
            for agent_file in agents_dir.glob('*.md'):
                metadata = self._extract_metadata(agent_file)
                if metadata:
                    component_id = f"agent:{metadata.get('name', agent_file.stem)}"
                    self._register_component(component_id, metadata, agent_file)
        
        # Scan scripts
        scripts_dir = self.claude_dir / 'scripts'
        if scripts_dir.exists():
            for script_file in scripts_dir.glob('*.py'):
                metadata = self._extract_metadata(script_file)
                if metadata:
                    component_id = f"script:{metadata.get('name', script_file.stem)}"
                    self._register_component(component_id, metadata, script_file)
        
        # Scan commands
        commands_dir = self.claude_dir / 'commands'
        if commands_dir.exists():
            for command_file in commands_dir.glob('*.md'):
                metadata = self._extract_metadata(command_file)
                if metadata:
                    component_id = f"command:{metadata.get('name', command_file.stem)}"
                    self._register_component(component_id, metadata, command_file)
        
        # Scan steering documents
        steering_dir = self.claude_dir / 'steering'
        if steering_dir.exists():
            for steering_file in steering_dir.glob('*.md'):
                if steering_file.name != 'README.md':
                    metadata = self._extract_metadata(steering_file)
                    if metadata:
                        component_id = f"steering:{metadata.get('name', steering_file.stem)}"
                        self._register_component(component_id, metadata, steering_file)
        
        self._save_registry()
        print(f"Scanned {len(self.components)} components")
    
    def _register_component(self, component_id, metadata, file_path):
        """Register a component in the version registry"""
        # Calculate file hash for integrity checking
        file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        
        component_info = {
            'name': metadata.get('name', 'unknown'),
            'version': metadata.get('version', '0.0.0'),
            'file_path': str(file_path.relative_to(self.project_root)),
            'file_hash': file_hash,
            'created': metadata.get('created'),
            'updated': metadata.get('updated'),
            'changelog': metadata.get('changelog', []),
            'dependencies': metadata.get('dependencies', []),
            'tags': metadata.get('tags', []),
            'last_scanned': datetime.now().isoformat()
        }
        
        self.components[component_id] = component_info
    
    def validate_versions(self):
        """Validate component versions and dependencies"""
        print("Validating component versions...")
        
        issues = []
        
        for component_id, info in self.components.items():
            # Check version format
            version = info.get('version', '0.0.0')
            if not re.match(r'^\d+\.\d+\.\d+', version):
                issues.append(f"{component_id}: Invalid version format '{version}'")
            
            # Check file integrity
            file_path = self.project_root / info['file_path']
            if file_path.exists():
                current_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
                if current_hash != info['file_hash']:
                    issues.append(f"{component_id}: File has been modified since last scan")
            else:
                issues.append(f"{component_id}: File not found at {info['file_path']}")
            
            # Check dependencies
            for dep in info.get('dependencies', []):
                if ':' in dep and not self._check_dependency(dep):
                    issues.append(f"{component_id}: Dependency '{dep}' not satisfied")
        
        return issues
    
    def _check_dependency(self, dependency):
        """Check if a dependency is satisfied"""
        if dependency.startswith('python>='):
            # Check Python version
            import sys
            required_version = dependency.split('>=')[1]
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            return self._version_compare(current_version, required_version) >= 0
        
        # Check for component dependencies
        for comp_id in self.components:
            if dependency in comp_id:
                return True
        
        return False
    
    def _version_compare(self, version1, version2):
        """Compare two version strings"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        
        v1 = version_tuple(version1)
        v2 = version_tuple(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    def generate_version_report(self):
        """Generate a comprehensive version report"""
        report = f"""# Version Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Components**: {len(self.components)}

## Component Overview

| Type | Name | Version | Last Updated | Dependencies |
|------|------|---------|--------------|--------------|
"""
        
        # Sort components by type and name
        sorted_components = sorted(self.components.items(), key=lambda x: x[0])
        
        for component_id, info in sorted_components:
            comp_type = component_id.split(':')[0]
            name = info['name']
            version = info['version']
            updated = info.get('updated', 'Unknown')
            deps = ', '.join(info.get('dependencies', []))
            
            report += f"| {comp_type} | {name} | {version} | {updated} | {deps} |\n"
        
        # Add validation issues
        issues = self.validate_versions()
        if issues:
            report += "\n## Validation Issues\n\n"
            for issue in issues:
                report += f"- {issue}\n"
        else:
            report += "\n## Validation Status\n\n✓ All components passed validation\n"
        
        # Add changelog summary
        report += "\n## Recent Changes\n\n"
        for component_id, info in sorted_components:
            changelog = info.get('changelog', [])
            if changelog:
                report += f"### {info['name']}\n"
                for entry in changelog[-3:]:  # Show last 3 entries
                    report += f"- {entry}\n"
                report += "\n"
        
        return report
    
    def update_component_version(self, component_id, new_version, changelog_entry=None):
        """Update a component's version"""
        if component_id not in self.components:
            print(f"Component {component_id} not found")
            return False
        
        component = self.components[component_id]
        old_version = component['version']
        
        # Update version
        component['version'] = new_version
        component['updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Add changelog entry
        if changelog_entry:
            if 'changelog' not in component:
                component['changelog'] = []
            component['changelog'].append(f"{new_version}: {changelog_entry}")
        
        # Update file hash
        file_path = self.project_root / component['file_path']
        if file_path.exists():
            component['file_hash'] = hashlib.md5(file_path.read_bytes()).hexdigest()
        
        self._save_registry()
        print(f"Updated {component_id} from {old_version} to {new_version}")
        return True
    
    def list_components(self, component_type=None):
        """List all components or components of a specific type"""
        filtered_components = self.components
        
        if component_type:
            filtered_components = {
                k: v for k, v in self.components.items() 
                if k.startswith(f"{component_type}:")
            }
        
        for component_id, info in sorted(filtered_components.items()):
            print(f"{component_id}: v{info['version']} ({info.get('updated', 'Unknown')})")
    
    def export_versions(self, output_file=None):
        """Export version information to a file"""
        if output_file is None:
            output_file = self.claude_dir / 'logs' / 'reports' / f'versions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'system_version': '1.0.0',
            'components': self.components
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Version data exported to: {output_file}")
        return output_file


def main():
    """Main function for command-line usage"""
    import sys
    
    manager = VersionManager()
    
    if len(sys.argv) < 2:
        print("Usage: python version_manager.py [scan|validate|report|list|update]")
        return
    
    command = sys.argv[1]
    
    if command == 'scan':
        manager.scan_components()
    elif command == 'validate':
        issues = manager.validate_versions()
        if issues:
            print("Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("All components passed validation")
    elif command == 'report':
        report = manager.generate_version_report()
        report_file = manager.claude_dir / 'logs' / 'reports' / f'version_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report, encoding='utf-8')
        print(f"Version report generated: {report_file}")
    elif command == 'list':
        component_type = sys.argv[2] if len(sys.argv) > 2 else None
        manager.list_components(component_type)
    elif command == 'export':
        manager.export_versions()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()