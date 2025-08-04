#!/bin/bash
# Pre-task hook - runs before task execution

TASK_ID=$1
SPEC_NAME=$2

# Create project state file if not exists
STATE_FILE=".claude/project-state.json"
if [ ! -f "$STATE_FILE" ]; then
    echo '{"tasks": {}, "specs": {}}' > "$STATE_FILE"
fi

# Check task dependencies
echo "Checking dependencies for task $TASK_ID..."

# Log task start
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting task: $SPEC_NAME/$TASK_ID" >> .claude/task.log

exit 0