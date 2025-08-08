#!/usr/bin/env python3
"""
Comprehensive spec lifecycle management
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class SpecStage(Enum):
    BACKLOG = "backlog"
    SCOPE = "scope" 
    COMPLETED = "completed"
    SANDBOX = "sandbox"
    ARCHIVED = "archived"

class SpecManager:
    def __init__(self):
        self.specs_root = Path('.claude/specs')
        self.meta_dir = self.specs_root / '_meta'
        self.ensure_structure()
        
        # Required metadata fields
        self.required_metadata_fields = [
            'name', 'description', 'stage', 'created', 'updated',
            'completion_rate', 'priority', 'version'
        ]
        
        # Valid priority values
        self.valid_priorities = ['low', 'medium', 'high', 'critical']
    
    def ensure_structure(self):
        """Ensure proper directory structure exists"""
        for stage in SpecStage:
            (self.specs_root / stage.value).mkdir(parents=True, exist_ok=True)
        self.meta_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_metadata(self, metadata: Dict) -> List[str]:
        """Validate metadata completeness and correctness"""
        issues = []
        
        # Check required fields
        for field in self.required_metadata_fields:
            if field not in metadata:
                issues.append(f"Missing required field: {field}")
        
        # Validate specific fields
        if 'priority' in metadata and metadata['priority'] not in self.valid_priorities:
            issues.append(f"Invalid priority: {metadata['priority']}. Must be one of: {', '.join(self.valid_priorities)}")
        
        if 'completion_rate' in metadata:
            rate = metadata['completion_rate']
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
                issues.append(f"Invalid completion_rate: {rate}. Must be between 0 and 1")
        
        if 'stage' in metadata and metadata['stage'] not in [s.value for s in SpecStage]:
            issues.append(f"Invalid stage: {metadata['stage']}")
        
        return issues
    
    def validate_spec_structure(self, spec_dir: Path) -> List[str]:
        """Validate that spec has required structure"""
        issues = []
        
        required_files = ['overview.md', '_meta.json', 'README.md']
        for file in required_files:
            if not (spec_dir / file).exists():
                issues.append(f"Missing required file: {file}")
        
        # Check metadata content
        meta_file = spec_dir / '_meta.json'
        if meta_file.exists():
            try:
                metadata = json.loads(meta_file.read_text())
                metadata_issues = self.validate_metadata(metadata)
                issues.extend(metadata_issues)
            except json.JSONDecodeError:
                issues.append("Invalid JSON in _meta.json")
            except Exception as e:
                issues.append(f"Error reading _meta.json: {e}")
        
        return issues
    
    def create_spec(self, name: str, description: str, stage: SpecStage = SpecStage.BACKLOG) -> bool:
        """Create new specification with complete metadata and error handling"""
        spec_dir = self.specs_root / stage.value / name
        
        if spec_dir.exists():
            print(f"[ERROR] Spec '{name}' already exists in {stage.value}")
            return False
        
        try:
            # Create directory with parents
            spec_dir.mkdir(parents=True, exist_ok=True)
            
            # Create COMPLETE metadata with all required fields
            metadata = {
                'name': name,
                'description': description,
                'stage': stage.value,
                'created': datetime.now().isoformat(),
                'updated': datetime.now().isoformat(),
                'completion_rate': 0.0,
                'priority': 'medium',
                'tags': [],
                'assignee': None,
                'version': '1.0.0',
                'estimated_effort': 'TBD'
            }
            
            # Write metadata with error handling
            (spec_dir / '_meta.json').write_text(
                json.dumps(metadata, indent=2), 
                encoding='utf-8'
            )
            
            # Create overview with better template
            overview_content = f"""# {name.replace('-', ' ').title()}

**Status**: {stage.value.title()}  
**Created**: {datetime.now().strftime('%Y-%m-%d')}  
**Description**: {description}

## Overview
{description}

## Success Criteria
- [ ] Define clear success criteria
- [ ] Establish measurable outcomes
- [ ] Set completion timeline

