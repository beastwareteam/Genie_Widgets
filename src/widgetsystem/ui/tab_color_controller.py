"""Tab Color Controller for managing tab bar text colors in ADS docking system."""

import logging
from typing import Any, Optional

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QApplication, QWidget
import PySide6QtAds as QtAds

logger = logging.getLogger(__name__)


class TabColorController(QObject):
    """Controls tab text colors (active/inactive) for all tab bars in dock areas.

    This controller monitors all dock widgets and dock areas in the application,
    applying custom colors to active and inactive tabs. It uses an event filter
    to detect when tabs become active or inactive and updates their colors accordingly.

    Attributes:
        active_color: Hex color string for active tab text (e.g., "#E0E0E0")
        inactive_color: Hex color string for inactive tab text (e.g., "#BDBDBD")
    """

    def __init__(self, active_color: str = "#E0E0E0", inactive_color: str = "#BDBDBD") -> None:
        """Initialize TabColorController with colors.

        Args:
            active_color: Hex color string for active tab text
            inactive_color: Hex color string for inactive tab text
        """
        super().__init__()
        self.active_color = active_color
        self.inactive_color = inactive_color
        self._installed = False

    def initialize(self) -> None:
        """Install event filter on QApplication to monitor all tab bars."""
        if self._installed:
            return

        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
            self._installed = True
            # Apply immediately to existing widgets
            self.apply()

    def apply(self) -> None:
        """Apply tab colors to all existing dock areas and tab bars."""
        for widget in QApplication.allWidgets():
            if not isinstance(widget, QtAds.CDockAreaWidget):
                continue
            dock_area: Any = widget  # Cast to avoid type checker issues
            current_dock = dock_area.currentDockWidget()
            if current_dock is None:
                continue
            try:
                current_tab_widget = current_dock.tabWidget()
            except Exception:
                continue
            for tab in dock_area.findChildren(QWidget):
                if "CDockWidgetTab" not in tab.metaObject().className():
                    continue
                is_active = tab == current_tab_widget
                color = self.active_color if is_active else self.inactive_color
                for label in tab.findChildren(QWidget):
                    if label.objectName() == "dockWidgetTabLabel":
                        label.setStyleSheet(f"color: {color};")

    def eventFilter(self, watched: Optional[QObject], event: Optional[QEvent]) -> bool:
        """Event filter to monitor dock area and tab changes.

        Args:
            watched: The object being watched
            event: The event that occurred

        Returns:
            False to allow normal event processing
        """
        if event is None or watched is None:
            return False

        try:
            # Monitor for show events on dock areas (when new areas are created)
            if event.type() == QEvent.Type.Show and isinstance(watched, QtAds.CDockAreaWidget):
                self.apply()

            # Monitor for current changed events on tab bars
            elif event.type() == QEvent.Type.FocusIn:
                # When a tab gets focus, reapply colors to ensure correct state
                parent = watched.parent() if isinstance(watched, QWidget) else None
                while parent:
                    if isinstance(parent, QtAds.CDockAreaWidget):
                        self.apply()
                        break
                    parent = parent.parent() if isinstance(parent, QWidget) else None

        except Exception as e:
            # Silently fail - don't disrupt normal event processing
            logger.exception(f"Event filter error: {e}")

        return False

    def shutdown(self) -> None:
        """Remove event filter and cleanup."""
        if not self._installed:
            return

        app = QApplication.instance()
        if app:
            app.removeEventFilter(self)
            self._installed = False
