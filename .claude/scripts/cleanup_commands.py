#!/usr/bin/env python3
"""
Clean up redundant and obsolete commands in .claude/commands folder
Archives unnecessary commands based on the consolidated workflow system
"""

import shutil
from pathlib import Path
from datetime import datetime

def cleanup_commands():
    """Identify and archive redundant commands"""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    commands_dir = project_root / ".claude/commands"
    archive_dir = commands_dir / "_archived"
    archive_dir.mkdir(exist_ok=True)
    
    # Create dated archive subfolder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dated_archive = archive_dir / f"cleanup_{timestamp}"
    dated_archive.mkdir(exist_ok=True)
    
    # ESSENTIAL COMMANDS - DO NOT ARCHIVE
    essential = {
        # Core workflow (just use start_workflow.py directly)
        "workflow.md",              # Main workflow command
        "workflow-control.md",      # Workflow control (start/stop/status)
        
        # Spec management (core functionality)
        "spec-create.md",          # Create new spec
        "spec-requirements.md",    # Generate requirements
        "spec-design.md",          # Create design
        "spec-tasks.md",           # Generate tasks
        "spec-review.md",          # Review implementation
        "spec-status.md",          # Check spec status
        "spec-list.md",            # List all specs
        
        # Project setup
        "project-init.md",         # Initialize new project
        "steering-setup.md",       # Setup steering context
        
        # System info
        "version.md",              # Version information
    }
    
    # REDUNDANT COMMANDS TO ARCHIVE
    redundant = {
        # Grooming commands (complex workflow not needed with consolidated system)
        "grooming-workflow.md": "Complex grooming not needed - use spec workflow",
        "grooming-start.md": "Part of old grooming workflow",
        "grooming-prioritize.md": "Part of old grooming workflow",
        "grooming-roadmap.md": "Part of old grooming workflow",
        "grooming-complete.md": "Part of old grooming workflow",
        
        # Bug management (can use spec workflow for bugs)
        "bug-create.md": "Use spec-create for bug fixes",
        "bug-analyze.md": "Use spec workflow for analysis",
        "bug-fix.md": "Use spec workflow for implementation",
        "bug-verify.md": "Use spec-review for verification",
        "bug-status.md": "Use spec-status instead",
        
        # Analysis commands (rarely used, complex)
        "analyze-codebase.md": "Complex analysis - rarely needed",
        "analyze-codebase-execution.py": "Python script for codebase analysis",
        "strategic-analysis.md": "Strategic analysis - rarely needed",
        "parallel-analysis.md": "Parallel analysis - complex and rarely used",
        
        # Dev setup (one-time or rarely used)
        "dev-setup.md": "One-time setup - rarely needed",
        "dev-mode.md": "Dev mode toggle - rarely used",
        
        # Spec extras (not essential)
        "spec-orchestrate.md": "Use workflow.md instead",
        "spec-promote.md": "Automatic with workflow",
        "spec-steering-setup.md": "Use steering-setup.md",
        
        # Dashboard and monitoring (old system)
        "dashboard.md": "Old dashboard system",
        "performance.md": "Performance monitoring - old system",
        
        # State and logs (old system)
        "state-backup.md": "State backup - old system",
        "log-manage.md": "Log management - old system",
        
        # Planning (old system)
        "planning.md": "Old planning system",
        
        # Misc/specific
        "resume-etsypro.md": "Specific to EtsyPro project",
        "feature-complete.md": "Use spec workflow completion",
    }
    
    print("=" * 70)
    print("COMMAND CLEANUP ANALYSIS")
    print("=" * 70)
    
    # Count files
    all_files = list(commands_dir.glob("*.md")) + list(commands_dir.glob("*.py"))
    
    print(f"Total files in commands folder: {len(all_files)}")
    print(f"Essential commands to keep: {len(essential)}")
    print(f"Redundant commands to archive: {len(redundant)}")
    print("-" * 70)
    
    # Archive redundant commands
    archived_count = 0
    errors = []
    
    for cmd_name, reason in redundant.items():
        cmd_path = commands_dir / cmd_name
        if cmd_path.exists():
            try:
                dest_path = dated_archive / cmd_name
                shutil.move(str(cmd_path), str(dest_path))
                print(f"[ARCHIVED] {cmd_name}")
                print(f"           Reason: {reason}")
                archived_count += 1
            except Exception as e:
                errors.append(f"{cmd_name}: {e}")
                print(f"[ERROR] Could not archive {cmd_name}: {e}")
        else:
            print(f"[SKIP] {cmd_name} - not found")
    
    # Create summary file
    summary_file = dated_archive / "cleanup_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Command Cleanup Summary\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"=" * 50 + "\n\n")
        
        f.write(f"Statistics:\n")
        f.write(f"- Total commands before: {len(all_files)}\n")
        f.write(f"- Commands archived: {archived_count}\n")
        f.write(f"- Commands remaining: {len(all_files) - archived_count}\n")
        f.write(f"- Errors: {len(errors)}\n\n")
        
        f.write(f"Essential Commands Kept:\n")
        for cmd in sorted(essential):
            f.write(f"  - {cmd}\n")
        
        f.write(f"\nArchived Commands:\n")
        for cmd, reason in sorted(redundant.items()):
            f.write(f"  - {cmd}: {reason}\n")
        
        if errors:
            f.write(f"\nErrors:\n")
            for error in errors:
                f.write(f"  - {error}\n")
    
    print("-" * 70)
    print(f"SUMMARY:")
    print(f"  Archived: {archived_count} files")
    print(f"  Errors: {len(errors)}")
    print(f"  Archive location: {dated_archive}")
    print(f"  Summary saved: {summary_file}")
    
    # List remaining commands
    remaining = list(commands_dir.glob("*.md"))
    remaining = [f for f in remaining if f.name not in redundant]
    
    print(f"\nREMAINING COMMANDS ({len(remaining)}):")
    print("\nCore Workflow:")
    for cmd in ["workflow.md", "workflow-control.md"]:
        if (commands_dir / cmd).exists():
            print(f"  ✓ {cmd}")
    
    print("\nSpec Management:")
    spec_cmds = [f for f in remaining if f.name.startswith("spec-")]
    for cmd in sorted(spec_cmds):
        print(f"  ✓ {cmd.name}")
    
    print("\nProject Setup:")
    for cmd in ["project-init.md", "steering-setup.md"]:
        if (commands_dir / cmd).exists():
            print(f"  ✓ {cmd}")
    
    print("\nSystem:")
    for cmd in ["version.md"]:
        if (commands_dir / cmd).exists():
            print(f"  ✓ {cmd}")
    
    print("=" * 70)
    
    # Create migration guide
    migration_file = dated_archive / "MIGRATION_GUIDE.md"
    with open(migration_file, 'w') as f:
        f.write("# Command Migration Guide\n\n")
        f.write("## How to replace archived commands:\n\n")
        
        f.write("### Grooming Workflow\n")
        f.write("- **Old**: `/grooming-workflow`, `/grooming-start`, etc.\n")
        f.write("- **New**: Use `/spec-create` and `/workflow` for feature development\n\n")
        
        f.write("### Bug Management\n")
        f.write("- **Old**: `/bug-create`, `/bug-fix`, etc.\n")
        f.write("- **New**: Create a spec for the bug fix using `/spec-create` then `/workflow`\n\n")
        
        f.write("### Analysis\n")
        f.write("- **Old**: `/analyze-codebase`, `/strategic-analysis`\n")
        f.write("- **New**: Use Task tool to delegate to codebase-analyst agent directly\n\n")
        
        f.write("### Spec Orchestration\n")
        f.write("- **Old**: `/spec-orchestrate`\n")
        f.write("- **New**: Use `/workflow` or `python .claude/scripts/start_workflow.py`\n\n")
        
        f.write("### Dashboard/Monitoring\n")
        f.write("- **Old**: `/dashboard`, `/performance`\n")
        f.write("- **New**: Check logs in `.claude/logs/workflows/`\n\n")
    
    print(f"\nMigration guide created: {migration_file}")
    
    return archived_count > 0


if __name__ == "__main__":
    success = cleanup_commands()
    exit(0 if success else 1)