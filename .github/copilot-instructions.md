# WidgetSystem - Project Guidelines

## Project Overview

WidgetSystem is a modular, configuration-driven GUI application framework built with PySide6 and Advanced Docking System. The project uses a factory pattern for component creation and JSON-based configuration for all UI elements.

## Architecture

### Project Structure (PEP 420 src-layout)

```
WidgetSystem/
├── src/widgetsystem/          # Main package - all source code here
│   ├── core/                  # Core application logic (main windows)
│   ├── factories/             # Factory classes for UI component creation
│   ├── ui/                    # UI components (visual layer, panels)
│   ├── __init__.py
│   ├── py.typed               # PEP 561 type checking marker
│   └── PySide6QtAds.pyi       # Type stubs for QtAds
├── tests/                     # Test suite
├── examples/                  # Demo applications
├── docs/                      # Documentation files
├── config/                    # JSON configuration files
├── schemas/                   # JSON schema validation files
├── themes/                    # QSS stylesheet files
├── data/                      # Data files (layouts, etc.)
└── pyproject.toml             # Modern Python project configuration
```

**Critical Rule**: All source code MUST be in `src/widgetsystem/`. Never create Python modules in the root directory.

### Key Design Patterns

- **Factory Pattern**: All UI components are created through factory classes
- **Configuration-Driven**: UI definitions stored in JSON files under `config/`
- **Separation of Concerns**:
  - `core/`: Application shell and main windows
  - `factories/`: Component creation logic
  - `ui/`: Visual components and panels

## Code Style

### Python Version & Type Hints

- **Target**: Python 3.10+ (configured in pyproject.toml)
- **Type hints required**: All functions, methods, and class attributes
- **Type checking**: Use MyPy (configured in pyproject.toml)

Example:
```python
from pathlib import Path
from typing import Any

def load_config(path: Path) -> dict[str, Any]:
    """Load configuration from JSON file.
    
    Args:
        path: Path to configuration file
        
    Returns:
        Parsed configuration dictionary
    """
    return json.loads(path.read_text(encoding="utf-8"))
```

### Docstrings

- **Required**: All classes, public methods, and functions
- **Style**: Google docstring format
- **Include**: Description, Args, Returns, Raises (when applicable)

### Import Conventions

**ALWAYS use absolute imports from the package root:**

```python
# ✅ CORRECT - Absolute imports
from widgetsystem.factories.layout_factory import LayoutFactory
from widgetsystem.factories.theme_factory import ThemeFactory
from widgetsystem.ui import ConfigurationPanel
from widgetsystem.ui.visual_layer import ListsViewer

# ❌ WRONG - Never use relative imports
from ..factories.layout_factory import LayoutFactory
from .visual_layer import ListsViewer
```

