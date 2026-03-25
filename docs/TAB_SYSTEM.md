# Tab System Documentation

## Overview

The WidgetSystem Tab System provides a comprehensive, folder-like tab management solution built on top of PySide6 QTabWidget with full drag-and-drop support, nesting capabilities, and undo/redo functionality.

## Key Features

### 1. Tab Nesting (Folder-like Behavior)
- Drag a tab INTO another tab's center zone to create a nested structure
- Nested tabs work like folders - you can nest up to 255 levels deep
- Auto-dissolve: When a folder has 0-1 tabs remaining, it automatically collapses

### 2. Drag & Drop Zones
When dragging a tab over another tab, three drop zones are detected:
- **BEFORE (25% left)**: Insert tab before target
- **INTO (50% center)**: Nest tab into target (creates folder)
- **AFTER (25% right)**: Insert tab after target
- **END**: Append at the end of the tab bar

### 3. Undo/Redo Support
All tab operations are reversible:
- `CloseTabUndoCommand`: Restore closed tabs with full state
- `NestTabUndoCommand`: Undo/redo nesting operations
- Shared `UndoRedoManager` across all tab widgets

### 4. CLI Automation
Programmatic control via `TabCommandController`:
```python
from widgetsystem.controllers import TabCommandController

controller = TabCommandController(dock_controller)
controller.move_tab("tab_charts", "main_tabs", index=0)
controller.nest_tab("tab_charts", "tab_analytics")
controller.close_tab("tab_settings")
controller.list_tabs()  # Returns all registered tabs
```

## Configuration

### layout_config.json
```json
{
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

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_nesting_depth` | int | 255 | Maximum folder nesting levels |
| `auto_dissolve_empty_folders` | bool | true | Auto-collapse folders with 0-1 tabs |
| `padding_vertical` | int | 2 | Vertical padding inside tabs |
| `padding_horizontal` | int | 4 | Horizontal padding inside tabs |
| `border_radius` | int | 4 | Tab corner radius |
| `font_size` | int | 11 | Tab label font size |

## Components

### Core Classes

#### EnhancedTabWidget
Main tab widget with drag & drop support.
```python
from widgetsystem.ui import EnhancedTabWidget

tabs = EnhancedTabWidget()
tabs.addTab(widget, "Label", tab_id="unique_id", closable=True, movable=True)

# Signals
tabs.tabNested.connect(lambda nested_id, parent_id: ...)
tabs.tabFloated.connect(lambda tab_id, widget: ...)
tabs.tabMoved.connect(lambda from_idx, to_idx: ...)
```

#### TabHierarchyValidator
Validates nesting operations and prevents invalid states.
```python
from widgetsystem.core.tab_hierarchy import get_hierarchy_validator

validator = get_hierarchy_validator()
is_valid, error_msg = validator.validate_nesting("source_id", "target_id")
depth = validator.get_nesting_depth("tab_id")
ancestors = validator.get_ancestor_chain("tab_id")
```

#### UIDimensionsFactory
Centralized UI dimensions from config.
```python
from widgetsystem.factories import UIDimensionsFactory

factory = UIDimensionsFactory.get_instance()
dims = factory.get()
print(dims.tabs.max_nesting_depth)  # 255
print(dims.tabs.auto_dissolve_empty_folders)  # True
```

### Controllers

#### TabCommandController
CLI automation for tab operations.
- `move_tab(tab_id, target, index)` - Move tab to new position
- `nest_tab(source_id, target_id)` - Nest tab into another
- `unnest_tab(tab_id)` - Extract tab from folder
- `float_tab(tab_id)` - Float tab to separate window
- `close_tab(tab_id)` - Close tab (undoable)
- `list_tabs()` - List all registered tabs

#### CommandRegistry
Central command dispatch for automation.
```python
from widgetsystem.core import CommandRegistry

registry = CommandRegistry()
registry.execute("nest_tab", source="tab_charts", target="tab_overview")
```

## Signal Flow

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
         │              │ Visual Feedback     │
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
│ Command Created  │
│ (Undoable)       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ UndoRedoManager  │
│ push(command)    │
└──────────────────┘
```

## Best Practices

1. **Always use tab IDs**: Provide unique `tab_id` when adding tabs for reliable tracking
2. **Handle signals**: Connect to `tabNested`, `tabFloated`, `tabMoved` for state tracking
3. **Use undo manager**: Access via `EnhancedTabWidget.get_undo_manager()` for consistent undo state
4. **Check nesting validity**: Use `TabHierarchyValidator.validate_nesting()` before programmatic nesting

## Troubleshooting

### Tab won't nest
- Check `max_nesting_depth` in config
- Verify no circular nesting (A into B into A)
- Ensure target is not a descendant of source

### Auto-dissolve not working
- Verify `auto_dissolve_empty_folders: true` in config
- Check that container has `parent_tab_id` property set

### Undo not restoring state
- Ensure operations go through command system
- Check `UndoRedoManager` has the command in history
