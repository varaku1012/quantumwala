#!/usr/bin/env python3
"""
Real-time dashboard for Claude Code multi-agent system
Usage: python dashboard.py [--port 3000]
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
from typing import Dict, List, Any

class DashboardData:
    """Collects and manages dashboard data"""
    
    def __init__(self, project_root=None):
        # Find project root
        if project_root:
            self.project_root = Path(project_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.claude').exists():
                    self.project_root = current
                    break
                current = current.parent
            else:
                self.project_root = Path.cwd()
        
        self.claude_dir = self.project_root / '.claude'
        self.data = {
            'project_info': {},
            'steering_status': {},
            'active_specs': [],
            'agent_activity': [],
            'metrics': {},
            'phase_status': {}
        }
    
    def collect_all(self):
        """Collect all dashboard data"""
        self.collect_project_info()
        self.collect_steering_status()
        self.collect_active_specs()
        self.collect_metrics()
        self.collect_phase_status()
        return self.data
    
    def collect_project_info(self):
        """Collect project information"""
        project_state_path = self.claude_dir / 'project-state.json'
        if project_state_path.exists():
            with open(project_state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.data['project_info'] = state.get('project', {})
    
    def collect_steering_status(self):
        """Collect steering document status"""
        steering_dir = self.claude_dir / 'steering'
        if steering_dir.exists():
            docs = ['product.md', 'tech.md', 'structure.md']
            for doc in docs:
                doc_path = steering_dir / doc
                if doc_path.exists():
                    stat = doc_path.stat()
                    self.data['steering_status'][doc] = {
                        'exists': True,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                else:
                    self.data['steering_status'][doc] = {'exists': False}
    
    def collect_active_specs(self):
        """Collect active specification status"""
        specs_dir = self.claude_dir / 'specs'
        if specs_dir.exists():
            for spec_dir in specs_dir.iterdir():
                if spec_dir.is_dir():
                    spec_info = {
                        'name': spec_dir.name,
                        'tasks': self.analyze_spec_tasks(spec_dir)
                    }
                    self.data['active_specs'].append(spec_info)
    
    def analyze_spec_tasks(self, spec_dir: Path) -> Dict:
        """Analyze tasks for a specification"""
        tasks_file = spec_dir / 'tasks.md'
        if not tasks_file.exists():
            return {'total': 0, 'completed': 0, 'pending': 0}
        
        content = tasks_file.read_text(encoding='utf-8')
        total = content.count('- [ ]') + content.count('- [x]')
        completed = content.count('- [x]')
        
        return {
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'progress': round((completed / total * 100) if total > 0 else 0, 1)
        }
    
    def collect_metrics(self):
        """Collect system metrics"""
        # Count agents
        agents_dir = self.claude_dir / 'agents'
        agent_count = len(list(agents_dir.glob('*.md'))) if agents_dir.exists() else 0
        
        # Count commands
        commands_dir = self.claude_dir / 'commands'
        command_count = len(list(commands_dir.glob('*.md'))) if commands_dir.exists() else 0
        
        # Count scripts
        scripts_dir = self.claude_dir / 'scripts'
        script_count = len(list(scripts_dir.glob('*.py'))) if scripts_dir.exists() else 0
        
        self.data['metrics'] = {
            'agents': agent_count,
            'commands': command_count,
            'scripts': script_count,
            'specs': len(self.data['active_specs'])
        }
    
    def collect_phase_status(self):
        """Collect phase implementation status"""
        project_state_path = self.claude_dir / 'project-state.json'
        if project_state_path.exists():
            with open(project_state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.data['phase_status'] = state.get('phases', {})

class DashboardServer(SimpleHTTPRequestHandler):
    """HTTP server for dashboard"""
    
    dashboard_data = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/data':
            self.serve_data()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_data(self):
        """Serve dashboard data as JSON"""
        if self.dashboard_data:
            data = self.dashboard_data.collect_all()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())
        else:
            self.send_error(500, "Dashboard data not available")
    
    def generate_dashboard_html(self):
        """Generate dashboard HTML"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Multi-Agent Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #555; font-size: 18px; }
        .metric { display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2196F3; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #4CAF50; transition: width 0.3s; }
        .status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .status.complete { background: #4CAF50; color: white; }
        .status.pending { background: #FF9800; color: white; }
        .status.planned { background: #9E9E9E; color: white; }
        .spec-item { margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 4px; }
        .refresh-info { text-align: center; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Claude Code Multi-Agent System Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h2>Project Status</h2>
                <div id="project-info"></div>
            </div>
            
            <div class="card">
                <h2>System Metrics</h2>
                <div id="metrics"></div>
            </div>
            
            <div class="card">
                <h2>Steering Documents</h2>
                <div id="steering-status"></div>
            </div>
        </div>
        
        <div class="card">
            <h2>Phase Implementation Status</h2>
            <div id="phase-status"></div>
        </div>
        
        <div class="card">
            <h2>Active Specifications</h2>
            <div id="active-specs"></div>
        </div>
        
        <div class="refresh-info">
            Dashboard refreshes every 5 seconds | <span id="last-update"></span>
        </div>
    </div>
    
    <script>
        async function updateDashboard() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                // Update project info
                const projectInfo = data.project_info;
                document.getElementById('project-info').innerHTML = `
                    <div class="metric">
                        <span>Name:</span>
                        <span>${projectInfo.name || 'Unknown'}</span>
                    </div>
                    <div class="metric">
                        <span>Phase:</span>
                        <span class="status ${projectInfo.phase?.includes('complete') ? 'complete' : 'pending'}">
                            ${projectInfo.phase || 'Unknown'}
                        </span>
                    </div>
                `;
                
                // Update metrics
                const metrics = data.metrics;
                document.getElementById('metrics').innerHTML = `
                    <div class="metric">
                        <span>Agents:</span>
                        <span class="metric-value">${metrics.agents || 0}</span>
                    </div>
                    <div class="metric">
                        <span>Commands:</span>
                        <span class="metric-value">${metrics.commands || 0}</span>
                    </div>
                    <div class="metric">
                        <span>Scripts:</span>
                        <span class="metric-value">${metrics.scripts || 0}</span>
                    </div>
                    <div class="metric">
                        <span>Active Specs:</span>
                        <span class="metric-value">${metrics.specs || 0}</span>
                    </div>
                `;
                
                // Update steering status
                const steeringHtml = Object.entries(data.steering_status).map(([doc, info]) => `
                    <div class="metric">
                        <span>${doc}:</span>
                        <span class="status ${info.exists ? 'complete' : 'pending'}">
                            ${info.exists ? 'Created' : 'Missing'}
                        </span>
                    </div>
                `).join('');
                document.getElementById('steering-status').innerHTML = steeringHtml;
                
                // Update phase status
                const phaseHtml = Object.entries(data.phase_status).map(([phase, info]) => `
                    <div class="spec-item">
                        <strong>${phase.toUpperCase()}</strong>
                        <span class="status ${info.status}">${info.status}</span>
                        <div style="margin-top: 5px; font-size: 14px; color: #666;">
                            ${info.features?.join(', ') || 'No features listed'}
                        </div>
                    </div>
                `).join('');
                document.getElementById('phase-status').innerHTML = phaseHtml;
                
                // Update active specs
                const specsHtml = data.active_specs.map(spec => `
                    <div class="spec-item">
                        <strong>${spec.name}</strong>
                        <div class="progress-bar" style="margin-top: 10px;">
                            <div class="progress-fill" style="width: ${spec.tasks.progress}%"></div>
                        </div>
                        <div style="margin-top: 5px; font-size: 14px; color: #666;">
                            ${spec.tasks.completed} / ${spec.tasks.total} tasks complete (${spec.tasks.progress}%)
                        </div>
                    </div>
                `).join('') || '<p>No active specifications</p>';
                document.getElementById('active-specs').innerHTML = specsHtml;
                
                // Update timestamp
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
            } catch (error) {
                console.error('Failed to update dashboard:', error);
            }
        }
        
        // Initial update
        updateDashboard();
        
        // Refresh every 5 seconds
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>"""

def run_dashboard(port=3000):
    """Run the dashboard server"""
    # Create dashboard data collector
    dashboard_data = DashboardData()
    DashboardServer.dashboard_data = dashboard_data
    
    # Start server
    server = HTTPServer(('localhost', port), DashboardServer)
    print(f"Dashboard running at http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped")
        server.shutdown()

def main():
    parser = argparse.ArgumentParser(description='Run Claude Code dashboard')
    parser.add_argument('--port', type=int, default=3000, help='Port to run dashboard on')
    
    args = parser.parse_args()
    run_dashboard(args.port)

if __name__ == "__main__":
    main()