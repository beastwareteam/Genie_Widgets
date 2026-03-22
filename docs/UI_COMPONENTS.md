# WidgetSystem UI Components

## Overview

WidgetSystem provides a comprehensive set of UI components built on PySide6 with QtAds integration. All components are designed for configuration-driven creation and seamless theming.

---

## Component Hierarchy

```
┌─────────────────────────────────────────────────────┐
│                    VisualApp                         │
│  Application wrapper with full visual system        │
├─────────────────────────────────────────────────────┤
│                 VisualMainWindow                     │
│  Main window with docking support                   │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ InlayTitleBar│ │VisualLayer  │ │ConfigPanel  │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │FloatingTitle │ │ ThemeEditor │ │ColorPicker  │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## VisualApp

Application wrapper providing full visual system initialization.

### Usage

```python
import sys
from widgetsystem.ui import VisualApp

def main():
    app = VisualApp(sys.argv)

    # Create main window
    window = app.create_main_window()
    window.show()

    # Run event loop
    return app.run()

if __name__ == "__main__":
    sys.exit(main())
```

### Features

- Application lifecycle management
- Theme system initialization
- Factory registration
- Plugin loading
- Signal connections

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `create_main_window()` | `VisualMainWindow` | Create main window instance |
| `run()` | `int` | Start event loop, return exit code |
| `quit()` | `None` | Quit application |
| `instance()` | `VisualApp` | Get current app instance (class method) |

---

## VisualMainWindow

Main application window with integrated docking system.

### Usage

```python
from widgetsystem.ui import VisualMainWindow
from pathlib import Path

window = VisualMainWindow(config_path=Path("config"))

# Access dock manager
dock_manager = window.dock_manager

# Add a dock widget
window.add_dock_widget("explorer", explorer_panel, "left")

# Show window
window.show()
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `dock_manager` | `CDockManager` | QtAds dock manager |
| `config_path` | `Path` | Configuration directory |
| `theme_manager` | `ThemeManager` | Theme manager instance |

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `add_dock_widget(id, widget, area)` | `id: str`, `widget: QWidget`, `area: str` | `CDockWidget` | Add dock widget |
| `remove_dock_widget(id)` | `id: str` | `bool` | Remove dock widget |
| `get_dock_widget(id)` | `id: str` | `CDockWidget` | Get dock widget by ID |
| `save_layout(name)` | `name: str` | `bool` | Save current layout |
| `restore_layout(name)` | `name: str` | `bool` | Restore saved layout |

---

## InlayTitleBar

Collapsible titlebar for dock widgets (3px collapsed, 35px expanded).

### Usage

```python
from widgetsystem.ui import InlayTitleBar
from PySide6.QtWidgets import QWidget

# Create titlebar
titlebar = InlayTitleBar(parent=dock_widget)

# Set title
titlebar.set_title("Explorer")

# Add action buttons
titlebar.add_action(
    icon=QIcon(":/icons/refresh.png"),
    tooltip="Refresh",
    callback=on_refresh
)

# Expand/collapse
titlebar.expand()
titlebar.collapse()
titlebar.toggle()
```

### Features

- **Collapsed State**: 3px thin bar, expands on hover
- **Expanded State**: 35px with title and action buttons
- **Smooth Animation**: Animated transitions
- **Action Buttons**: Add custom action buttons
- **Drag Support**: Enables panel dragging
- **Theme Integration**: Follows current theme

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `collapsed_height` | `int` | 3 | Height when collapsed |
| `expanded_height` | `int` | 35 | Height when expanded |
| `animation_duration` | `int` | 150 | Animation time (ms) |
| `is_expanded` | `bool` | False | Current expansion state |

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `set_title(title)` | `title: str` | `None` | Set titlebar text |
| `add_action(icon, tooltip, callback)` | see signature | `QPushButton` | Add action button |
| `remove_action(button)` | `button: QPushButton` | `None` | Remove action button |
| `expand()` | - | `None` | Expand titlebar |
| `collapse()` | - | `None` | Collapse titlebar |
| `toggle()` | - | `None` | Toggle state |
| `set_closable(closable)` | `closable: bool` | `None` | Enable/disable close |

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `expanded` | - | Emitted when expanded |
| `collapsed` | - | Emitted when collapsed |
| `closeRequested` | - | Close button clicked |
| `actionTriggered` | `str` | Action button clicked |

