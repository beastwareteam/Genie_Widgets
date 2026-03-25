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
│   ├── ui_config_factory.py # UI configuration
│   └── ui_dimensions_factory.py # Centralized UI dimensions
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

---

## Tab System Architecture (Enhanced)

### Quality Gates & Implementation Phases

#### Phase 1: Core Infrastructure (DONE)
| Component | Status | Quality Gate |
|-----------|--------|--------------|
| `EnhancedTabWidget` | Done | Drag & Drop, Nesting, Close |
| `TabDropIndicator` | Done | Zone detection (BEFORE/INTO/AFTER) |
| `DockController` | Done | Integration tests |
| `TabsFactory` | Done | Config validation |

#### Phase 2: Command System (DONE)
| Component | Status | Quality Gate |
|-----------|--------|--------------|
| `TabCommandController` | Done | Undo/Redo tests |
| `CommandRegistry` | Done | CLI automation tests |
| `tab_commands.py` | Done | All commands reversible |
| `CloseTabUndoCommand` | Done | Full state restore |
| `NestTabUndoCommand` | Done | Hierarchy restore |

#### Phase 3: Integration Layer (DONE)
| Component | Status | Quality Gate |
|-----------|--------|--------------|
| QtAds ↔ EnhancedTabWidget | Done | Float/Dock round-trip |
| Nested DnD | Done | Cross-container transfer |
| Visual Feedback | Done | Zone highlighting |

#### Phase 4: Polish & Hardening (DONE)
| Component | Status | Quality Gate |
|-----------|--------|--------------|
| Circular nesting prevention | Done | TabHierarchyValidator |
| Max depth limiter | Done | Config-driven (layout_config.json) |
| Auto-dissolve empty folders | Done | Config-driven |
| UIDimensionsFactory | Done | Centralized dimensions |

### Tab Component Registry

```
widgetsystem/
├── ui/
│   ├── enhanced_tab_widget.py    # EnhancedTabWidget, EnhancedTabBar, DropZone
│   ├── tab_drop_indicator.py     # TabDropIndicator, TabDropIndicatorController
│   └── unified_tab_item.py       # UnifiedTabItem (metadata container)
├── controllers/
│   ├── dock_controller.py        # DockController (QtAds integration)
│   ├── tab_command_controller.py # TabCommandController (CLI operations)
│   └── unified_tab_manager.py    # UnifiedTabManager (central registry)
├── core/
│   ├── tab_commands.py           # Command classes (undo/redo)
│   ├── command_registry.py       # CommandRegistry (CLI dispatch)
│   └── undo_redo.py              # UndoRedoManager
└── factories/
    └── tabs_factory.py           # TabsFactory (JSON → widgets)
```

### Required Helpers & Utilities

#### 1. Tab Hierarchy Validator (Implemented)
```python
# src/widgetsystem/core/tab_hierarchy.py
class TabHierarchyValidator:
    def __init__(self, max_depth: int | None = None, auto_dissolve: bool | None = None):
        """Load config from layout_config.json if not provided."""

    def validate_nesting(self, source_id: str, target_id: str) -> tuple[bool, str]:
        """Prevent circular nesting and enforce depth limit."""

    def get_nesting_depth(self, tab_id: str) -> int:
        """Calculate current nesting depth (0 = root)."""

    def get_ancestor_chain(self, tab_id: str) -> list[str]:
        """Return all parent tab IDs up to root."""

    def should_dissolve_folder(self, folder_id: str) -> bool:
        """Check if folder should auto-dissolve (0-1 children)."""

    def can_nest_here(self, target_depth: int) -> bool:
        """Check if nesting allowed at given depth."""
```

#### 2. Tab State Serializer
```python
class TabStateSerializer:
    def serialize_hierarchy(self, root_widget: EnhancedTabWidget) -> dict:
        """Export complete tab tree to JSON."""

    def restore_hierarchy(self, state: dict, factory: TabsFactory) -> EnhancedTabWidget:
        """Rebuild tab tree from serialized state."""
```

#### 3. Memory Monitor (Debug)
```python
class TabMemoryMonitor:
    def track_widget(self, widget: QWidget, name: str) -> None:
        """Track widget for leak detection."""

    def report_leaks(self) -> list[str]:
        """Return list of widgets not properly cleaned up."""
```

### Signal Flow (Tab DnD)

