---
description: Guidelines for writing tests in WidgetSystem
applyTo: "**/tests/**/*.py"
---

# Testing Guidelines

## Test Organization

Tests are organized by functionality:

```
tests/
├── __init__.py
├── verify_setup.py           # Setup verification
├── test_full_system.py        # Integration tests
├── test_visual_layer.py       # UI component tests
├── test_factories.py          # Factory tests (if exists)
└── test_*.py                  # Additional test modules
```

## Test Structure

Every test file should follow this structure:

```python
"""Test module for [Component] functionality."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
import pytest

from widgetsystem.component import Component


def test_component_basic_functionality():
    """Test basic component functionality.
    
    This test verifies that [specific behavior].
    """
    # Arrange
    component = Component()
    
    # Act
    result = component.do_something()
    
    # Assert
    assert result is not None
    assert isinstance(result, ExpectedType)


def test_component_error_handling():
    """Test component handles errors correctly."""
    component = Component()
    
    with pytest.raises(ValueError):
        component.invalid_operation()
```

## Test Naming

- **Test files**: `test_<module>.py` (e.g., `test_layout_factory.py`)
- **Test functions**: `test_<what>_<condition>()` (e.g., `test_factory_loads_config_successfully()`)
- **Test classes**: `Test<Component>` (e.g., `TestLayoutFactory`)

## Factory Testing

Test factories thoroughly:

```python
def test_factory_loads_configuration():
    """Test factory loads configuration from JSON."""
    factory = ComponentFactory(Path("config"))
    components = factory.load_components()
    
    assert isinstance(components, list)
    assert len(components) > 0
    
    # Verify first component
    first = components[0]
    assert hasattr(first, "id")
    assert hasattr(first, "name")


def test_factory_handles_missing_file():
    """Test factory handles missing configuration gracefully."""
    factory = ComponentFactory(Path("nonexistent"))
    components = factory.load_components()
    
    # Should return empty list, not error
    assert isinstance(components, list)
    assert len(components) == 0


def test_factory_validates_json_structure():
    """Test factory validates JSON structure."""
    # This would use a temporary config file
    # with invalid structure
```

## UI Component Testing

Test UI components with QApplication:

```python
def test_widget_creation():
    """Test widget can be created and initialized."""
    # Get or create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    widget = ComponentWidget(Path("config"))
    
    assert widget is not None
    assert isinstance(widget, QWidget)
    assert widget.factory is not None


def test_widget_refresh():
    """Test widget refresh updates display."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    widget = ComponentWidget(Path("config"))
    initial_count = widget.get_item_count()
    
    # Modify data
    widget.refresh()
    
    new_count = widget.get_item_count()
    assert new_count >= 0
```

## Integration Testing

Test complete workflows:

```python
def test_full_application_startup():
    """Test application can start and initialize all components."""
    app = QApplication(sys.argv)
    
    # Initialize all factories
    config_path = Path("config")
    layout_factory = LayoutFactory(config_path)
    theme_factory = ThemeFactory(config_path)
    
    # Verify factories load data
    assert len(layout_factory.load_layouts()) > 0
    assert len(theme_factory.load_themes()) > 0
    
    # Create main window
    window = MainWindow()
    assert window is not None
```

## Configuration Testing

Test configuration loading:

```python
def test_config_file_exists():
    """Test required configuration files exist."""
    config_path = Path("config")
    
    assert (config_path / "layouts.json").exists()
    assert (config_path / "themes.json").exists()
    assert (config_path / "menus.json").exists()


def test_config_json_valid():
    """Test configuration files are valid JSON."""
    import json
    
    config_file = Path("config/layouts.json")
    
    # Should not raise JSONDecodeError
    config_data = json.loads(
        config_file.read_text(encoding="utf-8")
    )
    
    assert isinstance(config_data, dict)
```

## Test Fixtures

Use pytest fixtures for common setup:

```python
import pytest
from pathlib import Path

@pytest.fixture
def config_path():
    """Provide config directory path."""
    return Path("config")


@pytest.fixture
def layout_factory(config_path):
    """Provide initialized LayoutFactory."""
    from widgetsystem.factories.layout_factory import LayoutFactory
    return LayoutFactory(config_path)


def test_with_fixture(layout_factory):
    """Test using fixture."""
    layouts = layout_factory.load_layouts()
    assert len(layouts) > 0
```

## Test Data

For tests requiring specific data:

```python
@pytest.fixture
def sample_config():
    """Provide sample configuration data."""
    return {
        "id": "test_item",
        "name": "Test Item",
        "properties": {
            "enabled": True
        }
    }


def test_with_sample_data(sample_config):
    """Test component with sample data."""
    component = Component(sample_config)
    assert component.id == "test_item"
```

## Assertions

Use descriptive assertions:

```python
# ✅ GOOD - Descriptive
assert len(components) > 0, "Should load at least one component"
assert component.name == "Test", f"Expected 'Test', got '{component.name}'"

# ❌ BAD - Not descriptive
assert len(components) > 0
assert component.name == "Test"
```

## Test Output

Use print statements for test progress:

```python
def test_complex_operation():
    """Test complex operation with progress output."""
    print("\nTesting complex operation...")
    print("  Step 1: Initialize")
    component = Component()
    
    print("  Step 2: Load data")
    component.load_data()
    
    print("  Step 3: Process")
    result = component.process()
    
    print("  ✅ All steps completed")
    assert result is not None
```

## Error Testing

Test error conditions:

```python
def test_handles_invalid_input():
    """Test component handles invalid input gracefully."""
    factory = ComponentFactory(Path("config"))
    
    # Should not raise exception
    result = factory.get_component("nonexistent_id")
    assert result is None


def test_raises_on_invalid_config():
    """Test raises exception for invalid configuration."""
    with pytest.raises(ValueError) as exc_info:
        Component(invalid_config={})
    
    assert "Invalid configuration" in str(exc_info.value)
```

## Coverage Goals

- **Factories**: All public methods tested
- **UI Components**: Creation, refresh, and main functionality
- **Integration**: Complete workflows from start to finish
- **Edge Cases**: Missing files, invalid data, empty configurations

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_full_system.py

# Run with verbose output
pytest -v tests/

# Run with print output
pytest -s tests/

# Run specific test
pytest tests/test_full_system.py::test_factory_loads_config
```

## Common Mistakes to Avoid

1. ❌ Not creating QApplication for widget tests
2. ❌ Testing implementation details instead of behavior
3. ❌ Not testing error conditions
4. ❌ Hardcoding paths instead of using `Path("config")`
5. ❌ Not using fixtures for common setup
6. ❌ Missing assertions
7. ❌ Tests that depend on external state
8. ❌ Not cleaning up resources (files, widgets)

## Test Documentation

Every test should have a docstring explaining:
1. What is being tested
2. Expected behavior
3. Why the test is important (if not obvious)

```python
def test_factory_caching():
    """Test factory caches loaded components.
    
    This test verifies that repeated calls to load_components()
    return cached data instead of re-reading from disk, which
    improves performance especially with large configurations.
    """
```

## Reference Examples

See these files for complete examples:
- `tests/verify_setup.py` - Setup verification pattern
- `tests/test_full_system.py` - Integration testing
- `tests/test_visual_layer.py` - UI component testing
