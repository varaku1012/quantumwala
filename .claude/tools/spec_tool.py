#!/usr/bin/env python3
"""Custom spec management tool for agents"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SpecTool:
    def __init__(self):
        self.specs_dir = Path('.claude/specs')
        self.specs_dir.mkdir(parents=True, exist_ok=True)
    
    def create(self, name: str, description: str) -> Dict:
        """Create a new specification structure"""
        spec_dir = self.specs_dir / name
        
        if spec_dir.exists():
            return {"error": f"Spec '{name}' already exists"}
        
        # Create directory structure
        spec_dir.mkdir(parents=True)
        
        # Create initial files
        files = {
            'overview.md': f"""# {name.replace('-', ' ').title()}

## Description
{description}

## Status
Created: {datetime.now().isoformat()}
Status: Draft

## Objectives
- [ ] Define requirements
- [ ] Create design
- [ ] Generate tasks
- [ ] Implement features
- [ ] Validate quality
""",
            'requirements.md': f"""# Requirements - {name}

## Functional Requirements
<!-- To be filled by business-analyst -->

## Non-Functional Requirements
<!-- To be filled by architect -->

## User Stories
<!-- To be filled by product-manager -->
""",
            'design.md': f"""# Design - {name}

## Architecture
<!-- To be filled by architect -->

## UI/UX Design
<!-- To be filled by uiux-designer -->

## Data Model
<!-- To be filled by data-engineer -->

## Security Considerations
<!-- To be filled by security-engineer -->
""",
            'tasks.md': f"""# Tasks - {name}

## Phase 1: Setup
- [ ] 1.1. Initialize project structure
- [ ] 1.2. Set up development environment

## Phase 2: Implementation
<!-- To be generated -->

## Phase 3: Testing
<!-- To be generated -->

## Phase 4: Deployment
<!-- To be generated -->
""",
            'status.md': f"""# Status - {name}

## Current Phase
Planning

## Progress
- [x] Specification created
- [ ] Requirements gathered
- [ ] Design completed
- [ ] Tasks generated
- [ ] Implementation started
- [ ] Testing completed
- [ ] Deployed

