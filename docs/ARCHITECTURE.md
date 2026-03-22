# WidgetSystem Architecture

## Overview

WidgetSystem is a modular, configuration-driven GUI framework built on PySide6 with QtAds (Advanced Docking System) integration. The architecture follows key software engineering principles:

- **Separation of Concerns**: Clear boundaries between core logic, factories, and UI
- **Factory Pattern**: Centralized component creation with configuration loading
- **Signal-based Communication**: Loose coupling via Qt signals
- **Plugin Architecture**: Runtime extensibility without code changes
- **Configuration-Driven**: JSON-based UI definition

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                         │
│  VisualApp │ MainWindow │ VisualMainWindow │ ConfigurationPanel │
├─────────────────────────────────────────────────────────────────┤
│                         UI COMPONENTS                            │
│  InlayTitleBar │ FloatingTitlebar │ TabSelector │ ThemeEditor   │
│  ARGBColorPicker │ WidgetFeaturesEditor │ VisualLayer           │
├─────────────────────────────────────────────────────────────────┤
│                        FACTORY SYSTEM                            │
│  Layout │ Theme │ Panel │ Menu │ Tabs │ DnD │ Responsive │ I18n │
│  List │ UIConfig                                                 │
├─────────────────────────────────────────────────────────────────┤
│                         CORE SYSTEMS                             │
│  PluginSystem │ UndoRedo │ ConfigIO │ TemplateSystem            │
│  ThemeManager │ GradientSystem │ ThemeProfile                    │
├─────────────────────────────────────────────────────────────────┤
│                      FOUNDATION (Qt/PySide6)                     │
│  PySide6.QtWidgets │ PySide6.QtCore │ PySide6.QtGui │ QtAds     │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/widgetsystem/
├── __init__.py              # Public API exports
├── py.typed                 # PEP 561 type marker
│
├── core/                    # Core systems
│   ├── __init__.py          # Core exports
│   ├── main.py              # Main application entry
│   ├── main_visual.py       # Visual main window
│   ├── plugin_system.py     # Dynamic plugin loading
│   ├── undo_redo.py         # Command pattern undo/redo
│   ├── config_io.py         # Import/export with backup
│   ├── template_system.py   # Configuration templates
│   ├── theme_manager.py     # Theme state management
│   ├── theme_profile.py     # Theme color profiles
│   └── gradient_system.py   # Dynamic gradient rendering
│
├── factories/               # Factory classes
│   ├── __init__.py          # Factory exports
│   ├── layout_factory.py    # Window layouts
│   ├── theme_factory.py     # Themes & stylesheets
│   ├── panel_factory.py     # Dock panels
│   ├── menu_factory.py      # Menu configurations
│   ├── tabs_factory.py      # Tab groups
│   ├── dnd_factory.py       # Drag & drop
│   ├── responsive_factory.py # Responsive layouts
│   ├── i18n_factory.py      # Internationalization
│   ├── list_factory.py      # Nested lists
│   └── ui_config_factory.py # UI configuration
│
└── ui/                      # UI components
    ├── __init__.py          # UI exports
    ├── visual_app.py        # Application wrapper
    ├── visual_layer.py      # Main visual layer
    ├── config_panel.py      # Configuration panel
    ├── inlay_titlebar.py    # Collapsible titlebar
    ├── floating_titlebar.py # Floating window titlebar
    ├── floating_state_tracker.py # Float state tracking
    ├── tab_color_controller.py   # Tab color management
    ├── tab_selector_monitor.py   # Tab count monitoring
    ├── tab_selector_event_handler.py # Tab selector events
    ├── tab_selector_visibility_controller.py
    ├── theme_editor.py      # Live theme editor
    ├── argb_color_picker.py # ARGB color selection
    └── widget_features_editor.py # Widget property editor
```

## Component Relationships

### Factory System

All factories inherit a common pattern:

```python
class SomeFactory:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._config: dict[str, Any] | None = None

    def _load_config(self) -> dict[str, Any]:
        """Load and cache configuration."""
        if self._config is None:
            with open(self.config_path / "config.json") as f:
                self._config = json.load(f)
        return self._config

    def create_something(self, key: str) -> SomeWidget:
        """Create component from configuration."""
        config = self._load_config()
        # Build and return widget
```

### Signal-based Communication

Components communicate via Qt signals for loose coupling:

```python
# ThemeManager signals
themeChanged = Signal(str)        # Theme name changed
colorsUpdated = Signal(dict)      # Color values updated
styleApplied = Signal(str)        # Stylesheet applied

# UndoRedoManager signals
undoAvailable = Signal(bool)      # Undo state changed
redoAvailable = Signal(bool)      # Redo state changed
commandExecuted = Signal(str)     # Command was executed
stackChanged = Signal()           # History changed

# PluginRegistry signals
pluginLoaded = Signal(str)        # Plugin loaded
pluginUnloaded = Signal(str)      # Plugin unloaded
factoryRegistered = Signal(str)   # Factory registered
```

### Dependency Injection

Factories receive configuration paths, enabling testing and flexibility:

```python
# Production
factory = ThemeFactory(Path("config"))

# Testing
factory = ThemeFactory(Path("tests/fixtures"))
```

## Design Patterns

### 1. Factory Pattern
Central creation of UI components with configuration loading:
- Encapsulates widget instantiation
- Provides consistent interface
- Enables configuration-driven UI

### 2. Command Pattern (Undo/Redo)
Reversible operations for configuration editing:
- `Command` base class with execute/undo
- `PropertyChangeCommand`, `DictChangeCommand`, `ListChangeCommand`
- `CompositeCommand` for grouped operations

### 3. Observer Pattern (Qt Signals)
Event-based communication:
- Decouples senders from receivers
- Enables reactive UI updates
- Thread-safe by Qt implementation

### 4. Plugin Architecture
Runtime extensibility:
- `PluginRegistry` for factory management
- `PluginManager` for discovery and loading
- Hot-reload capability

### 5. Template Method Pattern
Consistent factory structure:
- Abstract `_load_config()` logic
- Concrete `create_*()` methods
- Optional validation hooks

## Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    JSON      │────▶│   Factory    │────▶│   Widget     │
│   Config     │     │   Class      │     │   Instance   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Schema     │     │   Plugin     │     │   Signal     │
│  Validation  │     │   Registry   │     │  Emissions   │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Threading Model

- Main Qt event loop handles all UI operations
- Signals are thread-safe and can cross thread boundaries
- Heavy operations should use `QThread` or `QRunnable`
- Configuration loading is synchronous (typically fast)

## Extension Points

1. **Custom Factories**: Implement factory interface, register with PluginRegistry
2. **Custom Commands**: Inherit from `Command` for new undo/redo operations
3. **Custom Templates**: Add to TemplateManager's built-in collection
4. **Custom Themes**: JSON theme definitions with QSS stylesheets
5. **Custom Panels**: Factory-created dock panels with custom content

## Security Considerations

- Configuration files are validated against JSON schemas
- File paths are sanitized before use
- No dynamic code execution from configuration
- Backup system prevents data loss
- Export/import validates data integrity
