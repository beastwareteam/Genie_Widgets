"""Tab Selector Monitor - Manages visibility of tab selectors in dock areas.

This module monitors CDockAreaWidget instances and controls the visibility of
tab selector dropdowns based on the number of tabs in each dock area.

When a dock area has only 1 tab, the selector is hidden. When it has 2+ tabs,
the selector is shown to allow switching between tabs.
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal


logger = logging.getLogger(__name__)


class TabSelectorMonitor(QObject):
    """Monitor for tab selector visibility in dock areas.

    This monitor tracks the number of tabs in each dock area and signals
    when the tab count changes. It allows enabling/disabling the tab selector
    dropdown based on the number of tabs.

    Signals:
        tab_count_changed: Emitted when tab count changes for a dock area.

    Args:
                area_id (str): The dock area ID
                count (int): New tab count
    """

    tab_count_changed = Signal(str, int)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the tab selector monitor.

        Args:
            parent: Parent QObject, if any
        """
        super().__init__(parent)
        self._area_tab_counts: dict[str, int] = {}
        self._monitored_areas: dict[str, Any] = {}
        self._closed_widgets: set[int] = set()  # Track closed widget IDs

    def register_dock_area(self, area_id: str, area_widget: Any) -> None:
        """Register a dock area for monitoring.

        Args:
            area_id: Unique identifier for the dock area
            area_widget: The CDockAreaWidget instance to monitor
        """
        if area_id in self._monitored_areas:
            return

        self._monitored_areas[area_id] = area_widget
        count = self._count_tabs_in_area(area_widget)
        self._area_tab_counts[area_id] = count

    def unregister_dock_area(self, area_id: str) -> None:
        """Unregister a dock area from monitoring.

        Args:
            area_id: The dock area ID to unregister
        """
        if area_id in self._monitored_areas:
            del self._monitored_areas[area_id]
        if area_id in self._area_tab_counts:
            del self._area_tab_counts[area_id]

    def update_tab_count(self, area_id: str, new_count: int) -> None:
        """Update the tab count for a dock area.

        This method should be called when a widget is added or removed
        from a dock area.

        Args:
            area_id: The dock area ID
            new_count: The new number of tabs/widgets in the area

        Raises:
            ValueError: If area_id is not registered
        """
        if area_id not in self._area_tab_counts:
            raise ValueError(f"Dock area '{area_id}' is not registered")

        old_count = self._area_tab_counts[area_id]

        if old_count != new_count:
            logger.debug("Tab count changed for %s: %s -> %s", area_id, old_count, new_count)
            self._area_tab_counts[area_id] = new_count
            self.tab_count_changed.emit(area_id, new_count)

    def get_tab_count(self, area_id: str) -> int:
        """Get the current tab count for a dock area.

        Args:
            area_id: The dock area ID

        Returns:
            The number of tabs in the area, or 0 if area not found
        """
        return self._area_tab_counts.get(area_id, 0)

    def should_show_selector(self, area_id: str) -> bool:
        """Determine if tab selector should be visible.

        The selector is shown only when there are 2 or more tabs in the area.

        Args:
            area_id: The dock area ID

        Returns:
            True if selector should be visible, False otherwise
        """
        count = self.get_tab_count(area_id)
        return count > 1

    def get_all_area_counts(self) -> dict[str, int]:
        """Get tab counts for all monitored areas.

        Returns:
            Dictionary mapping area_id to tab count
        """
        return dict(self._area_tab_counts)

    def mark_widget_closed(self, widget: Any) -> None:
        """Mark a widget as closed.

        Args:
            widget: The CDockWidget that was closed
        """
        widget_id = id(widget)
        self._closed_widgets.add(widget_id)

    def is_widget_closed(self, widget: Any) -> bool:
        """Check if a widget is marked as closed.

        Args:
            widget: The CDockWidget to check

        Returns:
            True if widget is closed, False otherwise
        """
        return id(widget) in self._closed_widgets

    def _count_tabs_in_area(self, area_widget: Any) -> int:
        """Count the number of OPEN tabs/widgets in a dock area.

        Only counts widgets that are not marked as closed.

        Args:
            area_widget: The CDockAreaWidget instance

        Returns:
            The number of open tabs in the area
        """
        try:
            if hasattr(area_widget, "dockWidgets"):
                # Get all widgets and count only non-closed ones
                widgets = area_widget.dockWidgets()
                count = 0
                for widget in widgets:
                    # Skip widgets marked as closed
                    if not self.is_widget_closed(widget):
                        count += 1
                return count
            if hasattr(area_widget, "openDockWidgetsCount"):
                return int(area_widget.openDockWidgetsCount())
            if hasattr(area_widget, "dockWidgetsCount"):
                return int(area_widget.dockWidgetsCount())
            if hasattr(area_widget, "tabCount"):
                return int(area_widget.tabCount())
            return 1
        except Exception:
            return 1
