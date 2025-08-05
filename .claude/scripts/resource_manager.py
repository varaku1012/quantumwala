#!/usr/bin/env python3
"""
Resource management system for multi-agent execution
Manages CPU, memory, and concurrent task limits
"""

import asyncio
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict
import logging

@dataclass
class ResourceRequirements:
    cpu_percent: float = 20.0
    memory_mb: int = 512
    concurrent_slots: int = 1
    estimated_duration: int = 300  # seconds

@dataclass 
class TaskResource:
    task_id: str
    agent: str
    requirements: ResourceRequirements
    start_time: datetime
    pid: Optional[int] = None

class ResourceManager:
    """Manages system resources for concurrent agent execution"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        
        # Resource limits
        self.max_concurrent_tasks = 8
        self.cpu_limit = 80  # Max total CPU %
        self.memory_limit = 75  # Max memory %
        self.memory_reserve_mb = 1024  # Reserve memory
        
        # Current resource tracking
        self.active_tasks: Dict[str, TaskResource] = {}
        self.task_queue = asyncio.Queue()
        self.resource_lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            'tasks_executed': 0,
            'tasks_queued': 0,
            'resource_waits': 0,
            'peak_concurrent': 0
        }
        
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
        """Setup resource manager logging"""
        log_dir = self.claude_dir / 'logs' / 'resources'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'resources_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_system_load(self) -> float:
        """Get system load average (more stable than instant CPU usage)"""
        try:
            if hasattr(psutil, 'getloadavg'):
                # Unix systems - use load average
                load_avg = psutil.getloadavg()[0]  # 1-minute load average
                return load_avg / psutil.cpu_count()
            else:
                # Windows - use CPU percent over longer interval
                return psutil.cpu_percent(interval=1.0) / 100.0
        except Exception as e:
            self.logger.warning(f"Error getting system load: {e}")
            return 0.5  # Conservative fallback
    
    def get_memory_pressure(self) -> float:
        """Get memory pressure as a ratio (0.0 to 1.0)"""
        try:
            memory = psutil.virtual_memory()
            return memory.percent / 100.0
        except Exception as e:
            self.logger.warning(f"Error getting memory info: {e}")
            return 0.5  # Conservative fallback
    
    def estimate_resource_impact(self, requirements: ResourceRequirements) -> Dict[str, float]:
        """Estimate resource impact more accurately"""
        current_load = self.get_system_load()
        memory_pressure = self.get_memory_pressure()
        
        # Estimate CPU impact based on current load
        cpu_impact = requirements.cpu_percent / 100.0
        if current_load > 0.7:  # High load
            cpu_impact *= 1.5  # Commands will take longer
        
        # Estimate memory impact
        memory_impact = requirements.memory_mb / (psutil.virtual_memory().total / (1024 * 1024))
        
        return {
            'cpu_impact': cpu_impact,
            'memory_impact': memory_impact,
            'current_load': current_load,
            'memory_pressure': memory_pressure
        }
    
    async def can_execute(self, requirements: ResourceRequirements) -> bool:
        """Enhanced resource availability check with load-based decisions"""
        async with self.resource_lock:
            # Check concurrent task limit
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                self.logger.info(f"Max concurrent tasks reached: {len(self.active_tasks)}/{self.max_concurrent_tasks}")
                return False
            
            # Get enhanced resource analysis
            try:
                impact = self.estimate_resource_impact(requirements)
                
                # Decision based on system load rather than instant CPU
                if impact['current_load'] > 0.85:  # 85% load threshold
                    self.logger.info(f"System load too high: {impact['current_load']:.2f}")
                    return False
                
                # Memory pressure check
                if impact['memory_pressure'] > 0.80:  # 80% memory threshold
                    self.logger.info(f"Memory pressure too high: {impact['memory_pressure']:.2f}")
                    return False
                
                # Conservative check for high-impact tasks
                if impact['cpu_impact'] > 0.3 and impact['current_load'] > 0.6:
                    self.logger.info(f"High-impact task blocked due to existing load")
                    return False
                
                self.logger.debug(f"Resource check passed - Load: {impact['current_load']:.2f}, Memory: {impact['memory_pressure']:.2f}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error checking system resources: {e}")
                return len(self.active_tasks) < self.max_concurrent_tasks
    
    async def acquire_resources(self, task_id: str, agent: str, 
                               requirements: ResourceRequirements = None) -> bool:
        """Acquire resources for task execution"""
        if requirements is None:
            requirements = ResourceRequirements()
        
        self.logger.info(f"Acquiring resources for task {task_id} ({agent})")
        
        # Wait for resources to become available
        max_wait_time = 300  # 5 minutes
        wait_start = datetime.now()
        
        while not await self.can_execute(requirements):
            wait_duration = (datetime.now() - wait_start).seconds
            if wait_duration > max_wait_time:
                self.logger.error(f"Resource acquisition timeout for task {task_id}")
                return False
            
            self.stats['resource_waits'] += 1
            await asyncio.sleep(2)  # Check every 2 seconds
        
        # Acquire resources
        async with self.resource_lock:
            task_resource = TaskResource(
                task_id=task_id,
                agent=agent,
                requirements=requirements,
                start_time=datetime.now()
            )
            
            self.active_tasks[task_id] = task_resource
            self.stats['tasks_executed'] += 1
            self.stats['peak_concurrent'] = max(
                self.stats['peak_concurrent'], 
                len(self.active_tasks)
            )
            
            self.logger.info(
                f"Resources acquired for {task_id} - "
                f"Active: {len(self.active_tasks)}/{self.max_concurrent_tasks}"
            )
            
            return True
    
    async def release_resources(self, task_id: str):
        """Release resources after task completion"""
        async with self.resource_lock:
            if task_id in self.active_tasks:
                task = self.active_tasks.pop(task_id)
                duration = (datetime.now() - task.start_time).seconds
                
                self.logger.info(
                    f"Resources released for {task_id} after {duration}s - "
                    f"Active: {len(self.active_tasks)}/{self.max_concurrent_tasks}"
                )
            else:
                self.logger.warning(f"Attempted to release unknown task: {task_id}")
    
    def get_resource_status(self) -> Dict:
        """Get current resource status"""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            return {
                'system': {
                    'cpu_percent': cpu_usage,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / (1024 * 1024),
                    'memory_used_mb': memory.used / (1024 * 1024)
                },
                'limits': {
                    'max_concurrent_tasks': self.max_concurrent_tasks,
                    'cpu_limit': self.cpu_limit,
                    'memory_limit': self.memory_limit
                },
                'current': {
                    'active_tasks': len(self.active_tasks),
                    'task_ids': list(self.active_tasks.keys())
                },
                'statistics': self.stats.copy()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_active_tasks(self) -> List[Dict]:
        """Get list of currently active tasks"""
        tasks = []
        for task_id, task_resource in self.active_tasks.items():
            duration = (datetime.now() - task_resource.start_time).seconds
            tasks.append({
                'task_id': task_id,
                'agent': task_resource.agent,
                'duration_seconds': duration,
                'requirements': {
                    'cpu_percent': task_resource.requirements.cpu_percent,
                    'memory_mb': task_resource.requirements.memory_mb,
                    'concurrent_slots': task_resource.requirements.concurrent_slots
                }
            })
        return tasks
    
    async def wait_for_resources(self, requirements: ResourceRequirements, timeout: int = 300):
        """Wait for resources to become available"""
        start_time = datetime.now()
        
        while not await self.can_execute(requirements):
            elapsed = (datetime.now() - start_time).seconds
            if elapsed > timeout:
                raise TimeoutError(f"Resource wait timeout after {timeout}s")
            
            await asyncio.sleep(1)
    
    def update_limits(self, max_concurrent: int = None, cpu_limit: float = None, 
                     memory_limit: float = None):
        """Update resource limits"""
        if max_concurrent is not None:
            self.max_concurrent_tasks = max_concurrent
            self.logger.info(f"Updated max concurrent tasks to {max_concurrent}")
        
        if cpu_limit is not None:
            self.cpu_limit = cpu_limit
            self.logger.info(f"Updated CPU limit to {cpu_limit}%")
        
        if memory_limit is not None:
            self.memory_limit = memory_limit
            self.logger.info(f"Updated memory limit to {memory_limit}%")
    
    def save_stats(self):
        """Save resource statistics"""
        stats_file = self.claude_dir / 'logs' / 'resources' / 'stats.json'
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(stats_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'current_status': self.get_resource_status(),
                'session_stats': self.stats
            }, f, indent=2)

class ResourceContext:
    """Context manager for resource acquisition and release"""
    
    def __init__(self, resource_manager: ResourceManager, task_id: str, 
                 agent: str, requirements: ResourceRequirements = None):
        self.resource_manager = resource_manager
        self.task_id = task_id
        self.agent = agent
        self.requirements = requirements or ResourceRequirements()
        self.acquired = False
    
    async def __aenter__(self):
        self.acquired = await self.resource_manager.acquire_resources(
            self.task_id, self.agent, self.requirements
        )
        if not self.acquired:
            raise RuntimeError(f"Failed to acquire resources for task {self.task_id}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            await self.resource_manager.release_resources(self.task_id)

def main():
    """Test the resource manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Resource Manager Test')
    parser.add_argument('--status', action='store_true', help='Show resource status')
    parser.add_argument('--test', action='store_true', help='Run resource test')
    
    args = parser.parse_args()
    
    manager = ResourceManager()
    
    if args.status:
        status = manager.get_resource_status()
        print(json.dumps(status, indent=2))
    
    if args.test:
        async def test_resources():
            # Test resource acquisition
            req = ResourceRequirements(cpu_percent=30, memory_mb=1024)
            
            async with ResourceContext(manager, "test-task", "test-agent", req):
                print("Resources acquired successfully")
                await asyncio.sleep(2)
                print("Task simulation complete")
        
        asyncio.run(test_resources())

if __name__ == "__main__":
    main()