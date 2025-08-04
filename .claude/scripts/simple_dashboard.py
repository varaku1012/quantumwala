#!/usr/bin/env python3
"""
Simple dashboard for Claude Code multi-agent system
Usage: python simple_dashboard.py
"""

import json
import os
from pathlib import Path
from datetime import datetime
import webbrowser
import threading
import time

def find_project_root():
    """Find project root by looking for .claude directory"""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.claude').exists():
            return current
        current = current.parent
    return Path.cwd()

def collect_dashboard_data():
    """Collect dashboard data and create HTML file"""
    project_root = find_project_root()
    claude_dir = project_root / '.claude'
    
    # Collect project info
    project_info = {}
    project_state_path = claude_dir / 'project-state.json'
    if project_state_path.exists():
        with open(project_state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
            project_info = state.get('project', {})
    
    # Count resources
    agents_count = len(list((claude_dir / 'agents').glob('*.md'))) if (claude_dir / 'agents').exists() else 0
    commands_count = len(list((claude_dir / 'commands').glob('*.md'))) if (claude_dir / 'commands').exists() else 0
    scripts_count = len(list((claude_dir / 'scripts').glob('*.py'))) if (claude_dir / 'scripts').exists() else 0
    
    # Count specs and tasks
    specs_info = []
    specs_dir = claude_dir / 'specs'
    if specs_dir.exists():
        for spec_dir in specs_dir.iterdir():
            if spec_dir.is_dir():
                tasks_file = spec_dir / 'tasks.md'
                if tasks_file.exists():
                    content = tasks_file.read_text(encoding='utf-8')
                    total = content.count('- [ ]') + content.count('- [x]')
                    completed = content.count('- [x]')
                    progress = round((completed / total * 100) if total > 0 else 0, 1)
                    specs_info.append({
                        'name': spec_dir.name,
                        'total': total,
                        'completed': completed,
                        'progress': progress
                    })
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Dashboard</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #333; text-align: center; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #2196F3; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
        .progress-fill {{ height: 100%; background: #4CAF50; }}
        .spec-item {{ margin: 15px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; }}
        .timestamp {{ text-align: center; color: #666; margin-top: 20px; }}
        .phase {{ display: inline-block; padding: 4px 12px; border-radius: 4px; background: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Claude Code Multi-Agent System Dashboard</h1>
        
        <div class="card">
            <h2>Project Overview</h2>
            <p><strong>Name:</strong> {project_info.get('name', 'Unknown')}</p>
            <p><strong>Phase:</strong> <span class="phase">{project_info.get('phase', 'Unknown')}</span></p>
            <p><strong>Description:</strong> {project_info.get('description', 'No description')}</p>
        </div>
        
        <div class="card">
            <h2>System Metrics</h2>
            <div class="metric">
                <div class="metric-label">Agents</div>
                <div class="metric-value">{agents_count}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Commands</div>
                <div class="metric-value">{commands_count}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Scripts</div>
                <div class="metric-value">{scripts_count}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Active Specs</div>
                <div class="metric-value">{len(specs_info)}</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Active Specifications</h2>
            {''.join([f'''
            <div class="spec-item">
                <strong>{spec['name']}</strong>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {spec['progress']}%"></div>
                </div>
                <p>{spec['completed']} / {spec['total']} tasks complete ({spec['progress']}%)</p>
            </div>
            ''' for spec in specs_info]) if specs_info else '<p>No active specifications</p>'}
        </div>
        
        <div class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refreshes every 5 seconds
        </div>
    </div>
</body>
</html>"""
    
    # Write HTML file
    dashboard_path = project_root / 'dashboard.html'
    dashboard_path.write_text(html, encoding='utf-8')
    
    return dashboard_path

def auto_update():
    """Update dashboard every 5 seconds"""
    while True:
        try:
            collect_dashboard_data()
            time.sleep(5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Update error: {e}")
            time.sleep(5)

def main():
    print("Starting Claude Code Dashboard...")
    
    # Create initial dashboard
    dashboard_path = collect_dashboard_data()
    
    # Open in browser
    file_url = f"file:///{dashboard_path.as_posix()}"
    print(f"Opening dashboard at: {file_url}")
    webbrowser.open(file_url)
    
    # Start auto-update in background
    update_thread = threading.Thread(target=auto_update, daemon=True)
    update_thread.start()
    
    print("\nDashboard is running!")
    print("The dashboard.html file is being updated every 5 seconds.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDashboard stopped.")

if __name__ == "__main__":
    main()