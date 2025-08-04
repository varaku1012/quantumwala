@echo off
echo Starting Claude Code Dashboard...
cd /d "%~dp0"
python .claude\scripts\simple_dashboard.py
pause