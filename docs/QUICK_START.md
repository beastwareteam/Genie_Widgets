# WidgetSystem Quick Start Guide

Get up and running with WidgetSystem in minutes.

---

## Prerequisites

- **Python**: 3.10 or higher
- **PySide6**: 6.4 or higher
- **PySide6-QtAds**: Advanced Docking System

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/beastwareteam/Genie_Widgets.git
cd Genie_Widgets
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install package with dev dependencies
pip install -e ".[dev]"

# Or just runtime dependencies
pip install -e .
```

### 4. Verify Installation

```bash
# Run tests
pytest tests/ -v

# Run quality checks
python scripts/check_quality.py
```

---

## Your First Application

### Minimal Example

```python
"""Minimal WidgetSystem application."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QLabel

from widgetsystem.ui import VisualApp


def main() -> int:
    # Create application
    app = VisualApp(sys.argv)

    # Create main window
    window = app.create_main_window()

    # Add a simple panel
    content = QLabel("Hello, WidgetSystem!")
    content.setAlignment(Qt.AlignCenter)
    window.setCentralWidget(content)

    # Show and run
    window.show()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
```

### With Docking

```python
"""Application with dock panels."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QLabel, QTreeView, QTextEdit

from widgetsystem.ui import VisualApp, VisualMainWindow


def main() -> int:
    app = VisualApp(sys.argv)
    window = app.create_main_window()

    # Create panels
    explorer = QTreeView()
    explorer.setHeaderHidden(True)

    properties = QLabel("Properties Panel")
    properties.setAlignment(Qt.AlignCenter)

    editor = QTextEdit()
    editor.setPlaceholderText("Edit your content here...")

    # Add dock widgets
    window.add_dock_widget("explorer", explorer, "left")
    window.add_dock_widget("properties", properties, "right")
    window.add_dock_widget("editor", editor, "center")

    window.show()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
```

---

## Using Factories

### Load Theme

```python
from pathlib import Path
from widgetsystem.factories import ThemeFactory

# Create factory
factory = ThemeFactory(Path("config"))

# Get theme colors
theme = factory.get_theme("dark")
print(f"Background: {theme['colors']['background']}")

# Apply stylesheet
stylesheet = factory.get_stylesheet("dark")
widget.setStyleSheet(stylesheet)
```

### Create Panels from Config

```python
from widgetsystem.factories import PanelFactory

factory = PanelFactory(Path("config"))

# Create panel from configuration
explorer_panel = factory.create_panel("explorer")
properties_panel = factory.create_panel("properties")

# Add to window
window.add_dock_widget("explorer", explorer_panel, "left")
window.add_dock_widget("properties", properties_panel, "right")
```

### Setup Menus

```python
from widgetsystem.factories import MenuFactory

factory = MenuFactory(Path("config"))

# Create full menu bar
menubar = factory.create_menubar(window)
window.setMenuBar(menubar)

# Create context menu
context_menu = factory.create_context_menu("editor")
```

---

## Theme System

### Switch Themes

```python
from widgetsystem.core import ThemeManager

manager = ThemeManager()

# Set theme
manager.set_theme("dark")

# Get current theme
current = manager.current_theme
print(f"Current: {current.name}")

# React to changes
manager.themeChanged.connect(on_theme_changed)
```

### Use ARGB Colors

```python
from PySide6.QtGui import QColor

# Parse ARGB string
color_str = "#c0007acc"  # 75% opacity blue
alpha = int(color_str[1:3], 16)  # 192
r = int(color_str[3:5], 16)      # 0
g = int(color_str[5:7], 16)      # 122
b = int(color_str[7:9], 16)      # 204

color = QColor(r, g, b, alpha)
```

---

## Undo/Redo System

### Track Changes

```python
from widgetsystem.core import ConfigurationUndoManager

manager = ConfigurationUndoManager()

# Track a change
config = {"theme": "light"}
manager.track_config_change(config, "theme", "dark")

# Now config["theme"] == "dark"

# Undo
manager.undo()
# Now config["theme"] == "light"

# Redo
manager.redo()
# Now config["theme"] == "dark"
```

### Connect to UI

```python
# Enable/disable buttons
manager.undoAvailable.connect(undo_action.setEnabled)
manager.redoAvailable.connect(redo_action.setEnabled)

# Keyboard shortcuts
undo_action.triggered.connect(manager.undo)
redo_action.triggered.connect(manager.redo)
```

---

## Plugin System

### Register Custom Factory

```python
from widgetsystem.core import PluginRegistry
from my_plugin import CustomWidgetFactory