## Next Steps
Based on current stage ({stage.value}):
"""
            
            if stage == SpecStage.BACKLOG:
                overview_content += """
- [ ] Refine requirements and scope
- [ ] Estimate effort and timeline
- [ ] Prioritize against other backlog items
"""
            elif stage == SpecStage.SCOPE:
                overview_content += """
- [ ] Create detailed requirements
- [ ] Design technical architecture
- [ ] Break down into implementation tasks
"""
            else:
                overview_content += """
- [ ] Review current status
- [ ] Update documentation
- [ ] Plan next actions
"""
            
            (spec_dir / 'overview.md').write_text(overview_content, encoding='utf-8')
            
            # Create comprehensive README
            readme_content = f"""# {name}

Quick reference for the {name} specification.

**Stage**: {stage.value}  
**Description**: {description}  
**Created**: {datetime.now().strftime('%Y-%m-%d')}

## Files
- `overview.md` - Feature overview and success criteria
- `_meta.json` - Specification metadata and tracking
- `requirements.md` - Detailed requirements (created when moved to scope)
- `design.md` - Technical design (created during design phase)
- `tasks.md` - Implementation tasks (created during task breakdown)

## Quick Commands
```bash
# View status
python .claude/scripts/spec_manager.py status

# Promote to next stage
python .claude/scripts/spec_manager.py promote {name} --to=scope

# Update metadata
# Edit _meta.json directly or use promotion commands
```
"""
            (spec_dir / 'README.md').write_text(readme_content, encoding='utf-8')
            
            # Update dashboard with error handling
            try:
                self.update_dashboard()
            except Exception as e:
                print(f"Warning: Could not update dashboard: {e}")
                # Don't fail the entire operation if dashboard update fails
            
            print(f"[SUCCESS] Created spec '{name}' in {stage.value}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to create spec '{name}': {e}")
            # Clean up partial creation
            if spec_dir.exists():
                import shutil
                try:
                    shutil.rmtree(spec_dir)
                except:
                    pass
            return False
    
    def promote_spec(self, name: str, to_stage: SpecStage, reason: str = "") -> bool:
        """Promote spec to different stage"""
        # Find current location
        current_spec = self.find_spec(name)
        if not current_spec:
            print(f"Spec '{name}' not found")
            return False
        
        current_stage, spec_path = current_spec
        
        if current_stage == to_stage:
            print(f"Spec '{name}' already in {to_stage.value}")
            return True
        
        # Validate promotion
        if not self.validate_promotion(spec_path, current_stage, to_stage):
            return False
        
        # Move spec
        new_path = self.specs_root / to_stage.value / name
        spec_path.rename(new_path)
        
        # Update metadata
        self.update_spec_metadata(new_path, to_stage, reason)
        
        # Update dashboard
        self.update_dashboard()
        
        print(f"Promoted '{name}': {current_stage.value} -> {to_stage.value}")
        return True
    
    def find_spec(self, name: str) -> Optional[tuple]:
        """Find spec in any stage"""
        for stage in SpecStage:
            spec_path = self.specs_root / stage.value / name
            if spec_path.exists():
                return (stage, spec_path)
        return None
    
    def validate_promotion(self, spec_path: Path, from_stage: SpecStage, to_stage: SpecStage) -> bool:
        """Validate if promotion is allowed"""
        if to_stage == SpecStage.COMPLETED:
            # Check task completion
            tasks_file = spec_path / 'tasks.md'
            if not tasks_file.exists():
                print(f"Cannot promote to completed: no tasks.md found")
                return False
            
            try:
                tasks_content = tasks_file.read_text(encoding='utf-8')
                completed_tasks = tasks_content.count('✅')
                total_tasks = tasks_content.count('#### Task')
                
                if total_tasks == 0:
                    print(f"Cannot promote to completed: no tasks defined")
                    return False
                
                completion_rate = completed_tasks / total_tasks
                if completion_rate < 0.9:
                    print(f"Cannot promote to completed: only {completion_rate:.0%} tasks complete (need >90%)")
                    return False
            except UnicodeDecodeError:
                print(f"Cannot read tasks file due to encoding issues")
                return False
        
        return True
    
    def update_spec_metadata(self, spec_path: Path, new_stage: SpecStage, reason: str):
        """Update spec metadata"""
        meta_file = spec_path / '_meta.json'
        if meta_file.exists():
            metadata = json.loads(meta_file.read_text())
        else:
            metadata = {}
        
        metadata.update({
            'stage': new_stage.value,
            'updated': datetime.now().isoformat(),
            'promotion_reason': reason
        })
        
        meta_file.write_text(json.dumps(metadata, indent=2))
    
    def get_status_overview(self) -> Dict:
        """Get comprehensive status overview"""
        overview = {}
        
        for stage in SpecStage:
            stage_dir = self.specs_root / stage.value
            specs = []
            
            if stage_dir.exists():
                for spec_dir in stage_dir.iterdir():
                    if spec_dir.is_dir() and not spec_dir.name.startswith('_'):
                        spec_info = self.get_spec_info(spec_dir)
                        specs.append(spec_info)
            
            overview[stage.value] = {
                'count': len(specs),
                'specs': specs
            }
        
        return overview
    
    def get_spec_info(self, spec_dir: Path) -> Dict:
        """Get detailed spec information"""
        meta_file = spec_dir / '_meta.json'
        
        if meta_file.exists():
            metadata = json.loads(meta_file.read_text())
        else:
            metadata = {}
        
        # Ensure name is always set
        metadata['name'] = metadata.get('name', spec_dir.name)
        
        # Calculate completion rate
        tasks_file = spec_dir / 'tasks.md'
        if tasks_file.exists():
            try:
                tasks_content = tasks_file.read_text(encoding='utf-8')
                
                # Find all task headers and their completion status
                import re
                task_pattern = r'#### Task \d+:.*?\n(?:.*?\n)*?(?=#### Task|\Z)'
                tasks = re.findall(task_pattern, tasks_content, re.DOTALL)
                
                total_tasks = len(tasks)
                completed_tasks = 0
                
                for task in tasks:
                    # Count tasks with completion markers
                    # Check for ✅ in task headers or status lines
                    task_lines = task.split('\n')
                    for line in task_lines:
                        if line.startswith('**Status:**') and ('✅' in line or 'completed' in line.lower()):
                            completed_tasks += 1
                            break
                        elif line.startswith('#### Task') and '✅' in line:
                            completed_tasks += 1
                            break
                
                completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
                
            except (UnicodeDecodeError, Exception) as e:
                # Fallback for encoding issues
                completion_rate = 0
        else:
            completion_rate = 0
        
        metadata['completion_rate'] = completion_rate
        metadata['has_requirements'] = (spec_dir / 'requirements.md').exists()
        metadata['has_design'] = (spec_dir / 'design.md').exists()
        metadata['has_tasks'] = tasks_file.exists()
        
        return metadata
    
    def update_dashboard(self):
        """Update the status dashboard with error handling"""
        try:
            overview = self.get_status_overview()
            
            # Ensure meta directory exists
            self.meta_dir.mkdir(parents=True, exist_ok=True)
            
            dashboard_content = f"""# 📊 Specs Status Dashboard
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview
```
📋 Backlog:    {overview['backlog']['count']} specs
🎯 In Scope:   {overview['scope']['count']} specs
✅ Completed:  {overview['completed']['count']} specs
🧪 Sandbox:    {overview['sandbox']['count']} specs
❄️ Archived:   {overview['archived']['count']} specs
```

