"""Factory for managing splitter behavior, styling, and state tracking.

Handles:
- Splitter handle styling with configurable contrast
- Splitter state tracking (default, current, previous sizes)
- Double-click restore functionality
- Automatic event filter installation for all handles
- Corner handles for simultaneous multi-axis splitter movement
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QMenu,
    QSplitter,
    QSplitterHandle,
    QWidget,
)


class CornerSplitterHandle(QWidget):
    """Intelligent corner handle at splitter intersections with adaptive grouping.

    Placed at intersections where horizontal and vertical splitters meet.
    Supports:
    - Simultaneous multi-axis movement when grouped
    - Automatic separation on large drag offsets
    - Axis-locking for single-axis control
    - Visual feedback showing grouped/separated state
    - Right-click menu for manual grouping control
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize corner handle.

        Args:
            parent: Parent widget (usually the container with both splitters)
        """
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent; border: none;")
        self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        self.setMouseTracking(True)

        # State tracking
        self._drag_active: bool = False
        self._drag_start_pos: Any | None = None
        self._drag_cursor_offset: Any | None = None
        self._horizontal_bindings: list[tuple[QSplitter, int]] = []
        self._vertical_bindings: list[tuple[QSplitter, int]] = []

        # Adaptive grouping state
        self._is_grouped: bool = True  # True: all bound, False: separated
        self._last_drag_delta: QPoint = QPoint(0, 0)
        self._separation_threshold_px: int = 50  # Auto-separate after this much drag
        self._drag_started_globally: QPoint | None = None

        # Axis locking
        self._locked_axis: Qt.Orientation | None = None

        # Optional factory reference for cascade collapse during drag
        self._factory: "SplitterFactory | None" = None

    def is_drag_active(self) -> bool:
        """Return whether this corner handle is currently dragging."""
        return self._drag_active

    def is_grouped(self) -> bool:
        """Return whether splitters are bound together."""
        return self._is_grouped

    def horizontal_binding_count(self) -> int:
        """Return the number of bound X-axis splitters."""
        return len(self._horizontal_bindings)

    def vertical_binding_count(self) -> int:
        """Return the number of bound Y-axis splitters."""
        return len(self._vertical_bindings)

    def set_splitters(
        self,
        h_splitter: QSplitter,
        h_handle_index: int,
        v_splitter: QSplitter,
        v_handle_index: int,
    ) -> None:
        """Configure the horizontal and vertical splitters this corner controls.

        Args:
            h_splitter: Horizontal splitter
            h_handle_index: Index of handle in horizontal splitter
            v_splitter: Vertical splitter
            v_handle_index: Index of handle in vertical splitter
        """
        self.set_binding_groups(
            horizontal_bindings=[(h_splitter, h_handle_index)],
            vertical_bindings=[(v_splitter, v_handle_index)],
        )

    def set_binding_groups(
        self,
        *,
        horizontal_bindings: list[tuple[QSplitter, int]],
        vertical_bindings: list[tuple[QSplitter, int]],
    ) -> None:
        """Configure all horizontal and vertical splitter bindings at once."""
        self._horizontal_bindings.clear()
        self._vertical_bindings.clear()

        for splitter, handle_index in horizontal_bindings:
            self._append_unique_binding(self._horizontal_bindings, splitter, handle_index)

        for splitter, handle_index in vertical_bindings:
            self._append_unique_binding(self._vertical_bindings, splitter, handle_index)

        self.sync_to_intersection()

    def regroup(self) -> None:
        """Re-bind all splitters together."""
        self._is_grouped = True
        self._locked_axis = None
        self.update()

    def ungroup(self) -> None:
        """Separate all bound splitters."""
        self._is_grouped = False
        self.update()

    def add_splitter_pair(
        self,
        h_splitter: QSplitter,
        h_handle_index: int,
        v_splitter: QSplitter,
        v_handle_index: int,
    ) -> None:
        """Add an additional horizontal/vertical splitter pair to this corner control.

        Args:
            h_splitter: Horizontal splitter
            h_handle_index: Handle index in horizontal splitter
            v_splitter: Vertical splitter
            v_handle_index: Handle index in vertical splitter
        """
        self._append_unique_binding(self._horizontal_bindings, h_splitter, h_handle_index)
        self._append_unique_binding(self._vertical_bindings, v_splitter, v_handle_index)

    def _append_unique_binding(
        self,
        bindings: list[tuple[QSplitter, int]],
        splitter: QSplitter,
        handle_index: int,
    ) -> None:
        """Append a splitter-handle binding if it does not already exist."""
        for existing_splitter, existing_index in bindings:
            if existing_splitter is splitter and existing_index == handle_index:
                return
        bindings.append((splitter, handle_index))

    def set_factory(self, factory: "SplitterFactory") -> None:
        """Attach the SplitterFactory so drag movements can trigger cascade collapse.

        Args:
            factory: SplitterFactory instance owning this corner handle
        """
        self._factory = factory

    def _try_cascade(
        self,
        splitter: QSplitter,
        handle_index: int,
        *,
        direction: int,
        drag_step: int,
        edge_hint: str | None,
    ) -> None:
        """Delegate cascade collapse to the factory if available.

        Called after a corner-handle drag move reaches the snap zone so that
        neighbouring panes collapse in sequence (outside-in) just like a
        regular splitter-handle drag does via SplitterEventHandler.

        Args:
            splitter: The splitter whose handle was moved
            handle_index: Index of the moved handle
            direction: -1 for left/top, +1 for right/bottom
            drag_step: Pixel magnitude of this drag step
            edge_hint: "min" or "max" edge that is active
        """
        if self._factory is None:
            return
        self._factory.apply_hierarchical_drag_cascade(
            splitter,
            handle_index,
            direction,
            drag_step,
            edge_hint=edge_hint,
        )

    def paintEvent(self, _event: Any) -> None:
        """Draw corner indicator with state-dependent colors.
        
        - Grouped (anthracite): All splitters move together
        - Separated (gray): Individual splitter control
        - Drag active: Brightened anthracite
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(0, 0, -1, -1)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())

        # Color scheme based on state
        if self._drag_active:
            # Bright active state (anthracite)
            gradient.setColorAt(0.0, QColor(78, 82, 88, 235))
            gradient.setColorAt(0.55, QColor(49, 53, 59, 235))
            gradient.setColorAt(1.0, QColor(26, 29, 34, 235))
        elif self._is_grouped:
            # Grouped state (anthracite)
            gradient.setColorAt(0.0, QColor(62, 66, 72, 210))
            gradient.setColorAt(0.55, QColor(38, 42, 48, 190))
            gradient.setColorAt(1.0, QColor(18, 21, 26, 190))
        else:
            # Separated state (gray)
            gradient.setColorAt(0.0, QColor(150, 150, 150, 180))
            gradient.setColorAt(0.55, QColor(100, 100, 100, 160))
            gradient.setColorAt(1.0, QColor(70, 70, 70, 160))

        painter.fillRect(rect, gradient)

        # Draw border
        border_color = QColor(120, 128, 138, 190) if self._is_grouped else QColor(140, 140, 140, 150)
        painter.setPen(border_color)
        painter.drawRect(rect)

        # Draw crosshair (dark center accent)
        crosshair_color = QColor(8, 10, 12, 230)
        painter.setPen(crosshair_color)
        mid_x = self.width() // 2
        mid_y = self.height() // 2
        painter.drawLine(2, mid_y, self.width() - 2, mid_y)
        painter.drawLine(mid_x, 2, mid_x, self.height() - 2)

    def mousePressEvent(self, event: Any) -> None:
        """Handle mouse press: start drag (left), show menu (right)."""
        if event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPos())
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_started_globally = event.globalPos()
            self._last_drag_delta = QPoint(0, 0)
            self._locked_axis = None

            parent_widget = self.parentWidget()
            center = self._current_intersection_center(parent_widget)
            if parent_widget is not None and center is not None:
                center_global = parent_widget.mapToGlobal(QPoint(center[0], center[1]))
                self._drag_cursor_offset = event.globalPos() - center_global
            else:
                self._drag_cursor_offset = QPoint(0, 0)

            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            self.grabMouse()
            self.update()

    def mouseMoveEvent(self, event: Any) -> None:
        """Move splitters with intelligent axis locking and auto-separation.
        
        - Single axis movement: locks to strongest delta
        - Corner movement (both axes): allows 2D movement
        - Auto-separation: triggers at separation_threshold_px
        """
        if not self._drag_active or self._drag_started_globally is None:
            return

        parent_widget = self.parentWidget()
        current_center = self._current_intersection_center(parent_widget)
        if parent_widget is None or current_center is None:
            return

        # Calculate movement delta
        delta = event.globalPos() - self._drag_started_globally
        self._last_drag_delta = delta

        # Detect axis lock on first significant movement
        if self._locked_axis is None and (abs(delta.x()) > 5 or abs(delta.y()) > 5):
            self._locked_axis = self._detect_dominant_axis(delta)

        # Auto-separate if moved beyond threshold
        if self._is_grouped and abs(delta.x()) + abs(delta.y()) > self._separation_threshold_px:
            self.ungroup()

        # Apply movement based on axis lock
        offset = self._drag_cursor_offset if self._drag_cursor_offset is not None else QPoint(0, 0)
        desired_center_global = event.globalPos() - offset
        desired_center_local = parent_widget.mapFromGlobal(desired_center_global)

        delta_x = desired_center_local.x() - current_center[0]
        delta_y = desired_center_local.y() - current_center[1]

        # Only move if grouped OR axis not locked
        if (self._is_grouped or self._locked_axis is None or self._locked_axis == Qt.Orientation.Horizontal) and delta_x != 0:
            for h_splitter, h_handle_index in self._horizontal_bindings:
                self._move_splitter_handle(h_splitter, h_handle_index, delta_x)

        if (self._is_grouped or self._locked_axis is None or self._locked_axis == Qt.Orientation.Vertical) and delta_y != 0:
            for v_splitter, v_handle_index in self._vertical_bindings:
                self._move_splitter_handle(v_splitter, v_handle_index, delta_y)

        self._drag_started_globally = event.globalPos()
        self.sync_to_intersection()

    def mouseReleaseEvent(self, event: Any) -> None:
        """End drag operation and check for auto-regrouping."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
            self._drag_started_globally = None
            self._drag_cursor_offset = None

            # Check if should regroup after release
            if not self._is_grouped and abs(self._last_drag_delta.x()) + abs(self._last_drag_delta.y()) < 5:
                self.regroup()

            self._locked_axis = None
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            self.releaseMouse()
            self._sync_peer_corner_handles()
            self.update()

    def _move_splitter_handle(
        self,
        splitter: QSplitter,
        handle_index: int,
        delta: int,
    ) -> None:
        """Move a single splitter handle by delta pixels.

        Args:
            splitter: QSplitter instance
            handle_index: Index of the handle to move
            delta: Pixel delta to move
        """
        if delta == 0:
            return

        handle = splitter.handle(handle_index)
        if handle is None:
            return

        current_pos = handle.x() if splitter.orientation() == Qt.Orientation.Horizontal else handle.y()
        target_pos = current_pos + delta
        range_values = splitter.getRange(handle_index)
        if not isinstance(range_values, tuple) or len(range_values) != 2:
            return

        min_pos, max_pos = range_values
        collapse_snap = self._collapse_snap_distance(splitter)
        auto_collapse_enabled = self._auto_collapse_enabled(splitter)
        hierarchical_collapse_enabled = self._hierarchical_collapse_enabled(splitter)

        if not auto_collapse_enabled:
            legal_target = splitter.closestLegalPosition(target_pos, handle_index)
            splitter.moveSplitter(legal_target, handle_index)
            return

        if hierarchical_collapse_enabled and delta < 0 and target_pos <= min_pos + collapse_snap:
            overshoot = (min_pos + collapse_snap) - target_pos
            if self._apply_hierarchical_collapse(
                splitter,
                handle_index,
                direction=-1,
                overshoot_px=overshoot,
            ):
                self._try_cascade(splitter, handle_index, direction=-1, drag_step=abs(delta), edge_hint="min")
                return

        if delta < 0 and target_pos <= min_pos + collapse_snap:
            splitter.moveSplitter(min_pos, handle_index)
            self._try_cascade(splitter, handle_index, direction=-1, drag_step=abs(delta), edge_hint="min")
            return

        if hierarchical_collapse_enabled and delta > 0 and target_pos >= max_pos - collapse_snap:
            overshoot = target_pos - (max_pos - collapse_snap)
            if self._apply_hierarchical_collapse(
                splitter,
                handle_index,
                direction=1,
                overshoot_px=overshoot,
            ):
                self._try_cascade(splitter, handle_index, direction=1, drag_step=abs(delta), edge_hint="max")
                return

        if delta > 0 and target_pos >= max_pos - collapse_snap:
            splitter.moveSplitter(max_pos, handle_index)
            self._try_cascade(splitter, handle_index, direction=1, drag_step=abs(delta), edge_hint="max")
            return

        legal_target = splitter.closestLegalPosition(target_pos, handle_index)
        splitter.moveSplitter(legal_target, handle_index)

    def _collapse_snap_distance(self, splitter: QSplitter) -> int:
        """Return snap distance in pixels before a handle fully collapses."""
        property_value = splitter.property("ws_collapse_snap")
        if isinstance(property_value, int) and property_value > 0:
            return property_value
        return max(10, splitter.handleWidth() * 5)

    def _auto_collapse_enabled(self, splitter: QSplitter) -> bool:
        """Return whether edge snap auto-collapse is enabled for this splitter."""
        property_value = splitter.property("ws_auto_collapse_enabled")
        if isinstance(property_value, bool):
            return property_value
        return True

    def _hierarchical_collapse_enabled(self, splitter: QSplitter) -> bool:
        """Return whether cascade collapse order is enabled for this splitter."""
        property_value = splitter.property("ws_hierarchical_collapse_enabled")
        if isinstance(property_value, bool):
            return property_value
        return True

    def _min_remainder_for_splitter(self, splitter: QSplitter) -> int:
        """Return minimum remainder size for a splitter."""
        property_value = splitter.property("ws_min_remainder")
        if isinstance(property_value, int) and property_value > 0:
            return property_value
        return 18

    def _apply_hierarchical_collapse(
        self,
        splitter: QSplitter,
        handle_index: int,
        *,
        direction: int,
        overshoot_px: int,
    ) -> bool:
        """Apply sequential collapse from nearest pane to farthest pane.

        Direction semantics:
        - -1: collapse from handle toward start (top/left)
        -  1: collapse from handle toward end (bottom/right)

        Args:
            splitter: Splitter to update
            handle_index: Moved splitter handle index
            direction: Collapse direction (-1 or 1)
            overshoot_px: How far the drag moved into the collapse zone

        Returns:
            True if a hierarchical collapse update was applied
        """
        sizes = splitter.sizes()
        if not sizes:
            return False

        min_remainder = self._min_remainder_for_splitter(splitter)
        collapse_snap = self._collapse_snap_distance(splitter)
        budget = max(1, overshoot_px)
        budget = min(budget + (collapse_snap // 3), collapse_snap * 2)

        new_sizes = list(sizes)

        if direction < 0:
            shrink_indices = list(range(handle_index - 1, -1, -1))
            grow_index = min(handle_index, len(new_sizes) - 1)
        else:
            shrink_indices = list(range(handle_index, len(new_sizes)))
            grow_index = max(handle_index - 1, 0)

        consumed = 0
        for index in shrink_indices:
            if consumed >= budget:
                break

            available = max(0, new_sizes[index] - min_remainder)
            if available == 0:
                continue

            take = min(available, budget - consumed)
            new_sizes[index] -= take
            new_sizes[grow_index] += take
            consumed += take

        if consumed == 0:
            return False

        splitter.setSizes(new_sizes)
        return True

    def sync_to_intersection(self) -> None:
        """Reposition this corner handle to the current splitter intersection."""
        parent_widget = self.parentWidget()
        center = self._current_intersection_center(parent_widget)
        if center is None:
            return

        size = self.width()
        self.move(center[0] - (size // 2) + 1, center[1] - (size // 2) + 1)

    def _current_intersection_center(self, parent_widget: QWidget | None) -> tuple[int, int] | None:
        """Return current intersection center in parent coordinates.

        Args:
            parent_widget: Parent coordinate system

        Returns:
            Tuple of (x, y) center coordinates or None if unavailable
        """
        if parent_widget is None or not self._horizontal_bindings or not self._vertical_bindings:
            return None

        horizontal_geometries: list[QRect] = []
        for h_splitter, h_handle_index in self._horizontal_bindings:
            candidate = h_splitter.handle(h_handle_index)
            if candidate is not None:
                horizontal_geometries.append(self._handle_geometry_in_parent(parent_widget, candidate))

        vertical_geometries: list[QRect] = []
        for v_splitter, v_handle_index in self._vertical_bindings:
            candidate = v_splitter.handle(v_handle_index)
            if candidate is not None:
                vertical_geometries.append(self._handle_geometry_in_parent(parent_widget, candidate))

        if not horizontal_geometries or not vertical_geometries:
            return None

        center_x = round(
            sum(geometry.center().x() for geometry in horizontal_geometries) / len(horizontal_geometries)
        )
        center_y = round(
            sum(geometry.center().y() for geometry in vertical_geometries) / len(vertical_geometries)
        )
        return (center_x, center_y)

    def _handle_geometry_in_parent(
        self,
        parent_widget: QWidget,
        handle: QSplitterHandle,
    ) -> QRect:
        """Map a splitter handle geometry into parent coordinates."""
        top_left = parent_widget.mapFromGlobal(handle.mapToGlobal(handle.rect().topLeft()))
        return handle.rect().translated(top_left)

    def _sync_peer_corner_handles(self) -> None:
        """Reposition all sibling corner handles in the same parent widget."""
        parent_widget = self.parentWidget()
        if parent_widget is None:
            return

        for widget in parent_widget.findChildren(QWidget):
            if isinstance(widget, CornerSplitterHandle) and widget is not self:
                widget.sync_to_intersection()

    def sync_with_peers(self) -> None:
        """Public helper to synchronize this corner handle and all peers."""
        self.sync_to_intersection()
        self._sync_peer_corner_handles()

    def _show_context_menu(self, global_pos: QPoint) -> None:
        """Show context menu for manual grouping control.
        
        Args:
            global_pos: Global position for menu placement
        """
        menu = QMenu(self)

        if self._is_grouped:
            action = menu.addAction("Trennen (Separate)")
            action.triggered.connect(self.ungroup)
        else:
            action = menu.addAction("Zusammenbinden (Re-group)")
            action.triggered.connect(self.regroup)

        menu.addSeparator()
        
        info_text = f"Status: {'Verbunden' if self._is_grouped else 'Getrennt'} | "
        info_text += f"H: {len(self._horizontal_bindings)}, V: {len(self._vertical_bindings)}"
        menu.addAction(info_text).setEnabled(False)

        menu.exec(global_pos)

    def _detect_dominant_axis(self, delta: QPoint) -> Qt.Orientation | None:
        """Detect which axis has dominant movement.
        
        Args:
            delta: Movement delta (dx, dy)
            
        Returns:
            Qt.Orientation.Horizontal if X > Y,
            Qt.Orientation.Vertical if Y > X,
            None if both significant (corner drag)
        """
        abs_dx = abs(delta.x())
        abs_dy = abs(delta.y())

        # Both axes moved significantly - corner drag
        if abs_dx > 15 and abs_dy > 15:
            return None

        # X dominant
        if abs_dx > abs_dy + 5:
            return Qt.Orientation.Horizontal

        # Y dominant  
        if abs_dy > abs_dx + 5:
            return Qt.Orientation.Vertical

        # Ambiguous - allow both
        return None


@dataclass
class SplitterStyle:
    """Configuration for splitter handle appearance and contrast.

    Colors use RGBA format with adjustable alpha for contrast control.
    Darker alpha values reduce contrast.
    """

    # Handle background (anthracite base)
    handle_bg_rgba: str = "rgba(46, 50, 56, 0.28)"

    # Horizontal splitter handle borders (light/dark sides for 3D effect)
    horizontal_light_rgba: str = "rgba(98, 106, 116, 0.42)"
    horizontal_dark_rgba: str = "rgba(20, 24, 30, 0.58)"

    # Vertical splitter handle borders (light/dark sides for 3D effect)
    vertical_light_rgba: str = "rgba(98, 106, 116, 0.42)"
    vertical_dark_rgba: str = "rgba(20, 24, 30, 0.58)"

    # Hover state colors
    hover_bg_rgba: str = "rgba(0, 120, 212, 0.28)"
    hover_border_rgba: str = "rgba(0, 120, 212, 0.9)"

    # Corner handle colors
    corner_handle_size: int = 6
    corner_handle_bg_rgba: str = "rgba(40, 44, 50, 0.42)"
    corner_handle_hover_rgba: str = "rgba(68, 74, 82, 0.58)"


@dataclass(frozen=True)
class _HandleBindingRecord:
    """Internal geometry record for a splitter handle."""

    splitter: QSplitter
    handle_index: int
    orientation: Qt.Orientation
    geometry: QRect
    overlay_parent: QWidget


class SplitterFactory:
    """Factory for creating and managing splitter behavior across the application.

    Provides:
    - Unified splitter styling via QSS stylesheet
    - State tracking (default/current/previous sizes) for all splitters
    - Double-click restore functionality
    - Event filtering for handle interactions
    - Corner handles for multi-axis simultaneous movement
    """

    def __init__(self, style: SplitterStyle | None = None) -> None:
        """Initialize factory with optional style configuration.

        Args:
            style: SplitterStyle configuration. Defaults to standard dark theme.
        """
        self.style = style or SplitterStyle()
        self._handler: SplitterEventHandler | None = None
        self._corner_handles: list[CornerSplitterHandle] = []

    def get_collapse_snap_distance(self, splitter: QSplitter) -> int:
        """Return snap distance in pixels before a handle is considered collapse-near."""
        property_value = splitter.property("ws_collapse_snap")
        if isinstance(property_value, int) and property_value > 0:
            return property_value
        return max(10, splitter.handleWidth() * 5)

    def get_min_remainder(self, splitter: QSplitter) -> int:
        """Return minimum remainder size for a splitter."""
        property_value = splitter.property("ws_min_remainder")
        if isinstance(property_value, int) and property_value > 0:
            return property_value
        return 18

    def is_auto_collapse_enabled(self, splitter: QSplitter) -> bool:
        """Return whether edge snap auto-collapse is enabled for this splitter."""
        property_value = splitter.property("ws_auto_collapse_enabled")
        if isinstance(property_value, bool):
            return property_value
        return True

    def is_hierarchical_collapse_enabled(self, splitter: QSplitter) -> bool:
        """Return whether ordered cascade-collapse is enabled for this splitter."""
        property_value = splitter.property("ws_hierarchical_collapse_enabled")
        if isinstance(property_value, bool):
            return property_value
        return True

    def apply_hierarchical_drag_cascade(
        self,
        splitter: QSplitter,
        handle_index: int,
        direction: int,
        drag_step: int,
        edge_hint: str | None = None,
        collapse_mode: str = "outside_in",
    ) -> bool:
        """Apply ordered cascade collapse while dragging a splitter handle.

        Two collapse modes are supported:

        ``outside_in`` (default)
            The cascade starts at the pane adjacent to the dragged handle and
            continues toward the nearest edge in the drag direction.  This is
            the classic curtain collapse: drag left → leftmost panes disappear
            first, then the ones further right follow in sequence.

        ``inside_out``
            The cascade starts at the *centre* of the splitter and expands
            toward both edges simultaneously.  Useful for a "fold / unfold"
            effect where the middle content collapses outward.

        Args:
            splitter: Target splitter
            handle_index: Moved handle index (1..count-1)
            direction: -1 for top/left, +1 for bottom/right
            drag_step: Pixel movement magnitude for this drag step
            edge_hint: Force active edge: ``"min"``, ``"max"``, or ``None``
            collapse_mode: ``"outside_in"`` or ``"inside_out"``

        Returns:
            True if a cascade update was applied
        """
        if not self.is_auto_collapse_enabled(splitter):
            return False
        if not self.is_hierarchical_collapse_enabled(splitter):
            return False

        sizes = splitter.sizes()
        if not sizes or handle_index <= 0 or handle_index >= len(sizes):
            return False

        collapse_snap = self.get_collapse_snap_distance(splitter)
        range_values = splitter.getRange(handle_index)
        if not isinstance(range_values, tuple) or len(range_values) != 2:
            return False

        min_pos, max_pos = range_values
        handle = splitter.handle(handle_index)
        if handle is None:
            return False

        current_pos = (
            handle.x()
            if splitter.orientation() == Qt.Orientation.Horizontal
            else handle.y()
        )

        near_min = current_pos <= min_pos + collapse_snap
        near_max = current_pos >= max_pos - collapse_snap
        if edge_hint == "min":
            near_min = True
            near_max = False
        elif edge_hint == "max":
            near_min = False
            near_max = True
        if not near_min and not near_max:
            return False

        primary_index = handle_index - 1 if direction < 0 else handle_index
        if primary_index < 0 or primary_index >= len(sizes):
            return False

        budget = max(1, drag_step)
        remaining = budget
        applied = False

        if collapse_mode == "inside_out":
            # Build a handle chain that alternates outward from the centre:
            # centre → left neighbour, centre → right neighbour, etc.
            centre = splitter.count() // 2
            left_chain = list(range(centre - 1, 0, -1))
            right_chain = list(range(centre, splitter.count()))
            # Interleave: left[0], right[0], left[1], right[1], …
            interleaved: list[int] = []
            for l_idx, r_idx in zip(left_chain, right_chain, strict=False):
                interleaved.append(l_idx)
                interleaved.append(r_idx)
            # Append any remainder (asymmetric count)
            longer = left_chain if len(left_chain) > len(right_chain) else right_chain
            interleaved.extend(longer[min(len(left_chain), len(right_chain)):])
            handle_chain: list[int] = interleaved
        elif near_min:
            # Outside-in, left/top edge active: collapse from dragged handle backward.
            handle_chain = list(range(handle_index - 1, 0, -1))
        else:
            # Outside-in, right/bottom edge active: collapse from dragged handle forward.
            handle_chain = list(range(handle_index + 1, splitter.count()))

        for chain_handle_index in handle_chain:
            if remaining <= 0:
                break

            range_values = splitter.getRange(chain_handle_index)
            if not isinstance(range_values, tuple) or len(range_values) != 2:
                continue

            chain_min_pos, chain_max_pos = range_values
            chain_handle = splitter.handle(chain_handle_index)
            if chain_handle is None:
                continue

            current_chain_pos = (
                chain_handle.x()
                if splitter.orientation() == Qt.Orientation.Horizontal
                else chain_handle.y()
            )

            if direction < 0:
                target_pos = max(chain_min_pos, current_chain_pos - remaining)
            else:
                target_pos = min(chain_max_pos, current_chain_pos + remaining)

            legal_target = splitter.closestLegalPosition(target_pos, chain_handle_index)
            splitter.moveSplitter(legal_target, chain_handle_index)

            moved_delta = abs(current_chain_pos - legal_target)
            if moved_delta <= 0:
                continue

            remaining -= moved_delta
            applied = True

        return applied

    def _pane_minimum_size(
        self,
        splitter: QSplitter,
        index: int,
        fallback_minimum: int,
    ) -> int:
        """Return effective minimum size for a splitter pane by orientation.

        Args:
            splitter: Target splitter
            index: Pane index
            fallback_minimum: Fallback minimum when widget minimum is unavailable

        Returns:
            Effective minimum size in splitter axis direction
        """
        widget = splitter.widget(index)
        if widget is None:
            return fallback_minimum

        if splitter.orientation() == Qt.Orientation.Horizontal:
            return max(fallback_minimum, widget.minimumWidth())
        return max(fallback_minimum, widget.minimumHeight())

    def configure_handler(self, handler: "SplitterEventHandler") -> None:
        """Register an event handler for splitter interactions.

        Args:
            handler: SplitterEventHandler instance managing state and animations
        """
        self._handler = handler

    def generate_stylesheet(self) -> str:
        """Generate QSS stylesheet for splitter handles with current style.

        Returns:
            Complete QSS block for all splitter handle states
        """
        return f"""
