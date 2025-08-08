#!/bin/bash
# Generate individual task commands for a spec

SPEC_NAME=$1
TASKS_FILE=".claude/specs/$SPEC_NAME/tasks.md"

if [ ! -f "$TASKS_FILE" ]; then
    echo "Error: Tasks file not found for spec: $SPEC_NAME"
    exit 1
fi

# Create commands directory for spec
mkdir -p ".claude/commands/$SPEC_NAME"

# Parse tasks and create commands
TASK_ID=1
while IFS= read -r line; do
    if [[ $line =~ ^###[[:space:]]Task[[:space:]]([0-9.]+): ]]; then
        TASK_NUM="${BASH_REMATCH[1]}"
        TASK_DESC=$(echo "$line" | sed 's/^### Task [0-9.]*: //')
        
        # Create task command
        cat > ".claude/commands/$SPEC_NAME/task-$TASK_NUM.md" << TASK_EOF
Execute task $TASK_NUM for $SPEC_NAME: $TASK_DESC

This command will:
1. Load task details from specs
2. Use developer agent to implement
3. Follow TDD approach
4. Update task status

Usage: /$SPEC_NAME-task-$TASK_NUM
TASK_EOF
        
        echo "Created command: /$SPEC_NAME-task-$TASK_NUM"
    fi
done < "$TASKS_FILE"