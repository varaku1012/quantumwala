@echo off
REM Claude Code Workflow Launcher for Windows
REM Usage: workflow [spec-name] [options]

cd /d "%~dp0"
python .claude\scripts\start_workflow.py %*