#!/usr/bin/env python3
"""
Real workflow executor with parallel monitoring
Executes actual Claude Code commands and monitors performance
"""

import asyncio
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from real_executor import RealClaudeExecutor, ExecutionResult
from simple_workflow_monitor import SimpleWorkflowMonitor
from task_orchestrator import EnhancedTaskOrchestrator

class RealWorkflowExecutor:
    """Executes real workflow with monitoring"""
    
    def __init__(self, spec_name: str, description: str):
        self.spec_name = spec_name
        self.description = description
        self.project_root = self._find_project_root()
        self.executor = RealClaudeExecutor(self.project_root)
        self.monitor = SimpleWorkflowMonitor(spec_name)
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    async def run_workflow(self):
        """Execute the real dev-workflow command"""
        print(f"[START] Starting REAL dev-workflow execution")
        print(f"Spec: {self.spec_name}")
        print(f"Description: {self.description}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Phase 1: Use dev-workflow command to execute through chief-product-manager
        print("\n[PHASE 1] Executing dev-workflow through chief-product-manager")
        self.monitor.log_phase_start("dev-workflow")
        
        # Prepare the command
        workflow_command = f'/dev-workflow "{self.description}"'
        
        print(f"Executing: {workflow_command}")
        
        try:
            # Execute the real command
            result = await self.executor.execute_command(
                workflow_command,
                timeout=1800  # 30 minutes timeout
            )
            
            if result.success:
                print(f"\n[SUCCESS] Dev-workflow completed successfully!")
                print(f"Duration: {result.duration:.2f}s")
                self.monitor.log_phase_complete("dev-workflow", result.duration)
                
                # Phase 2: Check if spec was created
                spec_dir = self.project_root / '.claude' / 'specs' / self.spec_name
                if spec_dir.exists():
                    print(f"\n[VERIFIED] Spec created at: {spec_dir}")
                    
                    # Phase 3: Run task orchestration if tasks exist
                    tasks_file = spec_dir / 'tasks.md'
                    if tasks_file.exists():
                        print(f"\n[PHASE 3] Running task orchestration")
                        self.monitor.log_phase_start("task-orchestration")
                        
                        orchestrator = EnhancedTaskOrchestrator(self.spec_name)
                        orchestration_success = await orchestrator.orchestrate_real()
                        
                        orchestration_duration = time.time() - start_time - result.duration
                        self.monitor.log_phase_complete("task-orchestration", orchestration_duration)
                        
                        if orchestration_success:
                            print(f"\n[SUCCESS] Task orchestration completed!")
                        else:
                            print(f"\n[WARNING] Some tasks failed during orchestration")
                else:
                    print(f"\n[ERROR] Spec directory not created at expected location")
                    
            else:
                print(f"\n[FAILED] Dev-workflow execution failed")
                print(f"Error: {result.error}")
                self.monitor.log_phase_complete("dev-workflow", result.duration)
                
        except Exception as e:
            print(f"\n[ERROR] Exception during workflow execution: {e}")
            duration = time.time() - start_time
            self.monitor.log_phase_complete("dev-workflow", duration)
            raise
        
        total_duration = time.time() - start_time
        print(f"\n[COMPLETE] Total workflow duration: {total_duration:.2f}s")
        
        return total_duration
    
    async def monitor_performance(self):
        """Monitor workflow performance"""
        print(f"\n[MONITOR] Starting performance monitoring")
        
        # Monitor spec directory for changes
        spec_dir = self.project_root / '.claude' / 'specs' / self.spec_name
        
        while True:
            try:
                # Check for new files
                if spec_dir.exists():
                    for file in spec_dir.rglob('*'):
                        if file.is_file():
                            self.monitor.log_file_created(file)
                
                # Check resource usage (simplified)
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[MONITOR] Error: {e}")
                await asyncio.sleep(2)
    
    async def run(self):
        """Run workflow and monitoring in parallel"""
        print(f"""
==================================================================
      REAL WORKFLOW EXECUTION WITH MONITORING               
==================================================================
 Spec: {self.spec_name}
 Description: {self.description}
 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================================
        """)
        
        # Create tasks
        workflow_task = asyncio.create_task(self.run_workflow())
        monitor_task = asyncio.create_task(self.monitor_performance())
        
        try:
            # Wait for workflow to complete
            duration = await workflow_task
            
            # Stop monitoring
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            
            # Generate report
            print("\n" + "=" * 60)
            print("EXECUTION REPORT")
            print("=" * 60)
            
            report = self.monitor.generate_report()
            print(report)
            
            # Check results
            self._verify_results()
            
        except Exception as e:
            print(f"\n[ERROR] Workflow execution failed: {e}")
            monitor_task.cancel()
            raise
    
    def _verify_results(self):
        """Verify that real code was generated"""
        print("\n[VERIFICATION] Checking generated code...")
        
        spec_dir = self.project_root / '.claude' / 'specs' / self.spec_name
        
        if not spec_dir.exists():
            print("[ERROR] Spec directory not found!")
            return
        
        # Check for key files
        expected_files = ['overview.md', 'requirements.md', 'design.md', 'tasks.md']
        found_files = []
        
        for file_name in expected_files:
            file_path = spec_dir / file_name
            if file_path.exists():
                found_files.append(file_name)
                size = file_path.stat().st_size
                print(f"[FOUND] {file_name} ({size} bytes)")
        
        print(f"\n[SUMMARY] Found {len(found_files)}/{len(expected_files)} expected files")
        
        # Check for implementation files
        print("\n[CHECKING] Implementation files...")
        impl_files = list(self.project_root.rglob('*.py'))
        new_impl_files = [f for f in impl_files if self.spec_name in str(f)]
        
        if new_impl_files:
            print(f"[FOUND] {len(new_impl_files)} implementation files:")
            for f in new_impl_files[:5]:  # Show first 5
                print(f"  - {f.relative_to(self.project_root)}")
        else:
            print("[INFO] No implementation files found yet (may be in progress)")
        
        # Check monitoring results
        monitor_dir = self.project_root / '.claude' / 'monitoring' / self.spec_name
        if monitor_dir.exists():
            print(f"\n[MONITORING] Results saved to: {monitor_dir}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Execute real workflow with monitoring')
    parser.add_argument('--spec', default='user-auth', help='Spec name')
    parser.add_argument('--description', default='User authentication system with 2FA support', 
                       help='Feature description')
    
    args = parser.parse_args()
    
    # Run the real executor
    executor = RealWorkflowExecutor(args.spec, args.description)
    
    try:
        asyncio.run(executor.run())
        print("\n[SUCCESS] Real workflow execution completed!")
    except Exception as e:
        print(f"\n[FAILED] Workflow execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()