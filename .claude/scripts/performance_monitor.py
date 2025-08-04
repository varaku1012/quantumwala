#!/usr/bin/env python3
"""
Performance monitoring system for Claude Code multi-agent system
Tracks execution times, resource usage, and system performance

---
name: performance-monitor
version: 1.1.0
created: 2025-08-03
updated: 2025-08-03
changelog:
  - "1.0.0: Initial performance monitoring implementation"
  - "1.1.0: Added real-time dashboard integration"
dependencies:
  - psutil>=5.9.0
  - python>=3.7
---
"""

import json
import time
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

class PerformanceMonitor:
    """Real-time performance monitoring for multi-agent system"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.metrics_file = self.claude_dir / 'performance_metrics.json'
        self.metrics_log = self.claude_dir / 'logs' / 'performance' / f'perf_{datetime.now().strftime("%Y%m%d")}.jsonl'
        
        # In-memory metrics storage
        self.metrics = {
            'agent_executions': defaultdict(list),
            'command_executions': defaultdict(list),
            'resource_usage': deque(maxlen=1000),  # Keep last 1000 samples
            'task_completions': defaultdict(list),
            'errors': defaultdict(int),
            'session_start': datetime.now().isoformat()
        }
        
        # Ensure directories exist
        self.metrics_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing metrics if available
        self._load_metrics()
        
    def _find_project_root(self):
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_metrics(self):
        """Load existing metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    saved_metrics = json.load(f)
                    # Merge with current metrics
                    for key in ['agent_executions', 'command_executions', 'task_completions']:
                        if key in saved_metrics:
                            for k, v in saved_metrics[key].items():
                                self.metrics[key][k].extend(v)
            except Exception as e:
                print(f"Error loading metrics: {e}")
    
    def _save_metrics(self):
        """Save current metrics to file"""
        try:
            # Convert defaultdict to dict for JSON serialization
            serializable_metrics = {
                'agent_executions': dict(self.metrics['agent_executions']),
                'command_executions': dict(self.metrics['command_executions']),
                'task_completions': dict(self.metrics['task_completions']),
                'errors': dict(self.metrics['errors']),
                'session_start': self.metrics['session_start'],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_metrics, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def track_agent_execution(self, agent_name, duration, success=True, tokens_used=0):
        """Track agent execution metrics"""
        execution_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'success': success,
            'tokens_used': tokens_used
        }
        
        self.metrics['agent_executions'][agent_name].append(execution_data)
        
        # Log to file
        self._log_metric({
            'type': 'agent_execution',
            'agent': agent_name,
            **execution_data
        })
        
        # Save periodically
        if len(self.metrics['agent_executions'][agent_name]) % 10 == 0:
            self._save_metrics()
    
    def track_command_execution(self, command_name, duration, success=True):
        """Track command execution metrics"""
        execution_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'success': success
        }
        
        self.metrics['command_executions'][command_name].append(execution_data)
        
        # Log to file
        self._log_metric({
            'type': 'command_execution',
            'command': command_name,
            **execution_data
        })
    
    def track_task_completion(self, spec_name, task_id, duration):
        """Track task completion metrics"""
        completion_data = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'duration': duration
        }
        
        self.metrics['task_completions'][spec_name].append(completion_data)
        
        # Log to file
        self._log_metric({
            'type': 'task_completion',
            'spec': spec_name,
            **completion_data
        })
    
    def track_error(self, component, error_type):
        """Track error occurrences"""
        error_key = f"{component}:{error_type}"
        self.metrics['errors'][error_key] += 1
        
        # Log to file
        self._log_metric({
            'type': 'error',
            'component': component,
            'error_type': error_type,
            'timestamp': datetime.now().isoformat()
        })
    
    def track_resource_usage(self):
        """Track system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.project_root))
            
            usage_data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_mb': memory.used / (1024 * 1024),
                'disk_percent': disk.percent
            }
            
            self.metrics['resource_usage'].append(usage_data)
            
            # Log high resource usage
            if cpu_percent > 80 or memory.percent > 80:
                self._log_metric({
                    'type': 'high_resource_usage',
                    **usage_data
                })
            
        except Exception as e:
            print(f"Error tracking resources: {e}")
    
    def _log_metric(self, metric_data):
        """Log metric to file"""
        try:
            with open(self.metrics_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metric_data) + '\n')
        except Exception as e:
            print(f"Error logging metric: {e}")
    
    def get_performance_summary(self):
        """Get performance summary statistics"""
        summary = {
            'agents': {},
            'commands': {},
            'tasks': {},
            'resources': {},
            'errors': dict(self.metrics['errors']),
            'session_duration': str(datetime.now() - datetime.fromisoformat(self.metrics['session_start']))
        }
        
        # Agent performance
        for agent, executions in self.metrics['agent_executions'].items():
            if executions:
                durations = [e['duration'] for e in executions]
                success_rate = sum(1 for e in executions if e['success']) / len(executions) * 100
                tokens = sum(e.get('tokens_used', 0) for e in executions)
                
                summary['agents'][agent] = {
                    'executions': len(executions),
                    'avg_duration': round(statistics.mean(durations), 2),
                    'max_duration': round(max(durations), 2),
                    'success_rate': round(success_rate, 1),
                    'total_tokens': tokens
                }
        
        # Command performance
        for command, executions in self.metrics['command_executions'].items():
            if executions:
                durations = [e['duration'] for e in executions]
                success_rate = sum(1 for e in executions if e['success']) / len(executions) * 100
                
                summary['commands'][command] = {
                    'executions': len(executions),
                    'avg_duration': round(statistics.mean(durations), 2),
                    'success_rate': round(success_rate, 1)
                }
        
        # Task performance
        for spec, completions in self.metrics['task_completions'].items():
            if completions:
                durations = [c['duration'] for c in completions]
                
                summary['tasks'][spec] = {
                    'completed': len(completions),
                    'avg_duration': round(statistics.mean(durations), 2),
                    'total_time': round(sum(durations), 2)
                }
        
        # Resource usage
        if self.metrics['resource_usage']:
            recent_usage = list(self.metrics['resource_usage'])[-100:]  # Last 100 samples
            
            summary['resources'] = {
                'avg_cpu': round(statistics.mean(u['cpu_percent'] for u in recent_usage), 1),
                'max_cpu': round(max(u['cpu_percent'] for u in recent_usage), 1),
                'avg_memory': round(statistics.mean(u['memory_percent'] for u in recent_usage), 1),
                'max_memory': round(max(u['memory_percent'] for u in recent_usage), 1),
                'current_memory_mb': round(recent_usage[-1]['memory_mb'], 1) if recent_usage else 0
            }
        
        return summary
    
    def generate_performance_report(self):
        """Generate a detailed performance report"""
        summary = self.get_performance_summary()
        
        report = f"""# Performance Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Session Duration**: {summary['session_duration']}

