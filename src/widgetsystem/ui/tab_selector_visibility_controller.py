"""Tab Selector Visibility Controller - Controls tab selector button visibility.

This module controls the visibility of tab selector dropdown buttons in
CDockAreaTitleBar instances based on the number of tabs in each area.
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QWidget

from widgetsystem.ui.tab_selector_monitor import TabSelectorMonitor


logger = logging.getLogger(__name__)


class TabSelectorVisibilityController(QObject):
    """Controls visibility of tab selectors in dock areas.

    This controller listens to TabSelectorMonitor signals and manages
    the visibility of tab selector dropdown buttons in CDockAreaTitleBar.
    """

    def __init__(
        self,
        tab_monitor: TabSelectorMonitor,
        parent: QObject | None = None,
    ) -> None:
        """Initialize the visibility controller.

        Args:
            tab_monitor: The TabSelectorMonitor instance
            parent: Parent QObject, if any
        """
        super().__init__(parent)
        self.tab_monitor = tab_monitor
        self._title_bar_cache: dict[str, Any] = {}

        # Connect to monitor signals
        self.tab_monitor.tab_count_changed.connect(self._on_tab_count_changed)

    @Slot(str, int)
    def _on_tab_count_changed(self, area_id: str, count: int) -> None:
        """Handle tab count changes.

        Args:
            area_id: The dock area ID
            count: The new tab count
        """
        try:
            logger.debug(
                "_on_tab_count_changed called: %s, count=%s",
                area_id,
                count,
            )

            area_widget = self.tab_monitor._monitored_areas.get(area_id)
            if not area_widget:
                logger.debug(
                    "Area widget not found for %s",
                    area_id,
                )
                return

            # Get or find the title bar
            title_bar = self._get_title_bar(area_widget)
            if not title_bar:
                logger.debug(
                    "Title bar not found for %s",
                    area_id,
                )
                return

            # Get the tab selector (dropdown/combobox)
            tab_selector = self._find_tab_selector(title_bar)
            if not tab_selector:
                logger.debug(
                    "Tab selector button not found for %s",
                    area_id,
                )
            else:
                # Update visibility based on tab count
                should_show = count > 1
                logger.debug(
                    "Setting tab selector visibility for %s: %s (count=%s)",
                    area_id,
                    should_show,
                    count,
                )
                self._set_selector_visibility(tab_selector, should_show)

            # CRITICAL: Also ensure float button is visible!
            # This handles cases where count changes (e.g., widget added/removed)
            float_button = self._find_float_button(title_bar)
            if float_button and not float_button.isVisible():
                float_button.setVisible(True)
                logger.debug(
                    "Restored float button visibility for %s (on count change)",
                    area_id,
                )

        except Exception as e:
            logger.exception("Error in _on_tab_count_changed")

    def refresh_area_visibility(self, area_widget: Any) -> None:
        """Refresh tab selector AND float button visibility for a specific area.

        This is useful after title bar refreshes to reapply visibility state.
        After QtAds title bar recreation, both tab selector and float button
        need to be explicitly set to correct visibility.

        Args:
            area_widget: The CDockAreaWidget to refresh
        """
        try:
            # Find the area_id for this area
            area_id = None
            for aid, widget in self.tab_monitor._monitored_areas.items():
                if widget == area_widget:
                    area_id = aid
                    break

            if not area_id:
                return

            # Get current tab count
            count = self.tab_monitor.get_tab_count(area_id)

            # Get title bar
            title_bar = self._get_title_bar(area_widget)
            if not title_bar:
                return

            # Find and update tab selector
            tab_selector = self._find_tab_selector(title_bar)
            if tab_selector:
                should_show = count > 1
                self._set_selector_visibility(tab_selector, should_show)

            # CRITICAL: Also restore float button visibility!
            # QtAds recreates title bar on re-docking with wrong button states
            float_button = self._find_float_button(title_bar)
            if float_button:
                # Float button should always be visible (enabled state controlled by QtAds)
                float_button.setVisible(True)
                logger.debug(
                    "Restored float button visibility for %s",
                    area_id,
                )

        except Exception as e:
            logger.exception("Error in refresh_area_visibility")

    @staticmethod
    def _get_title_bar(area_widget: Any) -> Any:
        """Get the CDockAreaTitleBar from a dock area.

        Args:
            area_widget: The CDockAreaWidget

        Returns:
            The CDockAreaTitleBar or None
        """
        try:
            if hasattr(area_widget, "titleBar"):
                return area_widget.titleBar()
            return None
        except Exception:
            return None

    @staticmethod
    def _find_tab_selector(title_bar: Any) -> Any:
        """Find the tab selector (dropdown) in a title bar.

        The tab selector is a CTitleBarButton with objectName 'tabsMenuButton'
        that displays a dropdown menu to list all tabs in the dock area.

        Args:
            title_bar: The CDockAreaTitleBar

        Returns:
            The tabsMenuButton widget or None
        """
        try:
            # Method 1: Find by objectName 'tabsMenuButton' using findChild
            tabs_menu_button = title_bar.findChild(QWidget, "tabsMenuButton")
            if tabs_menu_button:
                return tabs_menu_button

            # Method 2: Search through all children for widget named 'tabsMenuButton'
            for child in title_bar.findChildren(QWidget):
                if hasattr(child, "objectName") and child.objectName() == "tabsMenuButton":
                    return child

            # Method 3: Direct access via method if available
            if hasattr(title_bar, "tabsMenuButton"):
                return title_bar.tabsMenuButton()

            return None
        except Exception as e:
            logger.exception("Error finding tab selector")
            return None

    @staticmethod
    def _find_float_button(title_bar: Any) -> Any:
        """Find the float/detach button in a title bar.

        The float button is a CTitleBarButton with objectName 'detachGroupButton'
        that allows floating/detaching the entire dock area.

        Args:
            title_bar: The CDockAreaTitleBar

        Returns:
            The detachGroupButton widget or None
        """
        try:
            # Method 1: Find by objectName 'detachGroupButton' using findChild
            detach_button = title_bar.findChild(QWidget, "detachGroupButton")
            if detach_button:
                return detach_button

            # Method 2: Search through all children for widget named 'detachGroupButton'
            for child in title_bar.findChildren(QWidget):
                if hasattr(child, "objectName") and child.objectName() == "detachGroupButton":
                    return child

            # Method 3: Direct access via method if available
            if hasattr(title_bar, "detachGroupButton"):
                return title_bar.detachGroupButton()

            return None
        except Exception as e:
            logger.exception("Error finding float button")
            return None

    @staticmethod
    def _set_selector_visibility(selector: Any, visible: bool) -> None:
        """Set the visibility of a tab selector.

        Args:
            selector: The tab selector widget (QComboBox or button)
            visible: Whether to show or hide the selector
        """
        try:
            if selector:
                selector.setVisible(visible)
        except Exception as e:
            logger.exception("Error setting tab selector visibility")

    def register_area(self, area_id: str, area_widget: Any) -> None:
        """Register a dock area for monitoring.

        Args:
            area_id: The dock area ID
            area_widget: The CDockAreaWidget instance
        """
        self.tab_monitor.register_dock_area(area_id, area_widget)

        # Initial visibility update
        count = self.tab_monitor.get_tab_count(area_id)
        self._on_tab_count_changed(area_id, count)
