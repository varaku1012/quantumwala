#!/usr/bin/env python3
"""
Parallel workflow execution and monitoring
Runs dev-workflow while monitoring performance
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from simple_workflow_monitor import SimpleWorkflowMonitor

class ParallelWorkflowTest:
    """Runs workflow and monitoring in parallel"""
    
    def __init__(self, spec_name: str):
        self.spec_name = spec_name
        self.project_root = self._find_project_root()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    async def run_workflow(self, monitor):
        """Run the dev-workflow command"""
        print(f"[START] Starting dev-workflow for: {self.spec_name}")
        
        # Check if the command exists
        spec_command = f"/spec-create {self.spec_name}"
        
        # Simulate workflow execution (in real implementation, would use real_executor)
        # For now, let's create a mock workflow execution
        workflow_phases = [
            ("spec-create", 3),
            ("spec-requirements", 5),
            ("spec-design", 8),
            ("spec-tasks", 4),
            ("implementation", 10),
            ("testing", 6)
        ]
        
        for phase, duration in workflow_phases:
            print(f"\n[PHASE] Executing phase: {phase}")
            phase_start = time.time()
            monitor.log_phase_start(phase)
            
            # Simulate work
            await asyncio.sleep(duration)
            
            # Create some output files to trigger monitoring
            output_dir = self.project_root / '.claude' / 'specs' / 'scope' / self.spec_name
            output_file = output_dir / f"{phase}_output.md"
            output_file.write_text(f"# {phase} Output\n\nGenerated at {datetime.now()}")
            monitor.log_file_created(output_file)
            
            phase_duration = time.time() - phase_start
            monitor.log_phase_complete(phase, phase_duration)
            print(f"[DONE] Phase {phase} completed in {phase_duration:.2f}s")
    
    async def run_monitoring(self, monitor):
        """Run workflow monitoring"""
        print(f"[MONITOR] Starting performance monitoring")
        
        # Simple monitoring - just wait
        while True:
            await asyncio.sleep(1)
    
    async def run(self):
        """Run workflow and monitoring in parallel"""
        print(f"""
==================================================================
     PARALLEL WORKFLOW EXECUTION AND MONITORING               
==================================================================
 Spec: {self.spec_name}
 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================================
        """)
        
        # Create monitor
        monitor = SimpleWorkflowMonitor(self.spec_name)
        
        # Create tasks
        workflow_task = asyncio.create_task(self.run_workflow(monitor))
        monitor_task = asyncio.create_task(self.run_monitoring(monitor))
        
        # Run workflow to completion
        await workflow_task
        
        # Stop monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        print("\n[COMPLETE] Parallel execution completed!")
        
        # Generate and show report
        report = monitor.generate_report()
        print("\n" + report)
        
        # Show monitoring results
        self._show_results()
    
    def _show_results(self):
        """Display monitoring results"""
        monitor_dir = self.project_root / '.claude' / 'monitoring' / self.spec_name
        analysis_file = monitor_dir / 'analysis.json'
        
        if analysis_file.exists():
            import json
            with open(analysis_file) as f:
                analysis = json.load(f)
            
            print("\n📊 PERFORMANCE ANALYSIS:")
            print(f"Duration: {analysis['monitoring_duration'] / 60:.1f} minutes")
            print(f"Bottlenecks found: {len(analysis['bottlenecks'])}")
            
            if analysis['bottlenecks']:
                print("\n🚨 BOTTLENECKS:")
                for b in analysis['bottlenecks'][:5]:  # Show top 5
                    print(f"- {b['severity'].upper()}: {b['issue_type']} in {b['phase']}")
                    print(f"  Details: {b['details']}")
                    print(f"  Fix: {b['recommendation']}")
            
            # Find the latest report
            reports = list(monitor_dir.glob('report_*.md'))
            if reports:
                latest_report = sorted(reports)[-1]
                print(f"\n📄 Full report: {latest_report}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run workflow with parallel monitoring')
    parser.add_argument('--spec', default='auth-test', help='Spec name to run')
    
    args = parser.parse_args()
    
    # Run the parallel test
    tester = ParallelWorkflowTest(args.spec)
    asyncio.run(tester.run())

if __name__ == "__main__":
    main()