## Agent Performance

| Agent | Executions | Avg Duration | Max Duration | Success Rate | Total Tokens |
|-------|------------|--------------|--------------|--------------|--------------|
"""
        
        for agent, stats in sorted(summary['agents'].items()):
            report += f"| {agent} | {stats['executions']} | {stats['avg_duration']}s | {stats['max_duration']}s | {stats['success_rate']}% | {stats['total_tokens']} |\n"
        
        report += f"""
## Command Performance

| Command | Executions | Avg Duration | Success Rate |
|---------|------------|--------------|--------------|
"""
        
        for command, stats in sorted(summary['commands'].items()):
            report += f"| {command} | {stats['executions']} | {stats['avg_duration']}s | {stats['success_rate']}% |\n"
        
        report += f"""
## Task Completion

| Specification | Tasks Completed | Avg Duration | Total Time |
|---------------|-----------------|--------------|------------|
"""
        
        for spec, stats in sorted(summary['tasks'].items()):
            report += f"| {spec} | {stats['completed']} | {stats['avg_duration']}s | {stats['total_time']}s |\n"
        
        report += f"""
## Resource Usage

- **Average CPU**: {summary['resources'].get('avg_cpu', 'N/A')}%
- **Maximum CPU**: {summary['resources'].get('max_cpu', 'N/A')}%
- **Average Memory**: {summary['resources'].get('avg_memory', 'N/A')}%
- **Maximum Memory**: {summary['resources'].get('max_memory', 'N/A')}%
- **Current Memory**: {summary['resources'].get('current_memory_mb', 'N/A')} MB

