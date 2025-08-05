#!/usr/bin/env python3
"""
Developer environment validation
Catches setup issues early to prevent developer frustration
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationIssue:
    """Represents a setup validation issue"""
    level: str  # 'error', 'warning', 'info'
    component: str
    message: str
    suggestion: str
    fix_command: str = None

class DevEnvironmentValidator:
    """Validates developer environment setup"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.issues: List[ValidationIssue] = []
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def add_issue(self, level: str, component: str, message: str, suggestion: str, fix_command: str = None):
        """Add a validation issue"""
        self.issues.append(ValidationIssue(level, component, message, suggestion, fix_command))
    
    def validate_python_environment(self):
        """Validate Python installation and version"""
        # Check Python version
        if sys.version_info < (3, 7):
            self.add_issue(
                'error', 'Python', 
                f'Python {sys.version_info.major}.{sys.version_info.minor} is too old',
                'Install Python 3.7 or newer',
                'Download from https://python.org'
            )
        elif sys.version_info < (3, 8):
            self.add_issue(
                'warning', 'Python',
                f'Python {sys.version_info.major}.{sys.version_info.minor} works but 3.8+ recommended',
                'Consider upgrading to Python 3.8+ for better performance'
            )
        else:
            # Python version is good
            pass
    
    def validate_required_packages(self):
        """Validate required Python packages"""
        required_packages = {
            'psutil': 'System resource monitoring',
            'asyncio': 'Async workflow execution'  # Built-in for Python 3.7+
        }
        
        optional_packages = {
            'aiofiles': 'Async file operations (improves performance)',
            'rich': 'Enhanced terminal output (better developer experience)'
        }
        
        for package, description in required_packages.items():
            try:
                if package == 'asyncio':
                    import asyncio  # Built-in module
                else:
                    __import__(package)
            except ImportError:
                fix_cmd = f'pip install {package}' if package != 'asyncio' else 'Upgrade to Python 3.7+'
                self.add_issue(
                    'error', 'Dependencies',
                    f'Missing required package: {package}',
                    f'Install {package} for {description}',
                    fix_cmd
                )
        
        for package, description in optional_packages.items():
            try:
                __import__(package)
            except ImportError:
                self.add_issue(
                    'info', 'Dependencies',
                    f'Optional package not installed: {package}',
                    f'Install {package} for {description}',
                    f'pip install {package}'
                )
    
    def validate_file_permissions(self):
        """Validate file system permissions"""
        # Check .claude directory write permissions
        if not self.claude_dir.exists():
            try:
                self.claude_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                self.add_issue(
                    'error', 'Permissions',
                    'Cannot create .claude directory',
                    'Ensure you have write permissions to the project directory'
                )
                return
        
        if not os.access(self.claude_dir, os.W_OK):
            self.add_issue(
                'error', 'Permissions',
                'No write permission to .claude directory',
                'Check directory permissions and file ownership'
            )
        
        # Check if we can create log directories
        log_dir = self.claude_dir / 'logs'
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            # Test write by creating a temporary file
            test_file = log_dir / 'permission_test.tmp'
            test_file.write_text('test')
            test_file.unlink()
        except Exception:
            self.add_issue(
                'error', 'Permissions',
                'Cannot write to logs directory',
                'Ensure write permissions to .claude/logs/ directory'
            )
    
    def validate_claude_code_installation(self):
        """Validate Claude Code CLI installation"""
        # Check if claude-code command exists
        if not shutil.which('claude-code'):
            self.add_issue(
                'warning', 'Claude Code',
                'claude-code command not found in PATH',
                'Install Claude Code CLI or ensure it is in your PATH',
                'See https://docs.anthropic.com/claude-code for installation'
            )
    
    def validate_project_structure(self):
        """Validate project directory structure"""
        required_dirs = [
            '.claude',
            '.claude/agents',
            '.claude/commands',
            '.claude/scripts',
            '.claude/hooks'
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                self.add_issue(
                    'warning', 'Project Structure',
                    f'Missing directory: {dir_path}',
                    f'Create the {dir_path} directory',
                    f'mkdir -p {dir_path}' if platform.system() != 'Windows' else f'mkdir {dir_path.replace("/", os.sep)}'
                )
    
    def validate_system_resources(self):
        """Validate system has adequate resources"""
        try:
            import psutil
            
            # Check available memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < 1:
                self.add_issue(
                    'error', 'System Resources',
                    f'Low available memory: {available_gb:.1f}GB',
                    'Close other applications or add more RAM'
                )
            elif available_gb < 2:
                self.add_issue(
                    'warning', 'System Resources',
                    f'Limited available memory: {available_gb:.1f}GB',
                    'Consider closing other applications for better performance'
                )
            
            # Check available disk space
            disk = psutil.disk_usage(str(self.project_root))
            available_gb = disk.free / (1024**3)
            
            if available_gb < 0.5:
                self.add_issue(
                    'error', 'System Resources',
                    f'Low disk space: {available_gb:.1f}GB available',
                    'Free up disk space before running workflows'
                )
            elif available_gb < 2:
                self.add_issue(
                    'warning', 'System Resources',
                    f'Limited disk space: {available_gb:.1f}GB available',
                    'Consider freeing up disk space'
                )
                
        except ImportError:
            self.add_issue(
                'warning', 'System Resources',
                'Cannot check system resources (psutil not installed)',
                'Install psutil for system resource monitoring',
                'pip install psutil'
            )
    
    def validate_settings_file(self):
        """Validate settings configuration"""
        settings_file = self.claude_dir / 'settings.local.json'
        
        if not settings_file.exists():
            self.add_issue(
                'info', 'Configuration',
                'No settings.local.json found',
                'Run /dev-mode on to create initial configuration',
                'This is normal for first-time setup'
            )
            return
        
        try:
            with open(settings_file) as f:
                settings = json.load(f)
            
            # Check for development mode configuration
            if not settings.get('development_mode', {}).get('enabled', False):
                self.add_issue(
                    'info', 'Configuration',
                    'Development mode not enabled',
                    'Run /dev-mode on for enhanced debugging experience'
                )
                
        except json.JSONDecodeError:
            self.add_issue(
                'error', 'Configuration',
                'Invalid JSON in settings.local.json',
                'Fix JSON syntax errors in settings file'
            )
        except Exception as e:
            self.add_issue(
                'warning', 'Configuration',
                f'Cannot read settings file: {e}',
                'Check file permissions and format'
            )
    
    def run_all_validations(self):
        """Run all validation checks"""
        print("🔍 Validating developer environment...")
        
        self.validate_python_environment()
        self.validate_required_packages()
        self.validate_file_permissions()
        self.validate_claude_code_installation()
        self.validate_project_structure()
        self.validate_system_resources()
        self.validate_settings_file()
    
    def generate_report(self) -> Dict:
        """Generate validation report"""
        errors = [issue for issue in self.issues if issue.level == 'error']
        warnings = [issue for issue in self.issues if issue.level == 'warning']
        info = [issue for issue in self.issues if issue.level == 'info']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'platform': platform.system(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'project_root': str(self.project_root),
            'summary': {
                'total_issues': len(self.issues),
                'errors': len(errors),
                'warnings': len(warnings),
                'info': len(info),
                'ready_to_use': len(errors) == 0
            },
            'issues': {
                'errors': [self._issue_to_dict(issue) for issue in errors],
                'warnings': [self._issue_to_dict(issue) for issue in warnings],
                'info': [self._issue_to_dict(issue) for issue in info]
            }
        }
    
    def _issue_to_dict(self, issue: ValidationIssue) -> Dict:
        """Convert validation issue to dictionary"""
        return {
            'component': issue.component,
            'message': issue.message,
            'suggestion': issue.suggestion,
            'fix_command': issue.fix_command
        }
    
    def print_report(self):
        """Print human-readable validation report"""
        errors = [issue for issue in self.issues if issue.level == 'error']
        warnings = [issue for issue in self.issues if issue.level == 'warning']
        info = [issue for issue in self.issues if issue.level == 'info']
        
        print(f"\n🔍 ENVIRONMENT VALIDATION RESULTS")
        print("=" * 50)
        print(f"📁 Project: {self.project_root.name}")
        print(f"🖥️  Platform: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        if len(errors) == 0:
            print(f"\n✅ READY TO USE - {len(warnings)} warnings, {len(info)} info items")
        else:
            print(f"\n❌ SETUP REQUIRED - {len(errors)} errors must be fixed")
        
        # Print errors (blockers)
        if errors:
            print(f"\n🚨 ERRORS ({len(errors)}) - Must fix before using:")
            for i, issue in enumerate(errors, 1):
                print(f"  {i}. [{issue.component}] {issue.message}")
                print(f"     💡 {issue.suggestion}")
                if issue.fix_command:
                    print(f"     🔧 Fix: {issue.fix_command}")
        
        # Print warnings (recommended fixes)
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}) - Recommended fixes:")
            for i, issue in enumerate(warnings, 1):
                print(f"  {i}. [{issue.component}] {issue.message}")
                print(f"     💡 {issue.suggestion}")
                if issue.fix_command:
                    print(f"     🔧 Fix: {issue.fix_command}")
        
        # Print info (optional improvements)
        if info:
            print(f"\n💡 INFO ({len(info)}) - Optional improvements:")
            for i, issue in enumerate(info, 1):
                print(f"  {i}. [{issue.component}] {issue.message}")
                print(f"     💡 {issue.suggestion}")
                if issue.fix_command:
                    print(f"     🔧 Command: {issue.fix_command}")
        
        # Next steps
        print(f"\n🎯 NEXT STEPS:")
        if errors:
            print("  1. Fix all errors listed above")
            print("  2. Re-run validation: python .claude/scripts/dev_environment_validator.py")
            print("  3. Once errors are fixed, you can start using the system")
        else:
            print("  1. Your environment is ready to use!")
            print("  2. Try: /dev-mode on")
            print("  3. Then: /workflow-auto \"test-feature\" \"Simple test feature\"")
            if warnings:
                print("  4. Consider fixing warnings for better experience")

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Developer Environment')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix common issues automatically')
    
    args = parser.parse_args()
    
    validator = DevEnvironmentValidator()
    validator.run_all_validations()
    
    if args.json:
        report = validator.generate_report()
        print(json.dumps(report, indent=2))
    else:
        validator.print_report()
    
    # Return appropriate exit code
    errors = [issue for issue in validator.issues if issue.level == 'error']
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()