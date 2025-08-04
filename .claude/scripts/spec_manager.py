#!/usr/bin/env python3
"""
Comprehensive spec lifecycle management
"""

import json
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
    
    def ensure_structure(self):
        """Ensure proper directory structure exists"""
        for stage in SpecStage:
            (self.specs_root / stage.value).mkdir(parents=True, exist_ok=True)
        self.meta_dir.mkdir(parents=True, exist_ok=True)
    
    def create_spec(self, name: str, description: str, stage: SpecStage = SpecStage.BACKLOG) -> bool:
        """Create new specification"""
        spec_dir = self.specs_root / stage.value / name
        
        if spec_dir.exists():
            print(f"❌ Spec '{name}' already exists in {stage.value}")
            return False
        
        spec_dir.mkdir(parents=True)
        
        # Create metadata
        metadata = {
            'name': name,
            'description': description,
            'stage': stage.value,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'completion_rate': 0.0,
            'priority': 'medium',
            'tags': [],
            'assignee': None
        }
        
        (spec_dir / '_meta.json').write_text(json.dumps(metadata, indent=2))
        
        # Create overview
        overview_content = f"""# {name.replace('-', ' ').title()}

**Status**: {stage.value.title()}  
**Created**: {datetime.now().strftime('%Y-%m-%d')}  
**Description**: {description}

## Overview
{description}

## Success Criteria
- [ ] Define success criteria

## Next Steps
- [ ] Define next steps based on stage
"""
        (spec_dir / 'overview.md').write_text(overview_content)
        
        # Create README
        readme_content = f"""# {name}

Quick reference for the {name} specification.

**Stage**: {stage.value}  
**Description**: {description}

## Files
- `overview.md` - Feature overview and success criteria
- `_meta.json` - Specification metadata
"""
        (spec_dir / 'README.md').write_text(readme_content)
        
        self.update_dashboard()
        print(f"Created spec '{name}' in {stage.value}")
        return True
    
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
                completed_tasks = tasks_content.count('✅')
                total_tasks = tasks_content.count('#### Task')
                completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
            except UnicodeDecodeError:
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
        """Update the status dashboard"""
        overview = self.get_status_overview()
        
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
        
        (self.meta_dir / 'status-dashboard.md').write_text(dashboard_content)

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