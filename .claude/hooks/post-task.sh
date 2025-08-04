#!/bin/bash
# Post-task hook - runs after task completion

TASK_ID=$1
SPEC_NAME=$2
STATUS=$3

# Update task status
STATE_FILE=".claude/project-state.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Update using jq if available, otherwise use simple approach
if command -v jq &> /dev/null; then
    jq ".tasks[\"$SPEC_NAME/$TASK_ID\"] = {\"status\": \"$STATUS\", \"completed\": \"$TIMESTAMP\"}" "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
fi

# Log completion
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Completed task: $SPEC_NAME/$TASK_ID (Status: $STATUS)" >> .claude/task.log

exit 0