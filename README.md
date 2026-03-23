# Genie Widgets (WidgetSystem)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                           GENIE WIDGETS v1.0.0                                ║
║         Configuration-Driven PySide6 GUI Framework with QtAds                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║   10 Factories  │  14 UI Components  │  6 Core Systems  │  100% Type Hints   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.4+-green.svg)](https://doc.qt.io/qtforpython/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION                                     │
│      VisualApp  ───▶  VisualMainWindow  ───▶  ConfigurationPanel            │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UI COMPONENTS (14)                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │InlayTitleBar │ │ ThemeEditor  │ │ARGBColorPick │ │WidgetEditor  │       │
│  │  3px → 35px  │ │  Live Edit   │ │  #AARRGGBB   │ │  Properties  │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FACTORY SYSTEM (10)                                 │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ Layout │ │ Theme  │ │ Panel  │ │  Menu  │ │  Tabs  │ │  DnD   │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                               │
│  │Respons.│ │  I18n  │ │  List  │ │UIConfig│                               │
│  └────────┘ └────────┘ └────────┘ └────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CORE SYSTEMS (6)                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │PluginSystem │ │  Undo/Redo  │ │  Config I/O │ │  Templates  │           │
│  │ Hot-Reload  │ │  Commands   │ │Import/Export│ │  5 Built-in │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐                                            │
│  │ThemeManager │ │  Gradients  │                                            │
│  │ ARGB Colors │ │  Dynamic    │                                            │
│  └─────────────┘ └─────────────┘                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       JSON CONFIGURATION (11 files)                          │
│  layouts │ themes │ panels │ menus │ tabs │ dnd │ responsive │ i18n │ ...  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Documentation

| Category | Documents |
|----------|-----------|
| **Getting Started** | [Quick Start](docs/QUICK_START.md) · [Setup](docs/SETUP.md) · [Visual Architecture](docs/VISUAL_ARCHITECTURE.md) |
| **Architecture** | [Architecture](docs/ARCHITECTURE.md) · [Factory System](docs/FACTORY_SYSTEM.md) · [Plugin Development](docs/PLUGIN_DEVELOPMENT.md) |
| **Components** | [API Reference](docs/API_REFERENCE.md) · [UI Components](docs/UI_COMPONENTS.md) · [Signals & Events](docs/SIGNALS_EVENTS.md) |
| **Configuration** | [Configuration Guide](docs/CONFIGURATION_GUIDE.md) · [Theme System](docs/THEME_SYSTEM.md) |

---

## Key Features

### Core Systems
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Plugin System  │  │   Undo/Redo     │  │   Config I/O    │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Hot-reload    │  │ • Command       │  │ • ZIP Export    │
│ • Registry      │  │   Pattern       │  │ • Import/Merge  │
│ • Discovery     │  │ • 100 History   │  │ • Auto-Backup   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### UI Capabilities
```
┌─────────────────────────────────────────────────────────────┐
│ InlayTitleBar: Collapsible 3px → 35px titlebar              │
├─────────────────────────────────────────────────────────────┤
│ COLLAPSED (3px)          EXPANDED (35px)                    │
│ ████████████████    │    Title          [−][□][×]           │
│                     │    ─────────────────────────          │
│ (hover to expand)   │    Panel Content                      │
└─────────────────────────────────────────────────────────────┘
```

### ARGB Color Support
```
#AARRGGBB Format:
 ││││││││
 ││││││└┴── Blue  (00-FF)
 ││││└┴──── Green (00-FF)
 ││└┴────── Red   (00-FF)
 └┴──────── Alpha (00-FF)  ← Transparency!

Examples: #FF007ACC (opaque) │ #80007ACC (50% transparent)
```

---

## Quick Start

```bash
# Clone & Install
git clone https://github.com/beastwareteam/Genie_Widgets.git
cd Genie_Widgets
pip install -e ".[dev]"

# Run Demo
python examples/complete_demo.py

# Run Tests
pytest tests/ -v
```

### Basic Usage

```python
from widgetsystem import (
    VisualApp,
    ThemeFactory,
    LayoutFactory,
    ThemeManager,
)
from pathlib import Path

# Create application
app = VisualApp(sys.argv)
window = app.create_main_window()

# Use factories
theme_factory = ThemeFactory(Path("config"))
theme = theme_factory.get_theme("dark")

window.show()
app.run()
```

---

## Project Structure

```
WidgetSystem/
├── src/widgetsystem/          # Source Code (44 modules)
│   ├── core/                  #   Core Systems (9)
│   ├── controllers/           #   Controllers (7)
│   ├── factories/             #   Factory Classes (10)
│   ├── ui/                    #   UI Components (14)
│   └── debug/                 #   Debug Tools (3)
├── config/                    # JSON Configuration (11 files)
├── schemas/                   # JSON Schemas (10 files)
├── themes/                    # QSS Stylesheets (3)
├── tests/                     # Test Suite (56 modules)
├── docs/                      # Documentation (12 files)
└── examples/                  # Demo Applications
```

---

## Configuration Files

| File | Purpose | Schema |
|------|---------|--------|
| `layouts.json` | Window layouts | `layouts.schema.json` |
| `themes.json` | Theme definitions | `themes.schema.json` |
| `panels.json` | Panel definitions | `panels.schema.json` |
| `menus.json` | Menu configurations | `menus.schema.json` |
| `tabs.json` | Tab configurations | `tabs.schema.json` |
| `dnd.json` | Drag & Drop | `dnd.schema.json` |
| `responsive.json` | Breakpoints | `responsive.schema.json` |
| `i18n.*.json` | Translations | `i18n.schema.json` |
| `lists.json` | List widgets | `lists.schema.json` |
| `ui_config.json` | General settings | `ui_config.schema.json` |

---

## Statistics

```
┌────────────────────────────────────────────────────────────┐
│                    PROJECT METRICS                          │
├────────────────────────────────────────────────────────────┤
│  Source Modules     44   ██████████████████████████████    │
│  Test Modules       56   ████████████████████████████████  │
│  UI Components      14   ████████████████████              │
│  Factory Classes    10   ███████                           │
│  Core Systems        6   ████                              │
│  JSON Configs       11   ████████                          │
│  JSON Schemas       10   ███████                           │
├────────────────────────────────────────────────────────────┤
│  Lines of Code    ~13,800                                  │
│  Type Coverage      100%                                   │
│  Python Version    3.10+                                   │
└────────────────────────────────────────────────────────────┘
```

---

## For AI Agents

Before starting work, read:
1. [MASTER_ROADMAP_CHECKLIST.md](MASTER_ROADMAP_CHECKLIST.md) - Source of Truth (Bestand, Roadmap, Regression)
2. [AGENT_CONFIG.md](AGENT_CONFIG.md) - Overview
3. [.github/copilot-instructions.md](.github/copilot-instructions.md) - Guidelines
4. [AGENTS.md](AGENTS.md) - Structure & conventions

---

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please submit a Pull Request.

## Support

- **Issues**: [GitHub Issues](https://github.com/beastwareteam/Genie_Widgets/issues)
- **Docs**: [docs/](docs/)
- **Examples**: [examples/](examples/)
