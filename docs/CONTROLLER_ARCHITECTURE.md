# Controller Architecture

This document describes the controller layer introduced in WidgetSystem v1.1.0 to address the "God Class" anti-pattern in MainWindow.

## Overview

The controller architecture follows the **MVC pattern**, extracting responsibilities from MainWindow into specialized controller classes. Each controller manages a single concern and communicates via Qt signals.

```
┌─────────────────────────────────────────────────────────────┐
│                      MainWindow                              │
│                    (Coordinator)                             │
│  - Initializes controllers                                   │
│  - Connects signals                                          │
│  - Handles window events                                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ DockController│   │LayoutController│   │ThemeController│
│               │   │               │   │               │
│ - create_panel│   │ - save()      │   │ - apply()     │
│ - float_all() │   │ - load()      │   │ - reload()    │
│ - dock_all()  │   │ - reset()     │   │ - register()  │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ DnDController │   │ResponsiveCtrl │   │ShortcutCtrl   │
│               │   │               │   │               │
│ - is_allowed()│   │ - update_for_ │   │ - create_     │
│ - initialize()│   │   width()     │   │   shortcuts() │
└───────────────┘   └───────────────┘   └───────────────┘
                              │
                              ▼
                    ┌───────────────┐
                    │  TabSubsystem │
                    │               │
                    │ - install()   │
                    │ - reset()     │
                    │ - apply_      │
                    │   theme_colors│
                    └───────────────┘
```

## Controllers

### DockController

**Location:** `src/widgetsystem/controllers/dock_controller.py`

Manages dock widget lifecycle including creation, registration, and bulk operations.

**Key Methods:**
- `create_panel(title, area, **options)` - Create a new dock panel
- `create_dynamic_panel()` - Create panel with auto-generated ID
- `create_tab_group(tab_group)` - Create dock with nested tabs
- `build_from_config()` - Build all docks from factory configs
- `float_all()` / `dock_all()` / `close_all()` - Bulk operations
- `find_dock(dock_id)` / `find_dock_by_title(title)` - Find docks

**Signals:**
- `dockAdded(dock_id, dock)` - Emitted when dock is created
- `dockRemoved(dock_id)` - Emitted when dock is removed
- `dockFloated(dock_id)` - Emitted when dock is floated
- `dockDocked(dock_id)` - Emitted when dock is docked

---

### LayoutController

**Location:** `src/widgetsystem/controllers/layout_controller.py`

Handles layout persistence: save, load, reset, and named layouts.

**Key Methods:**
- `save(path=None)` - Save current layout
- `load(path=None)` - Load layout from file
- `load_on_startup()` - Silent layout restoration
- `load_named(layout)` - Load a named layout
- `configure_dock_flags()` - Static method for CDockManager flags

**Signals:**
- `layoutSaved(path)` - Emitted on successful save
- `layoutLoaded(path)` - Emitted on successful load
- `layoutLoadFailed(path, error)` - Emitted on load failure
- `layoutReset()` - Emitted on layout reset

---

### ThemeController

**Location:** `src/widgetsystem/controllers/theme_controller.py`

Unified theme API consolidating ThemeFactory and ThemeManager.

**Key Methods:**
- `register_all_themes()` - Register legacy and profile themes
- `apply(theme_id)` - Apply theme by ID
- `apply_profile(profile_id)` - Apply profile theme
- `reload_themes()` - Hot-reload themes from factory

**Signals:**
- `themeApplied(theme_id, theme_name)` - Emitted on theme change
- `themeRegistered(theme_id)` - Emitted on theme registration
- `themeError(error_msg)` - Emitted on errors

---

### DnDController

**Location:** `src/widgetsystem/controllers/dnd_controller.py`

Manages drag-and-drop rules and drop zones.

**Key Methods:**
- `initialize()` - Load DnD config from factory
- `is_move_allowed(panel_id, source, target)` - Check if move is allowed
- `get_allowed_targets(panel_id, source)` - Get allowed target areas
- `get_drop_zone(area)` - Get drop zone for area

**Signals:**
- `moveBlocked(panel_id, source, target)` - Emitted when move is blocked
- `zoneRegistered(zone_id)` - Emitted on zone registration
- `ruleRegistered(rule_id)` - Emitted on rule registration

---

### ResponsiveController

**Location:** `src/widgetsystem/controllers/responsive_controller.py`

Handles responsive breakpoints and panel visibility rules.

**Key Methods:**
- `initialize()` - Load responsive config from factory
- `update_for_width(width)` - Update state for window width
- `get_breakpoint_for_width(width)` - Get breakpoint for width

**Signals:**
- `breakpointChanged(old_bp, new_bp)` - Emitted on breakpoint change
- `ruleApplied(rule_id)` - Emitted when rule is applied

---

### ShortcutController

**Location:** `src/widgetsystem/controllers/shortcut_controller.py`

Manages keyboard shortcuts and menu actions.

**Key Methods:**
- `register_handler(action_name, handler)` - Register action handler
- `create_global_shortcuts(shortcut_map)` - Create app-wide shortcuts
- `create_action(action_id, label, handler, shortcut)` - Create QAction
- `register_menu_actions()` - Register actions from MenuFactory

**Signals:**
- `actionRegistered(action_name)` - Emitted on action registration
- `shortcutRegistered(key_sequence)` - Emitted on shortcut registration

---

### TabSubsystem

**Location:** `src/widgetsystem/controllers/tab_subsystem.py`

Unified tab management consolidating 5 previous controllers.

**Key Methods:**
- `install(dock_manager)` - Install on dock manager
- `uninstall()` - Clean up controllers
- `reset()` - Reinstall all controllers
- `apply_theme_colors(active, inactive)` - Apply tab colors
- `track_dock_widget(dock_id, dock)` - Register dock for tracking

**Signals:**
- `tabColorsChanged(active, inactive)` - Emitted on color change
- `visibilityRefreshed()` - Emitted after visibility refresh

---

## Usage in MainWindow

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # ... window setup ...

        # Initialize controllers after dock_manager
        self.tab_sys = TabSubsystem()
        self.tab_sys.install(self.dock_manager)

        self.dnd_ctrl = DnDController(self.dnd_factory)
        self.dock_ctrl = DockController(
            self.dock_manager, self.panel_factory,
            self.tabs_factory, self.i18n_factory
        )
        self.layout_ctrl = LayoutController(
            self.dock_manager, self.layout_factory, self.i18n_factory
        )
        self.responsive_ctrl = ResponsiveController(
            self.responsive_factory, self.dock_ctrl
        )
        self.shortcut_ctrl = ShortcutController(
            self.menu_factory, self.i18n_factory, self
        )
        self.theme_ctrl = ThemeController(self.theme_factory)

        # Connect signals
        self.dock_ctrl.dockAdded.connect(
            lambda id, dock: self.tab_sys.track_dock_widget(id, dock)
        )
```

## Migration Guide

### Before (God Class):
```python
def _save_layout(self):
    state = self.dock_manager.saveState()
    self.layout_file.write_bytes(state.data())
    # ... error handling, messages ...
```

### After (Controller):
```python
def _save_layout(self):
    if self.layout_ctrl.save():
        QMessageBox.information(self, "Success", "Layout saved.")
```

## Benefits

1. **Single Responsibility** - Each controller handles one concern
2. **Testability** - Controllers can be unit tested in isolation
3. **Reusability** - Controllers can be used in other windows
4. **Maintainability** - Changes are localized to one controller
5. **Signal-based Communication** - Loose coupling via Qt signals
