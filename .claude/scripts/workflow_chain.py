#!/usr/bin/env python3
"""
Workflow chaining for automatic progression between phases
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class WorkflowChain:
    def __init__(self):
        self.chains = {
            'grooming-start': 'grooming-workflow',
            'grooming-workflow': 'grooming-complete',
            'grooming-complete': 'spec-create',
            'steering-setup': 'grooming-start',
            'spec-create': 'spec-requirements',
            'spec-requirements': 'spec-design',
            'spec-design': 'spec-tasks',
            'spec-tasks': 'task-execution'
        }
        
        self.phase_descriptions = {
            'grooming-start': 'Starting feature grooming',
            'grooming-workflow': 'Running grooming analysis',
            'grooming-complete': 'Finalizing grooming',
            'steering-setup': 'Initializing project context',
            'spec-create': 'Creating feature specification',
            'spec-requirements': 'Generating detailed requirements',
            'spec-design': 'Creating technical design',
            'spec-tasks': 'Breaking down into tasks',
            'task-execution': 'Implementing features'
        }
    
    def get_next_command(self, current_phase, spec_name=None):
        """Get the next command in the workflow chain"""
        next_phase = self.chains.get(current_phase)
        
        if not next_phase:
            return None
        
        # Special handling for task execution
        if next_phase == 'task-execution' and spec_name:
            return f'python .claude/scripts/task_orchestrator.py {spec_name}'
        
        # Format command
        if next_phase == 'spec-create' and spec_name:
            return f'/{next_phase} {spec_name}'
        else:
            return f'/{next_phase}'
    
    def log_phase_transition(self, from_phase, to_phase, spec_name=None):
        """Log phase transitions"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""
## Phase Transition Log

**Time**: {timestamp}
**From**: {self.phase_descriptions.get(from_phase, from_phase)}
**To**: {self.phase_descriptions.get(to_phase, to_phase)}
**Spec**: {spec_name or 'N/A'}

### Next Steps
Automatically proceeding to: {to_phase}
"""
        
        # Log to workflow progress file
        log_file = Path('.claude/logs/sessions/workflow_progress.md')
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(message)
            f.write('\n---\n\n')
        
        return message
    
    def generate_auto_chain_prompt(self, current_phase, spec_name=None):
        """Generate prompt for automatic continuation"""
        next_command = self.get_next_command(current_phase, spec_name)
        
        if not next_command:
            return None
        
        return f"""
## Automatic Workflow Continuation

The {self.phase_descriptions.get(current_phase, current_phase)} phase is complete.

**Next Command**: `{next_command}`

Proceeding automatically to maintain workflow continuity...
"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Workflow chain helper')
    parser.add_argument('current_phase', help='Current workflow phase')
    parser.add_argument('--spec-name', help='Specification name')
    parser.add_argument('--get-next', action='store_true', help='Get next command')
    parser.add_argument('--log-transition', action='store_true', help='Log transition')
    
    args = parser.parse_args()
    
    chain = WorkflowChain()
    
    if args.get_next:
        next_cmd = chain.get_next_command(args.current_phase, args.spec_name)
        if next_cmd:
            print(next_cmd)
    
    if args.log_transition:
        next_phase = chain.chains.get(args.current_phase)
        if next_phase:
            log = chain.log_phase_transition(args.current_phase, next_phase, args.spec_name)
            print(log)


if __name__ == '__main__':
    main()