### Styling

```css
/* InlayTitleBar styling */
InlayTitleBar {
    background-color: @titlebar_background;
    border-bottom: 1px solid @border;
}

InlayTitleBar[expanded="true"] {
    background-color: @titlebar_background;
}

InlayTitleBar[expanded="false"] {
    background-color: @accent;
}

InlayTitleBar QLabel {
    color: @titlebar_foreground;
    font-weight: bold;
}

InlayTitleBar QPushButton {
    background: transparent;
    border: none;
    padding: 4px;
}

InlayTitleBar QPushButton:hover {
    background-color: @button_hover;
}
```

---

## FloatingTitlebar

Titlebar for floating dock containers.

### Usage

```python
from widgetsystem.ui import FloatingTitlebar

# Applied automatically to floating containers
titlebar = FloatingTitlebar(floating_container)
```

### Features

- Window controls (minimize, maximize, close)
- Drag to move
- Double-click to dock
- Theme-aware styling

---

## FloatingStateTracker

Tracks floating window state to preserve titlebar buttons.

### Usage

```python
from widgetsystem.ui import FloatingStateTracker

tracker = FloatingStateTracker(dock_manager)
tracker.start_tracking()

# React to state changes
tracker.stateChanged.connect(on_state_changed)
```

### Purpose

- Preserves custom titlebar buttons after re-docking
- Tracks floating/docked transitions
- Triggers refresh after state changes

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `stateChanged` | `str, bool` | (widget_id, is_floating) |
| `floatingStarted` | `str` | Widget started floating |
| `dockingCompleted` | `str` | Widget docked |

---

## TabColorController

Manages tab colors based on theme.

### Usage

```python
from widgetsystem.ui import TabColorController

controller = TabColorController(dock_manager, theme_manager)

# Update all tab colors
controller.update_tab_colors()

# Connect to theme changes
theme_manager.themeChanged.connect(controller.update_tab_colors)
```

### Features

- Active/inactive tab styling
- Hover state colors
- Theme-reactive updates

---

## TabSelectorMonitor

Monitors tab count for auto-hide behavior.

### Usage

```python
from widgetsystem.ui import TabSelectorMonitor

monitor = TabSelectorMonitor(dock_manager)
monitor.start_monitoring()

# React to count changes
monitor.tabCountChanged.connect(on_tab_count_changed)
```

### Features

- Tracks panel count per dock area
- Signals when single panel (hide tabs)
- Signals when multiple panels (show tabs)

---

## VisualLayer

Main visual layer for content rendering.

### Usage

```python
from widgetsystem.ui import VisualLayer

layer = VisualLayer(parent=central_widget)
layer.set_content(content_widget)
```

### Features

- Central content area
- Layer management
- Effect support

---

## ConfigurationPanel

Runtime configuration editing panel.

### Usage

```python
from widgetsystem.ui import ConfigurationPanel

panel = ConfigurationPanel(
    factories={
        "theme": theme_factory,
        "layout": layout_factory,
        "panel": panel_factory
    }
)

# Connect to changes
panel.configChanged.connect(on_config_changed)

def on_config_changed(factory_name: str, key: str, value: Any) -> None:
    print(f"{factory_name}.{key} = {value}")
```

### Features

- Tree view of configuration
- Inline editing
- Type-aware editors
- Validation feedback
- Undo support

---

## ThemeEditor

Live theme editing dialog.

### Usage

```python
from widgetsystem.ui import ThemeEditor
from pathlib import Path

editor = ThemeEditor(config_path=Path("config"))
editor.themeModified.connect(on_modified)
editor.show()
```

### Features

- Color property editors
- Live preview
- Gradient editor
- Save/export themes
- Reset to defaults

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `themeModified` | `str, dict` | Theme name and colors |
| `themeSaved` | `str` | Theme saved |
| `themeReset` | `str` | Theme reset to default |

---

## ARGBColorPicker

Color picker with alpha channel support.

### Usage

```python
from widgetsystem.ui import ARGBColorPicker
from PySide6.QtGui import QColor

picker = ARGBColorPicker()

# Set color with alpha
picker.set_color(QColor(0, 122, 204, 200))

# Get ARGB string
color = picker.get_color()
argb = picker.get_argb_string()  # "#c8007acc"

# Connect to changes
picker.colorChanged.connect(on_color)
```

