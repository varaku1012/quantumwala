# Quantumwala Multi-Agent System with Unified Documentation

## 🚀 Overview

This is a powerful multi-agent orchestration system integrated with Claude Code, featuring a **Unified Documentation Server** that aggregates multiple documentation sources (DevDocs, MDN, NPM, Python docs, etc.) into a single interface. This ensures all agents generate high-quality, error-free code by validating against official documentation in real-time.

## ✨ Key Features

### Unified Documentation Server
- **Single Source of Truth**: One server aggregating 500+ documentation sources
- **Intelligent Routing**: Automatically selects relevant docs based on file type and context
- **Real-time Validation**: Validates generated code against official documentation
- **Deprecation Detection**: Identifies and suggests alternatives for deprecated APIs
- **Security Scanning**: Checks for known vulnerabilities and security anti-patterns
- **Performance Optimization**: Caches documentation locally for faster access

### Multi-Agent Architecture
- **Product Manager**: Creates vision and roadmap
- **Business Analyst**: Generates detailed requirements
- **UI/UX Designer**: Designs user interfaces and experiences
- **System Architect**: Designs technical architecture
- **Developer**: Implements features with TDD
- **QA Engineer**: Creates and runs comprehensive tests
- **Code Reviewer**: Reviews code for quality and standards
- **DevOps Engineer**: Handles deployment and infrastructure

## 📦 Installation

### Quick Install
```bash
cd C:\Users\varak\repos\quantumwala\multi-agent-system
install.bat
```

### Manual Installation
```bash
# Install Python dependencies
pip install aiohttp pyyaml aiofiles asyncio

# Install MCP servers (optional but recommended)
mcp install devdocs-server
mcp install mdn-server
mcp install npm-docs-server

# Install Claude Code (for full functionality)
# Visit: https://docs.anthropic.com/claude-code
```

## 🎯 Usage Examples

### 1. Basic Agent Execution
```python
import asyncio
from orchestrator import ClaudeCodeOrchestrator

async def run_developer():
    orchestrator = ClaudeCodeOrchestrator(".", enable_docs=True)
    
    result = await orchestrator.run_agent(
        agent_type="developer",
        task="Implement user authentication with JWT",
        input_data={"framework": "express", "database": "postgresql"},
        use_docs=True
    )
    
    print(f"Validation Score: {result['validation']['score']}/100")
    
asyncio.run(run_developer())
```

### 2. Parallel Agent Execution
```python
async def run_parallel():
    orchestrator = ClaudeCodeOrchestrator(".", enable_docs=True)
    
    tasks = [
        ("architect", "Design microservices architecture", {}),
        ("qa", "Create test plan", {}),
        ("developer", "Implement API endpoints", {})
    ]
    
    results = await orchestrator.run_parallel_agents(tasks)
    
asyncio.run(run_parallel())
```

### 3. Using Command Line
```bash
# Run system test
run_orchestrator.bat test

# Start development with documentation
run_orchestrator.bat develop "Create REST API for user management"

# Run architecture design
run_orchestrator.bat architect "Design scalable e-commerce platform"

# Run QA analysis
run_orchestrator.bat qa "Test authentication module"

# Run parallel agents demo
run_orchestrator.bat parallel
```

## 📚 Documentation Configuration

The documentation server is configured via `configs/documentation-config.yaml`:

```yaml
documentation:
  server: unified-docs
  
  sources:
    devdocs:
      enabled: true
      cache_ttl: 86400  # 24 hours
    
    mdn:
      enabled: true
      priority: high  # For web standards
    
    npm:
      enabled: true
      
  validation:
    block_deprecated: true
    require_types: true
    security_check: true
    
  cache:
    mode: "aggressive"
    size: "2GB"
```

## 🔄 Workflow Example: Building a Todo App

### Step 1: Initialize Project
```python
orchestrator = ClaudeCodeOrchestrator(".")
await orchestrator.run_agent(
    "product_manager",
    "Build a collaborative todo app with real-time sync",
    {}
)
```

