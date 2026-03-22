"""Phase 1 Tests - Tab Selector Visibility.

Tests for TabSelectorMonitor, TabSelectorEventHandler, and
TabSelectorVisibilityController.

These tests verify that:
1. TabSelectorMonitor correctly tracks tab counts
2. Event handlers properly update tab counts
3. Visibility controller shows/hides selectors based on tab count
"""

from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication
import pytest

from widgetsystem.ui.tab_selector_event_handler import TabSelectorEventHandler
from widgetsystem.ui.tab_selector_monitor import TabSelectorMonitor
from widgetsystem.ui.tab_selector_visibility_controller import TabSelectorVisibilityController


class TestTabSelectorMonitor:
    """Test suite for TabSelectorMonitor class."""

    def test_init(self) -> None:
        """Test TabSelectorMonitor initialization."""
        monitor = TabSelectorMonitor()
        assert monitor._area_tab_counts == {}
        assert monitor._monitored_areas == {}

    def test_register_dock_area(self) -> None:
        """Test registering a dock area."""
        monitor = TabSelectorMonitor()
        area_widget = Mock()

        monitor.register_dock_area("area_1", area_widget)

        assert "area_1" in monitor._monitored_areas
        assert "area_1" in monitor._area_tab_counts

    def test_unregister_dock_area(self) -> None:
        """Test unregistering a dock area."""
        monitor = TabSelectorMonitor()
        area_widget = Mock()

        monitor.register_dock_area("area_1", area_widget)
        assert "area_1" in monitor._monitored_areas

        monitor.unregister_dock_area("area_1")
        assert "area_1" not in monitor._monitored_areas
        assert "area_1" not in monitor._area_tab_counts

    def test_update_tab_count(self) -> None:
        """Test updating tab count."""
        monitor = TabSelectorMonitor()
        area_widget = Mock()
        area_widget.dockWidgetsCount = Mock(return_value=1)

        monitor.register_dock_area("area_1", area_widget)
        monitor._area_tab_counts["area_1"] = 1

        slot = Mock()
        monitor.tab_count_changed.connect(slot)
        monitor.update_tab_count("area_1", 2)

        app = QApplication.instance() or QApplication([])
        app.processEvents()

        assert monitor._area_tab_counts["area_1"] == 2
        slot.assert_called_once_with("area_1", 2)

    def test_update_tab_count_invalid_area(self) -> None:
        """Test updating tab count for invalid area."""
        monitor = TabSelectorMonitor()

        with pytest.raises(ValueError):
            monitor.update_tab_count("nonexistent", 1)

    def test_get_tab_count(self) -> None:
        """Test getting tab count."""
        monitor = TabSelectorMonitor()
        area_widget = Mock()

        monitor.register_dock_area("area_1", area_widget)
        monitor._area_tab_counts["area_1"] = 3

        assert monitor.get_tab_count("area_1") == 3

    def test_get_tab_count_nonexistent(self) -> None:
        """Test getting tab count for nonexistent area."""
        monitor = TabSelectorMonitor()

        assert monitor.get_tab_count("nonexistent") == 0

    def test_should_show_selector_single_tab(self) -> None:
        """Test selector visibility with single tab."""
        monitor = TabSelectorMonitor()
        area_widget = Mock()

        monitor.register_dock_area("area_1", area_widget)
        monitor._area_tab_counts["area_1"] = 1

        assert monitor.should_show_selector("area_1") is False

    def test_should_show_selector_multiple_tabs(self) -> None:
        """Test selector visibility with multiple tabs."""
        monitor = TabSelectorMonitor()
        area_widget = Mock()

        monitor.register_dock_area("area_1", area_widget)
        monitor._area_tab_counts["area_1"] = 2

        assert monitor.should_show_selector("area_1") is True

    def test_should_show_selector_many_tabs(self) -> None:
        """Test selector visibility with many tabs."""
        monitor = TabSelectorMonitor()
        area_widget = Mock()

        monitor.register_dock_area("area_1", area_widget)
        monitor._area_tab_counts["area_1"] = 5

        assert monitor.should_show_selector("area_1") is True

    def test_get_all_area_counts(self) -> None:
        """Test getting all area counts."""
        monitor = TabSelectorMonitor()

        area_1 = Mock()
        area_2 = Mock()

        monitor.register_dock_area("area_1", area_1)
        monitor.register_dock_area("area_2", area_2)

        monitor._area_tab_counts["area_1"] = 1
        monitor._area_tab_counts["area_2"] = 2

        counts = monitor.get_all_area_counts()

        assert counts == {"area_1": 1, "area_2": 2}

    def test_count_tabs_in_area_with_dockWidgetsCount(self) -> None:
        """Test counting tabs when dockWidgetsCount is available."""
        area_widget = Mock()
        area_widget.dockWidgets = Mock(return_value=[Mock(), Mock(), Mock()])
        area_widget.dockWidgetsCount = Mock(return_value=3)

        monitor = TabSelectorMonitor()
        count = monitor._count_tabs_in_area(area_widget)
        assert count == 3

    def test_count_tabs_in_area_with_tabCount(self) -> None:
        """Test counting tabs when tabCount is available."""
        # Use spec=[] so dockWidgets/dockWidgetsCount are not auto-created on Mock
        area_widget = Mock(spec=[])
        area_widget.tabCount = Mock(return_value=2)

        monitor = TabSelectorMonitor()
        count = monitor._count_tabs_in_area(area_widget)
        assert count == 2

        # Directly test the tabCount mock
        assert area_widget.tabCount() == 2, "tabCount mock is not returning the expected value"

    def test_count_tabs_in_area_fallback(self) -> None:
        """Test counting tabs with fallback."""
        area_widget = Mock(spec=[])

        monitor = TabSelectorMonitor()
        count = monitor._count_tabs_in_area(area_widget)
        assert count == 1


