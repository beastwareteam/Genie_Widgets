"""EnhancedTabWidget - QTabWidget with full dock-like features.

Provides the same functionality as QtAds dock tabs:
- Drag & Drop reordering
- Drag to float (extract tab to window)
- Drag to other tab widgets (cross-container)
- Drag INTO tab for nesting (folder-like behavior)
- Tab close with closable flag per tab
- Context menu with all actions
- Visual feedback during drag with drop zone highlighting
"""

from enum import Enum
from typing import Any

from PySide6.QtCore import QMimeData, QPoint, Qt, QRect, Signal
from PySide6.QtGui import QDrag, QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QTabBar, QTabWidget, QWidget

from widgetsystem.core.tab_hierarchy import get_hierarchy_validator
from widgetsystem.core.undo_redo import Command, UndoRedoManager


class DropZone(Enum):
    """Drop zone types for tab drag & drop."""

    NONE = "none"  # No valid drop zone
    BEFORE = "before"  # Insert before target tab
    INTO = "into"  # Nest into target tab
    AFTER = "after"  # Insert after target tab
    END = "end"  # Append at end


class CloseTabUndoCommand(Command):
    """Undoable command for closing/deleting a tab.

    Stores all information needed to restore the tab on undo.
    """

    def __init__(
        self,
        tab_widget: "EnhancedTabWidget",
        index: int,
    ) -> None:
        tab_id = tab_widget.get_tab_id(index) or "unknown"
        super().__init__(f"Close {tab_id}")

        self._tab_widget = tab_widget
        self._tab_id = tab_id
        self._label = tab_widget.tabText(index)
        self._meta = tab_widget._tab_meta.get(index, {}).copy()
        self._original_index = index

        # Store the content widget (will be kept alive by this command)
        self._content: QWidget | None = tab_widget.widget(index)

        # For nested tabs, store the entire structure
        self._is_container = isinstance(self._content, EnhancedTabWidget)
        self._nested_config: list[dict] = []
        if self._is_container and isinstance(self._content, EnhancedTabWidget):
            self._nested_config = self._content.export_config()

        self._executed = False

    def execute(self) -> None:
        """Execute the close operation."""
        if self._executed:
            return
        self._do_close()
        self._executed = True

    def redo(self) -> None:
        """Redo the close operation."""
        if self._executed:
            return
        self._do_close()
        self._executed = True

    def _do_close(self) -> None:
        """Perform the actual close."""
        idx = self._tab_widget.get_tab_index_by_id(self._tab_id)
        if idx >= 0:
            # Get content before removal (to keep it alive)
            self._content = self._tab_widget.widget(idx)
            # Remove tab but keep content widget
            self._tab_widget._remove_tab_keep_widget(idx)

    def undo(self) -> None:
        """Undo the close - restore the tab."""
        if not self._executed:
            return

        if self._content is None:
            self._executed = False
            return

        # Restore at original position (or end if out of bounds)
        insert_idx = min(self._original_index, self._tab_widget.count())

        self._tab_widget.insertTab(
            insert_idx,
            self._content,
            self._label,
            tab_id=self._tab_id,
            closable=self._meta.get("closable", True),
            movable=self._meta.get("movable", True),
            floatable=self._meta.get("floatable", True),
        )

        self._executed = False