registry = PluginRegistry()
registry.register_factory("CustomWidgetFactory", CustomWidgetFactory)

# Use it
factory_class = registry.get_factory("CustomWidgetFactory")
factory = factory_class(Path("config"))
widget = factory.create_widget("my_widget")
```

### Load Plugins

```python
from widgetsystem.core import PluginManager

manager = PluginManager([Path("plugins")])
loaded = manager.load_all_plugins()
print(f"Loaded: {loaded}")
```

---

## Configuration

### Create Configuration Files

**config/themes.json:**
```json
{
  "themes": {
    "dark": {
      "name": "Dark Theme",
      "colors": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "accent": "#007acc"
      }
    }
  }
}
```

**config/panels.json:**
```json
{
  "panels": {
    "explorer": {
      "title": "Explorer",
      "default_area": "left",
      "closable": true
    }
  }
}
```

### Validate with Schemas

```python
import json
import jsonschema
from pathlib import Path

config = json.loads(Path("config/panels.json").read_text())
schema = json.loads(Path("schemas/panels.schema.json").read_text())

jsonschema.validate(config, schema)  # Raises on error
```

---

## Import/Export

### Export Configuration

```python
from widgetsystem.core import ConfigurationExporter, ExportOptions
from pathlib import Path

exporter = ConfigurationExporter(Path("config"))
options = ExportOptions(
    include_themes=True,
    include_layouts=True,
    include_panels=True
)

exporter.export_to_archive(Path("backup.zip"), options)
```

### Import Configuration

```python
from widgetsystem.core import ConfigurationImporter, ImportOptions

importer = ConfigurationImporter(Path("config"))
options = ImportOptions(
    merge_mode="replace",
    backup_existing=True
)

importer.import_from_archive(Path("backup.zip"), options)
```

---

## Templates

### Apply Built-in Template

```python
from widgetsystem.core import TemplateManager

manager = TemplateManager()

# List available templates
templates = manager.list_templates()
for t in templates:
    print(f"{t.id}: {t.name}")

# Apply with overrides
config = manager.apply_template(
    "builtin_dark_theme",
    {"accent_color": "#ff5722"}
)
```

---

## Running the Application

### Development Mode

```bash
# Run main application
python -m widgetsystem.core.main

# Run visual app
python -m widgetsystem.ui.visual_app

# Run example
python examples/complete_demo.py
```

### Quality Checks

```bash
# Run all checks
python scripts/check_quality.py

# Auto-fix issues
python scripts/autofix.py

# Run tests
pytest tests/ -v --cov=src/widgetsystem
```

---

## Project Structure

```
WidgetSystem/
├── src/widgetsystem/        # Main package
│   ├── core/                # Core systems
│   ├── factories/           # Factory classes
│   └── ui/                  # UI components
├── config/                  # JSON configuration
├── schemas/                 # JSON schemas
├── themes/                  # QSS stylesheets
├── tests/                   # Test suite
├── examples/                # Example applications
└── docs/                    # Documentation
```

---

## Next Steps

1. **[Architecture](ARCHITECTURE.md)** - Understand system design
2. **[API Reference](API_REFERENCE.md)** - Full API documentation
3. **[Factory System](FACTORY_SYSTEM.md)** - Learn factory pattern
4. **[Theme System](THEME_SYSTEM.md)** - Customize appearance
5. **[Plugin Development](PLUGIN_DEVELOPMENT.md)** - Extend the system
6. **[Configuration Guide](CONFIGURATION_GUIDE.md)** - JSON configuration

---

## Getting Help

- **Issues**: https://github.com/beastwareteam/Genie_Widgets/issues
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory

---

## Common Issues

### Import Errors

```bash
# Ensure package is installed
pip install -e .

# Check Python path
python -c "import widgetsystem; print(widgetsystem.__file__)"
```

### Qt Platform Plugin Missing

```bash
# Windows
set QT_QPA_PLATFORM_PLUGIN_PATH=%VIRTUAL_ENV%\Lib\site-packages\PySide6\plugins\platforms

# Linux
export QT_QPA_PLATFORM_PLUGIN_PATH=$VIRTUAL_ENV/lib/python3.x/site-packages/PySide6/plugins/platforms
```

### Theme Not Applying

```python
# Ensure stylesheet is loaded
factory = ThemeFactory(Path("config"))
stylesheet = factory.get_stylesheet("dark")
if not stylesheet:
    print("No stylesheet loaded!")
```
