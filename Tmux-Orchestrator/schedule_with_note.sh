#!/bin/bash
# Dynamic scheduler with note for next check
# Usage: ./schedule_with_note.sh <minutes> "<note>" [target_window]

MINUTES=${1:-3}
NOTE=${2:-"Standard check-in"}
TARGET=${3:-"tmux-orc:0"}

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a note file for the next check
echo "=== Next Check Note ($(date)) ===" > "$SCRIPT_DIR/next_check_note.txt"
echo "Scheduled for: $MINUTES minutes" >> "$SCRIPT_DIR/next_check_note.txt"
echo "" >> "$SCRIPT_DIR/next_check_note.txt"
echo "$NOTE" >> "$SCRIPT_DIR/next_check_note.txt"

echo "Scheduling check in $MINUTES minutes with note: $NOTE"

# Calculate the exact time when the check will run
CURRENT_TIME=$(date +"%H:%M:%S")
RUN_TIME=$(date -d "+${MINUTES} minutes" +"%H:%M:%S" 2>/dev/null || date +"%H:%M:%S")

# Use nohup to completely detach the sleep process
SECONDS=$((MINUTES * 60))
nohup bash -c "sleep $SECONDS && tmux send-keys -t $TARGET 'Time for orchestrator check! cat $SCRIPT_DIR/next_check_note.txt && python3 $SCRIPT_DIR/claude_control.py status detailed' && sleep 1 && tmux send-keys -t $TARGET Enter" > /dev/null 2>&1 &

# Get the PID of the background process
SCHEDULE_PID=$!

echo "Scheduled successfully - process detached (PID: $SCHEDULE_PID)"
echo "SCHEDULED TO RUN AT: $RUN_TIME (in $MINUTES minutes from $CURRENT_TIME)"