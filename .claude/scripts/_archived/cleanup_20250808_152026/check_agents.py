#!/usr/bin/env python3
"""
Check if agents are enabled
Usage: python check_agents.py
"""

import json
from pathlib import Path

def check_agents_enabled():
    """Check if agents are enabled in spec-config.json"""
    # Find project root by looking for .claude directory
    current = Path.cwd()
    while current != current.parent:
        if (current / '.claude').exists():
            break
        current = current.parent
    
    config_path = current / '.claude' / 'spec-config.json'
    
    if not config_path.exists():
        print("false")
        return
    
    try:
        config = json.loads(config_path.read_text())
        enabled = config.get('spec_workflow', {}).get('agents_enabled', False)
        print("true" if enabled else "false")
    except:
        print("false")

if __name__ == "__main__":
    check_agents_enabled()