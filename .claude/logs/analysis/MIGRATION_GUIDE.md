# Migration Guide - New Multi-Agent System

## What's New
This conversation added a comprehensive multi-agent system to your existing Claude Code setup.

## New Agents Added (7 total)
1. **product-manager.md** - Product vision and roadmap planning
2. **business-analyst.md** - Requirements and specifications (with smart routing)
3. **uiux-designer.md** - Interface design and accessibility
4. **architect.md** - System design and technology decisions
5. **developer.md** - TDD-focused implementation
6. **qa-engineer.md** - Comprehensive testing strategies
7. **code-reviewer.md** - Code quality and security reviews

## New Commands Added
1. **/feature-complete** - Full feature workflow with all agents
2. **/parallel-analysis** - Run multiple agents simultaneously

## New Hooks Added
1. **preserve-agent-context.sh** - Preserves context between agent handoffs

## New Templates Added
1. **design.md** - Comprehensive design document template
2. **requirements.md** - Structured requirements template

## Integration with Existing System
Your existing system appears to have:
- A spec-driven workflow (similar approach)
- Bug tracking system
- Various validation agents

The new agents complement these by:
- Adding more specialized roles (PM, BA, UX, etc.)
- Providing smart agent routing
- Enabling parallel agent execution
- Adding TDD-focused development

## How to Use Together
1. Use existing `/spec-create` to start a feature
2. Use new agents for specialized analysis:
   - `Use product-manager agent for vision`
   - `Use business-analyst agent for requirements`
   - `Use architect agent for system design`
3. Continue with existing workflow or use `/feature-complete`

## Key Differences
- New agents have **handoff recommendations** in their output
- New agents support **parallel execution** (up to 10)
- New agents include **smart routing logic**
- Focus on **agent coordination** through output structure

## Recommendation
Try the new workflow on a test feature first:
```
/project-init "Test feature for new agent system"
```

Then compare with your existing workflow to see which works better for your needs.