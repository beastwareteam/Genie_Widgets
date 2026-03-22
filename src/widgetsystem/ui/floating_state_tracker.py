"""Floating State Tracker - Tracks and restores floating panel states.

This module ensures that title bar buttons (especially the float button) persist
correctly when panels are undocked and re-docked. QtAds recreates title bars on
docking operations, which can cause button states to be lost.
"""

import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QTimer, Slot

logger = logging.getLogger(__name__)


class FloatingStateTracker(QObject):
    """Tracks floating states and ensures title bar buttons persist.

    This tracker monitors when widgets transition between docked and floating
    states, and ensures that title bar buttons are properly refreshed after
    docking operations.
    """

    def __init__(
        self,
        dock_manager: Any,
        parent: QObject | None = None,
    ) -> None:
        """Initialize the floating state tracker.

        Args:
            dock_manager: The CDockManager instance to monitor
            parent: Parent QObject, if any
        """
        super().__init__(parent)
        self.dock_manager = dock_manager
        self._floating_widgets: dict[int, bool] = {}  # widget_id -> is_floating
        self._pending_refreshes: set[int] = set()  # widget_ids pending refresh
        self._post_refresh_callbacks: list[Callable[[Any], None]] = []  # Callbacks after refresh
        self._tracked_widgets: dict[str, Any] = {}  # widget_name -> dock_widget

        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect to CDockManager floating/docking signals."""
        try:
            # Signal: Widget starts floating
            if hasattr(self.dock_manager, "dockWidgetAboutToBeFloated"):
                self.dock_manager.dockWidgetAboutToBeFloated.connect(self._on_widget_about_to_float)

            # Signal: Floating container created
            if hasattr(self.dock_manager, "floatingWidgetCreated"):
                self.dock_manager.floatingWidgetCreated.connect(self._on_floating_widget_created)

            # Signal: Widget added (may be re-docked)
            if hasattr(self.dock_manager, "dockWidgetAdded"):
                self.dock_manager.dockWidgetAdded.connect(self._on_dock_widget_added)

        except Exception as e:
            logger.warning(f"Unable to connect floating state signals: {e}")

    @Slot(object)
    def _on_widget_about_to_float(self, dock_widget: Any) -> None:
        """Handle widget about to become floating.

        Args:
            dock_widget: The CDockWidget about to float
        """
        try:
            widget_id = id(dock_widget)
            widget_name = (
                dock_widget.objectName() if hasattr(dock_widget, "objectName") else str(widget_id)
            )
            self._floating_widgets[widget_id] = True
            logger.debug(f"Widget about to float: {widget_name} (id={widget_id})")
        except Exception as e:
            logger.exception(f"Error in _on_widget_about_to_float: {e}")

    @Slot(object)
    def _on_floating_widget_created(self, floating_container: Any) -> None:
        """Handle floating container creation.

        Args:
            floating_container: The created CDockFloatingContainer
        """
        try:
            # Nothing specific to do here, tracking is done per widget
            pass
        except Exception as e:
            logger.exception(f"Error in _on_floating_widget_created: {e}")

    @Slot(object)
    def _on_dock_widget_added(self, dock_widget: Any) -> None:
        """Handle widget added (may be re-docked from floating).

        Args:
            dock_widget: The added CDockWidget
        """
        try:
            widget_id = id(dock_widget)
            widget_name = (
                dock_widget.objectName() if hasattr(dock_widget, "objectName") else str(widget_id)
            )

            # Check if this widget was previously floating
            was_floating = self._floating_widgets.get(widget_id, False)

            logger.debug(f"dockWidgetAdded: {widget_name}, was_floating={was_floating}")

            if was_floating:
                # Mark as no longer floating
                self._floating_widgets[widget_id] = False

                # Schedule title bar refresh after short delay
                # (allows QtAds to complete internal setup)
                self._pending_refreshes.add(widget_id)
                logger.debug(f"Scheduling title bar refresh for {widget_name} in 100ms")
                QTimer.singleShot(100, lambda: self._refresh_title_bar(dock_widget))

        except Exception as e:
            logger.exception(f"Error in _on_dock_widget_added: {e}")

    def _refresh_title_bar(self, dock_widget: Any) -> None:
        """Refresh title bar buttons for a dock widget.

        Args:
            dock_widget: The CDockWidget to refresh
        """
        try:
            widget_id = id(dock_widget)
            widget_name = (
                dock_widget.objectName() if hasattr(dock_widget, "objectName") else str(widget_id)
            )

            # Only refresh if still pending
            if widget_id not in self._pending_refreshes:
                logger.debug(f"Skipping refresh for {widget_name} - not pending")
                return

            self._pending_refreshes.remove(widget_id)
            logger.debug(f"Executing title bar refresh for {widget_name}")

            # Get the dock area widget
            if not hasattr(dock_widget, "dockAreaWidget"):
                logger.debug(f"No dockAreaWidget method on {widget_name}")
                return

            area = dock_widget.dockAreaWidget()
            if not area:
                logger.debug(f"No dock area found for {widget_name}")
                return

            # Get the title bar
            if not hasattr(area, "titleBar"):
                logger.debug("No titleBar method on area")
                return

            title_bar = area.titleBar()
            if not title_bar:
                logger.debug("No title bar found")
                return

            logger.debug(f"Toggling title bar visibility for {widget_name}")

            # Force title bar update by toggling visibility
            # This ensures all buttons are recreated with correct state
            title_bar.setVisible(False)
            title_bar.setVisible(True)

            # Alternative: Update title bar explicitly
            if hasattr(title_bar, "update"):
                title_bar.update()

            logger.debug(f"Calling {len(self._post_refresh_callbacks)} post-refresh callbacks")

            # Execute post-refresh callbacks
            # This allows other systems (e.g., TabSelectorVisibility) to reapply their state
            for i, callback in enumerate(self._post_refresh_callbacks):
                try:
                    logger.debug(f"Executing callback {i + 1}/{len(self._post_refresh_callbacks)}")
                    callback(area)
                except Exception as cb_error:
                    logger.exception(f"Error in post-refresh callback: {cb_error}")

        except Exception as e:
            logger.exception(f"Error in _refresh_title_bar: {e}")

    def register_post_refresh_callback(self, callback: Callable[[Any], None]) -> None:
        """Register a callback to be executed after title bar refresh.

        The callback receives the CDockAreaWidget as parameter and can
        reapply any custom button states.

        Args:
            callback: Function to call after refresh, receives CDockAreaWidget
        """
        if callback not in self._post_refresh_callbacks:
            self._post_refresh_callbacks.append(callback)

    def track_dock_widget(self, widget_name: str, dock_widget: Any) -> None:
        """Track a specific dock widget for floating state changes.

        This method connects directly to the widget's topLevelChanged signal
        to detect when the widget becomes floating or docked.

        Args:
            widget_name: Name/ID of the widget to track
            dock_widget: The CDockWidget instance to track
        """
        try:
            widget_id = id(dock_widget)
            self._tracked_widgets[widget_name] = dock_widget
            self._floating_widgets[widget_id] = False  # Initially not floating

            # Connect to the widget's topLevelChanged signal
            # This signal fires with True when widget becomes floating (top-level window)
            # and False when it re-docks
            if hasattr(dock_widget, "topLevelChanged"):
                dock_widget.topLevelChanged.connect(
                    lambda is_floating, w=dock_widget, name=widget_name: (
                        self._on_widget_toplevel_changed(w, name, is_floating)
                    ),
                )
                logger.debug(f"Tracking widget: {widget_name} (id={widget_id})")
            else:
                logger.warning(f"Widget {widget_name} has no topLevelChanged signal")

        except Exception as e:
            logger.exception(f"Error tracking dock widget {widget_name}: {e}")

    def _on_widget_toplevel_changed(
        self,
        dock_widget: Any,
        widget_name: str,
        is_floating: bool,
    ) -> None:
        """Handle individual widget's top-level state change.

        Args:
            dock_widget: The CDockWidget that changed state
            widget_name: Name of the widget
            is_floating: True if now floating, False if docked
        """
        try:
            widget_id = id(dock_widget)
            was_floating = self._floating_widgets.get(widget_id, False)

            logger.debug(f"topLevelChanged: {widget_name}, is_floating={is_floating}, was={was_floating}")

            # Update state
            self._floating_widgets[widget_id] = is_floating

            # If widget just re-docked (was floating, now not)
            if was_floating and not is_floating:
                logger.debug(f"Widget {widget_name} re-docked! Scheduling refresh...")
                # Schedule title bar refresh after short delay
                self._pending_refreshes.add(widget_id)
                QTimer.singleShot(100, lambda: self._refresh_title_bar(dock_widget))
            elif not was_floating and is_floating:
                logger.debug(f"Widget {widget_name} became floating")

        except Exception as e:
            logger.exception(f"Error in _on_widget_toplevel_changed: {e}")

    def is_widget_floating(self, dock_widget: Any) -> bool:
        """Check if a widget is currently floating.

        Args:
            dock_widget: The CDockWidget to check

        Returns:
            True if widget is floating, False otherwise
        """
        widget_id = id(dock_widget)
        return self._floating_widgets.get(widget_id, False)

    def get_floating_widgets(self) -> dict[int, bool]:
        """Get all tracked floating states.

        Returns:
            Dictionary mapping widget_id to floating state
        """
        return dict(self._floating_widgets)
