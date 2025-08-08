#!/bin/bash
# Claude Code Workflow Launcher for Linux/Mac
# Usage: ./workflow.sh [spec-name] [options]

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project directory
cd "$DIR"

# Run the workflow launcher
python3 .claude/scripts/start_workflow.py "$@"