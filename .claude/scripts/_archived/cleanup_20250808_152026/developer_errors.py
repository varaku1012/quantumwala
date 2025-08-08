#!/usr/bin/env python3
"""
Developer-friendly error handling
Replaces cryptic errors with helpful messages and suggestions
"""

import sys
import traceback
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

@dataclass
class DeveloperSuggestion:
    """A helpful suggestion for developers"""
    action: str
    command: str = None
    explanation: str = None

class DeveloperError(Exception):
    """Error designed to help developers, not confuse them"""
    
    def __init__(
        self, 
        message: str, 
        suggestions: List[DeveloperSuggestion] = None,
        debug_info: Dict = None,
        original_error: Exception = None
    ):
        self.message = message
        self.suggestions = suggestions or []
        self.debug_info = debug_info or {}
        self.original_error = original_error
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format error message for developers"""
        msg = f"\n❌ {self.message}\n"
        
        if self.suggestions:
            msg += "\n💡 Try these solutions:\n"
            for i, suggestion in enumerate(self.suggestions, 1):
                msg += f"   {i}. {suggestion.action}\n"
                if suggestion.command:
                    msg += f"      Command: {suggestion.command}\n"
                if suggestion.explanation:
                    msg += f"      Why: {suggestion.explanation}\n"
        
        if self.debug_info:
            msg += "\n🔍 Debug Information:\n"
            for key, value in self.debug_info.items():
                msg += f"   • {key}: {value}\n"
        
        if self.original_error and hasattr(self.original_error, '__traceback__'):
            msg += f"\n🐛 Original Error: {str(self.original_error)}\n"
        
        return msg

class DeveloperErrorHandler:
    """Handles and converts technical errors to developer-friendly ones"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def handle_import_error(self, error: ImportError, module_name: str) -> DeveloperError:
        """Convert ImportError to developer-friendly error"""
        if module_name == 'psutil':
            return DeveloperError(
                f"Missing required package: {module_name}",
                suggestions=[
                    DeveloperSuggestion(
                        "Install the missing package",
                        "pip install psutil",
                        "psutil is needed for system resource monitoring"
                    ),
                    DeveloperSuggestion(
                        "Validate your environment",
                        "python .claude/scripts/dev_environment_validator.py",
                        "This will check for all missing dependencies"
                    )
                ],
                debug_info={
                    "module": module_name,
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "platform": sys.platform
                },
                original_error=error
            )
        
        elif module_name in ['unified_state', 'resource_manager', 'real_executor']:
            return DeveloperError(
                f"Cannot import Quantumwala module: {module_name}",
                suggestions=[
                    DeveloperSuggestion(
                        "Check you're in the project root directory",
                        "cd path/to/quantumwala && python script.py",
                        "Scripts need to be run from the project root"
                    ),
                    DeveloperSuggestion(
                        "Verify project structure",
                        "ls -la .claude/scripts/",
                        "Ensure all required script files exist"
                    ),
                    DeveloperSuggestion(
                        "Run environment validation",
                        "python .claude/scripts/dev_environment_validator.py",
                        "This will check project structure and dependencies"
                    )
                ],
                debug_info={
                    "module": module_name,
                    "current_directory": str(Path.cwd()),
                    "project_root": str(self.project_root),
                    "claude_dir_exists": (self.project_root / '.claude').exists()
                },
                original_error=error
            )
        
        else:
            return DeveloperError(
                f"Missing Python package: {module_name}",
                suggestions=[
                    DeveloperSuggestion(
                        "Install the package",
                        f"pip install {module_name}",
                        f"The {module_name} package is required for this functionality"
                    ),
                    DeveloperSuggestion(
                        "Check if it's a built-in module",
                        f"python -c 'import {module_name}'",
                        "Some modules are built-in and may indicate Python version issues"
                    )
                ],
                original_error=error
            )
    
    def handle_file_error(self, error: Exception, file_path: str) -> DeveloperError:
        """Convert file operation errors to developer-friendly errors"""
        path_obj = Path(file_path)
        
        if isinstance(error, FileNotFoundError):
            if 'workflow_state.py' in file_path:
                return DeveloperError(
                    f"Quantumwala script not found: {path_obj.name}",
                    suggestions=[
                        DeveloperSuggestion(
                            "Verify you're in the project root",
                            "pwd && ls -la .claude/scripts/",
                            "Scripts must be run from the project root directory"
                        ),
                        DeveloperSuggestion(
                            "Check project structure",
                            "python .claude/scripts/dev_environment_validator.py",
                            "This will verify all required files exist"
                        ),
                        DeveloperSuggestion(
                            "Re-clone the repository if files are missing",
                            "git status && git pull",
                            "Some files might not have been cloned properly"
                        )
                    ],
                    debug_info={
                        "file_path": file_path,
                        "exists": path_obj.exists(),
                        "parent_exists": path_obj.parent.exists(),
                        "current_dir": str(Path.cwd())
                    },
                    original_error=error
                )
            else:
                return DeveloperError(
                    f"File not found: {path_obj.name}",
                    suggestions=[
                        DeveloperSuggestion(
                            "Check the file path",
                            f"ls -la {path_obj.parent}" if path_obj.parent.exists() else f"mkdir -p {path_obj.parent}",
                            "Verify the file exists at the expected location"
                        ),
                        DeveloperSuggestion(
                            "Check file permissions",
                            f"ls -la {file_path}",
                            "Ensure you have read access to the file"
                        )
                    ],
                    debug_info={"file_path": file_path, "current_dir": str(Path.cwd())},
                    original_error=error
                )
        
        elif isinstance(error, PermissionError):
            return DeveloperError(
                f"Permission denied: {path_obj.name}",
                suggestions=[
                    DeveloperSuggestion(
                        "Fix file permissions",
                        f"chmod u+rw {file_path}" if sys.platform != 'win32' else f"icacls {file_path} /grant %USERNAME%:F",
                        "You need read/write permissions for this file"
                    ),
                    DeveloperSuggestion(
                        "Check directory permissions",
                        f"chmod u+rwx {path_obj.parent}" if sys.platform != 'win32' else f"icacls {path_obj.parent} /grant %USERNAME%:F /T",
                        "Directory permissions might be blocking file access"
                    ),
                    DeveloperSuggestion(
                        "Run as administrator (Windows) or with sudo (Unix)",
                        "May be needed for system-level directories"
                    )
                ],
                debug_info={"file_path": file_path, "platform": sys.platform},
                original_error=error
            )
        
        return DeveloperError(
            f"File operation failed: {str(error)}",
            suggestions=[
                DeveloperSuggestion(
                    "Check file exists and is accessible",
                    f"ls -la {file_path}",
                    "Verify file permissions and existence"
                )
            ],
            original_error=error
        )
    
    def handle_subprocess_error(self, error: Exception, command: str) -> DeveloperError:
        """Convert subprocess errors to developer-friendly errors"""
        if 'workflow_state.py' in command:
            return DeveloperError(
                "Workflow state script failed",
                suggestions=[
                    DeveloperSuggestion(
                        "Test the script directly",
                        "python .claude/scripts/workflow_state.py --help",
                        "Check if the script runs independently"
                    ),
                    DeveloperSuggestion(
                        "Check Python path and permissions",
                        "which python && python --version",
                        "Ensure Python is properly installed and accessible"
                    ),
                    DeveloperSuggestion(
                        "Run environment validation",
                        "python .claude/scripts/dev_environment_validator.py",
                        "This will check for common setup issues"
                    )
                ],
                debug_info={
                    "command": command,
                    "python_executable": sys.executable,
                    "current_dir": str(Path.cwd())
                },
                original_error=error
            )
        
        elif 'claude-code' in command:
            return DeveloperError(
                "Claude Code command failed",
                suggestions=[
                    DeveloperSuggestion(
                        "Check Claude Code installation",
                        "claude-code --version",
                        "Verify Claude Code CLI is installed and in PATH"
                    ),
                    DeveloperSuggestion(
                        "Install Claude Code CLI",
                        "See https://docs.anthropic.com/claude-code",
                        "The CLI is needed for some advanced features"
                    ),
                    DeveloperSuggestion(
                        "Use development mode for debugging",
                        "/dev-mode on",
                        "Development mode provides enhanced error reporting"
                    )
                ],
                debug_info={"command": command},
                original_error=error
            )
        
        return DeveloperError(
            f"Command failed: {command}",
            suggestions=[
                DeveloperSuggestion(
                    "Run the command manually to see detailed error",
                    command,
                    "This will show the full error output"
                ),
                DeveloperSuggestion(
                    "Check if all dependencies are installed",
                    "python .claude/scripts/dev_environment_validator.py",
                    "Missing dependencies often cause command failures"
                )
            ],
            debug_info={"command": command},
            original_error=error
        )
    
    def handle_json_error(self, error: Exception, file_path: str) -> DeveloperError:
        """Convert JSON errors to developer-friendly errors"""
        return DeveloperError(
            f"Invalid JSON in file: {Path(file_path).name}",
            suggestions=[
                DeveloperSuggestion(
                    "Validate JSON syntax",
                    f"python -m json.tool {file_path}",
                    "This will show exactly where the JSON syntax error is"
                ),
                DeveloperSuggestion(
                    "Backup and recreate the file",
                    f"cp {file_path} {file_path}.backup",
                    "Save the corrupted file before fixing it"
                ),
                DeveloperSuggestion(
                    "Use a JSON validator online",
                    "Copy the file content to jsonlint.com",
                    "Online tools can highlight JSON syntax errors"
                )
            ],
            debug_info={
                "file_path": file_path,
                "error_type": type(error).__name__
            },
            original_error=error
        )
    
    def wrap_function(self, func, *args, **kwargs):
        """Wrap function execution with developer-friendly error handling"""
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            module_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
            raise self.handle_import_error(e, module_name)
        except (FileNotFoundError, PermissionError, OSError) as e:
            file_path = getattr(e, 'filename', 'unknown file')
            raise self.handle_file_error(e, file_path)
        except subprocess.SubprocessError as e:
            command = getattr(e, 'cmd', 'unknown command')
            raise self.handle_subprocess_error(e, str(command))
        except (json.JSONDecodeError, ValueError) as e:
            if hasattr(e, 'doc'):
                raise self.handle_json_error(e, "settings file")
            else:
                raise DeveloperError(
                    f"Data format error: {str(e)}",
                    suggestions=[
                        DeveloperSuggestion(
                            "Check data format and syntax",
                            "Verify JSON, YAML, or other structured data is valid"
                        )
                    ],
                    original_error=e
                )
        except Exception as e:
            # Generic fallback with helpful context
            raise DeveloperError(
                f"Unexpected error: {str(e)}",
                suggestions=[
                    DeveloperSuggestion(
                        "Run environment validation",
                        "python .claude/scripts/dev_environment_validator.py",
                        "Check for common setup issues"
                    ),
                    DeveloperSuggestion(
                        "Enable development mode for more details",
                        "/dev-mode on",
                        "Development mode provides enhanced error reporting"
                    ),
                    DeveloperSuggestion(
                        "Check logs for more information",
                        "ls -la .claude/logs/",
                        "Log files may contain additional error context"
                    )
                ],
                debug_info={
                    "error_type": type(e).__name__,
                    "function": func.__name__ if hasattr(func, '__name__') else 'unknown',
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "platform": sys.platform
                },
                original_error=e
            )

# Convenience functions for common error patterns
def require_import(module_name: str):
    """Decorator to provide helpful error for missing imports"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            error_handler = DeveloperErrorHandler()
            return error_handler.wrap_function(func, *args, **kwargs)
        return wrapper
    return decorator

def developer_friendly(func):
    """Decorator to wrap functions with developer-friendly error handling"""
    def wrapper(*args, **kwargs):
        error_handler = DeveloperErrorHandler()
        return error_handler.wrap_function(func, *args, **kwargs)
    return wrapper