## Error Summary

"""
        
        if summary['errors']:
            report += "| Component | Error Type | Count |\n|-----------|------------|-------|\n"
            for error_key, count in sorted(summary['errors'].items()):
                component, error_type = error_key.split(':', 1)
                report += f"| {component} | {error_type} | {count} |\n"
        else:
            report += "No errors recorded.\n"
        
        report += f"""
## Recommendations

"""
        
        # Add recommendations based on metrics
        recommendations = []
        
        # Check for slow agents
        for agent, stats in summary['agents'].items():
            if stats['avg_duration'] > 10:
                recommendations.append(f"- {agent} has high average execution time ({stats['avg_duration']}s). Consider optimization.")
        
        # Check for high error rates
        if summary['errors']:
            total_errors = sum(summary['errors'].values())
            if total_errors > 10:
                recommendations.append(f"- High error count ({total_errors}). Review error logs for patterns.")
        
        # Check resource usage
        if summary['resources'].get('avg_cpu', 0) > 70:
            recommendations.append(f"- High average CPU usage ({summary['resources']['avg_cpu']}%). Consider performance optimization.")
        
        if summary['resources'].get('avg_memory', 0) > 70:
            recommendations.append(f"- High average memory usage ({summary['resources']['avg_memory']}%). Monitor for memory leaks.")
        
        if recommendations:
            report += '\n'.join(recommendations)
        else:
            report += "- System performance is within normal parameters."
        
        return report
    
    def start_monitoring(self, interval=60):
        """Start continuous resource monitoring"""
        def monitor_loop():
            while True:
                self.track_resource_usage()
                time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print(f"Performance monitoring started (interval: {interval}s)")
    
    def export_metrics(self, output_file=None):
        """Export metrics to file"""
        if output_file is None:
            output_file = self.claude_dir / 'logs' / 'reports' / f'performance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare exportable data
        export_data = {
            'export_time': datetime.now().isoformat(),
            'session_info': {
                'start': self.metrics['session_start'],
                'duration': str(datetime.now() - datetime.fromisoformat(self.metrics['session_start']))
            },
            'summary': self.get_performance_summary(),
            'raw_metrics': {
                'agent_executions': dict(self.metrics['agent_executions']),
                'command_executions': dict(self.metrics['command_executions']),
                'task_completions': dict(self.metrics['task_completions']),
                'errors': dict(self.metrics['errors'])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Metrics exported to: {output_file}")
        return output_file


# Decorator for tracking function execution time
def track_performance(component_type='function', component_name=None):
    """Decorator to track performance of functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            result = None
            
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                success = False
                # Get or create monitor instance
                monitor = getattr(wrapper, '_monitor', None)
                if monitor is None:
                    monitor = PerformanceMonitor()
                    wrapper._monitor = monitor
                
                monitor.track_error(
                    component_name or func.__name__,
                    type(e).__name__
                )
                raise
            finally:
                duration = time.time() - start_time
                
                # Get or create monitor instance
                monitor = getattr(wrapper, '_monitor', None)
                if monitor is None:
                    monitor = PerformanceMonitor()
                    wrapper._monitor = monitor
                
                if component_type == 'agent':
                    monitor.track_agent_execution(
                        component_name or func.__name__,
                        duration,
                        success
                    )
                elif component_type == 'command':
                    monitor.track_command_execution(
                        component_name or func.__name__,
                        duration,
                        success
                    )
            
            return result
        
        return wrapper
    return decorator


def main():
    """Main function for testing and generating reports"""
    monitor = PerformanceMonitor()
    
    # Start continuous monitoring
    monitor.start_monitoring(interval=30)
    
    # Generate and save report
    report = monitor.generate_performance_report()
    report_file = monitor.claude_dir / 'logs' / 'reports' / f'performance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report, encoding='utf-8')
    
    print(f"Performance report generated: {report_file}")
    print("\nSummary:")
    print(json.dumps(monitor.get_performance_summary(), indent=2))
    
    # Export metrics
    monitor.export_metrics()


if __name__ == "__main__":
    main()