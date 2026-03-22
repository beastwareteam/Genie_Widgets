# WidgetSystem Factory System

## Overview

The Factory System is the core pattern in WidgetSystem for creating UI components from JSON configuration. All 10 factories follow a consistent design pattern that enables:

- Configuration-driven UI creation
- Consistent interface across component types
- Lazy loading and caching
- Easy testing through dependency injection

## Factory Pattern

### Base Structure

Every factory follows this structure:

```python
from pathlib import Path
from typing import Any
import json

class SomeFactory:
    """Factory for creating Something components from configuration."""

    def __init__(self, config_path: Path) -> None:
        """Initialize factory.

        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path
        self._config: dict[str, Any] | None = None

    def _load_config(self) -> dict[str, Any]:
        """Load and cache configuration.

        Returns:
            Configuration dictionary
        """
        if self._config is None:
            config_file = self.config_path / "something.json"
            with open(config_file, encoding="utf-8") as f:
                self._config = json.load(f)
        return self._config

    def create_something(self, key: str) -> SomeWidget:
        """Create component from configuration.

        Args:
            key: Configuration key

        Returns:
            Created widget instance
        """
        config = self._load_config()
        item_config = config.get(key, {})
        return SomeWidget(**item_config)
```

---

## All 10 Factories

### 1. LayoutFactory

**Purpose**: Window layouts and dock arrangement

**Config File**: `config/layouts.json`

**Schema**: `schemas/layouts.schema.json`

```python
from widgetsystem.factories import LayoutFactory
from pathlib import Path

factory = LayoutFactory(Path("config"))

# Get layout definition
layout = factory.create_layout("main")

# Save current layout
factory.save_layout(dock_manager, "my_layout")

# List available layouts
layouts = factory.list_layouts()

# Delete a layout
factory.delete_layout("old_layout")
```

**Configuration Example**:
```json
{
  "layouts": {
    "main": {
      "areas": [
        {"id": "left", "type": "dock", "width": 250},
        {"id": "center", "type": "content", "flex": 1},
        {"id": "right", "type": "dock", "width": 300}
      ]
    },
    "minimal": {
      "areas": [
        {"id": "center", "type": "content", "flex": 1}
      ]
    }
  }
}
```

---

### 2. ThemeFactory

**Purpose**: Themes, colors, and stylesheets

**Config File**: `config/themes.json`

**Schema**: `schemas/themes.schema.json`

**QSS Files**: `themes/*.qss`

```python
from widgetsystem.factories import ThemeFactory

factory = ThemeFactory(Path("config"))

# Get theme colors
theme = factory.get_theme("dark")
# Returns: {"background": "#1e1e1e", "foreground": "#ffffff", ...}

# Get QSS stylesheet
stylesheet = factory.get_stylesheet("dark")

# List themes
themes = factory.list_themes()

# Create new theme
factory.create_theme("custom", {
    "background": "#2d2d2d",
    "foreground": "#e0e0e0",
    "accent": "#007acc"
})
```

**Configuration Example**:
```json
{
  "themes": {
    "dark": {
      "name": "Dark Theme",
      "colors": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "accent": "#007acc",
        "border": "#3c3c3c",
        "selection": "#264f78"
      },
      "stylesheet": "dark.qss"
    }
  }
}
```

**ARGB Color Format**:
```json
{
  "transparent_panel": "#80ffffff",
  "semi_transparent": "#c01e1e1e"
}
```
Format: `#AARRGGBB` where AA is alpha (00-FF)

---

### 3. PanelFactory

**Purpose**: Dock panel creation and configuration

**Config File**: `config/panels.json`

**Schema**: `schemas/panels.schema.json`

```python
from widgetsystem.factories import PanelFactory

factory = PanelFactory(Path("config"))

# Create a panel
panel = factory.create_panel("explorer")

# Get panel configuration
config = factory.get_panel_config("explorer")

# List available panels
panels = factory.list_panels()
```

**Configuration Example**:
```json
{
  "panels": {
    "explorer": {
      "title": "Explorer",
      "icon": "folder",
      "closable": true,
      "movable": true,
      "features": ["tree_view", "search"],
      "default_area": "left"
    },
    "properties": {
      "title": "Properties",
      "icon": "settings",
      "closable": true,
      "default_area": "right"
    }
  }
}
```

---

### 4. MenuFactory

**Purpose**: Menu bars, menus, and context menus

**Config File**: `config/menus.json`

**Schema**: `schemas/menus.schema.json`

