"""Tab command controller for CLI automation and undo/redo support.

Provides the execution layer for tab operations, integrating with:
- DockController for tab widget access
- UndoRedoManager for reversible operations
- EnhancedTabWidget for tab manipulation

All operations are undoable and can be triggered via CLI or DnD.
"""

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from widgetsystem.core.tab_commands import (
    ActivateTabCommand,
    CloseTabCommand,
    FloatTabCommand,
    MoveTabCommand,
    NestTabCommand,
    TabState,
    UnnestTabCommand,
)
from widgetsystem.core.undo_redo import UndoRedoManager
from widgetsystem.ui.enhanced_tab_widget import EnhancedTabWidget

if TYPE_CHECKING:
    from widgetsystem.controllers.dock_controller import DockController


class TabCommandController(QObject):
    """Controller for tab CLI commands with undo support.

    Provides high-level tab operations that can be executed via:
    - CLI commands (CommandRegistry)
    - Drag & Drop operations
    - Keyboard shortcuts
    - Menu actions

    All operations are recorded for undo/redo.

    Signals:
        tabMoved: Tab moved (tab_id, container_id, index)
        tabNested: Tab nested (child_id, parent_id)
        tabUnnested: Tab unnested (tab_id)
        tabFloated: Tab floated (tab_id, dock_id)
        tabClosed: Tab closed (tab_id)
        tabRestored: Tab restored (tab_id)
        tabActivated: Tab activated (tab_id)
    """

    tabMoved = Signal(str, str, int)  # tab_id, container_id, index
    tabNested = Signal(str, str)  # child_id, parent_id
    tabUnnested = Signal(str)  # tab_id
    tabFloated = Signal(str, str)  # tab_id, dock_id
    tabClosed = Signal(str)  # tab_id
    tabRestored = Signal(str)  # tab_id
    tabActivated = Signal(str)  # tab_id

    def __init__(
        self,
        dock_controller: "DockController",
        undo_manager: UndoRedoManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._dock_controller = dock_controller
        self._undo_manager = undo_manager or UndoRedoManager()

        # Tab registry: tab_id -> (container_id, metadata)
        self._tab_registry: dict[str, dict[str, Any]] = {}

        # Build initial registry from dock controller
        self._rebuild_registry()

    def _rebuild_registry(self) -> None:
        """Rebuild tab registry from dock controller's tab widgets."""
        self._tab_registry.clear()
        for tab_widget in self._dock_controller.tab_widgets:
            container_id = tab_widget.objectName()
            for i in range(tab_widget.count()):
                tab_id = tab_widget.get_tab_id(i)
                if tab_id:
                    self._tab_registry[tab_id] = {
                        "container_id": container_id,
                        "index": i,
                        "widget": tab_widget,
                    }
                    # Recursively register nested tabs
                    widget = tab_widget.widget(i)
                    if isinstance(widget, EnhancedTabWidget):
                        self._register_nested_tabs(widget, tab_id)

    def _register_nested_tabs(
        self, tab_widget: EnhancedTabWidget, parent_tab_id: str
    ) -> None:
        """Recursively register nested tabs."""
        container_id = tab_widget.objectName()
        for i in range(tab_widget.count()):
            tab_id = tab_widget.get_tab_id(i)
            if tab_id:
                self._tab_registry[tab_id] = {
                    "container_id": container_id,
                    "index": i,
                    "widget": tab_widget,
                    "parent_tab_id": parent_tab_id,
                }
                widget = tab_widget.widget(i)
                if isinstance(widget, EnhancedTabWidget):
                    self._register_nested_tabs(widget, tab_id)

    # ------------------------------------------------------------------
    # Public API - High Level Operations
    # ------------------------------------------------------------------

    def move_tab(self, tab_id: str, target: str, index: int = -1) -> bool:
        """Move tab to target container at index.

        Args:
            tab_id: Tab to move
            target: Target container ID
            index: Position in target (-1 for end)

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        cmd = MoveTabCommand(tab_id, target, index, self)
        self._undo_manager.execute(cmd)
        return True

    def nest_tab(self, source_id: str, target_id: str) -> bool:
        """Nest source tab inside target tab.

        Args:
            source_id: Tab to nest
            target_id: Tab to nest into

        Returns:
            True if successful
        """
        if source_id not in self._tab_registry:
            return False
        if target_id not in self._tab_registry:
            return False
        if source_id == target_id:
            return False

        cmd = NestTabCommand(source_id, target_id, self)
        self._undo_manager.execute(cmd)
        return True

    def unnest_tab(self, tab_id: str) -> bool:
        """Unnest tab to parent level.

        Args:
            tab_id: Tab to unnest

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        info = self._tab_registry.get(tab_id, {})
        if not info.get("parent_tab_id"):
            return False  # Not nested

        cmd = UnnestTabCommand(tab_id, self)
        self._undo_manager.execute(cmd)
        return True

    def float_tab(self, tab_id: str) -> str | None:
        """Float tab to separate window.

        Args:
            tab_id: Tab to float

        Returns:
            New dock ID or None if failed
        """
        if tab_id not in self._tab_registry:
            return None

        cmd = FloatTabCommand(tab_id, self)
        self._undo_manager.execute(cmd)
        return cmd._float_dock_id

    def close_tab(self, tab_id: str) -> bool:
        """Close tab (undoable).

        Args:
            tab_id: Tab to close

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        info = self._tab_registry.get(tab_id, {})
        widget = info.get("widget")
        if widget:
            index = widget.get_tab_index_by_id(tab_id)
            if index >= 0 and not widget.is_tab_closable(index):
                return False  # Not closable

        cmd = CloseTabCommand(tab_id, self)
        self._undo_manager.execute(cmd)
        return True

    def activate_tab(self, tab_id: str) -> bool:
        """Activate (switch to) tab.

        Args:
            tab_id: Tab to activate

        Returns:
            True if successful
        """
        if tab_id not in self._tab_registry:
            return False

        cmd = ActivateTabCommand(tab_id, self)
        self._undo_manager.execute(cmd)
        return True

    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------

    def list_tabs(self, container_id: str | None = None) -> list[dict[str, Any]]:
        """List all tabs, optionally filtered by container."""
        tabs = []
        for tab_id, info in self._tab_registry.items():
            if container_id and info.get("container_id") != container_id:
                continue
            widget = info.get("widget")
            if widget:
                index = widget.get_tab_index_by_id(tab_id)
                if index >= 0:
                    tabs.append({
                        "tab_id": tab_id,
                        "title": widget.tabText(index),
                        "container_id": info.get("container_id"),
                        "index": index,
                        "closable": widget.is_tab_closable(index),
                        "movable": widget.is_tab_movable(index),
                        "floatable": widget.is_tab_floatable(index),
                        "parent_tab_id": info.get("parent_tab_id"),
                    })
        return tabs

    def get_tab_info(self, tab_id: str) -> dict[str, Any] | None:
        """Get detailed info about a tab."""
        tabs = self.list_tabs()
        for tab in tabs:
            if tab["tab_id"] == tab_id:
                return tab
        return None

    def get_tab_location(self, tab_id: str) -> dict[str, Any] | None:
        """Get current location of a tab."""
        info = self._tab_registry.get(tab_id)
        if not info:
            return None
        widget = info.get("widget")
        if widget:
            index = widget.get_tab_index_by_id(tab_id)
            return {
                "container_id": info.get("container_id"),
                "index": index,
                "parent_tab_id": info.get("parent_tab_id"),
            }
        return None

    def get_active_tab_id(self, container_id: str | None = None) -> str | None:
        """Get currently active tab ID."""
        for tab_widget in self._dock_controller.tab_widgets:
            if container_id and tab_widget.objectName() != container_id:
                continue
            index = tab_widget.currentIndex()
            if index >= 0:
                return tab_widget.get_tab_id(index)
        return None

    def list_containers(self) -> list[dict[str, Any]]:
        """List all tab containers."""
        containers = []
        for tab_widget in self._dock_controller.tab_widgets:
            containers.append({
                "container_id": tab_widget.objectName(),
                "tab_count": tab_widget.count(),
                "active_index": tab_widget.currentIndex(),
            })
        return containers

    def export_tab_state(self, tab_id: str) -> TabState | None:
        """Export complete tab state for undo."""
        info = self._tab_registry.get(tab_id)
        if not info:
            return None

        widget = info.get("widget")
        if not widget:
            return None

        index = widget.get_tab_index_by_id(tab_id)
        if index < 0:
            return None

        return TabState(
            tab_id=tab_id,
            title=widget.tabText(index),
            container_id=info.get("container_id", ""),
            index=index,
            closable=widget.is_tab_closable(index),
            movable=widget.is_tab_movable(index),
            floatable=widget.is_tab_floatable(index),
            parent_tab_id=info.get("parent_tab_id"),
        )

    # ------------------------------------------------------------------
    # Undo/Redo
    # ------------------------------------------------------------------

    def undo(self) -> bool:
        """Undo last command."""
        if self._undo_manager.can_undo():
            self._undo_manager.undo()
            self._rebuild_registry()
            return True
        return False

    def redo(self) -> bool:
        """Redo last undone command."""
        if self._undo_manager.can_redo():
            self._undo_manager.redo()
            self._rebuild_registry()
            return True
        return False

    # ------------------------------------------------------------------
    # Internal Operations (called by Commands)
    # ------------------------------------------------------------------

    def _do_move_tab(
        self, tab_id: str, target_container_id: str, target_index: int
    ) -> None:
        """Internal: Move tab to new position."""
        info = self._tab_registry.get(tab_id)
        if not info:
            return

        source_widget = info.get("widget")
        if not source_widget:
            return

        source_index = source_widget.get_tab_index_by_id(tab_id)
        if source_index < 0:
            return

        # Find target widget
        target_widget = None
        for tw in self._dock_controller.tab_widgets:
            if tw.objectName() == target_container_id:
                target_widget = tw
                break

        if not target_widget:
            return

        # Extract tab from source
        widget = source_widget.widget(source_index)
        title = source_widget.tabText(source_index)
        meta = source_widget._tab_meta.get(source_index, {})

        source_widget.removeTab(source_index)

        # Insert into target
        if target_index < 0:
            target_index = target_widget.count()

        target_widget.insertTab(
            target_index,
            widget,
            title,
            tab_id=tab_id,
            closable=meta.get("closable", True),
            movable=meta.get("movable", True),
            floatable=meta.get("floatable", True),
        )

        # Update registry
        self._tab_registry[tab_id] = {
            "container_id": target_container_id,
            "index": target_index,
            "widget": target_widget,
        }

        self.tabMoved.emit(tab_id, target_container_id, target_index)

    def _do_nest_tab(self, source_tab_id: str, target_tab_id: str) -> None:
        """Internal: Nest source tab into target tab."""
        source_info = self._tab_registry.get(source_tab_id)
        target_info = self._tab_registry.get(target_tab_id)

        if not source_info or not target_info:
            return

        source_widget = source_info.get("widget")
        target_widget = target_info.get("widget")

        if not source_widget or not target_widget:
            return

        source_index = source_widget.get_tab_index_by_id(source_tab_id)
        target_index = target_widget.get_tab_index_by_id(target_tab_id)

        if source_index < 0 or target_index < 0:
            return

        # Get source tab content
        content = source_widget.widget(source_index)
        title = source_widget.tabText(source_index)
        meta = source_widget._tab_meta.get(source_index, {})

        # Remove from source
        source_widget.removeTab(source_index)

        # Get or create nested tab widget in target
        target_content = target_widget.widget(target_index)
        if not isinstance(target_content, EnhancedTabWidget):
            # Create nested tab widget
            nested_widget = EnhancedTabWidget()
            nested_widget.setObjectName(f"nested_{target_tab_id}")
            nested_widget.setMinimumSize(100, 50)

            # Move existing content to first tab
            old_content = target_content
            target_widget.removeTab(target_index)

            nested_widget.addTab(
                old_content,
                target_widget.tabText(target_index) if target_index < target_widget.count() else "Content",
                tab_id=f"{target_tab_id}_content",
            )

            # Re-insert target with nested widget
            target_widget.insertTab(
                target_index,
                nested_widget,
                target_widget.tabText(target_index) if target_index < target_widget.count() else target_tab_id,
            )
            target_content = nested_widget

        # Add source to nested widget
        if isinstance(target_content, EnhancedTabWidget):
            target_content.addTab(
                content,
                title,
                tab_id=source_tab_id,
                closable=meta.get("closable", True),
                movable=meta.get("movable", True),
                floatable=meta.get("floatable", True),
            )

            # Update registry
            self._tab_registry[source_tab_id] = {
                "container_id": target_content.objectName(),
                "index": target_content.count() - 1,
                "widget": target_content,
                "parent_tab_id": target_tab_id,
            }

        self.tabNested.emit(source_tab_id, target_tab_id)

    def _do_unnest_tab(self, tab_id: str, original_state: TabState) -> None:
        """Internal: Restore tab to original position (undo nest)."""
        # Move back to original container at original index
        self._do_move_tab(tab_id, original_state.container_id, original_state.index)

    def _do_unnest_to_parent(self, tab_id: str) -> None:
        """Internal: Unnest tab to parent level."""
        info = self._tab_registry.get(tab_id)
        if not info:
            return

        parent_tab_id = info.get("parent_tab_id")
        if not parent_tab_id:
            return

        parent_info = self._tab_registry.get(parent_tab_id)
        if not parent_info:
            return

        parent_container = parent_info.get("container_id")
        parent_widget = parent_info.get("widget")
        parent_index = parent_widget.get_tab_index_by_id(parent_tab_id) if parent_widget else -1

        if parent_container and parent_index >= 0:
            self._do_move_tab(tab_id, parent_container, parent_index + 1)

        self.tabUnnested.emit(tab_id)

    def _do_float_tab(self, tab_id: str) -> str | None:
        """Internal: Float tab to new dock window."""
        info = self._tab_registry.get(tab_id)
        if not info:
            return None

        widget = info.get("widget")
        if not widget:
            return None

        index = widget.get_tab_index_by_id(tab_id)
        if index < 0:
            return None

        # Trigger float via EnhancedTabWidget
        widget._on_float_requested(index, widget.mapToGlobal(widget.rect().center()))

        # The dock_controller handles the rest and emits tabFloated
        # We need to find the new dock ID
        # This is set by dock_controller._on_tab_floated
        dock_id = f"floated_{tab_id}"

        self.tabFloated.emit(tab_id, dock_id)
        return dock_id

    def _do_dock_tab(
        self, tab_id: str, float_dock_id: str, container_id: str, index: int
    ) -> None:
        """Internal: Dock a floated tab back."""
        # Close the float dock and move tab back
        dock = self._dock_controller.find_dock(float_dock_id)
        if dock:
            dock.closeDockWidget()

        self._do_move_tab(tab_id, container_id, index)

    def _do_close_tab(self, tab_id: str) -> None:
        """Internal: Close tab."""
        info = self._tab_registry.get(tab_id)
        if not info:
            return

        widget = info.get("widget")
        if not widget:
            return

        index = widget.get_tab_index_by_id(tab_id)
        if index >= 0:
            widget.removeTab(index)
            del self._tab_registry[tab_id]

        self.tabClosed.emit(tab_id)

    def _do_restore_tab(self, state: TabState) -> None:
        """Internal: Restore a closed tab."""
        # Find target container
        target_widget = None
        for tw in self._dock_controller.tab_widgets:
            if tw.objectName() == state.container_id:
                target_widget = tw
                break

        if not target_widget:
            return

        # Create placeholder widget
        content = QWidget()
        content.setMinimumSize(100, 50)

        # Insert tab
        target_widget.insertTab(
            state.index,
            content,
            state.title,
            tab_id=state.tab_id,
            closable=state.closable,
            movable=state.movable,
            floatable=state.floatable,
        )

        # Update registry
        self._tab_registry[state.tab_id] = {
            "container_id": state.container_id,
            "index": state.index,
            "widget": target_widget,
            "parent_tab_id": state.parent_tab_id,
        }

        self.tabRestored.emit(state.tab_id)

    def _do_activate_tab(self, tab_id: str) -> None:
        """Internal: Activate tab."""
        info = self._tab_registry.get(tab_id)
        if not info:
            return

        widget = info.get("widget")
        if not widget:
            return

        index = widget.get_tab_index_by_id(tab_id)
        if index >= 0:
            widget.setCurrentIndex(index)

        self.tabActivated.emit(tab_id)
