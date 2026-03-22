# WidgetSystem Signals & Events

## Overview

WidgetSystem uses Qt's signal-slot mechanism for loose coupling between components. This document provides a comprehensive reference for all signals emitted by system components.

---

## Signal Architecture

```
┌─────────────────┐     Signal      ┌─────────────────┐
│    Emitter      │ ───────────────▶│    Receiver     │
│   (QObject)     │                 │    (Slot)       │
└─────────────────┘                 └─────────────────┘
        │
        │  Thread-safe
        │  Type-checked
        ▼
┌─────────────────────────────────────────────────────┐
│                  Qt Event Loop                       │
│  - Queued connections for cross-thread              │
│  - Direct connections for same thread               │
│  - Automatic disconnection on object destruction    │
└─────────────────────────────────────────────────────┘
```

---

## Core System Signals

### PluginRegistry

```python
from widgetsystem.core import PluginRegistry

registry = PluginRegistry()
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `pluginLoaded` | `str` | Plugin name loaded |
| `pluginUnloaded` | `str` | Plugin name unloaded |
| `factoryRegistered` | `str` | Factory name registered |
| `factoryUnregistered` | `str` | Factory name unregistered |
| `errorOccurred` | `str` | Error message |

**Connection Example:**

```python
registry.pluginLoaded.connect(self._on_plugin_loaded)
registry.factoryRegistered.connect(self._on_factory_registered)
registry.errorOccurred.connect(self._on_error)

def _on_plugin_loaded(self, name: str) -> None:
    print(f"Plugin loaded: {name}")

def _on_factory_registered(self, name: str) -> None:
    print(f"Factory registered: {name}")

def _on_error(self, message: str) -> None:
    logging.error(f"Plugin error: {message}")
```

---

### UndoRedoManager

```python
from widgetsystem.core import UndoRedoManager

manager = UndoRedoManager(max_history=100)
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `undoAvailable` | `bool` | Undo availability changed |
| `redoAvailable` | `bool` | Redo availability changed |
| `commandExecuted` | `str` | Command description executed |
| `commandUndone` | `str` | Command description undone |
| `commandRedone` | `str` | Command description redone |
| `stackChanged` | - | Command stack modified |

**Connection Example:**

```python
# Enable/disable UI buttons
manager.undoAvailable.connect(undo_button.setEnabled)
manager.redoAvailable.connect(redo_button.setEnabled)

# Update status bar
manager.commandExecuted.connect(lambda desc: statusbar.showMessage(f"Executed: {desc}"))
manager.commandUndone.connect(lambda desc: statusbar.showMessage(f"Undone: {desc}"))

# Track history changes
manager.stackChanged.connect(self._update_history_view)
```

---

### ConfigurationUndoManager

Extends `UndoRedoManager` with:

| Signal | Parameters | Description |
|--------|------------|-------------|
| `savePointReached` | - | Returned to save point |

```python
from widgetsystem.core import ConfigurationUndoManager

manager = ConfigurationUndoManager()
manager.savePointReached.connect(self._on_save_point)
```

---

### ConfigurationExporter

```python
from widgetsystem.core import ConfigurationExporter

exporter = ConfigurationExporter(Path("config"))
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `exportStarted` | `str` | Export path |
| `exportProgress` | `int, str` | Percentage, current file |
| `exportCompleted` | `str` | Export path |
| `exportFailed` | `str` | Error message |

**Connection Example:**

```python
def export_with_progress():
    progress_dialog = QProgressDialog("Exporting...", "Cancel", 0, 100)

    exporter.exportStarted.connect(lambda p: progress_dialog.setLabelText(f"Exporting to {p}"))
    exporter.exportProgress.connect(lambda pct, f: progress_dialog.setValue(pct))
    exporter.exportCompleted.connect(lambda p: QMessageBox.information(None, "Done", f"Exported to {p}"))
    exporter.exportFailed.connect(lambda e: QMessageBox.critical(None, "Error", e))

    exporter.export_to_archive(Path("backup.zip"))
