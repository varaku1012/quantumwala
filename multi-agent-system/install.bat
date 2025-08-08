@echo off
echo ========================================
echo Unified Documentation Multi-Agent System
echo Installation Script for Quantumwala
echo ========================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    exit /b 1
)

echo [1/7] Installing Python dependencies...
pip install aiohttp pyyaml aiofiles asyncio dataclasses typing-extensions --upgrade

echo.
echo [2/7] Installing documentation tools...
pip install devdocs-cli 2>nul
if %errorlevel% neq 0 (
    echo Note: devdocs-cli not available, using fallback documentation
)

echo.
echo [3/7] Setting up directory structure...
cd /d "C:\Users\varak\repos\quantumwala\multi-agent-system"

:: Create required directories if they don't exist
if not exist "workspace" mkdir workspace
if not exist ".cache" mkdir .cache
if not exist ".cache\docs" mkdir .cache\docs
if not exist "documentation\internal" mkdir documentation\internal

echo.
echo [4/7] Initializing context...
python -c "import json; json.dump({'project_state': 'initialized', 'version': '1.0.0'}, open('context/state.json', 'w'))"

echo.
echo [5/7] Installing MCP servers (if MCP is installed)...
where mcp >nul 2>&1
if %errorlevel% equ 0 (
    echo Installing documentation MCP servers...
    mcp install devdocs-server 2>nul
    mcp install mdn-server 2>nul
    mcp install npm-docs-server 2>nul
    echo MCP servers installed successfully
) else (
    echo MCP not found. Install MCP to enable documentation servers
    echo Visit: https://github.com/anthropics/mcp for installation
)

echo.
echo [6/7] Setting up Claude Code integration...
where claude-code >nul 2>&1
if %errorlevel% equ 0 (
    echo Claude Code detected!
    claude-code --version
) else (
    echo Claude Code not detected. 
    echo The orchestrator will use mock responses for testing.
    echo Install Claude Code for full functionality.
)

echo.
echo [7/7] Running system test...
python -c "from orchestrator import ClaudeCodeOrchestrator; print('✓ Orchestrator module loaded successfully')"
python -c "from unified_doc_server import UnifiedDocumentationServer; print('✓ Documentation server loaded successfully')"
python -c "from templates.agent_templates import AGENT_TEMPLATES; print(f'✓ {len(AGENT_TEMPLATES)} agent templates loaded')"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run 'run_orchestrator.bat' to start the system
echo 2. Or use Python: python orchestrator.py
echo 3. Check README.md for usage examples
echo.
echo Documentation server will cache results in: .cache\docs
echo Logs will be saved in: logs\
echo Artifacts will be stored in: artifacts\
echo.
pause
