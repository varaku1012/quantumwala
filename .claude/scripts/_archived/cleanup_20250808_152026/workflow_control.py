#!/usr/bin/env python3
"""
Workflow Control Command - Manual control over workflow execution
Replaces: workflow-start, workflow-continue, workflow-reset
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from unified_state import UnifiedStateManager
from workflow_state import WorkflowStateManager
from unified_workflow import UnifiedWorkflow, WorkflowMode, AutomationLevel, MonitoringLevel

class WorkflowControl:
    """
    Manual control interface for workflow execution
    """
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.state_manager = UnifiedStateManager(self.project_root)
        self.workflow_state = WorkflowStateManager()
        self.state_file = self.project_root / '.claude' / 'workflow_state.json'
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def start(self, description: str, spec_name: Optional[str] = None, **kwargs) -> Dict:
        """Start a new workflow"""
        # Check if workflow already in progress
        current_state = self.get_status()
        if current_state and current_state.get('status') == 'in_progress':
            return {
                'error': 'Workflow already in progress',
                'hint': 'Use "workflow-control continue" or "workflow-control reset"'
            }
        
        # Initialize new workflow state
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        initial_state = {
            'workflow_id': workflow_id,
            'description': description,
            'spec_name': spec_name or self._generate_spec_name(description),
            'status': 'in_progress',
            'current_phase': 'initialization',
            'phases_completed': [],
            'started_at': datetime.now().isoformat(),
            'options': kwargs
        }
        
        # Save state
        self._save_state(initial_state)
        
        # Start workflow with manual mode
        workflow = UnifiedWorkflow(
            mode=WorkflowMode(kwargs.get('mode', 'parallel')),
            auto=AutomationLevel.MANUAL,  # Force manual for control
            monitor=MonitoringLevel(kwargs.get('monitor', 'basic'))
        )
        
        print(f"✅ Workflow started: {workflow_id}")
        print(f"📋 Spec: {initial_state['spec_name']}")
        print(f"🎯 Description: {description}")
        print("\nUse 'workflow-control continue' to proceed to next phase")
        
        return initial_state
    
    def continue_workflow(self) -> Dict:
        """Continue paused workflow"""
        # Load current state
        state = self._load_state()
        
        if not state:
            return {'error': 'No workflow in progress', 'hint': 'Use "workflow-control start"'}
        
        if state.get('status') == 'completed':
            return {'error': 'Workflow already completed'}
        
        # Determine next phase
        phases = [
            'initialization',
            'spec_creation',
            'requirements',
            'design', 
            'tasks',
            'implementation',
            'testing',
            'review'
        ]
        
        completed = state.get('phases_completed', [])
        current_index = 0
        
        for i, phase in enumerate(phases):
            if phase not in completed:
                current_index = i
                break
        
        if current_index >= len(phases):
            state['status'] = 'completed'
            self._save_state(state)
            return {'message': 'All phases completed', 'state': state}
        
        next_phase = phases[current_index]
        
        print(f"📍 Current phase: {next_phase}")
        print(f"✅ Completed phases: {', '.join(completed)}")
        print(f"⏳ Executing phase: {next_phase}...")
        
        # Execute next phase
        try:
            # Create workflow with saved options
            workflow = UnifiedWorkflow(
                mode=WorkflowMode(state['options'].get('mode', 'parallel')),
                auto=AutomationLevel.MANUAL,
                monitor=MonitoringLevel(state['options'].get('monitor', 'basic'))
            )
            
            # Execute single phase
            context = {
                'workflow_id': state['workflow_id'],
                'spec_name': state['spec_name'],
                'phases_completed': completed
            }
            
            result = workflow._execute_phase(next_phase, state['spec_name'], context)
            
            if result.success:
                completed.append(next_phase)
                state['phases_completed'] = completed
                state['current_phase'] = phases[current_index + 1] if current_index + 1 < len(phases) else 'completed'
                
                if state['current_phase'] == 'completed':
                    state['status'] = 'completed'
                    state['completed_at'] = datetime.now().isoformat()
                
                self._save_state(state)
                
                print(f"✅ Phase {next_phase} completed successfully")
                
                if state['status'] == 'completed':
                    print("\n🎉 Workflow completed!")
                else:
                    print(f"\n⏭️ Next phase: {state['current_phase']}")
                    print("Use 'workflow-control continue' to proceed")
            else:
                print(f"❌ Phase {next_phase} failed: {result.error}")
                print("Options: retry with 'continue', skip phase, or 'reset'")
                state['last_error'] = result.error
                self._save_state(state)
            
            return state
            
        except Exception as e:
            return {'error': f'Phase execution failed: {str(e)}'}
    
    def pause(self) -> Dict:
        """Pause current workflow"""
        state = self._load_state()
        
        if not state:
            return {'error': 'No workflow in progress'}
        
        if state.get('status') == 'paused':
            return {'message': 'Workflow already paused'}
        
        state['status'] = 'paused'
        state['paused_at'] = datetime.now().isoformat()
        self._save_state(state)
        
        print("⏸️ Workflow paused")
        print("Use 'workflow-control continue' to resume")
        
        return state
    
    def reset(self) -> Dict:
        """Reset workflow state"""
        state = self._load_state()
        
        if state:
            # Archive current state
            archive_dir = self.project_root / '.claude' / 'workflow_archive'
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_file = archive_dir / f"{state['workflow_id']}.json"
            with open(archive_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            print(f"📦 Current workflow archived to: {archive_file}")
        
        # Clear current state
        if self.state_file.exists():
            self.state_file.unlink()
        
        print("🔄 Workflow state reset")
        print("Use 'workflow-control start' to begin new workflow")
        
        return {'message': 'Workflow reset successful'}
    
    def get_status(self) -> Optional[Dict]:
        """Get current workflow status"""
        state = self._load_state()
        
        if not state:
            print("ℹ️ No workflow in progress")
            print("Use 'workflow-control start' to begin")
            return None
        
        # Calculate duration
        started = datetime.fromisoformat(state['started_at'])
        if state.get('completed_at'):
            ended = datetime.fromisoformat(state['completed_at'])
            duration = (ended - started).total_seconds()
        else:
            duration = (datetime.now() - started).total_seconds()
        
        # Format output
        print("\n" + "="*60)
        print("WORKFLOW STATUS")
        print("="*60)
        print(f"ID: {state['workflow_id']}")
        print(f"Spec: {state['spec_name']}")
        print(f"Status: {state['status']}")
        print(f"Current Phase: {state.get('current_phase', 'unknown')}")
        print(f"Duration: {duration:.1f} seconds")
        
        if state.get('phases_completed'):
            print(f"\n✅ Completed Phases ({len(state['phases_completed'])}):")
            for phase in state['phases_completed']:
                print(f"  - {phase}")
        
        remaining_phases = self._get_remaining_phases(state)
        if remaining_phases:
            print(f"\n⏳ Remaining Phases ({len(remaining_phases)}):")
            for phase in remaining_phases:
                print(f"  - {phase}")
        
        if state.get('last_error'):
            print(f"\n❌ Last Error: {state['last_error']}")
        
        print("\n" + "="*60)
        
        return state
    
    def _get_remaining_phases(self, state: Dict) -> list:
        """Get list of remaining phases"""
        all_phases = [
            'initialization',
            'spec_creation',
            'requirements',
            'design',
            'tasks',
            'implementation',
            'testing',
            'review'
        ]
        
        completed = state.get('phases_completed', [])
        return [p for p in all_phases if p not in completed]
    
    def _save_state(self, state: Dict):
        """Save workflow state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_state(self) -> Optional[Dict]:
        """Load workflow state"""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _generate_spec_name(self, description: str) -> str:
        """Generate spec name from description"""
        import re
        words = re.findall(r'\b\w+\b', description.lower())
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'with', 'for'}
        meaningful = [w for w in words if w not in stop_words and len(w) > 2]
        return '-'.join(meaningful[:4]) if meaningful else 'custom-feature'