```

---

### ConfigurationImporter

```python
from widgetsystem.core import ConfigurationImporter

importer = ConfigurationImporter(Path("config"))
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `importStarted` | `str` | Import source path |
| `importProgress` | `int, str` | Percentage, current file |
| `importCompleted` | `str` | Import source path |
| `importFailed` | `str` | Error message |
| `conflictDetected` | `str, str` | File, conflict type |

---

### TemplateManager

```python
from widgetsystem.core import TemplateManager

manager = TemplateManager()
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `templateCreated` | `str` | Template ID created |
| `templateApplied` | `str` | Template ID applied |
| `templateDeleted` | `str` | Template ID deleted |
| `templateModified` | `str` | Template ID modified |

---

### ThemeManager

```python
from widgetsystem.core import ThemeManager

manager = ThemeManager()
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `themeChanged` | `str` | New theme name |
| `colorsUpdated` | `dict` | Updated colors dictionary |
| `styleApplied` | `str` | Stylesheet content applied |
| `themeRegistered` | `str` | New theme registered |

**Connection Example:**

```python
# React to theme changes
theme_manager.themeChanged.connect(self._on_theme_changed)
theme_manager.colorsUpdated.connect(self._update_custom_widgets)

def _on_theme_changed(self, theme_name: str) -> None:
    # Update UI elements that need manual refresh
    self._refresh_icons()
    self._update_graphics_items()

def _update_custom_widgets(self, colors: dict) -> None:
    # Update widgets that don't use QSS
    self.custom_canvas.setBackgroundColor(QColor(colors["background"]))
```

---

## UI Component Signals

### InlayTitleBar

```python
from widgetsystem.ui import InlayTitleBar

titlebar = InlayTitleBar(parent)
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `expanded` | - | Titlebar expanded |
| `collapsed` | - | Titlebar collapsed |
| `closeRequested` | - | Close button clicked |
| `actionTriggered` | `str` | Action button ID clicked |
| `doubleClicked` | - | Titlebar double-clicked |
| `dragStarted` | `QPoint` | Drag operation started |

**Connection Example:**

```python
titlebar.expanded.connect(self._on_titlebar_expanded)
titlebar.collapsed.connect(self._on_titlebar_collapsed)
titlebar.closeRequested.connect(self._close_panel)
titlebar.actionTriggered.connect(self._handle_action)

def _handle_action(self, action_id: str) -> None:
    if action_id == "refresh":
        self._refresh_content()
    elif action_id == "settings":
        self._show_settings()
```

---

### ARGBColorPicker

```python
from widgetsystem.ui import ARGBColorPicker

picker = ARGBColorPicker()
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `colorChanged` | `QColor` | Color selection changed |
| `colorSelected` | `QColor` | Final color selected |
| `accepted` | `QColor` | OK button clicked |
| `rejected` | - | Cancel clicked |

**Connection Example:**

```python
picker.colorChanged.connect(self._preview_color)
picker.accepted.connect(self._apply_color)

def _preview_color(self, color: QColor) -> None:
    # Live preview without committing
    self.preview_widget.setStyleSheet(f"background: {color.name(QColor.HexArgb)};")

def _apply_color(self, color: QColor) -> None:
    # Commit the color change
    self.target_widget.setColor(color)
```

---

### ThemeEditor

```python
from widgetsystem.ui import ThemeEditor

editor = ThemeEditor(config_path)
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `themeModified` | `str, dict` | Theme name, colors |
| `themeSaved` | `str` | Theme name saved |
| `themeReset` | `str` | Theme name reset |
| `previewRequested` | `dict` | Colors to preview |

---

### FloatingStateTracker

```python
from widgetsystem.ui import FloatingStateTracker

tracker = FloatingStateTracker(dock_manager)
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `stateChanged` | `str, bool` | Widget ID, is floating |
| `floatingStarted` | `str` | Widget ID |
| `dockingCompleted` | `str` | Widget ID |
| `titlebarRefreshNeeded` | `str` | Widget ID |