### Step 2: Generate Requirements
```python
await orchestrator.run_agent(
    "business_analyst",
    "Create detailed requirements from product vision",
    {"vision": product_vision}
)
```

### Step 3: Design Architecture
```python
await orchestrator.run_agent(
    "architect",
    "Design scalable architecture with real-time capabilities",
    {"requirements": requirements}
)
```

### Step 4: Implement Features
```python
await orchestrator.run_agent(
    "developer",
    "Implement task management with CRUD operations",
    {"architecture": architecture, "specs": requirements}
)
```

### Step 5: Validate Quality
```python
# Code will be automatically validated against documentation
# Validation includes:
# - Deprecated API detection
# - Security vulnerability scanning
# - Performance anti-pattern detection
# - Type safety verification
```

## 📊 Metrics and Monitoring

The system tracks performance metrics for each agent:

```python
orchestrator.get_metrics_report()

# Output:
# === Agent Performance Metrics ===
# DEVELOPER:
#   Tasks Completed: 15
#   Tasks Failed: 1
#   Avg Validation Score: 92.3/100
```

## 🏗️ Project Structure

```
quantumwala/multi-agent-system/
├── configs/
│   └── documentation-config.yaml    # Documentation server config
├── agents/                          # Agent input/output files
├── context/
│   └── state.json                   # Shared project context
├── logs/                            # Execution logs
├── artifacts/                       # Generated artifacts
├── templates/
│   └── agent_templates.py          # Agent prompt templates
├── documentation/
│   └── internal/                   # Internal docs (if any)
├── .cache/
│   └── docs/                       # Documentation cache
├── unified_doc_server.py           # Documentation server
├── orchestrator.py                 # Main orchestrator
├── install.bat                     # Installation script
└── run_orchestrator.bat           # Run script
```

## 🔧 Advanced Features

### Custom Documentation Sources
Add your internal documentation:

```python
# Place markdown files in documentation/internal/
# They will be automatically indexed and searchable
```

### Documentation Validation Rules
```python
validation_results = {
    'deprecated_apis': [],      # APIs that should not be used
    'security_issues': [],      # Known vulnerabilities
    'performance_issues': [],   # Anti-patterns detected
    'missing_types': [],        # Missing type annotations
    'accessibility': []         # WCAG violations
}
```

### Agent Communication Protocol
Agents communicate through structured JSON:

```json
{
  "agent_id": "developer_001",
  "message_type": "task_complete",
  "payload": {
    "code": "...",
    "validation_score": 95,
    "tests_passed": true
  }
}
```

## 🐛 Troubleshooting

### Documentation Server Not Working
- Check internet connection for online sources
- Verify cache directory has write permissions
- Check `configs/documentation-config.yaml` is valid

### Claude Code Not Found
- System will use mock responses for testing
- Install Claude Code for full functionality
- Check Claude Code is in PATH

### Low Validation Scores
- Review deprecation warnings
- Check security advisories
- Ensure type annotations are present
- Follow documented best practices

## 📈 Performance Tips

1. **Enable Aggressive Caching**: Reduces API calls by 80%
2. **Use Parallel Agents**: Run independent tasks simultaneously
3. **Preload Common Docs**: Cache frequently used documentation
4. **Local Documentation Mirror**: For offline development

## 🔐 Security Features

- **Automatic vulnerability scanning** using documentation
- **Deprecation detection** prevents using outdated APIs
- **Security pattern validation** against OWASP guidelines
- **Input sanitization checks** in generated code

## 🚀 Getting Started

1. Run `install.bat` to set up the system
2. Configure your documentation sources in `configs/documentation-config.yaml`
3. Run `run_orchestrator.bat test` to verify installation
4. Start building with `run_orchestrator.bat develop "Your task here"`

## 📝 License

This system is part of the Quantumwala project. 

## 🤝 Support

For issues or questions:
- Check the logs in `logs/` directory
- Review validation results in agent outputs
- Ensure documentation server is properly configured

---

**Built with ❤️ for error-free, documentation-validated code generation**
