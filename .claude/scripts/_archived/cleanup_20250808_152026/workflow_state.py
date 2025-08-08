#!/usr/bin/env python3
"""
Workflow state management for continuous execution
"""

import json
import os
from pathlib import Path
from datetime import datetime
from enum import Enum

class WorkflowPhase(Enum):
    INIT = "initialization"
    STEERING = "steering_setup"
    SPEC_CREATE = "spec_creation"
    REQUIREMENTS = "requirements_generation"
    DESIGN = "design_creation"
    TASKS = "task_generation"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    COMPLETE = "complete"

class WorkflowState:
    def __init__(self, spec_name=None):
        self.spec_name = spec_name
        self.project_root = self._find_project_root()
        self.state_file = self.project_root / '.claude' / 'workflow_state.json'
        self.state = self._load_state()
    
    def _find_project_root(self):
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_state(self):
        """Load workflow state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return self._init_state()
    
    def _init_state(self):
        """Initialize new workflow state"""
        return {
            'current_phase': WorkflowPhase.INIT.value,
            'spec_name': self.spec_name,
            'phases_completed': [],
            'current_tasks': [],
            'errors': [],
            'started_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Save workflow state to file"""
        self.state['last_updated'] = datetime.now().isoformat()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_current_phase(self):
        """Get current workflow phase"""
        return WorkflowPhase(self.state['current_phase'])
    
    def complete_phase(self, phase):
        """Mark a phase as complete and determine next phase"""
        self.state['phases_completed'].append({
            'phase': phase.value,
            'completed_at': datetime.now().isoformat()
        })
        
        # Determine next phase
        phase_sequence = [
            WorkflowPhase.INIT,
            WorkflowPhase.STEERING,
            WorkflowPhase.SPEC_CREATE,
            WorkflowPhase.REQUIREMENTS,
            WorkflowPhase.DESIGN,
            WorkflowPhase.TASKS,
            WorkflowPhase.IMPLEMENTATION,
            WorkflowPhase.VALIDATION,
            WorkflowPhase.COMPLETE
        ]
        
        current_index = phase_sequence.index(phase)
        if current_index < len(phase_sequence) - 1:
            next_phase = phase_sequence[current_index + 1]
            self.state['current_phase'] = next_phase.value
        else:
            self.state['current_phase'] = WorkflowPhase.COMPLETE.value
        
        self._save_state()
        return self.get_current_phase()
    
    def get_next_command(self):
        """Get the next command to execute based on current phase"""
        phase = self.get_current_phase()
        spec = self.state.get('spec_name', 'feature')
        
        commands = {
            WorkflowPhase.INIT: '/project-init',
            WorkflowPhase.STEERING: '/steering-setup',
            WorkflowPhase.SPEC_CREATE: f'/spec-create "{spec}" "Feature implementation"',
            WorkflowPhase.REQUIREMENTS: '/spec-requirements',
            WorkflowPhase.DESIGN: '/spec-design',
            WorkflowPhase.TASKS: '/spec-tasks',
            WorkflowPhase.IMPLEMENTATION: '/spec-orchestrate',
            WorkflowPhase.VALIDATION: '/spec-review',
            WorkflowPhase.COMPLETE: None
        }
        
        return commands.get(phase)
    
    def add_error(self, phase, error):
        """Log an error for a phase"""
        self.state['errors'].append({
            'phase': phase.value,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        self._save_state()
    
    def should_continue(self):
        """Check if workflow should continue"""
        return self.get_current_phase() != WorkflowPhase.COMPLETE
    
    def get_progress(self):
        """Get workflow progress percentage"""
        total_phases = len(WorkflowPhase) - 1  # Exclude COMPLETE
        completed = len(self.state['phases_completed'])
        return int((completed / total_phases) * 100)
    
    def detect_current_state(self):
        """Detect current state by examining project files"""
        # Check for steering documents
        steering_dir = self.project_root / '.claude' / 'steering'
        if not steering_dir.exists() or not list(steering_dir.glob('*.md')):
            return WorkflowPhase.STEERING
        
        # Check for specifications
        specs_dir = self.project_root / '.claude' / 'specs'
        if not specs_dir.exists() or not list(specs_dir.glob('*')):
            return WorkflowPhase.SPEC_CREATE
        
        # Check specific spec
        if self.spec_name:
            spec_dir = specs_dir / self.spec_name
            if not spec_dir.exists():
                return WorkflowPhase.SPEC_CREATE
            
            # Check for requirements
            if not (spec_dir / 'requirements.md').exists():
                return WorkflowPhase.REQUIREMENTS
            
            # Check for design
            if not (spec_dir / 'design.md').exists():
                return WorkflowPhase.DESIGN
            
            # Check for tasks
            if not (spec_dir / 'tasks.md').exists():
                return WorkflowPhase.TASKS
            
            # Check task completion
            tasks_file = spec_dir / 'tasks.md'
            if tasks_file.exists():
                content = tasks_file.read_text()
                if '- [ ]' in content:
                    return WorkflowPhase.IMPLEMENTATION
                else:
                    return WorkflowPhase.VALIDATION
        
        return WorkflowPhase.COMPLETE


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Workflow state management')
    parser.add_argument('--spec-name', help='Specification name')
    parser.add_argument('--get-current', action='store_true', help='Get current phase')
    parser.add_argument('--get-next', action='store_true', help='Get next command')
    parser.add_argument('--complete-phase', help='Mark phase as complete')
    parser.add_argument('--detect', action='store_true', help='Detect current state')
    parser.add_argument('--progress', action='store_true', help='Show progress')
    
    args = parser.parse_args()
    
    state = WorkflowState(args.spec_name)
    
    if args.detect:
        detected = state.detect_current_state()
        print(f"Detected phase: {detected.value}")
        state.state['current_phase'] = detected.value
        state._save_state()
    
    if args.get_current:
        print(state.get_current_phase().value)
    
    if args.get_next:
        cmd = state.get_next_command()
        if cmd:
            print(cmd)
    
    if args.complete_phase:
        phase = WorkflowPhase(args.complete_phase)
        next_phase = state.complete_phase(phase)
        print(f"Next phase: {next_phase.value}")
    
    if args.progress:
        print(f"Progress: {state.get_progress()}%")


if __name__ == '__main__':
    main()