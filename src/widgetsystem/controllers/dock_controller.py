"""DockController - Centralized dock widget lifecycle management.

This controller encapsulates all dock widget creation, registration,
and lifecycle operations that were previously scattered across MainWindow.
"""

from typing import Any

import PySide6QtAds as QtAds
from PySide6.QtCore import QObject, QSize, Signal
from PySide6.QtWidgets import QWidget

from widgetsystem.enums import DockArea
from widgetsystem.ui.enhanced_tab_widget import EnhancedTabWidget


class DockController(QObject):
    """Controller for dock widget lifecycle management.

    Centralizes dock creation, registration, and operations.
    Emits signals for dock events to enable loose coupling.

    Signals:
        dockAdded: Emitted when a dock widget is created (dock_id, dock)
        dockRemoved: Emitted when a dock widget is removed (dock_id)
        dockFloated: Emitted when a dock is floated (dock_id)
        dockDocked: Emitted when a dock is docked (dock_id)
        tabFloated: Emitted when a tab is floated to new dock (tab_id, dock_id)
    """

    dockAdded = Signal(str, object)  # dock_id, dock_widget
    dockRemoved = Signal(str)  # dock_id
    dockFloated = Signal(str)  # dock_id
    dockDocked = Signal(str)  # dock_id
    tabFloated = Signal(str, str)  # tab_id, new_dock_id

    # Minimum sizes to prevent collapse
    MIN_TAB_WIDTH = 150
    MIN_TAB_HEIGHT = 100
    MIN_CONTENT_WIDTH = 100
    MIN_CONTENT_HEIGHT = 50

    def __init__(
        self,
        dock_manager: Any,
        panel_factory: Any,
        tabs_factory: Any,
        i18n_factory: Any,
        parent: QObject | None = None,
    ) -> None:
        """Initialize DockController."""
        super().__init__(parent)

        self._dock_manager = dock_manager
        self._panel_factory = panel_factory
        self._tabs_factory = tabs_factory
        self._i18n_factory = i18n_factory

        # Internal dock registry
        self._docks: list[Any] = []
        self._dock_map: dict[str, Any] = {}  # dock_id -> dock_widget

        # Track all tab widgets for signal connections
        self._tab_widgets: list[EnhancedTabWidget] = []

        # Counter for dynamic panel IDs
        self._panel_counter: int = 0
        self._floated_tab_counter: int = 0

    @property
    def docks(self) -> list[Any]:
        """Get read-only copy of dock list."""
        return list(self._docks)

    @property
    def dock_count(self) -> int:
        """Get number of registered docks."""
        return len(self._docks)

    @property
    def tab_widgets(self) -> list[EnhancedTabWidget]:
        """Get all EnhancedTabWidget instances."""
        return list(self._tab_widgets)

    def find_dock(self, dock_id: str) -> Any | None:
        """Find a dock widget by ID."""
        return self._dock_map.get(dock_id)

    def find_dock_by_title(self, title_part: str) -> Any | None:
        """Find a dock widget by partial title match."""
        for dock in self._docks:
            if hasattr(dock, "windowTitle") and title_part in dock.windowTitle():
                return dock
        return None

    def all_docks(self) -> list[Any]:
        """Get all registered dock widgets."""
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
        """Create a new dock panel."""
        qt_area = self._resolve_dock_area(area)
        if qt_area is None:
            raise ValueError(f"Invalid dock area: {area}")

        dock = QtAds.CDockWidget(self._dock_manager, title, self._dock_manager)
        if dock_id:
            dock.setObjectName(dock_id)

        # Create content widget with minimum size
        content = QWidget()
        content.setMinimumSize(self.MIN_CONTENT_WIDTH, self.MIN_CONTENT_HEIGHT)
        dock.setWidget(content)

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

        # Set minimum size on dock widget itself
        dock.setMinimumSizeHintMode(
            QtAds.CDockWidget.eMinimumSizeHintMode.MinimumSizeHintFromContent
        )

        self._dock_manager.addDockWidget(qt_area, dock)
        self._register_dock(dock_id or title, dock)

        return dock

    def create_dynamic_panel(self) -> Any:
        """Create a new dynamic panel with auto-generated ID."""
        self._panel_counter += 1
        panel_id = f"dynamic_panel_{self._panel_counter}"
        panel_name_key = f"panel.dynamic_{self._panel_counter}"

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
        """Create native QtAds dock widgets as tabs in the same area.

        Each tab becomes a CDockWidget. QtAds automatically groups them
        with a native tab bar when added to the same area.
        """
        qt_area = self._resolve_dock_area(tab_group.dock_area)
        if qt_area is None:
            return None

        # Track the dock area widget for adding subsequent tabs
        area_dock: Any = None
        first_dock: Any = None

        for i, tab in enumerate(tab_group.tabs):
            dock = self._create_tab_as_dock(tab, tab_group.id)
            if dock is None:
                continue

            if i == 0:
                # First tab - add to the specified area
                self._dock_manager.addDockWidget(qt_area, dock)
                first_dock = dock
                # Get the dock area widget for adding more tabs
                area_dock = dock.dockAreaWidget()
            else:
                # Subsequent tabs - add as tab to the same area
                if area_dock:
                    self._dock_manager.addDockWidgetTabToArea(dock, area_dock)
                else:
                    # Fallback: add to area (creates new group)
                    self._dock_manager.addDockWidget(qt_area, dock)

            self._register_dock(tab.id, dock)

        return first_dock

    def _create_tab_as_dock(self, tab: Any, _group_id: str) -> Any:
        """Create a single tab as a native CDockWidget.

        If the tab has children, creates nested dock structure.

        Args:
            tab: Tab configuration object
            _group_id: Parent group ID (reserved for future use)
        """
        tab_name = self._i18n_factory.translate(tab.title_key, default=tab.id)

        if tab.children:
            # Tab has children - create container with nested tabs
            # Use EnhancedTabWidget only for nested content
            nested_widget = EnhancedTabWidget()
            nested_widget.setObjectName(f"nested_{tab.id}")
            nested_widget.setMinimumSize(self.MIN_TAB_WIDTH, self.MIN_TAB_HEIGHT)

            # Connect float signal
            nested_widget.tabFloated.connect(
                lambda tid, w: self._on_tab_floated(tid, w, tab.id)
            )
            self._tab_widgets.append(nested_widget)

            # Add children to nested widget
            for child in tab.children:
                self._add_nested_tab(nested_widget, child)

            content = nested_widget
        else:
            # Leaf tab - simple content widget
            content = QWidget()
            content.setObjectName(f"content_{tab.id}")
            content.setMinimumSize(self.MIN_CONTENT_WIDTH, self.MIN_CONTENT_HEIGHT)

        # Create CDockWidget for this tab
        dock = QtAds.CDockWidget(self._dock_manager, tab_name, self._dock_manager)
        dock.setObjectName(tab.id)
        dock.setWidget(content)

        # Set features from config
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, tab.closable
        )
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, tab.movable
        )
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, tab.floatable
        )
        dock.setMinimumSizeHintMode(
            QtAds.CDockWidget.eMinimumSizeHintMode.MinimumSizeHintFromContent
        )

        return dock

    def _add_nested_tab(self, parent_widget: EnhancedTabWidget, tab: Any) -> None:
        """Add a nested tab to an EnhancedTabWidget (for sub-tabs only)."""
        tab_name = self._i18n_factory.translate(tab.title_key, default=tab.id)

        if tab.children:
            # Recursive nesting
            sub_widget = EnhancedTabWidget()
            sub_widget.setObjectName(f"subtabs_{tab.id}")
            sub_widget.setMinimumSize(self.MIN_TAB_WIDTH, self.MIN_TAB_HEIGHT)

            sub_widget.tabFloated.connect(
                lambda tid, w: self._on_tab_floated(tid, w, tab.id)
            )
            self._tab_widgets.append(sub_widget)

            for child in tab.children:
                self._add_nested_tab(sub_widget, child)

            parent_widget.addTab(
                sub_widget,
                tab_name,
                tab_id=tab.id,
                closable=tab.closable,
                movable=tab.movable,
                floatable=tab.floatable,
            )
        else:
            # Leaf tab
            content = QWidget()
            content.setObjectName(f"content_{tab.id}")
            content.setMinimumSize(self.MIN_CONTENT_WIDTH, self.MIN_CONTENT_HEIGHT)

            parent_widget.addTab(
                content,
                tab_name,
                tab_id=tab.id,
                closable=tab.closable,
                movable=tab.movable,
                floatable=tab.floatable,
            )

        if tab.active:
            parent_widget.setCurrentIndex(parent_widget.count() - 1)

    def _on_tab_floated(self, tab_id: str, widget: QWidget, source_id: str) -> None:
        """Handle tab float - create new dock widget for floated tab."""
        self._floated_tab_counter += 1
        dock_id = f"floated_{tab_id}_{self._floated_tab_counter}"

        # Ensure widget has minimum size
        widget.setMinimumSize(self.MIN_CONTENT_WIDTH, self.MIN_CONTENT_HEIGHT)

        # Create floating dock
        dock = QtAds.CDockWidget(self._dock_manager, tab_id, self._dock_manager)
        dock.setObjectName(dock_id)
        dock.setWidget(widget)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)

        dock.setMinimumSizeHintMode(
            QtAds.CDockWidget.eMinimumSizeHintMode.MinimumSizeHintFromContent
        )

        # Add as floating
        self._dock_manager.addDockWidget(QtAds.CenterDockWidgetArea, dock)

        # Float the dock
        if not dock.isFloating():
            dock.setFloating()

        self._register_dock(dock_id, dock)
        self.tabFloated.emit(tab_id, dock_id)

    def build_from_config(self) -> None:
        """Build all dock areas from factory configurations."""
        # Create panels
        try:
            panels = self._panel_factory.load_panels()
            for panel in panels:
                self._create_panel_from_config(panel)
        except Exception as e:
            print(f"Warning: Failed to load panels from factory: {e}")
            self._create_default_panels()

        # Create tab groups
        try:
            tab_groups = self._tabs_factory.load_tab_groups()
            for tab_group in tab_groups:
                self.create_tab_group(tab_group)
        except Exception as e:
            print(f"Warning: Failed to load tab groups from factory: {e}")

    def _create_panel_from_config(self, panel: Any) -> None:
        """Create a dock widget from PanelConfig."""
        qt_area = self._resolve_dock_area(panel.area)
        if qt_area is None:
            return

        panel_name = self._i18n_factory.translate(panel.name_key, default=panel.id)

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
    # Tab Navigation
    # ------------------------------------------------------------------

    def navigate_to_tab(self, tab_id: str) -> bool:
        """Navigate to a specific tab by ID across all tab widgets."""
        for tab_widget in self._tab_widgets:
            if tab_widget.navigate_to(tab_id):
                return True
        return False

    def get_active_tab_id(self) -> str | None:
        """Get currently active tab ID from focused tab widget."""
        for tab_widget in self._tab_widgets:
            if tab_widget.hasFocus():
                idx = tab_widget.currentIndex()
                return tab_widget.get_tab_id(idx)
        return None

    # ------------------------------------------------------------------
    # Bulk Operations
    # ------------------------------------------------------------------

    def float_all(self) -> None:
        """Float all dock widgets."""
        for dock in list(self._docks):
            if not dock.isFloating():
                dock.setFloating()
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
        """Reset dock controller state."""
        self._docks.clear()
        self._dock_map.clear()
        self._tab_widgets.clear()
        self._panel_counter = 0
        self._floated_tab_counter = 0

    # ------------------------------------------------------------------
    # Tab State Persistence (for nesting)
    # ------------------------------------------------------------------

    def export_tab_state(self) -> dict:
        """Export full tab state including nesting structure.

        Returns:
            Dict with tab widget states for persistence
        """
        state = {
            "version": 1,
            "tab_widgets": [],
        }

        for tab_widget in self._tab_widgets:
            widget_state = self._export_tab_widget_state(tab_widget)
            if widget_state:
                state["tab_widgets"].append(widget_state)

        return state

    def _export_tab_widget_state(self, tab_widget: EnhancedTabWidget) -> dict | None:
        """Export state of a single tab widget recursively."""
        if not tab_widget:
            return None

        state = {
            "object_name": tab_widget.objectName(),
            "current_index": tab_widget.currentIndex(),
            "tabs": [],
        }

        for i in range(tab_widget.count()):
            tab_id = tab_widget.get_tab_id(i)
            tab_text = tab_widget.tabText(i)
            content = tab_widget.widget(i)

            tab_state = {
                "index": i,
                "id": tab_id,
                "text": tab_text,
                "closable": tab_widget.is_tab_closable(i),
                "movable": tab_widget.is_tab_movable(i),
                "floatable": tab_widget.is_tab_floatable(i),
            }

            # Check for nested tabs
            if isinstance(content, EnhancedTabWidget):
                tab_state["nested"] = self._export_tab_widget_state(content)

            state["tabs"].append(tab_state)

        return state

    def import_tab_state(self, state: dict) -> bool:
        """Import tab state and restore nesting structure.

        Args:
            state: Previously exported state dict

        Returns:
            True if successful
        """
        if not state or state.get("version") != 1:
            return False

        # Map object names to widgets
        widget_map = {w.objectName(): w for w in self._tab_widgets}

        for widget_state in state.get("tab_widgets", []):
            obj_name = widget_state.get("object_name")
            if obj_name in widget_map:
                self._restore_tab_widget_state(widget_map[obj_name], widget_state)

        return True

    def _restore_tab_widget_state(
        self, tab_widget: EnhancedTabWidget, state: dict
    ) -> None:
        """Restore state of a single tab widget."""
        # Restore current index
        current_idx = state.get("current_index", 0)
        if 0 <= current_idx < tab_widget.count():
            tab_widget.setCurrentIndex(current_idx)

        # Note: Full nesting restoration requires more complex logic
        # as widgets may have been created/destroyed

    # ------------------------------------------------------------------
    # Cross-Dock Tab Transfer (QtAds ↔ EnhancedTabWidget)
    # ------------------------------------------------------------------

    def transfer_tab_to_dock(
        self,
        source_tab_widget: EnhancedTabWidget,
        tab_index: int,
        target_dock_id: str,
    ) -> bool:
        """Transfer a tab from EnhancedTabWidget to another dock.

        Args:
            source_tab_widget: Source tab widget
            tab_index: Index of tab to transfer
            target_dock_id: Target dock ID

        Returns:
            True if successful
        """
        target_dock = self._dock_map.get(target_dock_id)
        if not target_dock:
            return False

        # Get tab content
        tab_id = source_tab_widget.get_tab_id(tab_index)
        content = source_tab_widget.widget(tab_index)
        label = source_tab_widget.tabText(tab_index)

        if not content or not tab_id:
            return False

        # Remove from source
        source_tab_widget.removeTab(tab_index)

        # Check if target has EnhancedTabWidget
        target_content = target_dock.widget()
        if isinstance(target_content, EnhancedTabWidget):
            # Add to existing tab widget
            target_content.addTab(content, label, tab_id=tab_id)
            return True
        else:
            # Create new dock for the tab
            self._on_tab_floated(tab_id, content, "transfer")
            return True

    def get_all_tab_ids(self) -> list[str]:
        """Get all tab IDs across all tab widgets.

        Returns:
            List of all tab IDs
        """
        all_ids = []
        for tab_widget in self._tab_widgets:
            all_ids.extend(self._collect_tab_ids(tab_widget))
        return all_ids

    def _collect_tab_ids(self, tab_widget: EnhancedTabWidget) -> list[str]:
        """Recursively collect tab IDs from a tab widget."""
        ids = []
        for i in range(tab_widget.count()):
            tab_id = tab_widget.get_tab_id(i)
            if tab_id:
                ids.append(tab_id)

            # Check nested
            content = tab_widget.widget(i)
            if isinstance(content, EnhancedTabWidget):
                ids.extend(self._collect_tab_ids(content))

        return ids
