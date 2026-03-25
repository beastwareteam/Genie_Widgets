"""ComponentRegistry - Registry for tab content widgets.

Maps component IDs from tabs.json to actual QWidget classes/factories.
Supports lazy loading and custom widget creation.
"""

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


# Type alias for component factory functions
ComponentFactory = Callable[[dict[str, Any]], QWidget]


class ComponentRegistry:
    """Registry for mapping component IDs to widget factories.

    Usage:
        registry = ComponentRegistry()
        registry.register("charts", ChartsWidget)
        registry.register("tables", lambda config: TablesWidget(config))

        widget = registry.create("charts", {"title": "Sales"})
    """

    _instance: "ComponentRegistry | None" = None

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._factories: dict[str, ComponentFactory] = {}
        self._default_factory: ComponentFactory | None = None

    @classmethod
    def instance(cls) -> "ComponentRegistry":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._register_defaults()
        return cls._instance

    def _register_defaults(self) -> None:
        """Register default placeholder components."""
        self.set_default_factory(self._create_placeholder)

    def register(
        self,
        component_id: str,
        factory: type[QWidget] | ComponentFactory,
    ) -> None:
        """Register a component factory.

        Args:
            component_id: Unique component identifier (matches tabs.json)
            factory: Widget class or callable that creates widgets
        """
        if isinstance(factory, type):
            # Wrap class in factory function
            widget_class = factory
            self._factories[component_id] = lambda config: widget_class()
        else:
            self._factories[component_id] = factory

    def register_class(
        self,
        component_id: str,
        widget_class: type[QWidget],
        **default_kwargs: Any,
    ) -> None:
        """Register a widget class with default kwargs.

        Args:
            component_id: Unique component identifier
            widget_class: Widget class to instantiate
            **default_kwargs: Default arguments passed to constructor
        """
        def factory(config: dict[str, Any]) -> QWidget:
            merged = {**default_kwargs, **config}
            return widget_class(**merged)

        self._factories[component_id] = factory

    def unregister(self, component_id: str) -> bool:
        """Remove a component from registry.

        Args:
            component_id: Component to remove

        Returns:
            True if removed, False if not found
        """
        if component_id in self._factories:
            del self._factories[component_id]
            return True
        return False

    def set_default_factory(self, factory: ComponentFactory) -> None:
        """Set factory for unknown component IDs.

        Args:
            factory: Factory function for unknown components
        """
        self._default_factory = factory

    def create(
        self,
        component_id: str,
        config: dict[str, Any] | None = None,
    ) -> QWidget:
        """Create widget instance for component ID.

        Args:
            component_id: Component identifier from tabs.json
            config: Optional configuration passed to factory

        Returns:
            Created QWidget instance
        """
        config = config or {}
        config["component_id"] = component_id

        factory = self._factories.get(component_id)
        if factory:
            return factory(config)

        if self._default_factory:
            return self._default_factory(config)

        return self._create_placeholder(config)

    def has_component(self, component_id: str) -> bool:
        """Check if component is registered.

        Args:
            component_id: Component to check

        Returns:
            True if registered
        """
        return component_id in self._factories

    def list_components(self) -> list[str]:
        """List all registered component IDs.

        Returns:
            List of component IDs
        """
        return list(self._factories.keys())

    @staticmethod
    def _create_placeholder(config: dict[str, Any]) -> QWidget:
        """Create placeholder widget for unregistered components.

        Args:
            config: Configuration dict with component_id

        Returns:
            Placeholder widget with label
        """
        component_id = config.get("component_id", "unknown")
        title = config.get("title", component_id)

        widget = QWidget()
        widget.setObjectName(f"placeholder_{component_id}")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(f"Component: {title}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                font-style: italic;
                padding: 40px;
                border: 2px dashed #444444;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.02);
            }
        """)
        layout.addWidget(label)

        return widget


# Convenience function
def get_component_registry() -> ComponentRegistry:
    """Get the global ComponentRegistry instance."""
    return ComponentRegistry.instance()
