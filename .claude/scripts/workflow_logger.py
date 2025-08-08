#!/usr/bin/env python3
"""
Comprehensive Workflow Logging System
Provides detailed logging for all workflow executions with multiple outputs
"""

import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import traceback

class WorkflowLogger:
    """
    Comprehensive logging system for workflow execution
    Supports multiple outputs: console, file, JSON, and structured logs
    """
    
    def __init__(self, 
                 workflow_id: str,
                 spec_name: str,
                 log_level: str = "INFO",
                 enable_file_logging: bool = True,
                 enable_json_logging: bool = True,
                 enable_console: bool = True):
        """
        Initialize workflow logger
        
        Args:
            workflow_id: Unique workflow identifier
            spec_name: Name of the spec being processed
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_file_logging: Write logs to file
            enable_json_logging: Write structured JSON logs
            enable_console: Output to console
        """
        self.workflow_id = workflow_id
        self.spec_name = spec_name
        self.start_time = datetime.now()
        
        # Setup log directory
        # Get absolute path to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self.log_dir = project_root / ".claude/logs/workflows"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup different log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{timestamp}_{spec_name}_{workflow_id}.log"
        self.json_log_file = self.log_dir / f"{timestamp}_{spec_name}_{workflow_id}.json"
        self.summary_file = self.log_dir / f"{timestamp}_{spec_name}_summary.md"
        
        # Initialize structured log data
        self.structured_log = {
            "workflow_id": workflow_id,
            "spec_name": spec_name,
            "start_time": self.start_time.isoformat(),
            "phases": {},
            "agents_called": [],
            "tools_used": [],
            "files_created": [],
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        # Setup Python logger
        self.logger = logging.getLogger(f"workflow.{workflow_id}")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self._get_console_formatter())
            self.logger.addHandler(console_handler)
        
        # File handler
        if enable_file_logging:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setFormatter(self._get_file_formatter())
            self.logger.addHandler(file_handler)
        
        # JSON handler
        if enable_json_logging:
            self.json_handler = JsonLogHandler(self.json_log_file)
            self.logger.addHandler(self.json_handler)
        
        # Current phase tracking
        self.current_phase = None
        self.phase_start_time = None
        
    def _get_console_formatter(self):
        """Get formatter for console output"""
        return logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _get_file_formatter(self):
        """Get formatter for file output"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
    
    # Phase Management
    
    def start_phase(self, phase_name: str, description: str = ""):
        """Log the start of a workflow phase"""
        self.current_phase = phase_name
        self.phase_start_time = datetime.now()
        
        self.logger.info(f"{'='*60}")
        self.logger.info(f"PHASE START: {phase_name}")
        if description:
            self.logger.info(f"Description: {description}")
        self.logger.info(f"{'='*60}")
        
        # Update structured log
        self.structured_log["phases"][phase_name] = {
            "start_time": self.phase_start_time.isoformat(),
            "description": description,
            "status": "in_progress",
            "logs": [],
            "metrics": {}
        }
    
    def end_phase(self, phase_name: str, status: str = "success", error: str = None):
        """Log the end of a workflow phase"""
        if phase_name not in self.structured_log["phases"]:
            self.logger.warning(f"Ending phase {phase_name} that was not started")
            return
        
        duration = (datetime.now() - self.phase_start_time).total_seconds()
        
        self.logger.info(f"{'-'*60}")
        self.logger.info(f"PHASE END: {phase_name}")
        self.logger.info(f"Status: {status.upper()}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        if error:
            self.logger.error(f"Error: {error}")
        self.logger.info(f"{'-'*60}\n")
        
        # Update structured log
        phase_data = self.structured_log["phases"][phase_name]
        phase_data["end_time"] = datetime.now().isoformat()
        phase_data["duration_seconds"] = duration
        phase_data["status"] = status
        if error:
            phase_data["error"] = error
    
    # Agent and Tool Tracking
    
    def log_agent_call(self, agent_name: str, task: str, context: Dict[str, Any] = None):
        """Log when an agent is called"""
        self.logger.info(f"Calling Agent: {agent_name}")
        self.logger.info(f"  Task: {task}")
        if context:
            self.logger.debug(f"  Context: {json.dumps(context, indent=2)}")
        
        # Track in structured log
        agent_call = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "task": task,
            "phase": self.current_phase,
            "context_size": len(str(context)) if context else 0
        }
        self.structured_log["agents_called"].append(agent_call)
    
    def log_agent_response(self, agent_name: str, success: bool, response: Any = None, error: str = None):
        """Log agent response"""
        if success:
            self.logger.info(f"Agent {agent_name} completed successfully")
            if response:
                self.logger.debug(f"  Response preview: {str(response)[:200]}")
        else:
            self.logger.error(f"Agent {agent_name} failed: {error}")
        
        # Update last agent call
        if self.structured_log["agents_called"]:
            self.structured_log["agents_called"][-1]["success"] = success
            if error:
                self.structured_log["agents_called"][-1]["error"] = error
    
    def log_tool_use(self, tool_name: str, parameters: Dict[str, Any] = None):
        """Log tool usage"""
        self.logger.debug(f"Using tool: {tool_name}")
        if parameters:
            self.logger.debug(f"  Parameters: {json.dumps(parameters, indent=2)}")
        
        # Track in structured log
        tool_use = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "phase": self.current_phase,
            "parameters": parameters
        }
        self.structured_log["tools_used"].append(tool_use)
    
    # File Operations
    
    def log_file_created(self, file_path: str, file_type: str = "code"):
        """Log file creation"""
        self.logger.info(f"Created {file_type} file: {file_path}")
        
        # Track in structured log
        self.structured_log["files_created"].append({
            "path": file_path,
            "type": file_type,
            "phase": self.current_phase,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_directory_created(self, dir_path: str):
        """Log directory creation"""
        self.logger.debug(f"Created directory: {dir_path}")
    
    # Error and Warning Management
    
    def log_error(self, error_message: str, exception: Exception = None):
        """Log an error with optional exception details"""
        self.logger.error(error_message)
        if exception:
            self.logger.error(f"Exception: {str(exception)}")
            self.logger.debug(traceback.format_exc())
        
        # Track in structured log
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase,
            "message": error_message,
            "exception": str(exception) if exception else None,
            "traceback": traceback.format_exc() if exception else None
        }
        self.structured_log["errors"].append(error_data)
    
    def log_warning(self, warning_message: str):
        """Log a warning"""
        self.logger.warning(warning_message)
        
        # Track in structured log
        self.structured_log["warnings"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase,
            "message": warning_message
        })
    
    # Metrics and Performance
    
    def log_metric(self, metric_name: str, value: Any, unit: str = None):
        """Log a performance metric"""
        message = f"Metric: {metric_name} = {value}"
        if unit:
            message += f" {unit}"
        self.logger.info(message)
        
        # Track in structured log
        self.structured_log["metrics"][metric_name] = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase
        }
    
    # Progress Tracking
    
    def log_progress(self, current: int, total: int, description: str = ""):
        """Log progress of a task"""
        percentage = (current / total * 100) if total > 0 else 0
        self.logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - {description}")
    
    # Workflow Summary
    
    def generate_summary(self):
        """Generate and save workflow summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = f"""# Workflow Execution Summary

## Overview
- **Workflow ID**: {self.workflow_id}
- **Spec Name**: {self.spec_name}
- **Start Time**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Duration**: {duration:.2f} seconds
- **Status**: {self._get_overall_status()}

## Phases Executed
"""
        
        for phase_name, phase_data in self.structured_log["phases"].items():
            status_icon = "✅" if phase_data["status"] == "success" else "❌"
            phase_duration = phase_data.get("duration_seconds", 0)
            summary += f"- {status_icon} **{phase_name}** ({phase_duration:.2f}s)\n"
            if phase_data.get("error"):
                summary += f"  - Error: {phase_data['error']}\n"
        
        summary += f"""
## Agents Called
- Total: {len(self.structured_log['agents_called'])}
- Successful: {sum(1 for a in self.structured_log['agents_called'] if a.get('success', False))}
- Failed: {sum(1 for a in self.structured_log['agents_called'] if not a.get('success', True))}

## Files Created
- Total Files: {len(self.structured_log['files_created'])}
- Code Files: {sum(1 for f in self.structured_log['files_created'] if f['type'] == 'code')}
- Test Files: {sum(1 for f in self.structured_log['files_created'] if f['type'] == 'test')}
- Config Files: {sum(1 for f in self.structured_log['files_created'] if f['type'] == 'config')}

## Issues
- Errors: {len(self.structured_log['errors'])}
- Warnings: {len(self.structured_log['warnings'])}
"""
        
        if self.structured_log['errors']:
            summary += "\n### Errors:\n"
            for error in self.structured_log['errors']:
                summary += f"- {error['message']} (Phase: {error['phase']})\n"
        
        if self.structured_log['warnings']:
            summary += "\n### Warnings:\n"
            for warning in self.structured_log['warnings']:
                summary += f"- {warning['message']} (Phase: {warning['phase']})\n"
        
        # Save summary
        self.summary_file.write_text(summary, encoding='utf-8')
        self.logger.info(f"Summary saved to: {self.summary_file}")
        
        # Also save final JSON log
        self.save_json_log()
        
        return summary
    
    def save_json_log(self):
        """Save structured log as JSON"""
        self.structured_log["end_time"] = datetime.now().isoformat()
        self.structured_log["total_duration_seconds"] = (datetime.now() - self.start_time).total_seconds()
        
        with open(self.json_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.structured_log, f, indent=2)
        
        self.logger.info(f"JSON log saved to: {self.json_log_file}")
    
    def _get_overall_status(self):
        """Determine overall workflow status"""
        if self.structured_log["errors"]:
            return "FAILED"
        elif self.structured_log["warnings"]:
            return "COMPLETED_WITH_WARNINGS"
        else:
            return "SUCCESS"
    
    # Context Manager Support
    
    def __enter__(self):
        """Enter context manager"""
        self.logger.info(f"Starting workflow: {self.workflow_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and generate summary"""
        if exc_type:
            self.log_error(f"Workflow failed with exception: {exc_type.__name__}", exc_val)
        
        self.generate_summary()
        self.logger.info(f"Workflow completed: {self.workflow_id}")


class JsonLogHandler(logging.Handler):
    """Custom handler for JSON structured logging"""
    
    def __init__(self, json_file):
        super().__init__()
        self.json_file = json_file
        self.logs = []
    
    def emit(self, record):
        """Emit a log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_entry["exception"] = self.format(record)
        
        self.logs.append(log_entry)
    
    def close(self):
        """Save all logs to JSON file"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2)
        super().close()


# Convenience function for quick setup
def setup_workflow_logger(spec_name: str, log_level: str = "INFO") -> WorkflowLogger:
    """
    Quick setup function for workflow logger
    
    Args:
        spec_name: Name of the spec being processed
        log_level: Logging level
    
    Returns:
        Configured WorkflowLogger instance
    """
    workflow_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return WorkflowLogger(workflow_id, spec_name, log_level)


# Example usage
if __name__ == "__main__":
    # Example of how to use the workflow logger
    
    with setup_workflow_logger("test-spec", "DEBUG") as logger:
        # Phase 1
        logger.start_phase("Initialization", "Setting up workflow environment")
        logger.log_metric("memory_usage", 1024, "MB")
        logger.log_directory_created("/test/dir")
        logger.end_phase("Initialization")
        
        # Phase 2
        logger.start_phase("Processing", "Processing spec data")
        logger.log_agent_call("developer", "Generate code", {"spec": "test"})
        logger.log_tool_use("Write", {"file": "test.py"})
        logger.log_file_created("test.py", "code")
        logger.log_agent_response("developer", True, "Code generated")
        logger.log_progress(5, 10, "Processing files")
        logger.end_phase("Processing")
        
        # Phase 3 with error
        logger.start_phase("Validation", "Validating output")
        try:
            # Simulate error
            raise ValueError("Test error")
        except Exception as e:
            logger.log_error("Validation failed", e)
            logger.end_phase("Validation", "failed", str(e))
    
    print("Logging example completed - check .claude/logs/workflows/")