#!/usr/bin/env python3
"""
Simple workflow monitoring without external dependencies
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class SimpleMetric:
    timestamp: float
    phase: str
    event: str
    duration: float = 0.0
    details: str = ""

@dataclass 
class Enhancement:
    category: str
    issue: str
    recommendation: str
    priority: str  # low, medium, high

class SimpleWorkflowMonitor:
    """Lightweight workflow monitor"""
    
    def __init__(self, spec_name: str):
        self.spec_name = spec_name
        self.project_root = self._find_project_root()
        self.metrics: List[SimpleMetric] = []
        self.enhancements: List[Enhancement] = []
        self.start_time = time.time()
        
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
    
    def log_phase_start(self, phase: str):
        """Log when a phase starts"""
        self.metrics.append(SimpleMetric(
            timestamp=time.time(),
            phase=phase,
            event='phase_start',
            details=f"Starting {phase}"
        ))
        print(f"[LOG] Phase started: {phase}")
    
    def log_phase_complete(self, phase: str, duration: float):
        """Log when a phase completes"""
        self.metrics.append(SimpleMetric(
            timestamp=time.time(),
            phase=phase,
            event='phase_complete',
            duration=duration,
            details=f"Completed {phase} in {duration:.2f}s"
        ))
        
        # Check for performance issues
        if duration > 30:  # More than 30 seconds
            self.enhancements.append(Enhancement(
                category='performance',
                issue=f'{phase} took {duration:.2f}s',
                recommendation=f'Optimize {phase} by parallelizing subtasks',
                priority='medium' if duration < 60 else 'high'
            ))
    
    def log_file_created(self, file_path: Path):
        """Log when a file is created"""
        self.metrics.append(SimpleMetric(
            timestamp=time.time(),
            phase='file_operation',
            event='file_created',
            details=str(file_path)
        ))
    
    def analyze_workflow(self):
        """Analyze workflow and generate recommendations"""
        # Analyze phase durations
        phase_durations = {}
        for metric in self.metrics:
            if metric.event == 'phase_complete':
                phase_durations[metric.phase] = metric.duration
        
        # Check for workflow issues
        total_duration = time.time() - self.start_time
        
        if total_duration > 300:  # More than 5 minutes
            self.enhancements.append(Enhancement(
                category='workflow',
                issue='Total workflow duration exceeds 5 minutes',
                recommendation='Consider breaking into smaller workflows',
                priority='medium'
            ))
        
        # Check for missing context optimization
        if not any('context' in m.details.lower() for m in self.metrics):
            self.enhancements.append(Enhancement(
                category='context',
                issue='No context optimization detected',
                recommendation='Implement context compression for agents',
                priority='high'
            ))
        
        # Check for parallel execution opportunities
        sequential_phases = ['spec-create', 'spec-requirements', 'spec-design']
        sequential_duration = sum(phase_durations.get(p, 0) for p in sequential_phases)
        if sequential_duration > 60:
            self.enhancements.append(Enhancement(
                category='parallelization',
                issue='Sequential phases taking too long',
                recommendation='Run requirements and design analysis in parallel',
                priority='high'
            ))
    
    def generate_report(self) -> str:
        """Generate monitoring report"""
        self.analyze_workflow()
        
        report = f"""# Workflow Monitoring Report

**Spec**: {self.spec_name}
**Duration**: {(time.time() - self.start_time):.2f} seconds
**Phases Completed**: {len([m for m in self.metrics if m.event == 'phase_complete'])}

## Workflow Timeline
"""
        
        # Add timeline
        for metric in self.metrics:
            if metric.event in ['phase_start', 'phase_complete']:
                time_offset = metric.timestamp - self.start_time
                report += f"- **{time_offset:6.2f}s** | {metric.event:15} | {metric.phase}\n"
        
        report += "\n## Performance Enhancements\n\n"
        
        # Group enhancements by priority
        by_priority = {'high': [], 'medium': [], 'low': []}
        for e in self.enhancements:
            by_priority[e.priority].append(e)
        
        for priority in ['high', 'medium', 'low']:
            if by_priority[priority]:
                report += f"### {priority.upper()} Priority\n\n"
                for e in by_priority[priority]:
                    report += f"**{e.category}**: {e.issue}\n"
                    report += f"- Recommendation: {e.recommendation}\n\n"
        
        # Save report
        report_file = self.monitor_dir / f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        report_file.write_text(report)
        
        # Save metrics
        metrics_file = self.monitor_dir / 'metrics.json'
        with open(metrics_file, 'w') as f:
            json.dump({
                'metrics': [asdict(m) for m in self.metrics],
                'enhancements': [asdict(e) for e in self.enhancements]
            }, f, indent=2)
        
        return report