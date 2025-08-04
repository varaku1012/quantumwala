---
name: version
version: 1.0.0
created: 2025-08-03
updated: 2025-08-03
changelog:
  - "1.0.0: Initial version management command"
---

# Version Command

Manage component versions across the Claude Code multi-agent system

## Usage
```
/version [action] [options]
```

Actions:
- `scan` - Scan all components and extract version information
- `validate` - Validate component versions and dependencies
- `report` - Generate comprehensive version report
- `list [type]` - List all components or components of specific type
- `export` - Export version data to JSON file

## Examples

### Scan Components
```
/version scan
```
Scans all agents, scripts, commands, and steering documents for version metadata.

### Validate Versions
```
/version validate
```
Checks:
- Version format compliance (semver)
- File integrity
- Dependency satisfaction

### Generate Report
```
/version report
```
Creates detailed markdown report with:
- Component overview table
- Validation status
- Recent changes
- Dependency analysis

### List Components
```
/version list
/version list agent
/version list script
```

### Export Data
```
/version export
```
Exports all version data to JSON file for external tools.

## Version Format

All components should include version metadata:

```yaml
---
name: component-name
version: 1.2.0
created: 2025-01-15
updated: 2025-08-03
changelog:
  - "1.0.0: Initial release"
  - "1.1.0: Added new features"
  - "1.2.0: Performance improvements"
dependencies:
  - python>=3.7
  - other-component>=1.0.0
tags:
  - stable
  - production
---
```

## Version Registry

The system maintains a version registry at:
- `.claude/version-registry.json`

This tracks:
- All component versions
- File integrity hashes
- Dependency relationships
- Change history

## Benefits

1. **Dependency Management**: Track component dependencies
2. **Integrity Checking**: Detect unauthorized changes
3. **Change History**: Maintain comprehensive changelogs
4. **Compliance**: Ensure version format standards
5. **Reporting**: Generate version reports for audits