class NestTabUndoCommand(Command):
    """Undoable command for nesting a tab into another.

    SIMPLIFIED: Only tracks what's needed, recalculates indices at undo time.
    """

    def __init__(
        self,
        source_widget: "EnhancedTabWidget",
        source_index: int,
        target_widget: "EnhancedTabWidget",
        target_index: int,
    ) -> None:
        source_id = source_widget.get_tab_id(source_index) or "unknown"
        target_id = target_widget.get_tab_id(target_index) or "unknown"
        super().__init__(f"Nest {source_id} into {target_id}")

        # Store IDs and widgets (not indices - they change)
        self._source_widget = source_widget
        self._source_tab_id = source_id
        self._source_label = source_widget.tabText(source_index)
        self._source_meta = source_widget._tab_meta.get(source_index, {}).copy()

        self._target_widget = target_widget
        self._target_tab_id = target_id
        self._target_label = target_widget.tabText(target_index)
        self._target_meta = target_widget._tab_meta.get(target_index, {}).copy()
        self._target_was_container = isinstance(target_widget.widget(target_index), EnhancedTabWidget)

        # Store original indices for ordering restoration
        self._original_source_index = source_index
        self._original_target_index = target_index

        self._executed = False

    def execute(self) -> None:
        """Execute the nesting operation."""
        if self._executed:
            return
        self._do_nest()
        self._executed = True

    def redo(self) -> None:
        """Redo the nesting operation."""
        if self._executed:
            return
        self._do_nest()
        self._executed = True

    def _do_nest(self) -> None:
        """Perform the actual nesting."""
        # Find current indices by ID
        source_idx = self._source_widget.get_tab_index_by_id(self._source_tab_id)
        target_idx = self._target_widget.get_tab_index_by_id(self._target_tab_id)

        if source_idx >= 0 and target_idx >= 0:
            self._target_widget._nest_tab_into_internal(
                self._source_widget, source_idx, target_idx
            )

    def undo(self) -> None:
        """Undo the nesting - restore original state."""
        if not self._executed:
            return

        # Find the container by target ID
        target_idx = self._target_widget.get_tab_index_by_id(self._target_tab_id)
        if target_idx < 0:
            self._executed = False
            return

        container = self._target_widget.widget(target_idx)
        if not isinstance(container, EnhancedTabWidget):
            self._executed = False
            return

        # Extract source from container
        source_nested_idx = container.get_tab_index_by_id(self._source_tab_id)
        source_content = None
        if source_nested_idx >= 0:
            source_content = container.widget(source_nested_idx)
            container.removeTab(source_nested_idx)

        # If target was NOT a container before, restore it
        if not self._target_was_container:
            # Get target's original content
            content_tab_id = f"{self._target_tab_id}_content"
            content_idx = container.get_tab_index_by_id(content_tab_id)

            target_content = None
            if content_idx >= 0:
                target_content = container.widget(content_idx)
                container.removeTab(content_idx)
            elif container.count() > 0:
                target_content = container.widget(0)
                container.removeTab(0)

            # Remove container, restore target as normal tab
            self._target_widget.removeTab(target_idx)

            if target_content:
                insert_idx = min(self._original_target_index, self._target_widget.count())
                self._target_widget.insertTab(
                    insert_idx,
                    target_content,
                    self._target_label,
                    tab_id=self._target_tab_id,
                    closable=self._target_meta.get("closable", True),
                    movable=self._target_meta.get("movable", True),
                    floatable=self._target_meta.get("floatable", True),
                )
        else:
            # Target was already a container, just update its label
            self._target_widget.setTabText(target_idx, f"[{container.count()}]")

        # Restore source to its original widget
        if source_content:
            insert_idx = min(self._original_source_index, self._source_widget.count())
            self._source_widget.insertTab(
                insert_idx,
                source_content,
                self._source_label,
                tab_id=self._source_tab_id,
                closable=self._source_meta.get("closable", True),
                movable=self._source_meta.get("movable", True),
                floatable=self._source_meta.get("floatable", True),
            )

        self._executed = False


