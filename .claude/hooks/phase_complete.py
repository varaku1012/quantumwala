#!/usr/bin/env python3
"""
Cross-platform hook for automatic workflow phase progression
Replaces bash/batch scripts with unified Python implementation
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def find_project_root():
    """Find project root by looking for .claude directory"""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.claude').exists():
            return current
        current = current.parent
    return Path.cwd()

def get_current_phase():
    """Get current workflow phase - cross-platform"""
    try:
        project_root = find_project_root()
        workflow_state_script = project_root / '.claude' / 'scripts' / 'workflow_state.py'
        
        if workflow_state_script.exists():
            result = subprocess.run([
                sys.executable, 
                str(workflow_state_script), 
                '--get-current'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Warning: workflow_state.py returned error: {result.stderr}")
        
        return "unknown"
    except subprocess.TimeoutExpired:
        print("Warning: workflow_state.py timed out")
        return "unknown"
    except Exception as e:
        print(f"Warning: Error getting current phase: {e}")
        return "unknown"

def get_spec_name():
    """Get current specification name - cross-platform"""
    try:
        project_root = find_project_root()
        workflow_state_script = project_root / '.claude' / 'scripts' / 'workflow_state.py'
        
        if workflow_state_script.exists():
            result = subprocess.run([
                sys.executable,
                str(workflow_state_script),
                '--spec-name'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
        
        return "default"
    except Exception:
        return "default"

def log_phase_completion(phase, spec_name):
    """Log phase completion using log manager"""
    try:
        project_root = find_project_root()
        log_manager_script = project_root / '.claude' / 'scripts' / 'log_manager.py'
        
        if log_manager_script.exists():
            log_content = f"✓ Completed phase: {phase} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            subprocess.run([
                sys.executable,
                str(log_manager_script),
                'create', '--type', 'session',
                '--title', f'phase-complete-{phase}',
                '--content', log_content
            ], capture_output=True, timeout=30)
    except Exception as e:
        print(f"Warning: Could not log phase completion: {e}")

def determine_next_command(current_phase, spec_name):
    """Determine next command based on current phase"""
    phase_transitions = {
        "steering_setup": f'/spec-create "{spec_name}" "Feature implementation"',
        "spec_creation": "/spec-requirements",
        "requirements_generation": f'/planning design "{spec_name}"',
        "design_creation": "/spec-tasks",
        "task_generation": f'/planning implementation "{spec_name}"',
        "implementation": f'/planning testing "{spec_name}"',
        "validation": "/spec-review"
    }
    
    return phase_transitions.get(current_phase, "")

def create_command_suggestion(command):
    """Create command suggestion file for Claude Code to pick up"""
    try:
        project_root = find_project_root()
        suggestion_file = project_root / '.claude' / 'next_command.txt'
        
        # Write suggestion
        suggestion_file.write_text(command, encoding='utf-8')
        
        # Log the suggestion
        auto_progression_log = project_root / '.claude' / 'logs' / 'sessions' / 'auto_progression.log'
        auto_progression_log.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = f"{datetime.now().isoformat()}: Suggested next command: {command}\n"
        with open(auto_progression_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        return True
    except Exception as e:
        print(f"Error creating command suggestion: {e}")
        return False

def update_workflow_progress(phase):
    """Update workflow progress tracking"""
    try:
        project_root = find_project_root()
        workflow_state_script = project_root / '.claude' / 'scripts' / 'workflow_state.py'
        
        if workflow_state_script.exists():
            subprocess.run([
                sys.executable,
                str(workflow_state_script),
                '--complete-phase', phase
            ], capture_output=True, timeout=30)
    except Exception as e:
        print(f"Warning: Could not update workflow progress: {e}")

def main():
    """Main hook execution - cross-platform phase progression"""
    print("🔄 Phase completion hook starting...")
    
    # Get current state
    current_phase = get_current_phase()
    spec_name = get_spec_name()
    
    print(f"📊 Phase completion detected: {current_phase} for spec: {spec_name}")
    
    # Log phase completion
    log_phase_completion(current_phase, spec_name)
    
    # Determine next command
    next_command = determine_next_command(current_phase, spec_name)
    
    if next_command:
        print(f"🚀 Auto-progressing to next phase: {next_command}")
        
        # Create suggestion for Claude Code
        if create_command_suggestion(next_command):
            print("✅ Command suggestion created successfully")
        else:
            print("❌ Failed to create command suggestion")
    else:
        print("✅ Workflow complete or no next phase defined")
    
    # Update workflow progress
    update_workflow_progress(current_phase)
    
    print("🔄 Phase progression hook completed")

if __name__ == "__main__":
    main()