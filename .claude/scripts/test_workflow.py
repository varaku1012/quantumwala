#!/usr/bin/env python3
"""
Test script for the complete workflow system
"""

import os
import sys
import subprocess
from pathlib import Path
import json

class WorkflowTester:
    def __init__(self):
        self.project_root = self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.test_spec = "test-feature"
        self.errors = []
        self.successes = []
        
    def _find_project_root(self):
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def log(self, message, success=True):
        """Log test results"""
        if success:
            print(f"[PASS] {message}")
            self.successes.append(message)
        else:
            print(f"[FAIL] {message}")
            self.errors.append(message)
    
    def run_command(self, command, description):
        """Run a shell command and check result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.log(f"{description} - Command executed successfully")
                return True, result.stdout
            else:
                self.log(f"{description} - Command failed: {result.stderr}", False)
                return False, result.stderr
                
        except Exception as e:
            self.log(f"{description} - Exception: {str(e)}", False)
            return False, str(e)
    
    def test_directory_structure(self):
        """Test that required directories exist"""
        print("\n[TEST] Testing Directory Structure...")
        
        required_dirs = [
            '.claude',
            '.claude/agents',
            '.claude/commands', 
            '.claude/scripts',
            '.claude/hooks',
            '.claude/logs',
            '.claude/logs/sessions'
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.log(f"Directory exists: {dir_path}")
            else:
                self.log(f"Missing directory: {dir_path}", False)
    
    def test_agent_files(self):
        """Test that all agent files exist and are valid"""
        print("\n[TEST] Testing Agent Files...")
        
        expected_agents = [
            'architect.md',
            'business-analyst.md',
            'chief-product-manager-v2.md',
            'code-reviewer.md',
            'data-engineer.md',
            'developer.md',
            'devops-engineer.md',
            'genai-engineer.md',
            'product-manager.md',
            'qa-engineer.md',
            'security-engineer.md',
            'spec-task-executor.md',
            'steering-context-manager.md',
            'uiux-designer.md'
        ]
        
        agents_dir = self.claude_dir / 'agents'
        
        for agent_file in expected_agents:
            agent_path = agents_dir / agent_file
            if agent_path.exists():
                # Check for required sections
                content = agent_path.read_text()
                if 'name:' in content and '##' in content:
                    self.log(f"Agent file valid: {agent_file}")
                else:
                    self.log(f"Agent file incomplete: {agent_file}", False)
            else:
                self.log(f"Missing agent file: {agent_file}", False)
    
    def test_command_files(self):
        """Test that key command files exist"""
        print("\n[TEST] Testing Command Files...")
        
        key_commands = [
            'master-orchestrate.md',
            'planning.md',
            'spec-create.md',
            'spec-requirements.md',
            'spec-design.md',
            'spec-tasks.md',
            'steering-setup.md'
        ]
        
        commands_dir = self.claude_dir / 'commands'
        
        for cmd_file in key_commands:
            cmd_path = commands_dir / cmd_file
            if cmd_path.exists():
                self.log(f"Command file exists: {cmd_file}")
            else:
                self.log(f"Missing command file: {cmd_file}", False)
    
    def test_scripts(self):
        """Test that scripts exist and are executable"""
        print("\n[TEST] Testing Scripts...")
        
        key_scripts = [
            'master_orchestrator_fix.py',
            'planning_executor.py',
            'log_manager.py',
            'workflow_state.py',
            'task_orchestrator.py'
        ]
        
        scripts_dir = self.claude_dir / 'scripts'
        
        for script_file in key_scripts:
            script_path = scripts_dir / script_file
            if script_path.exists():
                # Test basic syntax
                success, output = self.run_command(
                    f"python {script_path} --help",
                    f"Script syntax check: {script_file}"
                )
                if not success and "unrecognized arguments: --help" in output:
                    # Some scripts might not have --help, that's ok
                    self.log(f"Script exists and runs: {script_file}")
            else:
                self.log(f"Missing script: {script_file}", False)
    
    def test_hooks(self):
        """Test hook files"""
        print("\n[TEST] Testing Hooks...")
        
        hooks_dir = self.claude_dir / 'hooks'
        
        required_hooks = [
            'phase-complete.sh',
            'phase-complete.bat',
            'README.md'
        ]
        
        for hook_file in required_hooks:
            hook_path = hooks_dir / hook_file
            if hook_path.exists():
                self.log(f"Hook file exists: {hook_file}")
            else:
                self.log(f"Missing hook file: {hook_file}", False)
    
    def test_planning_functionality(self):
        """Test planning script functionality"""
        print("\n[TEST] Testing Planning Functionality...")
        
        # Create a test spec directory
        test_spec_dir = self.claude_dir / 'specs' / self.test_spec
        test_spec_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a sample tasks.md file
        tasks_content = """# Test Feature Tasks

