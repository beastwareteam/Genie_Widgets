---
description: Guidelines for creating and maintaining factory classes in WidgetSystem
applyTo: "**/factories/**/*.py"
---

# Factory Pattern Guidelines

## Purpose

Factories in WidgetSystem are responsible for creating UI components from JSON configuration files. They provide a consistent interface for loading, parsing, and instantiating components.

## Factory Structure

Every factory MUST follow this structure:

```python
from pathlib import Path
from typing import Any
import json

class ComponentFactory:
    """Factory for creating [Component] instances from JSON configuration.
    
    This factory loads component definitions from config/[component].json
    and creates instances based on the configuration.
    """
    
    def __init__(self, config_path: Path) -> None:
        """Initialize factory with configuration directory.
        
        Args:
            config_path: Path to the config directory containing [component].json
        """
        self.config_path = config_path
        self.config_file = config_path / "[component].json"
        self._cache: dict[str, Component] = {}
    
    def load_components(self) -> list[Component]:
        """Load all components from configuration file.
        
        Returns:
            List of Component instances
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If configuration is invalid JSON
        """
        if not self.config_file.exists():
            return []
        
        config_data = json.loads(
            self.config_file.read_text(encoding="utf-8")
        )
        
        return [
            self._create_component(item)
            for item in config_data.get("components", [])
        ]
    
    def _create_component(self, data: dict[str, Any]) -> Component:
        """Create a single component from configuration data.
        
        Args:
            data: Component configuration dictionary
            
        Returns:
            Component instance
        """
        # Implementation
```

## Required Methods

Every factory MUST implement:

1. `__init__(config_path: Path)` - Initialize with configuration directory
2. `load_<components>()` - Load all components from JSON
3. `_create_<component>(data: dict[str, Any])` - Create single component (private)

Optional methods:
- `list_<components>()` - List available components
- `get_<component>(component_id: str)` - Get component by ID (with caching)
- `reload()` - Reload configuration from disk

## Configuration Loading

- **Always** use `Path` objects for file paths
- **Always** specify encoding (`encoding="utf-8"`)
- **Always** handle missing files gracefully (return empty list)
- **Always** validate JSON structure before parsing

## Type Hints

- **All** factory methods must have complete type hints
- Use `dict[str, Any]` for configuration dictionaries
- Use `list[Component]` for component collections
- Use `Path` for file paths (never `str`)

## Error Handling

```python
def load_components(self) -> list[Component]:
    """Load components with proper error handling."""
    if not self.config_file.exists():
        # Don't error - return empty list
        return []
    
    try:
        config_data = json.loads(
            self.config_file.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as e:
        # Log error and return empty list
        print(f"Invalid JSON in {self.config_file}: {e}")
        return []
    
    # Process configuration
```

## Caching

Use `_cache` dictionary for frequently accessed components:

```python
def get_component(self, component_id: str) -> Component | None:
    """Get component by ID with caching."""
    if component_id in self._cache:
        return self._cache[component_id]
    
    # Load and cache
    component = self._load_component(component_id)
    if component:
        self._cache[component_id] = component
    
    return component
```

## Import Requirements

```python
# Required imports for all factories
from pathlib import Path
from typing import Any
import json

# Import from widgetsystem (absolute imports only)
from widgetsystem.factories.base import BaseFactory  # if exists
```

## Testing

Every factory MUST have tests in `tests/`:

```python
def test_factory_loads_config():
    """Test that factory loads configuration correctly."""
    factory = ComponentFactory(Path("config"))
    components = factory.load_components()
    
    assert isinstance(components, list)
    assert len(components) > 0
```

## Common Mistakes to Avoid

1. ❌ Using relative paths (`"../config"`) instead of `Path` objects
2. ❌ Not handling missing configuration files
3. ❌ Missing type hints on methods
4. ❌ Not using encoding when reading files
5. ❌ Hardcoding file paths instead of using `config_path`
6. ❌ Returning `None` instead of empty list when no data
7. ❌ Not validating configuration structure

## Example: Complete Factory

See `layout_factory.py`, `theme_factory.py`, or `menu_factory.py` for complete examples.
