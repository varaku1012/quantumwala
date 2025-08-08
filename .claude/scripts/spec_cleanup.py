#!/usr/bin/env python3
"""
Spec Cleanup and Verification Tool
Ensures specs are in the correct folders and no duplicates exist
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

class SpecCleanup:
    """Clean up and verify spec lifecycle folders"""
    
    def __init__(self):
        # Setup paths
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        self.specs_dir = self.project_root / ".claude/specs"
        
        self.backlog_dir = self.specs_dir / "backlog"
        self.scope_dir = self.specs_dir / "scope"
        self.completed_dir = self.specs_dir / "completed"
        
        # Track issues
        self.issues = []
        self.fixed = []
    
    def verify_spec_locations(self):
        """Verify no duplicate specs across folders"""
        print("\n" + "=" * 70)
        print("SPEC LOCATION VERIFICATION")
        print("=" * 70)
        
        # Get all specs in each folder
        backlog_specs = set()
        scope_specs = set()
        completed_specs = set()
        
        if self.backlog_dir.exists():
            backlog_specs = {d.name for d in self.backlog_dir.iterdir() if d.is_dir()}
        
        if self.scope_dir.exists():
            scope_specs = {d.name for d in self.scope_dir.iterdir() if d.is_dir()}
        
        if self.completed_dir.exists():
            completed_specs = {d.name for d in self.completed_dir.iterdir() if d.is_dir()}
        
        # Check for duplicates
        print("\n[CHECKING] for duplicate specs...")
        
        # Check backlog vs scope
        duplicates_bs = backlog_specs & scope_specs
        if duplicates_bs:
            for spec in duplicates_bs:
                self.issues.append({
                    "type": "DUPLICATE",
                    "spec": spec,
                    "locations": ["backlog", "scope"],
                    "message": f"Spec '{spec}' exists in both backlog and scope"
                })
        
        # Check backlog vs completed
        duplicates_bc = backlog_specs & completed_specs
        if duplicates_bc:
            for spec in duplicates_bc:
                self.issues.append({
                    "type": "DUPLICATE",
                    "spec": spec,
                    "locations": ["backlog", "completed"],
                    "message": f"Spec '{spec}' exists in both backlog and completed"
                })
        
        # Check scope vs completed
        duplicates_sc = scope_specs & completed_specs
        if duplicates_sc:
            for spec in duplicates_sc:
                self.issues.append({
                    "type": "DUPLICATE",
                    "spec": spec,
                    "locations": ["scope", "completed"],
                    "message": f"Spec '{spec}' exists in both scope and completed"
                })
        
        # Report findings
        print("\n[RESULTS]")
        print("-" * 50)
        print(f"Backlog specs: {len(backlog_specs)}")
        for spec in sorted(backlog_specs):
            print(f"  - {spec}")
        
        print(f"\nScope specs: {len(scope_specs)}")
        for spec in sorted(scope_specs):
            print(f"  - {spec}")
        
        print(f"\nCompleted specs: {len(completed_specs)}")
        for spec in sorted(completed_specs):
            print(f"  - {spec}")
        
        if self.issues:
            print("\n[ISSUES FOUND]")
            print("-" * 50)
            for issue in self.issues:
                print(f"[{issue['type']}] {issue['message']}")
        else:
            print("\n[SUCCESS] No duplicate specs found!")
        
        return len(self.issues) == 0
    
    def fix_duplicates(self, auto_fix=False):
        """Fix duplicate specs based on metadata"""
        if not self.issues:
            print("\n[INFO] No issues to fix")
            return True
        
        print("\n" + "=" * 70)
        print("FIXING DUPLICATE SPECS")
        print("=" * 70)
        
        for issue in self.issues:
            if issue["type"] == "DUPLICATE":
                spec_name = issue["spec"]
                locations = issue["locations"]
                
                print(f"\n[FIXING] {spec_name} in {locations}")
                
                # Determine which one to keep based on metadata
                keep_location = self._determine_keep_location(spec_name, locations)
                
                if not auto_fix:
                    print(f"  Recommendation: Keep in '{keep_location}'")
                    response = input("  Apply fix? (y/N): ")
                    if response.lower() != 'y':
                        print("  Skipped")
                        continue
                
                # Remove from other locations
                for location in locations:
                    if location != keep_location:
                        spec_path = self.specs_dir / location / spec_name
                        if spec_path.exists():
                            print(f"  Removing from {location}...")
                            shutil.rmtree(spec_path)
                            self.fixed.append({
                                "spec": spec_name,
                                "action": f"Removed from {location}",
                                "kept": keep_location
                            })
        
        return True
    
    def _determine_keep_location(self, spec_name, locations):
        """Determine which location to keep based on metadata"""
        # Priority: completed > scope > backlog
        if "completed" in locations:
            # Check if it has completion metadata
            meta_file = self.completed_dir / spec_name / "_meta.json"
            if not meta_file.exists():
                meta_file = self.completed_dir / spec_name / "completion_meta.json"
            
            if meta_file.exists():
                try:
                    with open(meta_file, 'r') as f:
                        meta = json.load(f)
                        if meta.get("status") == "COMPLETED":
                            return "completed"
                except:
                    pass
        
        if "scope" in locations:
            # Check if actively being worked on
            meta_file = self.scope_dir / spec_name / "_meta.json"
            if meta_file.exists():
                try:
                    with open(meta_file, 'r') as f:
                        meta = json.load(f)
                        if meta.get("status") == "IN_SCOPE":
                            # Check if recently modified (within last hour)
                            scope_date = meta.get("scope_date", "")
                            if scope_date:
                                try:
                                    scope_time = datetime.fromisoformat(scope_date)
                                    if (datetime.now() - scope_time).total_seconds() < 3600:
                                        return "scope"  # Recently started, keep in scope
                                except:
                                    pass
                            # Old scope item, probably should be completed
                            if "completed" in locations:
                                return "completed"
                except:
                    pass
        
        # Default to backlog if nothing else
        return "backlog"
    
    def cleanup_empty_folders(self):
        """Remove any empty spec folders"""
        print("\n[CLEANING] empty folders...")
        
        for location in ["backlog", "scope", "completed"]:
            location_dir = self.specs_dir / location
            if location_dir.exists():
                for spec_dir in location_dir.iterdir():
                    if spec_dir.is_dir():
                        # Check if folder is empty or only has metadata
                        files = list(spec_dir.iterdir())
                        if len(files) == 0:
                            print(f"  Removing empty folder: {location}/{spec_dir.name}")
                            spec_dir.rmdir()
                        elif len(files) == 1 and files[0].name in ["_meta.json", ".gitkeep"]:
                            print(f"  Removing nearly empty folder: {location}/{spec_dir.name}")
                            shutil.rmtree(spec_dir)
    
    def generate_report(self):
        """Generate cleanup report"""
        print("\n" + "=" * 70)
        print("CLEANUP REPORT")
        print("=" * 70)
        
        if self.fixed:
            print("\n[FIXED ISSUES]")
            for fix in self.fixed:
                print(f"  - {fix['spec']}: {fix['action']} (kept in {fix['kept']})")
        else:
            print("\n[NO FIXES APPLIED]")
        
        # Final state
        print("\n[FINAL STATE]")
        self.verify_spec_locations()
        
        print("\n" + "=" * 70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up and verify spec locations"
    )
    
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically fix issues without prompting'
    )
    
    parser.add_argument(
        '--clean-empty',
        action='store_true',
        help='Remove empty spec folders'
    )
    
    args = parser.parse_args()
    
    cleanup = SpecCleanup()
    
    # Verify current state
    is_clean = cleanup.verify_spec_locations()
    
    # Fix issues if found
    if not is_clean:
        cleanup.fix_duplicates(auto_fix=args.auto_fix)
    
    # Clean empty folders
    if args.clean_empty:
        cleanup.cleanup_empty_folders()
    
    # Generate report
    cleanup.generate_report()
    
    return 0 if is_clean or cleanup.fixed else 1


if __name__ == "__main__":
    exit(main())