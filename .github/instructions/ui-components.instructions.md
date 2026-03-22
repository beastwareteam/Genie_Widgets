---
description: Guidelines for creating UI components and visual layer elements
applyTo: |
  **/ui/**/*.py
  **/core/**/*.py
---

# UI Components Guidelines

## Purpose

UI components in WidgetSystem are PySide6 widgets that display and interact with data from factories. They follow the Model-View pattern with factories as models.

## Component Structure

Every UI component MUST:

1. Inherit from appropriate PySide6 widget base class
2. Accept factories/configuration in `__init__`
3. Implement proper type hints
4. Include comprehensive docstring
5. Use signals for inter-widget communication

## Basic Template

```python
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from widgetsystem.factories.component_factory import ComponentFactory

class ComponentWidget(QWidget):
    """Widget for displaying and interacting with [Component].
    
    This widget provides a visual interface for [specific functionality].
    It loads data from ComponentFactory and updates automatically.
    
    Signals:
        component_selected: Emitted when a component is selected
        component_changed: Emitted when component data changes
    """
    
    # Define signals at class level
    component_selected = Signal(str)  # component_id
    component_changed = Signal(object)  # component object
    
    def __init__(
        self,
        config_path: Path,
        parent: QWidget | None = None
    ) -> None:
        """Initialize component widget.
        
        Args:
            config_path: Path to configuration directory
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        # Initialize factories
        self.factory = ComponentFactory(config_path)
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self.refresh()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        # Add widgets to layout
    
    def refresh(self) -> None:
        """Reload data from factory and update display."""
        components = self.factory.load_components()
        # Update UI with new data
```

## Import Guidelines

```python
# Standard library
from pathlib import Path
from typing import Any

# PySide6 imports (organized by module)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

# WidgetSystem imports (absolute only)
from widgetsystem.factories.component_factory import ComponentFactory
from widgetsystem.ui.base import BaseWidget  # if exists
```

## Signals and Slots

Use PySide6 signals for communication:

```python
class ComponentWidget(QWidget):
    # Define signals at class level
    data_changed = Signal(object)
    selection_changed = Signal(str)
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        # Connect signals to slots
        self.data_changed.connect(self._on_data_changed)
    
    @Slot(object)
    def _on_data_changed(self, data: Any) -> None:
        """Handle data change event."""
        # Update UI
```

## Layout Management

Use layouts (never absolute positioning):

```python
def _setup_ui(self) -> None:
    """Setup UI with proper layout."""
    # Main layout
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(5)
    
    # Add widgets
    self.label = QLabel("Text")
    main_layout.addWidget(self.label)
    
    # Nested layouts
    button_layout = QHBoxLayout()
    button_layout.addWidget(QPushButton("OK"))
    button_layout.addWidget(QPushButton("Cancel"))
    main_layout.addLayout(button_layout)
```

## Type Hints

All UI components must have complete type hints:

```python
# ✅ CORRECT
def set_data(self, data: list[Component]) -> None:
    """Set component data."""
    
def get_selected(self) -> Component | None:
    """Get selected component."""
    
def _create_widget(self, item: Component) -> QWidget:
    """Create widget for component."""

# ❌ WRONG
def set_data(self, data):  # Missing type hints
    """Set component data."""
```

## Factory Integration

Components should:
1. Accept `config_path` in `__init__`
2. Create factories in `__init__`
3. Load data in `refresh()` method
4. Not cache data (factories handle caching)

```python
class ComponentViewer(QWidget):
    def __init__(self, config_path: Path) -> None:
        super().__init__()
        
        # Create factories (don't cache data)
        self.factory = ComponentFactory(config_path)
        
        # Setup and load
        self._setup_ui()
        self.refresh()
    
    def refresh(self) -> None:
        """Reload from factory."""
        components = self.factory.load_components()
        self._update_display(components)
```

## Configuration Panel Integration

Widgets that modify configuration should:
1. Emit signals when data changes
2. Provide `refresh()` method
3. Allow external updates

```python
class EditableList(QWidget):
    items_changed = Signal()  # Notify of changes
    
    def add_item(self, item: str) -> None:
        """Add item to list."""
        # Add to UI
        # Save to config
        self.items_changed.emit()
    
    def refresh(self) -> None:
        """Reload from configuration."""
        # Reload and update display
```

## Docking Integration

When using QtAds DockWidget:

```python
import PySide6QtAds as QtAds

def create_dock_widget(
    self,
    title: str,
    widget: QWidget,
) -> QtAds.CDockWidget:
    """Create a dock widget.
    
    Args:
        title: Dock widget title
        widget: Widget to dock
        
    Returns:
        Configured dock widget
    """
    dock = QtAds.CDockWidget(title)
    dock.setWidget(widget)
    dock.setMinimumSizeHintMode(
        QtAds.CDockWidget.MinimumSizeHintFromDockWidget
    )
    return dock
```

## Error Handling

Display user-friendly errors:

```python
from PySide6.QtWidgets import QMessageBox

def load_data(self) -> None:
    """Load data with error handling."""
    try:
        data = self.factory.load_components()
        self._update_display(data)
    except Exception as e:
        QMessageBox.critical(
            self,
            "Error Loading Data",
            f"Failed to load components:\n{str(e)}"
        )
```

## Common Mistakes to Avoid

1. ❌ Not calling `super().__init__()` in `__init__`
2. ❌ Using relative imports
3. ❌ Missing type hints on methods
4. ❌ Caching factory data instead of calling `refresh()`
5. ❌ Not using layouts (absolute positioning)
6. ❌ Missing parent parameter in `__init__`
7. ❌ Not connecting signals before emitting
8. ❌ Hardcoding paths instead of using `config_path`

## Testing UI Components

```python
def test_component_widget_creation():
    """Test widget can be created."""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    widget = ComponentWidget(Path("config"))
    assert widget is not None
    assert isinstance(widget, QWidget)
```

## Reference Examples

See these files for complete examples:
- `src/widgetsystem/ui/visual_layer.py` - Visual viewers
- `src/widgetsystem/ui/config_panel.py` - Configuration panel
- `src/widgetsystem/ui/visual_app.py` - Main application window
