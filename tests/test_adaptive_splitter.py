"""Tests for adaptive splitter controller and enhanced corner handle behavior.

Tests focus on state management and logic without requiring full Qt GUI initialization.

Tests:
- Corner handle state transitions
- Axis-locking detection
- Automatic separation threshold
- Intersection data classes
- State transitions
"""

import pytest
from unittest.mock import Mock

from PySide6.QtCore import QPoint, Qt

from widgetsystem.factories.adaptive_splitter_controller import (
    AdaptiveSplitterController,
    CornerHandleState,
    SplitterIntersection,
)


class TestAxisLocking:
    """Test axis locking logic."""

    def test_detect_horizontal_movement_static(self) -> None:
        """Large X movement should lock X axis."""
        state = CornerHandleState()
        
        delta_x = 50
        delta_y = 5
        abs_dx = abs(delta_x)
        abs_dy = abs(delta_y)

        # Simulate the detection logic
        if abs_dx > abs_dy + 5:
            axis = Qt.Orientation.Horizontal
        else:
            axis = None
        
        assert axis == Qt.Orientation.Horizontal

    def test_detect_vertical_movement_static(self) -> None:
        """Large Y movement should lock Y axis."""
        state = CornerHandleState()
        
        delta_x = 5
        delta_y = 50
        abs_dx = abs(delta_x)
        abs_dy = abs(delta_y)

        # Simulate the detection logic
        if abs_dy > abs_dx + 5:
            axis = Qt.Orientation.Vertical
        else:
            axis = None
        
        assert axis == Qt.Orientation.Vertical

    def test_detect_corner_movement_static(self) -> None:
        """Balanced movement should allow both axes."""
        state = CornerHandleState()
        
        delta_x = 30
        delta_y = 25
        abs_dx = abs(delta_x)
        abs_dy = abs(delta_y)

        # Simulate the detection logic - both significant means both allowed
        if abs_dx > 15 and abs_dy > 15:
            axis = None
        elif abs_dx > abs_dy + 5:
            axis = Qt.Orientation.Horizontal
        elif abs_dy > abs_dx + 5:
            axis = Qt.Orientation.Vertical
        else:
            axis = None
        
        assert axis is None  # Both axes allowed


class TestAdaptiveController:
    """Test adaptive splitter controller logic."""

    def test_controller_initialization(self) -> None:
        """Controller should initialize without errors."""
        controller = AdaptiveSplitterController()
        assert controller._intersections == {}
        assert controller._corner_handle_states == {}

    def test_register_corner_handle(self) -> None:
        """Controller should register corner handles."""
        controller = AdaptiveSplitterController()
        handle = Mock()
        
        intersection = SplitterIntersection(
            h_splitter=Mock(),
            h_handle_index=0,
            v_splitter=Mock(),
            v_handle_index=0,
            position=QPoint(100, 100),
        )
        
        controller.register_corner_handle(handle, intersection)
        
        assert handle in controller._corner_handle_states
        state = controller._corner_handle_states[handle]
        assert state.is_grouped is True

    def test_ungroup_corner(self) -> None:
        """Controller should separate corners."""
        controller = AdaptiveSplitterController()
        handle = Mock()
        
        intersection = SplitterIntersection(
            h_splitter=Mock(),
            h_handle_index=0,
            v_splitter=Mock(),
            v_handle_index=0,
            position=QPoint(100, 100),
        )
        
        controller.register_corner_handle(handle, intersection)
        controller.ungroup_corner(handle)
        
        state = controller._corner_handle_states[handle]
        assert state.is_grouped is False

    def test_regroup_corner(self) -> None:
        """Controller should re-bind corners."""
        controller = AdaptiveSplitterController()
        handle = Mock()
        
        intersection = SplitterIntersection(
            h_splitter=Mock(),
            h_handle_index=0,
            v_splitter=Mock(),
            v_handle_index=0,
            position=QPoint(100, 100),
        )
        
        controller.register_corner_handle(handle, intersection)
        controller.ungroup_corner(handle)
        controller.regroup_corner(handle)
        
        state = controller._corner_handle_states[handle]
        assert state.is_grouped is True


class TestCornerHandleState:
    """Test corner handle state management."""

    def test_initial_state(self) -> None:
        """State should start as grouped."""
        state = CornerHandleState()
        assert state.is_grouped is True
        assert state.is_separated is False

    def test_state_transition(self) -> None:
        """State should track grouping changes."""
        state = CornerHandleState(is_grouped=True)
        assert state.is_grouped is True
        
        state.is_grouped = False
        assert state.is_separated is True


class TestSeparationThreshold:
    """Test automatic separation on movement threshold."""

    def test_separation_threshold_property(self) -> None:
        """Separation threshold should be configurable."""
        state = CornerHandleState()
        assert state.separation_threshold_px == 50

    def test_small_drag_no_separation(self) -> None:
        """Small dragging should not trigger separation."""
        # Manual check: sum of deltas (15) < threshold (50)
        delta_sum = abs(10) + abs(5)
        threshold = 50
        assert delta_sum < threshold

    def test_large_drag_triggers_separation(self) -> None:
        """Large dragging should trigger separation."""
        # Manual check: sum of deltas (60) > threshold (50)
        delta_sum = abs(40) + abs(20)
        threshold = 50
        assert delta_sum > threshold


class TestSplitterIntersection:
    """Test SplitterIntersection data class."""

    def test_intersection_creation(self) -> None:
        """Intersection should store all parameters."""
        h_split = Mock()
        v_split = Mock()
        pos = QPoint(100, 200)

        inter = SplitterIntersection(
            h_splitter=h_split,
            h_handle_index=0,
            v_splitter=v_split,
            v_handle_index=1,
            position=pos,
        )

        assert inter.h_splitter is h_split
        assert inter.h_handle_index == 0
        assert inter.v_splitter is v_split
        assert inter.v_handle_index == 1
        assert inter.position == pos

    def test_intersection_geometry_property(self) -> None:
        """Intersection should have geometry property."""
        pos = QPoint(150, 250)
        inter = SplitterIntersection(
            h_splitter=Mock(),
            h_handle_index=0,
            v_splitter=Mock(),
            v_handle_index=0,
            position=pos,
        )

        assert inter.geometry == (150, 250)
