Create a new software development project with the given description.

Process:
1. Use product-manager agent to create vision and roadmap
2. Initialize project structure with directories:
   - src/ (source code)
   - tests/ (test files)
   - docs/ (documentation)
   - .claude/specs/ (specifications)
3. Create initial documentation:
   - README.md
   - CONTRIBUTING.md
   - docs/ARCHITECTURE.md
4. Set up development workflow

When executing:
- First, ask product-manager to analyze the project description
- Create a project vision document in docs/VISION.md
- Generate initial roadmap in docs/ROADMAP.md
- Initialize git repository if not exists

Usage: /project-init "E-commerce platform with AI recommendations"