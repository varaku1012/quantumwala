#!/usr/bin/env python3
"""
Log management system for Claude Code multi-agent workflow
Standardizes where and how logs are created
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse
import json

class LogManager:
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
        
        self.logs_dir = self.project_root / '.claude' / 'logs'
        self.setup_directories()
    
    def setup_directories(self):
        """Ensure log directory structure exists"""
        directories = [
            'sessions',    # Daily work sessions
            'reports',     # Test reports, analysis reports
            'analysis',    # Code analysis, comparisons
            'phases',      # Phase completion logs
            'archive',     # Old logs
            'temp'         # Temporary working logs
        ]
        
        for dir_name in directories:
            (self.logs_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def get_log_path(self, category, name, timestamp=True):
        """Get standardized log path"""
        if timestamp:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{ts}_{name}.md"
        else:
            filename = f"{name}.md"
        
        return self.logs_dir / category / filename
    
    def create_session_log(self, title, content):
        """Create a session log"""
        date = datetime.now().strftime('%Y-%m-%d')
        path = self.get_log_path('sessions', f'session_{date}', timestamp=False)
        
        # Append to daily session log
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"\n## {datetime.now().strftime('%H:%M:%S')} - {title}\n\n")
            f.write(content)
            f.write("\n\n---\n")
        
        return path
    
    def create_report(self, report_type, title, content):
        """Create a report (test, analysis, etc.)"""
        safe_title = title.lower().replace(' ', '_')
        path = self.get_log_path('reports', f'{report_type}_{safe_title}')
        
        path.write_text(content, encoding='utf-8')
        return path
    
    def create_phase_log(self, phase, content):
        """Create a phase completion log"""
        path = self.get_log_path('phases', f'phase_{phase}_complete', timestamp=False)
        path.write_text(content, encoding='utf-8')
        return path
    
    def archive_old_logs(self, days=30):
        """Move logs older than specified days to archive"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        archived = 0
        
        for category in ['sessions', 'reports', 'analysis']:
            category_dir = self.logs_dir / category
            if not category_dir.exists():
                continue
                
            for file in category_dir.glob('*.md'):
                if file.stat().st_mtime < cutoff:
                    archive_path = self.logs_dir / 'archive' / category / file.name
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file), str(archive_path))
                    archived += 1
        
        return archived
    
    def clean_root_directory(self):
        """Move markdown files from root to appropriate log directories"""
        moved_files = []
        
        # Define patterns and their destinations
        patterns = {
            'CLAUDE_DESKTOP_CONVERSATION_SUMMARY_*.md': 'sessions',
            'CONVERSATION_SUMMARY_*.md': 'sessions',
            'SESSION_*.md': 'sessions',
            'PHASE_*_COMPLETE.md': 'phases',
            'PHASE_*_PLAN.md': 'phases',
            'TEST_REPORT*.md': 'reports',
            'ANALYSIS_*.md': 'analysis',
            'IMPLEMENTATION_*.md': 'phases',
            'DECISION_*.md': 'analysis',
            'CONTEXT_ENGINEERING_*.md': 'analysis',
            'URGENT_*.md': 'analysis',
            'MIGRATION_*.md': 'analysis',
            'SETUP_*.md': 'analysis',
            '*_QUICKSTART.md': 'analysis',
            'WHY_*.md': 'analysis'
        }
        
        for pattern, category in patterns.items():
            for file in self.project_root.glob(pattern):
                if file.is_file():
                    dest = self.logs_dir / category / file.name
                    shutil.move(str(file), str(dest))
                    moved_files.append((file.name, category))
                    print(f"Moved {file.name} to logs/{category}/")
        
        return moved_files
    
    def create_log_index(self):
        """Create an index of all logs"""
        index = {
            'generated': datetime.now().isoformat(),
            'categories': {}
        }
        
        for category in ['sessions', 'reports', 'analysis', 'phases']:
            category_dir = self.logs_dir / category
            if category_dir.exists():
                files = []
                for file in sorted(category_dir.glob('*.md')):
                    files.append({
                        'name': file.name,
                        'size': file.stat().st_size,
                        'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
                index['categories'][category] = files
        
        index_path = self.logs_dir / 'index.json'
        index_path.write_text(json.dumps(index, indent=2), encoding='utf-8')
        
        # Also create markdown index
        md_content = "# Log Index\n\n"
        md_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for category, files in index['categories'].items():
            md_content += f"## {category.title()}\n\n"
            for file in files:
                md_content += f"- [{file['name']}]({category}/{file['name']})\n"
            md_content += "\n"
        
        (self.logs_dir / 'README.md').write_text(md_content, encoding='utf-8')
        
        return index_path

def main():
    parser = argparse.ArgumentParser(description='Log management for Claude Code')
    parser.add_argument('action', choices=['create', 'clean', 'archive', 'index'],
                       help='Action to perform')
    parser.add_argument('--type', choices=['session', 'report', 'phase', 'analysis'],
                       help='Type of log to create')
    parser.add_argument('--title', help='Title for the log')
    parser.add_argument('--content', help='Content for the log (or stdin)')
    parser.add_argument('--days', type=int, default=30,
                       help='Days to keep before archiving (default: 30)')
    
    args = parser.parse_args()
    manager = LogManager()
    
    if args.action == 'create':
        if not args.type or not args.title:
            print("Error: --type and --title required for create action")
            return
        
        # Read content from stdin if not provided
        content = args.content
        if not content:
            import sys
            content = sys.stdin.read()
        
        if args.type == 'session':
            path = manager.create_session_log(args.title, content)
        elif args.type == 'report':
            path = manager.create_report('test', args.title, content)
        elif args.type == 'phase':
            path = manager.create_phase_log(args.title, content)
        elif args.type == 'analysis':
            path = manager.create_report('analysis', args.title, content)
        
        print(f"Log created: {path}")
    
    elif args.action == 'clean':
        moved = manager.clean_root_directory()
        print(f"Moved {len(moved)} files to organized log directories")
    
    elif args.action == 'archive':
        archived = manager.archive_old_logs(args.days)
        print(f"Archived {archived} old log files")
    
    elif args.action == 'index':
        index_path = manager.create_log_index()
        print(f"Created log index: {index_path}")

if __name__ == "__main__":
    main()