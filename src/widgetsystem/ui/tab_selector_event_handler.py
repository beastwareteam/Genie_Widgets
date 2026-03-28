"""Tab Selector Event Handler - Connects QtAds signals to TabSelectorMonitor.

This module provides event handlers that connect CDockManager signals to
the TabSelectorMonitor, automatically updating tab counts when dock areas
or widgets are added/removed.
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Slot

from widgetsystem.ui.tab_selector_monitor import TabSelectorMonitor

logger = logging.getLogger(__name__)


class TabSelectorEventHandler(QObject):
    """Handles CDockManager events for tab selector updates.

    This handler connects to CDockManager signals and updates the
    TabSelectorMonitor when dock areas are created, widgets are added,
    or widgets are removed.
    """

    def __init__(
        self,
        dock_manager: Any,
        tab_monitor: TabSelectorMonitor,
        parent: QObject | None = None,
    ) -> None:
        """Initialize the event handler.

        Args:
            dock_manager: The CDockManager instance
            tab_monitor: The TabSelectorMonitor instance
            parent: Parent QObject, if any
        """
        super().__init__(parent)
        self.dock_manager = dock_manager
        self.tab_monitor = tab_monitor
        self._area_id_counter = 0

        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect to CDockManager signals."""
        try:
            # Signal: New dock area created
            if hasattr(self.dock_manager, "dockAreaCreated"):
                self.dock_manager.dockAreaCreated.connect(self._on_dock_area_created)

            # Signal: Widget added to dock
            if hasattr(self.dock_manager, "dockWidgetAdded"):
                self.dock_manager.dockWidgetAdded.connect(self._on_dock_widget_added)

            # Signal: Widget removed from dock
            if hasattr(self.dock_manager, "dockWidgetRemoved"):
                self.dock_manager.dockWidgetRemoved.connect(self._on_dock_widget_removed)

            # Signal: Floating widget created
            if hasattr(self.dock_manager, "floatingWidgetCreated"):
                self.dock_manager.floatingWidgetCreated.connect(self._on_floating_widget_created)

        except Exception as e:
            logger.warning(f"Unable to connect all CDockManager signals: {e}")

    @Slot(object)
    def _on_dock_area_created(self, area_widget: Any) -> None:
        """Handle dock area creation.

        Args:
            area_widget: The created CDockAreaWidget
        """
        try:
            # Generate a unique area ID if not available
            if hasattr(area_widget, "objectName") and area_widget.objectName():
                area_id = area_widget.objectName()
            else:
                area_id = f"area_{self._area_id_counter}"
                self._area_id_counter += 1

                # CRITICAL: Set objectName on widget so we can find it later!
                if hasattr(area_widget, "setObjectName"):
                    area_widget.setObjectName(area_id)

            logger.debug(f"dock_area_created: {area_id}")

            self.tab_monitor.register_dock_area(area_id, area_widget)

            # Initial count
            count = self.tab_monitor._count_tabs_in_area(area_widget)
            self.tab_monitor._area_tab_counts[area_id] = count

            logger.debug(f"Initial tab count for {area_id}: {count}")

            # Trigger initial visibility update
            self.tab_monitor.tab_count_changed.emit(area_id, count)

        except Exception as e:
            logger.exception(f"Error in _on_dock_area_created: {e}")

    @Slot(object)
    def _on_dock_widget_added(self, dock_widget: Any) -> None:
        """Handle dock widget addition.

        Args:
            dock_widget: The added CDockWidget
        """
        try:
            logger.debug(f"dock_widget_added: {dock_widget}")

            # Find the parent dock area
            area = self._find_parent_area(dock_widget)
            logger.debug(f"Found area: {area}")

            if area:
                area_id = self._get_area_id(area)
                logger.debug(f"Area ID: {area_id}")

                if area_id:
                    # If area not registered yet, register it now
                    if area_id not in self.tab_monitor._monitored_areas:
                        logger.debug(f"Auto-registering area {area_id}")
                        self.tab_monitor.register_dock_area(area_id, area)

                    # IMPORTANT: Connect to widget's signals (guard against duplicates)
                    # visibilityChanged: Update count when tab changes
                    if hasattr(dock_widget, "visibilityChanged") and not dock_widget.property(
                        "ws_signals_connected"
                    ):
                        dock_widget.visibilityChanged.connect(
                            lambda visible, w=dock_widget: self._on_widget_visibility_changed(
                                w,
                                visible,
                            ),
                        )

                    # closed: Mark widget as permanently closed
                    if hasattr(dock_widget, "closed") and not dock_widget.property(
                        "ws_signals_connected"
                    ):
                        dock_widget.closed.connect(lambda w=dock_widget: self._on_widget_closed(w))

                    dock_widget.setProperty("ws_signals_connected", True)

                    count = self.tab_monitor._count_tabs_in_area(area)
                    logger.debug(f"Updating tab count for {area_id}: {count}")

                    # Update via monitor which will emit signal
                    try:
                        self.tab_monitor.update_tab_count(area_id, count)
                    except ValueError:
                        # Area not registered, do it now
                        self.tab_monitor.register_dock_area(area_id, area)
                        self.tab_monitor._area_tab_counts[area_id] = count
                        self.tab_monitor.tab_count_changed.emit(area_id, count)
                else:
                    logger.warning("area_id is None/empty!")
            else:
                logger.warning("area is None!")
        except Exception as e:
            logger.exception(f"Error in _on_dock_widget_added: {e}")

    @Slot(object)
    def _on_dock_widget_removed(self, dock_widget: Any) -> None:
        """Handle dock widget removal.

        Args:
            dock_widget: The removed CDockWidget
        """
        try:
            logger.debug(f"dock_widget_removed: {dock_widget}")

            # Find all areas and update their counts
            for area_id, area_widget in list(self.tab_monitor._monitored_areas.items()):
                count = self.tab_monitor._count_tabs_in_area(area_widget)
                current_count = self.tab_monitor.get_tab_count(area_id)

                logger.debug(f"Area {area_id}: count={count}, current={current_count}")

                if count != current_count:
                    logger.debug(f"Updating {area_id} to count={count}")
                    self.tab_monitor.update_tab_count(area_id, count)
        except Exception as e:
            logger.exception(f"Error in _on_dock_widget_removed: {e}")

    def _on_widget_visibility_changed(self, dock_widget: Any, visible: bool) -> None:
        """Handle widget visibility change (tab switching).

        Args:
            dock_widget: The CDockWidget that changed visibility
            visible: True if now visible, False if hidden
        """
        try:
            widget_title = dock_widget.windowTitle() if hasattr(dock_widget, "windowTitle") else str(dock_widget)
            logger.debug(f"widget_visibility_changed: {widget_title}, visible={visible}")

            # Just update counts, don't mark as closed
            # (closed is handled by _on_widget_closed)
            area = self._find_parent_area(dock_widget)
            if area:
                area_id = self._get_area_id(area)
                if area_id and area_id in self.tab_monitor._monitored_areas:
                    count = self.tab_monitor._count_tabs_in_area(area)
                    logger.debug(f"Updating {area_id} count to {count}")
                    # Only update if count changed
                    if count != self.tab_monitor.get_tab_count(area_id):
                        self.tab_monitor.update_tab_count(area_id, count)
        except Exception as e:
            logger.exception(f"Error in _on_widget_visibility_changed: {e}")

    def _on_widget_closed(self, dock_widget: Any) -> None:
        """Handle widget closed signal (permanent close).

        Args:
            dock_widget: The CDockWidget that was closed
        """
        try:
            widget_title = dock_widget.windowTitle() if hasattr(dock_widget, "windowTitle") else str(dock_widget)
            logger.debug(f"widget_closed: {widget_title}")

            # Mark widget as permanently closed
            self.tab_monitor.mark_widget_closed(dock_widget)

            # Update count for the widget's area
            area = self._find_parent_area(dock_widget)
            if area:
                area_id = self._get_area_id(area)
                if area_id and area_id in self.tab_monitor._monitored_areas:
                    count = self.tab_monitor._count_tabs_in_area(area)
                    logger.debug(f"Updating {area_id} count to {count}")
                    self.tab_monitor.update_tab_count(area_id, count)
        except Exception as e:
            logger.exception(f"Error in _on_widget_closed: {e}")

    @Slot(object)
    def _on_floating_widget_created(self, floating_widget: Any) -> None:
        """Handle floating widget creation.

        Args:
            floating_widget: The created floating container
        """
        # Floating widgets don't have tab selectors

    @staticmethod
    def _find_parent_area(dock_widget: Any) -> Any:
        """Find the parent CDockAreaWidget for a dock widget.

        Args:
            dock_widget: The CDockWidget

        Returns:
            The parent CDockAreaWidget or None
        """
        try:
            if hasattr(dock_widget, "dockAreaWidget"):
                return dock_widget.dockAreaWidget()
            if hasattr(dock_widget, "parent"):
                parent = dock_widget.parent()
                if parent and hasattr(parent, "dockWidgetsCount"):
                    return parent
            return None
        except Exception:
            return None

    @staticmethod
    def _get_area_id(area_widget: Any) -> str | None:
        """Get a unique ID for a dock area.

        Args:
            area_widget: The CDockAreaWidget

        Returns:
            The area ID or None
        """
        try:
            if hasattr(area_widget, "objectName"):
                return area_widget.objectName() or None
            return None
        except Exception:
            return None
