# CLAUDE.md - Project Guidelines for AI Assistants

## Git Workflow

This project uses **Git Flow** with a 2-person team:

- `main` - Production-ready code (protected, PR only)
- `develop` - Integration branch (protected, PR only)
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Rules for Claude

1. **Never commit directly to `main` or `develop`**
2. **Always create feature branches** from `develop`
3. **Use conventional commits**: `type(scope): description`
4. **Suggest syncing with develop** before creating PRs

### Commit Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code restructuring
- `test` - Tests
- `chore` - Maintenance

## Project Structure

```
src/widgetsystem/
├── controllers/    # Business logic, event handling
├── core/           # Core classes, themes, profiles
├── factories/      # Widget creation
└── ui/             # UI components
```

## Testing

```bash
python -m pytest tests/
```

## Team

- 2 developers working in parallel
- All PRs require 1 approval
- Squash merge preferred