## 🎯 Active Development (Scope)
"""
            
            for spec in overview['scope']['specs']:
                completion = spec.get('completion_rate', 0)
                name = spec.get('name', 'Unknown')
                dashboard_content += f"- **{name}**: {completion:.0%} complete\n"
            
            if not overview['scope']['specs']:
                dashboard_content += "*No specs currently in scope*\n"
            
            dashboard_content += "\n## 📋 Next Up (Backlog)\n"
            
            for spec in overview['backlog']['specs'][:5]:  # Show top 5
                name = spec.get('name', 'Unknown')
                description = spec.get('description', 'No description')
                dashboard_content += f"- **{name}**: {description}\n"
            
            if len(overview['backlog']['specs']) > 5:
                dashboard_content += f"- *...and {len(overview['backlog']['specs']) - 5} more*\n"
            
            dashboard_content += f"""
## 📈 Metrics
- **Total Specs**: {sum(stage['count'] for stage in overview.values())}
- **Active Work**: {overview['scope']['count']} specs
- **Completion Rate**: {len([s for s in overview['scope']['specs'] if s.get('completion_rate', 0) > 0.5])} / {overview['scope']['count']} specs >50% complete
"""
            
            dashboard_file = self.meta_dir / 'status-dashboard.md'
            dashboard_file.write_text(dashboard_content, encoding='utf-8')
            
        except Exception as e:
            print(f"Warning: Could not update dashboard: {e}")
            # Don't fail the entire operation if dashboard update fails

class SpecTransaction:
    """Ensure atomic operations for spec management"""
    
    def __init__(self, spec_manager: SpecManager):
        self.manager = spec_manager
        self.rollback_actions = []
        self.created_dirs = []
        self.created_files = []
        self.moved_items = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Rollback on error
            print(f"Transaction failed: {exc_val}. Rolling back...")
            for action in reversed(self.rollback_actions):
                try:
                    action()
                except Exception as e:
                    print(f"Warning: Rollback action failed: {e}")
            
            # Clean up created files and directories
            for file_path in self.created_files:
                try:
                    if file_path.exists():
                        file_path.unlink()
                except:
                    pass
            
            for dir_path in self.created_dirs:
                try:
                    if dir_path.exists():
                        import shutil
                        shutil.rmtree(dir_path)
                except:
                    pass
    
    def track_file(self, file_path: Path):
        """Track a created file for potential rollback"""
        self.created_files.append(file_path)
    
    def track_dir(self, dir_path: Path):
        """Track a created directory for potential rollback"""
        self.created_dirs.append(dir_path)
    
    def move_spec(self, from_path: Path, to_path: Path):
        """Move spec with rollback capability"""
        from_path.rename(to_path)
        self.moved_items.append((from_path, to_path))
        self.rollback_actions.append(lambda: to_path.rename(from_path))

# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage specification lifecycle')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new spec')
    create_parser.add_argument('name', help='Spec name (kebab-case)')
    create_parser.add_argument('description', help='Spec description')
    create_parser.add_argument('--stage', choices=['backlog', 'scope'], default='backlog')
    
    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Promote spec to different stage')
    promote_parser.add_argument('name', help='Spec name')
    promote_parser.add_argument('--to', choices=['scope', 'completed', 'archived'], required=True)
    promote_parser.add_argument('--reason', help='Reason for promotion')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show status overview')
    status_parser.add_argument('--detailed', action='store_true')
    
    args = parser.parse_args()
    manager = SpecManager()
    
    if args.command == 'create':
        stage = SpecStage(args.stage)
        manager.create_spec(args.name, args.description, stage)
    
    elif args.command == 'promote':
        to_stage = SpecStage(args.to)
        manager.promote_spec(args.name, to_stage, args.reason or "")
    
    elif args.command == 'status':
        overview = manager.get_status_overview()
        print("SPECS OVERVIEW")
        print("=" * 50)
        
        for stage_name, stage_data in overview.items():
            icon = {'backlog': 'BACKLOG', 'scope': 'IN SCOPE', 'completed': 'COMPLETED', 'sandbox': 'SANDBOX', 'archived': 'ARCHIVED'}[stage_name]
            print(f"\n{icon} ({stage_data['count']} specs)")
            
            for spec in stage_data['specs']:
                name = spec.get('name', spec_dir.name if 'spec_dir' in locals() else 'Unknown')
                completion = spec.get('completion_rate', 0)
                if completion > 0:
                    print(f"  - {name} ({completion:.0%} complete)")
                else:
                    print(f"  - {name}")
        
        print(f"\nTotal: {sum(stage['count'] for stage in overview.values())} specifications")