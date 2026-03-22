"""Unit tests for Phase 2 - FloatingStateTracker.

Tests for the FloatingStateTracker class that ensures title bar button
persistence when panels are floated and re-docked.
"""

from pathlib import Path
import sys
from unittest.mock import Mock, patch

import pytest


# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.ui.floating_state_tracker import FloatingStateTracker


class TestFloatingStateTracker:
    """Test suite for FloatingStateTracker class."""

    @pytest.fixture
    def mock_dock_manager(self):
        """Create a mock CDockManager."""
        manager = Mock()
        manager.dockWidgetAboutToBeFloated = Mock()
        manager.dockWidgetAboutToBeFloated.connect = Mock()
        manager.floatingWidgetCreated = Mock()
        manager.floatingWidgetCreated.connect = Mock()
        manager.dockWidgetAdded = Mock()
        manager.dockWidgetAdded.connect = Mock()
        return manager

    @pytest.fixture
    def tracker(self, mock_dock_manager):
        """Create FloatingStateTracker instance."""
        return FloatingStateTracker(mock_dock_manager)

    def test_initialization(self, tracker, mock_dock_manager):
        """Test tracker initialization."""
        assert tracker.dock_manager == mock_dock_manager
        assert isinstance(tracker._floating_widgets, dict)
        assert isinstance(tracker._pending_refreshes, set)
        assert len(tracker._floating_widgets) == 0
        assert len(tracker._pending_refreshes) == 0

    def test_signal_connections(self, mock_dock_manager):
        """Test that signals are connected on initialization."""
        tracker = FloatingStateTracker(mock_dock_manager)

        # Verify signals were connected
        assert mock_dock_manager.dockWidgetAboutToBeFloated.connect.called
        assert mock_dock_manager.floatingWidgetCreated.connect.called
        assert mock_dock_manager.dockWidgetAdded.connect.called

    def test_widget_about_to_float(self, tracker):
        """Test tracking when widget is about to float."""
        widget = Mock()
        widget.windowTitle.return_value = "Test Widget"

        tracker._on_widget_about_to_float(widget)

        widget_id = id(widget)
        assert widget_id in tracker._floating_widgets
        assert tracker._floating_widgets[widget_id] is True

    def test_floating_widget_created(self, tracker):
        """Test handling of floating container creation."""
        container = Mock()

        # Should not raise exception
        tracker._on_floating_widget_created(container)

        # No specific state changes expected
        assert len(tracker._floating_widgets) == 0

    def test_widget_added_not_previously_floating(self, tracker):
        """Test widget added that was not previously floating."""
        widget = Mock()
        widget.windowTitle.return_value = "Test Widget"

        tracker._on_dock_widget_added(widget)

        # Should not schedule refresh for widget that wasn't floating
        widget_id = id(widget)
        assert widget_id not in tracker._pending_refreshes

    def test_widget_added_was_floating(self, tracker):
        """Test widget added that was previously floating (re-docked)."""
        widget = Mock()
        widget.windowTitle.return_value = "Test Widget"
        widget_id = id(widget)

        # Mark as floating first
        tracker._floating_widgets[widget_id] = True

        with patch.object(tracker, "_refresh_title_bar"):
            tracker._on_dock_widget_added(widget)

        # Should mark as no longer floating
        assert tracker._floating_widgets[widget_id] is False

        # Should schedule refresh
        assert widget_id in tracker._pending_refreshes

    def test_is_widget_floating_true(self, tracker):
        """Test checking if widget is floating (when it is)."""
        widget = Mock()
        widget_id = id(widget)
        tracker._floating_widgets[widget_id] = True

        assert tracker.is_widget_floating(widget) is True

    def test_is_widget_floating_false(self, tracker):
        """Test checking if widget is floating (when it isn't)."""
        widget = Mock()
        widget_id = id(widget)
        tracker._floating_widgets[widget_id] = False

        assert tracker.is_widget_floating(widget) is False

    def test_is_widget_floating_unknown(self, tracker):
        """Test checking if widget is floating (unknown widget)."""
        widget = Mock()

        # Unknown widget should return False
        assert tracker.is_widget_floating(widget) is False

    def test_get_floating_widgets(self, tracker):
        """Test getting all floating widget states."""
        widget1 = Mock()
        widget2 = Mock()
        widget3 = Mock()

        tracker._floating_widgets[id(widget1)] = True
        tracker._floating_widgets[id(widget2)] = False
        tracker._floating_widgets[id(widget3)] = True

        floating_states = tracker.get_floating_widgets()

        assert isinstance(floating_states, dict)
        assert len(floating_states) == 3
        assert floating_states[id(widget1)] is True
        assert floating_states[id(widget2)] is False
        assert floating_states[id(widget3)] is True

    def test_refresh_title_bar_no_pending(self, tracker):
        """Test title bar refresh when not pending."""
        widget = Mock()
        widget.windowTitle.return_value = "Test Widget"

        # Should do nothing if not pending
        tracker._refresh_title_bar(widget)

        # Widget methods should not be called
        if hasattr(widget, "dockAreaWidget"):
            assert not widget.dockAreaWidget.called

    def test_refresh_title_bar_pending(self, tracker):
        """Test title bar refresh when pending."""
        widget = Mock()
        widget.windowTitle.return_value = "Test Widget"
        widget_id = id(widget)

        # Mock dock area and title bar
        mock_area = Mock()
        mock_title_bar = Mock()
        mock_area.titleBar.return_value = mock_title_bar
        widget.dockAreaWidget.return_value = mock_area

        # Mark as pending
        tracker._pending_refreshes.add(widget_id)

        tracker._refresh_title_bar(widget)

        # Should have called titleBar methods
        assert widget.dockAreaWidget.called
        assert mock_area.titleBar.called
        assert mock_title_bar.setVisible.called

        # Should be removed from pending
        assert widget_id not in tracker._pending_refreshes

    def test_refresh_title_bar_no_area(self, tracker):
        """Test title bar refresh when widget has no area."""
        widget = Mock()
        widget.windowTitle.return_value = "Test Widget"
        widget_id = id(widget)
        widget.dockAreaWidget.return_value = None

        # Mark as pending
        tracker._pending_refreshes.add(widget_id)

        tracker._refresh_title_bar(widget)

        # Should be removed from pending even if failed
        assert widget_id not in tracker._pending_refreshes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
