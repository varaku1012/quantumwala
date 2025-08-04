#!/usr/bin/env python3
"""
Enhanced dashboard for Claude Code multi-agent system
Features:
- Real-time metrics and analytics
- Task execution timeline
- Agent activity monitoring
- Performance metrics
- Log analysis
- Interactive UI with charts

---
name: enhanced-dashboard
version: 2.0.0
created: 2025-08-03
updated: 2025-08-03
changelog:
  - "1.0.0: Basic dashboard with project metrics"
  - "1.5.0: Added agent activity and timeline"
  - "2.0.0: Integrated performance monitoring and modern UI"
dependencies:
  - python>=3.7
  - performance_monitor (optional)
---
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import webbrowser
import threading
import time
import re
from collections import defaultdict, Counter
import sys
sys.path.append(str(Path(__file__).parent))
try:
    from performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None

def find_project_root():
    """Find project root by looking for .claude directory"""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.claude').exists():
            return current
        current = current.parent
    return Path.cwd()

class EnhancedDashboard:
    def __init__(self):
        self.project_root = find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.logs_dir = self.claude_dir / 'logs'
        self.performance_monitor = PerformanceMonitor() if PerformanceMonitor else None
        
    def collect_metrics(self):
        """Collect comprehensive metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'project': self._get_project_info(),
            'resources': self._get_resource_counts(),
            'specifications': self._get_specs_info(),
            'agent_activity': self._analyze_agent_activity(),
            'task_timeline': self._get_task_timeline(),
            'performance': self._calculate_performance_metrics(),
            'logs': self._analyze_logs(),
            'steering': self._get_steering_status(),
            'real_time_performance': self._get_real_time_performance()
        }
        return metrics
    
    def _get_project_info(self):
        """Get project information"""
        project_state_path = self.claude_dir / 'project-state.json'
        if project_state_path.exists():
            with open(project_state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return state.get('project', {})
        return {}
    
    def _get_resource_counts(self):
        """Count system resources"""
        return {
            'agents': len(list((self.claude_dir / 'agents').glob('*.md'))) if (self.claude_dir / 'agents').exists() else 0,
            'commands': len(list((self.claude_dir / 'commands').glob('*.md'))) if (self.claude_dir / 'commands').exists() else 0,
            'scripts': len(list((self.claude_dir / 'scripts').glob('*.py'))) if (self.claude_dir / 'scripts').exists() else 0,
            'templates': len(list((self.claude_dir / 'templates').glob('*.md'))) if (self.claude_dir / 'templates').exists() else 0,
            'hooks': len(list((self.claude_dir / 'hooks').glob('*'))) if (self.claude_dir / 'hooks').exists() else 0
        }
    
    def _get_specs_info(self):
        """Get detailed specification information"""
        specs_info = []
        specs_dir = self.claude_dir / 'specs'
        if specs_dir.exists():
            for spec_dir in specs_dir.iterdir():
                if spec_dir.is_dir():
                    spec_data = {
                        'name': spec_dir.name,
                        'tasks': self._analyze_tasks(spec_dir),
                        'files': len(list(spec_dir.glob('*.md'))),
                        'created': datetime.fromtimestamp(spec_dir.stat().st_ctime).strftime('%Y-%m-%d'),
                        'status': self._determine_spec_status(spec_dir)
                    }
                    specs_info.append(spec_data)
        return specs_info
    
    def _analyze_tasks(self, spec_dir):
        """Analyze tasks in a specification"""
        tasks_file = spec_dir / 'tasks.md'
        if not tasks_file.exists():
            return {'total': 0, 'completed': 0, 'in_progress': 0, 'pending': 0, 'progress': 0}
        
        content = tasks_file.read_text(encoding='utf-8')
        total = content.count('- [ ]') + content.count('- [x]')
        completed = content.count('- [x]')
        
        # Try to detect in-progress tasks (marked with arrow or similar)
        in_progress = content.count('- [ ] →') + content.count('- [ ] ▶')
        pending = total - completed - in_progress
        
        progress = round((completed / total * 100) if total > 0 else 0, 1)
        
        return {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'pending': pending,
            'progress': progress
        }
    
    def _determine_spec_status(self, spec_dir):
        """Determine specification status"""
        tasks = self._analyze_tasks(spec_dir)
        if tasks['total'] == 0:
            return 'planning'
        elif tasks['progress'] == 100:
            return 'completed'
        elif tasks['in_progress'] > 0 or tasks['completed'] > 0:
            return 'active'
        else:
            return 'pending'
    
    def _analyze_agent_activity(self):
        """Analyze agent activity from logs"""
        activity = defaultdict(int)
        recent_logs = self._get_recent_logs(hours=24)
        
        agent_patterns = {
            'product-manager': r'product[\s-]?manager',
            'business-analyst': r'business[\s-]?analyst',
            'architect': r'architect',
            'developer': r'developer',
            'qa-engineer': r'qa[\s-]?engineer',
            'code-reviewer': r'code[\s-]?reviewer',
            'uiux-designer': r'ui/?ux[\s-]?designer',
            'chief-product-manager': r'chief[\s-]?product[\s-]?manager'
        }
        
        for log_content in recent_logs:
            for agent, pattern in agent_patterns.items():
                if re.search(pattern, log_content, re.IGNORECASE):
                    activity[agent] += 1
        
        return dict(activity)
    
    def _get_task_timeline(self):
        """Get task execution timeline"""
        timeline = []
        sessions_dir = self.logs_dir / 'sessions'
        
        if sessions_dir.exists():
            for session_file in sorted(sessions_dir.glob('*.md'), key=lambda x: x.stat().st_mtime)[-10:]:
                try:
                    content = session_file.read_text(encoding='utf-8')
                    # Extract task completions
                    task_pattern = r'(?:Completed|Finished|Done):\s*(.+?)(?:\n|$)'
                    tasks = re.findall(task_pattern, content, re.IGNORECASE)
                    
                    if tasks:
                        timestamp = datetime.fromtimestamp(session_file.stat().st_mtime)
                        timeline.append({
                            'date': timestamp.strftime('%Y-%m-%d %H:%M'),
                            'tasks': tasks[:3]  # Show max 3 tasks per session
                        })
                except Exception:
                    pass
        
        return timeline[-5:]  # Return last 5 entries
    
    def _calculate_performance_metrics(self):
        """Calculate performance metrics"""
        metrics = {
            'avg_task_completion_time': 'N/A',
            'total_tasks_24h': 0,
            'active_sessions': 0,
            'efficiency_score': 0
        }
        
        # Count tasks completed in last 24 hours
        recent_logs = self._get_recent_logs(hours=24)
        task_count = sum(1 for log in recent_logs if 'completed' in log.lower() or 'finished' in log.lower())
        metrics['total_tasks_24h'] = task_count
        
        # Count active sessions
        sessions_dir = self.logs_dir / 'sessions'
        if sessions_dir.exists():
            recent_sessions = [f for f in sessions_dir.glob('*.md') 
                             if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days < 1]
            metrics['active_sessions'] = len(recent_sessions)
        
        # Calculate efficiency score (simple heuristic)
        if metrics['total_tasks_24h'] > 0:
            metrics['efficiency_score'] = min(100, metrics['total_tasks_24h'] * 10)
        
        return metrics
    
    def _analyze_logs(self):
        """Analyze log patterns"""
        analysis = {
            'total_logs': 0,
            'errors': 0,
            'warnings': 0,
            'recent_errors': []
        }
        
        if self.logs_dir.exists():
            # Count all log files
            analysis['total_logs'] = sum(1 for _ in self.logs_dir.rglob('*.md'))
            
            # Analyze recent logs for errors/warnings
            recent_logs = self._get_recent_logs(hours=6)
            for log_content in recent_logs:
                if 'error' in log_content.lower():
                    analysis['errors'] += 1
                    # Extract error message (simple pattern)
                    error_match = re.search(r'error:?\s*(.{0,100})', log_content, re.IGNORECASE)
                    if error_match and len(analysis['recent_errors']) < 3:
                        analysis['recent_errors'].append(error_match.group(1).strip())
                
                if 'warning' in log_content.lower():
                    analysis['warnings'] += 1
        
        return analysis
    
    def _get_steering_status(self):
        """Get steering context status"""
        steering_dir = self.claude_dir / 'steering'
        status = {
            'initialized': False,
            'documents': {
                'product': False,
                'tech': False,
                'structure': False
            },
            'last_updated': 'Never'
        }
        
        if steering_dir.exists():
            for doc_name in ['product', 'tech', 'structure']:
                doc_path = steering_dir / f'{doc_name}.md'
                if doc_path.exists():
                    status['documents'][doc_name] = True
                    # Check if it's not just a template
                    content = doc_path.read_text(encoding='utf-8')
                    if '[Your' not in content and 'TODO' not in content:
                        status['initialized'] = True
            
            # Get last update time
            if status['initialized']:
                latest_mtime = max((steering_dir / f'{doc}.md').stat().st_mtime 
                                 for doc in ['product', 'tech', 'structure'] 
                                 if (steering_dir / f'{doc}.md').exists())
                status['last_updated'] = datetime.fromtimestamp(latest_mtime).strftime('%Y-%m-%d %H:%M')
        
        return status
    
    def _get_recent_logs(self, hours=24):
        """Get content from recent log files"""
        logs = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if self.logs_dir.exists():
            for log_file in self.logs_dir.rglob('*.md'):
                if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff_time:
                    try:
                        logs.append(log_file.read_text(encoding='utf-8')[:1000])  # First 1000 chars
                    except Exception:
                        pass
        
        return logs
    
    def _get_real_time_performance(self):
        """Get real-time performance metrics from monitor"""
        if not self.performance_monitor:
            return None
        
        try:
            summary = self.performance_monitor.get_performance_summary()
            return {
                'agents': summary.get('agents', {}),
                'resources': summary.get('resources', {}),
                'session_duration': summary.get('session_duration', 'N/A')
            }
        except Exception:
            return None
    
    def generate_html(self, metrics):
        """Generate enhanced HTML dashboard"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Enhanced Dashboard</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="10">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f0f2f5; 
            color: #1a1a1a;
            line-height: 1.6;
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px;
        }}
        h1 {{ 
            color: #2c3e50; 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px;
        }}
        .card {{ 
            background: white; 
            border-radius: 12px; 
            padding: 24px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        .card h2 {{ 
            color: #34495e; 
            margin-bottom: 16px; 
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .metric {{ 
            display: flex;
            align-items: baseline;
            gap: 8px;
            margin: 12px 0;
        }}
        .metric-label {{ 
            color: #7f8c8d; 
            font-size: 0.9em;
            min-width: 120px;
        }}
        .metric-value {{ 
            font-size: 1.8em; 
            font-weight: 600; 
            color: #3498db;
        }}
        .metric-small {{ font-size: 1.2em; }}
        .progress-bar {{ 
            width: 100%; 
            height: 8px; 
            background: #ecf0f1; 
            border-radius: 4px; 
            overflow: hidden; 
            margin: 8px 0;
        }}
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .status-active {{ background: #d4edda; color: #155724; }}
        .status-pending {{ background: #fff3cd; color: #856404; }}
        .status-completed {{ background: #cce5ff; color: #004085; }}
        .status-planning {{ background: #f8d7da; color: #721c24; }}
        .agent-activity {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 12px;
        }}
        .agent-badge {{
            background: #e3f2fd;
            color: #1565c0;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .agent-count {{
            background: #1565c0;
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.8em;
        }}
        .timeline {{
            margin-top: 12px;
        }}
        .timeline-item {{
            border-left: 2px solid #3498db;
            padding-left: 20px;
            margin-left: 10px;
            position: relative;
            padding-bottom: 12px;
        }}
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -6px;
            top: 0;
            width: 10px;
            height: 10px;
            background: #3498db;
            border-radius: 50%;
        }}
        .timeline-date {{
            color: #7f8c8d;
            font-size: 0.85em;
        }}
        .error-list {{
            margin-top: 12px;
            padding: 12px;
            background: #fff5f5;
            border-radius: 6px;
            border: 1px solid #ffebee;
        }}
        .error-item {{
            color: #c62828;
            font-size: 0.9em;
            margin: 4px 0;
        }}
        .icon {{
            width: 20px;
            height: 20px;
            display: inline-block;
        }}
        .full-width {{ grid-column: 1 / -1; }}
        .timestamp {{ 
            text-align: center; 
            color: #7f8c8d; 
            margin-top: 20px;
            font-size: 0.9em;
        }}
        .steering-indicator {{
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }}
        .doc-status {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }}
        .doc-ready {{ background: #d4edda; color: #155724; }}
        .doc-missing {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Claude Code Enhanced Dashboard</h1>
        
        <div class="grid">
            <!-- Project Overview -->
            <div class="card">
                <h2>📊 Project Overview</h2>
                <p><strong>{metrics['project'].get('name', 'Untitled Project')}</strong></p>
                <p>Phase: <span class="status-badge status-active">{metrics['project'].get('phase', 'Unknown')}</span></p>
                <p style="margin-top: 8px; color: #7f8c8d;">{metrics['project'].get('description', 'No description available')}</p>
            </div>
            
            <!-- Performance Metrics -->
            <div class="card">
                <h2>⚡ Performance Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Tasks (24h):</span>
                    <span class="metric-value">{metrics['performance']['total_tasks_24h']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Sessions:</span>
                    <span class="metric-value metric-small">{metrics['performance']['active_sessions']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Efficiency:</span>
                    <span class="metric-value metric-small">{metrics['performance']['efficiency_score']}%</span>
                </div>
            </div>
            
            <!-- System Resources -->
            <div class="card">
                <h2>🔧 System Resources</h2>
                <div class="metric">
                    <span class="metric-label">Agents:</span>
                    <span class="metric-value">{metrics['resources']['agents']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Commands:</span>
                    <span class="metric-value metric-small">{metrics['resources']['commands']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Scripts:</span>
                    <span class="metric-value metric-small">{metrics['resources']['scripts']}</span>
                </div>
            </div>
            
            <!-- Steering Context -->
            <div class="card">
                <h2>🎯 Steering Context</h2>
                <p>Status: <span class="status-badge {'status-completed' if metrics['steering']['initialized'] else 'status-pending'}">
                    {'Initialized' if metrics['steering']['initialized'] else 'Not Initialized'}
                </span></p>
                <div class="steering-indicator">
                    <span class="doc-status {'doc-ready' if metrics['steering']['documents']['product'] else 'doc-missing'}">Product</span>
                    <span class="doc-status {'doc-ready' if metrics['steering']['documents']['tech'] else 'doc-missing'}">Tech</span>
                    <span class="doc-status {'doc-ready' if metrics['steering']['documents']['structure'] else 'doc-missing'}">Structure</span>
                </div>
                <p style="margin-top: 8px; font-size: 0.85em; color: #7f8c8d;">
                    Last updated: {metrics['steering']['last_updated']}
                </p>
            </div>
            
            <!-- Active Specifications -->
            <div class="card full-width">
                <h2>📋 Active Specifications ({len(metrics['specifications'])})</h2>
                {self._generate_specs_html(metrics['specifications'])}
            </div>
            
            <!-- Agent Activity -->
            <div class="card">
                <h2>🤖 Agent Activity (24h)</h2>
                <div class="agent-activity">
                    {self._generate_agent_activity_html(metrics['agent_activity'])}
                </div>
            </div>
            
            <!-- Task Timeline -->
            <div class="card">
                <h2>📅 Recent Task Timeline</h2>
                <div class="timeline">
                    {self._generate_timeline_html(metrics['task_timeline'])}
                </div>
            </div>
            
            <!-- Log Analysis -->
            <div class="card">
                <h2>📝 Log Analysis</h2>
                <div class="metric">
                    <span class="metric-label">Total Logs:</span>
                    <span class="metric-value metric-small">{metrics['logs']['total_logs']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Errors:</span>
                    <span class="metric-value metric-small" style="color: #e74c3c;">{metrics['logs']['errors']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Warnings:</span>
                    <span class="metric-value metric-small" style="color: #f39c12;">{metrics['logs']['warnings']}</span>
                </div>
                {self._generate_errors_html(metrics['logs']['recent_errors'])}
            </div>
            
            {self._generate_performance_section(metrics.get('real_time_performance'))}
        </div>
        
        <div class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refreshes every 10 seconds
        </div>
    </div>
</body>
</html>"""
        return html
    
    def _generate_specs_html(self, specs):
        """Generate HTML for specifications"""
        if not specs:
            return '<p style="color: #7f8c8d;">No active specifications</p>'
        
        html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px;">'
        for spec in specs:
            status_class = f'status-{spec["status"]}'
            html += f'''
            <div style="padding: 16px; background: #f8f9fa; border-radius: 8px;">
                <h3 style="margin-bottom: 8px;">{spec['name']}</h3>
                <span class="status-badge {status_class}">{spec['status'].title()}</span>
                <div class="progress-bar" style="margin: 12px 0;">
                    <div class="progress-fill" style="width: {spec['tasks']['progress']}%"></div>
                </div>
                <p style="font-size: 0.85em; color: #7f8c8d;">
                    {spec['tasks']['completed']} / {spec['tasks']['total']} tasks 
                    ({spec['tasks']['progress']}%)
                </p>
                <p style="font-size: 0.8em; color: #95a5a6; margin-top: 4px;">
                    Created: {spec['created']} | Files: {spec['files']}
                </p>
            </div>
            '''
        html += '</div>'
        return html
    
    def _generate_performance_section(self, perf_data):
        """Generate performance monitoring section"""
        if not perf_data:
            return ''
        
        html = '''
        <!-- Real-time Performance -->
        <div class="card full-width">
            <h2>🚀 Real-time Performance Monitoring</h2>
            <p style="margin-bottom: 12px;">Session Duration: <strong>{}</strong></p>
        '''.format(perf_data.get('session_duration', 'N/A'))
        
        # Agent performance table
        if perf_data.get('agents'):
            html += '''
            <h3 style="margin-top: 16px; margin-bottom: 8px;">Agent Performance</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f8f9fa;">
                    <th style="padding: 8px; text-align: left;">Agent</th>
                    <th style="padding: 8px; text-align: center;">Executions</th>
                    <th style="padding: 8px; text-align: center;">Avg Duration</th>
                    <th style="padding: 8px; text-align: center;">Success Rate</th>
                </tr>
            '''
            
            for agent, stats in sorted(perf_data['agents'].items()):
                html += f'''
                <tr>
                    <td style="padding: 8px; border-top: 1px solid #dee2e6;">{agent}</td>
                    <td style="padding: 8px; text-align: center; border-top: 1px solid #dee2e6;">{stats.get('executions', 0)}</td>
                    <td style="padding: 8px; text-align: center; border-top: 1px solid #dee2e6;">{stats.get('avg_duration', 0)}s</td>
                    <td style="padding: 8px; text-align: center; border-top: 1px solid #dee2e6;">{stats.get('success_rate', 100)}%</td>
                </tr>
                '''
            
            html += '</table>'
        
        # Resource usage
        if perf_data.get('resources'):
            resources = perf_data['resources']
            html += f'''
            <h3 style="margin-top: 16px; margin-bottom: 8px;">Resource Usage</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                <div style="padding: 12px; background: #f8f9fa; border-radius: 6px;">
                    <div style="color: #7f8c8d; font-size: 0.85em;">CPU Usage</div>
                    <div style="font-size: 1.4em; font-weight: bold; color: #3498db;">
                        {resources.get('avg_cpu', 0)}% avg / {resources.get('max_cpu', 0)}% max
                    </div>
                </div>
                <div style="padding: 12px; background: #f8f9fa; border-radius: 6px;">
                    <div style="color: #7f8c8d; font-size: 0.85em;">Memory Usage</div>
                    <div style="font-size: 1.4em; font-weight: bold; color: #2ecc71;">
                        {resources.get('avg_memory', 0)}% avg / {resources.get('current_memory_mb', 0)} MB
                    </div>
                </div>
            </div>
            '''
        
        html += '</div>'
        return html
    
    def _generate_agent_activity_html(self, activity):
        """Generate HTML for agent activity"""
        if not activity:
            return '<p style="color: #7f8c8d;">No recent agent activity</p>'
        
        html = ''
        for agent, count in sorted(activity.items(), key=lambda x: x[1], reverse=True):
            html += f'''
            <div class="agent-badge">
                {agent.replace('-', ' ').title()}
                <span class="agent-count">{count}</span>
            </div>
            '''
        return html
    
    def _generate_timeline_html(self, timeline):
        """Generate HTML for task timeline"""
        if not timeline:
            return '<p style="color: #7f8c8d;">No recent tasks</p>'
        
        html = ''
        for item in timeline:
            tasks_html = '<br>'.join(f'• {task[:50]}...' if len(task) > 50 else f'• {task}' 
                                   for task in item['tasks'])
            html += f'''
            <div class="timeline-item">
                <div class="timeline-date">{item['date']}</div>
                <div style="font-size: 0.9em; margin-top: 4px;">{tasks_html}</div>
            </div>
            '''
        return html
    
    def _generate_errors_html(self, errors):
        """Generate HTML for recent errors"""
        if not errors:
            return ''
        
        html = '<div class="error-list"><strong>Recent Errors:</strong>'
        for error in errors:
            html += f'<div class="error-item">• {error[:80]}...</div>'
        html += '</div>'
        return html
    
    def run(self):
        """Run the enhanced dashboard"""
        print("Starting Claude Code Enhanced Dashboard...")
        
        # Create initial dashboard
        metrics = self.collect_metrics()
        html = self.generate_html(metrics)
        
        dashboard_path = self.project_root / 'enhanced_dashboard.html'
        dashboard_path.write_text(html, encoding='utf-8')
        
        # Open in browser
        file_url = f"file:///{dashboard_path.as_posix()}"
        print(f"Opening dashboard at: {file_url}")
        webbrowser.open(file_url)
        
        # Auto-update loop
        print("\nEnhanced Dashboard is running!")
        print("The dashboard updates every 10 seconds.")
        print("Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(10)
                metrics = self.collect_metrics()
                html = self.generate_html(metrics)
                dashboard_path.write_text(html, encoding='utf-8')
        except KeyboardInterrupt:
            print("\nDashboard stopped.")

def main():
    dashboard = EnhancedDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()