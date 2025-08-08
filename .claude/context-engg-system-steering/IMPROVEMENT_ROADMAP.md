# Context Engineering System - Improvement Roadmap

## Executive Summary
**Current State**: 35% Functional  
**Target State**: 95% Production-Ready  
**Timeline**: 6 weeks  
**Risk**: CRITICAL - System not working as designed

---

# PHASE 1: CRITICAL FIXES (Week 1)
*Make the system actually work*

## 1.1 Connect Agent Tool Bridge

### Problem
The bridge exists but isn't connected to anything.

### Solution
```python
# Fix 1: Update real_executor.py
from agent_tool_bridge import AgentToolBridge, TaskRequest

class RealClaudeExecutor:
    def __init__(self, project_root=None):
        self.project_root = project_root
        self.bridge = AgentToolBridge(project_root)  # ADD THIS
    
    async def handle_task_delegation(self, agent, description, context):
        """New method to handle Task tool calls"""
        request = TaskRequest(
            agent=agent,
            description=description,
            context=context,
            parent_agent='system'
        )
        return await self.bridge.process_task_delegation(request)
```

### Files to Update
- [ ] `real_executor.py` - Add bridge integration
- [ ] `unified_workflow.py` - Use bridge for delegations
- [ ] `parallel_workflow_orchestrator.py` - Route through bridge

## 1.2 Fix Memory Persistence

### Problem  
Memory is only in-memory, lost on restart.

### Solution
```python
# Fix 2: Update memory_manager.py
import sqlite3
import json
from pathlib import Path

class MemoryManager:
    def __init__(self, project_root=None):
        self.project_root = project_root or Path.cwd()
        self.db_path = self.project_root / '.claude' / 'data' / 'memory.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    agent TEXT,
                    context TEXT,
                    result TEXT,
                    success BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_task (task_id),
                    INDEX idx_agent (agent)
                )
            ''')
```

## 1.3 Implement Real Token Counting

### Problem
Using len(text)//4 instead of actual token counting.

### Solution
```python
# Fix 3: Update context_engine.py
import tiktoken

class ContextCompressor:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self._token_cache = {}  # Cache for performance
    
    def count_tokens(self, text: str) -> int:
        """Actually count tokens properly"""
        cache_key = hash(text)
        if cache_key not in self._token_cache:
            self._token_cache[cache_key] = len(self.encoder.encode(text))
        return self._token_cache[cache_key]
    
    def compress(self, text: str, max_tokens: int = 4000) -> str:
        current_tokens = self.count_tokens(text)
        if current_tokens <= max_tokens:
            return text
        
        # Progressive compression with real token counting
        return self._compress_to_fit(text, max_tokens)
```

---

# PHASE 2: SECURITY & SAFETY (Week 2)
*Fix dangerous vulnerabilities*

## 2.1 Fix Command Injection

### Problem
Using shell=True with user input.

### Solution
```python
# Fix 4: Safe command execution
import shlex
import subprocess

def safe_execute(command: str, args: list):
    """Execute commands safely without shell injection"""
    cmd_parts = [command] + [shlex.quote(arg) for arg in args]
    
    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            check=True,
            shell=False,  # NEVER use shell=True
            timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out: {command}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr}")
```

## 2.2 Add Input Validation

### Solution
```python
# Fix 5: Input validation
import re
from pathlib import Path

class InputValidator:
    @staticmethod
    def validate_path(user_path: str, base_dir: Path) -> Path:
        """Prevent path traversal attacks"""
        # Resolve to absolute path
        requested = (base_dir / user_path).resolve()
        
        # Ensure it's within base directory
        if not str(requested).startswith(str(base_dir.resolve())):
            raise ValueError(f"Path traversal attempt: {user_path}")
        
        return requested
    
    @staticmethod
    def validate_spec_name(name: str) -> str:
        """Ensure spec names are safe"""
        if not re.match(r'^[a-z0-9-]+$', name):
            raise ValueError(f"Invalid spec name: {name}")
        return name
```

## 2.3 Add Error Handling

### Solution
```python
# Fix 6: Comprehensive error handling
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class WorkflowError(Exception):
    """Base exception for workflow errors"""
    pass

class RecoverableError(WorkflowError):
    """Errors that can be recovered from"""
    def __init__(self, message, recovery_action=None):
        super().__init__(message)
        self.recovery_action = recovery_action

async def execute_with_recovery(func, *args, **kwargs):
    """Execute with automatic recovery"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except RecoverableError as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if e.recovery_action:
                await e.recovery_action()
        except Exception as e:
            logger.error(f"Unrecoverable error: {e}")
            raise
    
    raise WorkflowError(f"Failed after {max_retries} attempts")
```

---

# PHASE 3: INTEGRATION (Week 3)
*Connect all components properly*

## 3.1 Wire Up Components

### Solution
```python
# Fix 7: Proper component integration
class IntegratedSystem:
    def __init__(self):
        # Initialize all components
        self.context_engine = ContextEngine()
        self.memory_manager = MemoryManager()
        self.tool_bridge = AgentToolBridge()
        self.executor = RealClaudeExecutor()
        
        # Wire them together
        self.tool_bridge.memory_manager = self.memory_manager
        self.tool_bridge.context_engine = self.context_engine
        self.executor.bridge = self.tool_bridge
        
        # Setup event bus for loose coupling
        self.event_bus = EventBus()
        self._register_handlers()
```

## 3.2 Add Monitoring

