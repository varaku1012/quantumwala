# Structure Steering Document

## Directory Organization

### Project Root Structure
```
project-root/
├── src/                    # Source code
├── tests/                  # Test files
├── docs/                   # Documentation
├── scripts/                # Build and utility scripts
├── config/                 # Configuration files
├── public/                 # Static assets (if applicable)
└── .claude/                # Claude Code agent system
```

### Source Code Organization
```
src/
├── [organize by feature/domain/layer - specify your approach]
├── 
├── 
└── 
```

[Add your specific structure based on your architecture]

## Naming Conventions

### Files
- **Components**: [e.g., PascalCase.jsx, kebab-case.ts]
- **Utilities**: [e.g., camelCase.js, snake_case.py]
- **Tests**: [e.g., *.test.js, *_test.py, *.spec.ts]
- **Styles**: [e.g., *.module.css, *.styled.ts]

### Code Elements
- **Classes**: [e.g., PascalCase]
- **Functions**: [e.g., camelCase, snake_case]
- **Constants**: [e.g., UPPER_SNAKE_CASE]
- **Interfaces/Types**: [e.g., PascalCase with 'I' prefix]

### Database
- **Tables**: [e.g., plural snake_case]
- **Columns**: [e.g., snake_case]
- **Indexes**: [e.g., idx_table_column]
- **Foreign Keys**: [e.g., fk_table_reference]

## Code Organization Patterns

### Module Structure
[Describe how modules/packages should be organized]

### Import Order
1. [Standard library imports]
2. [Third-party imports]
3. [Local application imports]
4. [Relative imports]

### File Length Guidelines
- **Maximum lines**: [e.g., 500 lines]
- **When to split**: [Guidelines for breaking up files]

## Component Patterns

### Frontend Components (if applicable)
```
ComponentName/
├── index.ts              # Public exports
├── ComponentName.tsx     # Main component
├── ComponentName.test.tsx # Tests
├── ComponentName.styles.ts # Styles
└── types.ts             # TypeScript types
```

### API Endpoints (if applicable)
```
/api/v1/resource          # REST pattern
/graphql                  # GraphQL endpoint
/ws                      # WebSocket endpoint
```

## Testing Structure

### Test File Location
- [ ] Colocated with source files
- [ ] Separate test directory
- [ ] Mirror source structure

### Test Naming
- **Unit Tests**: [Pattern]
- **Integration Tests**: [Pattern]
- **E2E Tests**: [Pattern]

## Documentation Standards

### Code Documentation
- **File Headers**: [Required information]
- **Function Documentation**: [Format and requirements]
- **Complex Logic**: [When and how to document]

### README Files
Each major directory should have a README explaining:
- Purpose of the directory
- Key files and their roles
- Any special considerations

## Git Conventions

### Branch Naming
- **Feature**: feature/[ticket-id]-brief-description
- **Bugfix**: bugfix/[ticket-id]-brief-description
- **Hotfix**: hotfix/[ticket-id]-brief-description
- **Release**: release/[version]

### Commit Messages
```
[type]([scope]): [subject]

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

## Configuration Management

### Environment Variables
- **Naming**: [e.g., REACT_APP_*, NODE_ENV]
- **Files**: [.env, .env.local, .env.production]
- **Secrets**: [How to handle sensitive data]

### Configuration Files
- **Format**: [JSON, YAML, TOML, etc.]
- **Location**: [Where configs live]
- **Override Strategy**: [How configs cascade]

## Build and Deployment

### Build Artifacts
- **Location**: [dist/, build/, out/]
- **Naming**: [Version strategy]
- **Cleanup**: [When to clean]

### Deployment Structure
[Describe production file organization]

---
*Last Updated: [Date]*
*Lead Developer: [Name]*