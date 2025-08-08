#!/usr/bin/env python3
"""
Clean up redundant and obsolete scripts in .claude/scripts folder
Groups scripts by category and moves unnecessary ones to archive
"""

import shutil
from pathlib import Path
from datetime import datetime

def cleanup_scripts():
    """Identify and archive redundant scripts"""
    
    script_dir = Path(__file__).parent
    archive_dir = script_dir / "_archived"
    archive_dir.mkdir(exist_ok=True)
    
    # Create dated archive subfolder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dated_archive = archive_dir / f"cleanup_{timestamp}"
    dated_archive.mkdir(exist_ok=True)
    
    # ESSENTIAL SCRIPTS - DO NOT ARCHIVE
    essential = {
        # Core workflow
        "workflow_executor.py",         # Main unified executor
        "start_workflow.py",            # Main launcher
        "workflow_logger.py",           # Logging system
        "workflow_validator.py",        # Validation system
        
        # Spec management
        "spec_cleanup.py",              # Spec folder verification
        
        # Context system (keep for future integration)
        "context_engine.py",            # Context engineering
        "memory_manager.py",            # Memory system
        "steering_loader.py",           # Steering doc loader
        
        # Current script
        "cleanup_scripts.py",           # This script
    }
    
    # REDUNDANT SCRIPTS TO ARCHIVE
    redundant = {
        # Old workflow executors and related
        "execute_real_workflow.py": "Replaced by workflow_executor.py",
        "real_executor.py": "Replaced by workflow_executor.py",
        "real_workflow_executor.py": "Replaced by workflow_executor.py",
        "parallel_workflow_orchestrator.py": "Replaced by workflow_executor.py",
        "parallel_workflow_test.py": "Test for obsolete orchestrator",
        "unified_workflow.py": "Replaced by workflow_executor.py",
        "unified_dev_workflow.py": "Replaced by workflow_executor.py",
        "planning_executor.py": "Replaced by workflow_executor.py",
        "workflow_automation.py": "Replaced by workflow_executor.py",
        "workflow_chain.py": "Replaced by workflow_executor.py",
        
        # Old orchestrators
        "orchestrate-auth-test.py": "Specific test orchestrator",
        "orchestrate-test-context-integration.py": "Specific test orchestrator",
        "orchestrate-test-demo.py": "Specific test orchestrator",
        "master_orchestrator_fix.py": "Old orchestrator fix",
        "task_orchestrator.py": "Old task orchestrator",
        
        # Old monitoring/dashboard
        "dashboard.py": "Old dashboard",
        "enhanced_dashboard.py": "Old dashboard",
        "simple_dashboard.py": "Old dashboard",
        "test_dashboard.py": "Dashboard test",
        "simple_workflow_monitor.py": "Old monitor",
        "workflow_monitor.py": "Old monitor",
        
        # Test scripts
        "test_complete_workflow.py": "Old workflow test",
        "test_real_execution.py": "Old execution test",
        "test_workflow.py": "Old workflow test",
        
        # Deprecated/old versions
        "deprecated_commands.py": "Explicitly deprecated",
        "grooming_workflow.py": "Old grooming workflow",
        "spec_migrator.py": "One-time migration script",
        "developer_errors.py": "Old error tracking",
        "developer_status.py": "Old status tracking",
        "dev_mode_manager.py": "Old dev mode",
        "dev_environment_validator.py": "Old validator",
        
        # Utility scripts that are rarely needed
        "check_agents.py": "Agent checker - rarely used",
        "codebase_analyzer.py": "Code analyzer - rarely used",
        "create_database.py": "DB creation - one-time",
        "get_content.py": "Content getter - rarely used",
        "get_tasks.py": "Task getter - rarely used",
        "performance_monitor.py": "Old performance monitor",
        "resource_manager.py": "Old resource manager",
        "suggestion_consumer.py": "Old suggestion system",
        "system_health_check.py": "Old health check",
        "version_manager.py": "Version management - rarely used",
        
        # Old state management
        "unified_state.py": "Old state management",
        "workflow_state.py": "Old workflow state",
        "workflow_control.py": "Old workflow control",
        "workflow_recovery.py": "Old recovery system",
        
        # Task generation (old)
        "task-generator.py": "Old task generator",
        "generate-task-commands.sh": "Old shell script",
        
        # Already archived script
        "archive_old_executors.py": "Already used, can archive",
        
        # Context-related (keep only essential)
        "context_aware_loader.py": "Replaced by context_engine.py",
        "integrated_system.py": "Old integration system",
        "agent_tool_bridge.py": "Old bridge system",
        
        # Spec management (old)
        "spec_manager.py": "Old spec manager",
        "log_manager.py": "Old log manager",
    }
    
    # Documentation files to keep
    keep_docs = {
        "agent_coordination.md",
        "coordination_diagram.svg",
        "coordination_example.txt",
        "example_workflow.md",
    }
    
    print("=" * 70)
    print("SCRIPT CLEANUP ANALYSIS")
    print("=" * 70)
    
    # Count files
    all_files = list(script_dir.glob("*.py")) + list(script_dir.glob("*.sh")) + list(script_dir.glob("*.md"))
    py_files = [f for f in all_files if f.suffix == ".py"]
    
    print(f"Total files in scripts folder: {len(all_files)}")
    print(f"Python scripts: {len(py_files)}")
    print(f"Essential scripts to keep: {len(essential)}")
    print(f"Redundant scripts to archive: {len(redundant)}")
    print("-" * 70)
    
    # Archive redundant scripts
    archived_count = 0
    errors = []
    
    for script_name, reason in redundant.items():
        script_path = script_dir / script_name
        if script_path.exists():
            try:
                dest_path = dated_archive / script_name
                shutil.move(str(script_path), str(dest_path))
                print(f"[ARCHIVED] {script_name}")
                print(f"           Reason: {reason}")
                archived_count += 1
            except Exception as e:
                errors.append(f"{script_name}: {e}")
                print(f"[ERROR] Could not archive {script_name}: {e}")
        else:
            print(f"[SKIP] {script_name} - not found")
    
    # Check for folders that shouldn't be in scripts
    unwanted_folders = ["services", "frontend", "infrastructure"]
    for folder_name in unwanted_folders:
        folder_path = script_dir / folder_name
        if folder_path.exists() and folder_path.is_dir():
            try:
                dest_path = dated_archive / folder_name
                shutil.move(str(folder_path), str(dest_path))
                print(f"[MOVED] {folder_name}/ - shouldn't be in scripts folder")
                archived_count += 1
            except Exception as e:
                errors.append(f"{folder_name}: {e}")
    
    # Create summary file
    summary_file = dated_archive / "cleanup_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Script Cleanup Summary\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"=" * 50 + "\n\n")
        
        f.write(f"Statistics:\n")
        f.write(f"- Total scripts before: {len(py_files)}\n")
        f.write(f"- Scripts archived: {archived_count}\n")
        f.write(f"- Scripts remaining: {len(py_files) - archived_count}\n")
        f.write(f"- Errors: {len(errors)}\n\n")
        
        f.write(f"Essential Scripts Kept:\n")
        for script in sorted(essential):
            f.write(f"  - {script}\n")
        
        f.write(f"\nArchived Scripts:\n")
        for script, reason in sorted(redundant.items()):
            f.write(f"  - {script}: {reason}\n")
        
        if errors:
            f.write(f"\nErrors:\n")
            for error in errors:
                f.write(f"  - {error}\n")
    
    print("-" * 70)
    print(f"SUMMARY:")
    print(f"  Archived: {archived_count} files/folders")
    print(f"  Errors: {len(errors)}")
    print(f"  Archive location: {dated_archive}")
    print(f"  Summary saved: {summary_file}")
    
    # List remaining Python scripts
    remaining = list(script_dir.glob("*.py"))
    print(f"\nREMAINING SCRIPTS ({len(remaining)}):")
    for script in sorted(remaining):
        if script.name in essential:
            print(f"  ✓ {script.name} [ESSENTIAL]")
        else:
            print(f"  ? {script.name} [REVIEW]")
    
    print("=" * 70)
    
    return archived_count > 0


if __name__ == "__main__":
    success = cleanup_scripts()
    exit(0 if success else 1)