class EnhancedTabBar(QTabBar):
    """Enhanced tab bar with drag & drop support.

    Signals:
        tabDragStarted: Tab drag started (index, global_pos)
        tabDropped: Tab dropped on this bar (source_widget, source_index, target_index, zone)
        tabFloatRequested: Tab should be floated (index, global_pos)
        tabNestRequested: Tab should be nested into target (source_id, target_id)
        dropZoneChanged: Drop zone changed during drag (zone, target_index, rect)
    """

    tabDragStarted = Signal(int, QPoint)  # index, global_pos
    tabDropped = Signal(object, int, int, str)  # source_widget, source_index, target_index, zone
    tabFloatRequested = Signal(int, QPoint)  # index, global_pos
    tabNestRequested = Signal(str, str)  # source_tab_id, target_tab_id
    dropZoneChanged = Signal(str, int, object)  # zone, target_index, rect (for visual indicator)

    # Minimum drag distance before starting drag
    DRAG_THRESHOLD = 10

    # Zone detection: 25% left/right for insert, 50% center for nest
    ZONE_EDGE_RATIO = 0.25

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize EnhancedTabBar."""
        super().__init__(parent)

        self._drag_start_pos: QPoint | None = None
        self._drag_tab_index: int = -1
        self._dragging = False
        self._current_drop_zone: DropZone = DropZone.NONE
        self._current_target_index: int = -1

        # Enable drops
        self.setAcceptDrops(True)
        self.setMovable(True)  # Built-in reordering

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Start potential drag operation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
            self._drag_tab_index = self.tabAt(self._drag_start_pos)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move - start drag if threshold exceeded.

        Strategy:
        - Always use custom QDrag for full control over drop zones
        - This enables: reordering, nesting (INTO), and cross-widget transfer
        """
        if not self._drag_start_pos or self._drag_tab_index < 0:
            super().mouseMoveEvent(event)
            return

        # Check if we've moved enough to start a drag
        diff = event.position().toPoint() - self._drag_start_pos
        if diff.manhattanLength() < self.DRAG_THRESHOLD:
            super().mouseMoveEvent(event)
            return

        # Check if dragging far outside tab bar vertically (float request)
        global_pos = event.globalPosition().toPoint()
        local_pos = self.mapFromGlobal(global_pos)

        if local_pos.y() < -40 or local_pos.y() > self.height() + 40:
            # Far outside - request float
            self.tabFloatRequested.emit(self._drag_tab_index, global_pos)
            self._reset_drag()
            return

        # Start custom drag for ALL operations (reorder, nest, transfer)
        # This gives us full control over drop zones
        if not self._dragging:
            self._start_drag(event)

        # Don't call super - we handle everything via QDrag

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """End drag operation."""
        self._reset_drag()
        super().mouseReleaseEvent(event)

    def _start_drag(self, event: QMouseEvent) -> None:
        """Start drag operation with visual feedback."""
        if self._drag_tab_index < 0:
            return

        self._dragging = True
        self.tabDragStarted.emit(
            self._drag_tab_index,
            event.globalPosition().toPoint()
        )

        # Create drag with tab preview
        drag = QDrag(self)
        mime_data = QMimeData()

        # Store tab info in mime data
        mime_data.setData(
            "application/x-enhanced-tab",
            f"{id(self.parent())}:{self._drag_tab_index}".encode()
        )
        drag.setMimeData(mime_data)

        # Create tab preview pixmap
        tab_rect = self.tabRect(self._drag_tab_index)
        pixmap = QPixmap(tab_rect.size())
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setOpacity(0.7)

        # Render tab to pixmap
        self.render(painter, QPoint(), self.rect().intersected(tab_rect))
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))

        # Execute drag
        drag.exec(Qt.DropAction.MoveAction)
        self._reset_drag()

    def _reset_drag(self) -> None:
        """Reset drag state."""
        self._drag_start_pos = None
        self._drag_tab_index = -1
        self._dragging = False

    def dragEnterEvent(self, event: Any) -> None:
        """Accept tab drops."""
        if event.mimeData().hasFormat("application/x-enhanced-tab"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: Any) -> None:
        """Show drop indicator and detect drop zone."""
        if not event.mimeData().hasFormat("application/x-enhanced-tab"):
            event.ignore()
            return

        event.acceptProposedAction()

        # Calculate drop zone
        drop_pos = event.position().toPoint()
        target_index = self.tabAt(drop_pos)
        zone, highlight_rect = self._calculate_drop_zone(drop_pos, target_index)

        # Only emit if zone OR target changed (prevents flicker)
        if zone != self._current_drop_zone or target_index != self._current_target_index:
            self._current_drop_zone = zone
            self._current_target_index = target_index
            # Single emit per zone change
            self.dropZoneChanged.emit(zone.value, target_index, highlight_rect)

    def dragLeaveEvent(self, event: Any) -> None:
        """Clear drop indicator when leaving."""
        self._current_drop_zone = DropZone.NONE
        self._current_target_index = -1
        self.dropZoneChanged.emit(DropZone.NONE.value, -1, None)
        super().dragLeaveEvent(event)

    def _calculate_drop_zone(
        self, drop_pos: QPoint, target_index: int
    ) -> tuple[DropZone, QRect | None]:
        """Calculate which drop zone the cursor is in.

        Drop zones:
        - BEFORE (25% left): Insert before target tab
        - INTO (50% center): Nest into target tab
        - AFTER (25% right): Insert after target tab
        - END: Append at end (no tab under cursor)

        Returns:
            Tuple of (DropZone, highlight_rect for visual feedback)
        """
        if target_index < 0:
            # No tab under cursor - drop at end
            return DropZone.END, None

        tab_rect = self.tabRect(target_index)
        tab_width = tab_rect.width()
        edge_width = int(tab_width * self.ZONE_EDGE_RATIO)

        local_x = drop_pos.x() - tab_rect.x()

        if local_x < edge_width:
            # Left edge - insert before
            highlight_rect = QRect(
                tab_rect.x() - 2, tab_rect.y(), 4, tab_rect.height()
            )
            return DropZone.BEFORE, highlight_rect

        elif local_x > tab_width - edge_width:
            # Right edge - insert after
            highlight_rect = QRect(
                tab_rect.right() - 2, tab_rect.y(), 4, tab_rect.height()
            )
            return DropZone.AFTER, highlight_rect

        else:
            # Center - nest into
            highlight_rect = tab_rect
            return DropZone.INTO, highlight_rect

    def dropEvent(self, event: Any) -> None:
        """Handle tab drop with zone detection."""
        if not event.mimeData().hasFormat("application/x-enhanced-tab"):
            event.ignore()
            return

        # Parse source info
        data = event.mimeData().data("application/x-enhanced-tab").data().decode()
        source_id, source_index = data.split(":")
        source_index = int(source_index)

        # Find drop position and zone
        drop_pos = event.position().toPoint()
        original_target_index = self.tabAt(drop_pos)
        zone, _ = self._calculate_drop_zone(drop_pos, original_target_index)

        # For INTO zone, use original index; for BEFORE/AFTER/END, adjust
        if zone == DropZone.INTO:
            target_index = original_target_index  # Keep original for nesting
        elif zone == DropZone.END:
            target_index = self.count()
        elif zone == DropZone.AFTER and original_target_index >= 0:
            target_index = original_target_index + 1
        else:
            target_index = original_target_index

        # Find source widget
        source_widget = None
        for widget in QApplication.topLevelWidgets():
            found = self._find_tab_widget_by_id(widget, int(source_id))
            if found:
                source_widget = found
                break

        if source_widget:
            # Emit with zone info for nest detection
            self.tabDropped.emit(source_widget, source_index, target_index, zone.value)

        # Clear drop zone indicator
        self._current_drop_zone = DropZone.NONE
        self._current_target_index = -1
        self.dropZoneChanged.emit(DropZone.NONE.value, -1, None)

        event.acceptProposedAction()

    def _find_tab_widget_by_id(self, widget: QWidget, widget_id: int) -> QWidget | None:
        """Recursively find QTabWidget by id."""
        if id(widget) == widget_id:
            return widget

        for child in widget.children():
            if isinstance(child, QWidget):
                result = self._find_tab_widget_by_id(child, widget_id)
                if result:
                    return result

        return None


