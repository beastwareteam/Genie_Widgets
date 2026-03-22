# WidgetSystem Plugin Development Guide

## Overview

The WidgetSystem Plugin System enables runtime extensibility through:

- Dynamic factory registration
- Plugin discovery and loading
- Hot-reload capability
- Event-based notifications

## Architecture

```
┌─────────────────────────────────────────┐
│            PluginManager                │
│  - Discovery                            │
│  - Loading/Unloading                    │
│  - Hot Reload                           │
├─────────────────────────────────────────┤
│            PluginRegistry               │
│  - Factory Registration                 │
│  - Factory Lookup                       │
│  - Signal Notifications                 │
├─────────────────────────────────────────┤
│              Plugins                    │
│  - Custom Factories                     │
│  - Custom Components                    │
│  - Configuration Extensions             │
└─────────────────────────────────────────┘
```

---

## PluginRegistry

Central registry for factory management.

### Basic Usage

```python
from widgetsystem.core import PluginRegistry

# Create or get global registry
registry = PluginRegistry()

# Register a factory
registry.register_factory("MyFactory", MyFactoryClass)

# Get a factory
factory_class = registry.get_factory("MyFactory")

# List all factories
names = registry.list_factories()

# Unregister
registry.unregister_factory("MyFactory")

# Clear all
registry.clear()
```

### Signals

```python
from PySide6.QtCore import QObject

# Connect to registry signals
registry.factoryRegistered.connect(on_factory_registered)
registry.pluginLoaded.connect(on_plugin_loaded)
registry.pluginUnloaded.connect(on_plugin_unloaded)
registry.errorOccurred.connect(on_error)

def on_factory_registered(name: str) -> None:
    print(f"Factory registered: {name}")

def on_plugin_loaded(name: str) -> None:
    print(f"Plugin loaded: {name}")
```

---

## PluginManager

Handles plugin discovery and lifecycle.

### Setup

```python
from widgetsystem.core import PluginManager
from pathlib import Path

# Initialize with plugin directories
manager = PluginManager([
    Path("plugins"),
    Path("~/.widgetsystem/plugins").expanduser()
])
```

### Loading Plugins

```python
# Load all discovered plugins
loaded = manager.load_all_plugins()
print(f"Loaded plugins: {loaded}")

# Load single plugin
success = manager.load_plugin(Path("plugins/my_plugin.py"))

# Unload plugin
manager.unload_plugin("my_plugin")
```

### Hot Reload

```python
# Reload a plugin (preserves state where possible)
success = manager.reload_plugin("my_plugin")
```

### Plugin Information

```python
# Get plugin metadata
info = manager.get_plugin_info("my_plugin")
# Returns: {
#     "name": "my_plugin",
#     "version": "1.0.0",
#     "author": "Developer",
#     "description": "My plugin description",
#     "factories": ["MyFactory", "AnotherFactory"]
# }

# List all plugins
plugins = manager.list_plugins()
```

---

## Creating a Plugin

### Plugin Structure

```
plugins/
└── my_plugin/
    ├── __init__.py       # Plugin entry point
    ├── plugin.json       # Plugin metadata
    ├── factory.py        # Custom factory
    ├── widgets.py        # Custom widgets
    └── config/           # Plugin configuration
        └── settings.json
```

### Plugin Metadata (plugin.json)

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Description of what this plugin does",
  "dependencies": [],
  "min_widgetsystem_version": "1.0.0",
  "factories": [
    "MyCustomFactory"
  ],
  "entry_point": "__init__.py"
}
```

### Plugin Entry Point (__init__.py)

```python
"""My Plugin - Custom functionality for WidgetSystem."""

from pathlib import Path
from widgetsystem.core import PluginRegistry

from .factory import MyCustomFactory

# Plugin metadata (can also be in plugin.json)
PLUGIN_NAME = "my_plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "Your Name"
PLUGIN_DESCRIPTION = "Custom functionality for WidgetSystem"


def register(registry: PluginRegistry) -> None:
    """Register plugin factories.

    This function is called when the plugin is loaded.

    Args:
        registry: The global plugin registry
    """
    registry.register_factory("MyCustomFactory", MyCustomFactory)


