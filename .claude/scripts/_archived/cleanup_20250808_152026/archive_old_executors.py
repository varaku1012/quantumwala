#!/usr/bin/env python3
"""
Archive old workflow executor scripts
Moves duplicate/obsolete executors to an archive folder
"""

import shutil
from pathlib import Path
from datetime import datetime

def archive_old_executors():
    """Archive old executor scripts to clean up the scripts folder"""
    
    script_dir = Path(__file__).parent
    archive_dir = script_dir / "_archived_executors"
    archive_dir.mkdir(exist_ok=True)
    
    # Add timestamp to archive folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_info = archive_dir / f"archive_info_{timestamp}.txt"
    
    # List of old executors to archive
    old_executors = [
        "enhanced_workflow_executor.py",
        "logged_workflow_executor.py",
        "corrected_workflow_executor.py",
        "fully_integrated_workflow.py",
        "execute_complete_development.py"
    ]
    
    archived = []
    not_found = []
    
    print("=" * 60)
    print("ARCHIVING OLD WORKFLOW EXECUTORS")
    print("=" * 60)
    print(f"Archive location: {archive_dir}")
    print("-" * 60)
    
    for executor in old_executors:
        executor_path = script_dir / executor
        if executor_path.exists():
            try:
                # Move to archive
                archive_path = archive_dir / executor
                if archive_path.exists():
                    # Add timestamp if already exists
                    archive_path = archive_dir / f"{executor_path.stem}_{timestamp}{executor_path.suffix}"
                
                shutil.move(str(executor_path), str(archive_path))
                archived.append(executor)
                print(f"  [ARCHIVED] {executor}")
            except Exception as e:
                print(f"  [ERROR] Failed to archive {executor}: {e}")
        else:
            not_found.append(executor)
            print(f"  [SKIP] {executor} - not found")
    
    # Write archive info
    with open(archive_info, 'w') as f:
        f.write(f"Archive Date: {datetime.now().isoformat()}\n")
        f.write(f"Reason: Consolidated into single workflow_executor.py\n\n")
        f.write("Archived Files:\n")
        for file in archived:
            f.write(f"  - {file}\n")
        f.write(f"\nTotal: {len(archived)} files archived\n")
    
    print("-" * 60)
    print(f"Summary:")
    print(f"  Archived: {len(archived)} files")
    print(f"  Not found: {len(not_found)} files")
    print(f"\nAll workflow execution is now handled by:")
    print(f"  workflow_executor.py")
    print("=" * 60)
    
    return len(archived) > 0


if __name__ == "__main__":
    success = archive_old_executors()
    exit(0 if success else 1)