class EnhancedTabWidget(QTabWidget):
    """Enhanced QTabWidget with full dock-like features.

    Features:
    - Per-tab closable flag
    - Drag & drop reordering
    - Drag to float
    - Drag between tab widgets
    - Context menu
    - Navigation signals

    Signals:
        tabFloated: Tab was floated (tab_id, widget)
        tabMoved: Tab moved within widget (from_index, to_index)
        tabTransferred: Tab moved to another widget (tab_id, target_widget)
        activeTabChanged: Active tab changed (tab_id)
    """

    tabFloated = Signal(str, object)  # tab_id, widget
    tabMoved = Signal(int, int)  # from_index, to_index
    tabTransferred = Signal(str, object)  # tab_id, target_widget
    tabNested = Signal(str, str)  # nested_tab_id, parent_tab_id
    activeTabChanged = Signal(str)  # tab_id
    dropZoneChanged = Signal(str, int, object)  # zone, target_index, rect

    # Shared undo manager for all tab widgets
    _shared_undo_manager: UndoRedoManager | None = None

    @classmethod
    def get_undo_manager(cls) -> UndoRedoManager:
        """Get the shared undo/redo manager for tab operations."""
        if cls._shared_undo_manager is None:
            cls._shared_undo_manager = UndoRedoManager()
        return cls._shared_undo_manager

    @classmethod
    def set_undo_manager(cls, manager: UndoRedoManager) -> None:
        """Set a custom undo/redo manager (e.g., app-wide manager)."""
        cls._shared_undo_manager = manager

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize EnhancedTabWidget."""
        super().__init__(parent)

        # Replace standard tab bar with enhanced one
        self._tab_bar = EnhancedTabBar(self)
        self.setTabBar(self._tab_bar)

        # Tab metadata: index -> {closable, movable, floatable, tab_id}
        self._tab_meta: dict[int, dict[str, Any]] = {}

        # Connect signals
        self._tab_bar.tabFloatRequested.connect(self._on_float_requested)
        self._tab_bar.tabDropped.connect(self._on_tab_dropped)
        self._tab_bar.dropZoneChanged.connect(self._on_drop_zone_changed)
        self.currentChanged.connect(self._on_current_changed)  # pylint: disable=no-member
        self.tabCloseRequested.connect(self._on_close_requested)  # pylint: disable=no-member

        # Enable features
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)

        # Prevent collapse when splitter is moved
        self.setMinimumSize(100, 50)

    def addTab(
        self,
        widget: QWidget,
        label: str,
        tab_id: str | None = None,
        closable: bool = True,
        movable: bool = True,
        floatable: bool = True,
    ) -> int:
        """Add tab with metadata.

        Args:
            widget: Content widget
            label: Tab label
            tab_id: Unique tab ID (generated if None)
            closable: Whether tab can be closed
            movable: Whether tab can be moved
            floatable: Whether tab can be floated

        Returns:
            Tab index
        """
        index = super().addTab(widget, label)

        # Generate tab_id if not provided
        if tab_id is None:
            tab_id = f"tab_{id(widget)}"

        # Store metadata
        self._tab_meta[index] = {
            "tab_id": tab_id,
            "closable": closable,
            "movable": movable,
            "floatable": floatable,
        }

        # Store tab_id in widget for lookup
        widget.setProperty("tab_id", tab_id)

        # Register in hierarchy validator
        validator = get_hierarchy_validator()
        parent_id = self.property("parent_tab_id")  # Set when nested
        validator.register_tab(tab_id, parent_id, self)

        return index

    def insertTab(
        self,
        index: int,
        widget: QWidget,
        label: str,
        tab_id: str | None = None,
        closable: bool = True,
        movable: bool = True,
        floatable: bool = True,
    ) -> int:
        """Insert tab with metadata at specific position."""
        actual_index = super().insertTab(index, widget, label)

        if tab_id is None:
            tab_id = f"tab_{id(widget)}"

        # Shift metadata for tabs after insertion
        new_meta: dict[int, dict[str, Any]] = {}
        for idx, meta in self._tab_meta.items():
            if idx >= actual_index:
                new_meta[idx + 1] = meta
            else:
                new_meta[idx] = meta

        new_meta[actual_index] = {
            "tab_id": tab_id,
            "closable": closable,
            "movable": movable,
            "floatable": floatable,
        }

        self._tab_meta = new_meta
        widget.setProperty("tab_id", tab_id)

        return actual_index

    def removeTab(self, index: int) -> None:
        """Remove tab and its metadata."""
        # Unregister from hierarchy validator
        tab_id = self.get_tab_id(index)
        if tab_id:
            validator = get_hierarchy_validator()
            validator.unregister_tab(tab_id)

        if index in self._tab_meta:
            del self._tab_meta[index]

        super().removeTab(index)

        # Reindex metadata
        new_meta: dict[int, dict[str, Any]] = {}
        for idx, meta in sorted(self._tab_meta.items()):
            if idx > index:
                new_meta[idx - 1] = meta
            else:
                new_meta[idx] = meta
        self._tab_meta = new_meta

        # Auto-dissolve: if this is a nested widget with only 1 tab left,
        # signal parent to dissolve this container
        self._check_auto_dissolve()

    def _check_auto_dissolve(self) -> None:
        """Check if this container should dissolve (1 or 0 children)."""
        validator = get_hierarchy_validator()
        if not validator.auto_dissolve_empty_folders:
            return

        # Only dissolve if we're a nested container (have parent_tab_id)
        parent_tab_id = self.property("parent_tab_id")
        if not parent_tab_id:
            return

        # Dissolve if 0 or 1 tabs remaining
        if self.count() <= 1:
            self._dissolve_container()

    def _dissolve_container(self) -> None:
        """Dissolve this container, replacing it with remaining content.

        Called when a nested container has 0 or 1 tabs left.
        - 0 tabs: Remove the container tab from parent entirely
        - 1 tab: Replace the container with the remaining tab's content
        """
        parent_tab_id = self.property("parent_tab_id")
        if not parent_tab_id:
            return

        # Find parent widget that contains this container
        parent_widget = self.parent()
        while parent_widget and not isinstance(parent_widget, EnhancedTabWidget):
            parent_widget = parent_widget.parent()

        if not isinstance(parent_widget, EnhancedTabWidget):
            return

        # Find this container's index in parent
        container_index = -1
        for i in range(parent_widget.count()):
            if parent_widget.widget(i) is self:
                container_index = i
                break

        if container_index < 0:
            return

        if self.count() == 0:
            # No tabs left - just remove the container
            parent_widget.removeTab(container_index)
        elif self.count() == 1:
            # One tab left - extract it and replace container
            remaining_content = self.widget(0)
            remaining_label = self.tabText(0)
            remaining_meta = self._tab_meta.get(0, {}).copy()
            remaining_tab_id = remaining_meta.get("tab_id", f"tab_{id(remaining_content)}")

            # Check if this is the _content tab - restore original ID
            if remaining_tab_id.endswith("_content"):
                remaining_tab_id = remaining_tab_id[:-8]  # Remove "_content" suffix
                remaining_label = parent_widget.tabText(container_index)

            # Keep widget alive by removing without destroying
            super(EnhancedTabWidget, self).removeTab(0)

            # Remove container from parent
            parent_widget.removeTab(container_index)

            # Insert the extracted content at the same position
            parent_widget.insertTab(
                container_index,
                remaining_content,
                remaining_label,
                tab_id=remaining_tab_id,
                closable=remaining_meta.get("closable", True),
                movable=remaining_meta.get("movable", True),
                floatable=remaining_meta.get("floatable", True),
            )

            parent_widget.setCurrentIndex(container_index)

    def _remove_tab_keep_widget(self, index: int) -> QWidget | None:
        """Remove tab but keep widget alive (for undo).

        Unlike removeTab(), this does NOT destroy the widget.

        Args:
            index: Tab index to remove

        Returns:
            The widget that was removed (still alive)
        """
        # Get widget before removal
        widget = self.widget(index)
        if not widget:
            return None

        # Unregister from hierarchy validator
        tab_id = self.get_tab_id(index)
        if tab_id:
            validator = get_hierarchy_validator()
            validator.unregister_tab(tab_id)

        if index in self._tab_meta:
            del self._tab_meta[index]

        # QTabWidget.removeTab() will call widget.setParent(None) internally
        # which keeps the widget alive. We just need to call the base removeTab.
        super().removeTab(index)

        # Reindex metadata
        new_meta: dict[int, dict[str, Any]] = {}
        for idx, meta in sorted(self._tab_meta.items()):
            if idx > index:
                new_meta[idx - 1] = meta
            else:
                new_meta[idx] = meta
        self._tab_meta = new_meta

        return widget

    def get_tab_id(self, index: int) -> str | None:
        """Get tab ID by index."""
        meta = self._tab_meta.get(index)
        return meta["tab_id"] if meta else None

    def get_tab_index_by_id(self, tab_id: str) -> int:
        """Get tab index by ID."""
        for idx, meta in self._tab_meta.items():
            if meta.get("tab_id") == tab_id:
                return idx
        return -1

    def is_tab_closable(self, index: int) -> bool:
        """Check if specific tab is closable."""
        meta = self._tab_meta.get(index)
        return meta.get("closable", True) if meta else True

    def is_tab_movable(self, index: int) -> bool:
        """Check if specific tab is movable."""
        meta = self._tab_meta.get(index)
        return meta.get("movable", True) if meta else True

    def is_tab_floatable(self, index: int) -> bool:
        """Check if specific tab is floatable."""
        meta = self._tab_meta.get(index)
        return meta.get("floatable", True) if meta else True

    def set_tab_closable(self, index: int, closable: bool) -> None:
        """Set closable flag for specific tab."""
        if index in self._tab_meta:
            self._tab_meta[index]["closable"] = closable

    def set_tab_movable(self, index: int, movable: bool) -> None:
        """Set movable flag for specific tab."""
        if index in self._tab_meta:
            self._tab_meta[index]["movable"] = movable

    def set_tab_floatable(self, index: int, floatable: bool) -> None:
        """Set floatable flag for specific tab."""
        if index in self._tab_meta:
            self._tab_meta[index]["floatable"] = floatable

    def navigate_to(self, tab_id: str) -> bool:
        """Navigate to tab by ID.

        Args:
            tab_id: Tab identifier

        Returns:
            True if found and activated
        """
        index = self.get_tab_index_by_id(tab_id)
        if index >= 0:
            self.setCurrentIndex(index)
            return True
        return False

    def _on_close_requested(self, index: int) -> None:
        """Handle close request - check closable flag and use undo system."""
        if not self.is_tab_closable(index):
            return  # Ignore close for non-closable tabs

        # Create and execute undo command
        cmd = CloseTabUndoCommand(self, index)
        self.get_undo_manager().execute(cmd)

    def _on_float_requested(self, index: int, global_pos: QPoint) -> None:
        """Handle float request from tab bar.

        Args:
            index: Tab index to float
            global_pos: Global position for window placement (reserved)
        """
        _ = global_pos  # Reserved for floating window positioning
        if not self.is_tab_floatable(index):
            return

        tab_id = self.get_tab_id(index)
        widget = self.widget(index)

        if tab_id and widget:
            # Remove from this widget
            self.removeTab(index)

            # Emit signal for external handling (create floating window)
            self.tabFloated.emit(tab_id, widget)

    def _on_drop_zone_changed(
        self, zone: str, target_index: int, rect: Any
    ) -> None:
        """Forward drop zone changes for visual indicator."""
        self.dropZoneChanged.emit(zone, target_index, rect)

    def _on_tab_dropped(
        self, source_widget: QWidget, source_index: int, target_index: int, zone: str
    ) -> None:
        """Handle tab drop with full zone detection (nest, reorder, transfer)."""
        if not isinstance(source_widget, EnhancedTabWidget):
            return

        source_tab_id = source_widget.get_tab_id(source_index)
        target_tab_id = self.get_tab_id(target_index) if target_index >= 0 else None

        # Prevent dropping on self
        if source_tab_id == target_tab_id:
            return

        # Check for NEST operation (drop INTO center zone)
        is_nest_op = (
            zone == DropZone.INTO.value
            and target_index >= 0
            and target_tab_id
            and source_tab_id
            and source_tab_id != target_tab_id
        )
        if is_nest_op:
            self._nest_tab_into(source_widget, source_index, target_index)
            return

        # REORDER or TRANSFER operation (BEFORE, AFTER, END zones)
        tab_id = source_widget.get_tab_id(source_index)
        widget = source_widget.widget(source_index)
        label = source_widget.tabText(source_index)
        meta = source_widget._tab_meta.get(source_index, {})

        if not widget:
            return

        # Calculate final insert position
        insert_index = target_index
        if zone == DropZone.END.value or target_index < 0:
            insert_index = self.count()
        elif zone == DropZone.AFTER.value:
            insert_index = target_index + 1

        # For internal moves, adjust index if source is before target
        is_internal = source_widget is self
        if is_internal and source_index < insert_index:
            insert_index -= 1

        # Remove from source
        source_widget.removeTab(source_index)

        # Add to target
        self.insertTab(
            insert_index,
            widget,
            label,
            tab_id=tab_id,
            closable=meta.get("closable", True),
            movable=meta.get("movable", True),
            floatable=meta.get("floatable", True),
        )

        self.setCurrentIndex(insert_index)

        if is_internal:
            self.tabMoved.emit(source_index, insert_index)
        else:
            self.tabTransferred.emit(tab_id or "", self)

    def _nest_tab_into(
        self, source_widget: "EnhancedTabWidget", source_index: int, target_index: int
    ) -> None:
        """Nest a tab into another tab with undo support.

        Creates an undoable command and executes it.
        """
        # Create and execute undo command
        cmd = NestTabUndoCommand(source_widget, source_index, self, target_index)
        self.get_undo_manager().execute(cmd)

    def _nest_tab_into_internal(
        self, source_widget: "EnhancedTabWidget", source_index: int, target_index: int
    ) -> None:
        """Internal: Nest a tab into another tab, creating sub-tab structure.

        Folder-like behavior:
        - Target tab becomes a CONTAINER
        - Source tab and Target's content are BOTH in the nested widget
        - All content remains accessible

        This is the actual implementation - use _nest_tab_into for undo support.
        """
        source_tab_id = source_widget.get_tab_id(source_index)
        target_tab_id = self.get_tab_id(target_index)

        if not source_tab_id or not target_tab_id:
            return

        # Prevent nesting _content tab back into its container
        if source_tab_id.endswith("_content") and source_tab_id.startswith(target_tab_id):
            return

        # Validate nesting operation (prevents circular nesting and depth overflow)
        validator = get_hierarchy_validator()
        is_valid, _ = validator.validate_nesting(source_tab_id, target_tab_id)
        if not is_valid:
            return

        # Get source tab content and metadata BEFORE any removal
        source_content = source_widget.widget(source_index)
        source_label = source_widget.tabText(source_index)
        source_meta = source_widget._tab_meta.get(source_index, {}).copy()

        if not source_content:
            return

        # Get target tab content and metadata
        target_content = self.widget(target_index)
        target_label = self.tabText(target_index)
        target_meta = self._tab_meta.get(target_index, {}).copy()

        if not target_content:
            return

        # IMPORTANT: Adjust target_index if source is removed before target
        # and they are in the same widget
        adjusted_target_index = target_index
        if source_widget is self and source_index < target_index:
            adjusted_target_index -= 1

        # Remove source tab first
        source_widget.removeTab(source_index)

        # Re-get target content after potential index shift
        if source_widget is self:
            target_content = self.widget(adjusted_target_index)
            target_label = self.tabText(adjusted_target_index)
            target_meta = self._tab_meta.get(adjusted_target_index, {}).copy()
            if not target_content:
                return

        # Check if target already has nested tabs
        if isinstance(target_content, EnhancedTabWidget):
            # Already a container - just add source to it
            target_content.addTab(
                source_content,
                source_label,
                tab_id=source_tab_id,
                closable=source_meta.get("closable", True),
                movable=source_meta.get("movable", True),
                floatable=source_meta.get("floatable", True),
            )
            # Update container label with new count
            self.setTabText(adjusted_target_index, f"[{target_content.count()}]")
        else:
            # Convert target to container with BOTH tabs inside:
            #
            # BEFORE: [Alpha] [Beta] [Gamma] [Delta]
            #
            # AFTER (drag Alpha → Delta):
            #   Outer: [Beta] [Gamma] [▼]
            #   Inner: [Alpha] [Delta]  <-- BOTH preserved!

            nested_widget = EnhancedTabWidget()
            nested_widget.setObjectName(f"nested_{target_tab_id}")
            nested_widget.setMinimumSize(100, 100)  # Prevent collapse when empty
            nested_widget.setProperty("parent_tab_id", target_tab_id)

            # Remove target tab to release its content
            self.removeTab(adjusted_target_index)

            # Add SOURCE first
            nested_widget.addTab(
                source_content,
                source_label,
                tab_id=source_tab_id,
                closable=source_meta.get("closable", True),
                movable=source_meta.get("movable", True),
                floatable=source_meta.get("floatable", True),
            )

            # Add TARGET's original content second (preserved!)
            nested_widget.addTab(
                target_content,
                target_label,
                tab_id=target_tab_id + "_content",
                closable=target_meta.get("closable", True),
                movable=target_meta.get("movable", True),
                floatable=target_meta.get("floatable", True),
            )

            # Insert container tab with dynamic count symbol
            self.insertTab(
                adjusted_target_index,
                nested_widget,
                f"[{nested_widget.count()}]",  # [2] shows nested tab count
                tab_id=target_tab_id,
                closable=target_meta.get("closable", True),
                movable=target_meta.get("movable", True),
                floatable=target_meta.get("floatable", True),
            )

        self.setCurrentIndex(adjusted_target_index if adjusted_target_index < self.count() else self.count() - 1)
        self.tabNested.emit(source_tab_id, target_tab_id)

    def _update_container_label(self, index: int) -> None:
        """Update container tab label to show nested tab count."""
        if index < 0 or index >= self.count():
            return
        widget = self.widget(index)
        if isinstance(widget, EnhancedTabWidget):
            self.setTabText(index, f"[{widget.count()}]")

    def _on_current_changed(self, index: int) -> None:
        """Handle tab change."""
        tab_id = self.get_tab_id(index)
        if tab_id:
            self.activeTabChanged.emit(tab_id)

    def export_config(self) -> list[dict[str, Any]]:
        """Export all tabs configuration.

        Returns:
            List of tab configurations
        """
        configs = []
        for i in range(self.count()):
            meta = self._tab_meta.get(i, {})
            configs.append({
                "tab_id": meta.get("tab_id", f"tab_{i}"),
                "title": self.tabText(i),
                "closable": meta.get("closable", True),
                "movable": meta.get("movable", True),
                "floatable": meta.get("floatable", True),
                "visible": self.isTabVisible(i),
                "enabled": self.isTabEnabled(i),
            })
        return configs
