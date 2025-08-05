#!/usr/bin/env python3
"""
Command suggestion consumer
Reads suggestions from hooks and executes them automatically
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from real_executor import RealClaudeExecutor, ExecutionResult
    from resource_manager import ResourceManager, ResourceRequirements
    from unified_state import UnifiedStateManager
    from developer_errors import DeveloperError, DeveloperSuggestion, developer_friendly
except ImportError as e:
    # Create developer-friendly error message
    module_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
    
    if module_name in ['real_executor', 'resource_manager', 'unified_state']:
        print(f"\n❌ Cannot import Quantumwala module: {module_name}")
        print(f"\n💡 Try these solutions:")
        print(f"   1. Check you're in the project root directory")
        print(f"      Command: cd path/to/quantumwala && python .claude/scripts/suggestion_consumer.py")
        print(f"   2. Verify project structure")
        print(f"      Command: ls -la .claude/scripts/")
        print(f"   3. Run environment validation")
        print(f"      Command: python .claude/scripts/dev_environment_validator.py")
        print(f"\n🔍 Debug Information:")
        print(f"   • Module: {module_name}")
        print(f"   • Current directory: {Path.cwd()}")
        print(f"   • Python version: {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print(f"\n❌ Missing Python package: {module_name}")
        print(f"\n💡 Try these solutions:")
        print(f"   1. Install the package")
        print(f"      Command: pip install {module_name}")
        print(f"   2. Run environment validation")
        print(f"      Command: python .claude/scripts/dev_environment_validator.py")
    
    sys.exit(1)

class SuggestionConsumer:
    """Consumes command suggestions from hooks and executes them"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        
        # Core components
        self.executor = RealClaudeExecutor(self.project_root)
        self.resource_manager = ResourceManager(self.project_root)
        self.state_manager = UnifiedStateManager()
        
        # Configuration files
        self.suggestion_file = self.claude_dir / 'next_command.txt'
        self.config_file = self.claude_dir / 'settings.local.json'
        self.execution_log = self.claude_dir / 'logs' / 'sessions' / 'auto_execution.log'
        
        # Execution settings
        self.auto_execution_enabled = True
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        self.setup_logging()
        self.load_config()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def setup_logging(self):
        """Setup suggestion consumer logging"""
        log_dir = self.claude_dir / 'logs' / 'execution'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'suggestion_consumer_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        """Load configuration from settings file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                
                workflow_config = config.get('workflow', {})
                self.auto_execution_enabled = workflow_config.get('auto_progression', True)
                self.max_retries = workflow_config.get('max_retries', 3)
                self.retry_delay = workflow_config.get('retry_delay', 5)
                
                self.logger.info(f"Configuration loaded - Auto-execution: {self.auto_execution_enabled}")
                
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
    
    async def check_for_suggestions(self) -> Optional[str]:
        """Check for command suggestions from hooks"""
        if not self.suggestion_file.exists():
            return None
        
        try:
            command = self.suggestion_file.read_text().strip()
            if command:
                self.logger.info(f"Found suggested command: {command}")
                return command
        except Exception as e:
            self.logger.error(f"Error reading suggestion file: {e}")
        
        return None
    
    async def execute_suggestion(self, command: str) -> ExecutionResult:
        """Execute a suggested command with enhanced resource management and error handling"""
        self.logger.info(f"🚀 Executing suggested command: {command}")
        
        # Validate command before execution
        if not self._validate_command_safety(command):
            error_msg = f"Command validation failed: {command}"
            self.logger.error(error_msg)
            return ExecutionResult(
                success=False,
                error=error_msg,
                command=command
            )
        
        # Estimate resource requirements based on command type
        requirements = self._estimate_requirements(command)
        task_id = f"suggestion_{int(time.time())}"
        
        try:
            # Try to acquire resources with timeout
            resource_acquired = await asyncio.wait_for(
                self.resource_manager.acquire_resources(task_id, "suggestion_consumer", requirements),
                timeout=60.0  # 1 minute timeout for resource acquisition
            )
            
            if resource_acquired:
                try:
                    # Execute the command with timeout
                    result = await asyncio.wait_for(
                        self.executor.execute_command(command),
                        timeout=requirements.estimated_duration + 60  # Add buffer time
                    )
                    
                    # Log execution with enhanced context
                    await self._log_execution(command, result)
                    
                    return result
                    
                except asyncio.TimeoutError:
                    timeout_error = f"Command execution timed out after {requirements.estimated_duration + 60}s"
                    self.logger.error(timeout_error)
                    return ExecutionResult(
                        success=False,
                        error=timeout_error,
                        command=command,
                        duration=requirements.estimated_duration + 60
                    )
                finally:
                    # Always release resources
                    try:
                        await self.resource_manager.release_resources(task_id)
                    except Exception as release_error:
                        self.logger.error(f"Failed to release resources: {release_error}")
            else:
                error_msg = f"Failed to acquire resources for command: {command}"
                self.logger.error(error_msg)
                return ExecutionResult(
                    success=False,
                    error=error_msg,
                    command=command
                )
                
        except asyncio.TimeoutError:
            timeout_error = "Resource acquisition timed out"
            self.logger.error(timeout_error)
            return ExecutionResult(
                success=False,
                error=timeout_error,
                command=command
            )
        except Exception as e:
            error_msg = f"Unexpected error executing suggestion: {str(e)}"
            self.logger.error(error_msg)
            
            # Try to release resources in case they were acquired
            try:
                await self.resource_manager.release_resources(task_id)
            except:
                pass  # Ignore cleanup errors
                
            return ExecutionResult(
                success=False,
                error=error_msg,
                command=command
            )
    
    def _validate_command_safety(self, command: str) -> bool:
        """Basic command safety validation for internal use"""
        # For internal dev use, mostly just log suspicious commands
        suspicious_patterns = ['rm -rf', 'del /s', 'format', 'shutdown', 'reboot']
        
        for pattern in suspicious_patterns:
            if pattern.lower() in command.lower():
                self.logger.warning(f"Potentially dangerous command detected: {command}")
                return False  # Block clearly dangerous commands
        
        return True
    
    def _estimate_requirements(self, command: str) -> ResourceRequirements:
        """Estimate resource requirements based on command type"""
        # Basic heuristics for resource estimation
        if any(keyword in command.lower() for keyword in ['orchestrate', 'master', 'workflow-auto']):
            return ResourceRequirements(cpu_percent=40, memory_mb=1024, estimated_duration=1800)
        elif any(keyword in command.lower() for keyword in ['spec-tasks', 'planning', 'spec-design']):
            return ResourceRequirements(cpu_percent=25, memory_mb=512, estimated_duration=600)
        elif any(keyword in command.lower() for keyword in ['spec-requirements', 'spec-create']):
            return ResourceRequirements(cpu_percent=20, memory_mb=256, estimated_duration=300)
        else:
            return ResourceRequirements(cpu_percent=15, memory_mb=256, estimated_duration=180)
    
    async def _log_execution(self, command: str, result: ExecutionResult):
        """Enhanced execution logging with context and error details"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'success': result.success,
            'duration': result.duration,
            'output_length': len(result.output) if result.output else 0,
            'error': result.error if result.error else None,
            'agent_used': getattr(result, 'agent_used', None),
            'context': {
                'concurrent_tasks': len(self.resource_manager.active_tasks) if hasattr(self.resource_manager, 'active_tasks') else 0,
                'system_load': self.resource_manager.get_system_load() if hasattr(self.resource_manager, 'get_system_load') else None
            }
        }
        
        # Append to execution log with error handling
        self.execution_log.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.execution_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, default=str) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write execution log: {e}")
            # Try to write to fallback location
            try:
                fallback_log = self.claude_dir / 'logs' / 'execution_fallback.log'
                with open(fallback_log, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now().isoformat()}: {command} - {result.success} - {result.error or 'No error'}\n")
            except:
                pass  # Silent fallback failure
    
    async def process_suggestion_with_retry(self, command: str) -> ExecutionResult:
        """Process suggestion with retry logic"""
        last_result = None
        
        for attempt in range(self.max_retries):
            try:
                result = await self.execute_suggestion(command)
                
                if result.success:
                    self.logger.info(f"✅ Command executed successfully on attempt {attempt + 1}")
                    # Remove suggestion file on success
                    if self.suggestion_file.exists():
                        self.suggestion_file.unlink()
                    return result
                else:
                    self.logger.warning(f"❌ Command failed on attempt {attempt + 1}: {result.error}")
                    last_result = result
                    
                    if attempt < self.max_retries - 1:
                        self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                        
            except Exception as e:
                self.logger.error(f"Exception during attempt {attempt + 1}: {e}")
                last_result = ExecutionResult(
                    success=False,
                    error=str(e),
                    command=command
                )
        
        # All retries failed
        self.logger.error(f"Command failed after {self.max_retries} attempts")
        return last_result or ExecutionResult(
            success=False,
            error="Max retries exceeded",
            command=command
        )
    
    async def run_once(self) -> bool:
        """Check for and process one suggestion"""
        if not self.auto_execution_enabled:
            return False
        
        command = await self.check_for_suggestions()
        if not command:
            return False
        
        result = await self.process_suggestion_with_retry(command)
        
        if result.success:
            self.logger.info("Suggestion processed successfully")
            # Update workflow state if applicable
            await self._update_workflow_state(command, result)
        else:
            self.logger.error(f"Suggestion processing failed: {result.error}")
        
        return True
    
    async def _update_workflow_state(self, command: str, result: ExecutionResult):
        """Update workflow state based on command execution"""
        try:
            # Extract phase information from command
            if '/spec-create' in command:
                self.state_manager.update_workflow_phase('spec_creation')
            elif '/spec-requirements' in command:
                self.state_manager.update_workflow_phase('requirements_generation')
            elif '/spec-design' in command:
                self.state_manager.update_workflow_phase('design_creation')
            elif '/spec-tasks' in command:
                self.state_manager.update_workflow_phase('task_generation')
            elif 'implementation' in command:
                self.state_manager.update_workflow_phase('implementation')
            elif '/spec-review' in command:
                self.state_manager.update_workflow_phase('validation')
                
        except Exception as e:
            self.logger.error(f"Error updating workflow state: {e}")
    
    async def run_continuous(self, check_interval: int = 10):
        """Run continuous suggestion monitoring"""
        self.logger.info(f"Starting continuous suggestion monitoring (interval: {check_interval}s)")
        
        while True:
            try:
                processed = await self.run_once()
                if not processed:
                    await asyncio.sleep(check_interval)
                else:
                    # If we processed something, check again quickly
                    await asyncio.sleep(2)
                    
            except KeyboardInterrupt:
                self.logger.info("Suggestion consumer stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous loop: {e}")
                await asyncio.sleep(check_interval)
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'recent_commands': []
        }
        
        if self.execution_log.exists():
            try:
                with open(self.execution_log) as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        stats['total_executions'] += 1
                        
                        if entry['success']:
                            stats['successful_executions'] += 1
                        else:
                            stats['failed_executions'] += 1
                        
                        # Keep last 10 commands
                        if len(stats['recent_commands']) < 10:
                            stats['recent_commands'].append({
                                'command': entry['command'],
                                'success': entry['success'],
                                'timestamp': entry['timestamp'],
                                'duration': entry.get('duration', 0)
                            })
                            
            except Exception as e:
                stats['error'] = str(e)
        
        return stats

def main():
    """Main function for running suggestion consumer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Command Suggestion Consumer')
    parser.add_argument('--once', action='store_true', help='Process one suggestion and exit')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=10, help='Check interval in seconds')
    parser.add_argument('--stats', action='store_true', help='Show execution statistics')
    
    args = parser.parse_args()
    
    consumer = SuggestionConsumer()
    
    if args.stats:
        stats = consumer.get_execution_stats()
        print(json.dumps(stats, indent=2))
        return
    
    if args.once:
        result = asyncio.run(consumer.run_once())
        if result:
            print("Suggestion processed")
        else:
            print("No suggestions found")
    elif args.continuous:
        asyncio.run(consumer.run_continuous(args.interval))
    else:
        print("Use --once, --continuous, or --stats")

if __name__ == "__main__":
    main()