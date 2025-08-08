@echo off
echo ========================================
echo Quantumwala Multi-Agent Orchestrator
echo With Unified Documentation Support
echo ========================================
echo.

cd /d "C:\Users\varak\repos\quantumwala\multi-agent-system"

if "%1"=="" (
    echo Usage: run_orchestrator.bat [command] [options]
    echo.
    echo Commands:
    echo   test        - Run system test
    echo   develop     - Start development agent
    echo   architect   - Start architecture design
    echo   qa          - Run QA analysis
    echo   review      - Run code review
    echo   parallel    - Run parallel agents demo
    echo   interactive - Start interactive mode
    echo.
    goto :eof
)

if "%1"=="test" (
    echo Running system test...
    python orchestrator.py
    goto :eof
)

if "%1"=="develop" (
    echo Starting Developer Agent with Documentation...
    python -c "import asyncio; from orchestrator import ClaudeCodeOrchestrator; o = ClaudeCodeOrchestrator('.'); asyncio.run(o.run_agent('developer', '%2', {}, True))"
    goto :eof
)

if "%1"=="architect" (
    echo Starting Architect Agent...
    python -c "import asyncio; from orchestrator import ClaudeCodeOrchestrator; o = ClaudeCodeOrchestrator('.'); asyncio.run(o.run_agent('architect', '%2', {}, True))"
    goto :eof
)

if "%1"=="qa" (
    echo Starting QA Agent...
    python -c "import asyncio; from orchestrator import ClaudeCodeOrchestrator; o = ClaudeCodeOrchestrator('.'); asyncio.run(o.run_agent('qa', '%2', {}, True))"
    goto :eof
)

if "%1"=="review" (
    echo Starting Code Review Agent...
    python -c "import asyncio; from orchestrator import ClaudeCodeOrchestrator; o = ClaudeCodeOrchestrator('.'); asyncio.run(o.run_agent('code_reviewer', '%2', {}, True))"
    goto :eof
)

if "%1"=="parallel" (
    echo Running Parallel Agents Demo...
    python -c "import asyncio; from orchestrator import main; asyncio.run(main())"
    goto :eof
)

if "%1"=="interactive" (
    echo Starting Interactive Mode...
    python interactive_cli.py
    goto :eof
)

echo Unknown command: %1
echo Run 'run_orchestrator.bat' without arguments to see usage