### Core Implementation
- [ ] 1.1. Create user model
- [ ] 1.2. Create authentication service
- [ ] 2.1. Build user interface
- [ ] 2.2. Add form validation

### Testing
- [ ] 3.1. Write unit tests
- [ ] 3.2. Write integration tests
"""
        
        tasks_file = test_spec_dir / 'tasks.md'
        tasks_file.write_text(tasks_content)
        
        # Test planning script
        planning_script = self.claude_dir / 'scripts' / 'planning_executor.py'
        
        if planning_script.exists():
            success, output = self.run_command(
                f"python {planning_script} implementation {self.test_spec}",
                "Planning script execution"
            )
            
            if success and "Implementation Execution Plan" in output:
                self.log("Planning script generates execution plan")
            else:
                self.log("Planning script failed to generate plan", False)
        
        # Clean up test files
        if tasks_file.exists():
            tasks_file.unlink()
        if test_spec_dir.exists():
            test_spec_dir.rmdir()
    
    def test_log_manager(self):
        """Test log manager functionality"""
        print("\n[TEST] Testing Log Manager...")
        
        log_script = self.claude_dir / 'scripts' / 'log_manager.py'
        
        if log_script.exists():
            # Test creating a session log
            success, output = self.run_command(
                f'python {log_script} create --type session --title "test-session" --content "Test log entry"',
                "Log manager create session"
            )
            
            if success:
                self.log("Log manager can create session logs")
            
            # Test index creation
            success, output = self.run_command(
                f'python {log_script} index',
                "Log manager index creation"
            )
            
            if success:
                self.log("Log manager can create index")
    
    def test_workflow_state(self):
        """Test workflow state management"""
        print("\n[TEST] Testing Workflow State...")
        
        state_script = self.claude_dir / 'scripts' / 'workflow_state.py'
        
        if state_script.exists():
            # Test state detection
            success, output = self.run_command(
                f'python {state_script} --detect',
                "Workflow state detection"
            )
            
            if success:
                self.log("Workflow state can detect current phase")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("[REPORT] WORKFLOW TEST REPORT")
        print("="*60)
        
        total_tests = len(self.successes) + len(self.errors)
        success_rate = (len(self.successes) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Successes: {len(self.successes)}")
        print(f"Failures: {len(self.errors)}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\n[FAIL] FAILURES ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        print(f"\n[PASS] SUCCESSES ({len(self.successes)}):")
        for i, success in enumerate(self.successes, 1):
            print(f"  {i}. {success}")
        
        # Save report to file
        report_file = self.claude_dir / 'logs' / 'test_report.md'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = f"""# Workflow System Test Report

Generated: {os.popen('date').read().strip()}

## Summary
- Total Tests: {total_tests}
- Successes: {len(self.successes)}
- Failures: {len(self.errors)}
- Success Rate: {success_rate:.1f}%

## Failures
{chr(10).join(f"- {error}" for error in self.errors)}

## Successes
{chr(10).join(f"- {success}" for success in self.successes)}

## Next Steps
{self._get_next_steps()}
"""
        
        report_file.write_text(report_content)
        print(f"\n[FILE] Full report saved to: {report_file}")
        
        return len(self.errors) == 0
    
    def _get_next_steps(self):
        """Generate next steps based on test results"""
        if not self.errors:
            return """
[PASS] All tests passed! The workflow system is ready for use.

To get started:
1. Run `/master-orchestrate "project-name" "description"`
2. Or use individual commands like `/planning analysis project-name`
3. Monitor progress in `.claude/logs/`
"""
        else:
            return """
[WARN] Some tests failed. Address the following:

1. Ensure all required files are present
2. Check Python script syntax and dependencies
3. Verify directory permissions
4. Test individual components manually

Run this test again after fixes.
"""
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting Workflow System Tests")
        print("="*60)
        
        self.test_directory_structure()
        self.test_agent_files()
        self.test_command_files()
        self.test_scripts()
        self.test_hooks()
        self.test_planning_functionality()
        self.test_log_manager()
        self.test_workflow_state()
        
        return self.generate_report()

def main():
    tester = WorkflowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()