### Solution
```python
# Fix 8: Real-time monitoring
from prometheus_client import Counter, Histogram, Gauge

# Metrics
task_counter = Counter('tasks_total', 'Total tasks executed', ['agent', 'status'])
task_duration = Histogram('task_duration_seconds', 'Task execution time', ['agent'])
active_workflows = Gauge('active_workflows', 'Currently active workflows')

class MonitoredExecutor:
    async def execute(self, agent, task):
        active_workflows.inc()
        
        with task_duration.labels(agent=agent).time():
            try:
                result = await self._execute_internal(agent, task)
                task_counter.labels(agent=agent, status='success').inc()
                return result
            except Exception as e:
                task_counter.labels(agent=agent, status='failure').inc()
                raise
            finally:
                active_workflows.dec()
```

---

# PHASE 4: TESTING (Week 4)
*Add comprehensive testing*

## 4.1 Unit Tests

### Solution
```python
# tests/test_context_engine.py
import pytest
from context_engine import ContextEngine

class TestContextEngine:
    def test_compression_preserves_meaning(self):
        engine = ContextEngine()
        original = "This is important. This is not." * 100
        compressed = engine.compress(original, max_tokens=50)
        
        assert "important" in compressed
        assert engine.count_tokens(compressed) <= 50
    
    def test_isolation_prevents_contamination(self):
        engine = ContextEngine()
        context1 = {"data": "sensitive"}
        context2 = engine.isolate(context1)
        
        context2["data"] = "modified"
        assert context1["data"] == "sensitive"
```

## 4.2 Integration Tests

### Solution
```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_full_workflow():
    system = IntegratedSystem()
    
    # Create a test workflow
    result = await system.execute_workflow(
        description="test feature",
        mode="sequential"
    )
    
    assert result['success']
    assert len(result['phases_completed']) > 0
    
    # Verify memory was stored
    memories = system.memory_manager.get_recent(1)
    assert len(memories) > 0
```

---

# PHASE 5: PERFORMANCE (Week 5)
*Optimize for production use*

## 5.1 Add Caching

### Solution
```python
# Fix 9: Implement caching
from functools import lru_cache
import hashlib

class CachedContextEngine:
    def __init__(self):
        self._cache = {}
    
    @lru_cache(maxsize=100)
    def compress(self, text_hash: str, max_tokens: int):
        """Cache compression results"""
        # Actual compression logic
        pass
    
    def compress_text(self, text: str, max_tokens: int):
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.compress(text_hash, max_tokens)
```

## 5.2 Async I/O

### Solution
```python
# Fix 10: Use async file operations
import aiofiles

async def read_file_async(path: Path) -> str:
    async with aiofiles.open(path, 'r') as f:
        return await f.read()

async def write_file_async(path: Path, content: str):
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)
```

---

# PHASE 6: PRODUCTION READY (Week 6)
*Final polish and deployment prep*

## 6.1 Configuration Management

### Solution
```yaml
# config/production.yaml
context:
  max_tokens: 4000
  compression:
    enabled: true
    levels: [whitespace, summarize, truncate]
    
memory:
  backend: postgresql
  connection: ${DATABASE_URL}
  cache:
    ttl: 3600
    max_size: 1000
    
monitoring:
  enabled: true
  metrics_port: 9090
  
security:
  rate_limit:
    requests_per_minute: 60
  input_validation:
    strict: true
```

## 6.2 Health Checks

### Solution
```python
# Fix 11: System health monitoring
class HealthChecker:
    async def check_health(self) -> dict:
        checks = {
            'database': await self._check_database(),
            'memory': await self._check_memory(),
            'disk': await self._check_disk_space(),
            'api': await self._check_external_apis()
        }
        
        overall = all(check['healthy'] for check in checks.values())
        
        return {
            'healthy': overall,
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }
```

---

# Implementation Priority Matrix

| Priority | Component | Risk | Effort | Impact |
|----------|-----------|------|--------|--------|
| P0 | Agent Tool Bridge Connection | Critical | Low | High |
| P0 | Memory Persistence | Critical | Medium | High |
| P0 | Token Counting | Critical | Low | High |
| P1 | Security Fixes | Critical | Medium | High |
| P1 | Error Handling | High | Medium | High |
| P2 | Integration | High | High | High |
| P2 | Testing | Medium | High | High |
| P3 | Performance | Low | Medium | Medium |
| P3 | Monitoring | Low | Medium | Medium |

---

# Success Metrics

## Week 1 Goals
- [ ] Tool Bridge connected and working
- [ ] Memory persists across restarts
- [ ] Token counting accurate within 5%

## Week 2 Goals
- [ ] Zero security vulnerabilities
- [ ] All inputs validated
- [ ] Error recovery implemented

## Week 3 Goals
- [ ] All components integrated
- [ ] Monitoring dashboard functional
- [ ] Event bus operational

## Week 4 Goals
- [ ] 80% test coverage
- [ ] All critical paths tested
- [ ] Performance benchmarks established

## Week 5 Goals
- [ ] Response time < 2s
- [ ] Memory usage < 500MB
- [ ] Cache hit rate > 70%

## Week 6 Goals
- [ ] Production configuration ready
- [ ] Health checks passing
- [ ] Documentation complete

---

# Next Steps

1. **Today**: Fix Agent Tool Bridge connection
2. **Tomorrow**: Implement memory persistence
3. **This Week**: Complete Phase 1 critical fixes
4. **Next Week**: Security audit and fixes
5. **Month End**: System ready for testing

## Resources Needed
- SQLite/PostgreSQL for persistence
- Redis for caching (optional)
- Monitoring stack (Prometheus/Grafana)
- Test infrastructure
- CI/CD pipeline

---

# Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking changes | Feature flags for gradual rollout |
| Data loss | Backup before changes |
| Performance degradation | Load testing before deployment |
| Security vulnerabilities | Security audit and penetration testing |

---

**Remember**: Fix critical issues first. The system is NOT production-ready until Phase 2 is complete.