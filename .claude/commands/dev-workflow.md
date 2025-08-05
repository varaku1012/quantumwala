# Developer Workflow Command

**Simple, unified interface powered by chief-product-manager**  
Uses the chief-product-manager agent internally for autonomous workflow execution.

## Usage
```
/dev-workflow "what I want to build"
```

## What it does

🚀 **Delegates to chief-product-manager for autonomous execution**  
📋 **Handles complexity so you focus on building**  
🎯 **Provides developer-friendly interface to proven workflow engine**  
🔄 **Manages the entire development lifecycle automatically**

## Examples

### Build a Feature
```
/dev-workflow "user authentication with 2FA"
```

**What the chief-product-manager does automatically:**
1. ✅ **Strategic Analysis & Planning** - Market research and product vision
2. ✅ **Agent Orchestration & Requirements** - Coordinates specialized agents
3. ✅ **Design & Architecture** - Technical design and system architecture
4. ✅ **Task Generation & Planning** - Breaks down into atomic tasks
5. ✅ **Implementation Orchestration** - Manages parallel execution
6. ✅ **Quality Assurance & Deployment** - Testing and validation

### Build an API
```
/dev-workflow "REST API for product catalog with search and filters"
```

**Chief-product-manager automatically coordinates:**
- 🏗️ **Architect** for API design and technical feasibility
- 👩‍💻 **Developer** for implementation
- 🔌 **API Integration Specialist** for external services
- 🧪 **QA Engineer** for API testing
- 🔒 **Security Engineer** for security validation

### Build a UI Component
```
/dev-workflow "responsive shopping cart component with animations"
```

**Chief-product-manager automatically coordinates:**
- 🎨 **UI/UX Designer** for component design and user experience
- 👩‍💻 **Developer** for implementation
- ⚡ **Performance Optimizer** for animations and optimization
- 🧪 **QA Engineer** for cross-browser testing

## Implementation

```bash
# Powered by chief-product-manager agent internally
python .claude/scripts/unified_dev_workflow.py "description"
```

## Smart Agent Selection

The chief-product-manager automatically chooses and coordinates agents based on your description:

| Keywords | Agents Coordinated by Chief-Product-Manager |
|----------|-------------|
| "API", "REST", "GraphQL" | **Architect** + **API Integration Specialist** + **Developer** |
| "UI", "component", "interface" | **UI/UX Designer** + **Developer** + **QA Engineer** |
| "authentication", "login", "security" | **Security Engineer** + **Developer** + **QA Engineer** |
| "database", "data", "storage" | **Data Engineer** + **Developer** + **QA Engineer** |
| "performance", "optimization" | **Performance Optimizer** + **Developer** + **Architect** |
| "deployment", "infrastructure" | **DevOps Engineer** + **Developer** + **Security Engineer** |

The chief-product-manager handles all coordination, sequencing, and parallel execution automatically.

## Development Modes

### Quick Mode (Default)
```
/dev-workflow "simple contact form"
```
- **Chief-product-manager** executes streamlined workflow
- Focus on essential phases
- Faster completion (~30 minutes)

### Comprehensive Mode
```
/dev-workflow "enterprise user management system" --comprehensive
```
- **Chief-product-manager** executes full strategic workflow
- Complete market analysis and strategic planning
- Extensive documentation and testing
- Security audit and performance optimization (~60 minutes)

### Learning Mode
```
/dev-workflow "my first React component" --learning
```
- **Chief-product-manager** provides educational execution
- Step-by-step explanations throughout phases
- Best practice guidance and detailed rationale
- Extra validation and learning opportunities (~90 minutes)

## Configuration

Developers can customize behavior in `.claude/dev_profiles/`:

```json
{
  "developer_name": "John Developer",
  "preferences": {
    "auto_progression": false,
    "verbose_explanations": true,
    "preferred_agents": ["developer", "qa-engineer"],
    "skip_agents": ["security-engineer"]
  },
  "resource_limits": {
    "max_concurrent": 4,
    "timeout_minutes": 30
  }
}
```

## Progress Tracking

Real-time progress updates:
```
🚀 Starting development workflow...
📋 I'll handle the complexity - you focus on building!

[●●●○○○○○] Phase 1/8: Setting up context...
[●●●●○○○○] Phase 2/8: Creating specification...
[●●●●●○○○] Phase 3/8: Generating requirements...
[●●●●●●○○] Phase 4/8: Designing system...
[●●●●●●●○] Phase 5/8: Creating tasks...
[●●●●●●●●] Phase 6/8: Implementing (3/7 tasks done)...
```

## Error Handling

Developer-friendly error messages:
```
❌ Development workflow failed at Requirements phase

💡 Try these solutions:
   1. Check your description is clear and specific
      Example: Instead of "build app", try "build todo app with user accounts"
   2. Run environment validation
      Command: python .claude/scripts/dev_environment_validator.py
   3. Enable development mode for more details
      Command: /dev-mode on

🔍 Debug Information:
   • Phase: requirements_generation
   • Agent: business-analyst
   • Description: "vague request"
```

## Advanced Usage

### Resume Interrupted Workflow
```
/dev-workflow --resume "user-authentication"
```

### Skip Phases
```
/dev-workflow "payment integration" --skip-design
```

### Use Specific Agents
```
/dev-workflow "optimize database queries" --agents "performance-optimizer,data-engineer"
```

### Dry Run (See What Would Happen)
```
/dev-workflow "new feature" --dry-run
```

## Integration with Development Tools

### VS Code
Add to your tasks.json:
```json
{
  "label": "Dev Workflow",
  "type": "shell",
  "command": "/dev-workflow",
  "args": ["${input:featureDescription}"],
  "group": "build"
}
```

### Terminal Alias
```bash
# Add to your .bashrc or .zshrc
alias dw='/dev-workflow'

# Usage
dw "user profile page"
```

## Benefits

### For New Developers
- **No learning curve**: Just describe what you want to build
- **Best practices**: Automatically follows team standards
- **Complete workflow**: Handles everything from design to testing
- **Educational**: Learn by seeing how experts would build it

### For Experienced Developers  
- **Speed**: Skip manual agent selection and command sequences
- **Consistency**: Same high-quality process every time
- **Flexibility**: Override defaults when needed
- **Integration**: Works with existing development tools

### For Teams
- **Standardization**: Everyone uses the same proven workflow
- **Quality**: Built-in quality gates and validation
- **Documentation**: Automatic documentation generation
- **Knowledge sharing**: Capture and reuse team expertise

## Getting Started

1. **Validate your environment**:
   ```
   python .claude/scripts/dev_environment_validator.py
   ```

2. **Enable development mode**:
   ```
   /dev-mode on
   ```

3. **Try your first workflow**:
   ```
   /dev-workflow "simple calculator app"
   ```

4. **Check the results**:
   ```
   ls -la .claude/specs/simple-calculator-app/
   ```

## Next Steps

Once comfortable with basic usage:
- Explore agent-specific commands for fine control
- Customize your developer profile
- Use parallel execution for complex features
- Integrate with your IDE and development tools