---

### TabSelectorMonitor

```python
from widgetsystem.ui import TabSelectorMonitor

monitor = TabSelectorMonitor(dock_manager)
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `tabCountChanged` | `str, int` | Area ID, count |
| `singleTabArea` | `str` | Area with single tab |
| `multiTabArea` | `str` | Area with multiple tabs |

---

### ConfigurationPanel

```python
from widgetsystem.ui import ConfigurationPanel

panel = ConfigurationPanel(factories)
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `configChanged` | `str, str, Any` | Factory, key, value |
| `validationError` | `str, str` | Key, error message |
| `saveRequested` | - | Save button clicked |
| `resetRequested` | `str` | Reset factory name |

---

## QtAds Dock Signals

### CDockManager

```python
from PySide6QtAds import CDockManager

dock_manager = CDockManager(parent)
```

| Signal | Parameters | Description |
|--------|------------|-------------|
| `dockWidgetAdded` | `CDockWidget` | Widget added |
| `dockWidgetAboutToBeRemoved` | `CDockWidget` | Widget being removed |
| `dockWidgetRemoved` | `CDockWidget` | Widget removed |
| `floatingWidgetCreated` | `CFloatingDockContainer` | Float container created |
| `dockAreaCreated` | `CDockAreaWidget` | Dock area created |
| `stateChanged` | - | Layout state changed |

**Connection Example:**

```python
dock_manager.dockWidgetAdded.connect(self._on_dock_added)
dock_manager.floatingWidgetCreated.connect(self._on_float_created)
dock_manager.stateChanged.connect(self._save_layout)

def _on_dock_added(self, dock_widget: CDockWidget) -> None:
    # Setup custom titlebar
    titlebar = InlayTitleBar(dock_widget)
    dock_widget.setTitleBarWidget(titlebar)

def _on_float_created(self, container: CFloatingDockContainer) -> None:
    # Apply floating window style
    container.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
```

### CDockWidget

| Signal | Parameters | Description |
|--------|------------|-------------|
| `viewToggled` | `bool` | Visibility changed |
| `closed` | - | Widget closed |
| `topLevelChanged` | `bool` | Floating state changed |
| `visibilityChanged` | `bool` | Visibility changed |

---

## Custom Signal Patterns

### Defining Custom Signals

```python
from PySide6.QtCore import QObject, Signal

class MyComponent(QObject):
    """Component with custom signals."""

    # Signal definitions (class level)
    valueChanged = Signal(str)              # Single parameter
    rangeChanged = Signal(int, int)         # Multiple parameters
    dataUpdated = Signal(dict)              # Complex type
    errorOccurred = Signal(str, Exception)  # Multiple types
    completed = Signal()                     # No parameters

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def set_value(self, value: str) -> None:
        self._value = value
        self.valueChanged.emit(value)

    def process(self) -> None:
        try:
            # Do work...
            self.completed.emit()
        except Exception as e:
            self.errorOccurred.emit(str(e), e)
```

### Connecting Signals

```python
# Method 1: Direct connection
component.valueChanged.connect(self._on_value_changed)

# Method 2: Lambda (be careful with closures)
component.valueChanged.connect(lambda v: print(f"Value: {v}"))

# Method 3: Slot decorator
@Slot(str)
def _on_value_changed(self, value: str) -> None:
    print(f"Value changed to: {value}")

# Method 4: Connect to another signal (chaining)
component.valueChanged.connect(other_component.setValue)
```

### Disconnecting Signals

```python
# Disconnect specific slot
component.valueChanged.disconnect(self._on_value_changed)

# Disconnect all slots from signal
component.valueChanged.disconnect()

# Disconnect in destructor
def closeEvent(self, event: QCloseEvent) -> None:
    # Disconnect to prevent callbacks after destruction
    self.component.valueChanged.disconnect()
    super().closeEvent(event)
```

---

## Signal Connection Types