## Last Updated
{datetime.now().isoformat()}
"""
        }
        
        for filename, content in files.items():
            (spec_dir / filename).write_text(content)
        
        return {
            "created": True,
            "spec": name,
            "path": str(spec_dir),
            "files": list(files.keys())
        }
    
    def validate(self, spec_name: str) -> Dict:
        """Validate spec completeness"""
        spec_dir = self.specs_dir / spec_name
        
        if not spec_dir.exists():
            return {"error": f"Spec '{spec_name}' not found"}
        
        required_files = ['overview.md', 'requirements.md', 'design.md', 'tasks.md', 'status.md']
        issues = []
        completeness = {}
        
        for file in required_files:
            file_path = spec_dir / file
            if not file_path.exists():
                issues.append(f"Missing required file: {file}")
                completeness[file] = False
            else:
                content = file_path.read_text()
                # Check if file has meaningful content (not just template)
                if '<!-- To be' in content or len(content.strip()) < 100:
                    issues.append(f"Incomplete content in: {file}")
                    completeness[file] = False
                else:
                    completeness[file] = True
        
        # Calculate overall completeness
        complete_count = sum(1 for v in completeness.values() if v)
        total_count = len(completeness)
        completeness_percent = (complete_count / total_count) * 100
        
        return {
            "valid": len(issues) == 0,
            "completeness": f"{completeness_percent:.0f}%",
            "files": completeness,
            "issues": issues
        }
    
    def generate_tasks(self, spec_name: str) -> Dict:
        """Generate tasks from requirements and design"""
        spec_dir = self.specs_dir / spec_name
        
        if not spec_dir.exists():
            return {"error": f"Spec '{spec_name}' not found"}
        
        # Read requirements and design
        req_file = spec_dir / 'requirements.md'
        design_file = spec_dir / 'design.md'
        
        if not req_file.exists() or not design_file.exists():
            return {"error": "Requirements and design must exist before generating tasks"}
        
        requirements = req_file.read_text()
        design = design_file.read_text()
        
        # Generate tasks based on content (simplified for demo)
        tasks = []
        task_id = 2.1  # Start after setup phase
        
        # Backend tasks
        if 'api' in requirements.lower() or 'backend' in design.lower():
            tasks.append(f"- [ ] {task_id}. Create API endpoints")
            task_id += 0.1
            tasks.append(f"- [ ] {task_id}. Implement business logic")
            task_id += 0.1
            tasks.append(f"- [ ] {task_id}. Add data validation")
            task_id += 0.1
        
        # Frontend tasks
        if 'ui' in requirements.lower() or 'frontend' in design.lower():
            tasks.append(f"- [ ] {task_id}. Create UI components")
            task_id += 0.1
            tasks.append(f"- [ ] {task_id}. Implement user interactions")
            task_id += 0.1
            tasks.append(f"- [ ] {task_id}. Add responsive design")
            task_id += 0.1
        
        # Database tasks
        if 'data' in requirements.lower() or 'database' in design.lower():
            tasks.append(f"- [ ] {task_id}. Design database schema")
            task_id += 0.1
            tasks.append(f"- [ ] {task_id}. Create migrations")
            task_id += 0.1
            tasks.append(f"- [ ] {task_id}. Add indexes and constraints")
            task_id += 0.1
        
        # Testing tasks
        tasks.append(f"- [ ] 3.1. Write unit tests")
        tasks.append(f"- [ ] 3.2. Write integration tests")
        tasks.append(f"- [ ] 3.3. Perform security testing")
        tasks.append(f"- [ ] 3.4. Conduct performance testing")
        
        # Update tasks file
        tasks_file = spec_dir / 'tasks.md'
        current_content = tasks_file.read_text()
        
        # Replace the implementation phase section
        new_content = current_content.replace(
            "## Phase 2: Implementation\n<!-- To be generated -->",
            f"## Phase 2: Implementation\n" + "\n".join(tasks)
        )
        
        tasks_file.write_text(new_content)
        
        return {
            "generated": True,
            "spec": spec_name,
            "task_count": len(tasks),
            "tasks": tasks
        }
    
    def update_status(self, spec_name: str, phase: str, progress: Dict = None) -> Dict:
        """Update spec status"""
        spec_dir = self.specs_dir / spec_name
        
        if not spec_dir.exists():
            return {"error": f"Spec '{spec_name}' not found"}
        
        status_file = spec_dir / 'status.md'
        
        # Read current status
        if status_file.exists():
            lines = status_file.read_text().split('\n')
        else:
            lines = []
        
        # Update phase
        phase_updated = False
        for i, line in enumerate(lines):
            if line.startswith('## Current Phase'):
                if i + 1 < len(lines):
                    lines[i + 1] = phase
                    phase_updated = True
                break
        
        if not phase_updated:
            lines.append(f"## Current Phase\n{phase}")
        
        # Update progress if provided
        if progress:
            progress_section = []
            progress_section.append("## Progress")
            for item, completed in progress.items():
                marker = "x" if completed else " "
                progress_section.append(f"- [{marker}] {item}")
            
            # Find and replace progress section
            progress_start = -1
            progress_end = -1
            for i, line in enumerate(lines):
                if line.startswith('## Progress'):
                    progress_start = i
                elif progress_start >= 0 and line.startswith('##'):
                    progress_end = i
                    break
            
            if progress_start >= 0:
                if progress_end < 0:
                    progress_end = len(lines)
                lines[progress_start:progress_end] = progress_section
        
        # Update timestamp
        timestamp_updated = False
        for i, line in enumerate(lines):
            if line.startswith('## Last Updated'):
                if i + 1 < len(lines):
                    lines[i + 1] = datetime.now().isoformat()
                    timestamp_updated = True
                break
        
        if not timestamp_updated:
            lines.append(f"## Last Updated\n{datetime.now().isoformat()}")
        
        # Write updated status
        status_file.write_text('\n'.join(lines))
        
        return {
            "updated": True,
            "spec": spec_name,
            "phase": phase,
            "timestamp": datetime.now().isoformat()
        }
    
    def list_specs(self) -> Dict:
        """List all specifications"""
        specs = []
        
        for spec_dir in self.specs_dir.iterdir():
            if spec_dir.is_dir() and not spec_dir.name.startswith('.'):
                # Get basic info
                status_file = spec_dir / 'status.md'
                phase = "Unknown"
                
                if status_file.exists():
                    content = status_file.read_text()
                    for line in content.split('\n'):
                        if prev_line and prev_line.startswith('## Current Phase'):
                            phase = line.strip()
                            break
                        prev_line = line
                
                specs.append({
                    "name": spec_dir.name,
                    "path": str(spec_dir),
                    "phase": phase,
                    "files": len(list(spec_dir.glob('*.md')))
                })
        
        return {
            "specs": specs,
            "count": len(specs)
        }

def main():
    """CLI interface for spec tool"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)
    
    tool = SpecTool()
    command = sys.argv[1]
    
    try:
        if command == "create":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "Usage: create <name> <description>"}))
                sys.exit(1)
            
            name = sys.argv[2]
            description = ' '.join(sys.argv[3:])
            result = tool.create(name, description)
            
        elif command == "validate":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: validate <spec_name>"}))
                sys.exit(1)
            
            result = tool.validate(sys.argv[2])
            
        elif command == "generate_tasks":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: generate_tasks <spec_name>"}))
                sys.exit(1)
            
            result = tool.generate_tasks(sys.argv[2])
            
        elif command == "update_status":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "Usage: update_status <spec_name> <phase>"}))
                sys.exit(1)
            
            spec_name = sys.argv[2]
            phase = sys.argv[3]
            # Could parse additional progress data from argv[4] if provided
            result = tool.update_status(spec_name, phase)
            
        elif command == "list":
            result = tool.list_specs()
            
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()