```
User Drag Action
       │
       ▼
┌──────────────────┐
│ EnhancedTabBar   │
│ mouseMoveEvent() │
└────────┬─────────┘
         │ QDrag started
         ▼
┌──────────────────┐
│ dragMoveEvent()  │──────► dropZoneChanged Signal
└────────┬─────────┘              │
         │                        ▼
         │              ┌─────────────────────┐
         │              │ TabDropIndicator    │
         │              │ show_*_indicator()  │
         │              └─────────────────────┘
         ▼
┌──────────────────┐
│ dropEvent()      │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ Zone?   │
    └────┬────┘
         │
    ┌────┼────┬────┐
    ▼    ▼    ▼    ▼
 BEFORE INTO AFTER END
    │    │    │    │
    ▼    ▼    ▼    ▼
┌──────────────────┐
│ TabCommand       │
│ execute()        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ UndoRedoManager  │
│ push(command)    │
└──────────────────┘
```

### QtAds Integration Workarounds

1. **CDockOverlay Size**: QtAds overlay is C++ rendered, not QSS customizable
   - Solution: Use custom `TabDropIndicator` for tab-level DnD
   - QtAds overlay only for dock-level operations

2. **Float Window Title Bar**: QtAds uses native or custom title bar
   - Solution: `FloatingWindowPatcher` already implemented
   - Hooks into `CDockManager.floatingWidgetCreated`

3. **Dock Area Synchronization**: Keep tab state synced with dock state
   - Solution: `DockController._on_dock_closed()` cleanup handler
   - `_on_tab_floated()` creates new CDockWidget

### Integration Checklist
- [x] Tab float → CDockWidget creation
- [x] CDockWidget close → Tab cleanup
- [x] Tab nesting (folder-like behavior)
- [x] Auto-dissolve empty folders
- [x] Max nesting depth enforcement
- [x] Circular nesting prevention
- [x] Undo/Redo for close and nest operations
- [ ] Dock split → Tab transfer
- [ ] Floating window → Tab float back
- [ ] Dock area restore → Tab state restore

### Configuration Schema (Extended)

#### layout_config.json (UI Dimensions)
```json
{
  "titlebar": {
    "collapsed_height": 3,
    "collapsed_hit_height": 6,
    "expanded_height": 36,
    "animation_duration_ms": 160
  },
  "tabs": {
    "padding_vertical": 2,
    "padding_horizontal": 4,
    "margin_top": 2,
    "margin_right": 1,
    "margin_bottom": 0,
    "margin_left": 2,
    "border_radius": 4,
    "font_size": 11,
    "max_nesting_depth": 255,
    "auto_dissolve_empty_folders": true,
    "close_button": {
      "size": 14,
      "margin_top": 2,
      "margin_right": 2,
      "margin_bottom": 2,
      "margin_left": 2,
      "border_radius": 3
    }
  }
}
```

#### tabs.json (Tab Definitions)
```json
{
  "tabs": [
    {
      "id": "tab_main",
      "title_key": "tab.main",
      "closable": true,
      "movable": true,
      "floatable": true
    }
  ]
}
```

### Testing Strategy

#### Unit Tests
```
tests/
├── test_enhanced_tab_widget.py
│   ├── test_add_tab_with_metadata
│   ├── test_remove_tab_cleanup
│   ├── test_tab_metadata_persistence
│   └── test_nested_tab_creation
├── test_drop_zone.py
│   ├── test_zone_calculation_before
│   ├── test_zone_calculation_into
│   ├── test_zone_calculation_after
│   └── test_zone_edge_cases
├── test_tab_commands.py
│   ├── test_move_tab_undo_redo
│   ├── test_nest_tab_undo_redo
│   ├── test_unnest_tab_undo_redo
│   └── test_close_tab_undo_redo
└── test_memory.py
    ├── test_no_leaks_on_tab_close
    ├── test_no_leaks_on_nesting
    └── test_no_leaks_on_float
```

#### Integration Tests
```
tests/
├── test_qtads_integration.py
│   ├── test_tab_to_dock_float
│   ├── test_dock_to_tab_return
│   └── test_dock_split_with_tabs
└── test_dnd_e2e.py
    ├── test_drag_reorder
    ├── test_drag_nest
    ├── test_drag_cross_container
    └── test_drag_to_float
```
