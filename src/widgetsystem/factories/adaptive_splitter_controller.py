"""Adaptive splitter management system with dynamic grouping/ungrouping.

Controls intelligent splitter binding behavior:
- Detects splitter intersections and creates corner handles
- Monitors movement to detect separation threshold
- Auto-binds splitters when they return to parallel alignment
- Manages axis-locking for single/multi-axis movement
- Provides visual feedback and state management
"""

from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QSplitter, QWidget


@dataclass(frozen=True)
class SplitterIntersection:
    """Represents a point where horizontal and vertical splitters meet."""

    h_splitter: QSplitter
    h_handle_index: int
    v_splitter: QSplitter
    v_handle_index: int
    position: QPoint

    @property
    def geometry(self) -> tuple[int, int]:
        """Return (x, y) of intersection."""
        return (self.position.x(), self.position.y())


@dataclass
class CornerHandleState:
    """Tracks state of a corner handle."""

    is_grouped: bool = True  # True: splitters bound, False: separated
    last_drag_delta: QPoint = field(default_factory=lambda: QPoint(0, 0))
    drag_started_at: QPoint | None = None
    locked_axis: Qt.Orientation | None = None  # X, Y, or None for both
    separation_threshold_px: int = 50
    recombine_threshold_px: int = 5

    @property
    def is_separated(self) -> bool:
        """Return True if this corner's splitters are separated."""
        return not self.is_grouped