class TestTabSelectorEventHandler:
    """Test suite for TabSelectorEventHandler class."""

    def test_init(self) -> None:
        """Test TabSelectorEventHandler initialization."""
        dock_manager = Mock()
        monitor = TabSelectorMonitor()

        handler = TabSelectorEventHandler(dock_manager, monitor)

        assert handler.dock_manager == dock_manager
        assert handler.tab_monitor == monitor

    def test_find_parent_area(self) -> None:
        """Test finding parent area from dock widget."""
        parent_area = Mock()
        dock_widget = Mock()
        dock_widget.dockAreaWidget = Mock(return_value=parent_area)

        result = TabSelectorEventHandler._find_parent_area(dock_widget)
        assert result == parent_area

    def test_find_parent_area_none(self) -> None:
        """Test finding parent area when widget has no parent."""
        dock_widget = Mock(spec=[])

        result = TabSelectorEventHandler._find_parent_area(dock_widget)
        assert result is None

    def test_get_area_id(self) -> None:
        """Test getting area ID."""
        area_widget = Mock()
        area_widget.objectName = Mock(return_value="test_area")

        area_id = TabSelectorEventHandler._get_area_id(area_widget)
        assert area_id == "test_area"

    def test_get_area_id_none(self) -> None:
        """Test getting area ID when no name is set."""
        area_widget = Mock()
        area_widget.objectName = Mock(return_value="")

        area_id = TabSelectorEventHandler._get_area_id(area_widget)
        assert area_id is None

    def test_on_dock_area_created_assigns_generated_id(self) -> None:
        """Area creation without objectName gets generated ID and initial count emit."""
        dock_manager = Mock()
        monitor = TabSelectorMonitor()
        monitor.tab_count_changed = Mock()
        monitor.tab_count_changed.emit = Mock()

        handler = TabSelectorEventHandler(dock_manager, monitor)
        area_widget = Mock()
        area_widget.objectName = Mock(return_value="")
        area_widget.setObjectName = Mock()

        with patch.object(monitor, "_count_tabs_in_area", return_value=1):
            handler._on_dock_area_created(area_widget)

        assert "area_0" in monitor._monitored_areas
        area_widget.setObjectName.assert_called_once_with("area_0")
        monitor.tab_count_changed.emit.assert_called_once_with("area_0", 1)

    def test_on_dock_widget_added_auto_registers_and_handles_update_error(self) -> None:
        """Widget add auto-registers area and uses fallback path on update error."""
        dock_manager = Mock()
        monitor = TabSelectorMonitor()
        handler = TabSelectorEventHandler(dock_manager, monitor)

        area_widget = Mock()
        area_widget.objectName = Mock(return_value="area_x")
        dock_widget = Mock()
        dock_widget.dockAreaWidget = Mock(return_value=area_widget)
        dock_widget.visibilityChanged = Mock(connect=Mock())
        dock_widget.closed = Mock(connect=Mock())

        with (
            patch.object(monitor, "_count_tabs_in_area", return_value=2),
            patch.object(
                monitor,
                "update_tab_count",
                side_effect=ValueError("not registered"),
            ),
        ):
            handler._on_dock_widget_added(dock_widget)

        assert "area_x" in monitor._monitored_areas
        assert monitor.get_tab_count("area_x") == 2

    def test_on_dock_widget_removed_updates_changed_areas(self) -> None:
        """Widget removal updates monitor counts when changed."""
        dock_manager = Mock()
        monitor = TabSelectorMonitor()
        handler = TabSelectorEventHandler(dock_manager, monitor)

        area_widget = Mock()
        monitor._monitored_areas["area_1"] = area_widget
        monitor._area_tab_counts["area_1"] = 3

        with patch.object(monitor, "_count_tabs_in_area", return_value=1):
            with patch.object(monitor, "update_tab_count") as update_count:
                handler._on_dock_widget_removed(Mock())
                update_count.assert_called_once_with("area_1", 1)

    def test_on_widget_visibility_changed_updates_when_count_differs(self) -> None:
        """Visibility callback updates tab count for monitored area when needed."""
        dock_manager = Mock()
        monitor = TabSelectorMonitor()
        handler = TabSelectorEventHandler(dock_manager, monitor)

        area_widget = Mock()
        area_widget.objectName = Mock(return_value="area_2")
        monitor._monitored_areas["area_2"] = area_widget
        monitor._area_tab_counts["area_2"] = 1

        dock_widget = Mock()
        dock_widget.dockAreaWidget = Mock(return_value=area_widget)

        with patch.object(monitor, "_count_tabs_in_area", return_value=2):
            with patch.object(monitor, "update_tab_count") as update_count:
                handler._on_widget_visibility_changed(dock_widget, True)
                update_count.assert_called_once_with("area_2", 2)

    def test_on_widget_closed_marks_closed_and_updates(self) -> None:
        """Closed callback marks widget and updates monitored area count."""
        dock_manager = Mock()
        monitor = TabSelectorMonitor()
        handler = TabSelectorEventHandler(dock_manager, monitor)

        area_widget = Mock()
        area_widget.objectName = Mock(return_value="area_3")
        monitor._monitored_areas["area_3"] = area_widget

        dock_widget = Mock()
        dock_widget.dockAreaWidget = Mock(return_value=area_widget)

        with patch.object(monitor, "_count_tabs_in_area", return_value=0):
            with patch.object(monitor, "update_tab_count") as update_count:
                handler._on_widget_closed(dock_widget)
                assert monitor.is_widget_closed(dock_widget) is True
                update_count.assert_called_once_with("area_3", 0)


