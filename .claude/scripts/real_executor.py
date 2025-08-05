#!/usr/bin/env python3
"""
Real Claude Code execution engine
Replaces simulation with actual command execution
"""

import asyncio
import json
import time
import os
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import logging
import sys
import platform
import subprocess

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None

@dataclass
class ExecutionResult:
    success: bool
    output: str = ""
    error: str = ""
    duration: float = 0.0
    command: str = ""
    agent_used: str = ""

class RealClaudeExecutor:
    """Real Claude Code command executor with monitoring and context management"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.context_cache = {}
        self.performance_monitor = PerformanceMonitor() if PerformanceMonitor else None
        
        # Setup logging
        self.setup_logging()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def setup_logging(self):
        """Setup structured logging"""
        log_dir = self.claude_dir / 'logs' / 'execution'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'executor_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def execute_command(self, command: str, context: Dict = None, timeout: int = 300) -> ExecutionResult:
        """Execute actual Claude Code command with enhanced monitoring and safe termination"""
        start_time = time.time()
        self.logger.info(f"Executing command: {command}")
        
        try:
            # Prepare context if provided
            if context:
                await self._prepare_context(context)
            
            # Validate command for basic safety
            if not self._validate_command(command):
                raise ValueError(f"Invalid or potentially unsafe command: {command}")
            
            # Execute the actual Claude Code command with process group
            process = await self._create_safe_subprocess(f'claude-code "{command}"')
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                await self._safe_terminate_process(process)
                raise asyncio.TimeoutError(f"Command timed out after {timeout} seconds")
            
            duration = time.time() - start_time
            success = process.returncode == 0
            
            result = ExecutionResult(
                success=success,
                output=stdout.decode('utf-8', errors='ignore'),
                error=stderr.decode('utf-8', errors='ignore'),
                duration=duration,
                command=command
            )
            
            # Track performance if monitor is available
            if self.performance_monitor:
                self.performance_monitor.track_command_execution(
                    command, duration, success
                )
            
            # Log result
            if success:
                self.logger.info(f"Command completed successfully in {duration:.2f}s")
            else:
                self.logger.error(f"Command failed after {duration:.2f}s: {result.error}")
            
            return result
            
        except asyncio.TimeoutError as e:
            duration = time.time() - start_time
            result = ExecutionResult(
                success=False,
                error=str(e),
                duration=duration,
                command=command
            )
            self.logger.error(f"Command timed out: {command}")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = ExecutionResult(
                success=False,
                error=f"Execution error: {str(e)}",
                duration=duration,
                command=command
            )
            self.logger.error(f"Command execution error: {e}")
            return result
    
    async def execute_agent_task(self, agent_name: str, task_description: str, 
                                context: Dict = None, timeout: int = 600) -> ExecutionResult:
        """Execute a task using a specific agent"""
        self.logger.info(f"Executing task with {agent_name}: {task_description}")
        
        # Construct agent-specific command
        agent_command = f"Use {agent_name} agent to: {task_description}"
        
        result = await self.execute_command(agent_command, context, timeout)
        result.agent_used = agent_name
        
        # Track agent performance if monitor available
        if self.performance_monitor:
            self.performance_monitor.track_agent_execution(
                agent_name, result.duration, result.success
            )
        
        return result
    
    async def _prepare_context(self, context: Dict):
        """Prepare context for command execution"""
        context_file = self.claude_dir / 'temp' / 'execution_context.json'
        context_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2, default=str)
        
        self.logger.debug(f"Context prepared: {len(context)} items")
    
    async def execute_batch(self, commands: List[str], max_concurrent: int = 4) -> List[ExecutionResult]:
        """Execute multiple commands concurrently"""
        self.logger.info(f"Executing batch of {len(commands)} commands")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(cmd):
            async with semaphore:
                return await self.execute_command(cmd)
        
        tasks = [execute_with_semaphore(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ExecutionResult(
                    success=False,
                    error=str(result),
                    command=commands[i]
                ))
            else:
                final_results.append(result)
        
        success_count = sum(1 for r in final_results if r.success)
        self.logger.info(f"Batch completed: {success_count}/{len(commands)} successful")
        
        return final_results
    
    def _validate_command(self, command: str) -> bool:
        """Basic command validation for internal dev use"""
        # Allow common Claude Code commands
        allowed_prefixes = [
            '/spec-', '/workflow-', '/planning', '/steering-', '/master-orchestrate',
            'Use ', 'python .claude/scripts/', '/log-manage', '/dashboard'
        ]
        
        # Check if command starts with allowed prefix
        for prefix in allowed_prefixes:
            if command.strip().startswith(prefix):
                return True
                
        # Log suspicious commands but don't block (internal use)
        self.logger.warning(f"Unusual command detected: {command}")
        return True  # Allow all commands for internal dev use
    
    async def execute_with_fallback(self, primary_command: str, fallback_command: str = None, context: Dict = None, timeout: int = 300) -> ExecutionResult:
        """Execute command with graceful fallback on failure"""
        try:
            # Try primary command first
            result = await self.execute_command(primary_command, context, timeout)
            if result.success:
                return result
            else:
                self.logger.warning(f"Primary command failed: {primary_command} - {result.error}")
                
                if fallback_command:
                    self.logger.info(f"Trying fallback: {fallback_command}")
                    fallback_result = await self.execute_command(fallback_command, context, timeout)
                    if fallback_result.success:
                        self.logger.info(f"Fallback succeeded: {fallback_command}")
                        return fallback_result
                    else:
                        self.logger.error(f"Fallback also failed: {fallback_command}")
                        # Return original failure with fallback context
                        result.error += f" (Fallback also failed: {fallback_result.error})"
                        return result
                else:
                    return result
                    
        except Exception as e:
            self.logger.error(f"Exception during command execution: {e}")
            return ExecutionResult(
                success=False,
                error=f"Command execution failed: {str(e)}",
                command=primary_command
            )
    
    async def _create_safe_subprocess(self, command: str):
        """Create subprocess with safe termination support"""
        if platform.system() == 'Windows':
            # Windows process creation
            return await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # Unix-like systems with process group
            return await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root,
                preexec_fn=os.setsid
            )
    
    async def _safe_terminate_process(self, process):
        """Safely terminate process with fallbacks"""
        self.logger.warning(f"Terminating process {process.pid} due to timeout")
        
        try:
            if platform.system() == 'Windows':
                # Windows process termination
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
            else:
                # Unix-like systems - terminate process group
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except (asyncio.TimeoutError, ProcessLookupError):
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        await process.wait()
                    except ProcessLookupError:
                        pass  # Process already dead
        except Exception as e:
            self.logger.error(f"Error terminating process: {e}")
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        if self.performance_monitor:
            return self.performance_monitor.get_performance_summary()
        return {"message": "Performance monitoring not available"}

def main():
    """Test the real executor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real Claude Code Executor')
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds')
    parser.add_argument('--context', help='JSON context file')
    
    args = parser.parse_args()
    
    executor = RealClaudeExecutor()
    
    # Load context if provided
    context = None
    if args.context:
        with open(args.context) as f:
            context = json.load(f)
    
    # Execute command
    result = asyncio.run(executor.execute_command(args.command, context, args.timeout))
    
    # Print result
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration:.2f}s")
    if result.output:
        print(f"Output: {result.output[:500]}...")
    if result.error:
        print(f"Error: {result.error}")

if __name__ == "__main__":
    main()