def unregister(registry: PluginRegistry) -> None:
    """Unregister plugin factories.

    This function is called when the plugin is unloaded.

    Args:
        registry: The global plugin registry
    """
    registry.unregister_factory("MyCustomFactory")


def on_load() -> None:
    """Called after plugin is loaded (optional)."""
    print(f"{PLUGIN_NAME} v{PLUGIN_VERSION} loaded")


def on_unload() -> None:
    """Called before plugin is unloaded (optional)."""
    print(f"{PLUGIN_NAME} unloading...")
```

### Custom Factory Implementation

```python
"""Custom factory for My Plugin."""

from pathlib import Path
from typing import Any
import json

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class MyCustomWidget(QWidget):
    """Custom widget created by the factory."""

    def __init__(
        self,
        title: str = "Default",
        color: str = "#ffffff",
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("MyCustomWidget")

        layout = QVBoxLayout(self)
        self.label = QLabel(title)
        self.label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.label)


class MyCustomFactory:
    """Factory for creating MyCustomWidget instances."""

    def __init__(self, config_path: Path) -> None:
        """Initialize factory.

        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path
        self._config: dict[str, Any] | None = None

    def _load_config(self) -> dict[str, Any]:
        """Load and cache configuration."""
        if self._config is None:
            config_file = self.config_path / "my_widgets.json"
            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    self._config = json.load(f)
            else:
                self._config = {"widgets": {}}
        return self._config

    def create_widget(self, name: str) -> MyCustomWidget:
        """Create a widget by name.

        Args:
            name: Widget configuration name

        Returns:
            Configured widget instance
        """
        config = self._load_config()
        widget_config = config.get("widgets", {}).get(name, {})

        return MyCustomWidget(
            title=widget_config.get("title", name),
            color=widget_config.get("color", "#ffffff")
        )

    def list_widgets(self) -> list[str]:
        """List available widget configurations.

        Returns:
            List of widget names
        """
        config = self._load_config()
        return list(config.get("widgets", {}).keys())
```

---

## Plugin Configuration

### Configuration File

Create `config/my_widgets.json`:

```json
{
  "widgets": {
    "info_panel": {
      "title": "Information Panel",
      "color": "#00ff00"
    },
    "status_display": {
      "title": "Status",
      "color": "#ffff00"
    }
  }
}
```

### Schema Validation (Optional)

Create `schemas/my_widgets.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "my_widgets.schema.json",
  "title": "My Widgets Configuration",
  "type": "object",
  "properties": {
    "widgets": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Widget title"
          },
          "color": {
            "type": "string",
            "pattern": "^#[0-9a-fA-F]{6}$",
            "description": "Text color in hex format"
          }
        },
        "required": ["title"]
      }
    }
  },
  "required": ["widgets"]
}
```

---

## Using the Plugin

### Loading

```python
from widgetsystem.core import PluginManager, PluginRegistry
from pathlib import Path

# Setup plugin manager
manager = PluginManager([Path("plugins")])
manager.load_all_plugins()

# Access the factory
registry = PluginRegistry()
MyCustomFactory = registry.get_factory("MyCustomFactory")

# Use the factory
factory = MyCustomFactory(Path("config"))
widget = factory.create_widget("info_panel")
```

### Integration with Main Application

```python
from widgetsystem.ui import VisualApp
from widgetsystem.core import PluginManager
from pathlib import Path

class MyApplication(VisualApp):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self._init_plugins()

    def _init_plugins(self) -> None:
        """Initialize plugin system."""
        self.plugin_manager = PluginManager([
            Path("plugins"),
            Path("~/.widgetsystem/plugins").expanduser()
        ])
        self.plugin_manager.load_all_plugins()
```

---

## Advanced Topics

### Event Hooks

```python
def register(registry: PluginRegistry) -> None:
    """Register with event hooks."""
    registry.register_factory("MyFactory", MyFactory)

    # Connect to application events
    from widgetsystem.ui import VisualApp
    app = VisualApp.instance()
    if app:
        app.themeChanged.connect(on_theme_changed)
        app.windowCreated.connect(on_window_created)


def on_theme_changed(theme_name: str) -> None:
    """Handle theme change."""
    print(f"Theme changed to: {theme_name}")


def on_window_created(window: QWidget) -> None:
    """Handle new window creation."""
    # Add custom UI elements
    pass
```

### State Persistence

```python
import json
from pathlib import Path

class StatefulPlugin:
    """Plugin with persistent state."""

    STATE_FILE = Path("~/.widgetsystem/plugins/my_plugin_state.json").expanduser()

    @classmethod
    def save_state(cls, state: dict) -> None:
        """Save plugin state to disk."""
        cls.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(cls.STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load_state(cls) -> dict:
        """Load plugin state from disk."""
        if cls.STATE_FILE.exists():
            with open(cls.STATE_FILE) as f:
                return json.load(f)
        return {}


def on_unload() -> None:
    """Save state before unload."""
    StatefulPlugin.save_state({"last_unload": "2026-03-22"})
```

### Dependencies

```python
# plugin.json
{
  "name": "my_plugin",
  "dependencies": [
    "base_plugin>=1.0.0",
    "utils_plugin"
  ]
}
```

```python
# __init__.py
def check_dependencies() -> bool:
    """Check if dependencies are satisfied."""
    from widgetsystem.core import PluginRegistry
    registry = PluginRegistry()

    required = ["base_plugin", "utils_plugin"]
    for dep in required:
        if not registry.get_factory(f"{dep}Factory"):
            return False
    return True


def register(registry: PluginRegistry) -> None:
    if not check_dependencies():
        raise RuntimeError("Missing required dependencies")

    registry.register_factory("MyFactory", MyFactory)
```

---

## Testing Plugins

```python
import pytest
from pathlib import Path
from widgetsystem.core import PluginRegistry

from my_plugin import register, unregister
from my_plugin.factory import MyCustomFactory


@pytest.fixture
def registry() -> PluginRegistry:
    """Create clean registry for testing."""
    reg = PluginRegistry()
    reg.clear()
    return reg


@pytest.fixture
def factory(tmp_path: Path) -> MyCustomFactory:
    """Create factory with test config."""
    config = tmp_path / "my_widgets.json"
    config.write_text('{"widgets": {"test": {"title": "Test Widget"}}}')
    return MyCustomFactory(tmp_path)


def test_plugin_registration(registry: PluginRegistry) -> None:
    """Test plugin registers factory."""
    register(registry)
    assert registry.get_factory("MyCustomFactory") is not None


def test_plugin_unregistration(registry: PluginRegistry) -> None:
    """Test plugin unregisters cleanly."""
    register(registry)
    unregister(registry)
    assert registry.get_factory("MyCustomFactory") is None


def test_factory_creates_widget(factory: MyCustomFactory) -> None:
    """Test factory creates widgets."""
    widget = factory.create_widget("test")
    assert widget is not None
    assert widget.label.text() == "Test Widget"
```

---

## Best Practices

1. **Unique Names**: Use unique, descriptive factory names to avoid conflicts
2. **Clean Unregister**: Always implement `unregister()` to clean up properly
3. **Error Handling**: Handle missing config gracefully with defaults
4. **Type Hints**: Use type hints on all public APIs
5. **Documentation**: Document factory methods with docstrings
6. **Testing**: Include tests for all plugin functionality
7. **Versioning**: Use semantic versioning in plugin.json
8. **Dependencies**: Declare dependencies explicitly
9. **Signals**: Use Qt signals for communication, not global state
10. **Configuration**: Support runtime configuration changes where possible

---

## Troubleshooting

### Plugin Not Loading

1. Check plugin directory is in search path
2. Verify `plugin.json` has correct syntax
3. Check for import errors in `__init__.py`
4. Enable debug logging: `logging.getLogger("widgetsystem").setLevel(logging.DEBUG)`

### Factory Not Found

1. Verify `register()` function is called
2. Check factory name spelling (case-sensitive)
3. Ensure plugin loaded successfully

### Hot Reload Issues

1. Some state may not preserve across reloads
2. Connected signals may need reconnection
3. Clear caches after reload if needed
