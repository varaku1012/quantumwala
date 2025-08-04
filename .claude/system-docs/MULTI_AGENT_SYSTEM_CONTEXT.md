# Claude Code Multi-Agent System - System Documentation

This document contains the steering context for the Claude Code Multi-Agent System itself (the infrastructure you're using), NOT for your actual product.

## Product Context (Multi-Agent System)

### Vision Statement
Transform Claude Code into an enterprise-scale multi-agent development platform that enables autonomous, coordinated software development through specialized AI agents working in parallel across multiple sessions and projects.

### Target Users
- **Primary**: Software developers, DevOps engineers, and technical leads using Claude Code for complex projects
- **Secondary**: AI researchers and automation enthusiasts exploring multi-agent coordination
- **Future**: Enterprise development teams requiring scalable AI-assisted development workflows

### Core Features
1. **Steering Context System**: Persistent project knowledge that maintains consistency across all agent interactions and sessions
2. **Specialized Agent Ecosystem**: Domain-specific agents (product-manager, architect, developer, qa-engineer, etc.) with distinct roles and capabilities
3. **Workflow Orchestration**: Automated execution of complex development workflows with quality gates and validation
4. **TMUX Parallel Execution**: True parallel development using multiple Claude Code instances coordinated through TMUX sessions
5. **Intelligent Task Management**: Auto-generated task commands with dependency detection and progress tracking

## Technical Context (Multi-Agent System)

### Technology Stack
- **Foundation**: Claude Code CLI (Anthropic's official command-line interface)
- **Language**: Python for utilities and TMUX orchestration
- **Shell Scripting**: Bash for automation and coordination
- **Session Management**: TMUX for parallel agent execution
- **Operating System**: Cross-platform (Windows, macOS, Linux)

### Agent Architecture
- **Agent Definition**: Markdown files in `.claude/agents/` directory
- **Agent Types**: Specialized roles with distinct expertise areas
- **Context Loading**: Automatic steering document integration
- **Communication**: File-based state management

### Development Standards
- **Python**: Version 3.7+ for cross-platform compatibility
- **Code Style**: PEP 8 compliance for Python scripts
- **Documentation**: Comprehensive inline comments and README files
- **Testing**: Unit tests for critical functions

## Structure Context (Multi-Agent System)

### Directory Organization
```
.claude/
├── agents/              # Specialized AI agents (markdown files)
├── commands/            # Slash commands for Claude Code
├── steering/            # Project steering documents
├── specs/               # Feature specifications
├── scripts/             # Python utilities and automation
├── context/             # Context management utilities
├── hooks/               # Automation hooks
└── templates/           # Document templates
```

### File Naming Conventions
- **Agents**: `{role-name}.md` (kebab-case)
- **Commands**: `{command-name}.md` (kebab-case)
- **Scripts**: `{function_name}.py` (snake_case)
- **Specs**: `{feature-name}/` (kebab-case directories)

### Agent Boundaries
Each agent has clearly defined responsibilities:
- **product-manager**: Vision, features, priorities
- **business-analyst**: Requirements, user stories
- **architect**: Technical design, system architecture
- **developer**: Implementation, coding
- **qa-engineer**: Testing, quality assurance
- **code-reviewer**: Code quality, best practices

---

**Note**: This document describes the multi-agent system infrastructure. Your actual product steering documents should be created in `.claude/steering/` and should describe YOUR product, not this system.