```python
from widgetsystem.factories import MenuFactory

factory = MenuFactory(Path("config"))

# Create full menu bar
menubar = factory.create_menubar(main_window)

# Create single menu
file_menu = factory.create_menu("file", parent_widget)

# Create context menu
context = factory.create_context_menu("editor_context")
```

**Configuration Example**:
```json
{
  "menubar": {
    "menus": ["file", "edit", "view", "help"]
  },
  "menus": {
    "file": {
      "title": "&File",
      "items": [
        {"action": "new", "text": "&New", "shortcut": "Ctrl+N"},
        {"action": "open", "text": "&Open...", "shortcut": "Ctrl+O"},
        {"type": "separator"},
        {"action": "save", "text": "&Save", "shortcut": "Ctrl+S"},
        {"action": "save_as", "text": "Save &As..."},
        {"type": "separator"},
        {"action": "exit", "text": "E&xit", "shortcut": "Alt+F4"}
      ]
    }
  },
  "context_menus": {
    "editor_context": {
      "items": [
        {"action": "cut", "text": "Cut", "shortcut": "Ctrl+X"},
        {"action": "copy", "text": "Copy", "shortcut": "Ctrl+C"},
        {"action": "paste", "text": "Paste", "shortcut": "Ctrl+V"}
      ]
    }
  }
}
```

---

### 5. TabsFactory

**Purpose**: Tab groups and tab widget configuration

**Config File**: `config/tabs.json`

**Schema**: `schemas/tabs.schema.json`

```python
from widgetsystem.factories import TabsFactory

factory = TabsFactory(Path("config"))

# Create tab group
tabs = factory.create_tab_group("main_tabs")

# Get tab configuration
config = factory.get_tab_config("editor_tabs")
```

**Configuration Example**:
```json
{
  "tab_groups": {
    "main_tabs": {
      "position": "top",
      "movable": true,
      "closable": true,
      "tabs": [
        {"id": "welcome", "title": "Welcome", "icon": "home"},
        {"id": "editor", "title": "Editor", "icon": "code"}
      ]
    }
  }
}
```

---

### 6. DnDFactory

**Purpose**: Drag and drop configuration

**Config File**: `config/dnd.json`

**Schema**: `schemas/dnd.schema.json`

```python
from widgetsystem.factories import DnDFactory

factory = DnDFactory(Path("config"))

# Setup drag & drop on widget
factory.setup_drag_drop(widget)

# Get DnD configuration
config = factory.get_dnd_config()
```

**Configuration Example**:
```json
{
  "drag_drop": {
    "enabled": true,
    "mime_types": ["text/plain", "application/json"],
    "drop_actions": ["copy", "move"],
    "visual_feedback": true
  }
}
```

---

### 7. ResponsiveFactory

**Purpose**: Responsive layout breakpoints

**Config File**: `config/responsive.json`

**Schema**: `schemas/responsive.schema.json`

```python
from widgetsystem.factories import ResponsiveFactory

factory = ResponsiveFactory(Path("config"))

# Apply responsive layout
factory.apply_responsive_layout(widget, width=1200)

# Get breakpoint for width
breakpoint = factory.get_breakpoint(800)
```

**Configuration Example**:
```json
{
  "breakpoints": {
    "small": {"max_width": 600, "columns": 1},
    "medium": {"min_width": 601, "max_width": 1200, "columns": 2},
    "large": {"min_width": 1201, "columns": 3}
  },
  "responsive_rules": {
    "sidebar": {
      "small": {"visible": false},
      "medium": {"visible": true, "width": 200},
      "large": {"visible": true, "width": 300}
    }
  }
}
```

---

### 8. I18nFactory

**Purpose**: Internationalization and localization

**Config Files**: `config/i18n.*.json` (per language)

```python
from widgetsystem.factories import I18nFactory

factory = I18nFactory(Path("config"))

# Set language
factory.set_language("de")

# Translate key
text = factory.translate("menu.file")
# Returns: "Datei" (German)

# Get with fallback
text = factory.translate("unknown.key", fallback="Default Text")

# List available languages
languages = factory.list_languages()
# Returns: ["en", "de"]
```

**Configuration Example** (`i18n.de.json`):
```json
{
  "language": "de",
  "name": "Deutsch",
  "translations": {
    "menu.file": "Datei",
    "menu.edit": "Bearbeiten",
    "menu.view": "Ansicht",
    "button.ok": "OK",
    "button.cancel": "Abbrechen",
    "dialog.save_changes": "Änderungen speichern?"
  }
}
```

