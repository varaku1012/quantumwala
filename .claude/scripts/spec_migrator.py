#!/usr/bin/env python3
"""
Migrate existing specs to new structured organization
"""

import shutil
from pathlib import Path
import json
from datetime import datetime

class SpecMigrator:
    def __init__(self):
        self.specs_root = Path('.claude/specs')
        self.new_structure = {
            'backlog': [],
            'scope': [],
            'completed': [],
            'sandbox': [],
            'archived': []
        }
    
    def analyze_existing_specs(self):
        """Analyze current specs and suggest categorization"""
        existing_specs = []
        
        # Skip structure directories
        structure_dirs = {'backlog', 'scope', 'completed', 'sandbox', 'archived', '_meta'}
        
        for spec_dir in self.specs_root.iterdir():
            if spec_dir.is_dir() and spec_dir.name not in structure_dirs:
                spec_info = self.analyze_spec(spec_dir)
                existing_specs.append(spec_info)
        
        return existing_specs
    
    def analyze_spec(self, spec_dir):
        """Analyze individual spec to determine its status"""
        spec_name = spec_dir.name
        
        # Check for completion indicators
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
        
        # Determine suggested category
        if spec_name.startswith('test-'):
            suggested_category = 'sandbox'
        elif completion_rate >= 0.9:
            suggested_category = 'completed'
        elif completion_rate > 0:
            suggested_category = 'scope'
        else:
            suggested_category = 'backlog'
        
        return {
            'name': spec_name,
            'path': spec_dir,
            'completion_rate': completion_rate,
            'suggested_category': suggested_category,
            'has_tasks': tasks_file.exists(),
            'has_requirements': (spec_dir / 'requirements.md').exists(),
            'has_design': (spec_dir / 'design.md').exists()
        }
    
    def migrate_specs(self, categorization_plan):
        """Execute the migration based on categorization plan"""
        # Create new structure
        for category in ['backlog', 'scope', 'completed', 'sandbox', 'archived', '_meta']:
            (self.specs_root / category).mkdir(exist_ok=True)
        
        # Move specs to their new locations
        for spec_name, category in categorization_plan.items():
            old_path = self.specs_root / spec_name
            new_path = self.specs_root / category / spec_name
            
            if old_path.exists():
                shutil.move(str(old_path), str(new_path))
                print(f"Moved {spec_name} -> {category}/")
        
        # Create meta files
        self.create_meta_files()
    
    def create_meta_files(self):
        """Create management and status files"""
        meta_dir = self.specs_root / '_meta'
        
        # Create roadmap
        roadmap_content = """# Product Roadmap

## Current Sprint (Scope)
- [ ] Features currently in development

## Next Sprint (Backlog - High Priority)  
- [ ] Features ready for development

## Future Releases (Backlog - Future)
- [ ] Features for later consideration

## Completed Features
- [x] Features that are done and deployed
"""
        (meta_dir / 'roadmap.md').write_text(roadmap_content)
        
        # Create status dashboard
        self.create_status_dashboard()
    
    def create_status_dashboard(self):
        """Create a visual status dashboard"""
        dashboard_content = f"""# Specs Status Dashboard
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Overview
```
Backlog:    {len(list((self.specs_root / 'backlog').iterdir()))} specs
In Scope:   {len(list((self.specs_root / 'scope').iterdir()))} specs  
Completed:  {len(list((self.specs_root / 'completed').iterdir()))} specs
Sandbox:    {len(list((self.specs_root / 'sandbox').iterdir()))} specs
```

## Active Development (Scope)
"""
        
        # Add active specs
        scope_dir = self.specs_root / 'scope'
        if scope_dir.exists():
            for spec_dir in scope_dir.iterdir():
                if spec_dir.is_dir():
                    dashboard_content += f"- **{spec_dir.name}**: In progress\n"
        
        dashboard_content += "\n## Next Up (Backlog)\n"
        
        # Add backlog specs  
        backlog_dir = self.specs_root / 'backlog'
        if backlog_dir.exists():
            for spec_dir in backlog_dir.iterdir():
                if spec_dir.is_dir():
                    dashboard_content += f"- **{spec_dir.name}**: Ready for development\n"
        
        (self.specs_root / '_meta' / 'status-dashboard.md').write_text(dashboard_content)

if __name__ == "__main__":
    migrator = SpecMigrator()
    
    print("Analyzing existing specs...")
    existing_specs = migrator.analyze_existing_specs()
    
    print("\nSuggested categorization:")
    categorization_plan = {}
    for spec in existing_specs:
        print(f"  {spec['name']} -> {spec['suggested_category']} ({spec['completion_rate']:.0%} complete)")
        categorization_plan[spec['name']] = spec['suggested_category']
    
    print(f"\nMigrating {len(existing_specs)} specs to new structure...")
    migrator.migrate_specs(categorization_plan)
    
    print("Migration complete!")
    print("Check .claude/specs/_meta/status-dashboard.md for overview")