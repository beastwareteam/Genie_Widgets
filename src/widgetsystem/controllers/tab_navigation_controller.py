"""TabNavigationController - Manages nested tab navigation and state.

Provides programmatic control over nested QTabWidget hierarchies,
including navigation, activation, and state tracking.
"""

from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QTabWidget, QWidget


class TabNavigationController(QObject):
    """Controller for managing nested tab navigation.

    Tracks QTabWidget hierarchies and provides methods to:
    - Navigate to tabs by ID (including nested)
    - Get/set active tab paths
    - Track tab state changes
    - Handle tab close requests

    Signals:
        tabActivated: Emitted when tab is activated (tab_id, tab_path)
        tabClosed: Emitted when tab is closed (tab_id)
        tabAdded: Emitted when tab is added (tab_id, parent_id)
        navigationChanged: Emitted when navigation path changes (path)
    """

    tabActivated = Signal(str, list)  # tab_id, path as list of ids
    tabClosed = Signal(str)  # tab_id
    tabAdded = Signal(str, str)  # tab_id, parent_id
    navigationChanged = Signal(list)  # path as list of ids

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize TabNavigationController."""
        super().__init__(parent)

        # Registry: tab_id -> (QTabWidget parent, tab index, QWidget content)
        self._tab_registry: dict[str, tuple[QTabWidget, int, QWidget]] = {}

        # Hierarchy: tab_id -> parent_tab_id (None for root)
        self._tab_hierarchy: dict[str, str | None] = {}

        # QTabWidget -> group_id mapping
        self._tabwidget_to_group: dict[int, str] = {}

        # Track active path
        self._active_path: list[str] = []

    def register_tab(
        self,
        tab_id: str,
        parent_widget: QTabWidget,
        tab_index: int,
        content_widget: QWidget,
        parent_tab_id: str | None = None,
    ) -> None:
        """Register a tab with the controller.

        Args:
            tab_id: Unique tab identifier
            parent_widget: QTabWidget containing this tab
            tab_index: Index of tab in parent
            content_widget: The widget content of the tab
            parent_tab_id: ID of parent tab (for nested tabs)
        """
        self._tab_registry[tab_id] = (parent_widget, tab_index, content_widget)
        self._tab_hierarchy[tab_id] = parent_tab_id

        # Connect to tab changes
        parent_widget.currentChanged.connect(
            lambda idx, tw=parent_widget: self._on_tab_changed(tw, idx)
        )

        # Connect to tab close if closable
        if parent_widget.tabsClosable():
            parent_widget.tabCloseRequested.connect(
                lambda idx, tw=parent_widget: self._on_tab_close_requested(tw, idx)
            )

        self.tabAdded.emit(tab_id, parent_tab_id or "")

    def register_tab_widget(self, tab_widget: QTabWidget, group_id: str) -> None:
        """Register a QTabWidget as a tab group.

        Args:
            tab_widget: The QTabWidget to register
            group_id: Group identifier
        """
        self._tabwidget_to_group[id(tab_widget)] = group_id

    def unregister_tab(self, tab_id: str) -> bool:
        """Unregister a tab.

        Args:
            tab_id: Tab to unregister

        Returns:
            True if unregistered
        """
        if tab_id in self._tab_registry:
            del self._tab_registry[tab_id]
            self._tab_hierarchy.pop(tab_id, None)
            return True
        return False

    def navigate_to(self, tab_id: str) -> bool:
        """Navigate to a tab by ID, activating all parent tabs.

        Args:
            tab_id: Tab to navigate to

        Returns:
            True if navigation successful
        """
        if tab_id not in self._tab_registry:
            return False

        # Build path from root to target
        path = self._build_path_to(tab_id)

        # Activate each tab in path
        for tid in path:
            if tid in self._tab_registry:
                parent_widget, tab_index, _ = self._tab_registry[tid]
                parent_widget.setCurrentIndex(tab_index)

        self._active_path = path
        self.navigationChanged.emit(path)
        self.tabActivated.emit(tab_id, path)

        return True

    def get_active_path(self) -> list[str]:
        """Get current active tab path.

        Returns:
            List of tab IDs from root to active leaf
        """
        return list(self._active_path)

    def get_active_tab(self) -> str | None:
        """Get currently active leaf tab ID.

        Returns:
            Active tab ID or None
        """
        return self._active_path[-1] if self._active_path else None

    def get_tab_widget(self, tab_id: str) -> QWidget | None:
        """Get content widget for a tab.

        Args:
            tab_id: Tab identifier

        Returns:
            Content QWidget or None
        """
        if tab_id in self._tab_registry:
            return self._tab_registry[tab_id][2]
        return None

    def get_parent_tab(self, tab_id: str) -> str | None:
        """Get parent tab ID.

        Args:
            tab_id: Tab to get parent of

        Returns:
            Parent tab ID or None for root tabs
        """
        return self._tab_hierarchy.get(tab_id)

    def get_children(self, tab_id: str) -> list[str]:
        """Get child tab IDs.

        Args:
            tab_id: Parent tab ID

        Returns:
            List of child tab IDs
        """
        return [
            tid for tid, parent in self._tab_hierarchy.items()
            if parent == tab_id
        ]

    def get_siblings(self, tab_id: str) -> list[str]:
        """Get sibling tab IDs (same parent).

        Args:
            tab_id: Tab to get siblings of

        Returns:
            List of sibling tab IDs (including self)
        """
        parent = self._tab_hierarchy.get(tab_id)
        return [
            tid for tid, p in self._tab_hierarchy.items()
            if p == parent
        ]

    def set_tab_enabled(self, tab_id: str, enabled: bool) -> bool:
        """Enable/disable a tab.

        Args:
            tab_id: Tab to modify
            enabled: Enable state

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        parent_widget, tab_index, _ = self._tab_registry[tab_id]
        parent_widget.setTabEnabled(tab_index, enabled)
        return True

    def set_tab_visible(self, tab_id: str, visible: bool) -> bool:
        """Show/hide a tab.

        Args:
            tab_id: Tab to modify
            visible: Visibility state

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        parent_widget, tab_index, _ = self._tab_registry[tab_id]
        parent_widget.setTabVisible(tab_index, visible)
        return True

    def set_tab_text(self, tab_id: str, text: str) -> bool:
        """Set tab text.

        Args:
            tab_id: Tab to modify
            text: New tab text

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        parent_widget, tab_index, _ = self._tab_registry[tab_id]
        parent_widget.setTabText(tab_index, text)
        return True

    def set_tab_icon(self, tab_id: str, icon: QIcon) -> bool:
        """Set tab icon.

        Args:
            tab_id: Tab to modify
            icon: New icon

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        parent_widget, tab_index, _ = self._tab_registry[tab_id]
        parent_widget.setTabIcon(tab_index, icon)
        return True

    def set_tab_tooltip(self, tab_id: str, tooltip: str) -> bool:
        """Set tab tooltip.

        Args:
            tab_id: Tab to modify
            tooltip: Tooltip text

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        parent_widget, tab_index, _ = self._tab_registry[tab_id]
        parent_widget.setTabToolTip(tab_index, tooltip)
        return True

    def close_tab(self, tab_id: str) -> bool:
        """Programmatically close a tab.

        Args:
            tab_id: Tab to close

        Returns:
            True if closed
        """
        if tab_id not in self._tab_registry:
            return False

        parent_widget, tab_index, _ = self._tab_registry[tab_id]
        parent_widget.removeTab(tab_index)

        # Update indices for tabs after removed one
        self._reindex_tabs(parent_widget, tab_index)

        self.unregister_tab(tab_id)
        self.tabClosed.emit(tab_id)

        return True

    def list_all_tabs(self) -> list[str]:
        """List all registered tab IDs.

        Returns:
            List of tab IDs
        """
        return list(self._tab_registry.keys())

    def list_root_tabs(self) -> list[str]:
        """List root-level tab IDs (no parent).

        Returns:
            List of root tab IDs
        """
        return [
            tid for tid, parent in self._tab_hierarchy.items()
            if parent is None
        ]

    def _build_path_to(self, tab_id: str) -> list[str]:
        """Build path from root to target tab.

        Args:
            tab_id: Target tab

        Returns:
            List of tab IDs from root to target
        """
        path: list[str] = []
        current = tab_id

        while current:
            path.insert(0, current)
            current = self._tab_hierarchy.get(current)  # type: ignore[assignment]

        return path

    def _on_tab_changed(self, tab_widget: QTabWidget, index: int) -> None:
        """Handle tab change in a QTabWidget.

        Args:
            tab_widget: The QTabWidget that changed
            index: New active index
        """
        # Find the tab_id for this index
        for tid, (tw, idx, _) in self._tab_registry.items():
            if tw is tab_widget and idx == index:
                path = self._build_path_to(tid)
                self._active_path = path
                self.navigationChanged.emit(path)
                self.tabActivated.emit(tid, path)
                break

    def _on_tab_close_requested(self, tab_widget: QTabWidget, index: int) -> None:
        """Handle tab close request.

        Args:
            tab_widget: The QTabWidget
            index: Tab index to close
        """
        # Find the tab_id for this index
        for tid, (tw, idx, _) in list(self._tab_registry.items()):
            if tw is tab_widget and idx == index:
                self.close_tab(tid)
                break

    def _reindex_tabs(self, tab_widget: QTabWidget, removed_index: int) -> None:
        """Update indices after tab removal.

        Args:
            tab_widget: The QTabWidget
            removed_index: Index that was removed
        """
        for tid, (tw, idx, widget) in list(self._tab_registry.items()):
            if tw is tab_widget and idx > removed_index:
                # Decrement index for tabs after removed
                self._tab_registry[tid] = (tw, idx - 1, widget)
