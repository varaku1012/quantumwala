# Steering Documents Guide

## What Are Steering Documents?

Steering documents provide persistent context about YOUR product to all AI agents in the Claude Code system. They ensure every agent understands your product vision, technical choices, and coding standards without you having to explain them repeatedly.

## The Three Steering Documents

### 1. product.md - Product Vision & Strategy
Defines WHAT you're building and WHY:
- Product vision and goals
- Target users and their needs
- Core features and roadmap
- Success metrics
- Business constraints

### 2. tech.md - Technical Decisions
Defines HOW you're building it:
- Technology stack choices
- Architecture patterns
- Development standards
- Testing requirements
- Performance targets

### 3. structure.md - Code Organization
Defines WHERE things go and naming patterns:
- Directory structure
- File naming conventions
- Code organization patterns
- Git workflow
- Documentation standards

## How to Fill Them Out

1. **Replace all placeholder text** marked with [brackets]
2. **Be specific** - The more detail you provide, the better agents can help
3. **Keep them updated** - As decisions change, update the documents
4. **Use examples** - Show actual patterns from your codebase

## Quick Start Example

If you're building a "Task Management SaaS", your product.md might start with:

```markdown
## Vision Statement
Build the most intuitive task management platform for remote teams, reducing project chaos by 50% through smart automation and clear visualizations.

## Product Name
TaskFlow Pro

## Target Users
- **Primary**: Remote team leads managing 5-20 people across time zones
- **Secondary**: Freelancers juggling multiple client projects
```

## How Agents Use These Documents

When you run any command, agents automatically:
1. Load relevant sections from steering documents
2. Apply your standards to their outputs
3. Make recommendations aligned with your vision
4. Follow your coding conventions

## Benefits

- **No Repetition**: Never explain your tech stack again
- **Consistency**: All agents follow the same standards
- **Efficiency**: 70% less context needed per task
- **Quality**: Outputs match your specifications

## Tips

- Start with product.md to establish vision
- Fill tech.md based on your architecture decisions
- Update structure.md as patterns emerge
- Review quarterly and update as needed

## System vs Product Context

- **This folder** (`.claude/steering/`): Contains YOUR product context
- **System docs** (`.claude/system-docs/`): Contains multi-agent system documentation

---

Ready to start? Edit the three .md files in this folder with your product details!