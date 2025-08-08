#!/usr/bin/env python3
"""
Standard Workflow Launcher
Main entry point for executing spec workflows with full logging and integration
"""

import argparse
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

def print_banner():
    """Print workflow banner"""
    print("""
================================================================================
                     CLAUDE CODE WORKFLOW EXECUTOR                      
                    Context Engineering System v2.0                     
================================================================================
    """)

def list_available_specs():
    """List all available specs in backlog"""
    project_root = Path(__file__).parent.parent.parent
    backlog_path = project_root / ".claude/specs/backlog"
    
    if not backlog_path.exists():
        print("No backlog folder found")
        return []
    
    specs = []
    for spec_dir in backlog_path.iterdir():
        if spec_dir.is_dir():
            # Check for key files
            has_overview = (spec_dir / "overview.md").exists()
            has_requirements = (spec_dir / "requirements.md").exists()
            has_design = (spec_dir / "design.md").exists()
            
            spec_info = {
                "name": spec_dir.name,
                "complete": has_overview and has_requirements,
                "files": []
            }
            
            if has_overview:
                spec_info["files"].append("overview")
            if has_requirements:
                spec_info["files"].append("requirements")
            if has_design:
                spec_info["files"].append("design")
            
            specs.append(spec_info)
    
    return specs

def list_specs_in_progress():
    """List specs currently in scope"""
    project_root = Path(__file__).parent.parent.parent
    scope_path = project_root / ".claude/specs/scope"
    
    if not scope_path.exists():
        return []
    
    specs = []
    for spec_dir in scope_path.iterdir():
        if spec_dir.is_dir():
            meta_file = spec_dir / "_meta.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                specs.append({
                    "name": spec_dir.name,
                    "status": meta.get("status", "IN_SCOPE"),
                    "date": meta.get("scope_date", "Unknown")
                })
            else:
                specs.append({
                    "name": spec_dir.name,
                    "status": "IN_SCOPE",
                    "date": "Unknown"
                })
    
    return specs

def list_completed_specs():
    """List completed specs"""
    project_root = Path(__file__).parent.parent.parent
    completed_path = project_root / ".claude/specs/completed"
    
    if not completed_path.exists():
        return []
    
    specs = []
    for spec_dir in completed_path.iterdir():
        if spec_dir.is_dir():
            meta_file = spec_dir / "_meta.json"
            if not meta_file.exists():
                meta_file = spec_dir / "completion_meta.json"
            
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                specs.append({
                    "name": spec_dir.name,
                    "date": meta.get("completion_date", "Unknown"),
                    "location": meta.get("implementation_location", "Unknown")
                })
            else:
                specs.append({
                    "name": spec_dir.name,
                    "date": "Unknown",
                    "location": "Unknown"
                })
    
    return specs

def show_spec_status():
    """Show status of all specs"""
    print("\n[SPEC STATUS OVERVIEW]")
    print("=" * 70)
    
    # Backlog specs
    print("\n[BACKLOG] Ready to implement:")
    print("-" * 70)
    backlog_specs = list_available_specs()
    if backlog_specs:
        for spec in backlog_specs:
            status = "[READY]" if spec["complete"] else "[INCOMPLETE]"
            files = ", ".join(spec["files"]) if spec["files"] else "No files"
            print(f"  {status} {spec['name']:<30} Files: {files}")
    else:
        print("  No specs in backlog")
    
    # In Progress specs
    print("\n[IN PROGRESS] Currently being implemented:")
    print("-" * 70)
    scope_specs = list_specs_in_progress()
    if scope_specs:
        for spec in scope_specs:
            print(f"  [>] {spec['name']:<30} Started: {spec['date'][:10] if len(spec['date']) > 10 else spec['date']}")
    else:
        print("  No specs in progress")
    
    # Completed specs
    print("\n[COMPLETED]:")
    print("-" * 70)
    completed_specs = list_completed_specs()
    if completed_specs:
        for spec in completed_specs:
            print(f"  [v] {spec['name']:<30} Location: {spec['location']}")
    else:
        print("  No completed specs")
    
    print("\n" + "=" * 70)

async def run_workflow(args):
    """Run the selected workflow"""
    
    # Use the unified workflow executor
    from workflow_executor import WorkflowExecutor
    
    print(f"\n[STARTING] Workflow for: {args.spec}")
    print(f"   Implementation: implementations/{args.spec}/")
    
    # Create executor with appropriate settings
    enable_logging = not args.no_logging if hasattr(args, 'no_logging') else True
    executor = WorkflowExecutor(
        spec_name=args.spec,
        spec_folder=args.source,
        log_level=args.log_level,
        enable_logging=enable_logging
    )
    
    print(f"   Source: {args.source}")
    print(f"   Log Level: {args.log_level}")
    
    if args.dry_run:
        print("\n[WARNING] DRY RUN MODE - No changes will be made")
        print("\nWould execute with these settings:")
        print(f"  - Spec: {args.spec}")
        print(f"  - Source: {args.source}")
        print(f"  - Log Level: {args.log_level}")
        print(f"  - Logging: {'Enabled' if enable_logging else 'Disabled'}")
        return 0
    
    print("\n" + "-" * 70)
    
    # Execute workflow
    try:
        success = await executor.execute_workflow()
        
        if success:
            print("\n[SUCCESS] WORKFLOW COMPLETED SUCCESSFULLY")
            if hasattr(executor, 'logger'):
                print(f"\n[INFO] Logs saved to: .claude/logs/workflows/")
                if hasattr(executor.logger, 'summary_file'):
                    print(f"[INFO] Summary: {executor.logger.summary_file}")
            return 0
        else:
            print("\n[ERROR] WORKFLOW FAILED")
            return 1
            
    except Exception as e:
        print(f"\n[CRITICAL] ERROR: {str(e)}")
        import traceback
        if args.log_level == "DEBUG":
            traceback.print_exc()
        return 1

