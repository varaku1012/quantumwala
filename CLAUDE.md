# Claude Code Multi-Agent Development System

This project uses an enhanced multi-agent workflow system with Claude Code to streamline software development.

## 🆕 Recent Enhancements (Phase 1 Complete)

### Steering Context System
The system now includes persistent project context through steering documents:

1. **Initialize project context:**
   ```
   /steering-setup
   ```

2. **Steering documents** in `.claude/steering/`:
   - `product.md` - Vision, users, goals
   - `tech.md` - Technology stack, standards
   - `structure.md` - Conventions, patterns

3. **Context commands:**
   - `/context-for [agent] [task]` - Get relevant context
   - `/context-validate [proposal]` - Check alignment
   - `/steering-update [doc] [changes]` - Update documents

**All agents now automatically load and use steering context!**

## Quick Start

1. **Initialize project context (NEW):**
   ```
   /steering-setup
   ```

2. **Groom a new feature (NEW):**
   ```
   /grooming-workflow "feature-name" "Feature description"
   ```
   
   Or manually:
   ```
   /grooming-start "feature-name"
   /grooming-prioritize "feature-name"
   /grooming-roadmap "feature-name"
   /grooming-complete "feature-name"
   ```

3. **Create a feature spec (after grooming):**
   ```
   /spec-create "feature-name" "Feature description"
   ```

4. **Generate requirements:**
   ```
   /spec-requirements
   ```

5. **Design the feature:**
   ```
   /spec-design
   ```

6. **Generate tasks:**
   ```
   /spec-tasks
   ```

7. **Implement tasks:**
   ```
   /feature-name-task-1
   /feature-name-task-2
   ```

8. **Review implementation:**
   ```
   /spec-review 1
   ```

## Available Agents

### Core Agents
- **product-manager**: Vision, roadmap, and feature prioritization
- **business-analyst**: Requirements and specifications
- **uiux-designer**: Interface design and user experience
- **architect**: System design and technology decisions
- **developer**: Code implementation
- **qa-engineer**: Testing and quality assurance
- **code-reviewer**: Code quality and best practices

### 🆕 Context Management
- **steering-context-manager**: Manages persistent project context

## Project Structure

```
.claude/
├── agents/          # Specialized AI assistants
├── commands/        # Slash commands
├── context/        # 🆕 Context management
├── hooks/          # Automation scripts
├── steering/       # 🆕 Steering documents
├── templates/      # Document templates
├── specs/          # Feature specifications
└── scripts/        # Utility scripts
```

## Enhanced Workflow

1. **Context Setup** (NEW): Steering Context Manager → Create steering docs
2. **Grooming Phase** (NEW): Chief PM + Business Analyst + Architect → Feature analysis
3. **Planning Phase**: Product Manager → Business Analyst (context-aware)
4. **Design Phase**: UI/UX Designer + Architect (follows standards)
5. **Implementation Phase**: Developer (uses conventions)
6. **Quality Phase**: QA Engineer + Code Reviewer (validates compliance)

Each phase now references and aligns with steering documents automatically.

## Tips

- Start with `/steering-setup` to establish project context
- Let Claude Code automatically delegate to appropriate agents
- Use the spec-driven workflow for complex features
- Review the generated tasks before implementation
- Use parallel task execution for independent tasks
- Update steering documents as project evolves

## Customization

- Customize agents by editing files in `.claude/agents/`
- Add new commands in `.claude/commands/`
- Modify templates in `.claude/templates/`
- **Update steering context in `.claude/steering/`**

## Roadmap

✅ **Phase 1**: Steering Context (COMPLETE)
📋 **Phase 2**: Validation & Orchestration (READY)
📅 **Phase 3**: Automation & Dashboard (PLANNED)
🚀 **Phase 4**: TMUX Parallel Execution (FUTURE)

See `IMPLEMENTATION_ROADMAP.md` for details.

## Log Management

IMPORTANT: Keep the root directory clean by using the log management system:

### Creating Logs
```bash
# Session logs
python .claude/scripts/log_manager.py create --type session --title "work-description"

# Reports
python .claude/scripts/log_manager.py create --type report --title "report-name"

# Analysis
python .claude/scripts/log_manager.py create --type analysis --title "analysis-topic"

# Phase documentation
python .claude/scripts/log_manager.py create --type phase --title "phase-number"
```

### Log Organization
All logs are organized in `.claude/logs/`:
- `sessions/` - Daily work sessions
- `reports/` - Test and implementation reports
- `analysis/` - Analysis and comparison documents
- `phases/` - Phase completion documentation
- `archive/` - Old logs (auto-archived after 30 days)

### Commands
- `/log-manage clean` - Move root markdown files to logs
- `/log-manage index` - Create searchable index
- `/log-manage archive` - Archive old logs