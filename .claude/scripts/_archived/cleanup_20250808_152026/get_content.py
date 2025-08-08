#!/usr/bin/env python3
"""
Efficiently load file contents for agents
Usage: python get_content.py <file-path>
"""

import sys
import os
from pathlib import Path

def get_content(file_path):
    """Load and output file content"""
    try:
        # Normalize path for cross-platform
        path = Path(file_path).resolve()
        
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        # Output content to stdout for agent consumption
        content = path.read_text(encoding='utf-8')
        # Handle Windows console encoding issues
        try:
            print(content)
        except UnicodeEncodeError:
            # Fallback to safe encoding for Windows console
            import sys
            sys.stdout.reconfigure(encoding='utf-8')
            print(content)
        
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide a file path", file=sys.stderr)
        print("Usage: get_content.py <file-path>", file=sys.stderr)
        sys.exit(1)
    
    get_content(sys.argv[1])