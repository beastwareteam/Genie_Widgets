"""DockController - Centralized dock widget lifecycle management.

This controller encapsulates all dock widget creation, registration,
and lifecycle operations that were previously scattered across MainWindow.
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTabWidget, QWidget
import PySide6QtAds as QtAds

from widgetsystem.enums import DockArea


logger = logging.getLogger(__name__)


class DockController(QObject):
    """Controller for dock widget lifecycle management.

    Centralizes dock creation, registration, and operations.
    Emits signals for dock events to enable loose coupling.

    Signals:
        dockAdded: Emitted when a dock widget is created (dock_id, dock)
        dockRemoved: Emitted when a dock widget is removed (dock_id)
        dockFloated: Emitted when a dock is floated (dock_id)
        dockDocked: Emitted when a dock is docked (dock_id)
    """

    dockAdded = Signal(str, object)  # dock_id, dock_widget
    dockRemoved = Signal(str)  # dock_id
    dockFloated = Signal(str)  # dock_id
    dockDocked = Signal(str)  # dock_id

    def __init__(
        self,
        dock_manager: Any,
        panel_factory: Any,
        tabs_factory: Any,
        i18n_factory: Any,
        parent: QObject | None = None,
    ) -> None:
        """Initialize DockController.

        Args:
            dock_manager: The CDockManager instance
            panel_factory: PanelFactory for loading panel configurations
            tabs_factory: TabsFactory for loading tab group configurations
            i18n_factory: I18nFactory for translations
            parent: Parent QObject
        """
        super().__init__(parent)

        self._dock_manager = dock_manager
        self._panel_factory = panel_factory
        self._tabs_factory = tabs_factory
        self._i18n_factory = i18n_factory

        # Internal dock registry
        self._docks: list[Any] = []
        self._dock_map: dict[str, Any] = {}  # dock_id -> dock_widget

        # Counter for dynamic panel IDs
        self._panel_counter: int = 0

    @property
    def docks(self) -> list[Any]:
        """Get read-only copy of dock list."""
        return list(self._docks)

    @property
    def dock_count(self) -> int:
        """Get number of registered docks."""
        return len(self._docks)

    def find_dock(self, dock_id: str) -> Any | None:
        """Find a dock widget by ID.

        Args:
            dock_id: The dock identifier

        Returns:
            CDockWidget or None if not found
        """
        return self._dock_map.get(dock_id)

    def find_dock_by_title(self, title_part: str) -> Any | None:
        """Find a dock widget by partial title match.

        Args:
            title_part: Substring to match in dock title

        Returns:
            First matching CDockWidget or None
        """
        for dock in self._docks:
            if hasattr(dock, "windowTitle") and title_part in dock.windowTitle():
                return dock
        return None

    def all_docks(self) -> list[Any]:
        """Get all registered dock widgets.

        Returns:
            Read-only copy of dock list
        """
        return list(self._docks)

    def create_panel(
        self,
        title: str,
        area: DockArea | str,
        dock_id: str | None = None,
        *,
        closable: bool = True,
        movable: bool = True,
        floatable: bool = True,
        delete_on_close: bool = False,
    ) -> Any:
        """Create a new dock panel.

        Args:
            title: Panel title
            area: Dock area (DockArea enum or string)
            dock_id: Optional unique identifier
            closable: Allow closing the panel
            movable: Allow moving the panel
            floatable: Allow floating the panel
            delete_on_close: Delete widget when closed

        Returns:
            Created CDockWidget instance
        """
        qt_area = self._resolve_dock_area(area)
        if qt_area is None:
            raise ValueError(f"Invalid dock area: {area}")

        dock = QtAds.CDockWidget(self._dock_manager, title, self._dock_manager)
        if dock_id:
            dock.setObjectName(dock_id)

        dock.setWidget(QWidget())
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, closable
        )
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, movable
        )
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, floatable
        )
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetDeleteOnClose, delete_on_close
        )

        self._dock_manager.addDockWidget(qt_area, dock)
        self._register_dock(dock_id or title, dock)

        return dock

    def create_dynamic_panel(self) -> Any:
        """Create a new dynamic panel with auto-generated ID.

        Returns:
            Created CDockWidget instance
        """
        self._panel_counter += 1
        panel_id = f"dynamic_panel_{self._panel_counter}"
        panel_name_key = f"panel.dynamic_{self._panel_counter}"

        # Add to panel configuration for persistence
        self._panel_factory.add_panel(
            panel_id,
            panel_name_key,
            area="center",
            closable=True,
            movable=True,
        )

        title = self._i18n_factory.translate(
            "panel.new", default=f"Panel {self._panel_counter}"
        )

        return self.create_panel(title, DockArea.CENTER, dock_id=panel_id)

    def create_tab_group(self, tab_group: Any) -> Any:
        """Create a dock widget containing a tab group.

        Args:
            tab_group: TabGroup configuration object

        Returns:
            Created CDockWidget instance
        """
        qt_area = self._resolve_dock_area(tab_group.dock_area)
        if qt_area is None:
            return None

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)
        tab_widget.setTabsClosable(True)

        # Add tabs recursively
        for tab in tab_group.tabs:
            self._add_tab_recursive(tab_widget, tab, depth=0)

        # Translate group name
        group_name = self._i18n_factory.translate(
            tab_group.title_key, default=tab_group.id
        )

        # Create dock for tab group
        dock = QtAds.CDockWidget(self._dock_manager, group_name, self._dock_manager)
        dock.setObjectName(tab_group.id)
        dock.setWidget(tab_widget)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)

        self._dock_manager.addDockWidget(qt_area, dock)
        self._register_dock(tab_group.id, dock)

        return dock

    def _add_tab_recursive(
        self, parent_widget: QTabWidget, tab: Any, depth: int = 0
    ) -> None:
        """Recursively add tabs (handling nested children)."""
        tab_name = self._i18n_factory.translate(tab.title_key, default=tab.id)

        if tab.children:
            # Tab has nested children - create sub-tab widget
            sub_tab_widget = QTabWidget()
            sub_tab_widget.setDocumentMode(True)
            sub_tab_widget.setTabsClosable(True)

            for child_tab in tab.children:
                self._add_tab_recursive(sub_tab_widget, child_tab, depth=depth + 1)

            parent_widget.addTab(sub_tab_widget, tab_name)
        else:
            # Leaf tab - add placeholder content
            content_widget = QWidget()
            parent_widget.addTab(content_widget, tab_name)

        # Set active tab if specified
        if tab.active and depth == 0:
            parent_widget.setCurrentIndex(parent_widget.count() - 1)

    def build_from_config(self) -> None:
        """Build all dock areas from factory configurations.

        Creates panels from PanelFactory and tab groups from TabsFactory.
        """
        # Create panels
        try:
            panels = self._panel_factory.load_panels()
            for panel in panels:
                self._create_panel_from_config(panel)
        except Exception as e:
            logger.warning("Failed to load panels from factory: %s", e)
            self._create_default_panels()

        # Create tab groups
        try:
            tab_groups = self._tabs_factory.load_tab_groups()
            for tab_group in tab_groups:
                self.create_tab_group(tab_group)
        except Exception as e:
            logger.warning("Failed to load tab groups from factory: %s", e)

    def _create_panel_from_config(self, panel: Any) -> None:
        """Create a dock widget from PanelConfig."""
        qt_area = self._resolve_dock_area(panel.area)
        if qt_area is None:
            return

        # Translate panel name
        panel_name = self._i18n_factory.translate(panel.name_key, default=panel.id)

        # If DnD is disabled, restrict movement
        movable = panel.movable and panel.dnd_enabled
        floatable = panel.floatable and panel.dnd_enabled

        self.create_panel(
            panel_name,
            panel.area,
            dock_id=panel.id,
            closable=panel.closable,
            movable=movable,
            floatable=floatable,
            delete_on_close=panel.delete_on_close,
        )

    def _create_default_panels(self) -> None:
        """Create minimal default panel set if factory fails."""
        self.create_panel("Left Panel", DockArea.LEFT, dock_id="left_panel")
        self.create_panel("Bottom Panel", DockArea.BOTTOM, dock_id="bottom_panel")
        self.create_panel("Center Panel", DockArea.CENTER, dock_id="center_panel")

    def _register_dock(self, dock_id: str, dock: Any) -> None:
        """Register a dock widget internally."""
        self._docks.append(dock)
        self._dock_map[dock_id] = dock
        self.dockAdded.emit(dock_id, dock)

    def _unregister_dock(self, dock_id: str) -> None:
        """Unregister a dock widget."""
        dock = self._dock_map.pop(dock_id, None)
        if dock and dock in self._docks:
            self._docks.remove(dock)
        self.dockRemoved.emit(dock_id)

    def _resolve_dock_area(self, area: DockArea | str) -> Any:
        """Map area to QtAds dock area constant."""
        if isinstance(area, DockArea):
            area = area.value

        area_map = {
            DockArea.LEFT.value: QtAds.LeftDockWidgetArea,
            DockArea.RIGHT.value: QtAds.RightDockWidgetArea,
            DockArea.BOTTOM.value: QtAds.BottomDockWidgetArea,
            DockArea.CENTER.value: QtAds.CenterDockWidgetArea,
            DockArea.TOP.value: QtAds.TopDockWidgetArea,
        }
        return area_map.get(area.strip().lower() if isinstance(area, str) else area)

    # ------------------------------------------------------------------
    # Bulk Operations
    # ------------------------------------------------------------------

    def float_all(self) -> None:
        """Float all dock widgets."""
        for dock in list(self._docks):
            dock.setFloating(True)
            dock_id = dock.objectName()
            if dock_id:
                self.dockFloated.emit(dock_id)

    def dock_all(self) -> None:
        """Dock all floating panels to center area."""
        for dock in list(self._docks):
            if dock.isFloating():
                self._dock_manager.addDockWidget(QtAds.CenterDockWidgetArea, dock)
                dock_id = dock.objectName()
                if dock_id:
                    self.dockDocked.emit(dock_id)

    def close_all(self) -> None:
        """Close all dock widgets."""
        for dock in list(self._docks):
            dock.closeDockWidget()

    def reset(self) -> None:
        """Reset dock controller state.

        Clears all registrations and counters.
        """
        self._docks.clear()
        self._dock_map.clear()
        self._panel_counter = 0