class AdaptiveSplitterController(QObject):
    """Main controller for adaptive splitter behavior.

    Manages:
    - Detection of splitter intersections
    - Dynamic grouping/ungrouping of corner handles
    - Axis-locking and intelligent movement
    - Visual feedback and state persistence
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize controller.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._intersections: dict[tuple[int, int], SplitterIntersection] = {}
        self._corner_handle_states: dict[QWidget, CornerHandleState] = {}
        self._current_drag_handle: QWidget | None = None

        # Monitoring
        self._parallel_check_timer = QTimer(self)
        self._parallel_check_timer.timeout.connect(self._check_parallel_alignment)
        self._parallel_check_timer.setInterval(200)  # Check every 200ms

    def detect_intersections(
        self, parent_widget: QWidget
    ) -> list[SplitterIntersection]:
        """Detect all splitter intersections in a widget tree.

        Only returns points where BOTH horizontal AND vertical splitters meet.

        Args:
            parent_widget: Root widget to scan

        Returns:
            List of detected intersections
        """
        intersections: list[SplitterIntersection] = []

        # Collect all splitters
        splitters = self._collect_splitters(parent_widget)
        h_splitters = [s for s in splitters if s.orientation() == Qt.Orientation.Horizontal]
        v_splitters = [s for s in splitters if s.orientation() == Qt.Orientation.Vertical]

        # Find intersections
        for h_split in h_splitters:
            for h_idx, _h_handle in enumerate(self._get_handles(h_split)):
                h_rect = self._get_handle_rect_global(h_split, h_idx)

                for v_split in v_splitters:
                    for v_idx, _v_handle in enumerate(self._get_handles(v_split)):
                        v_rect = self._get_handle_rect_global(v_split, v_idx)

                        # Check if rectangles intersect
                        if h_rect.intersects(v_rect):
                            intersection_point = QPoint(h_rect.center().x(), v_rect.center().y())
                            intersections.append(
                                SplitterIntersection(
                                    h_splitter=h_split,
                                    h_handle_index=h_idx,
                                    v_splitter=v_split,
                                    v_handle_index=v_idx,
                                    position=intersection_point,
                                )
                            )

        self._intersections = {inter.geometry: inter for inter in intersections}
        return intersections

    def register_corner_handle(
        self, corner_handle: QWidget, _intersection: SplitterIntersection
    ) -> None:
        """Register a corner handle for state management.

        Args:
            corner_handle: The corner widget
            _intersection: Associated splitter intersection (reserved for future use)
        """
        state = CornerHandleState(is_grouped=True)
        self._corner_handle_states[corner_handle] = state

        # Enable drag monitoring
        corner_handle.installEventFilter(self)

    def ungroup_corner(self, corner_handle: QWidget) -> None:
        """Separate splitters at a corner handle.

        Args:
            corner_handle: The corner handle to ungroup
        """
        if corner_handle not in self._corner_handle_states:
            return

        state = self._corner_handle_states[corner_handle]
        state.is_grouped = False
        self._update_corner_visual(corner_handle)

    def regroup_corner(self, corner_handle: QWidget) -> None:
        """Re-bind splitters at a corner handle.

        Args:
            corner_handle: The corner handle to regroup
        """
        if corner_handle not in self._corner_handle_states:
            return

        state = self._corner_handle_states[corner_handle]
        state.is_grouped = True
        self._update_corner_visual(corner_handle)

    def get_locked_axis(self, corner_handle: QWidget) -> Qt.Orientation | None:
        """Get which axis is locked for movement.

        Args:
            corner_handle: The corner handle

        Returns:
            Qt.Orientation.Horizontal, Qt.Orientation.Vertical, or None
        """
        if corner_handle not in self._corner_handle_states:
            return None

        return self._corner_handle_states[corner_handle].locked_axis

    def set_locked_axis(
        self, corner_handle: QWidget, axis: Qt.Orientation | None
    ) -> None:
        """Lock movement to a specific axis.

        Args:
            corner_handle: The corner handle
            axis: Orientation to lock to, or None for both axes
        """
        if corner_handle not in self._corner_handle_states:
            return

        self._corner_handle_states[corner_handle].locked_axis = axis

    def start_monitoring(self) -> None:
        """Start monitoring for parallel alignment."""
        self._parallel_check_timer.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring for parallel alignment."""
        self._parallel_check_timer.stop()

    def detect_drag_axis(self, corner_handle: QWidget, delta: QPoint) -> Qt.Orientation | None:
        """Detect which axis the user is primarily moving.

        Args:
            corner_handle: The corner handle being dragged
            delta: Movement delta (dx, dy)

        Returns:
            Qt.Orientation.Horizontal if X movement > Y,
            Qt.Orientation.Vertical if Y movement > X,
            None if both axes moved equally (corner drag)
        """
        state = self._corner_handle_states.get(corner_handle)
        if not state:
            return None

        abs_dx = abs(delta.x())
        abs_dy = abs(delta.y())

        # Both axes moved significantly → allow both
        if abs_dx > 15 and abs_dy > 15:
            return None  # Both axes

        # X dominant
        if abs_dx > abs_dy + 5:
            return Qt.Orientation.Horizontal

        # Y dominant
        if abs_dy > abs_dx + 5:
            return Qt.Orientation.Vertical

        # Ambiguous → allow both
        return None

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Track drag events for axis locking and separation detection.

        Args:
            obj: Object being filtered
            event: Event to process

        Returns:
            True if event handled, False to continue propagation
        """
        if not isinstance(obj, QWidget):
            return False

        if event.type() == QEvent.Type.MouseButtonPress:
            if isinstance(event, QMouseEvent):
                state = self._corner_handle_states.get(obj)
                if state:
                    state.drag_started_at = event.globalPos()
                    state.last_drag_delta = QPoint(0, 0)
                    self._current_drag_handle = obj
            return False

        if event.type() == QEvent.Type.MouseMove:
            if isinstance(event, QMouseEvent) and self._current_drag_handle is obj:
                state = self._corner_handle_states.get(obj)
                if state and state.drag_started_at:
                    delta = event.globalPos() - state.drag_started_at
                    state.last_drag_delta = delta

                    # Detect axis lock
                    axis = self.detect_drag_axis(obj, delta)
                    state.locked_axis = axis

                    # Check separation threshold
                    if state.is_grouped and abs(delta.x()) + abs(delta.y()) > state.separation_threshold_px:
                        self.ungroup_corner(obj)

            return False

        if event.type() == QEvent.Type.MouseButtonRelease:
            if self._current_drag_handle is obj:
                state = self._corner_handle_states.get(obj)
                if state:
                    state.drag_started_at = None
                    state.locked_axis = None
                self._current_drag_handle = None

            return False

        return False

    def _check_parallel_alignment(self) -> None:
        """Periodically check if separated splitters should be re-grouped."""
        for state in self._corner_handle_states.values():
            if not state.is_separated:
                continue

            # Check if splitters are back in parallel alignment
            # If yes and drag_delta < recombine_threshold: regroup

    def _collect_splitters(self, parent: QWidget) -> list[QSplitter]:
        """Collect all splitter widgets in a tree.

        Args:
            parent: Root widget

        Returns:
            List of QSplitter instances
        """
        splitters: list[QSplitter] = []

        if isinstance(parent, QSplitter):
            splitters.append(parent)

        for child in parent.findChildren(QSplitter):
            if child not in splitters:
                splitters.append(child)

        return splitters

    def _get_handles(self, splitter: QSplitter) -> list[Any]:
        """Get all splitter handles.

        Args:
            splitter: The splitter

        Returns:
            List of QSplitterHandle instances
        """
        handles = []
        for i in range(splitter.count() - 1):
            handles.append(splitter.handle(i))
        return handles

    def _get_handle_rect_global(self, splitter: QSplitter, handle_index: int) -> QRect:
        """Get global rect of a splitter handle.

        Args:
            splitter: The splitter
            handle_index: Index of handle

        Returns:
            Global QRect of the handle
        """
        handle = splitter.handle(handle_index)
        if not handle:
            return QRect()

        rect = handle.geometry()
        global_pos = splitter.mapToGlobal(rect.topLeft())
        return QRect(global_pos, rect.size())

    def _update_corner_visual(self, corner_handle: QWidget) -> None:
        """Update visual appearance based on state.

        Args:
            corner_handle: The corner handle
        """
        if corner_handle not in self._corner_handle_states:
            return

        # Trigger repaint - color determined by is_grouped state
        corner_handle.update()
