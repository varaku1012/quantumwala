#!/usr/bin/env python3
"""
Real-time workflow monitoring and performance analysis
"""

import time
import json
import psutil
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import threading

@dataclass
class PerformanceMetric:
    timestamp: float
    phase: str
    agent: str
    duration: float
    cpu_usage: float
    memory_usage: float
    tokens_used: int
    success: bool
    error: Optional[str] = None

@dataclass
class WorkflowBottleneck:
    phase: str
    issue_type: str  # slow_execution, high_memory, high_tokens, failure
    severity: str    # low, medium, high, critical
    details: str
    recommendation: str

class WorkflowMonitor:
    """Monitors workflow execution and identifies bottlenecks"""
    
    def __init__(self, spec_name: str):
        self.spec_name = spec_name
        self.project_root = self._find_project_root()
        self.metrics: List[PerformanceMetric] = []
        self.bottlenecks: List[WorkflowBottleneck] = []
        self.start_time = time.time()
        self.monitoring = True
        
        # Performance thresholds
        self.thresholds = {
            'max_phase_duration': 300,  # 5 minutes
            'max_agent_duration': 120,  # 2 minutes
            'max_cpu_usage': 80,        # 80%
            'max_memory_usage': 70,     # 70%
            'max_tokens_per_task': 8000,
            'failure_rate_threshold': 0.2  # 20%
        }
        
        # Create monitoring directory
        self.monitor_dir = self.project_root / '.claude' / 'monitoring' / spec_name
        self.monitor_dir.mkdir(parents=True, exist_ok=True)
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    async def start_monitoring(self):
        """Start monitoring workflow execution"""
        print(f"🔍 Starting workflow monitoring for: {self.spec_name}")
        
        # Monitor different aspects in parallel
        await asyncio.gather(
            self._monitor_file_changes(),
            self._monitor_system_resources(),
            self._monitor_agent_executions(),
            self._analyze_performance()
        )
    
    async def _monitor_file_changes(self):
        """Monitor file changes in spec directory"""
        spec_dir = self.project_root / '.claude' / 'specs' / 'scope' / self.spec_name
        last_modified = {}
        
        while self.monitoring:
            try:
                for file in spec_dir.rglob('*'):
                    if file.is_file():
                        mtime = file.stat().st_mtime
                        if file not in last_modified or last_modified[file] < mtime:
                            last_modified[file] = mtime
                            self._log_file_change(file)
            except Exception as e:
                print(f"File monitoring error: {e}")
            
            await asyncio.sleep(1)
    
    async def _monitor_system_resources(self):
        """Monitor CPU and memory usage"""
        while self.monitoring:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            if cpu_percent > self.thresholds['max_cpu_usage']:
                self.bottlenecks.append(WorkflowBottleneck(
                    phase='system',
                    issue_type='high_cpu',
                    severity='high',
                    details=f'CPU usage: {cpu_percent}%',
                    recommendation='Consider reducing parallel agent execution'
                ))
            
            if memory.percent > self.thresholds['max_memory_usage']:
                self.bottlenecks.append(WorkflowBottleneck(
                    phase='system',
                    issue_type='high_memory',
                    severity='high',
                    details=f'Memory usage: {memory.percent}%',
                    recommendation='Implement context compression more aggressively'
                ))
            
            await asyncio.sleep(5)
    
    async def _monitor_agent_executions(self):
        """Monitor agent execution logs"""
        log_dir = self.project_root / '.claude' / 'logs' / 'execution'
        last_position = 0
        
        while self.monitoring:
            try:
                # Read latest execution log
                log_files = sorted(log_dir.glob('*.log'), key=lambda x: x.stat().st_mtime)
                if log_files:
                    latest_log = log_files[-1]
                    
                    with open(latest_log, 'r') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            self._parse_execution_log(line)
                            
            except Exception as e:
                print(f"Log monitoring error: {e}")
            
            await asyncio.sleep(2)
    
    async def _analyze_performance(self):
        """Analyze performance metrics and identify bottlenecks"""
        while self.monitoring:
            await asyncio.sleep(10)  # Analyze every 10 seconds
            
            if len(self.metrics) < 2:
                continue
            
            # Analyze phase durations
            phase_metrics = {}
            for metric in self.metrics:
                if metric.phase not in phase_metrics:
                    phase_metrics[metric.phase] = []
                phase_metrics[metric.phase].append(metric)
            
            for phase, metrics in phase_metrics.items():
                # Check average duration
                avg_duration = sum(m.duration for m in metrics) / len(metrics)
                if avg_duration > self.thresholds['max_agent_duration']:
                    self.bottlenecks.append(WorkflowBottleneck(
                        phase=phase,
                        issue_type='slow_execution',
                        severity='medium',
                        details=f'Average duration: {avg_duration:.2f}s',
                        recommendation=f'Optimize {phase} phase or split into smaller tasks'
                    ))
                
                # Check failure rate
                failures = sum(1 for m in metrics if not m.success)
                failure_rate = failures / len(metrics)
                if failure_rate > self.thresholds['failure_rate_threshold']:
                    self.bottlenecks.append(WorkflowBottleneck(
                        phase=phase,
                        issue_type='high_failure_rate',
                        severity='critical',
                        details=f'Failure rate: {failure_rate:.1%}',
                        recommendation='Review agent instructions and context quality'
                    ))
            
            # Save analysis
            self._save_analysis()
    
    def _log_file_change(self, file: Path):
        """Log when a file changes"""
        relative_path = file.relative_to(self.project_root)
        print(f"📝 File updated: {relative_path}")
    
    def _parse_execution_log(self, line: str):
        """Parse execution log line for metrics"""
        # Simple parsing - in production would be more robust
        if 'Executing command:' in line:
            # Extract command info
            pass
        elif 'Command completed successfully' in line:
            # Extract duration
            if 'in' in line and 's' in line:
                try:
                    duration = float(line.split('in')[1].split('s')[0].strip())
                    self.metrics.append(PerformanceMetric(
                        timestamp=time.time(),
                        phase='unknown',
                        agent='unknown',
                        duration=duration,
                        cpu_usage=psutil.cpu_percent(),
                        memory_usage=psutil.virtual_memory().percent,
                        tokens_used=0,  # Would need to parse from context
                        success=True
                    ))
                except:
                    pass
    
    def _save_analysis(self):
        """Save current analysis to file"""
        analysis = {
            'spec_name': self.spec_name,
            'monitoring_duration': time.time() - self.start_time,
            'total_metrics': len(self.metrics),
            'bottlenecks': [asdict(b) for b in self.bottlenecks[-10:]],  # Last 10
            'summary': self._generate_summary()
        }
        
        analysis_file = self.monitor_dir / 'analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
    
    def _generate_summary(self) -> Dict:
        """Generate performance summary"""
        if not self.metrics:
            return {'status': 'no_data'}
        
        return {
            'total_phases': len(set(m.phase for m in self.metrics)),
            'average_duration': sum(m.duration for m in self.metrics) / len(self.metrics),
            'success_rate': sum(1 for m in self.metrics if m.success) / len(self.metrics),
            'bottleneck_count': len(self.bottlenecks),
            'critical_issues': sum(1 for b in self.bottlenecks if b.severity == 'critical')
        }
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self._generate_final_report()
    
    def _generate_final_report(self):
        """Generate final monitoring report"""
        report = f"""# Workflow Monitoring Report

**Spec**: {self.spec_name}
**Duration**: {(time.time() - self.start_time) / 60:.1f} minutes
**Metrics Collected**: {len(self.metrics)}

## Performance Summary
{json.dumps(self._generate_summary(), indent=2)}

## Identified Bottlenecks
"""
        
        # Group bottlenecks by severity
        by_severity = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for bottleneck in self.bottlenecks:
            by_severity[bottleneck.severity].append(bottleneck)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if by_severity[severity]:
                report += f"\n### {severity.upper()} Priority\n"
                for b in by_severity[severity]:
                    report += f"- **{b.phase}** - {b.issue_type}: {b.details}\n"
                    report += f"  - Recommendation: {b.recommendation}\n"
        
        report += "\n## Enhancement Recommendations\n"
        report += self._generate_recommendations()
        
        # Save report
        report_file = self.monitor_dir / f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n✅ Monitoring report saved: {report_file}")
    
    def _generate_recommendations(self) -> str:
        """Generate enhancement recommendations based on monitoring"""
        recommendations = []
        
        # Analyze bottlenecks for patterns
        issue_types = [b.issue_type for b in self.bottlenecks]
        
        if issue_types.count('slow_execution') > 3:
            recommendations.append(
                "1. **Implement Task Batching**: Multiple agents are running slowly. "
                "Consider batching similar tasks to reduce overhead."
            )
        
        if issue_types.count('high_tokens') > 2:
            recommendations.append(
                "2. **Enhance Context Compression**: Token usage is high. "
                "Implement more aggressive context filtering based on task type."
            )
        
        if issue_types.count('high_failure_rate') > 0:
            recommendations.append(
                "3. **Improve Agent Instructions**: High failure rates detected. "
                "Review and clarify agent prompts, add more examples."
            )
        
        if issue_types.count('high_memory') > 0:
            recommendations.append(
                "4. **Optimize Memory Usage**: Implement streaming for large outputs "
                "and clear context between phases."
            )
        
        if not recommendations:
            recommendations.append(
                "No significant issues detected. Consider monitoring under higher load."
            )
        
        return '\n'.join(recommendations)

async def monitor_workflow(spec_name: str, duration_minutes: int = 10):
    """Monitor workflow for specified duration"""
    monitor = WorkflowMonitor(spec_name)
    
    # Run monitoring for specified duration
    monitoring_task = asyncio.create_task(monitor.start_monitoring())
    
    # Wait for duration
    await asyncio.sleep(duration_minutes * 60)
    
    # Stop monitoring
    monitor.stop_monitoring()
    monitoring_task.cancel()
    
    return monitor

if __name__ == "__main__":
    # Example usage
    asyncio.run(monitor_workflow('auth-test', duration_minutes=5))