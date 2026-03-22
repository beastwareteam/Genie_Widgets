# Genie Widgets (WidgetSystem)

A comprehensive, modular GUI application framework built with PySide6 and Advanced Docking System (QtAds). Fully configuration-driven with extensive theming, plugin support, and professional-grade architecture.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.4+-green.svg)](https://doc.qt.io/qtforpython/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

## Documentation

| Document | Description |
|----------|-------------|
| **[Quick Start](docs/QUICK_START.md)** | Get started in minutes |
| **[Architecture](docs/ARCHITECTURE.md)** | System design and patterns |
| **[API Reference](docs/API_REFERENCE.md)** | Complete API documentation |
| **[Factory System](docs/FACTORY_SYSTEM.md)** | Factory pattern and all 10 factories |
| **[Theme System](docs/THEME_SYSTEM.md)** | Themes, ARGB colors, gradients |
| **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)** | JSON configuration reference |
| **[UI Components](docs/UI_COMPONENTS.md)** | All UI components |
| **[Plugin Development](docs/PLUGIN_DEVELOPMENT.md)** | Creating custom plugins |
| **[Signals & Events](docs/SIGNALS_EVENTS.md)** | Qt signals reference |

## For AI Agents

**Before starting work, read these files:**
1. **[AGENT_CONFIG.md](AGENT_CONFIG.md)** - Overview for all AI agents
2. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Complete guidelines
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference (German)

See also: **[AGENTS.md](AGENTS.md)** for detailed project structure and conventions.

## Key Features

### Core Systems
- **10 Factory Classes**: Layout, Theme, Panel, Menu, Tabs, DnD, Responsive, I18n, List, UIConfig
- **Plugin System**: Dynamic factory registration with hot-reload
- **Undo/Redo**: Command pattern for reversible operations
- **Import/Export**: Configuration backup and restore
- **Template System**: Pre-built configuration templates

### UI Capabilities
- **Advanced Docking**: Full QtAds integration with floating windows
- **InlayTitleBar**: Collapsible 3px→35px titlebars
- **ARGB Color Support**: Full alpha channel (#AARRGGBB format)
- **Live Theme Editor**: Real-time theme customization
- **Gradient System**: Dynamic gradient rendering

### Quality
- **100% Type Coverage**: Full type hints with mypy strict mode
- **Comprehensive Tests**: 49 test modules
- **JSON Schema Validation**: All configuration validated
- **Signal-based Architecture**: Loose coupling via Qt signals

## Project Structure

```
WidgetSystem/
├── .github/
│   ├── copilot-instructions.md    # GitHub Copilot configuration
│   └── instructions/              # File-specific guidelines
├── src/
│   └── widgetsystem/          # Main package
│       ├── core/              # Core application logic
│       ├── factories/         # Factory classes for UI components
│       ├── ui/                # UI components and visual layer
│       └── py.typed           # PEP 561 marker for type checking
├── tests/                     # Test suite
├── examples/                  # Demo applications
├── docs/                      # Documentation
├── config/                    # Configuration files (.json)
├── schemas/                   # JSON schemas for validation
├── themes/                    # Theme stylesheets (.qss)
├── data/                      # Data files
└── pyproject.toml             # Project configuration
```

## Installation

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd WidgetSystem
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

3. Install the package in editable mode with dev dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Running Examples

```bash
# Run the complete demo
python examples/complete_demo.py

# Run the basic demo
python examples/demo.py
```

### Import Package

```python
from widgetsystem.factories import LayoutFactory, ThemeFactory
from widgetsystem.ui import VisualApp
```

## Development

### Quick Start

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all quality checks (recommended before commit)
python scripts/check_quality.py

# Auto-fix common issues
python scripts/autofix.py

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Running Tests

```bash
# All tests with coverage
pytest tests/ --cov=src/widgetsystem

# Specific test
pytest tests/verify_setup.py -v
```

### Code Quality Tools

This project enforces strict quality standards with:
- **Ruff** (600+ linting rules enabled)
- **MyPy** (strict type checking)
- **Pylint** (min score 9.0/10)
- **Bandit** (security scanning)
- **Pytest** (80% coverage required)

See [`scripts/README.md`](scripts/README.md) for detailed tool usage.

### GitHub Copilot Configuration

This project includes comprehensive GitHub Copilot instructions to maintain code quality and consistency:

- **Workspace Instructions** (`.github/copilot-instructions.md`): Project-wide standards that apply everywhere
- **File-Specific Instructions** (`.github/instructions/`): Context-aware guidelines for:
  - Factory classes (`factories.instructions.md`)
  - UI components (`ui-components.instructions.md`)
  - Tests (`testing.instructions.md`)
  - JSON configuration (`json-config.instructions.md`)

These instructions help Copilot provide suggestions that follow project conventions automatically. See [`.github/README.md`](.github/README.md) for details.

## Configuration

The application uses JSON configuration files located in the `config/` directory:

| File | Purpose | Schema |
|------|---------|--------|
| `layouts.json` | Window layouts | `layouts.schema.json` |
| `themes.json` | Theme definitions | `themes.schema.json` |
| `menus.json` | Menu configurations | `menus.schema.json` |
| `panels.json` | Panel definitions | `panels.schema.json` |
| `tabs.json` | Tab configurations | `tabs.schema.json` |
| `dnd.json` | Drag & Drop settings | `dnd.schema.json` |
| `responsive.json` | Responsive breakpoints | `responsive.schema.json` |
| `i18n.*.json` | Internationalization | - |
| `ui_config.json` | General UI settings | - |

See [Configuration Guide](docs/CONFIGURATION_GUIDE.md) for detailed documentation.

## Project Statistics

| Metric | Value |
|--------|-------|
| Source Files | 41 Python modules |
| Lines of Code | ~13,800 LOC |
| Test Files | 49 test modules |
| Factories | 10 factory classes |
| UI Components | 20+ modules |
| Type Coverage | 100% |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- **Issues**: [GitHub Issues](https://github.com/beastwareteam/Genie_Widgets/issues)
- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)