class TestTabSelectorVisibilityController:
    """Test suite for TabSelectorVisibilityController class."""

    def test_init(self) -> None:
        """Test TabSelectorVisibilityController initialization."""
        monitor = TabSelectorMonitor()
        controller = TabSelectorVisibilityController(monitor)

        assert controller.tab_monitor == monitor
        assert controller._title_bar_cache == {}

    def test_get_title_bar(self) -> None:
        """Test getting title bar from area widget."""
        title_bar = Mock()
        area_widget = Mock()
        area_widget.titleBar = Mock(return_value=title_bar)

        result = TabSelectorVisibilityController._get_title_bar(area_widget)
        assert result == title_bar

    def test_get_title_bar_none(self) -> None:
        """Test getting title bar when no titleBar method."""
        area_widget = Mock(spec=[])

        result = TabSelectorVisibilityController._get_title_bar(area_widget)
        assert result is None

    def test_find_tab_selector(self) -> None:
        """Test finding tab selector in title bar."""
        selector = Mock()
        title_bar = Mock(spec=[])
        title_bar.findChild = Mock(return_value=None)
        title_bar.findChildren = Mock(return_value=[])
        title_bar.tabsMenuButton = Mock(return_value=selector)

        result = TabSelectorVisibilityController._find_tab_selector(title_bar)
        assert result == selector

    def test_set_selector_visibility_true(self) -> None:
        """Test setting selector visibility to true."""
        selector = Mock()

        TabSelectorVisibilityController._set_selector_visibility(selector, True)
        selector.setVisible.assert_called_once_with(True)

    def test_set_selector_visibility_false(self) -> None:
        """Test setting selector visibility to false."""
        selector = Mock()

        TabSelectorVisibilityController._set_selector_visibility(selector, False)
        selector.setVisible.assert_called_once_with(False)

    def test_set_selector_visibility_none(self) -> None:
        """Test setting visibility on None selector."""
        # Should not raise error
        TabSelectorVisibilityController._set_selector_visibility(None, True)

    def test_register_area(self) -> None:
        """Test registering area with controller."""
        monitor = TabSelectorMonitor()
        controller = TabSelectorVisibilityController(monitor)

        area_widget = Mock()
        area_widget.dockWidgetsCount = Mock(return_value=1)
        area_widget.titleBar = Mock(return_value=None)

        controller.register_area("area_1", area_widget)

        assert "area_1" in monitor._monitored_areas

    def test_find_float_button_by_find_child(self) -> None:
        """Test finding float button via findChild path."""
        button = Mock()
        title_bar = Mock()
        title_bar.findChild = Mock(return_value=button)

        result = TabSelectorVisibilityController._find_float_button(title_bar)
        assert result == button

    def test_find_float_button_by_children(self) -> None:
        """Test finding float button by iterating children."""
        child = Mock()
        child.objectName = Mock(return_value="detachGroupButton")
        title_bar = Mock()
        title_bar.findChild = Mock(return_value=None)
        title_bar.findChildren = Mock(return_value=[child])

        result = TabSelectorVisibilityController._find_float_button(title_bar)
        assert result == child

    def test_on_tab_count_changed_updates_selector_and_float_button(self) -> None:
        """Test count-change handler updates both selector and float button visibility."""
        monitor = TabSelectorMonitor()
        controller = TabSelectorVisibilityController(monitor)

        area_widget = Mock()
        monitor._monitored_areas["area_1"] = area_widget

        title_bar = Mock()
        selector = Mock()
        float_button = Mock()
        float_button.isVisible = Mock(return_value=False)

        with patch.object(controller, "_get_title_bar", return_value=title_bar):
            with patch.object(controller, "_find_tab_selector", return_value=selector):
                with patch.object(controller, "_find_float_button", return_value=float_button):
                    with patch.object(controller, "_set_selector_visibility") as set_visibility:
                        controller._on_tab_count_changed("area_1", 2)

                        set_visibility.assert_called_once_with(selector, True)
                        float_button.setVisible.assert_called_once_with(True)

    def test_refresh_area_visibility_updates_selector_and_float_button(self) -> None:
        """Test refresh re-applies selector and float-button visibility."""
        monitor = TabSelectorMonitor()
        controller = TabSelectorVisibilityController(monitor)

        area_widget = Mock()
        monitor._monitored_areas["area_1"] = area_widget
        monitor._area_tab_counts["area_1"] = 2

        title_bar = Mock()
        selector = Mock()
        float_button = Mock()

        with patch.object(controller, "_get_title_bar", return_value=title_bar):
            with patch.object(controller, "_find_tab_selector", return_value=selector):
                with patch.object(controller, "_find_float_button", return_value=float_button):
                    with patch.object(controller, "_set_selector_visibility") as set_visibility:
                        controller.refresh_area_visibility(area_widget)

                        set_visibility.assert_called_once_with(selector, True)
                        float_button.setVisible.assert_called_once_with(True)


# Integration test
def test_phase_1_integration() -> None:
    """Integration test for Phase 1 - Tab Selector Visibility."""
    monitor = TabSelectorMonitor()

    area_1 = Mock()
    area_1.dockWidgetsCount = Mock(return_value=1)
    area_1.titleBar = Mock(return_value=None)

    # Single tab - selector should be hidden
    monitor.register_dock_area("area_1", area_1)
    assert monitor.should_show_selector("area_1") is False

    # Multiple tabs - selector should be shown
    monitor._area_tab_counts["area_1"] = 2
    assert monitor.should_show_selector("area_1") is True

    # Back to single tab - selector should be hidden
    monitor._area_tab_counts["area_1"] = 1
    assert monitor.should_show_selector("area_1") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
