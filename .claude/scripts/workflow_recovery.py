#!/usr/bin/env python3
"""
Workflow recovery utilities
Provides backup, restore, and reset functionality for development teams
"""

import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from unified_state import UnifiedStateManager
except ImportError:
    print("Error: Could not import unified_state module")
    sys.exit(1)

class WorkflowRecovery:
    """Workflow recovery and backup management"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.backup_dir = self.claude_dir / 'backups'
        self.state_manager = UnifiedStateManager(self.project_root)
        
        # Ensure backup directories exist
        (self.backup_dir / 'state').mkdir(parents=True, exist_ok=True)
        (self.backup_dir / 'workflows').mkdir(parents=True, exist_ok=True)
        
        self.setup_logging()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def setup_logging(self):
        """Setup recovery logging"""
        log_dir = self.claude_dir / 'logs' / 'recovery'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'recovery_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_state_backup(self, backup_name: str = None) -> str:
        """Create a backup of current unified state"""
        if backup_name is None:
            backup_name = f"state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        print(f"✓ Creating state backup: {backup_name}")
        
        try:
            backup_path = self.state_manager.create_state_backup(backup_name)
            file_size = Path(backup_path).stat().st_size / (1024 * 1024)  # MB
            
            print(f"✓ State backup created successfully ({file_size:.1f}MB)")
            print(f"  Location: {backup_path}")
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Failed to create state backup: {e}")
            self.logger.error(f"State backup failed: {e}")
            raise
    
    def list_state_backups(self) -> List[Dict]:
        """List available state backups"""
        backup_dir = self.backup_dir / 'state'
        backups = []
        
        for backup_file in backup_dir.glob('*.json'):
            try:
                stat = backup_file.stat()
                age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
                
                backups.append({
                    'name': backup_file.name,
                    'path': str(backup_file),
                    'size_mb': stat.st_size / (1024 * 1024),
                    'age_hours': age.total_seconds() / 3600,
                    'created': datetime.fromtimestamp(stat.st_mtime)
                })
            except Exception:
                continue  # Skip corrupted files
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def restore_state_backup(self, backup_name: str) -> bool:
        """Restore state from backup"""
        print(f"✓ Restoring state from backup: {backup_name}")
        
        # Find backup file
        backup_dir = self.backup_dir / 'state'
        backup_path = backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_name}")
            return False
        
        try:
            success = self.state_manager.restore_state_from_backup(str(backup_path))
            if success:
                print(f"✓ State restored successfully from {backup_name}")
                return True
            else:
                print(f"❌ Failed to restore state from {backup_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error restoring state: {e}")
            self.logger.error(f"State restore failed: {e}")
            return False
    
    def reset_workflow(self, spec_name: str, hard_reset: bool = False) -> bool:
        """Reset workflow state for a specification"""
        print(f"✓ Resetting workflow for spec: {spec_name}")
        
        try:
            # Create backup before reset
            backup_name = f"pre_reset_{spec_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.create_state_backup(backup_name)
            
            # Reset workflow state
            state = self.state_manager.state
            
            if spec_name in state.get('specifications', {}):\n                if hard_reset:\n                    # Hard reset: remove all generated files\n                    spec_dir = self.claude_dir / 'specs' / spec_name\n                    if spec_dir.exists():\n                        # Backup before deletion\n                        backup_spec_dir = self.backup_dir / 'workflows' / f\"{spec_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}\"\n                        shutil.copytree(spec_dir, backup_spec_dir)\n                        print(f\"✓ Spec files backed up to: {backup_spec_dir}\")\n                        \n                        # Remove generated files but keep requirements\n                        for file_to_remove in ['design.md', 'tasks.md', 'review.md']:\n                            file_path = spec_dir / file_to_remove\n                            if file_path.exists():\n                                file_path.unlink()\n                                print(f\"✓ Removed: {file_to_remove}\")\n                \n                # Reset state entries\n                spec_state = state['specifications'][spec_name]\n                spec_state['current_phase'] = 'requirements_generation'\n                spec_state['tasks'] = {}\n                spec_state['progress_percentage'] = 0.0\n                \n                # Clear completed phases after requirements\n                spec_state['completed_phases'] = [\n                    phase for phase in spec_state.get('completed_phases', [])\n                    if phase.get('name') in ['steering_setup', 'spec_creation']\n                ]\n            \n            # Reset global workflow state if this was the current spec\n            if state['workflow'].get('current_spec') == spec_name:\n                state['workflow']['global_phase'] = 'requirements_generation'\n            \n            # Clear suggestion files\n            suggestion_file = self.claude_dir / 'next_command.txt'\n            if suggestion_file.exists():\n                suggestion_file.unlink()\n                print(\"✓ Cleared command suggestions\")\n            \n            # Save updated state\n            self.state_manager.save_state()\n            \n            reset_type = \"Hard reset\" if hard_reset else \"Soft reset\"\n            print(f\"✓ {reset_type} completed for {spec_name}\")\n            print(f\"  Next: Run /spec-requirements to restart workflow\")\n            \n            return True\n            \n        except Exception as e:\n            print(f\"❌ Workflow reset failed: {e}\")\n            self.logger.error(f\"Workflow reset failed for {spec_name}: {e}\")\n            return False\n    \n    def clean_old_backups(self, days: int = 7) -> int:\n        \"\"\"Clean backups older than specified days\"\"\"\n        cutoff_date = datetime.now() - timedelta(days=days)\n        cleaned_count = 0\n        total_size_saved = 0\n        \n        print(f\"✓ Cleaning backups older than {days} days...\")\n        \n        # Clean state backups\n        for backup_file in (self.backup_dir / 'state').glob('*.json'):\n            try:\n                if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:\n                    size = backup_file.stat().st_size\n                    backup_file.unlink()\n                    cleaned_count += 1\n                    total_size_saved += size\n                    self.logger.info(f\"Cleaned old backup: {backup_file.name}\")\n            except Exception as e:\n                self.logger.warning(f\"Failed to clean backup {backup_file.name}: {e}\")\n        \n        # Clean workflow backups\n        for backup_dir in (self.backup_dir / 'workflows').iterdir():\n            if backup_dir.is_dir():\n                try:\n                    if datetime.fromtimestamp(backup_dir.stat().st_mtime) < cutoff_date:\n                        size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())\n                        shutil.rmtree(backup_dir)\n                        cleaned_count += 1\n                        total_size_saved += size\n                        self.logger.info(f\"Cleaned old workflow backup: {backup_dir.name}\")\n                except Exception as e:\n                    self.logger.warning(f\"Failed to clean workflow backup {backup_dir.name}: {e}\")\n        \n        if cleaned_count > 0:\n            size_mb = total_size_saved / (1024 * 1024)\n            print(f\"✓ Cleaned {cleaned_count} backups\")\n            print(f\"✓ Storage saved: {size_mb:.1f}MB\")\n        else:\n            print(\"✓ No old backups to clean\")\n        \n        return cleaned_count

def main():
    \"\"\"Main function for workflow recovery operations\"\"\"
    parser = argparse.ArgumentParser(description='Workflow Recovery Utilities')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create state backup')
    backup_parser.add_argument('name', nargs='?', help='Backup name (optional)')
    backup_parser.add_argument('--list', action='store_true', help='List available backups')
    backup_parser.add_argument('--restore', help='Restore from backup')
    backup_parser.add_argument('--clean', action='store_true', help='Clean old backups')
    backup_parser.add_argument('--days', type=int, default=7, help='Days to keep (for clean)')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset workflow')
    reset_parser.add_argument('spec_name', help='Specification name to reset')
    reset_parser.add_argument('--hard', action='store_true', help='Hard reset (removes files)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    recovery = WorkflowRecovery()
    
    if args.command == 'backup':
        if args.list:
            backups = recovery.list_state_backups()
            if backups:
                print(\"\\nAvailable State Backups:\")
                for backup in backups:\n                    age_str = f\"{backup['age_hours']:.1f} hours ago\" if backup['age_hours'] < 24 else f\"{backup['age_hours']/24:.1f} days ago\"\n                    print(f\"- {backup['name']} ({backup['size_mb']:.1f}MB) - {age_str}\")\n            else:\n                print(\"No backups found\")\n        elif args.restore:\n            recovery.restore_state_backup(args.restore)\n        elif args.clean:\n            recovery.clean_old_backups(args.days)\n        else:\n            recovery.create_state_backup(args.name)\n    \n    elif args.command == 'reset':\n        if args.hard:\n            confirm = input(f\"Hard reset will remove generated files for '{args.spec_name}'. Continue? (y/N): \")\n            if confirm.lower() != 'y':\n                print(\"Reset cancelled\")\n                return\n        \n        recovery.reset_workflow(args.spec_name, args.hard)

if __name__ == "__main__":
    main()