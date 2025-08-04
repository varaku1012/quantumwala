#!/bin/bash
# This hook runs after each agent completes to preserve context for next agents

AGENT_NAME=$1
OUTPUT_FILE=$2

# Create context file for next agent
CONTEXT_DIR=".claude/agent-context"
mkdir -p "$CONTEXT_DIR"

# Extract key information for next agents
if [ "$AGENT_NAME" = "product-manager" ]; then
    # Extract sections marked for other agents
    grep -A 10 "For Business Analyst Agent" "$OUTPUT_FILE" > "$CONTEXT_DIR/ba-context.md"
    grep -A 10 "For Architect Agent" "$OUTPUT_FILE" > "$CONTEXT_DIR/arch-context.md"
    grep -A 10 "For UI/UX Designer Agent" "$OUTPUT_FILE" > "$CONTEXT_DIR/ux-context.md"
fi

# Create summary for next agent
cat > "$CONTEXT_DIR/last-agent-summary.md" << EOF
# Previous Agent: $AGENT_NAME
# Timestamp: $(date)
# Key Outputs:

$(tail -n 20 "$OUTPUT_FILE" | grep -E "^(##|→|Next:)")
EOF

echo "Context preserved for next agent in $CONTEXT_DIR"