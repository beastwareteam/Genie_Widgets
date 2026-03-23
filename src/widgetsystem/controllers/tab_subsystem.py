"""TabSubsystem - Unified tab management controller.

This module consolidates five previously separate tab-related controllers
into a single cohesive subsystem:
- TabSelectorMonitor
- TabSelectorEventHandler
- TabSelectorVisibilityController
- FloatingStateTracker
- TabColorController

The TabSubsystem provides a unified lifecycle and API for all tab-related
functionality in the dock manager.
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal


logger = logging.getLogger(__name__)


class TabSubsystem(QObject):
    """Unified tab management subsystem.

    Consolidates all tab-related controllers into a single cohesive unit
    with shared lifecycle management and coordinated signal handling.

    Signals:
        tabColorsChanged: Emitted when tab colors are updated
        visibilityRefreshed: Emitted after tab visibility is refreshed
    """

    tabColorsChanged = Signal(str, str)  # active_color, inactive_color
    visibilityRefreshed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize TabSubsystem without dock manager.

        Call install() to attach to a dock manager.
        """
        super().__init__(parent)

        # Internal controller references (created on install)
        self._tab_monitor: Any = None
        self._tab_event_handler: Any = None
        self._tab_visibility: Any = None
        self._floating_tracker: Any = None
        self._tab_color_controller: Any = None

        # State
        self._dock_manager: Any = None
        self._active_color: str = "#E0E0E0"
        self._inactive_color: str = "#BDBDBD"
        self._installed: bool = False

    @property
    def is_installed(self) -> bool:
        """Check if subsystem is installed on a dock manager."""
        return self._installed

    @property
    def dock_manager(self) -> Any:
        """Get the associated dock manager."""
        return self._dock_manager

    @property
    def tab_monitor(self) -> Any:
        """Get the tab selector monitor."""
        return self._tab_monitor

    @property
    def floating_tracker(self) -> Any:
        """Get the floating state tracker."""
        return self._floating_tracker

    @property
    def tab_color_controller(self) -> Any:
        """Get the tab color controller."""
        return self._tab_color_controller

    def install(self, dock_manager: Any) -> None:
        """Install the TabSubsystem on a dock manager.

        Creates and initializes all internal controllers.

        Args:
            dock_manager: The CDockManager instance to attach to
        """
        if self._installed:
            self.uninstall()

        self._dock_manager = dock_manager

        # Import UI components
        from widgetsystem.ui import (
            FloatingStateTracker,
            TabColorController,
            TabSelectorEventHandler,
            TabSelectorMonitor,
            TabSelectorVisibilityController,
        )

        # Create controllers
        self._tab_monitor = TabSelectorMonitor()
        self._tab_event_handler = TabSelectorEventHandler(
            dock_manager, self._tab_monitor
        )
        self._tab_visibility = TabSelectorVisibilityController(self._tab_monitor)

        # Floating state tracker
        self._floating_tracker = FloatingStateTracker(dock_manager)
        self._floating_tracker.register_post_refresh_callback(
            self._tab_visibility.refresh_area_visibility,
        )

        # Tab color controller
        self._tab_color_controller = TabColorController(
            self._active_color, self._inactive_color
        )
        self._tab_color_controller.initialize()

        self._installed = True
        logger.info("Installed on dock manager")

    def uninstall(self) -> None:
        """Uninstall the TabSubsystem from the dock manager.

        Cleans up all internal controllers.
        """
        if not self._installed:
            return

        # Clear controller references
        self._tab_monitor = None
        self._tab_event_handler = None
        self._tab_visibility = None
        self._floating_tracker = None
        self._tab_color_controller = None

        self._dock_manager = None
        self._installed = False
        logger.info("Uninstalled")

    def reset(self) -> None:
        """Reset the TabSubsystem.

        Reinstalls all controllers on the current dock manager.
        """
        if self._dock_manager:
            dock_manager = self._dock_manager
            self.uninstall()
            self.install(dock_manager)

    def apply_theme_colors(self, active_color: str, inactive_color: str) -> None:
        """Apply new tab colors from theme.

        Args:
            active_color: Color for active tab
            inactive_color: Color for inactive tabs
        """
        self._active_color = active_color
        self._inactive_color = inactive_color

        if self._tab_color_controller:
            self._tab_color_controller.active_color = active_color
            self._tab_color_controller.inactive_color = inactive_color
            self._tab_color_controller.apply()

        self.tabColorsChanged.emit(active_color, inactive_color)

    def track_dock_widget(self, dock_id: str, dock_widget: Any) -> None:
        """Register a dock widget with the floating tracker.

        Args:
            dock_id: Unique identifier for the dock
            dock_widget: The CDockWidget instance
        """
        if self._floating_tracker:
            self._floating_tracker.track_dock_widget(dock_id, dock_widget)

    def refresh_visibility(self) -> None:
        """Refresh tab selector visibility for all dock areas."""
        if self._tab_visibility:
            self._tab_visibility.refresh_area_visibility()
            self.visibilityRefreshed.emit()

    def register_post_refresh_callback(self, callback: Any) -> None:
        """Register a callback to be called after title bar refresh.

        Args:
            callback: Function to call after refresh
        """
        if self._floating_tracker:
            self._floating_tracker.register_post_refresh_callback(callback)