def main():
    """CLI interface for workflow control"""
    parser = argparse.ArgumentParser(description='Workflow Control Command')
    
    subparsers = parser.add_subparsers(dest='action', help='Control action')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start new workflow')
    start_parser.add_argument('description', help='What to build')
    start_parser.add_argument('--spec-name', help='Optional spec name')
    start_parser.add_argument('--mode', 
                            choices=['sequential', 'parallel', 'optimized'],
                            default='parallel')
    start_parser.add_argument('--monitor',
                            choices=['none', 'basic', 'full'],
                            default='basic')
    
    # Other commands
    subparsers.add_parser('continue', help='Continue workflow')
    subparsers.add_parser('pause', help='Pause workflow')
    subparsers.add_parser('reset', help='Reset workflow')
    subparsers.add_parser('status', help='Get workflow status')
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    control = WorkflowControl()
    
    if args.action == 'start':
        result = control.start(
            args.description,
            args.spec_name,
            mode=args.mode,
            monitor=args.monitor
        )
    elif args.action == 'continue':
        result = control.continue_workflow()
    elif args.action == 'pause':
        result = control.pause()
    elif args.action == 'reset':
        result = control.reset()
    elif args.action == 'status':
        result = control.get_status()
    
    if result and result.get('error'):
        print(f"❌ Error: {result['error']}")
        if result.get('hint'):
            print(f"💡 Hint: {result['hint']}")
        sys.exit(1)


if __name__ == "__main__":
    main()