### Direct Connection

```python
# Same thread, immediate execution
component.signal.connect(slot, Qt.DirectConnection)
```

### Queued Connection

```python
# Cross-thread safe, queued in event loop
component.signal.connect(slot, Qt.QueuedConnection)
```

### Auto Connection (Default)

```python
# Qt decides based on thread affinity
component.signal.connect(slot, Qt.AutoConnection)
```

### Blocking Queued Connection

```python
# Cross-thread, blocks until slot completes
component.signal.connect(slot, Qt.BlockingQueuedConnection)
```

### Unique Connection

```python
# Prevent duplicate connections
component.signal.connect(slot, Qt.UniqueConnection)
```

---

## Event Handling

### Standard Qt Events

```python
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QWidget

class MyWidget(QWidget):
    def event(self, event: QEvent) -> bool:
        """Handle all events."""
        if event.type() == QEvent.Enter:
            self._on_mouse_enter()
        elif event.type() == QEvent.Leave:
            self._on_mouse_leave()
        return super().event(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        """Mouse entered widget."""
        self._highlight()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Mouse left widget."""
        self._unhighlight()
        super().leaveEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Widget resized."""
        self._update_layout()
        super().resizeEvent(event)
```

### Event Filters

```python
from PySide6.QtCore import QObject, QEvent

class EventFilter(QObject):
    """Custom event filter."""

    hoverEnter = Signal(QObject)
    hoverLeave = Signal(QObject)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.HoverEnter:
            self.hoverEnter.emit(watched)
        elif event.type() == QEvent.HoverLeave:
            self.hoverLeave.emit(watched)
        # Return False to let event propagate
        return False

# Usage
filter = EventFilter()
widget.installEventFilter(filter)
filter.hoverEnter.connect(lambda w: print(f"Hover: {w.objectName()}"))
```

---

## Best Practices

### 1. Signal Naming

```python
# Use past tense for events that happened
dataLoaded = Signal(dict)
fileOpened = Signal(str)
connectionClosed = Signal()

# Use present tense for state changes
valueChanging = Signal(str)  # About to change
valueChanged = Signal(str)   # Has changed

# Use Requested suffix for user actions
closeRequested = Signal()
saveRequested = Signal(str)
```

### 2. Parameter Design

```python
# Prefer simple types
countChanged = Signal(int)

# Use dict for complex data
dataUpdated = Signal(dict)

# Avoid large objects (copy cost)
# BAD: Signal(list[ComplexObject])
# GOOD: Signal(list[str])  # IDs only
```

### 3. Thread Safety

```python
# Emit from any thread, use QueuedConnection
worker_thread.resultReady.connect(
    main_window.update_ui,
    Qt.QueuedConnection
)
```

### 4. Memory Management

```python
def closeEvent(self, event: QCloseEvent) -> None:
    # Disconnect signals to prevent dangling references
    self.external_component.signal.disconnect(self._handler)
    super().closeEvent(event)
```

### 5. Documentation

```python
class MyClass(QObject):
    """Class description.

    Signals:
        valueChanged: Emitted when value changes.
            Parameters: new_value (str)
        errorOccurred: Emitted on error.
            Parameters: message (str), exception (Exception)
    """
    valueChanged = Signal(str)
    errorOccurred = Signal(str, Exception)
```

---

## Debugging Signals

### Enable Qt Debug Output

```python
import os
os.environ["QT_DEBUG_PLUGINS"] = "1"
```

### Log Signal Emissions

```python
from PySide6.QtCore import QObject

def debug_connect(signal, slot, name=""):
    """Wrapper for debugging connections."""
    def wrapper(*args, **kwargs):
        print(f"Signal {name}: {args}")
        return slot(*args, **kwargs)
    signal.connect(wrapper)

# Usage
debug_connect(component.valueChanged, handler, "valueChanged")
```

### Check Connections

```python
# Check if signal has connections
if component.receivers(component.valueChanged) > 0:
    print("Signal has connections")
```
