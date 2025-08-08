# user-auth-test

Quick reference for the user-auth-test specification.

**Stage**: scope  
**Description**: User authentication system with JWT, MFA, password reset, and session management  
**Created**: 2025-08-07

## Files
- `overview.md` - Feature overview and success criteria
- `_meta.json` - Specification metadata and tracking
- `requirements.md` - Detailed requirements (created when moved to scope)
- `design.md` - Technical design (created during design phase)
- `tasks.md` - Implementation tasks (created during task breakdown)

## Quick Commands
```bash
# View status
python .claude/scripts/spec_manager.py status

# Promote to next stage
python .claude/scripts/spec_manager.py promote user-auth-test --to=scope

# Update metadata
# Edit _meta.json directly or use promotion commands
```
