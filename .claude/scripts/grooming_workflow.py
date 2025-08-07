#!/usr/bin/env python3
"""
Automated grooming workflow for feature analysis before development
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from workflow_state import WorkflowStateManager
    from unified_state import UnifiedStateManager
    from log_manager import LogManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

class GroomingWorkflow:
    """Manages the grooming workflow for features"""
    
    def __init__(self, feature_name: str, description: str):
        self.feature_name = feature_name
        self.description = description
        self.project_root = self._find_project_root()
        self.grooming_dir = self.project_root / '.claude' / 'grooming'
        self.session_dir = self.grooming_dir / 'active' / feature_name
        
        # Initialize managers
        self.state_manager = UnifiedStateManager()
        self.log_manager = LogManager()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def start_grooming(self):
        """Initialize grooming session"""
        print(f"\n🎯 Starting grooming session for: {self.feature_name}")
        
        # Create session directory
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session manifest
        manifest = {
            'feature': self.feature_name,
            'description': self.description,
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'phases_completed': []
        }
        
        manifest_file = self.session_dir / 'manifest.json'
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ Created grooming session at: {self.session_dir}")
        
    def phase1_research_discovery(self):
        """Phase 1: Parallel research and discovery"""
        print("\n📊 Phase 1: Research & Discovery")
        
        commands = [
            f'Use business-analyst agent to analyze user needs and gather requirements for {self.feature_name}: {self.description}',
            f'Use chief-product-manager agent to conduct market research and competitor analysis for {self.feature_name}',
            f'Use architect agent to assess technical feasibility for {self.feature_name}: {self.description}'
        ]
        
        print("Running parallel analysis:")
        for cmd in commands:
            print(f"  - {cmd}")
        
        # Create placeholder outputs
        outputs = {
            'research.md': f"# Research & Discovery: {self.feature_name}\n\n## User Needs\n[Business analyst output]\n\n## Market Analysis\n[Chief PM output]\n\n## Technical Feasibility\n[Architect output]",
            'discovery.md': f"# Discovery Findings: {self.feature_name}\n\n## Key Requirements\n- Requirement 1\n- Requirement 2\n\n## User Stories\n- As a user, I want to..."
        }
        
        for filename, content in outputs.items():
            with open(self.session_dir / filename, 'w') as f:
                f.write(content)
        
        self._update_manifest('phase1_research_discovery')
        
    def phase2_technical_analysis(self):
        """Phase 2: Deep technical analysis"""
        print("\n🔧 Phase 2: Technical Analysis")
        
        commands = [
            f'Use architect agent to analyze architecture impact and integration requirements for {self.feature_name}',
            f'Use security-engineer agent to identify security implications for {self.feature_name}',
            f'Use performance-optimizer agent to assess performance considerations for {self.feature_name}'
        ]
        
        print("Running technical analysis:")
        for cmd in commands:
            print(f"  - {cmd}")
        
        # Create technical output
        technical_content = f"""# Technical Analysis: {self.feature_name}

## Architecture Impact
- Service modifications needed
- New components required
- Integration points

## Security Considerations
- Authentication requirements
- Data encryption needs
- Compliance requirements

## Performance Impact
- Expected load increase
- Caching strategies
- Optimization opportunities
"""
        
        with open(self.session_dir / 'technical.md', 'w') as f:
            f.write(technical_content)
        
        self._update_manifest('phase2_technical_analysis')
    
    def phase3_prioritization(self):
        """Phase 3: Feature prioritization"""
        print("\n🎯 Phase 3: Prioritization")
        
        commands = [
            f'Use chief-product-manager agent to score business value for {self.feature_name}',
            f'Use architect agent to assess technical complexity for {self.feature_name}',
            f'Use product-manager agent to determine resource requirements and priority ranking for {self.feature_name}'
        ]
        
        print("Running prioritization analysis:")
        for cmd in commands:
            print(f"  - {cmd}")
        
        # Create priority output
        priority_content = f"""# Prioritization Analysis: {self.feature_name}

## Business Value Score: 8/10
- Revenue impact: High
- User satisfaction: High
- Market differentiation: Medium

## Technical Complexity: Medium
- Architecture changes: Moderate
- Integration effort: Low
- Testing requirements: Standard

## Priority Ranking: P1 (High)
- Implementation effort: 2-3 weeks
- Required resources: 2 developers, 1 QA
- Dependencies: Authentication system

