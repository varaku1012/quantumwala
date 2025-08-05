#!/usr/bin/env python3
"""
Developer-friendly status dashboard
Simple overview of project, environment, and workflow status
"""

import os
import sys
import json
import psutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from developer_errors import developer_friendly
    from dev_environment_validator import DevEnvironmentValidator
except ImportError:
    # Graceful fallback for status command
    def developer_friendly(func):
        return func

@dataclass
class ProjectInfo:
    """Basic project information"""
    name: str
    location: str
    created: Optional[datetime] = None
    last_activity: Optional[datetime] = None

@dataclass
class WorkflowStatus:
    """Current workflow status"""
    project_name: str
    current_phase: str
    progress_percentage: float
    active_tasks: List[Dict]
    completed_tasks: int
    total_tasks: int
    estimated_remaining_minutes: int

@dataclass
class SystemHealth:
    """System health information"""
    python_version: str
    dependencies_ok: bool
    permissions_ok: bool
    dev_mode_enabled: bool
    available_disk_gb: float
    available_memory_gb: float
    cpu_usage_percent: float

class DeveloperStatus:
    """Developer-friendly status dashboard"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    @developer_friendly
    def get_project_info(self) -> ProjectInfo:
        """Get basic project information"""
        # Try to determine project name from directory or specs
        project_name = "No active project"
        
        # Check for active specifications
        specs_dir = self.claude_dir / 'specs'
        if specs_dir.exists():
            spec_dirs = [d for d in specs_dir.iterdir() if d.is_dir()]
            if spec_dirs:
                # Use most recently modified spec as current project
                latest_spec = max(spec_dirs, key=lambda d: d.stat().st_mtime)
                project_name = latest_spec.name
        
        # Get creation and activity times
        created = None
        last_activity = None
        
        if self.claude_dir.exists():
            created = datetime.fromtimestamp(self.claude_dir.stat().st_ctime)
            
            # Find most recent activity in logs
            logs_dir = self.claude_dir / 'logs'
            if logs_dir.exists():
                log_files = list(logs_dir.rglob('*.log'))
                if log_files:
                    latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                    last_activity = datetime.fromtimestamp(latest_log.stat().st_mtime)
        
        return ProjectInfo(
            name=project_name,
            location=str(self.project_root),
            created=created,
            last_activity=last_activity
        )
    
    @developer_friendly
    def get_system_health(self) -> SystemHealth:
        """Get system health information"""
        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Check dependencies
        dependencies_ok = True
        try:
            import psutil
        except ImportError:
            dependencies_ok = False
        
        # Check permissions
        permissions_ok = os.access(self.claude_dir, os.W_OK) if self.claude_dir.exists() else False
        
        # Check development mode
        dev_mode_enabled = False
        settings_file = self.claude_dir / 'settings.local.json'
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    settings = json.load(f)
                dev_mode_enabled = settings.get('development_mode', {}).get('enabled', False)
            except:
                pass
        
        # System resources
        try:
            disk = psutil.disk_usage(str(self.project_root))
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            available_disk_gb = disk.free / (1024**3)
            available_memory_gb = memory.available / (1024**3)
        except:
            available_disk_gb = 0.0
            available_memory_gb = 0.0
            cpu_percent = 0.0
        
        return SystemHealth(
            python_version=python_version,
            dependencies_ok=dependencies_ok,
            permissions_ok=permissions_ok,
            dev_mode_enabled=dev_mode_enabled,
            available_disk_gb=available_disk_gb,
            available_memory_gb=available_memory_gb,
            cpu_usage_percent=cpu_percent
        )
    
    @developer_friendly
    def get_workflow_status(self) -> Optional[WorkflowStatus]:
        """Get current workflow status"""
        # Try to load unified state
        state_file = self.claude_dir / 'unified_state.json'
        if not state_file.exists():
            return None
        
        try:
            with open(state_file) as f:
                state = json.load(f)
            
            workflow = state.get('workflow', {})
            current_spec = workflow.get('current_spec')
            
            if not current_spec:
                return None
            
            specs = state.get('specifications', {})
            if current_spec not in specs:
                return None
            
            spec_state = specs[current_spec]
            
            # Calculate progress
            tasks = spec_state.get('tasks', {})
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks.values() if task.get('status') == 'completed')
            
            progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Get active tasks
            active_tasks = [
                {
                    'id': task_id,
                    'description': task.get('description', ''),
                    'agent': task.get('agent', ''),
                    'status': task.get('status', '')
                }
                for task_id, task in tasks.items()
                if task.get('status') in ['in_progress', 'pending']
            ]
            
            # Estimate remaining time (rough calculation)
            remaining_tasks = total_tasks - completed_tasks
            estimated_remaining_minutes = remaining_tasks * 10  # Rough estimate: 10 min per task
            
            return WorkflowStatus(
                project_name=current_spec,
                current_phase=spec_state.get('current_phase', 'unknown'),
                progress_percentage=progress_percentage,
                active_tasks=active_tasks,
                completed_tasks=completed_tasks,
                total_tasks=total_tasks,
                estimated_remaining_minutes=estimated_remaining_minutes
            )
            
        except Exception:
            return None
    
    def get_recent_activity(self, limit: int = 5) -> List[Dict]:
        """Get recent command activity"""
        activities = []
        
        # Check auto progression log
        auto_log = self.claude_dir / 'logs' / 'sessions' / 'auto_progression.log'
        if auto_log.exists():
            try:
                with open(auto_log) as f:
                    lines = f.readlines()
                
                for line in reversed(lines[-limit:]):
                    if 'Suggested next command:' in line:
                        parts = line.strip().split(': Suggested next command: ')
                        if len(parts) == 2:
                            timestamp_str, command = parts
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str)
                                activities.append({
                                    'time': timestamp.strftime('%H:%M'),
                                    'command': command,
                                    'status': '✅'
                                })
                            except:
                                continue
            except:
                pass
        
        return activities
    
    def get_issues_and_alerts(self) -> List[Dict]:
        """Get current issues and alerts"""
        issues = []
        
        # Check system health issues
        health = self.get_system_health()
        
        if not health.dependencies_ok:
            issues.append({
                'type': 'error',
                'message': 'Missing dependencies (psutil)',
                'suggestion': 'pip install psutil'
            })
        
        if not health.permissions_ok:
            issues.append({
                'type': 'error', 
                'message': 'No write permission to .claude directory',
                'suggestion': 'Fix file permissions'
            })
        
        if health.available_disk_gb < 1.0:
            issues.append({
                'type': 'warning',
                'message': f'Low disk space: {health.available_disk_gb:.1f}GB remaining',
                'suggestion': 'Free up disk space'
            })
        
        if health.available_memory_gb < 1.0:
            issues.append({
                'type': 'warning',
                'message': f'Low memory: {health.available_memory_gb:.1f}GB available',
                'suggestion': 'Close other applications'
            })
        
        return issues
    
    def print_status(self, sections: List[str] = None):
        """Print comprehensive status report"""
        if sections is None:
            sections = ['project', 'environment', 'workflow', 'activity', 'issues']
        
        print("🔍 QUANTUMWALA STATUS")
        print("=" * 50)
        
        if 'project' in sections:
            project = self.get_project_info()
            print(f"\n📁 PROJECT INFORMATION")
            print(f"   Name: {project.name}")
            print(f"   Location: {project.location}")
            if project.created:
                age = datetime.now() - project.created
                if age.days > 0:
                    print(f"   Created: {age.days} days ago")
                else:
                    print(f"   Created: {age.seconds // 3600} hours ago")
            if project.last_activity:
                age = datetime.now() - project.last_activity
                if age.seconds < 60:
                    print(f"   Last activity: {age.seconds} seconds ago")
                elif age.seconds < 3600:
                    print(f"   Last activity: {age.seconds // 60} minutes ago")
                else:
                    print(f"   Last activity: {age.seconds // 3600} hours ago")
        
        if 'environment' in sections:
            health = self.get_system_health()
            print(f"\n⚡ ENVIRONMENT STATUS")
            
            py_status = "✅" if float(health.python_version.split('.')[1]) >= 7 else "⚠️"
            print(f"   {py_status} Python {health.python_version}")
            
            deps_status = "✅" if health.dependencies_ok else "❌"
            print(f"   {deps_status} Dependencies {'installed' if health.dependencies_ok else 'missing'}")
            
            perm_status = "✅" if health.permissions_ok else "❌"
            print(f"   {perm_status} Permissions {'OK' if health.permissions_ok else 'insufficient'}")
            
            dev_status = "🔧" if health.dev_mode_enabled else "📋"
            dev_text = "ENABLED" if health.dev_mode_enabled else "DISABLED"
            print(f"   {dev_status} Development mode: {dev_text}")
            
            print(f"   💾 Available disk: {health.available_disk_gb:.1f}GB")
            print(f"   🧠 Available memory: {health.available_memory_gb:.1f}GB")
        
        if 'workflow' in sections:
            workflow = self.get_workflow_status()
            if workflow:
                print(f"\n📊 CURRENT WORKFLOW")
                print(f"   Project: {workflow.project_name}")
                print(f"   Phase: {workflow.current_phase}")
                
                # Progress bar
                progress_bars = int(workflow.progress_percentage / 10)
                progress_bar = "█" * progress_bars + "░" * (10 - progress_bars)
                print(f"   Progress: {progress_bar} {workflow.progress_percentage:.0f}% complete")
                
                if workflow.active_tasks:
                    print(f"\n   Active Tasks:")
                    for task in workflow.active_tasks[:3]:  # Show max 3 tasks
                        status_icon = "⚡" if task['status'] == 'in_progress' else "⏳"
                        print(f"   • {task['id']}: {task['description']} ({task['agent']}) - {status_icon}")
                
                print(f"\n   Completed: {workflow.completed_tasks}/{workflow.total_tasks} tasks")
                if workflow.estimated_remaining_minutes > 0:
                    print(f"   Estimated time remaining: {workflow.estimated_remaining_minutes} minutes")
            else:
                print(f"\n📊 CURRENT WORKFLOW")
                print(f"   No active workflow")
                print(f"   🎯 Next: Try /dev-workflow \"describe what you want to build\"")
        
        if 'activity' in sections:
            activities = self.get_recent_activity()
            if activities:
                print(f"\n📈 RECENT ACTIVITY")
                for activity in activities:
                    print(f"   {activity['time']} - {activity['command']} {activity['status']}")
            else:
                print(f"\n📈 RECENT ACTIVITY")
                print(f"   No recent activity")
        
        if 'issues' in sections:
            issues = self.get_issues_and_alerts()
            print(f"\n🚨 ISSUES & ALERTS")
            if issues:
                for issue in issues:
                    icon = "❌" if issue['type'] == 'error' else "⚠️"
                    print(f"   {icon} {issue['message']}")
                    if 'suggestion' in issue:
                        print(f"      💡 {issue['suggestion']}")
            else:
                print(f"   No current issues ✅")
        
        # Always show next steps for guidance
        workflow = self.get_workflow_status()
        if workflow and workflow.active_tasks:
            print(f"\n🎯 NEXT STEPS")
            print(f"   1. Wait for current tasks to complete")
            print(f"   2. Monitor progress with /status")
            print(f"   3. Ready for next phase in ~{workflow.estimated_remaining_minutes} minutes")
        elif not workflow:
            print(f"\n🎯 NEXT STEPS")
            print(f"   1. Start a new workflow: /dev-workflow \"describe your project\"")
            print(f"   2. Or enable development mode: /dev-mode on")
            print(f"   3. Check environment: /dev-setup validate")
    
    def get_status_json(self) -> Dict[str, Any]:
        """Get status as JSON for programmatic use"""
        project = self.get_project_info()
        health = self.get_system_health()
        workflow = self.get_workflow_status()
        activities = self.get_recent_activity()
        issues = self.get_issues_and_alerts()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'project': {
                'name': project.name,
                'location': project.location,
                'created': project.created.isoformat() if project.created else None,
                'last_activity': project.last_activity.isoformat() if project.last_activity else None
            },
            'environment': {
                'python_version': health.python_version,
                'dependencies_ok': health.dependencies_ok,
                'permissions_ok': health.permissions_ok,
                'dev_mode_enabled': health.dev_mode_enabled,
                'available_disk_gb': health.available_disk_gb,
                'available_memory_gb': health.available_memory_gb,
                'cpu_usage_percent': health.cpu_usage_percent
            },
            'workflow': {
                'active': workflow is not None,
                'project_name': workflow.project_name if workflow else None,
                'current_phase': workflow.current_phase if workflow else None,
                'progress_percentage': workflow.progress_percentage if workflow else 0,
                'active_tasks': workflow.active_tasks if workflow else [],
                'completed_tasks': workflow.completed_tasks if workflow else 0,
                'total_tasks': workflow.total_tasks if workflow else 0,
                'estimated_remaining_minutes': workflow.estimated_remaining_minutes if workflow else 0
            },
            'recent_activity': activities,
            'issues': issues
        }

def main():
    """Main function for developer status"""
    parser = argparse.ArgumentParser(description='Developer Status Dashboard')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--sections', help='Comma-separated list of sections to show')
    parser.add_argument('--env', action='store_true', help='Show environment status only')
    parser.add_argument('--workflow', action='store_true', help='Show workflow status only')
    parser.add_argument('--issues', action='store_true', help='Show issues only')
    parser.add_argument('--prompt', action='store_true', help='Brief status for shell prompt')
    parser.add_argument('--watch', action='store_true', help='Continuously monitor status')
    parser.add_argument('--interval', type=int, default=10, help='Watch interval in seconds')
    
    args = parser.parse_args()
    
    try:
        status = DeveloperStatus()
        
        if args.json:
            print(json.dumps(status.get_status_json(), indent=2))
        elif args.prompt:
            # Brief status for shell prompt
            workflow = status.get_workflow_status()
            if workflow:
                progress = int(workflow.progress_percentage / 10)
                bar = "█" * progress + "░" * (10 - progress)
                print(f"[QW:{workflow.project_name}:{bar}]")
            else:
                print("[QW:ready]")
        elif args.watch:
            import time
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                status.print_status()
                print(f"\n⏱️  Refreshing every {args.interval}s... (Ctrl+C to stop)")
                time.sleep(args.interval)
        else:
            # Determine sections to show
            sections = None
            if args.sections:
                sections = args.sections.split(',')
            elif args.env:
                sections = ['environment']
            elif args.workflow:
                sections = ['workflow']
            elif args.issues:
                sections = ['issues']
            
            status.print_status(sections)
    
    except KeyboardInterrupt:
        print("\n⏹️  Status monitoring stopped")
    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")
        print(f"💡 Try: python .claude/scripts/dev_environment_validator.py")
        sys.exit(1)

if __name__ == "__main__":
    main()