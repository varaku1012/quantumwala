#!/usr/bin/env python3
"""
Unified state management system
Single source of truth for all workflow state
"""

import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class WorkflowPhase(Enum):
    INITIALIZATION = "initialization"
    STEERING_SETUP = "steering_setup"
    SPEC_CREATION = "spec_creation"
    REQUIREMENTS_GENERATION = "requirements_generation"
    DESIGN_CREATION = "design_creation"
    TASK_GENERATION = "task_generation"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    COMPLETE = "complete"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class TaskState:
    id: str
    spec_name: str
    status: TaskStatus
    agent: str
    description: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0

@dataclass
class AgentPerformance:
    name: str
    executions: int = 0
    successes: int = 0
    failures: int = 0
    total_duration: float = 0.0
    average_duration: float = 0.0
    last_execution: Optional[datetime] = None

@dataclass
class SpecificationState:
    name: str
    current_phase: WorkflowPhase
    created_at: datetime
    tasks: Dict[str, TaskState]
    completed_phases: List[Dict[str, Any]]
    progress_percentage: float = 0.0

class UnifiedStateManager:
    """Unified state management for the entire Quantumwala system"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.state_file = self.claude_dir / 'unified_state.json'
        
        # Thread safety
        self._lock = threading.RLock()
        
        self.setup_logging()
        
        # State structure
        self.state = self._load_state()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def setup_logging(self):
        """Setup state manager logging"""
        log_dir = self.claude_dir / 'logs' / 'state'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'state_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def save_state(self):
        """Public method to save state with thread safety"""
        with self._lock:
            self._atomic_save_state()
    
    def create_state_backup(self, backup_name: str = None) -> str:
        """Create a backup of current state"""
        with self._lock:
            if backup_name is None:
                backup_name = f"state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            backup_dir = self.claude_dir / 'backups' / 'state'
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / backup_name
            
            try:
                with open(backup_path, 'w') as f:
                    json.dump(self.state, f, indent=2, default=str)
                self.logger.info(f"State backup created: {backup_name}")
                return str(backup_path)
            except Exception as e:
                self.logger.error(f"Failed to create state backup: {e}")
                raise
    
    def restore_state_from_backup(self, backup_path: str) -> bool:
        """Restore state from backup"""
        with self._lock:
            try:
                backup_file = Path(backup_path)
                if not backup_file.exists():
                    self.logger.error(f"Backup file not found: {backup_path}")
                    return False
                
                with open(backup_file, 'r') as f:
                    backup_state = json.load(f)
                
                if self._validate_state_structure(backup_state):
                    # Create backup of current state before restore
                    self.create_state_backup("pre_restore_backup.json")
                    
                    self.state = backup_state
                    self._atomic_save_state()
                    self.logger.info(f"State restored from backup: {backup_path}")
                    return True
                else:
                    self.logger.error(f"Invalid backup state structure: {backup_path}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Failed to restore from backup: {e}")
                return False
    
    def _load_state(self) -> Dict:
        """Load unified state from file with corruption detection"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    loaded_state = json.load(f)
                    
                # Basic validation
                if self._validate_state_structure(loaded_state):
                    self.logger.info("Unified state loaded from file")
                    return loaded_state
                else:
                    self.logger.warning("State file structure invalid, reinitializing")
                    self._backup_corrupted_state()
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"State file corrupted (JSON error): {e}")
                self._backup_corrupted_state()
            except Exception as e:
                self.logger.error(f"Error loading state: {e}")
                self._backup_corrupted_state()
        
        return self._initialize_state()
    
    def _validate_state_structure(self, state: Dict) -> bool:
        """Validate state file structure"""
        required_keys = ['session', 'workflow', 'specifications', 'agents', 'resources']
        return all(key in state for key in required_keys)
    
    def _backup_corrupted_state(self):
        """Backup corrupted state file for debugging"""
        if self.state_file.exists():
            backup_name = f"unified_state_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.state_file.parent / backup_name
            try:
                self.state_file.rename(backup_path)
                self.logger.info(f"Corrupted state backed up to {backup_name}")
            except Exception as e:
                self.logger.error(f"Failed to backup corrupted state: {e}")
    
    def _initialize_state(self) -> Dict:
        """Initialize new unified state"""
        initial_state = {
            'session': {
                'started_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'version': '1.0.0'
            },
            'workflow': {
                'current_spec': None,
                'global_phase': 'initialization',
                'auto_progression': True
            },
            'specifications': {},
            'agents': {
                'performance': {},
                'active_tasks': {},
                'total_executions': 0
            },
            'resources': {
                'peak_concurrent_tasks': 0,
                'total_tasks_executed': 0,
                'system_stats': []
            },
            'errors': [],
            'commands': {
                'total_executed': 0,
                'recent_commands': []
            }
        }
        
        self.logger.info("Initialized new unified state")
        return initial_state
    
    def _atomic_save_state(self):
        """Save state atomically to prevent corruption"""
        try:
            # Create temporary file
            temp_file = self.state_file.with_suffix('.tmp')
            
            # Update timestamp
            self.state['session']['last_updated'] = datetime.now().isoformat()
            
            # Write to temporary file
            with open(temp_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            
            # Atomic replace (works on both Windows and Unix)
            temp_file.replace(self.state_file)
            
            self.logger.debug("State saved atomically")
            
        except Exception as e:
            self.logger.error(f"Error saving state atomically: {e}")
            # Clean up temp file if it exists
            temp_file = self.state_file.with_suffix('.tmp')
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
    
    def _save_state(self):
        """Save state atomically"""
        with self._lock:
            # Update timestamp
            self.state['session']['last_updated'] = datetime.now().isoformat()
            
            # Create temporary file for atomic write
            temp_file = self.state_file.with_suffix('.tmp')
            
            try:
                with open(temp_file, 'w') as f:
                    json.dump(self.state, f, indent=2, default=str)
                
                # Atomic move
                temp_file.replace(self.state_file)
                
            except Exception as e:
                self.logger.error(f"Error saving state: {e}")
                if temp_file.exists():
                    temp_file.unlink()
    
    def create_specification(self, name: str, description: str = "") -> bool:
        """Create a new specification and set it as current"""
        with self._lock:
            if name in self.state['specifications']:
                self.logger.warning(f"Specification {name} already exists")
                return False
            
            spec_state = {
                'name': name,
                'description': description,
                'current_phase': WorkflowPhase.INITIALIZATION.value,
                'created_at': datetime.now().isoformat(),
                'tasks': {},
                'completed_phases': [],
                'progress_percentage': 0.0,
                'files': {
                    'requirements': None,
                    'design': None,
                    'tasks': None
                }
            }
            
            self.state['specifications'][name] = spec_state
            self.state['workflow']['current_spec'] = name
            
            self._save_state()
            self.logger.info(f"Created specification: {name}")
            return True
    
    def update_workflow_phase(self, new_phase: str, spec_name: str = None):
        """Update workflow phase with validation"""
        with self._lock:
            if spec_name is None:
                spec_name = self.state['workflow']['current_spec']
            
            if not spec_name or spec_name not in self.state['specifications']:
                self.logger.error(f"Cannot update phase: spec {spec_name} not found")
                return False
            
            spec = self.state['specifications'][spec_name]
            old_phase = spec['current_phase']
            
            # Add to completed phases
            spec['completed_phases'].append({
                'phase': old_phase,
                'completed_at': datetime.now().isoformat()
            })
            
            # Update current phase
            spec['current_phase'] = new_phase
            
            # Update progress
            phase_list = [p.value for p in WorkflowPhase]
            if new_phase in phase_list:
                completed_count = len(spec['completed_phases'])
                total_phases = len(phase_list) - 1  # Exclude initialization
                spec['progress_percentage'] = min(100, (completed_count / total_phases) * 100)
            
            self._save_state()
            self.logger.info(f"Updated phase for {spec_name}: {old_phase} → {new_phase}")
            return True
    
    def add_task(self, spec_name: str, task_id: str, description: str, 
                 agent: str, status: TaskStatus = TaskStatus.PENDING) -> bool:
        """Add a task to specification"""
        with self._lock:
            if spec_name not in self.state['specifications']:
                self.logger.error(f"Specification {spec_name} not found")
                return False
            
            task_state = {
                'id': task_id,
                'spec_name': spec_name,
                'status': status.value,
                'agent': agent,
                'description': description,
                'started_at': None,
                'completed_at': None,
                'error': None,
                'duration_seconds': 0.0
            }
            
            self.state['specifications'][spec_name]['tasks'][task_id] = task_state
            self._save_state()
            
            self.logger.info(f"Added task {task_id} to {spec_name}")
            return True
    
    def update_task_status(self, spec_name: str, task_id: str, 
                          status: TaskStatus, error: str = None) -> bool:
        """Update task status"""
        with self._lock:
            if (spec_name not in self.state['specifications'] or 
                task_id not in self.state['specifications'][spec_name]['tasks']):
                self.logger.error(f"Task {task_id} in spec {spec_name} not found")
                return False
            
            task = self.state['specifications'][spec_name]['tasks'][task_id]
            old_status = task['status']
            
            # Update status
            task['status'] = status.value
            
            # Handle status-specific updates
            if status == TaskStatus.IN_PROGRESS and old_status == TaskStatus.PENDING.value:
                task['started_at'] = datetime.now().isoformat()
                
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task['completed_at'] = datetime.now().isoformat()
                
                # Calculate duration
                if task['started_at']:
                    start_time = datetime.fromisoformat(task['started_at'])
                    duration = (datetime.now() - start_time).total_seconds()
                    task['duration_seconds'] = duration
                
                if error:
                    task['error'] = error
                
                # Update resource statistics
                self.state['resources']['total_tasks_executed'] += 1
            
            self._save_state()
            self.logger.info(f"Updated task {task_id} status: {old_status} → {status.value}")
            return True
    
    def track_agent_execution(self, agent_name: str, duration: float, 
                            success: bool, spec_name: str = None):
        """Track agent performance"""
        with self._lock:
            if agent_name not in self.state['agents']['performance']:
                self.state['agents']['performance'][agent_name] = {
                    'name': agent_name,
                    'executions': 0,
                    'successes': 0,
                    'failures': 0,
                    'total_duration': 0.0,
                    'average_duration': 0.0,
                    'last_execution': None
                }
            
            perf = self.state['agents']['performance'][agent_name]
            perf['executions'] += 1
            perf['total_duration'] += duration
            perf['average_duration'] = perf['total_duration'] / perf['executions']
            perf['last_execution'] = datetime.now().isoformat()
            
            if success:
                perf['successes'] += 1
            else:
                perf['failures'] += 1
            
            self.state['agents']['total_executions'] += 1
            self._save_state()
            
            self.logger.debug(f"Tracked execution for {agent_name}: {duration:.2f}s, success={success}")
    
    def track_command_execution(self, command: str, success: bool, duration: float = 0.0):
        """Track command execution"""
        with self._lock:
            self.state['commands']['total_executed'] += 1
            
            # Add to recent commands (keep last 20)
            command_entry = {
                'command': command,
                'success': success,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            self.state['commands']['recent_commands'].append(command_entry)
            if len(self.state['commands']['recent_commands']) > 20:
                self.state['commands']['recent_commands'].pop(0)
            
            self._save_state()
    
    def log_error(self, component: str, error: str, context: Dict = None):
        """Log an error"""
        with self._lock:
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'component': component,
                'error': error,
                'context': context or {}
            }
            
            self.state['errors'].append(error_entry)
            
            # Keep only last 100 errors
            if len(self.state['errors']) > 100:
                self.state['errors'].pop(0)
            
            self._save_state()
            self.logger.error(f"Logged error from {component}: {error}")
    
    def get_current_spec(self) -> Optional[Dict]:
        """Get current specification state"""
        with self._lock:
            current_name = self.state['workflow']['current_spec']
            if current_name and current_name in self.state['specifications']:
                return self.state['specifications'][current_name]
            return None
    
    def get_specification(self, name: str) -> Optional[Dict]:
        """Get specific specification state"""
        with self._lock:
            return self.state['specifications'].get(name)
    
    def get_all_specifications(self) -> Dict[str, Dict]:
        """Get all specifications"""
        with self._lock:
            return self.state['specifications'].copy()
    
    def get_agent_performance(self, agent_name: str = None) -> Dict:
        """Get agent performance statistics"""
        with self._lock:
            if agent_name:
                return self.state['agents']['performance'].get(agent_name, {})
            return self.state['agents']['performance'].copy()
    
    def get_system_statistics(self) -> Dict:
        """Get overall system statistics"""
        with self._lock:
            return {
                'session': self.state['session'].copy(),
                'workflow': self.state['workflow'].copy(),
                'resources': self.state['resources'].copy(),
                'agents': {
                    'total_executions': self.state['agents']['total_executions'],
                    'agent_count': len(self.state['agents']['performance']),
                    'active_tasks': len(self.state['agents']['active_tasks'])
                },
                'commands': self.state['commands'].copy(),
                'specifications': {
                    'total': len(self.state['specifications']),
                    'active': len([s for s in self.state['specifications'].values() 
                                 if s['current_phase'] != 'complete'])
                },
                'errors': {
                    'total': len(self.state['errors']),
                    'recent': len([e for e in self.state['errors'] 
                                 if (datetime.now() - datetime.fromisoformat(e['timestamp'])).hours < 24])
                }
            }
    
    def get_recent_activity(self, hours: int = 24) -> Dict:
        """Get recent activity summary"""
        with self._lock:
            cutoff_time = datetime.now() - datetime.timedelta(hours=hours)
            
            activity = {
                'commands': [],
                'task_completions': [],
                'errors': [],
                'phase_changes': []
            }
            
            # Recent commands
            for cmd in self.state['commands']['recent_commands']:
                if datetime.fromisoformat(cmd['timestamp']) > cutoff_time:
                    activity['commands'].append(cmd)
            
            # Recent task completions
            for spec_name, spec in self.state['specifications'].items():
                for task_id, task in spec['tasks'].items():
                    if (task['completed_at'] and 
                        datetime.fromisoformat(task['completed_at']) > cutoff_time):
                        activity['task_completions'].append({
                            'spec': spec_name,
                            'task_id': task_id,
                            'status': task['status'],
                            'completed_at': task['completed_at']
                        })
            
            # Recent errors
            for error in self.state['errors']:
                if datetime.fromisoformat(error['timestamp']) > cutoff_time:
                    activity['errors'].append(error)
            
            return activity
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data to prevent state file from growing too large"""
        with self._lock:
            cutoff_time = datetime.now() - datetime.timedelta(days=days)
            
            # Clean old errors
            self.state['errors'] = [
                error for error in self.state['errors']
                if datetime.fromisoformat(error['timestamp']) > cutoff_time
            ]
            
            # Clean old command history
            self.state['commands']['recent_commands'] = [
                cmd for cmd in self.state['commands']['recent_commands']
                if datetime.fromisoformat(cmd['timestamp']) > cutoff_time
            ]
            
            self._save_state()
            self.logger.info(f"Cleaned up data older than {days} days")

def main():
    """Test the unified state manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified State Manager')
    parser.add_argument('--stats', action='store_true', help='Show system statistics')
    parser.add_argument('--create-spec', help='Create a new specification')
    parser.add_argument('--current-spec', action='store_true', help='Show current specification')
    parser.add_argument('--cleanup', type=int, help='Clean up data older than N days')
    
    args = parser.parse_args()
    
    manager = UnifiedStateManager()
    
    if args.stats:
        stats = manager.get_system_statistics()
        print(json.dumps(stats, indent=2))
    
    if args.create_spec:
        success = manager.create_specification(args.create_spec, "Test specification")
        print(f"Specification created: {success}")
    
    if args.current_spec:
        spec = manager.get_current_spec()
        if spec:
            print(json.dumps(spec, indent=2))
        else:
            print("No current specification")
    
    if args.cleanup:
        manager.cleanup_old_data(args.cleanup)
        print(f"Cleaned up data older than {args.cleanup} days")

if __name__ == "__main__":
    main()