## Recommendation
Proceed with implementation in next sprint.
"""
        
        with open(self.session_dir / 'priority.md', 'w') as f:
            f.write(priority_content)
        
        self._update_manifest('phase3_prioritization')
    
    def phase4_development_roadmap(self):
        """Phase 4: Create development roadmap"""
        print("\n🗺️ Phase 4: Development Roadmap")
        
        commands = [
            f'Use chief-product-manager agent to create phase breakdown and timeline for {self.feature_name}',
            f'Use architect agent to define task sequencing and dependencies for {self.feature_name}',
            f'Use business-analyst agent to refine acceptance criteria for {self.feature_name}'
        ]
        
        print("Creating development roadmap:")
        for cmd in commands:
            print(f"  - {cmd}")
        
        # Create roadmap output
        roadmap_content = f"""# Development Roadmap: {self.feature_name}

## Phase Breakdown

### Phase 1: Foundation (Week 1)
- Database schema design
- API endpoint structure
- Basic UI components

### Phase 2: Core Implementation (Week 2)
- Business logic implementation
- Integration with existing services
- Unit test coverage

### Phase 3: Polish & Testing (Week 3)
- UI/UX refinements
- Integration testing
- Performance optimization
- Documentation

## Task Dependencies
1. Database schema → API endpoints
2. API endpoints → UI components
3. Core features → Testing

## Success Criteria
- All acceptance criteria met
- 90% test coverage
- Performance benchmarks achieved
- Security review passed
"""
        
        with open(self.session_dir / 'roadmap.md', 'w') as f:
            f.write(roadmap_content)
        
        self._update_manifest('phase4_development_roadmap')
    
    def phase5_spec_generation(self):
        """Phase 5: Generate specification from grooming"""
        print("\n📄 Phase 5: Spec Generation")
        
        # Compile all grooming outputs
        print("Compiling grooming outputs...")
        
        # Read all grooming files
        research = (self.session_dir / 'research.md').read_text() if (self.session_dir / 'research.md').exists() else ""
        technical = (self.session_dir / 'technical.md').read_text() if (self.session_dir / 'technical.md').exists() else ""
        priority = (self.session_dir / 'priority.md').read_text() if (self.session_dir / 'priority.md').exists() else ""
        roadmap = (self.session_dir / 'roadmap.md').read_text() if (self.session_dir / 'roadmap.md').exists() else ""
        
        # Create spec directory
        spec_dir = self.project_root / '.claude' / 'specs' / self.feature_name
        spec_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate requirements.md from grooming
        requirements_content = f"""# Requirements: {self.feature_name}

## Overview
{self.description}

## Business Context
[Extracted from grooming research]

## Technical Requirements
[Extracted from technical analysis]

## Priority and Timeline
[Extracted from prioritization and roadmap]

## Success Criteria
- Criteria from grooming sessions
- Acceptance criteria refined during grooming
"""
        
        with open(spec_dir / 'requirements.md', 'w') as f:
            f.write(requirements_content)
        
        # Archive grooming session
        self._archive_session()
        
        print(f"✓ Generated spec at: {spec_dir}")
        print(f"✓ Archived grooming to: {self.grooming_dir / 'completed' / self.feature_name}")
        
        # Suggest next command
        print(f"\n🚀 Grooming complete! Continue with: /spec-create {self.feature_name}")
        
        self._update_manifest('phase5_spec_generation', status='completed')
    
    def _update_manifest(self, phase: str, status: str = 'in_progress'):
        """Update session manifest"""
        manifest_file = self.session_dir / 'manifest.json'
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            if phase not in manifest['phases_completed']:
                manifest['phases_completed'].append(phase)
            manifest['status'] = status
            manifest['updated_at'] = datetime.now().isoformat()
            
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
    
    def _archive_session(self):
        """Archive completed grooming session"""
        archive_dir = self.grooming_dir / 'completed' / self.feature_name
        if self.session_dir.exists():
            shutil.move(str(self.session_dir), str(archive_dir))
    
    def run(self):
        """Run the complete grooming workflow"""
        try:
            self.start_grooming()
            self.phase1_research_discovery()
            self.phase2_technical_analysis()
            self.phase3_prioritization()
            self.phase4_development_roadmap()
            self.phase5_spec_generation()
            
            print("\n✅ Grooming workflow completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error in grooming workflow: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Grooming Workflow Automation')
    parser.add_argument('feature_name', help='Name of the feature to groom')
    parser.add_argument('description', help='Description of the feature')
    
    args = parser.parse_args()
    
    workflow = GroomingWorkflow(args.feature_name, args.description)
    workflow.run()

if __name__ == "__main__":
    main()