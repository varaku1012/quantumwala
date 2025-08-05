@echo off
REM Hook to automatically progress workflow phases (Windows version)

REM Get current working directory
set PROJECT_ROOT=%CD%

REM Ensure we have the .claude directory
if not exist ".claude" (
    echo Warning: .claude directory not found. Skipping phase progression.
    exit /b 0
)

REM Get current phase from workflow state
for /f "delims=" %%i in ('python .claude\scripts\workflow_state.py --get-current 2^>nul') do set CURRENT_PHASE=%%i
for /f "delims=" %%i in ('python .claude\scripts\workflow_state.py --spec-name 2^>nul') do set SPEC_NAME=%%i

if "%CURRENT_PHASE%"=="" set CURRENT_PHASE=unknown
if "%SPEC_NAME%"=="" set SPEC_NAME=default

echo Phase completion detected: %CURRENT_PHASE% for spec: %SPEC_NAME%

REM Log the phase completion
python .claude\scripts\log_manager.py create --type session --title "phase-complete-%CURRENT_PHASE%" --content "✓ Completed phase: %CURRENT_PHASE% at %DATE% %TIME%" 2>nul

REM Get next command based on phase
set NEXT_CMD=
if "%CURRENT_PHASE%"=="steering_setup" (
    set NEXT_CMD=/spec-create "%SPEC_NAME%" "Feature implementation"
) else if "%CURRENT_PHASE%"=="spec_creation" (
    set NEXT_CMD=/spec-requirements
) else if "%CURRENT_PHASE%"=="requirements_generation" (
    set NEXT_CMD=/planning design "%SPEC_NAME%"
) else if "%CURRENT_PHASE%"=="design_creation" (
    set NEXT_CMD=/spec-tasks
) else if "%CURRENT_PHASE%"=="task_generation" (
    set NEXT_CMD=/planning implementation "%SPEC_NAME%"
) else if "%CURRENT_PHASE%"=="implementation" (
    set NEXT_CMD=/planning testing "%SPEC_NAME%"
) else if "%CURRENT_PHASE%"=="validation" (
    set NEXT_CMD=/spec-review
)

if not "%NEXT_CMD%"=="" (
    echo 🚀 Auto-progressing to next phase: %NEXT_CMD%
    
    REM Create a suggestion file for Claude Code to pick up
    echo %NEXT_CMD% > .claude\next_command.txt
    echo %DATE% %TIME%: Suggested next command: %NEXT_CMD% >> .claude\logs\sessions\auto_progression.log
) else (
    echo ✅ Workflow complete or no next phase defined
)

REM Update workflow progress
python .claude\scripts\workflow_state.py --complete-phase "%CURRENT_PHASE%" 2>nul

echo Phase progression hook completed