def main():
    """Main entry point"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Claude Code Workflow Executor - Execute spec workflows with full integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Show status of all specs
  python start_workflow.py --status
  
  # Run workflow for a spec
  python start_workflow.py user-auth
  
  # Run with debug logging
  python start_workflow.py user-auth --log-level DEBUG
  
  # Run without logging (faster)
  python start_workflow.py analytics-dashboard --no-logging
  
  # Dry run to see what would happen
  python start_workflow.py test-spec --dry-run
  
  # Resume a spec already in scope
  python start_workflow.py my-spec --source scope --resume
  
  # Check and fix duplicate specs
  python start_workflow.py --cleanup

WORKFLOW FEATURES:
  - Creates all code under implementations/{feature-name}/
  - Moves specs through lifecycle: backlog → scope → completed
  - Comprehensive logging and validation
  - Follows steering document standards
  - Clean, organized folder structure
        """
    )
    
    # Positional argument
    parser.add_argument(
        'spec',
        nargs='?',
        help='Name of the spec to process'
    )
    
    # Logging control
    parser.add_argument(
        '--no-logging',
        action='store_true',
        help='Disable logging (run faster without logs)'
    )
    
    # Source folder
    parser.add_argument(
        '--source', '-s',
        choices=['backlog', 'scope'],
        default='backlog',
        help='Source folder for the spec (default: backlog)'
    )
    
    # Log level
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    # Status display
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show status of all specs and exit'
    )
    
    # Cleanup check
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Check and fix duplicate specs across folders'
    )
    
    # Validate last workflow
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate the last workflow execution for the spec'
    )
    
    # List specs
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available specs in backlog and exit'
    )
    
    # Dry run
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show what would be executed without making changes'
    )
    
    # Resume flag
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume a spec already in scope (sets source to scope)'
    )
    
    args = parser.parse_args()
    
    # Handle status display
    if args.status:
        show_spec_status()
        return 0
    
    # Handle cleanup
    if args.cleanup:
        print("\n[CLEANUP] Checking for duplicate specs...")
        print("-" * 70)
        
        try:
            from spec_cleanup import SpecCleanup
            cleanup = SpecCleanup()
            is_clean = cleanup.verify_spec_locations()
            
            if not is_clean:
                print("\n[WARNING] Duplicate specs found!")
                response = input("Fix automatically? (y/N): ")
                if response.lower() == 'y':
                    cleanup.fix_duplicates(auto_fix=True)
                    cleanup.generate_report()
            else:
                print("\n[SUCCESS] No duplicate specs found!")
            
            return 0
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {str(e)}")
            return 1
    
    # Handle validation
    if args.validate:
        if not args.spec:
            print("[ERROR] No spec name provided for validation")
            print("Usage: python start_workflow.py <spec-name> --validate")
            return 1
        
        print(f"\n[VALIDATING] Last workflow for spec: {args.spec}")
        print("-" * 70)
        
        try:
            from workflow_validator import validate_latest_workflow
            results = validate_latest_workflow(args.spec)
            
            # Exit code based on health score
            if results["health_score"] >= 70:
                print(f"\n[SUCCESS] Validation passed with health score: {results['health_score']}/100")
                return 0
            else:
                print(f"\n[WARNING] Validation completed with issues. Health score: {results['health_score']}/100")
                return 1
        except Exception as e:
            print(f"[ERROR] Validation failed: {str(e)}")
            return 1
    
    # Handle list
    if args.list:
        print("\n[AVAILABLE SPECS IN BACKLOG]:")
        print("-" * 70)
        specs = list_available_specs()
        if specs:
            for spec in specs:
                status = "[OK]" if spec["complete"] else "[!] "
                print(f"  {status} {spec['name']}")
        else:
            print("  No specs found in backlog")
        print()
        return 0
    
    # Check if spec was provided
    if not args.spec:
        print("[ERROR] No spec name provided")
        print("\nUse --status to see available specs")
        print("Use --help for usage information")
        return 1
    
    # Handle resume flag
    if args.resume:
        args.source = 'scope'
        print(f"[RESUME] Resuming spec from scope: {args.spec}")
    
    # Validate spec exists
    project_root = Path(__file__).parent.parent.parent
    spec_path = project_root / f".claude/specs/{args.source}/{args.spec}"
    
    if not spec_path.exists():
        print(f"\n[ERROR] Spec '{args.spec}' not found in {args.source}")
        print(f"   Looked in: {spec_path}")
        
        # Suggest alternatives
        print("\n[TIP] Available specs in backlog:")
        specs = list_available_specs()
        for spec in specs[:5]:  # Show first 5
            print(f"   - {spec['name']}")
        
        if len(specs) > 5:
            print(f"   ... and {len(specs) - 5} more")
        
        print("\nUse --status to see all specs")
        return 1
    
    # Check spec completeness
    has_overview = (spec_path / "overview.md").exists()
    has_requirements = (spec_path / "requirements.md").exists()
    
    if not has_overview and not has_requirements:
        print(f"\n[WARNING] Spec '{args.spec}' appears incomplete")
        print(f"   Missing: overview.md and requirements.md")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 0
    
    # Run the workflow
    return asyncio.run(run_workflow(args))

if __name__ == "__main__":
    sys.exit(main())