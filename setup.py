#!/usr/bin/env python3
"""
Automated setup script for Claude Code Multi-Agent System
One-command installation and configuration
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class ClaudeAgentSetup:
    """Setup and configuration manager"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.claude_dir = self.project_root / '.claude'
        self.errors = []
        self.warnings = []
        
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 7):
            self.errors.append("Python 3.7+ required")
            return False
        
        # Check if in a git repository (optional)
        if not (self.project_root / '.git').exists():
            self.warnings.append("Not in a git repository - version control recommended")
        
        # Check if Claude Code is accessible
        try:
            # This is a placeholder - actual check would verify Claude Code CLI
            print("[OK] Python version: " + sys.version.split()[0])
            print("[OK] Working directory: " + str(self.project_root))
            return True
        except Exception as e:
            self.errors.append(f"Setup check failed: {str(e)}")
            return False
    
    def create_directory_structure(self):
        """Create all required directories"""
        print("\nCreating directory structure...")
        
        directories = [
            'agents',
            'commands', 
            'steering',
            'scripts',
            'specs',
            'context',
            'hooks',
            'templates',
            'logs/sessions',
            'logs/reports',
            'logs/analysis',
            'logs/phases',
            'logs/archive',
            'system-docs',
            'tests',
            'docs'
        ]
        
        for dir_name in directories:
            dir_path = self.claude_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  [OK] Created {dir_name}/")
    
    def download_core_files(self):
        """Download or copy core system files"""
        print("\nInstalling core files...")
        
        # In a real implementation, these would be downloaded from a repository
        # For now, we'll check if they exist
        
        core_files = {
            'agents': [
                'product-manager.md',
                'business-analyst.md', 
                'architect.md',
                'developer.md',
                'qa-engineer.md',
                'code-reviewer.md',
                'uiux-designer.md',
                'chief-product-manager.md',
                'steering-context-manager.md'
            ],
            'scripts': [
                'get_content.py',
                'get_tasks.py',
                'check_agents.py',
                'steering_loader.py',
                'log_manager.py',
                'task-generator.py',
                'dashboard.py',
                'simple_dashboard.py'
            ],
            'commands': [
                'steering-setup.md',
                'spec-create.md',
                'spec-tasks.md',
                'spec-generate-tasks.md',
                'log-manage.md',
                'dashboard.md'
            ]
        }
        
        installed = 0
        for category, files in core_files.items():
            for file_name in files:
                file_path = self.claude_dir / category / file_name
                if file_path.exists():
                    installed += 1
                else:
                    self.warnings.append(f"Missing: {category}/{file_name}")
        
        print(f"  [OK] Found {installed} core files")
        return installed > 0
    
    def initialize_configuration(self):
        """Create initial configuration files"""
        print("\nInitializing configuration...")
        
        # Create spec-config.json
        spec_config = {
            "spec_workflow": {
                "version": "1.0.0",
                "auto_create_directories": True,
                "auto_reference_requirements": True,
                "enforce_approval_workflow": True,
                "default_feature_prefix": "feature-",
                "supported_formats": ["markdown", "mermaid"],
                "agents_enabled": True,
                "context_engineering": True
            },
            "context_settings": {
                "max_tokens_per_load": 5000,
                "smart_loading": True,
                "cross_platform": True
            }
        }
        
        config_path = self.claude_dir / 'spec-config.json'
        config_path.write_text(json.dumps(spec_config, indent=2))
        print("  [OK] Created spec-config.json")
        
        # Create project-state.json
        project_state = {
            "project": {
                "name": "Your Project Name",
                "description": "Your project description",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "phase": "setup_complete"
            },
            "steering": {
                "initialized": False,
                "documents": {
                    "product": False,
                    "tech": False,
                    "structure": False
                }
            },
            "phases": {
                "setup": {
                    "status": "complete",
                    "timestamp": datetime.now().isoformat()
                }
            }
        }
        
        state_path = self.claude_dir / 'project-state.json'
        state_path.write_text(json.dumps(project_state, indent=2))
        print("  [OK] Created project-state.json")
    
    def create_steering_templates(self):
        """Create steering document templates"""
        print("\nCreating steering templates...")
        
        # These templates are already created in the actual system
        # Just verify they exist
        templates_created = 0
        
        for doc in ['product.md', 'tech.md', 'structure.md', 'README.md']:
            if (self.claude_dir / 'steering' / doc).exists():
                templates_created += 1
        
        if templates_created < 4:
            self.warnings.append("Some steering templates are missing - run /steering-setup")
        else:
            print(f"  [OK] All {templates_created} steering templates found")
    
    def create_claude_md(self):
        """Create or update CLAUDE.md file"""
        print("\nConfiguring CLAUDE.md...")
        
        claude_md_content = """# Claude Code Multi-Agent Development System

This project uses an enhanced multi-agent workflow system with Claude Code.

## Quick Start

1. **Initialize steering context:**
   ```
   /steering-setup
   ```

2. **Create a feature:**
   ```
   /spec-create "feature-name" "description"
   ```

3. **Generate tasks:**
   ```
   /spec-generate-tasks feature-name
   ```

4. **View progress:**
   ```
   /dashboard
   ```

## Available Agents

Run `/help` to see all available agents and commands.

## Log Management

All logs are organized in `.claude/logs/`. To clean root directory:
```
/log-manage clean
```

---
*Setup completed: {timestamp}*
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        claude_md_path = self.project_root / 'CLAUDE.md'
        if not claude_md_path.exists():
            claude_md_path.write_text(claude_md_content)
            print("  [OK] Created CLAUDE.md")
        else:
            print("  [OK] CLAUDE.md already exists")
    
    def run_initial_tests(self):
        """Run basic system tests"""
        print("\nRunning system tests...")
        
        try:
            # Test Python scripts syntax
            test_script = self.claude_dir / 'scripts' / 'check_agents.py'
            if test_script.exists():
                result = subprocess.run(
                    [sys.executable, str(test_script)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("  [OK] Scripts are executable")
                else:
                    self.warnings.append("Some scripts may have issues")
            
            # Test directory permissions
            test_file = self.claude_dir / 'logs' / '.test'
            try:
                test_file.touch()
                test_file.unlink()
                print("  [OK] Directory permissions OK")
            except:
                self.errors.append("Cannot write to .claude directory")
                
        except Exception as e:
            self.warnings.append(f"Test skipped: {str(e)}")
    
    def print_next_steps(self):
        """Print next steps for user"""
        print("\n" + "="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        
        print("\n[INFO] Next Steps:\n")
        print("1. Edit steering documents with your project details:")
        print("   - .claude/steering/product.md")
        print("   - .claude/steering/tech.md") 
        print("   - .claude/steering/structure.md")
        
        print("\n2. Run initial steering setup:")
        print("   /steering-setup")
        
        print("\n3. Create your first feature:")
        print("   /spec-create \"user-authentication\" \"Secure login system\"")
        
        print("\n4. View the dashboard:")
        print("   /dashboard")
        
        if self.warnings:
            print(f"\n[WARNING] Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if self.errors:
            print(f"\n[ERROR] Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
            print("\nPlease fix errors before proceeding.")
        else:
            print("\n[SUCCESS] System ready to use!")
    
    def run(self):
        """Run complete setup process"""
        print("Claude Code Multi-Agent System Setup")
        print("=" * 40)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n[ERROR] Prerequisites check failed!")
            for error in self.errors:
                print(f"   - {error}")
            return False
        
        # Create structure
        self.create_directory_structure()
        
        # Install files
        self.download_core_files()
        
        # Initialize config
        self.initialize_configuration()
        
        # Create templates
        self.create_steering_templates()
        
        # Create CLAUDE.md
        self.create_claude_md()
        
        # Run tests
        self.run_initial_tests()
        
        # Print next steps
        self.print_next_steps()
        
        # Create log of setup
        log_content = {
            "setup_time": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "warnings": self.warnings,
            "errors": self.errors,
            "success": len(self.errors) == 0
        }
        
        log_path = self.claude_dir / 'logs' / 'setup.json'
        log_path.write_text(json.dumps(log_content, indent=2))
        
        return len(self.errors) == 0

def main():
    """Main entry point"""
    setup = ClaudeAgentSetup()
    success = setup.run()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()