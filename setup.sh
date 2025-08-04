#!/bin/bash

echo ""
echo "Claude Code Multi-Agent System Setup"
echo "===================================="
echo ""
echo "This will set up the complete multi-agent system in your project."
echo ""
echo "Press Enter to continue..."
read

python3 setup.py || python setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup completed successfully!"
    echo ""
    echo "Next: Edit .claude/steering/*.md files with your project details"
    echo "Then run: /steering-setup in Claude Code"
else
    echo ""
    echo "Setup failed! Please check the errors above."
fi