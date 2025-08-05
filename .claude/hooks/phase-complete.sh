#!/bin/bash
# Hook to automatically progress workflow phases

# Get current working directory
PROJECT_ROOT=$(pwd)

# Ensure we have the .claude directory
if [ ! -d ".claude" ]; then
    echo "Warning: .claude directory not found. Skipping phase progression."
    exit 0
fi

# Get current phase from workflow state
CURRENT_PHASE=$(python .claude/scripts/workflow_state.py --get-current 2>/dev/null || echo "unknown")
SPEC_NAME=$(python .claude/scripts/workflow_state.py --spec-name 2>/dev/null || echo "default")

echo "Phase completion detected: $CURRENT_PHASE for spec: $SPEC_NAME"

# Log the phase completion
python .claude/scripts/log_manager.py create --type session \
    --title "phase-complete-$CURRENT_PHASE" \
    --content "✓ Completed phase: $CURRENT_PHASE at $(date)" 2>/dev/null

# Get next command based on phase
case "$CURRENT_PHASE" in
    "steering_setup")
        NEXT_CMD="/spec-create \"$SPEC_NAME\" \"Feature implementation\""
        ;;
    "spec_creation")
        NEXT_CMD="/spec-requirements"
        ;;
    "requirements_generation")
        NEXT_CMD="/planning design \"$SPEC_NAME\""
        ;;
    "design_creation")
        NEXT_CMD="/spec-tasks"
        ;;
    "task_generation")
        NEXT_CMD="/planning implementation \"$SPEC_NAME\""
        ;;
    "implementation")
        NEXT_CMD="/planning testing \"$SPEC_NAME\""
        ;;
    "validation")
        NEXT_CMD="/spec-review"
        ;;
    *)
        NEXT_CMD=""
        ;;
esac

if [ ! -z "$NEXT_CMD" ]; then
    echo "🚀 Auto-progressing to next phase: $NEXT_CMD"
    
    # Create a suggestion file for Claude Code to pick up
    echo "$NEXT_CMD" > .claude/next_command.txt
    echo "$(date): Suggested next command: $NEXT_CMD" >> .claude/logs/sessions/auto_progression.log
else
    echo "✅ Workflow complete or no next phase defined"
fi

# Update workflow progress
python .claude/scripts/workflow_state.py --complete-phase "$CURRENT_PHASE" 2>/dev/null

echo "Phase progression hook completed"