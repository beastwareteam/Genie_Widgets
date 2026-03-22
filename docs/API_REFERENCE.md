# WidgetSystem API Reference

Complete API documentation for all public classes and methods.

---

## Table of Contents

1. [Core Systems](#core-systems)
   - [PluginSystem](#pluginsystem)
   - [UndoRedo](#undoredo)
   - [ConfigIO](#configio)
   - [TemplateSystem](#templatesystem)
   - [ThemeManager](#thememanager)
   - [GradientSystem](#gradientsystem)
2. [Factory Classes](#factory-classes)
3. [UI Components](#ui-components)

---

## Core Systems

### PluginSystem

#### PluginRegistry

Central registry for factory management.

```python
from widgetsystem.core import PluginRegistry

registry = PluginRegistry()
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `register_factory(name, factory_class)` | `name: str`, `factory_class: Type` | `None` | Register a factory class |
| `unregister_factory(name)` | `name: str` | `bool` | Unregister a factory |
| `get_factory(name)` | `name: str` | `Type \| None` | Get registered factory |
| `list_factories()` | - | `list[str]` | List all registered factory names |
| `clear()` | - | `None` | Remove all registrations |

**Signals:**

| Signal | Parameters | Description |
|--------|------------|-------------|
| `pluginLoaded` | `str` | Emitted when plugin is loaded |
| `pluginUnloaded` | `str` | Emitted when plugin is unloaded |
| `factoryRegistered` | `str` | Emitted when factory is registered |
| `errorOccurred` | `str` | Emitted on error |

#### PluginManager

Dynamic plugin discovery and loading.

```python
from widgetsystem.core import PluginManager
from pathlib import Path

manager = PluginManager([Path("plugins")])
manager.load_all_plugins()
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `load_plugin(path)` | `path: Path` | `bool` | Load single plugin |
| `load_all_plugins()` | - | `list[str]` | Load all discovered plugins |
| `unload_plugin(name)` | `name: str` | `bool` | Unload a plugin |
| `reload_plugin(name)` | `name: str` | `bool` | Hot-reload a plugin |
| `get_plugin_info(name)` | `name: str` | `dict` | Get plugin metadata |
| `list_plugins()` | - | `list[str]` | List loaded plugin names |

---

### UndoRedo

#### Command (Abstract Base Class)

```python
from widgetsystem.core import Command

class MyCommand(Command):
    def execute(self) -> None:
        # Perform action
        pass

    def undo(self) -> None:
        # Reverse action
        pass
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `description` | `str` | Human-readable description |
| `timestamp` | `datetime` | When command was created |

#### PropertyChangeCommand

```python
from widgetsystem.core import PropertyChangeCommand

cmd = PropertyChangeCommand(
    target=some_object,
    property_name="name",
    old_value="old",
    new_value="new",
    description="Change name"
)
```

#### DictChangeCommand

```python
from widgetsystem.core import DictChangeCommand

cmd = DictChangeCommand(
    target_dict=my_dict,
    key="setting",
    old_value="old_value",
    new_value="new_value"
)
```

#### ListChangeCommand

```python
from widgetsystem.core import ListChangeCommand

cmd = ListChangeCommand(
    target_list=my_list,
    index=0,
    old_item=None,      # None = insert
    new_item="new_item"
)
```

#### CompositeCommand

```python
from widgetsystem.core import CompositeCommand

composite = CompositeCommand(
    commands=[cmd1, cmd2, cmd3],
    description="Batch changes"
)
```

#### UndoRedoManager

```python
from widgetsystem.core import UndoRedoManager

manager = UndoRedoManager(max_history=100)
manager.execute(command)
manager.undo()
manager.redo()
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `execute(command)` | `command: Command` | `None` | Execute and track command |
| `undo()` | - | `bool` | Undo last command |
| `redo()` | - | `bool` | Redo last undone command |
| `can_undo()` | - | `bool` | Check if undo available |
| `can_redo()` | - | `bool` | Check if redo available |
| `clear()` | - | `None` | Clear all history |
| `get_undo_description()` | - | `str \| None` | Get next undo description |
| `get_redo_description()` | - | `str \| None` | Get next redo description |
| `get_undo_history()` | - | `list[str]` | Get undo stack descriptions |
| `get_redo_history()` | - | `list[str]` | Get redo stack descriptions |

**Signals:**

| Signal | Parameters | Description |
|--------|------------|-------------|
| `undoAvailable` | `bool` | Undo availability changed |
| `redoAvailable` | `bool` | Redo availability changed |
| `commandExecuted` | `str` | Command was executed |
| `commandUndone` | `str` | Command was undone |
| `commandRedone` | `str` | Command was redone |
| `stackChanged` | - | Stack was modified |

#### ConfigurationUndoManager

Extended undo manager for configuration editing.

```python
from widgetsystem.core import ConfigurationUndoManager
from pathlib import Path

manager = ConfigurationUndoManager(config_path=Path("config"))
```

**Additional Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_snapshot(name, data)` | `name: str`, `data: Any` | `None` | Create named snapshot |
| `restore_snapshot(name)` | `name: str` | `Any \| None` | Restore snapshot |
| `delete_snapshot(name)` | `name: str` | `None` | Delete snapshot |
| `set_save_point()` | - | `None` | Mark current state |
| `is_at_save_point()` | - | `bool` | Check if at save point |
| `has_unsaved_changes()` | - | `bool` | Check for unsaved changes |
| `track_config_change(...)` | see below | `None` | Track config modification |
| `track_list_insert(...)` | see below | `None` | Track list insertion |
| `track_list_remove(...)` | see below | `None` | Track list removal |

---

### ConfigIO

#### ConfigurationExporter

```python
from widgetsystem.core import ConfigurationExporter, ExportOptions
from pathlib import Path

exporter = ConfigurationExporter(Path("config"))
options = ExportOptions(include_themes=True, include_layouts=True)
exporter.export_to_archive(Path("backup.zip"), options)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `export_to_archive(path, options)` | `path: Path`, `options: ExportOptions` | `bool` | Export to ZIP |
| `export_to_directory(path, options)` | `path: Path`, `options: ExportOptions` | `bool` | Export to folder |
| `get_exportable_configs()` | - | `list[str]` | List available configs |

**Signals:**

| Signal | Parameters | Description |
|--------|------------|-------------|
| `exportStarted` | `str` | Export started |
| `exportProgress` | `int, str` | Progress update |
| `exportCompleted` | `str` | Export finished |
| `exportFailed` | `str` | Export error |

#### ConfigurationImporter

```python
from widgetsystem.core import ConfigurationImporter, ImportOptions

importer = ConfigurationImporter(Path("config"))
options = ImportOptions(merge_mode="replace", backup_existing=True)
importer.import_from_archive(Path("backup.zip"), options)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `import_from_archive(path, options)` | `path: Path`, `options: ImportOptions` | `bool` | Import from ZIP |
| `import_from_directory(path, options)` | `path: Path`, `options: ImportOptions` | `bool` | Import from folder |
| `validate_import(path)` | `path: Path` | `tuple[bool, list[str]]` | Validate before import |

#### BackupManager

```python
from widgetsystem.core import BackupManager

backup = BackupManager(Path("config"), max_backups=10)
backup.create_backup("before_update")
backup.restore_backup("backup_name")
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_backup(name)` | `name: str` | `Path` | Create named backup |
| `restore_backup(name)` | `name: str` | `bool` | Restore from backup |
| `list_backups()` | - | `list[str]` | List available backups |
| `delete_backup(name)` | `name: str` | `bool` | Delete a backup |
| `cleanup_old_backups()` | - | `int` | Remove excess backups |

---

### TemplateSystem

#### TemplateManager

```python
from widgetsystem.core import TemplateManager

manager = TemplateManager()
templates = manager.list_templates()
config = manager.apply_template("builtin_dark_theme", {"accent_color": "#FF5722"})
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `list_templates()` | - | `list[TemplateMetadata]` | List all templates |
| `get_template(template_id)` | `template_id: str` | `ConfigurationTemplate \| None` | Get template |
| `apply_template(template_id, overrides)` | `template_id: str`, `overrides: dict` | `dict` | Apply with overrides |
| `create_template(name, config, category)` | see signature | `str` | Create new template |
| `delete_template(template_id)` | `template_id: str` | `bool` | Delete template |
| `export_template(template_id, path)` | `template_id: str`, `path: Path` | `bool` | Export to file |
| `import_template(path)` | `path: Path` | `str` | Import from file |

**Built-in Templates:**

| ID | Name | Category |
|----|------|----------|
| `builtin_minimal` | Minimal Layout | layouts |
| `builtin_developer` | Developer Layout | layouts |
| `builtin_dashboard` | Dashboard Layout | layouts |
| `builtin_dark_theme` | Dark Theme | themes |
| `builtin_light_theme` | Light Theme | themes |

**Signals:**

| Signal | Parameters | Description |
|--------|------------|-------------|
| `templateCreated` | `str` | Template created |
| `templateApplied` | `str` | Template applied |
| `templateDeleted` | `str` | Template deleted |

---

### ThemeManager

```python
from widgetsystem.core import ThemeManager, Theme

manager = ThemeManager()
manager.set_theme("dark")
current = manager.current_theme
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `set_theme(name)` | `name: str` | `bool` | Apply theme by name |
| `get_theme(name)` | `name: str` | `Theme \| None` | Get theme definition |
| `list_themes()` | - | `list[str]` | List available themes |
| `register_theme(theme)` | `theme: Theme` | `None` | Register new theme |
| `apply_stylesheet(widget)` | `widget: QWidget` | `None` | Apply current theme |
| `get_color(color_name)` | `color_name: str` | `str` | Get theme color |

**Signals:**

| Signal | Parameters | Description |
|--------|------------|-------------|
| `themeChanged` | `str` | Theme was changed |
| `colorsUpdated` | `dict` | Colors were modified |
| `styleApplied` | `str` | Stylesheet applied |

---

### GradientSystem

```python
from widgetsystem.core import GradientRenderer, GradientDefinition, GradientStop

renderer = GradientRenderer()
gradient = GradientDefinition(
    stops=[
        GradientStop(0.0, "#FF0000"),
        GradientStop(1.0, "#0000FF")
    ],
    angle=45
)
qss = renderer.to_qss(gradient)
```

---

## Factory Classes

All factories follow the same initialization pattern:

```python
from pathlib import Path
factory = SomeFactory(Path("config"))
```

### LayoutFactory

```python
from widgetsystem.factories import LayoutFactory

factory = LayoutFactory(Path("config"))
layout = factory.create_layout("main_layout")
factory.save_layout(dock_manager, "custom_layout")
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_layout(name)` | `name: str` | `dict` | Get layout definition |
| `save_layout(dock_manager, name)` | `dock_manager, name: str` | `bool` | Save current layout |
| `list_layouts()` | - | `list[str]` | List available layouts |
| `delete_layout(name)` | `name: str` | `bool` | Delete a layout |

### ThemeFactory

```python
from widgetsystem.factories import ThemeFactory

factory = ThemeFactory(Path("config"))
theme_data = factory.get_theme("dark")
stylesheet = factory.get_stylesheet("dark")
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_theme(name)` | `name: str` | `dict` | Get theme definition |
| `get_stylesheet(name)` | `name: str` | `str` | Get QSS stylesheet |
| `list_themes()` | - | `list[str]` | List available themes |
| `create_theme(name, colors)` | `name: str`, `colors: dict` | `bool` | Create new theme |

### PanelFactory

```python
from widgetsystem.factories import PanelFactory

factory = PanelFactory(Path("config"))
panel = factory.create_panel("explorer")
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_panel(name)` | `name: str` | `QWidget` | Create panel widget |
| `list_panels()` | - | `list[str]` | List available panels |
| `get_panel_config(name)` | `name: str` | `dict` | Get panel configuration |

### MenuFactory

```python
from widgetsystem.factories import MenuFactory

factory = MenuFactory(Path("config"))
menubar = factory.create_menubar(parent_widget)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_menubar(parent)` | `parent: QWidget` | `QMenuBar` | Create menu bar |
| `create_menu(name, parent)` | `name: str`, `parent: QWidget` | `QMenu` | Create single menu |
| `create_context_menu(name)` | `name: str` | `QMenu` | Create context menu |

### TabsFactory

```python
from widgetsystem.factories import TabsFactory

factory = TabsFactory(Path("config"))
tabs = factory.create_tab_group("main_tabs")
```

### DnDFactory

```python
from widgetsystem.factories import DnDFactory

factory = DnDFactory(Path("config"))
factory.setup_drag_drop(widget)
```

### I18nFactory

```python
from widgetsystem.factories import I18nFactory

factory = I18nFactory(Path("config"))
factory.set_language("de")
text = factory.translate("menu.file")
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `set_language(code)` | `code: str` | `None` | Set active language |
| `translate(key)` | `key: str` | `str` | Get translated text |
| `list_languages()` | - | `list[str]` | List available languages |

### ListFactory

```python
from widgetsystem.factories import ListFactory

factory = ListFactory(Path("config"))
list_widget = factory.create_list("file_list")
```

### ResponsiveFactory

```python
from widgetsystem.factories import ResponsiveFactory

factory = ResponsiveFactory(Path("config"))
factory.apply_responsive_layout(widget, width=1200)
```

### UIConfigFactory

```python
from widgetsystem.factories import UIConfigFactory

factory = UIConfigFactory(Path("config"))
config = factory.get_config()
```

---

## UI Components

### VisualApp

Application wrapper with full visual system.

```python
from widgetsystem.ui import VisualApp
import sys

app = VisualApp(sys.argv)
window = app.create_main_window()
app.run()
```

### InlayTitleBar

Collapsible titlebar (3px collapsed, 35px expanded).

```python
from widgetsystem.ui import InlayTitleBar

titlebar = InlayTitleBar(parent=dock_widget)
titlebar.set_title("Panel Title")
titlebar.add_action(icon, "tooltip", callback)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `set_title(title)` | `title: str` | `None` | Set titlebar text |
| `add_action(icon, tooltip, callback)` | see signature | `QPushButton` | Add action button |
| `expand()` | - | `None` | Expand titlebar |
| `collapse()` | - | `None` | Collapse titlebar |
| `toggle()` | - | `None` | Toggle expanded state |

### FloatingTitlebar

Titlebar for floating dock windows.

```python
from widgetsystem.ui import FloatingTitlebar

titlebar = FloatingTitlebar(floating_container)
```

### ARGBColorPicker

ARGB color picker with alpha channel support.

```python
from widgetsystem.ui import ARGBColorPicker
from PySide6.QtGui import QColor

picker = ARGBColorPicker()
picker.colorChanged.connect(on_color_changed)
picker.set_color(QColor("#80FF5722"))  # With alpha
color = picker.get_color()
```

**Signals:**

| Signal | Parameters | Description |
|--------|------------|-------------|
| `colorChanged` | `QColor` | Color selection changed |

### ThemeEditor

Live theme editing dialog.

```python
from widgetsystem.ui import ThemeEditor

editor = ThemeEditor(theme_factory, parent=window)
editor.themeModified.connect(on_theme_changed)
editor.show()
```

### WidgetFeaturesEditor

Widget property editor.

```python
from widgetsystem.ui import WidgetFeaturesEditor

editor = WidgetFeaturesEditor(target_widget)
editor.propertyChanged.connect(on_property_changed)
```

### ConfigurationPanel

Runtime configuration GUI.

```python
from widgetsystem.ui import ConfigurationPanel

panel = ConfigurationPanel(factories_dict)
panel.configChanged.connect(on_config_changed)
```

### TabColorController

Tab color management.

```python
from widgetsystem.ui import TabColorController

controller = TabColorController(dock_manager, theme_manager)
controller.update_tab_colors()
```

### FloatingStateTracker

Tracks floating window state for titlebar preservation.

```python
from widgetsystem.ui import FloatingStateTracker

tracker = FloatingStateTracker(dock_manager)
tracker.start_tracking()
```

---

## Type Definitions

All public types are exported from the main package:

```python
from widgetsystem import (
    # Core
    PluginRegistry,
    PluginManager,
    UndoRedoManager,
    ConfigurationUndoManager,
    Command,
    PropertyChangeCommand,
    DictChangeCommand,
    ListChangeCommand,
    CompositeCommand,
    CallbackCommand,
    ConfigurationExporter,
    ConfigurationImporter,
    BackupManager,
    ExportOptions,
    ImportOptions,
    ConfigMetadata,
    TemplateManager,
    ConfigurationTemplate,
    TemplateMetadata,
    ThemeManager,
    Theme,
    ThemeProfile,
    ThemeColors,
    GradientRenderer,
    GradientDefinition,
    GradientStop,

    # Factories
    LayoutFactory,
    ThemeFactory,
    PanelFactory,
    MenuFactory,
    TabsFactory,
    DnDFactory,
    I18nFactory,
    ListFactory,
    ResponsiveFactory,
    UIConfigFactory,

    # UI
    VisualApp,
    VisualLayer,
    ConfigurationPanel,
    InlayTitleBar,
    FloatingTitlebar,
    ARGBColorPicker,
    ThemeEditor,
    WidgetFeaturesEditor,
    TabColorController,
    FloatingStateTracker,
)
```