---

### 9. ListFactory

**Purpose**: List widgets with nesting support

**Config File**: `config/lists.json`

```python
from widgetsystem.factories import ListFactory

factory = ListFactory(Path("config"))

# Create list widget
list_widget = factory.create_list("file_list")

# Create nested list
nested_list = factory.create_nested_list("project_tree")
```

**Configuration Example**:
```json
{
  "lists": {
    "file_list": {
      "type": "simple",
      "selection_mode": "single",
      "drag_enabled": true
    },
    "project_tree": {
      "type": "tree",
      "expandable": true,
      "icons_enabled": true,
      "levels": 3
    }
  }
}
```

---

### 10. UIConfigFactory

**Purpose**: General UI configuration

**Config File**: `config/ui_config.json`

```python
from widgetsystem.factories import UIConfigFactory

factory = UIConfigFactory(Path("config"))

# Get complete config
config = factory.get_config()

# Get specific setting
font_size = factory.get_setting("editor.font_size", default=12)

# Update setting
factory.set_setting("editor.font_size", 14)
```

**Configuration Example**:
```json
{
  "ui_config": {
    "window": {
      "default_width": 1280,
      "default_height": 720,
      "remember_position": true
    },
    "editor": {
      "font_family": "Consolas",
      "font_size": 12,
      "tab_size": 4,
      "word_wrap": true
    },
    "appearance": {
      "default_theme": "dark",
      "animations_enabled": true,
      "toolbar_style": "icon_only"
    }
  }
}
```

---

## Plugin Registry Integration

Factories can be dynamically registered via the Plugin System:

```python
from widgetsystem.core import PluginRegistry

# Get global registry
registry = PluginRegistry()

# Register all factories
registry.register_factory("LayoutFactory", LayoutFactory)
registry.register_factory("ThemeFactory", ThemeFactory)
registry.register_factory("PanelFactory", PanelFactory)
# ... etc

# Get factory by name
factory_class = registry.get_factory("ThemeFactory")
factory = factory_class(Path("config"))

# List registered factories
names = registry.list_factories()
```

---

## Creating Custom Factories

### Step 1: Define the Factory Class

```python
from pathlib import Path
from typing import Any
import json

class CustomWidgetFactory:
    """Factory for creating CustomWidget instances."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._config: dict[str, Any] | None = None

    def _load_config(self) -> dict[str, Any]:
        if self._config is None:
            with open(self.config_path / "custom_widgets.json") as f:
                self._config = json.load(f)
        return self._config

    def create_widget(self, key: str) -> CustomWidget:
        config = self._load_config()
        widget_config = config.get("widgets", {}).get(key, {})
        return CustomWidget(**widget_config)
```

### Step 2: Create Configuration File

```json
{
  "widgets": {
    "my_widget": {
      "title": "My Custom Widget",
      "width": 400,
      "height": 300,
      "features": ["feature1", "feature2"]
    }
  }
}
```

### Step 3: Create JSON Schema (Optional)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "widgets": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "width": {"type": "integer", "minimum": 0},
          "height": {"type": "integer", "minimum": 0},
          "features": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title"]
      }
    }
  }
}
```

### Step 4: Register with Plugin System

```python
from widgetsystem.core import PluginRegistry

registry = PluginRegistry()
registry.register_factory("CustomWidgetFactory", CustomWidgetFactory)
```

---

## Testing Factories

```python
import pytest
from pathlib import Path
from widgetsystem.factories import ThemeFactory

@pytest.fixture
def factory(tmp_path: Path) -> ThemeFactory:
    """Create factory with test configuration."""
    config_file = tmp_path / "themes.json"
    config_file.write_text('{"themes": {"test": {"name": "Test"}}}')
    return ThemeFactory(tmp_path)

def test_get_theme(factory: ThemeFactory) -> None:
    """Test theme retrieval."""
    theme = factory.get_theme("test")
    assert theme is not None
    assert theme["name"] == "Test"

def test_list_themes(factory: ThemeFactory) -> None:
    """Test theme listing."""
    themes = factory.list_themes()
    assert "test" in themes
```

---

## Best Practices

1. **Always use Path objects** for configuration paths
2. **Cache loaded configuration** to avoid repeated file I/O
3. **Use type hints** on all public methods
4. **Provide default values** for optional configuration
5. **Validate against JSON schemas** where possible
6. **Document public methods** with Google-style docstrings
7. **Handle missing keys gracefully** with sensible defaults
8. **Use dependency injection** for testability