**Import order** (enforced by ruff/isort):
1. Standard library
2. Third-party (PySide6, PySide6QtAds)
3. First-party (widgetsystem.*)

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `LayoutFactory`, `ConfigurationPanel`)
- **Functions/Methods**: `snake_case` (e.g., `load_config`, `create_widget`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_THEME`, `MAX_ITEMS`)
- **Private members**: Prefix with `_` (e.g., `_internal_state`)

### Factory Classes

All factories follow this pattern:

```python
from pathlib import Path
from typing import Any

class ComponentFactory:
    """Factory for creating component instances from JSON configuration."""
    
    def __init__(self, config_path: Path) -> None:
        """Initialize factory with configuration directory."""
        self.config_path = config_path
        self.config_file = config_path / "component.json"
        self._cache: dict[str, Any] = {}
    
    def load_components(self) -> list[Component]:
        """Load all components from configuration file."""
        # Implementation
```

**Factory naming**: `<Component>Factory` (e.g., `LayoutFactory`, `MenuFactory`)

## Configuration Management

### JSON Configuration Files

- **Location**: `config/` directory
- **Schema validation**: JSON schemas in `schemas/` directory
- **Naming**: lowercase with underscores (e.g., `layouts.json`, `ui_config.json`)

### File Paths in Configuration

**Always use relative paths from workspace root:**

```json
{
  "file": "data/layout.xml",           // ✅ CORRECT
  "stylesheet": "themes/dark.qss"      // ✅ CORRECT
}
```

NOT:
```json
{
  "file": "layout.xml",                // ❌ WRONG - ambiguous
  "file": "D:\\absolute\\path.xml"     // ❌ WRONG - not portable
}
```

## Build and Test

### Installation

```bash
# Development setup (editable install with dev dependencies)
pip install -e ".[dev]"
```

### Running Tests

```bash
# Verification test
python tests/verify_setup.py

# Full system test
python tests/test_full_system.py

# Visual layer test
python tests/test_visual_layer.py

# Run with pytest
pytest tests/
```

### Running Examples

```bash
# Complete demo with visual layer
python examples/complete_demo.py

# Basic demo
python examples/demo.py
```

### Code Quality

**This project enforces STRICT code quality standards:**

#### Quick Start

```bash
# Run ALL quality checks (recommended before commit)
python scripts/check_quality.py

# Auto-fix common issues
python scripts/autofix.py

# Or use pre-commit hooks (runs automatically on git commit)
pre-commit install
pre-commit run --all-files
```

#### Individual Tools

```bash
# Ruff - Fast linting (600+ rules enabled)
ruff check src/              # Check for issues
ruff check --fix src/        # Auto-fix issues
ruff format src/             # Format code

# MyPy - Strict type checking
mypy src/                    # Requires type hints everywhere

# Pylint - Additional quality checks (min score: 9.0/10)
pylint src/widgetsystem/

# Bandit - Security scanning
bandit -r src/ -c pyproject.toml

# Pytest - Tests with coverage (min 80%)
pytest tests/ --cov=src/widgetsystem --cov-report=term-missing
```

#### Quality Rules Summary

**MyPy (Type Checking)**
- `strict = true` - All strict checks enabled
- `disallow_untyped_defs = true` - Type hints required everywhere
- `disallow_any_generics = true` - No bare generics (list → list[str])
- `warn_return_any = true` - Return types must be specific
- No implicit Optional, no untyped calls, no untyped decorators

**Ruff (Linting)**
- `select = ["ALL"]` - ALL 600+ rules enabled
- Google-style docstrings required (D417)
- Line length: 100 characters
- Automatic import sorting
- Key rule categories: F (pyflakes), E/W (pycodestyle), I (isort), N (pep8-naming), D (pydocstyle), UP (pyupgrade), S (bandit), B (bugbear), A (builtins), C4 (comprehensions), RET (return), SIM (simplify), and many more
- See pyproject.toml for ignored rules (mostly Qt-specific patterns)

**Pylint**
- Minimum score: 9.0/10.0
- Good names: i, j, k, ex, _
- Max line length: 100
- Additional checks beyond Ruff

**Pytest + Coverage**
- Minimum coverage: 80%
- Coverage XML reports for CI/CD
- Auto-discovery of tests
- Parallel execution support (pytest-xdist)

**Bandit (Security)**
- Checks for common security issues
- SQL injection, weak crypto, shell injection, etc.
- Tests directory excluded from security checks

All tools are configured in `pyproject.toml` and `mypy.ini`.

## Development Workflow

### Adding New Components

1. **Create factory class** in `src/widgetsystem/factories/`
2. **Add JSON configuration** in `config/`
3. **Create JSON schema** in `schemas/`
4. **Export from `__init__.py`** in appropriate module
5. **Write tests** in `tests/`
6. **Update documentation** in `docs/`

### File Creation Rules

- **Never** create Python files in root directory
- **Always** create modules under `src/widgetsystem/`
- **Always** include `__init__.py` in new packages
- **Always** update `__all__` exports when adding public APIs

### Modifying Imports

When refactoring:
1. Update the source file
2. Update all imports in dependent files
3. Update `__init__.py` exports
4. Run tests to verify
5. Check for circular imports

## Package Structure Rules

### Module Organization

```
src/widgetsystem/
├── __init__.py              # Main package exports
├── core/
│   ├── __init__.py          # Export: MainWindow, etc.
│   ├── main.py
│   └── main_visual.py
├── factories/
│   ├── __init__.py          # Export: all Factory classes
│   ├── layout_factory.py
│   ├── theme_factory.py
│   └── ...
└── ui/
    ├── __init__.py          # Export: UI components
    ├── visual_layer.py
    ├── visual_app.py
    └── config_panel.py
```

### Public API Exports

Each `__init__.py` should explicitly export public APIs:

```python
"""Module description."""

from widgetsystem.module.component import Component

__all__ = [
    "Component",
]
```

## Common Pitfalls to Avoid

1. **❌ Root-level Python files**: Never create `.py` files in project root (except `setup.py` if needed)
2. **❌ Relative imports**: Always use `from widgetsystem.` imports
3. **❌ Missing type hints**: All new code must have type annotations
4. **❌ Hardcoded paths**: Use `Path` objects and relative paths
5. **❌ Direct widget creation**: Use factories for all UI components
6. **❌ Missing docstrings**: All public APIs need documentation
7. **❌ Incorrect import statements after refactoring**: Update imports across all files
8. **❌ Circular imports**: Keep dependencies flowing downward (core → ui → factories)
9. **❌ Untyped generics**: Use `list[str]` not `list`, `dict[str, Any]` not `dict`
10. **❌ Bare `except:`**: Always specify exception types
11. **❌ Ignoring linter warnings**: Address all Ruff and MyPy errors before committing
12. **❌ Low test coverage**: Maintain minimum 80% coverage on all new code

## Dependencies

### Required

- Python 3.10+
- PySide6 >= 6.5.0
- PySide6-QtAds >= 4.0.0

### Development

- mypy >= 1.8.0 (type checking)
- ruff >= 0.2.0 (linting and formatting)
- pylint >= 3.0.0 (additional linting)
- pytest >= 7.4.0 (testing)
- pytest-cov >= 4.1.0 (coverage reporting)
- pytest-xdist >= 3.5.0 (parallel test execution)
- pytest-timeout >= 2.2.0 (test timeouts)
- bandit >= 1.7.0 (security scanning)
- pre-commit >= 3.6.0 (git hooks)
- pyupgrade >= 3.15.0 (syntax modernization)
- sphinx >= 7.2.0 (documentation)

## Additional Resources

- Project structure: See README.md
- Type checking config: See mypy.ini and pyrightconfig.json
- Linting config: See pyproject.toml [tool.ruff] section
- Testing: See tests/README.md (if exists)

## Questions or Updates

When in doubt:
- Check existing factory implementations for patterns
- Review tests for usage examples
- Verify with `mypy` and `ruff` before committing
- Run full test suite to ensure nothing breaks
