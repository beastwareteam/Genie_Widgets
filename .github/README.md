# GitHub Copilot Configuration

This directory contains configuration files for GitHub Copilot to understand and follow WidgetSystem project conventions.

## Files

### Workspace Instructions

- **`copilot-instructions.md`** - Main project guidelines that apply to all code in the workspace
  - Project structure and architecture
  - Code style and conventions
  - Import rules and naming
  - Build and test commands
  - Common pitfalls to avoid

### File-Specific Instructions

Located in `instructions/` subdirectory, these apply to specific file patterns:

- **`factories.instructions.md`** - Guidelines for factory classes (`**/factories/**/*.py`)
  - Factory structure and required methods
  - Configuration loading patterns
  - Type hints and error handling
  - Caching strategies

- **`ui-components.instructions.md`** - Guidelines for UI components (`**/ui/**/*.py`, `**/core/**/*.py`)
  - PySide6 widget patterns
  - Signals and slots usage
  - Layout management
  - Factory integration

- **`testing.instructions.md`** - Guidelines for tests (`**/tests/**/*.py`)
  - Test organization and naming
  - Factory testing patterns
  - UI component testing with QApplication
  - Integration testing strategies

- **`json-config.instructions.md`** - Guidelines for JSON files (`**/config/**/*.json`, `**/schemas/**/*.json`)
  - Configuration structure
  - File path conventions
  - Schema validation
  - Formatting standards

## How It Works

GitHub Copilot automatically:
1. Loads `copilot-instructions.md` for all code in the workspace
2. Applies file-specific instructions based on `applyTo` patterns
3. Uses these guidelines to provide context-aware suggestions

## Updating Instructions

When project conventions change:
1. Update the relevant instruction file
2. Commit changes to version control
3. Instructions apply immediately to all team members using Copilot

## Benefits

- **Consistent coding style** across the team
- **Reduced onboarding time** for new developers
- **Automated best practices** enforcement
- **Project-specific suggestions** from Copilot

## Learn More

- [GitHub Copilot Custom Instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Agent Customization](https://code.visualstudio.com/docs/copilot/customization)
