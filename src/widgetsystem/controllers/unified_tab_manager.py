"""UnifiedTabManager - Central manager for all tab items.

Ensures every tab (dock, sub, nested) has the same features and
syncs configuration changes to persistence layer.
"""

from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTabWidget, QWidget

from widgetsystem.ui.unified_tab_item import UnifiedTabItem


class UnifiedTabManager(QObject):
    """Central manager for unified tab items.

    Responsibilities:
    - Creates UnifiedTabItem wrappers for all tabs
    - Syncs config changes to TabsFactory/persistence
    - Handles float requests (converts to dock widget)
    - Tracks tab hierarchy

    Signals:
        tabCreated: New tab created (tab_id, UnifiedTabItem)
        tabClosed: Tab was closed (tab_id)
        tabFloated: Tab was floated (tab_id, new_dock_id)
        configSyncRequested: Config needs saving (full_config)
    """

    tabCreated = Signal(str, object)  # tab_id, UnifiedTabItem
    tabClosed = Signal(str)  # tab_id
    tabFloated = Signal(str, str)  # tab_id, new_dock_id
    configSyncRequested = Signal(dict)  # full config to save

    _instance: "UnifiedTabManager | None" = None

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize UnifiedTabManager."""
        super().__init__(parent)

        # Registry: tab_id -> UnifiedTabItem
        self._tabs: dict[str, UnifiedTabItem] = {}

        # Hierarchy: tab_id -> parent_tab_id
        self._hierarchy: dict[str, str | None] = {}

        # Group registry: group_id -> list of tab_ids
        self._groups: dict[str, list[str]] = {}

        # Reference to dock controller for floating
        self._dock_controller: Any = None

        # Reference to tabs factory for persistence
        self._tabs_factory: Any = None

    @classmethod
    def instance(cls) -> "UnifiedTabManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_dock_controller(self, dock_controller: Any) -> None:
        """Set reference to dock controller.

        Args:
            dock_controller: DockController instance
        """
        self._dock_controller = dock_controller

    def set_tabs_factory(self, tabs_factory: Any) -> None:
        """Set reference to tabs factory.

        Args:
            tabs_factory: TabsFactory instance
        """
        self._tabs_factory = tabs_factory

    def create_tab(
        self,
        tab_id: str,
        title: str,
        content_widget: QWidget,
        parent_tab_widget: QTabWidget,
        tab_index: int,
        config: dict[str, Any] | None = None,
        parent_tab_id: str | None = None,
        group_id: str | None = None,
    ) -> UnifiedTabItem:
        """Create and register a unified tab item.

        Args:
            tab_id: Unique tab identifier
            title: Display title
            content_widget: Content widget
            parent_tab_widget: Parent QTabWidget
            tab_index: Index in parent
            config: Tab configuration
            parent_tab_id: Parent tab ID (for nested)
            group_id: Tab group ID

        Returns:
            Created UnifiedTabItem
        """
        # Create wrapper
        item = UnifiedTabItem(
            tab_id=tab_id,
            title=title,
            content_widget=content_widget,
            parent_tab_widget=parent_tab_widget,
            tab_index=tab_index,
            config=config,
            parent=self,
        )

        # Connect signals
        item.closed.connect(self._on_tab_closed)
        item.floatRequested.connect(self._on_float_requested)
        item.configChanged.connect(self._on_config_changed)

        # Register
        self._tabs[tab_id] = item
        self._hierarchy[tab_id] = parent_tab_id

        if group_id:
            if group_id not in self._groups:
                self._groups[group_id] = []
            self._groups[group_id].append(tab_id)

        # Connect parent QTabWidget close signal
        self._connect_tab_widget_signals(parent_tab_widget)

        self.tabCreated.emit(tab_id, item)
        return item

    def _connect_tab_widget_signals(self, tab_widget: QTabWidget) -> None:
        """Connect signals for a QTabWidget.

        Args:
            tab_widget: The tab widget
        """
        # Only connect once
        if hasattr(tab_widget, "_unified_signals_connected"):
            return

        tab_widget.tabCloseRequested.connect(
            lambda idx, tw=tab_widget: self._on_tab_close_requested(tw, idx)
        )
        tab_widget._unified_signals_connected = True  # type: ignore[attr-defined]

    def _on_tab_close_requested(self, tab_widget: QTabWidget, index: int) -> None:
        """Handle tab close request from QTabWidget.

        Args:
            tab_widget: The tab widget
            index: Tab index to close
        """
        widget = tab_widget.widget(index)
        if widget:
            item = widget.property("unified_tab_item")
            if item and isinstance(item, UnifiedTabItem):
                if item.is_closable:
                    item.close()

    def _on_tab_closed(self, tab_id: str) -> None:
        """Handle tab closed.

        Args:
            tab_id: Closed tab ID
        """
        # Remove from registry
        if tab_id in self._tabs:
            del self._tabs[tab_id]

        # Remove from hierarchy
        self._hierarchy.pop(tab_id, None)

        # Remove from groups
        for group_tabs in self._groups.values():
            if tab_id in group_tabs:
                group_tabs.remove(tab_id)

        # Sync to persistence
        self._sync_config()

        self.tabClosed.emit(tab_id)

    def _on_float_requested(self, tab_id: str) -> None:
        """Handle float request.

        Args:
            tab_id: Tab to float
        """
        if not self._dock_controller:
            return

        item = self._tabs.get(tab_id)
        if not item:
            return

        # Get content widget
        content = item.content_widget

        # Remove from current tab widget
        item.parent_tab_widget.removeTab(item.tab_index)

        # Create new dock widget
        dock_id = f"floated_{tab_id}"
        dock = self._dock_controller.create_panel(
            title=item.title,
            area="center",  # Float in center initially
            dock_id=dock_id,
            content_widget=content,
            closable=item.is_closable,
            movable=item.is_movable,
            floatable=True,
        )

        if dock:
            # Float it
            dock.setFloating(True)

            # Remove from our registry (now managed as dock)
            if tab_id in self._tabs:
                del self._tabs[tab_id]

            self.tabFloated.emit(tab_id, dock_id)

    def _on_config_changed(self, tab_id: str, config: dict[str, Any]) -> None:
        """Handle tab config change.

        Args:
            tab_id: Tab that changed (logged for debugging)
            config: New configuration (used during sync)
        """
        _ = tab_id, config  # Used indirectly via _sync_config
        self._sync_config()

    def _sync_config(self) -> None:
        """Sync current state to persistence layer."""
        if not self._tabs_factory:
            return

        # Build full config
        full_config = self.export_config()
        self.configSyncRequested.emit(full_config)

        # TODO: Actually save to tabs_factory
        # self._tabs_factory.update_from_runtime(full_config)

    def get_tab(self, tab_id: str) -> UnifiedTabItem | None:
        """Get tab by ID.

        Args:
            tab_id: Tab identifier

        Returns:
            UnifiedTabItem or None
        """
        return self._tabs.get(tab_id)

    def get_tabs_in_group(self, group_id: str) -> list[UnifiedTabItem]:
        """Get all tabs in a group.

        Args:
            group_id: Group identifier

        Returns:
            List of UnifiedTabItem
        """
        tab_ids = self._groups.get(group_id, [])
        return [self._tabs[tid] for tid in tab_ids if tid in self._tabs]

    def get_children(self, tab_id: str) -> list[UnifiedTabItem]:
        """Get child tabs.

        Args:
            tab_id: Parent tab ID

        Returns:
            List of child UnifiedTabItem
        """
        children = []
        for tid, parent in self._hierarchy.items():
            if parent == tab_id and tid in self._tabs:
                children.append(self._tabs[tid])
        return children

    def navigate_to(self, tab_id: str) -> bool:
        """Navigate to a tab (activating all parents).

        Args:
            tab_id: Tab to navigate to

        Returns:
            True if successful
        """
        item = self._tabs.get(tab_id)
        if not item:
            return False

        # Build path to root
        path = []
        current = tab_id
        while current:
            path.insert(0, current)
            current = self._hierarchy.get(current)

        # Activate each tab in path
        for tid in path:
            tab_item = self._tabs.get(tid)
            if tab_item:
                tab_item.activate()

        return True

    def close_all_in_group(self, group_id: str) -> int:
        """Close all tabs in a group.

        Args:
            group_id: Group to close

        Returns:
            Number of tabs closed
        """
        closed = 0
        tab_ids = list(self._groups.get(group_id, []))

        for tab_id in reversed(tab_ids):  # Close from end
            item = self._tabs.get(tab_id)
            if item and item.is_closable:
                if item.close():
                    closed += 1

        return closed

    def export_config(self) -> dict[str, Any]:
        """Export all tabs configuration.

        Returns:
            Full configuration dict
        """
        groups_config = {}

        for group_id, tab_ids in self._groups.items():
            tabs_config = []
            for tab_id in tab_ids:
                item = self._tabs.get(tab_id)
                if item:
                    tab_config = item.to_dict()
                    # Add children
                    children = self.get_children(tab_id)
                    if children:
                        tab_config["children"] = [c.to_dict() for c in children]
                    tabs_config.append(tab_config)

            groups_config[group_id] = {
                "id": group_id,
                "tabs": tabs_config,
            }

        return {"tab_groups": list(groups_config.values())}

    def list_all_tabs(self) -> list[str]:
        """List all registered tab IDs.

        Returns:
            List of tab IDs
        """
        return list(self._tabs.keys())


# Convenience function
def get_unified_tab_manager() -> UnifiedTabManager:
    """Get the global UnifiedTabManager instance."""
    return UnifiedTabManager.instance()
