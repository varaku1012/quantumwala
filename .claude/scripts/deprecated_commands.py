#!/usr/bin/env python3
"""
Deprecation wrapper for old workflow commands
Provides migration path to new unified commands
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

class DeprecatedCommand:
    """Wrapper for deprecated commands with migration guidance"""
    
    # Deprecation sunset date (30 days from now)
    SUNSET_DATE = datetime.now() + timedelta(days=30)
    
    # Command migration mappings
    MIGRATIONS = {
        'workflow-auto': {
            'new': 'workflow',
            'args': '--auto=auto',
            'description': 'Automated workflow without manual intervention'
        },
        'parallel-workflow': {
            'new': 'workflow', 
            'args': '--mode=parallel',
            'description': 'Workflow with intelligent parallelization'
        },
        'dev-workflow': {
            'new': 'workflow',
            'args': '--auto=smart',
            'description': 'Developer-friendly workflow interface'
        },
        'master-orchestrate': {
            'new': 'workflow',
            'args': '--mode=optimized --auto=auto',
            'description': 'Fully autonomous optimized execution'
        },
        'optimized-execution': {
            'new': 'workflow',
            'args': '--mode=optimized',
            'description': 'Single task with optimization'
        },
        'workflow-start': {
            'new': 'workflow-control',
            'args': 'start',
            'description': 'Start workflow with manual control'
        },
        'workflow-continue': {
            'new': 'workflow-control',
            'args': 'continue',
            'description': 'Continue paused workflow'
        },
        'workflow-reset': {
            'new': 'workflow-control',
            'args': 'reset',
            'description': 'Reset workflow state'
        },
        'spec-implement': {
            'new': 'spec-orchestrate',
            'args': '',
            'description': 'Implement specification tasks'
        },
        'spec-execute': {
            'new': 'spec-orchestrate',
            'args': '',
            'description': 'Execute specification tasks'
        },
        'spec-generate-tasks': {
            'new': 'spec-tasks',
            'args': '',
            'description': 'Generate tasks from spec'
        }
    }
    
    def __init__(self, old_command: str):
        self.old_command = old_command
        self.migration = self.MIGRATIONS.get(old_command)
        self.project_root = self._find_project_root()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def show_deprecation_warning(self):
        """Display deprecation warning with migration guidance"""
        print("\n" + "="*60)
        print("⚠️  DEPRECATION WARNING")
        print("="*60)
        
        print(f"\n❌ The command '/{self.old_command}' is deprecated.")
        
        if self.migration:
            print(f"\n✅ Please use: /{self.migration['new']} {self.migration['args']}")
            print(f"   Description: {self.migration['description']}")
        
        print(f"\n📅 This command will be removed on: {self.SUNSET_DATE.strftime('%Y-%m-%d')}")
        
        print("\n" + "="*60)
        print("MIGRATION GUIDE")
        print("="*60)
        
        self._show_migration_examples()
        
        print("\n" + "="*60 + "\n")
    
    def _show_migration_examples(self):
        """Show specific migration examples"""
        if not self.migration:
            print("No migration path available.")
            return
        
        examples = {
            'workflow-auto': [
                ("Old", "/workflow-auto 'build feature'"),
                ("New", "/workflow 'build feature' --auto=auto")
            ],
            'parallel-workflow': [
                ("Old", "/parallel-workflow 'user-auth'"),
                ("New", "/workflow 'user-auth' --mode=parallel")
            ],
            'dev-workflow': [
                ("Old", "/dev-workflow 'api endpoints'"),
                ("New", "/workflow 'api endpoints' --auto=smart")
            ],
            'workflow-start': [
                ("Old", "/workflow-start 'feature'"),
                ("New", "/workflow-control start 'feature'")
            ],
            'spec-implement': [
                ("Old", "/spec-implement"),
                ("New", "/spec-orchestrate")
            ]
        }
        
        if self.old_command in examples:
            print("\nExamples:")
            for label, example in examples[self.old_command]:
                print(f"  {label}: {example}")
    
    def execute_with_new_command(self, args: list) -> int:
        """Execute using the new command"""
        if not self.migration:
            print(f"❌ No migration available for '{self.old_command}'")
            return 1
        
        # Build new command
        new_command = ['python', f'.claude/scripts/unified_workflow.py']
        
        # Add description/arguments
        if args:
            new_command.extend(args)
        
        # Add migration arguments
        if self.migration['args']:
            new_command.extend(self.migration['args'].split())
        
        print(f"\n🔄 Redirecting to: {' '.join(new_command)}\n")
        
        # Execute new command
        try:
            result = subprocess.run(new_command, cwd=self.project_root)
            return result.returncode
        except Exception as e:
            print(f"❌ Error executing new command: {e}")
            return 1
    
    def should_block_execution(self) -> bool:
        """Check if command should be blocked (after sunset date)"""
        return datetime.now() > self.SUNSET_DATE


def handle_deprecated_command(command_name: str, args: list = None) -> int:
    """
    Main handler for deprecated commands
    
    Args:
        command_name: The deprecated command name
        args: Arguments passed to the command
    
    Returns:
        Exit code
    """
    
    handler = DeprecatedCommand(command_name)
    
    # Show deprecation warning
    handler.show_deprecation_warning()
    
    # Check if past sunset date
    if handler.should_block_execution():
        print("\n❌ This command has been removed. Please use the new command shown above.")
        return 1
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Continue with OLD command (not recommended)")
    print("2. Use NEW command (recommended)")
    print("3. Cancel")
    
    try:
        choice = input("\nChoice (1/2/3): ").strip()
        
        if choice == '1':
            print("\n⚠️ Continuing with deprecated command...")
            # Would execute old command here
            print("Old command execution not implemented in this demo")
            return 0
            
        elif choice == '2':
            return handler.execute_with_new_command(args or [])
            
        else:
            print("\n❌ Cancelled")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled")
        return 1


def create_deprecation_stubs():
    """Create stub files for all deprecated commands"""
    
    stub_template = '''# {command_name} - DEPRECATED

**⚠️ This command is deprecated and will be removed on {sunset_date}**

## Migration Required

Please use: `/{new_command} {args}`

## Description
{description}

## Why Deprecated?
This command has been consolidated into the unified workflow system to reduce complexity and improve maintainability.

## Migration Guide

### Old Usage
```
/{old_command} [arguments]
```

### New Usage  
```
/{new_command} {args} [arguments]
```

## Examples

See `/workflow` for complete documentation.

## Implementation

This command now redirects to:
```bash
python .claude/scripts/deprecated_commands.py {old_command}
```

---

**Action Required**: Update your scripts and workflows to use the new command before {sunset_date}.
'''
    
    commands_dir = Path('.claude/commands')
    
    for old_cmd, migration in DeprecatedCommand.MIGRATIONS.items():
        stub_file = commands_dir / f"{old_cmd}-deprecated.md"
        
        content = stub_template.format(
            command_name=old_cmd.replace('-', ' ').title(),
            old_command=old_cmd,
            new_command=migration['new'],
            args=migration['args'],
            description=migration['description'],
            sunset_date=DeprecatedCommand.SUNSET_DATE.strftime('%Y-%m-%d')
        )
        
        with open(stub_file, 'w') as f:
            f.write(content)
        
        print(f"Created deprecation stub: {stub_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Deprecated command handler')
    parser.add_argument('command', help='Deprecated command name')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--create-stubs', action='store_true', 
                       help='Create deprecation stub files')
    
    args = parser.parse_args()
    
    if args.create_stubs:
        create_deprecation_stubs()
    else:
        exit_code = handle_deprecated_command(args.command, args.args)
        sys.exit(exit_code)