### Components

- **Color Wheel**: Hue/saturation selection
- **Brightness Slider**: Value/brightness
- **Alpha Slider**: Transparency
- **RGBA Inputs**: Numeric input (0-255)
- **Hex Input**: #AARRGGBB string
- **Preview**: Current/previous comparison
- **Presets**: Quick color palette

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `colorChanged` | `QColor` | Color selection changed |
| `accepted` | `QColor` | OK clicked |
| `rejected` | - | Cancel clicked |

---

## WidgetFeaturesEditor

Widget property editor dialog.

### Usage

```python
from widgetsystem.ui import WidgetFeaturesEditor

editor = WidgetFeaturesEditor(target_widget=some_widget)
editor.propertyChanged.connect(on_property_changed)
editor.show()
```

### Features

- Property listing
- Type-appropriate editors
- Real-time preview
- Reset to defaults

### Supported Property Types

| Type | Editor |
|------|--------|
| `bool` | Checkbox |
| `int` | Spin box |
| `float` | Double spin box |
| `str` | Line edit |
| `QColor` | Color picker |
| `QFont` | Font dialog |
| `enum` | Combo box |

---

## TabSelector Components

### TabSelectorVisibilityController

Controls tab bar visibility based on panel count.

```python
from widgetsystem.ui import TabSelectorVisibilityController

controller = TabSelectorVisibilityController(dock_manager)
controller.start()

# Single panel: tabs hidden
# Multiple panels: tabs shown
```

### TabSelectorEventHandler

Handles tab selection events.

```python
from widgetsystem.ui import TabSelectorEventHandler

handler = TabSelectorEventHandler(dock_manager)
handler.tabSelected.connect(on_tab_selected)
```

---

## Creating Custom Components

### Basic Widget Pattern

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

class CustomWidget(QWidget):
    """Custom widget with signals."""

    # Define signals
    valueChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CustomWidget")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # Add widgets...

    def set_value(self, value: str) -> None:
        """Set value and emit signal."""
        self._value = value
        self.valueChanged.emit(value)

    def get_value(self) -> str:
        """Get current value."""
        return self._value
```

### Theme-Aware Widget

```python
from PySide6.QtWidgets import QWidget
from widgetsystem.core import ThemeManager

class ThemedWidget(QWidget):
    """Widget that responds to theme changes."""

    def __init__(self, theme_manager: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.theme_manager = theme_manager

        # Connect to theme changes
        self.theme_manager.themeChanged.connect(self._on_theme_changed)
        self.theme_manager.colorsUpdated.connect(self._update_colors)

        # Apply initial theme
        self._apply_theme()

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change."""
        self._apply_theme()

    def _update_colors(self, colors: dict) -> None:
        """Handle color updates."""
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply current theme to widget."""
        bg = self.theme_manager.get_color("background")
        fg = self.theme_manager.get_color("foreground")
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
        """)
```

### Factory-Created Widget

```python
from pathlib import Path
from typing import Any

class MyWidgetFactory:
    """Factory for creating themed widgets."""

    def __init__(self, config_path: Path, theme_manager: ThemeManager) -> None:
        self.config_path = config_path
        self.theme_manager = theme_manager
        self._config: dict | None = None

    def _load_config(self) -> dict[str, Any]:
        if self._config is None:
            with open(self.config_path / "my_widgets.json") as f:
                self._config = json.load(f)
        return self._config

    def create_widget(self, name: str) -> ThemedWidget:
        config = self._load_config()
        widget_config = config.get(name, {})

        widget = ThemedWidget(self.theme_manager)
        widget.setObjectName(name)
        # Apply config...

        return widget
```

---

## Best Practices

1. **Object Names**: Always set `objectName` for QSS targeting
2. **Signal Connections**: Disconnect signals in `closeEvent`
3. **Theme Awareness**: Connect to theme signals for dynamic updates
4. **Type Hints**: Use full type hints on all methods
5. **Docstrings**: Document all public methods
6. **Layout Margins**: Use consistent margins (typically 0 for containers)
7. **Parent References**: Always pass parent to prevent memory leaks
8. **Factory Creation**: Prefer factory creation over direct instantiation