QSplitter::handle {{
    background-color: {self.style.handle_bg_rgba};
}}

QSplitter::handle:horizontal {{
    background: qlineargradient(
        x1: 0,
        y1: 0,
        x2: 1,
        y2: 0,
        stop: 0 {self.style.horizontal_light_rgba},
        stop: 0.42 {self.style.handle_bg_rgba},
        stop: 1 {self.style.horizontal_dark_rgba}
    );
}}

QSplitter::handle:vertical {{
    background: qlineargradient(
        x1: 0,
        y1: 0,
        x2: 0,
        y2: 1,
        stop: 0 {self.style.vertical_light_rgba},
        stop: 0.42 {self.style.handle_bg_rgba},
        stop: 1 {self.style.vertical_dark_rgba}
    );
}}

QSplitter::handle:hover {{
    background-color: {self.style.hover_bg_rgba};
    border: none;
    outline: none;
}}
"""

    def apply_modern_behavior(
        self,
        splitter: QSplitter,
        *,
        handle_width: int = 3,
        min_remainder: int = 18,
        allow_auto_collapse: bool = True,
        hierarchical_collapse: bool = True,
    ) -> None:
        """Apply modern splitter behavior: narrow, collapsible, DnD-usable.

        Args:
            splitter: QSplitter to configure
            handle_width: Width of splitter handles in pixels (default: 3)
            min_remainder: Minimum size of collapsed panels in pixels (default: 18)
            allow_auto_collapse: Enable automatic edge snapping/collapse behavior
            hierarchical_collapse: Collapse panes sequentially from nearest to farthest
        """
        splitter.setHandleWidth(max(1, handle_width))
        splitter.setOpaqueResize(True)
        splitter.setProperty("ws_min_remainder", min_remainder)
        splitter.setProperty("ws_collapse_snap", max(10, max(1, handle_width) * 6))
        splitter.setProperty("ws_auto_collapse_enabled", allow_auto_collapse)
        splitter.setProperty("ws_hierarchical_collapse_enabled", hierarchical_collapse)
        splitter.setChildrenCollapsible(allow_auto_collapse)

        for index in range(splitter.count()):
            splitter.setCollapsible(index, allow_auto_collapse)

        self._install_handle_filters(splitter)

    def install_corner_handles(self, parent_widget: Any) -> None:
        """Install corner handles at intersections of perpendicular splitters.

        Searches for all splitters in parent_widget, finds intersections,
        and creates corner handles for simultaneous multi-axis movement.

        Args:
            parent_widget: Widget containing all splitters to analyze
        """
        # Clear existing corner handles first
        self.clear_corner_handles()

        splitters = list(parent_widget.findChildren(QSplitter))
        if isinstance(parent_widget, QSplitter):
            splitters.insert(0, parent_widget)
        if len(splitters) < 2:
            return

        horizontal_splitters = [
            splitter
            for splitter in splitters
            if splitter.orientation() == Qt.Orientation.Horizontal
        ]
        vertical_splitters = [
            splitter
            for splitter in splitters
            if splitter.orientation() == Qt.Orientation.Vertical
        ]

        for h_splitter in horizontal_splitters:
            for v_splitter in vertical_splitters:
                if h_splitter is v_splitter:
                    continue
                self._create_corner_at_intersection(
                    parent_widget=parent_widget,
                    h_splitter=h_splitter,
                    v_splitter=v_splitter,
                )

    def clear_corner_handles(self) -> None:
        """Remove all corner handles from the layout.

        Called before reinstalling or when disabling corner handles.
        Uses setParent(None) for immediate synchronous removal instead of
        deleteLater(), which is asynchronous and causes ghost widgets when
        install_corner_handles() is called right after clear.
        """
        handles = list(self._corner_handles)
        self._corner_handles.clear()
        for corner_handle in handles:
            corner_handle.hide()
            corner_handle.setParent(None)  # type: ignore[arg-type]
            corner_handle.deleteLater()

    def has_corner_handles(self) -> bool:
        """Return whether at least one corner handle is currently installed."""
        return len(self._corner_handles) > 0

    def is_corner_drag_active(self) -> bool:
        """Return whether any corner handle is actively dragging."""
        return any(handle.is_drag_active() for handle in self._corner_handles)

    def sync_corner_handles(self) -> None:
        """Synchronize all installed corner handles with current splitter geometry."""
        for corner_handle in self._corner_handles:
            corner_handle.sync_to_intersection()

    def _create_corner_at_intersection(
        self,
        parent_widget: Any,
        h_splitter: QSplitter,
        v_splitter: QSplitter,
    ) -> None:
        """Create corner handle at intersection of two perpendicular splitters.

        Args:
            parent_widget: Container widget
            h_splitter: Horizontal splitter
            v_splitter: Vertical splitter
        """
        # Get geometry of both splitter handles (if they exist)
        for h_idx in range(1, h_splitter.count()):
            h_handle = h_splitter.handle(h_idx)
            if h_handle is None:
                continue

            for v_idx in range(1, v_splitter.count()):
                v_handle = v_splitter.handle(v_idx)
                if v_handle is None:
                    continue

                # Check if handles intersect geometrically
                if self._handles_intersect(
                    parent_widget=parent_widget,
                    h_handle=h_handle,
                    v_handle=v_handle,
                ):
                    self._create_corner_handle_widget(
                        parent_widget,
                        h_splitter,
                        h_idx,
                        v_splitter,
                        v_idx,
                        h_handle,
                        v_handle,
                    )

    def _collect_handle_records(
        self,
        parent_widget: Any,
        splitters: list[QSplitter],
    ) -> list[_HandleBindingRecord]:
        """Collect geometry records for all splitter handles in the parent widget."""
        records: list[_HandleBindingRecord] = []
        for splitter in splitters:
            for handle_index in range(1, splitter.count()):
                handle = splitter.handle(handle_index)
                if handle is None:
                    continue

                overlay_parent = self._resolve_overlay_parent(parent_widget, handle)
                records.append(
                    _HandleBindingRecord(
                        splitter=splitter,
                        handle_index=handle_index,
                        orientation=splitter.orientation(),
                        geometry=self._handle_geometry_in_parent(parent_widget, handle),
                        overlay_parent=overlay_parent,
                    )
                )
        return records

    def _build_corner_handle_groups(
        self,
        handle_records: list[_HandleBindingRecord],
        tolerance: int = 12,
    ) -> list[list[_HandleBindingRecord]]:
        """Group all contacting splitter handles into connected corner clusters."""
        groups: list[list[_HandleBindingRecord]] = []
        visited: set[int] = set()

        for start_index, _record in enumerate(handle_records):
            if start_index in visited:
                continue

            pending = [start_index]
            component_indices: set[int] = set()
            while pending:
                current_index = pending.pop()
                if current_index in visited:
                    continue

                visited.add(current_index)
                component_indices.add(current_index)
                current_record = handle_records[current_index]

                for next_index, next_record in enumerate(handle_records):
                    if next_index in visited:
                        continue
                    if current_record.overlay_parent is not next_record.overlay_parent:
                        continue
                    if self._rects_touch(current_record.geometry, next_record.geometry, tolerance):
                        pending.append(next_index)

            group = [handle_records[index] for index in sorted(component_indices)]
            orientations = {record.orientation for record in group}
            if {
                Qt.Orientation.Horizontal,
                Qt.Orientation.Vertical,
            }.issubset(orientations):
                groups.append(group)

        return groups

    def _rects_touch(
        self,
        first_rect: QRect,
        second_rect: QRect,
        tolerance: int,
    ) -> bool:
        """Return whether two rectangles intersect or nearly touch."""
        if first_rect.intersects(second_rect):
            return True

        dx = max(second_rect.left() - first_rect.right(), first_rect.left() - second_rect.right(), 0)
        dy = max(second_rect.top() - first_rect.bottom(), first_rect.top() - second_rect.bottom(), 0)
        return dx <= tolerance and dy <= tolerance

    def _create_corner_handle_for_group(
        self,
        group: list[_HandleBindingRecord],
    ) -> None:
        """Create one unified corner handle for a connected splitter group."""
        horizontal_bindings = [
            (record.splitter, record.handle_index)
            for record in group
            if record.orientation == Qt.Orientation.Horizontal
        ]
        vertical_bindings = [
            (record.splitter, record.handle_index)
            for record in group
            if record.orientation == Qt.Orientation.Vertical
        ]
        if not horizontal_bindings or not vertical_bindings:
            return

        overlay_parent = group[0].overlay_parent
        size = self.style.corner_handle_size
        center_x = round(
            sum(record.geometry.center().x() for record in group if record.orientation == Qt.Orientation.Horizontal)
            / len(horizontal_bindings)
        )
        center_y = round(
            sum(record.geometry.center().y() for record in group if record.orientation == Qt.Orientation.Vertical)
            / len(vertical_bindings)
        )

        corner_handle = CornerSplitterHandle(overlay_parent)
        corner_handle.setGeometry(
            center_x - (size // 2) + 1,
            center_y - (size // 2) + 1,
            size,
            size,
        )
        corner_handle.set_binding_groups(
            horizontal_bindings=horizontal_bindings,
            vertical_bindings=vertical_bindings,
        )
        corner_handle.show()
        corner_handle.raise_()
        self._corner_handles.append(corner_handle)

    def _handles_intersect(
        self,
        parent_widget: Any,
        h_handle: QSplitterHandle,
        v_handle: QSplitterHandle,
        tolerance: int = 12,
    ) -> bool:
        """Check if two handles intersect or nearly touch.

        Args:
            parent_widget: Common coordinate system target
            h_handle: Horizontal splitter handle
            v_handle: Vertical splitter handle
            tolerance: Max gap in pixels to still consider as touching

        Returns:
            True if handles share an intersection area
        """
        h_geom = self._handle_geometry_in_parent(parent_widget, h_handle)
        v_geom = self._handle_geometry_in_parent(parent_widget, v_handle)
        if h_geom.intersects(v_geom):
            return True

        dx = max(v_geom.left() - h_geom.right(), h_geom.left() - v_geom.right(), 0)
        dy = max(v_geom.top() - h_geom.bottom(), h_geom.top() - v_geom.bottom(), 0)
        return dx <= tolerance and dy <= tolerance

    def _handle_geometry_in_parent(self, parent_widget: Any, handle: QSplitterHandle) -> Any:
        """Map a splitter handle geometry into parent-widget coordinates.

        Args:
            parent_widget: Common coordinate system target
            handle: Splitter handle whose geometry should be mapped

        Returns:
            QRect-like geometry in parent-widget coordinates
        """
        target_parent = self._resolve_overlay_parent(parent_widget, handle)
        top_left_global = handle.mapToGlobal(handle.rect().topLeft())
        top_left_in_parent = target_parent.mapFromGlobal(top_left_global)
        return handle.rect().translated(top_left_in_parent)

    def _resolve_overlay_parent(self, parent_widget: Any, handle: QSplitterHandle) -> QWidget:
        """Resolve a stable QWidget for coordinate mapping and corner overlay parenting.

        Args:
            parent_widget: Desired parent/container passed by caller
            handle: Reference splitter handle

        Returns:
            QWidget that shares the same window as the handle
        """
        handle_window = handle.window()
        if isinstance(parent_widget, QWidget) and parent_widget.window() == handle_window:
            return parent_widget
        if isinstance(handle_window, QWidget):
            return handle_window
        parent = handle.parentWidget()
        if isinstance(parent, QWidget):
            return parent
        return handle

    def _create_corner_handle_widget(
        self,
        parent_widget: Any,
        h_splitter: QSplitter,
        h_idx: int,
        v_splitter: QSplitter,
        v_idx: int,
        h_handle: QSplitterHandle,
        v_handle: QSplitterHandle,
    ) -> None:
        """Create and position a corner handle widget.

        Args:
            parent_widget: Container widget
            h_splitter: Horizontal splitter
            h_idx: Handle index in horizontal splitter
            v_splitter: Vertical splitter
            v_idx: Handle index in vertical splitter
            h_handle: Horizontal handle widget
            v_handle: Vertical handle widget
        """
        size = self.style.corner_handle_size
        h_geom = self._handle_geometry_in_parent(parent_widget, h_handle)
        v_geom = self._handle_geometry_in_parent(parent_widget, v_handle)

        # The corner X comes from the H-handle (vertical bar): its center X = the dividing X position.
        # The corner Y comes from the V-handle (horizontal bar): its center Y = the dividing Y position.
        center_x = h_geom.center().x()
        center_y = v_geom.center().y()

        overlay_parent = self._resolve_overlay_parent(parent_widget, h_handle)
        corner_handle = CornerSplitterHandle(overlay_parent)
        x_pos = center_x - (size // 2) + 1
        y_pos = center_y - (size // 2) + 1
        corner_handle.setGeometry(
            x_pos,
            y_pos,
            size,
            size,
        )
        corner_handle.set_splitters(h_splitter, h_idx, v_splitter, v_idx)
        corner_handle.set_factory(self)

        corner_handle.show()
        corner_handle.raise_()
        self._corner_handles.append(corner_handle)

    def _install_handle_filters(self, splitter: QSplitter) -> None:
        """Install event filters on all splitter handles for double-click restore.

        Args:
            splitter: QSplitter to install filters on
        """
        if self._handler is None:
            return

        for handle_index in range(1, splitter.count()):
            handle = splitter.handle(handle_index)
            if handle is None:
                continue

            if not bool(handle.property("ws_handle_filter_installed")):
                handle.installEventFilter(self._handler)
                handle.setProperty("ws_handle_filter_installed", True)

    def update_handle_tooltips(
        self,
        splitter: QSplitter,
        panel_count: int | None = None,
        sizes: list[int] | None = None,
    ) -> None:
        """Update tooltips on all handles showing size information.

        Args:
            splitter: QSplitter with handles to update
            panel_count: Total number of panels (optional, detected from sizes)
            sizes: Panel sizes in pixels (optional, detected from splitter)
        """
        if sizes is None:
            sizes = splitter.sizes()

        if not sizes:
            return

        if panel_count is None:
            panel_count = len(sizes)

        total_size = sum(sizes)
        handle_count = max(panel_count - 1, 0)

        for handle_index in range(1, panel_count):
            handle = splitter.handle(handle_index)
            if handle is None:
                continue

            left_size = sizes[handle_index - 1]
            right_size = sizes[handle_index] if handle_index < panel_count else 0
            tooltip = (
                f"Splitter {handle_index}/{handle_count} | Panels: {panel_count}\n"
                f"Größe links: {left_size}px | rechts: {right_size}px | total: {total_size}px\n"
                "Doppelklick: vorheriger Zustand / Standardgröße"
            )
            handle.setToolTip(tooltip)

    def build_standard_sizes(
        self,
        splitter: QSplitter,
        count: int,
        min_remainder: int = 18,
    ) -> list[int]:
        """Build balanced default sizes for a splitter with minimum remainder safety.

        Args:
            splitter: QSplitter to calculate sizes for
            count: Number of panels
            min_remainder: Minimum size for collapsed panels

        Returns:
            List of panel sizes that sum to current splitter dimension
        """
        if count <= 0:
            return []

        current_total = sum(splitter.sizes())
        if current_total <= 0:
            dimension = max(splitter.width(), splitter.height(), count * min_remainder)
            current_total = dimension

        base_size = max(current_total // count, min_remainder)
        sizes = [base_size for _ in range(count)]
        sizes[0] += max(0, current_total - sum(sizes))
        return sizes

    def build_curtain_sizes(
        self,
        splitter: QSplitter,
        side: str,
        min_remainder: int = 18,
        handle_width: int = 3,
    ) -> list[int] | None:
        """Build target sizes with a small remainder for curtain-snap effect.

        Supported ``side`` values:

        * ``"left"``  / ``"top"``    – leftmost / topmost pane expands, rest collapse
        * ``"right"`` / ``"bottom"`` – rightmost / bottommost pane expands, rest collapse
        * ``"collapse_center"``      – centre pane(s) collapse, outer panes expand equally
        * ``"expand_center"``        – outer panes collapse to remainder, centre pane expands

        Args:
            splitter: QSplitter to calculate sizes for
            side: Collapse direction (see above)
            min_remainder: Minimum size for collapsed panels
            handle_width: Width of splitter handles

        Returns:
            List of target panel sizes, or None if invalid configuration
        """
        count = splitter.count()
        if count < 2:
            return None

        total = sum(splitter.sizes())
        if total <= 0:
            return None

        remainder = max(min_remainder, handle_width * 2)
        collapsed_total = remainder * (count - 1)
        main_size = max(total - collapsed_total, remainder)

        # "left" and "top" are equivalent: the first pane in the splitter expands.
        if side in ("left", "top"):
            sizes = [remainder] * count
            sizes[0] = main_size
            return sizes

        # "right" and "bottom": last pane expands.
        if side in ("right", "bottom"):
            sizes = [remainder] * count
            sizes[-1] = main_size
            return sizes

        # "expand_center": middle pane(s) take all the space, outer panes collapse.
        if side == "expand_center":
            sizes = [remainder] * count
            centre = count // 2
            # For even counts give the extra space to the right-centre pane.
            centre_space = max(total - remainder * (count - 1), remainder)
            sizes[centre] = centre_space
            return sizes

        # "collapse_center": outer panes split the space equally, centre collapses.
        if side == "collapse_center":
            sizes = [remainder] * count
            centre = count // 2
            outer_count = count - 1  # centre collapses
            outer_space = max(total - remainder, remainder)
            per_outer = max(outer_space // max(outer_count, 1), remainder)
            for idx in range(count):
                if idx != centre:
                    sizes[idx] = per_outer
            # Adjust rounding remainder into first outer pane.
            rounding = total - sum(sizes)
            sizes[0] = max(remainder, sizes[0] + rounding)
            return sizes

        # Unknown side – fall back to right.
        sizes = [remainder] * count
        sizes[-1] = main_size
        return sizes

    # ------------------------------------------------------------------
    # Dock-area title-bar collapse synchronisation
    # ------------------------------------------------------------------

    #: Pixel threshold below which a pane is considered "collapsed".
    #: ADS title bar is ~26 px; 38 px gives a small safety margin.
    _TITLE_BAR_THRESHOLD: int = 38

    def sync_dock_area_collapse(self, splitter: QSplitter) -> None:
        """Show or hide CDockAreaWidget title bars based on current pane sizes.

        Design rules that avoid the ghost-widget / jitter traps:

        1. Only inspect DIRECT children of ``splitter`` via ``widget(i)`` –
           never ``findChildren(QSplitter)``.  Nested splitters are reached
           by the caller (``sync_all_dock_area_collapse``) which walks the
           full tree in a single, non-recursive pass.

        2. Collapse state is guarded by a ``ws_dock_collapsed`` property so
           the show/hide API is called **only on transitions**, not on every
           drag event.

        3. ``tabBar()`` is on the *title bar*, not directly on the dock area.

        Args:
            splitter: The QSplitter whose direct children should be inspected.
        """
        is_horizontal = splitter.orientation() == Qt.Orientation.Horizontal
        sizes = splitter.sizes()

        try:
            import PySide6QtAds as QtAds  # noqa: PLC0415
            _dock_area_type: Any = QtAds.CDockAreaWidget
        except (ImportError, AttributeError):
            _dock_area_type = None

        for pane_index, pane_size in enumerate(sizes):
            child = splitter.widget(pane_index)
            if child is None:
                continue

            collapsed = pane_size < self._TITLE_BAR_THRESHOLD

            # The direct child is either a CDockAreaWidget or another QSplitter.
            # For nested splitters the outer size governs: if the whole pane is
            # below threshold we collapse every dock area inside it; if above we
            # expand them.  We only touch DIRECT dock-area children here because
            # the nested splitters own their own sizing – those are handled when
            # sync_all_dock_area_collapse calls us on the nested splitter itself.
            if _dock_area_type is not None and isinstance(child, _dock_area_type):
                self._set_dock_area_collapsed(child, collapsed=collapsed, is_horizontal=is_horizontal)
            elif _dock_area_type is not None:
                # Child is a nested QSplitter or intermediate container.
                # Propagate the outer collapse state to every dock area inside it.
                for dock_area in child.findChildren(_dock_area_type):
                    self._set_dock_area_collapsed(dock_area, collapsed=collapsed, is_horizontal=is_horizontal)

    def _set_dock_area_collapsed(
        self,
        dock_area: Any,
        *,
        collapsed: bool,
        is_horizontal: bool,
    ) -> None:
        """Toggle title-bar / tab-bar visibility for a single CDockAreaWidget.

        Calls are no-ops when the state has not changed to avoid redundant
        Qt paint cycles that cause flicker.

        Args:
            dock_area: CDockAreaWidget instance
            collapsed: True when the pane is below the collapse threshold
            is_horizontal: True when the parent splitter is horizontal
        """
        already_collapsed = bool(dock_area.property("ws_dock_collapsed"))
        if already_collapsed == collapsed:
            return  # State unchanged – nothing to do, no repaint triggered.

        dock_area.setProperty("ws_dock_collapsed", collapsed)

        title_bar = None
        try:
            if hasattr(dock_area, "titleBar"):
                title_bar = dock_area.titleBar()
        except RuntimeError:
            return  # C++ object already deleted.

        # Tab bar lives on the title bar, NOT on the dock area itself.
        tab_bar = None
        if title_bar is not None:
            try:
                if hasattr(title_bar, "tabBar"):
                    tab_bar = title_bar.tabBar()
            except RuntimeError:
                tab_bar = None

        if collapsed:
            if title_bar is not None:
                title_bar.setVisible(False)
            if tab_bar is not None:
                tab_bar.setVisible(False)
            # Allow the widget to shrink to zero along the split axis.
            if is_horizontal:
                dock_area.setMinimumWidth(0)
            else:
                dock_area.setMinimumHeight(0)
        else:
            # Restore – title bar needs at least 26 px so it is usable.
            if is_horizontal:
                dock_area.setMinimumWidth(0)
            else:
                dock_area.setMinimumHeight(26)
            if title_bar is not None:
                title_bar.setVisible(True)
            if tab_bar is not None:
                tab_bar.setVisible(True)

    def sync_all_dock_area_collapse(self, root_widget: Any) -> None:
        """Synchronise title-bar collapse state for every splitter under root_widget.

        Walks ALL splitters in a single flat pass (no recursion) to avoid
        the O(N²) cost of nested findChildren calls.

        Args:
            root_widget: CDockManager or any container widget.
        """
        if root_widget is None:
            return
        # findChildren returns the full tree; each splitter is visited once.
        for splitter in root_widget.findChildren(QSplitter):
            self.sync_dock_area_collapse(splitter)


class SplitterEventHandler(QObject):
    """Event handler for splitter interactions with state tracking and restoration.

    Manages:
    - Splitter size state (default, current, previous)
    - Double-click restore functionality on handles
    - Toolbar drag-and-drop interactions
    """

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize event handler.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self._splitter_default_sizes: dict[int, list[int]] = {}
        self._splitter_current_sizes: dict[int, list[int]] = {}
        self._splitter_previous_sizes: dict[int, list[int]] = {}
        self._factory: SplitterFactory | None = None
        self._on_restore_callback: Callable[[QSplitter, str], None] | None = None
        self._min_remainder: int = 18
        self._last_drag_global_pos: dict[int, QPoint] = {}
        self._active_drag_handle_index: dict[int, int] = {}
        self._active_drag_button: dict[int, Qt.MouseButton] = {}
        self._active_drag_edge: dict[int, str] = {}

    def set_factory(self, factory: SplitterFactory) -> None:
        """Set the factory for style/size calculations.

        Args:
            factory: SplitterFactory instance
        """
        self._factory = factory

    def set_restore_callback(self, callback: Callable[[QSplitter, str], None]) -> None:
        """Set callback function when splitter restored via double-click.

        Args:
            callback: Function(splitter, mode_str) called after restore
        """
        self._on_restore_callback = callback

    def set_min_remainder(self, min_remainder: int) -> None:
        """Set minimum size for collapsed panels.

        Args:
            min_remainder: Minimum size in pixels
        """
        self._min_remainder = min_remainder

    def track_splitter(self, splitter: QSplitter) -> None:
        """Initialize state tracking for a splitter.

        Args:
            splitter: QSplitter to track
        """
        splitter_key = id(splitter)
        current_sizes = splitter.sizes()

        if splitter_key not in self._splitter_default_sizes:
            self._splitter_default_sizes[splitter_key] = list(current_sizes)

        if splitter_key not in self._splitter_current_sizes:
            self._splitter_current_sizes[splitter_key] = list(current_sizes)

        if splitter_key not in self._splitter_previous_sizes:
            self._splitter_previous_sizes[splitter_key] = list(current_sizes)

    def on_splitter_moved(self, splitter: QSplitter) -> None:
        """Called when splitter sizes change (user drag or programmatic).

        Args:
            splitter: QSplitter that moved
        """
        splitter_key = id(splitter)
        new_sizes = splitter.sizes()
        current_sizes = self._splitter_current_sizes.get(splitter_key)

        if current_sizes is not None and current_sizes != new_sizes:
            self._splitter_previous_sizes[splitter_key] = list(current_sizes)

        self._splitter_current_sizes[splitter_key] = list(new_sizes)

        if self._factory is not None:
            self._factory.update_handle_tooltips(splitter)
            self._factory.sync_dock_area_collapse(splitter)

    def restore_splitter(self, splitter: QSplitter) -> None:
        """Restore splitter to previous state or default (double-click restore).

        Args:
            splitter: QSplitter to restore
        """
        splitter_key = id(splitter)
        current_sizes = splitter.sizes()
        previous_sizes = self._splitter_previous_sizes.get(splitter_key)
        default_sizes = self._splitter_default_sizes.get(splitter_key)

        # Choose restore target prioritizing previous state
        if (
            previous_sizes
            and previous_sizes != current_sizes
            and len(previous_sizes) == splitter.count()
        ):
            target_sizes = list(previous_sizes)
            restore_mode = "vorheriger Zustand"
        elif default_sizes and len(default_sizes) == splitter.count():
            target_sizes = list(default_sizes)
            restore_mode = "Standardgröße"
        else:
            if self._factory is None:
                return
            target_sizes = self._factory.build_standard_sizes(splitter, splitter.count(), self._min_remainder)
            restore_mode = "berechnete Standardgröße"

        # Apply restore and update tracking
        self._splitter_previous_sizes[splitter_key] = list(current_sizes)
        self._splitter_current_sizes[splitter_key] = list(target_sizes)
        splitter.setSizes(target_sizes)

        if self._factory is not None:
            self._factory.update_handle_tooltips(splitter)

        if self._on_restore_callback is not None:
            self._on_restore_callback(splitter, restore_mode)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle splitter handle double-click events.

        Args:
            obj: Object receiving event
            event: QEvent to filter

        Returns:
            True if event consumed, False to pass to default handler
        """
        if isinstance(obj, QSplitterHandle) and event.type() == QEvent.Type.MouseButtonDblClick:
            # Find parent splitter
            parent = obj.parent()
            while parent is not None and not isinstance(parent, QSplitter):
                parent = parent.parent()

            if isinstance(parent, QSplitter):
                self.restore_splitter(parent)
                return True

        if not isinstance(obj, QSplitterHandle):
            return False

        parent = obj.parent()
        while parent is not None and not isinstance(parent, QSplitter):
            parent = parent.parent()

        if not isinstance(parent, QSplitter):
            return False

        splitter = parent
        splitter_key = id(splitter)

        handle_index = -1
        for index in range(1, splitter.count()):
            if splitter.handle(index) is obj:
                handle_index = index
                break

        if handle_index <= 0:
            return False

        mouse_event: Any = event

        if event.type() == QEvent.Type.MouseButtonPress:
            if (
                callable(getattr(mouse_event, "button", None))
                and callable(getattr(mouse_event, "globalPos", None))
                and mouse_event.button() in {Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton}
            ):
                self._active_drag_handle_index[splitter_key] = handle_index
                self._active_drag_button[splitter_key] = mouse_event.button()
                self._last_drag_global_pos[splitter_key] = mouse_event.globalPos()
                self._active_drag_edge.pop(splitter_key, None)
            return False

        if event.type() == QEvent.Type.MouseMove:
            if not (
                callable(getattr(mouse_event, "buttons", None))
                and callable(getattr(mouse_event, "globalPos", None))
            ):
                return False

            drag_button = self._active_drag_button.get(splitter_key)
            if drag_button is None:
                return False

            if not (mouse_event.buttons() & drag_button):
                return False

            previous_global = self._last_drag_global_pos.get(splitter_key)
            current_global = mouse_event.globalPos()
            self._last_drag_global_pos[splitter_key] = current_global
            if previous_global is None or self._factory is None:
                return False

            movement = current_global - previous_global
            axis_delta = movement.x() if splitter.orientation() == Qt.Orientation.Horizontal else movement.y()
            if axis_delta == 0:
                return False

            tracked_handle_index = self._active_drag_handle_index.get(splitter_key, handle_index)

            # RMB = precision mode (no cascade), LMB = cascade mode.
            if drag_button == Qt.MouseButton.RightButton:
                return False

            direction = -1 if axis_delta < 0 else 1
            drag_step = abs(axis_delta)

            edge_hint = self._active_drag_edge.get(splitter_key)
            if edge_hint is None:
                range_values = splitter.getRange(tracked_handle_index)
                tracked_handle = splitter.handle(tracked_handle_index)
                if (
                    isinstance(range_values, tuple)
                    and len(range_values) == 2
                    and tracked_handle is not None
                ):
                    min_pos, max_pos = range_values
                    current_pos = (
                        tracked_handle.x()
                        if splitter.orientation() == Qt.Orientation.Horizontal
                        else tracked_handle.y()
                    )
                    collapse_snap = self._factory.get_collapse_snap_distance(splitter)
                    if current_pos <= min_pos + collapse_snap:
                        edge_hint = "min"
                    elif current_pos >= max_pos - collapse_snap:
                        edge_hint = "max"

            if edge_hint is not None:
                self._active_drag_edge[splitter_key] = edge_hint

            QTimer.singleShot(
                0,
                lambda tracked_splitter=splitter, tracked_index=tracked_handle_index, tracked_direction=direction, tracked_step=drag_step, tracked_edge=edge_hint: self._apply_runtime_cascade(
                    tracked_splitter,
                    tracked_index,
                    tracked_direction,
                    tracked_step,
                    tracked_edge,
                ),
            )
            return False

        if event.type() == QEvent.Type.MouseButtonRelease:
            self._last_drag_global_pos.pop(splitter_key, None)
            self._active_drag_handle_index.pop(splitter_key, None)
            self._active_drag_button.pop(splitter_key, None)
            self._active_drag_edge.pop(splitter_key, None)
            return False

        return False

    def _apply_runtime_cascade(
        self,
        splitter: QSplitter,
        handle_index: int,
        direction: int,
        drag_step: int,
        edge_hint: str | None,
    ) -> None:
        """Apply hierarchical cascade immediately after native splitter move updates."""
        if self._factory is None:
            return

        applied = self._factory.apply_hierarchical_drag_cascade(
            splitter,
            handle_index,
            direction,
            drag_step,
            edge_hint=edge_hint,
        )
        if not applied:
            return

        splitter_key = id(splitter)
        sizes = splitter.sizes()
        self._splitter_current_sizes[splitter_key] = list(sizes)
        self._factory.update_handle_tooltips(splitter)
        self._factory.sync_dock_area_collapse(splitter)
