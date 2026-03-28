"""Main application entry point with full factory integration."""

import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, cast

import PySide6QtAds as QtAds
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTabWidget,
    QToolBar,
    QToolButton,
    QWidget,
)

from widgetsystem.core import Theme, ThemeManager, get_gradient_renderer
from widgetsystem.controllers import (
    DnDController,
    DockController,
    LayoutController,
    ResponsiveController,
    ShortcutController,
    TabSubsystem,
    ThemeController,
)
from widgetsystem.enums import ActionName, DockArea
from widgetsystem.factories.action_factory import ActionFactory
from widgetsystem.factories.dnd_factory import DnDFactory
from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.layout_factory import LayoutDefinition, LayoutFactory
from widgetsystem.factories.list_factory import ListFactory
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.factories.panel_factory import PanelConfig, PanelFactory
from widgetsystem.factories.responsive_factory import ResponsiveFactory
from widgetsystem.factories.splitter_factory import SplitterEventHandler, SplitterFactory
from widgetsystem.factories.tabs_factory import Tab, TabGroup, TabsFactory
from widgetsystem.factories.theme_factory import ThemeDefinition, ThemeFactory
from widgetsystem.factories.toolbar_factory import ToolbarFactory
from widgetsystem.factories.ui_config_factory import UIConfigFactory
from widgetsystem.core.action_registry import ActionRegistry
from widgetsystem.core.plugin_system import PluginManager, PluginRegistry
from widgetsystem.ui import (
    ConfigurationPanel,
    EnhancedTabWidget,
    PluginManagerDialog,
    TabDropIndicatorController,
)

# Load UI dimensions from config
from widgetsystem.factories.ui_dimensions_factory import UIDimensionsFactory

_ui_dims = UIDimensionsFactory.get_instance().get()


class MainWindow(QMainWindow):
    """Main application window with docking system and factory integration."""

    def __init__(self) -> None:
        """Initialize main window with all factories and UI components."""
        super().__init__()

        # Load dimensions from config
        self._dims = _ui_dims

        # Enable FULL window transparency with frameless window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        # Track drag position for window movement
        self._drag_pos: tuple[int, int] | None = None

        self.setWindowTitle("WidgetSystem")
        self.setMinimumSize(self._dims.window.min_width, self._dims.window.min_height)

        # Initialize all factories
        self.layout_factory = LayoutFactory(Path("config"))
        self.theme_factory = ThemeFactory(Path("config"))
        self.panel_factory = PanelFactory(Path("config"))
        self.menu_factory = MenuFactory(Path("config"))
        self.tabs_factory = TabsFactory(Path("config"))
        self.dnd_factory = DnDFactory(Path("config"))
        self.responsive_factory = ResponsiveFactory(Path("config"))
        self.i18n_factory = I18nFactory(Path("config"), locale="de")
        self.list_factory = ListFactory(Path("config"))
        self.ui_config_factory = UIConfigFactory(Path("config"))
        self.action_factory = ActionFactory(Path("config"), self.i18n_factory)
        self.toolbar_factory = ToolbarFactory(Path("config"), self.i18n_factory)

        # Initialize ActionRegistry singleton
        self.action_registry = ActionRegistry.instance()
        self.action_registry.initialize(
            action_factory=self.action_factory,
            parent=self,
            handler_map=self._build_action_handlers(),
        )

        # Initialize Plugin System
        self._init_plugin_system()

        # Initialize Theme Manager (theme registration happens after controllers are ready)
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.themeChanged.connect(self._on_theme_changed)

        # Create default theme profiles if they don't exist
        self.theme_factory.create_default_profiles()

        # NOTE: _register_theme_profiles() is called after controllers are initialized
        # to ensure _tab_color_controller is available for theme application

        # Legacy state variables - delegated to controllers but kept for compatibility
        # These will be removed in future versions once all code uses controllers
        self.panel_counter = 0
        self._docks: list[Any] = []
        self._toolbar: QToolBar | None = None
        self.layouts_menu: QMenu | None = None
        self.themes_menu: QMenu | None = None
        self.action_handlers: dict[str, Any] = {}
        self.registered_action_names: set[str] = set()
        self.registered_shortcuts: set[str] = set()
        self.global_shortcuts: list[QShortcut] = []
        self.dnd_rules_map: dict[str, dict[str, list[str]]] = {}
        self.drop_zones_map: dict[str, Any] = {}
        self.current_breakpoint: str | None = None
        self.responsive_width_ranges: dict[str, tuple[int, int]] = {}
        self.responsive_applied_rules: set[str] = set()
        self._layout_file: Path | None = None

        # Tab controller references (initialized in _reinitialize_tab_controllers)
        self._tab_monitor: Any = None
        self._tab_event_handler: Any = None
        self._tab_visibility: Any = None

        # Initialize custom gradient system (replaces QtAds default gradients)
        self.gradient_renderer = get_gradient_renderer()

        # Splitter behavior: native collapse resistance + corner controls
        self._splitter_handle_width = max(1, self._dims.dock.splitter_width)
        self._splitter_horizontal_bar_width = max(1, self._splitter_handle_width - 1)
        self._splitter_min_remainder = max(4, self._splitter_handle_width * 2)
        self.splitter_factory = SplitterFactory()
        self.splitter_event_handler = SplitterEventHandler(self)
        self.splitter_factory.configure_handler(self.splitter_event_handler)
        self.splitter_event_handler.set_factory(self.splitter_factory)
        self.splitter_event_handler.set_min_remainder(self._splitter_min_remainder)

        # Timer for continuous splitter width enforcement (catches DnD operations)
        self._splitter_timer = QTimer(self)
        self._connect_qt_signal(self._splitter_timer, "timeout", self._set_narrow_splitters)
        self._splitter_timer.start(300)  # Check every 300ms

        # Configure CDockManager flags before creating instance
        self._configure_dock_flags()

        # Create dock manager as central widget
        self.dock_manager: Any = QtAds.CDockManager(self)

        # Set narrow splitter width by finding all QSplitter widgets
        self._set_narrow_splitters()

        # Enable transparency for DockManager central widget
        if hasattr(self.dock_manager, "centralWidget"):
            central = self.dock_manager.centralWidget()
            if central:
                central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Install event filter to patch floating containers before they are shown
        from widgetsystem.ui import FloatingWindowPatcher

        self._floating_patcher = FloatingWindowPatcher()
        app = QApplication.instance()
        if app:
            app.installEventFilter(self._floating_patcher)

        # =================================================================
        # Initialize Controllers (Phase A1)
        # =================================================================

        # TabSubsystem - unified tab management
        self.tab_sys = TabSubsystem()
        self.tab_sys.install(self.dock_manager)

        # DnDController - drag & drop rules
        self.dnd_ctrl = DnDController(self.dnd_factory)

        # DockController - dock lifecycle (needs TabSubsystem for tracking)
        self.dock_ctrl = DockController(
            self.dock_manager,
            self.panel_factory,
            self.tabs_factory,
            self.i18n_factory,
        )
        # Connect dock events to TabSubsystem
        self.dock_ctrl.dockAdded.connect(self.tab_sys.track_dock_widget)

        # LayoutController - layout persistence
        self.layout_ctrl = LayoutController(
            self.dock_manager,
            self.layout_factory,
            self.i18n_factory,
        )

        # ResponsiveController - breakpoints
        self.responsive_ctrl = ResponsiveController(
            self.responsive_factory,
            self.dock_ctrl,
        )

        # ShortcutController - shortcuts and actions
        self.shortcut_ctrl = ShortcutController(
            self.menu_factory,
            self.i18n_factory,
            self,
        )

        # ThemeController - unified theme management
        self.theme_ctrl = ThemeController(self.theme_factory)
        self.theme_ctrl.set_tab_color_controller(self.tab_sys.tab_color_controller)

        # TabDropIndicator - visual feedback for tab drag & drop
        self._tab_drop_indicator: TabDropIndicatorController | None = None

        # =================================================================
        # Legacy compatibility - keep old references for gradual migration
        # =================================================================
        self._tab_color_controller = self.tab_sys.tab_color_controller
        self._floating_tracker = self.tab_sys.floating_tracker

        # Register theme profiles NOW (after controllers are ready)
        self._register_theme_profiles()

        # Build UI with factories (delegates to controllers)
        self._initialize_dnd()
        self._initialize_responsive()
        self._create_menu()
        self._create_global_shortcuts()
        self.menuBar().hide()

        # Create Toolbar and dock areas FIRST
        self._create_toolbar()
        # Use DockController for unified dock/tab creation with full features
        self.dock_ctrl.build_from_config()

        # Create inlay titlebar LAST (so it's on top)
        self._create_inlay_title_bar()
        # Load persisted layout AFTER all docks are created
        self._load_layout_on_startup()

        # Apply custom gradients to override QtAds default gradients
        QTimer.singleShot(150, self._apply_custom_gradients)

    # ------------------------------------------------------------------
    # Properties for Controller Delegation (Backwards Compatibility)
    # ------------------------------------------------------------------

    @property
    def docks(self) -> list[Any]:
        """Get list of dock widgets (delegates to DockController if available)."""
        if hasattr(self, "dock_ctrl") and self.dock_ctrl:
            return self.dock_ctrl.docks
        return self._docks

    @property
    def layout_file(self) -> Path:
        """Get layout file path (delegates to LayoutController if available)."""
        if hasattr(self, "layout_ctrl") and self.layout_ctrl:
            return self.layout_ctrl.layout_file
        if self._layout_file:
            return self._layout_file
        return self._resolve_default_layout_file()

    @layout_file.setter
    def layout_file(self, value: Path) -> None:
        """Set layout file path."""
        self._layout_file = value
        if hasattr(self, "layout_ctrl") and self.layout_ctrl:
            self.layout_ctrl.layout_file = value

    # ------------------------------------------------------------------
    # Dock Manager Configuration (DRY - Single Source of Truth)
    # ------------------------------------------------------------------

    def _configure_dock_flags(self) -> None:
        """Configure CDockManager flags.

        This method is the SINGLE source of truth for dock manager configuration.
        Called by __init__ and _reset_layout to ensure consistent behavior.
        """
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.XmlCompressionEnabled, False
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DockAreaHasCloseButton, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DockAreaHasUndockButton, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DisableTabTextEliding, True
        )
        # Use Qt custom title bar for floating containers (not Windows native)
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerForceNativeTitleBar, False
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerForceQWidgetTitleBar, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerHasWidgetTitle, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerHasWidgetIcon, True
        )

    # ------------------------------------------------------------------
    # Dock creation helpers
    # ------------------------------------------------------------------

    def _set_narrow_splitters(self) -> None:
        """Refresh splitter behavior, widths, tooltips, and corner controls.

        This is called by a QTimer every 300ms to catch splitters recreated
        by QtAds during drag-and-drop operations.
        """
        from PySide6.QtWidgets import QSplitter

        # Find all splitters in the dock manager
        splitters = (
            self.dock_manager.findChildren(QSplitter) if hasattr(self, "dock_manager") else []
        )

        if not splitters:
            return

        for splitter in splitters:
            target_width = self._splitter_width_for(splitter)
            self.splitter_factory.apply_modern_behavior(
                splitter,
                handle_width=target_width,
                min_remainder=self._splitter_min_remainder,
            )
            self.splitter_event_handler.track_splitter(splitter)

            if not bool(splitter.property("ws_splitter_moved_connected")):
                self._connect_qt_signal(
                    splitter,
                    "splitterMoved",
                    lambda _pos, _index, tracked_splitter=splitter: self.splitter_event_handler.on_splitter_moved(
                        tracked_splitter
                    ),
                )
                splitter.setProperty("ws_splitter_moved_connected", True)

            self.splitter_factory.update_handle_tooltips(splitter)

        if not self.splitter_factory.is_corner_drag_active():
            self.splitter_factory.install_corner_handles(self.dock_manager)

    def _splitter_width_for(self, splitter: Any) -> int:
        """Return the desired handle thickness for the given splitter orientation."""
        orientation = splitter.orientation()
        if orientation == Qt.Orientation.Vertical:
            return self._splitter_horizontal_bar_width
        return self._splitter_handle_width

    def _apply_custom_gradients(self) -> None:
        """Re-apply stylesheet to dock manager to ensure gradient overrides work.

        QtAds renders gradients in C++ (CDockAreaWidget::paintEvent) which can
        ignore QSS properties. Re-applying the stylesheet after a short delay
        helps ensure the theme gradients from dark.qss take effect.
        """
        app = QApplication.instance()
        if isinstance(app, QApplication) and hasattr(self, "dock_manager") and self.dock_manager:
            # Re-apply current stylesheet to dock manager for better override
            self.dock_manager.setStyleSheet(app.styleSheet())
            print("[+] Theme stylesheet re-applied to dock manager")

    def _create_empty_dock(
        self,
        title: str,
        area: Any,
        dock_id: str | None = None,
        *,
        closable: bool = True,
        movable: bool = True,
        floatable: bool = True,
        delete_on_close: bool = False,
    ) -> Any:
        """Create a CDockWidget with an empty QWidget and add it to the given area."""
        dock = QtAds.CDockWidget(self.dock_manager, title, self)
        if dock_id:
            dock.setObjectName(dock_id)
        dock.setWidget(QWidget())
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, closable)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, movable)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, floatable)
        dock.setFeature(
            QtAds.CDockWidget.DockWidgetFeature.DockWidgetDeleteOnClose,
            delete_on_close,
        )
        self.dock_manager.addDockWidget(area, dock)
        self.docks.append(dock)

        # Register widget with FloatingStateTracker for float button persistence
        if dock_id:
            self._floating_tracker.track_dock_widget(dock_id, dock)

        return dock

    def _create_dock_areas(self) -> None:
        """Create dock panels from PanelFactory configuration."""
        try:
            panels = self.panel_factory.load_panels()
            for panel in panels:
                self._create_panel_dock(panel)
        except Exception as e:
            print(f"Warning: Failed to load panels from factory: {e}")
            self._create_default_panels()

    def _create_default_panels(self) -> None:
        """Create minimal default panel set if factory fails."""
        self._create_empty_dock("Left Panel", QtAds.LeftDockWidgetArea, dock_id="left_panel")
        self._create_empty_dock("Bottom Panel", QtAds.BottomDockWidgetArea, dock_id="bottom_panel")
        self._create_empty_dock("Center Panel", QtAds.CenterDockWidgetArea, dock_id="center_panel")

    def _create_tab_groups(self) -> None:
        """Create dock panels from TabsFactory configuration (nested tabs)."""
        # Initialize drop indicator controller for visual DnD feedback
        self._tab_drop_indicator = TabDropIndicatorController(self)

        try:
            tab_groups = self.tabs_factory.load_tab_groups()
            for tab_group in tab_groups:
                self._create_tab_group_dock(tab_group)
        except Exception as e:
            print(f"Warning: Failed to load tab groups from factory: {e}")

    def _create_tab_group_dock(self, tab_group: TabGroup) -> None:
        """Create a dock widget containing a tab group with nested tabs."""
        area = self._resolve_dock_area(tab_group.dock_area)
        if area is None:
            return

        # Create enhanced tab widget with full DnD, nesting, and undo/redo support
        tab_widget = EnhancedTabWidget()
        tab_widget.setObjectName(f"tab_group_{tab_group.id}")

        # Connect drop zone signals for visual indicator
        tab_widget.dropZoneChanged.connect(self._on_tab_drop_zone_changed)
        tab_widget.tabNested.connect(self._on_tab_nested)
        tab_widget.tabFloated.connect(self._on_tab_floated)

        # Add tabs recursively
        for tab in tab_group.tabs:
            self._add_tab_recursive(tab_widget, tab, depth=0)

        # Style close buttons for main tab widget
        self._style_tab_widget(tab_widget)

        # Translate group name using i18n
        group_name = self.i18n_factory.translate(tab_group.title_key, default=tab_group.id)

        # Create dock for tab group
        dock = QtAds.CDockWidget(self.dock_manager, group_name, self)
        dock.setObjectName(tab_group.id)
        dock.setWidget(tab_widget)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)
        self.dock_manager.addDockWidget(area, dock)
        self.docks.append(dock)

        # Register widget with FloatingStateTracker for float button persistence
        self._floating_tracker.track_dock_widget(tab_group.id, dock)

    def _style_tab_widget(self, tab_widget: QTabWidget) -> None:
        """Apply consistent styling to tab widget close buttons."""
        # Delay styling to ensure buttons exist
        QTimer.singleShot(50, lambda: self._apply_tab_close_styling(tab_widget))

    def _apply_tab_close_styling(self, tab_widget: QTabWidget) -> None:
        """Apply close button icons after tabs are fully created.

        Note: Button styling is handled by dark.qss (QTabWidget QTabBar::close-button).
        This method only sets the icon and size.
        """
        tab_bar = tab_widget.tabBar()
        # Use Qt standard close icon
        style = tab_widget.style()
        close_icon = style.standardIcon(style.StandardPixmap.SP_TitleBarCloseButton) if style else QIcon()

        for i in range(tab_bar.count()):
            close_btn = tab_bar.tabButton(i, tab_bar.ButtonPosition.RightSide)
            if close_btn and isinstance(close_btn, QAbstractButton):
                close_btn.setIcon(close_icon)
                close_btn.setIconSize(QSize(10, 10))
                close_btn.setFixedSize(QSize(14, 14))

    def _add_tab_recursive(
        self, parent_widget: EnhancedTabWidget, tab: Tab, depth: int = 0
    ) -> None:
        """Recursively add tabs (handling nested children)."""
        # Translate tab name using i18n
        tab_name = self.i18n_factory.translate(tab.title_key, default=tab.id)

        if tab.children:
            # Tab has nested children - create sub-tab widget
            sub_tab_widget = EnhancedTabWidget()
            sub_tab_widget.setObjectName(f"nested_{tab.id}")
            sub_tab_widget.setProperty("parent_tab_id", tab.id)
            sub_tab_widget.setProperty("nesting_depth", depth + 1)

            # Connect signals for nested widget
            sub_tab_widget.dropZoneChanged.connect(self._on_tab_drop_zone_changed)
            sub_tab_widget.tabNested.connect(self._on_tab_nested)
            sub_tab_widget.tabFloated.connect(self._on_tab_floated)

            for child_tab in tab.children:
                self._add_tab_recursive(sub_tab_widget, child_tab, depth=depth + 1)

            # Add container tab with count indicator
            parent_widget.addTab(
                sub_tab_widget,
                f"[{sub_tab_widget.count()}]",
                tab_id=tab.id,
                closable=tab.closable,
                movable=tab.movable,
                floatable=tab.floatable,
            )
            # Style close buttons after tabs are added
            self._style_tab_widget(sub_tab_widget)
        else:
            # Leaf tab - add placeholder content with full metadata
            content_widget = QWidget()
            content_widget.setObjectName(f"content_{tab.id}")
            parent_widget.addTab(
                content_widget,
                tab_name,
                tab_id=tab.id,
                closable=tab.closable,
                movable=tab.movable,
                floatable=tab.floatable,
            )

        # Set active tab if specified
        if tab.active and depth == 0:
            parent_widget.setCurrentIndex(parent_widget.count() - 1)

    def _create_panel_dock(self, panel: PanelConfig) -> None:
        """Create a dock widget from PanelConfig."""
        area = self._resolve_dock_area(panel.area)
        if area is None:
            return

        # Translate panel name using i18n
        panel_name = self.i18n_factory.translate(panel.name_key, default=panel.id)

        # If DnD is disabled for this panel, restrict movement
        movable = panel.movable and panel.dnd_enabled
        floatable = panel.floatable and panel.dnd_enabled

        self._create_empty_dock(
            panel_name,
            area,
            dock_id=panel.id,
            closable=panel.closable,
            movable=movable,
            floatable=floatable,
            delete_on_close=panel.delete_on_close,
        )

    def _resolve_dock_area(self, area_name: str | DockArea) -> Any:
        """Map area name to QtAds dock area constant.

        Args:
            area_name: Area name as string or DockArea enum

        Returns:
            QtAds dock area constant or None if invalid
        """
        # Convert DockArea enum to string value
        if isinstance(area_name, DockArea):
            area_name = area_name.value

        area_map = {
            DockArea.LEFT.value: QtAds.LeftDockWidgetArea,
            DockArea.RIGHT.value: QtAds.RightDockWidgetArea,
            DockArea.BOTTOM.value: QtAds.BottomDockWidgetArea,
            DockArea.CENTER.value: QtAds.CenterDockWidgetArea,
            DockArea.TOP.value: QtAds.TopDockWidgetArea,
        }
        return area_map.get(area_name.strip().lower())

    def _resolve_default_layout_file(self) -> Path:
        """Resolve default layout file path from LayoutFactory configuration."""
        default_layout_id = self.layout_factory.get_default_layout_id()
        if default_layout_id:
            for layout in self.layout_factory.list_layouts():
                if layout.layout_id == default_layout_id:
                    return layout.file_path

        return (Path.cwd() / "data" / "layout.xml").resolve()

    # ------------------------------------------------------------------
    # Drag & Drop (DnD) System
    # ------------------------------------------------------------------

    def _initialize_dnd(self) -> None:
        """Initialize drag-and-drop system via DnDController."""
        self.dnd_ctrl.initialize()

    def is_dnd_move_allowed(self, panel_id: str, source_area: str, target_area: str) -> bool:
        """Check if a panel is allowed to move (delegates to DnDController)."""
        return self.dnd_ctrl.is_move_allowed(panel_id, source_area, target_area)

    # ------------------------------------------------------------------
    # Responsive Design System
    # ------------------------------------------------------------------

    def _initialize_responsive(self) -> None:
        """Initialize responsive design system via ResponsiveController."""
        self.responsive_ctrl.initialize()
        # Check initial breakpoint on startup
        self.resizeEvent(None)

    def _get_current_breakpoint(self, width: int) -> str | None:
        """Determine current breakpoint (delegates to ResponsiveController)."""
        return self.responsive_ctrl.get_breakpoint_for_width(width)

    def _apply_responsive_rules(self, breakpoint_id: str) -> None:
        """Apply panel visibility rules (handled by ResponsiveController).

        Args:
            breakpoint_id: The breakpoint identifier (unused, handled internally)
        """
        # ResponsiveController handles this internally via update_for_width()
        _ = breakpoint_id  # Explicitly mark as intentionally unused

    def _find_dock_by_panel_id(self, panel_id: str) -> Any:
        """Find a dock widget by panel ID (delegates to DockController)."""
        return self.dock_ctrl.find_dock_by_title(panel_id)

    def keyPressEvent(self, event: Any) -> None:
        """Handle global key presses for core layout actions."""
        if event.matches(QKeySequence.StandardKey.Save):
            self._save_layout()
            event.accept()
            return

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_L:
            self._load_layout()
            event.accept()
            return

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_R:
            self._reset_layout()
            event.accept()
            return

        super().keyPressEvent(event)

    # ------------------------------------------------------------------

    def _connect_qt_signal(
        self,
        owner: Any,
        signal_name: str,
        handler: Callable[..., None],
    ) -> None:
        """Connect a Qt signal without triggering static-analysis false positives."""
        signal = getattr(owner, signal_name, None)
        if signal is not None:
            signal.connect(handler)

    # ------------------------------------------------------------------

    def _create_menu(self) -> None:
        """Create menu structure from MenuFactory (hidden)."""
        try:
            menus = self.menu_factory.load_menus()
            for menu_item in menus:
                self._register_menu_item_actions(menu_item)
        except Exception as e:
            print(f"Warning: Failed to load menus from factory: {e}")

        # Register built-in fallback shortcuts only when not provided by config
        if "save_layout" not in self.registered_action_names:
            save_action = QAction(
                self.i18n_factory.translate("menu.file.save", default="Save Layout"),
                self,
            )
            self._connect_qt_signal(save_action, "triggered", self._save_layout)
            self.addAction(save_action)

        if "load_layout" not in self.registered_action_names:
            load_action = QAction(
                self.i18n_factory.translate("menu.file.load", default="Load Layout"),
                self,
            )
            self._connect_qt_signal(load_action, "triggered", self._load_layout)
            self.addAction(load_action)

        if "reset_layout" not in self.registered_action_names:
            reset_action = QAction(
                self.i18n_factory.translate("menu.file.reset", default="Reset Layout"),
                self,
            )
            self._connect_qt_signal(reset_action, "triggered", self._reset_layout)
            self.addAction(reset_action)

        # Add configuration action
        config_action = QAction(
            self.i18n_factory.translate("menu.tools.config", default="Configuration"),
            self,
        )
        config_action.setShortcut("Ctrl+Shift+C")
        self._connect_qt_signal(config_action, "triggered", self._show_configuration_panel)
        self.addAction(config_action)

    def _register_menu_item_actions(self, menu_item: MenuItem) -> None:
        """Register menu item as action (recursively for children)."""
        if (
            menu_item.type == "action"
            and menu_item.action
            and menu_item.id not in self.action_handlers
        ):
            handler = self._get_action_handler(menu_item.action)
            if handler:
                action = QAction(
                    self.i18n_factory.translate(menu_item.label_key, default=menu_item.id),
                    self,
                )
                shortcut = menu_item.shortcut.strip()
                shortcut_key = shortcut.lower()
                layout_actions = {"save_layout", "load_layout", "reset_layout"}
                if (
                    shortcut
                    and shortcut_key not in self.registered_shortcuts
                    and menu_item.action not in layout_actions
                ):
                    action.setShortcut(shortcut)
                    self.registered_shortcuts.add(shortcut_key)

                self._connect_qt_signal(action, "triggered", handler)
                self.registered_action_names.add(menu_item.action)

                self.addAction(action)
                self.action_handlers[menu_item.id] = action

        for child in menu_item.children:
            self._register_menu_item_actions(child)

    def _create_global_shortcuts(self) -> None:
        """Create app-wide global shortcuts for core layout actions."""
        shortcut_map: dict[str, Any] = {
            "Ctrl+S": self._save_layout,
            "Ctrl+L": self._load_layout,
            "Ctrl+R": self._reset_layout,
        }

        for key_sequence, handler in shortcut_map.items():
            shortcut = QShortcut(QKeySequence(key_sequence), self)
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            self._connect_qt_signal(shortcut, "activated", handler)
            self.global_shortcuts.append(shortcut)

        # Undo/Redo shortcuts for tab operations
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self._connect_qt_signal(undo_shortcut, "activated", self._on_undo)
        self.global_shortcuts.append(undo_shortcut)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self._connect_qt_signal(redo_shortcut, "activated", self._on_redo)
        self.global_shortcuts.append(redo_shortcut)

    # ------------------------------------------------------------------
    # Tab Event Handlers (EnhancedTabWidget integration)
    # ------------------------------------------------------------------

    def _on_tab_drop_zone_changed(
        self, zone: str, target_index: int, rect: Any
    ) -> None:
        """Handle drop zone changes for visual indicator.

        Args:
            zone: Drop zone type (none, before, into, after, end)
            target_index: Target tab index
            rect: Highlight rectangle (QRect or None)
        """
        if not self._tab_drop_indicator:
            return

        # Get the sender (EnhancedTabWidget) and its tab bar
        sender = self.sender()
        if isinstance(sender, EnhancedTabWidget):
            tab_bar = sender.tabBar()
            self._tab_drop_indicator.set_tab_bar(tab_bar)
            self._tab_drop_indicator.on_drop_zone_changed(zone, target_index, rect)

    def _on_tab_nested(self, nested_tab_id: str, parent_tab_id: str) -> None:
        """Handle tab nesting event.

        Args:
            nested_tab_id: ID of the nested tab
            parent_tab_id: ID of the parent/container tab
        """
        print(f"[TAB] Nested '{nested_tab_id}' into '{parent_tab_id}'")

    def _on_tab_floated(self, tab_id: str, widget: QWidget) -> None:
        """Handle tab float request - create floating window.

        Args:
            tab_id: ID of the floated tab
            widget: Content widget to float (stored for future use)
        """
        _ = widget  # Will be used when floating dock windows are implemented
        print(f"[TAB] Float requested for '{tab_id}'")
        # Future: Create floating dock window for the tab content

    def _on_undo(self) -> None:
        """Handle undo shortcut (Ctrl+Z)."""
        undo_manager = EnhancedTabWidget.get_undo_manager()
        if undo_manager.can_undo():
            undo_manager.undo()
            print("[UNDO] Tab operation undone")

    def _on_redo(self) -> None:
        """Handle redo shortcut (Ctrl+Y)."""
        undo_manager = EnhancedTabWidget.get_undo_manager()
        if undo_manager.can_redo():
            undo_manager.redo()
            print("[REDO] Tab operation redone")

    def _on_refresh(self) -> None:
        """Refresh toolbar menus, splitter overlays, and dock-related UI state."""
        try:
            self._populate_layouts_menu()
        except Exception as e:
            print(f"[REFRESH] Layout menu refresh failed: {e}")

        try:
            self._populate_themes_menu()
        except Exception as e:
            print(f"[REFRESH] Theme menu refresh failed: {e}")

        try:
            self._set_narrow_splitters()
        except Exception as e:
            print(f"[REFRESH] Splitter refresh failed: {e}")

        try:
            if hasattr(self, "dock_manager") and self.dock_manager:
                self.dock_manager.update()
        except Exception:
            pass

        print("[REFRESH] Main UI refreshed")

    def _get_action_handler(self, action_name: str | ActionName) -> Any:
        """Get handler function for named action.

        Args:
            action_name: Action name as string or ActionName enum

        Returns:
            Handler function or None if action not found
        """
        # Convert ActionName enum to string value
        if isinstance(action_name, ActionName):
            action_name = action_name.value

        handlers: dict[str, Any] = {
            ActionName.SAVE_DOCK.value: self._on_save_dock,
            ActionName.LOAD_DOCK.value: self._on_load_dock,
            ActionName.SAVE_LAYOUT.value: self._save_layout,
            ActionName.LOAD_LAYOUT.value: self._load_layout,
            ActionName.RESET_LAYOUT.value: self._reset_layout,
            ActionName.NEW_DOCK.value: self._on_new_dock,
            ActionName.FLOAT_ALL.value: self._on_float_all,
            ActionName.DOCK_ALL.value: self._on_dock_all,
            ActionName.CLOSE_ALL.value: self._on_close_all,
            # Phase 5: Advanced Features
            ActionName.SHOW_THEME_EDITOR.value: self._show_theme_editor,
            ActionName.SHOW_COLOR_PICKER.value: self._show_color_picker,
            ActionName.SHOW_WIDGET_FEATURES_EDITOR.value: self._show_widget_features_editor,
            ActionName.SHOW_PLUGIN_MANAGER.value: self._show_plugin_manager,
        }
        return handlers.get(action_name)

    def _build_action_handlers(self) -> dict[str, Callable[[], None]]:
        """Build mapping of action names to handler methods for ActionRegistry.

        Returns:
            Dictionary mapping action names to handler functions
        """
        return {
            ActionName.SAVE_DOCK.value: self._on_save_dock,
            ActionName.LOAD_DOCK.value: self._on_load_dock,
            ActionName.SAVE_LAYOUT.value: self._save_layout,
            ActionName.LOAD_LAYOUT.value: self._load_layout,
            ActionName.RESET_LAYOUT.value: self._reset_layout,
            ActionName.NEW_DOCK.value: self._on_new_dock,
            ActionName.FLOAT_ALL.value: self._on_float_all,
            ActionName.DOCK_ALL.value: self._on_dock_all,
            ActionName.CLOSE_ALL.value: self._on_close_all,
            ActionName.SHOW_THEME_EDITOR.value: self._show_theme_editor,
            ActionName.SHOW_COLOR_PICKER.value: self._show_color_picker,
            ActionName.SHOW_WIDGET_FEATURES_EDITOR.value: self._show_widget_features_editor,
            ActionName.SHOW_PLUGIN_MANAGER.value: self._show_plugin_manager,
            "show_configuration": self._show_configuration_panel,
            "undo": self._on_undo,
            "redo": self._on_redo,
            "refresh": self._on_refresh,
        }

    # ------------------------------------------------------------------
    # Inlay Title Bar (Collapsible 3px->36px)
    # ------------------------------------------------------------------

    def _create_inlay_title_bar(self) -> None:
        """Install the hover-expand inlay title bar as menu widget.

        The title bar gets its own space above the toolbar, not overlapping content.
        """
        print("[TITLEBAR] Creating InlayTitleBar (menu widget mode)...")

        # Import here to avoid circular imports
        from widgetsystem.ui.inlay_titlebar import InlayTitleBar

        # Create titlebar directly and set as menu widget
        self._titlebar = InlayTitleBar(self)
        self._titlebar.set_title("WidgetSystem - Advanced Docking")

        # setMenuWidget places it above toolbar in QMainWindow layout
        self.setMenuWidget(self._titlebar)

        print(f"[TITLEBAR] TitleBar created: {type(self._titlebar).__name__}")
        print(f"[TITLEBAR] Height: {self._titlebar.height()}")
        print("[TITLEBAR] OK - menu widget mode, has its own space")

    def _on_titlebar_height_changed(self, new_height: int) -> None:
        """No-op in overlay mode.

        Args:
            new_height: Unused. Kept for compatibility.
        """
        _ = new_height

    def _sync_content_geometry(self, titlebar_height: int) -> None:
        """Position dock manager below toolbar.

        This runs at startup and on resize only. Hover expansion of the overlay
        titlebar must not shift content.

        Args:
            titlebar_height: Unused. Kept for compatibility.
        """
        _ = titlebar_height
        if not hasattr(self, "dock_manager") or self.dock_manager is None:
            return

        content_top = self._dims.titlebar.collapsed_height
        if hasattr(self, "_toolbar") and self._toolbar:
            toolbar_rect = self._toolbar.geometry()
            content_top = toolbar_rect.bottom() + 1

        self.dock_manager.setGeometry(
            0,
            content_top,
            self.width(),
            max(0, self.height() - content_top),
        )
        print(f"[LAYOUT] DockManager positioned once at Y={content_top} (static)")

    def resizeEvent(self, event: Any) -> None:
        """Handle window resize without hover-based layout shifts."""
        super().resizeEvent(event)

        w = self.width()

        # Titlebar is now a menu widget - QMainWindow handles its width automatically
        _ = w  # width handled by QMainWindow layout

        # Keep dock manager filling remaining space below toolbar.
        if hasattr(self, "_toolbar") and self._toolbar and hasattr(self, "dock_manager"):
            toolbar_rect = self._toolbar.geometry()
            content_top = toolbar_rect.bottom() + 1
            self.dock_manager.setGeometry(
                0,
                content_top,
                w,
                max(0, self.height() - content_top),
            )

        # Responsive breakpoints (delegated to ResponsiveController)
        self.responsive_ctrl.update_for_width(w)

    def toggle_max_normal(self) -> None:
        """Toggle between maximized and normal window state."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _title_bar_mouse_press(self, event: Any) -> None:
        """Start window drag on title bar mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint().x(),
                event.globalPosition().toPoint().y(),
            )
            event.accept()

    def _title_bar_mouse_move(self, event: Any) -> None:
        """Move window during title bar drag."""
        if self._drag_pos:
            current_pos = event.globalPosition().toPoint()
            delta_x = current_pos.x() - self._drag_pos[0]
            delta_y = current_pos.y() - self._drag_pos[1]
            self.move(self.x() + delta_x, self.y() + delta_y)
            self._drag_pos = (current_pos.x(), current_pos.y())
            event.accept()

    def _title_bar_mouse_release(self, event: Any) -> None:
        """End window drag."""
        self._drag_pos = None
        event.accept()

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------

    def _create_toolbar(self) -> None:
        """Create toolbar from ToolbarFactory configuration.

        Uses ActionRegistry for actions and ToolbarFactory for layout.
        Falls back to hardcoded toolbar if config is not available.
        """
        # Register menu creators for dynamic menus
        self.toolbar_factory.register_menu_creator(
            "layouts_menu", self._create_layouts_menu
        )
        self.toolbar_factory.register_menu_creator(
            "themes_menu", self._create_themes_menu
        )

        # Try to create toolbar from config
        try:
            toolbars = self.toolbar_factory.create_all_toolbars(
                action_registry=self.action_registry,
                parent=self,
            )
            if toolbars:
                self._toolbar = toolbars[0]
                # Setup dynamic menus after toolbar creation
                self._setup_toolbar_menus()
                return
        except Exception as e:
            print(f"[TOOLBAR] Factory failed, using fallback: {e}")

        # Fallback: Create toolbar manually if factory fails
        self._create_toolbar_fallback()

    def _create_toolbar_fallback(self) -> None:
        """Create toolbar with hardcoded buttons (fallback)."""
        toolbar = QToolBar(self.i18n_factory.translate("toolbar.title", default="Dock Tools"))
        toolbar.setMovable(True)
        toolbar.setFloatable(False)

        toolbar.setStyleSheet("""
            QToolBar {
                margin: 0px;
                padding: 0px;
                spacing: 2px;
            }
        """)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self._toolbar = toolbar

        toolbar.addAction("+").triggered.connect(self._on_new_dock)
        toolbar.addAction("❐").triggered.connect(self._on_float_all)
        toolbar.addAction("▣").triggered.connect(self._on_dock_all)
        toolbar.addSeparator()
        toolbar.addAction("✕").triggered.connect(self._on_close_all)
        toolbar.addSeparator()

        self._setup_toolbar_menus()

        toolbar.addSeparator()
        theme_editor_btn = QToolButton()
        theme_editor_btn.setText("🎨")
        theme_editor_btn.setToolTip(
            self.i18n_factory.translate("action.show_theme_editor", default="Theme Editor"),
        )
        self._connect_qt_signal(theme_editor_btn, "clicked", self._show_theme_editor)
        toolbar.addWidget(theme_editor_btn)

        plugin_btn = QToolButton()
        plugin_btn.setText("🧩")
        plugin_btn.setToolTip(
            self.i18n_factory.translate("action.show_plugin_manager", default="Plugin Manager"),
        )
        self._connect_qt_signal(plugin_btn, "clicked", self._show_plugin_manager)
        toolbar.addWidget(plugin_btn)

        refresh_btn = QToolButton()
        refresh_btn.setText("↻")
        refresh_btn.setToolTip(self.i18n_factory.translate("action.refresh", default="Refresh"))
        self._connect_qt_signal(refresh_btn, "clicked", self._on_refresh)
        toolbar.addWidget(refresh_btn)

        config_btn = QToolButton()
        config_btn.setText("⚙")
        config_btn.setToolTip(self.i18n_factory.translate("toolbar.config", default="Config"))
        self._connect_qt_signal(config_btn, "clicked", self._show_configuration_panel)
        toolbar.addWidget(config_btn)

    def _create_layouts_menu(self) -> QMenu:
        """Create and return layouts dropdown menu."""
        self.layouts_menu = QMenu(
            self.i18n_factory.translate("toolbar.layouts", default="Layouts"),
            self,
        )
        self._populate_layouts_menu()
        return self.layouts_menu

    def _create_themes_menu(self) -> QMenu:
        """Create and return themes dropdown menu."""
        self.themes_menu = QMenu(
            self.i18n_factory.translate("toolbar.themes", default="Themes"),
            self,
        )
        self._populate_themes_menu()
        return self.themes_menu

    def _setup_toolbar_menus(self) -> None:
        """Setup dynamic dropdown menus in toolbar."""
        toolbar = self._toolbar
        if toolbar is None:
            return

        # Create layouts menu if not exists
        if self.layouts_menu is None:
            self.layouts_menu = QMenu(
                self.i18n_factory.translate("toolbar.layouts", default="Layouts"),
                self,
            )
            self._populate_layouts_menu()
            layouts_button = QToolButton()
            layouts_button.setText("▤")
            layouts_button.setToolTip(self.i18n_factory.translate("toolbar.layouts", default="Layouts"))
            layouts_button.setMenu(self.layouts_menu)
            layouts_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            toolbar.addWidget(layouts_button)

        # Create themes menu if not exists
        if self.themes_menu is None:
            self.themes_menu = QMenu(
                self.i18n_factory.translate("toolbar.themes", default="Themes"),
                self,
            )
            self._populate_themes_menu()
            themes_button = QToolButton()
            themes_button.setText("✦")
            themes_button.setToolTip(self.i18n_factory.translate("toolbar.themes", default="Themes"))
            themes_button.setMenu(self.themes_menu)
            themes_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            toolbar.addWidget(themes_button)

    def _populate_layouts_menu(self) -> None:
        """Populate layouts menu from LayoutFactory."""
        menu = self.layouts_menu
        if menu is None:
            return

        menu.clear()
        try:
            layouts = self.layout_factory.list_layouts()
            if not layouts:
                empty_action = menu.addAction(
                    self.i18n_factory.translate("layout.none_found", default="No layouts found"),
                )
                empty_action.setEnabled(False)
            else:
                for layout in layouts:
                    action = menu.addAction(layout.name)
                    action.triggered.connect(
                        lambda checked=False, layout=layout: self._load_named_layout(layout),
                    )

            menu.addSeparator()
            menu.addAction(
                self.i18n_factory.translate("layout.reload", default="Reload Layout List"),
            ).triggered.connect(self._reload_layouts_menu)
        except Exception as e:
            error_action = menu.addAction(f"Error: {str(e)[:30]}")
            error_action.setEnabled(False)

    def _reload_layouts_menu(self) -> None:
        """Reload layouts menu."""
        self._populate_layouts_menu()

    def _populate_themes_menu(self) -> None:
        """Populate themes menu from ThemeFactory (legacy) and ThemeManager."""
        menu = self.themes_menu
        if menu is None:
            return

        menu.clear()
        try:
            # Add themes from ThemeManager (includes both legacy and profiles)
            theme_names = self.theme_manager.theme_names()
            if not theme_names:
                empty_action = menu.addAction(
                    self.i18n_factory.translate("theme.none_found", default="No themes found"),
                )
                empty_action.setEnabled(False)
            else:
                for theme_id in theme_names:
                    theme = self.theme_manager.get_theme(theme_id)
                    if theme:
                        action = menu.addAction(theme.name)
                        action.triggered.connect(
                            lambda checked=False, tid=theme_id: (
                                self.theme_manager.set_current_theme(tid)
                            ),
                        )

            menu.addSeparator()
            menu.addAction(
                self.i18n_factory.translate("theme.reload", default="Reload Theme List"),
            ).triggered.connect(self._reload_themes_menu)
        except Exception as e:
            error_action = menu.addAction(f"Error: {str(e)[:30]}")
            error_action.setEnabled(False)

    def _reload_themes_menu(self) -> None:
        """Reload themes menu by re-registering all themes."""
        # Clear and re-register all themes
        self.theme_manager.clear()
        self._register_theme_profiles()
        self._populate_themes_menu()

    @staticmethod
    def _invoke_callable(func: Any) -> Any:
        """Invoke a callable object and return its result."""
        return func()

    # ------------------------------------------------------------------
    # Layout persistence
    # ------------------------------------------------------------------

    def _save_layout(self) -> None:
        """Save current layout (delegates to LayoutController)."""
        if self.layout_ctrl.save():
            QMessageBox.information(
                self,
                self.i18n_factory.translate("message.success", default="Success"),
                self.i18n_factory.translate(
                    "message.layout_saved", default="Layout saved successfully."
                ),
            )
        else:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("message.warning", default="Warning"),
                self.i18n_factory.translate(
                    "message.layout_save_failed", default="Failed to save layout."
                ),
            )

    def _load_layout(self) -> None:
        """Load layout (delegates to LayoutController)."""
        if self.layout_ctrl.load():
            QMessageBox.information(
                self,
                self.i18n_factory.translate("message.success", default="Success"),
                self.i18n_factory.translate(
                    "message.layout_loaded", default="Layout loaded successfully."
                ),
            )
        else:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("message.warning", default="Warning"),
                self.i18n_factory.translate(
                    "message.layout_load_failed", default="Failed to load layout."
                ),
            )

    def _load_layout_on_startup(self) -> None:
        """Load layout on startup (delegates to LayoutController)."""
        self.layout_ctrl.load_on_startup()

    def _load_named_layout(self, layout: LayoutDefinition) -> None:
        """Load a named layout (delegates to LayoutController)."""
        if self.layout_ctrl.load_named(layout):
            QMessageBox.information(
                self,
                self.i18n_factory.translate("message.success", default="Success"),
                f"{self.i18n_factory.translate('message.layout_loaded', default='Layout loaded')}: {layout.name}",
            )
        else:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("message.warning", default="Warning"),
                self.i18n_factory.translate(
                    "message.layout_load_failed", default="Failed to load layout."
                ),
            )

    def _apply_theme(self, theme: ThemeDefinition) -> None:
        """Apply a named theme from ThemeFactory."""
        try:
            if not theme.file_path.exists():
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.warning", default="Warning"),
                    self.i18n_factory.translate("message.file_not_found", default="File not found")
                    + f":\n{theme.file_path}",
                )
                return
            stylesheet = theme.file_path.read_text(encoding="utf-8")
            app = QApplication.instance()
            if isinstance(app, QApplication):
                app.setStyleSheet(stylesheet)

                # Update tab colors from theme
                self._tab_color_controller.active_color = theme.tab_active_color
                self._tab_color_controller.inactive_color = theme.tab_inactive_color
                self._tab_color_controller.apply()

                QMessageBox.information(
                    self,
                    self.i18n_factory.translate("message.success", default="Success"),
                    f"{self.i18n_factory.translate('message.theme_applied', default='Theme applied')}: {theme.name}",
                )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Failed to apply theme:\n{exc}",
            )

    def _reset_layout(self) -> None:
        """Reset layout to default.

        Performs a complete reset of all subsystems:
        1. Clears dock list
        2. Destroys old dock manager
        3. Resets all controller states
        4. Recreates dock manager with fresh configuration
        5. Rebuilds dock areas
        """
        try:
            # Clear dock list
            self.docks.clear()

            # Destroy old dock manager
            self.dock_manager.deleteLater()

            # Reset controller states (prevents inconsistent state after reset)
            self._reset_controller_states()

            # Reconfigure dock flags (DRY - uses single source of truth)
            self._configure_dock_flags()

            # Recreate dock manager
            self.dock_manager = QtAds.CDockManager(self)

            # Rebuild dock areas and tab groups via DockController
            # Re-create DockController with new dock_manager
            self.dock_ctrl = DockController(
                self.dock_manager,
                self.panel_factory,
                self.tabs_factory,
                self.i18n_factory,
            )
            self.dock_ctrl.dockAdded.connect(self.tab_sys.track_dock_widget)
            self.dock_ctrl.build_from_config()

            # Re-initialize tab subsystem controllers
            self._reinitialize_tab_controllers()

            QMessageBox.information(
                self,
                self.i18n_factory.translate("message.success", default="Success"),
                self.i18n_factory.translate(
                    "message.layout_reset",
                    default="Layout reset to default.",
                ),
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Failed to reset layout:\n{exc}",
            )

    def _reset_controller_states(self) -> None:
        """Reset all controller states to ensure consistent behavior after layout reset."""
        # Reset responsive state
        self.current_breakpoint = None
        self.responsive_applied_rules.clear()

        # Reset DnD state (keep rules, clear runtime state)
        # Rules are loaded from config, no need to clear

        # Reset panel counter for new dynamic panels
        self.panel_counter = 0

    def _reinitialize_tab_controllers(self) -> None:
        """Re-initialize tab-related controllers after dock manager recreation."""
        from widgetsystem.ui import (
            FloatingStateTracker,
            TabColorController,
            TabSelectorEventHandler,
            TabSelectorMonitor,
            TabSelectorVisibilityController,
        )

        # Recreate tab subsystem controllers with new dock manager
        self._tab_monitor = TabSelectorMonitor()
        self._tab_event_handler = TabSelectorEventHandler(
            self.dock_manager, self._tab_monitor
        )
        self._tab_visibility = TabSelectorVisibilityController(self._tab_monitor)

        # Recreate floating tracker
        self._floating_tracker = FloatingStateTracker(self.dock_manager)
        self._floating_tracker.register_post_refresh_callback(
            self._tab_visibility.refresh_area_visibility,
        )

        # Recreate tab color controller
        active, inactive = "#E0E0E0", "#BDBDBD"
        self._tab_color_controller = TabColorController(active, inactive)
        self._tab_color_controller.initialize()

    # ------------------------------------------------------------------
    # Theme Management (New API)
    # ------------------------------------------------------------------

    def _init_plugin_system(self) -> None:
        """Initialize the plugin system and register all factories.

        The plugin system provides:
        - Dynamic factory registration
        - Plugin discovery and hot-reload
        - Configuration persistence
        """
        # Create plugin registry
        self.plugin_registry = PluginRegistry(self)

        # Register all factories with the plugin system
        factories_to_register = [
            ("LayoutFactory", LayoutFactory),
            ("ThemeFactory", ThemeFactory),
            ("PanelFactory", PanelFactory),
            ("MenuFactory", MenuFactory),
            ("TabsFactory", TabsFactory),
            ("DnDFactory", DnDFactory),
            ("ResponsiveFactory", ResponsiveFactory),
            ("I18nFactory", I18nFactory),
            ("ListFactory", ListFactory),
            ("UIConfigFactory", UIConfigFactory),
        ]

        import contextlib

        for factory_name, factory_class in factories_to_register:
            with contextlib.suppress(ValueError):
                self.plugin_registry.register_factory(factory_name, factory_class)

        # Create plugin manager for plugin discovery
        self.plugin_manager = PluginManager(
            plugin_dirs=[Path("plugins")],
            registry=self.plugin_registry,
        )

        # Connect plugin signals
        self.plugin_registry.pluginLoaded.connect(self._on_plugin_loaded)
        self.plugin_registry.pluginUnloaded.connect(self._on_plugin_unloaded)
        self.plugin_registry.factoryRegistered.connect(self._on_factory_registered)
        self.plugin_registry.errorOccurred.connect(self._on_plugin_error)

        # Discover and load plugins from plugins directory (if exists)
        plugins_dir = Path("plugins")
        if plugins_dir.exists():
            self.plugin_manager.load_all_plugins()

        print(f"[+] Plugin system initialized with {len(self.plugin_registry.factories)} factories")

    def _on_plugin_loaded(self, plugin_name: str) -> None:
        """Handle plugin loaded event."""
        print(f"[+] Plugin loaded: {plugin_name}")

    def _on_plugin_unloaded(self, plugin_name: str) -> None:
        """Handle plugin unloaded event."""
        print(f"[+] Plugin unloaded: {plugin_name}")

    def _on_factory_registered(self, factory_name: str) -> None:
        """Handle factory registered event."""
        print(f"  -> Factory registered: {factory_name}")

    def _on_plugin_error(self, error_msg: str) -> None:
        """Handle plugin error event."""
        print(f"[!] Plugin error: {error_msg}")

    def _register_theme_profiles(self) -> None:
        """Register all available theme profiles with ThemeManager."""
        # Register legacy QSS themes (if supported by ThemeFactory implementation)
        list_themes = getattr(self.theme_factory, "list_themes", None)
        if callable(list_themes):
            theme_defs = list_themes()
            if not isinstance(theme_defs, Iterable):
                theme_defs = []

            for theme_def in theme_defs:
                theme = Theme(theme_def.theme_id, theme_def.name)
                try:
                    if theme_def.file_path.exists():
                        theme.set_stylesheet(theme_def.file_path.read_text(encoding="utf-8"))
                        theme.set_property("tab_active_color", theme_def.tab_active_color)
                        theme.set_property("tab_inactive_color", theme_def.tab_inactive_color)
                        self.theme_manager.register_theme(theme)
                        print(f"[+] Registered legacy theme: {theme_def.name}")
                except Exception as e:
                    print(f"Failed to register legacy theme '{theme_def.name}': {e}")

        # Register new theme profiles (if supported by ThemeFactory implementation)
        list_profiles = getattr(self.theme_factory, "list_profiles", None)
        load_profile = getattr(self.theme_factory, "load_profile", None)
        if callable(list_profiles) and callable(load_profile):
            profile_ids = list_profiles()
            if isinstance(profile_ids, Iterable):
                for profile_id in profile_ids:
                    try:
                        profile = load_profile(profile_id)
                        if not profile:
                            continue
                        profile_name = getattr(profile, "name", None)
                        if not isinstance(profile_name, str):
                            continue
                        qss_generator = getattr(profile, "generate_qss", None)
                        if not isinstance(qss_generator, Callable):
                            continue
                        theme = Theme(f"profile_{profile_id}", profile_name)
                        qss_content = None
                        try:
                            result = self._invoke_callable(cast(Any, qss_generator))
                            qss_content = result if isinstance(result, str) else None
                        except TypeError:
                            # generate_qss might not be callable, skip this profile
                            continue
                        except Exception as e:
                            print(f"[!] Failed to generate QSS for profile '{profile_id}': {e}")
                            qss_content = None
                        if qss_content:
                            theme.set_stylesheet(qss_content)
                            theme.set_property("is_profile", True)
                            theme.set_property("profile_id", profile_id)
                            self.theme_manager.register_theme(theme)
                            print(f"[+] Registered profile theme: {profile_name}")
                    except Exception as e:
                        print(f"[!] Failed to register profile theme '{profile_id}': {e}")

        # Set default theme
        default_theme_id = self.theme_factory.get_default_theme_id()
        if default_theme_id:
            self.theme_manager.set_current_theme(default_theme_id)
        elif self.theme_manager.theme_names():
            # Fallback to first available theme
            self.theme_manager.set_current_theme(self.theme_manager.theme_names()[0])

    def _on_theme_changed(self, theme: Theme) -> None:
        """Handle theme change signal from ThemeManager.

        Args:
            theme: New theme to apply
        """
        try:
            app = QApplication.instance()
            if isinstance(app, QApplication):
                # Apply stylesheet to application
                app.setStyleSheet(theme.stylesheet)

                # ALSO apply to DockManager for better transparency support
                if hasattr(self, "dock_manager") and self.dock_manager:
                    self.dock_manager.setStyleSheet(theme.stylesheet)

                # Apply custom palette if available
                if theme.has_custom_palette and theme.palette:
                    app.setPalette(theme.palette)

                # Update tab colors
                tab_active = theme.get_property("tab_active_color", "#E0E0E0")
                tab_inactive = theme.get_property("tab_inactive_color", "#BDBDBD")
                self._tab_color_controller.active_color = tab_active
                self._tab_color_controller.inactive_color = tab_inactive
                self._tab_color_controller.apply()

                print(f"[+] Theme applied: {theme.name}")
                print(f"  Stylesheet length: {len(theme.stylesheet)} chars")
                print(f"  Has rgba colors: {'rgba(' in theme.stylesheet}")
        except Exception as e:
            print(f"[!] Failed to apply theme '{theme.name}': {e}")

    def _apply_theme_profile(self, profile_id: str) -> None:
        """Apply a theme profile by ID.

        Args:
            profile_id: Profile identifier
        """
        theme_id = f"profile_{profile_id}"
        if self.theme_manager.set_current_theme(theme_id):
            theme = self.theme_manager.current_theme()
            if theme:
                QMessageBox.information(
                    self,
                    self.i18n_factory.translate("message.success", default="Success"),
                    f"{self.i18n_factory.translate('message.theme_applied', default='Theme applied')}: {theme.name}",
                )
        else:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("message.warning", default="Warning"),
                self.i18n_factory.translate("message.theme_not_found", default="Theme not found")
                + f": {profile_id}",
            )

    # ------------------------------------------------------------------
    # Toolbar actions
    # ------------------------------------------------------------------

    def _on_save_dock(self) -> None:
        """Menu action: Save dock."""
        self._save_layout()

    def _on_load_dock(self) -> None:
        """Menu action: Load dock."""
        self._load_layout()

    def _on_new_dock(self) -> None:
        """Toolbar action: Create new dock and add to configuration."""
        self.panel_counter += 1
        panel_id = f"dynamic_panel_{self.panel_counter}"
        panel_name_key = f"panel.dynamic_{self.panel_counter}"

        # Add to panel configuration for persistence
        self.panel_factory.add_panel(
            panel_id,
            panel_name_key,
            area="center",
            closable=True,
            movable=True,
        )

        self._create_empty_dock(
            self.i18n_factory.translate("panel.new", default=f"Panel {self.panel_counter}"),
            QtAds.CenterDockWidgetArea,
            dock_id=panel_id,
        )

    def _on_float_all(self) -> None:
        """Toolbar action: Float all docks."""
        for dock in list(self.docks):
            dock.setFloating()

    def _on_dock_all(self) -> None:
        """Toolbar action: Dock all floating panels."""
        for dock in list(self.docks):
            if dock.isFloating():
                self.dock_manager.addDockWidget(QtAds.CenterDockWidgetArea, dock)

    def _on_close_all(self) -> None:
        """Toolbar action: Close all docks."""
        for dock in list(self.docks):
            dock.closeDockWidget()

    def _show_configuration_panel(self) -> None:
        """Show configuration panel for UI customization."""
        try:
            # Create configuration panel widget
            config_widget_content = ConfigurationPanel(Path("config"), self.i18n_factory)

            # Find or create configuration dock
            config_dock = None
            for dock in self.docks:
                if hasattr(dock, "windowTitle") and "Configuration" in dock.windowTitle():
                    config_dock = dock
                    break

            if config_dock is None:
                # Create new configuration dock
                config_dock = QtAds.CDockWidget(
                    self.dock_manager,
                    self.i18n_factory.translate("toolbar.config", default="Configuration"),
                    self,
                )
                config_dock.setWidget(config_widget_content)
                config_dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
                config_dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
                config_dock.setFeature(
                    QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable,
                    True,
                )
                self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, config_dock)
                self.docks.append(config_dock)

            # Connect signals for live updates
            config_widget_content.config_changed.connect(self._on_config_changed)

        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Failed to show configuration panel:\n{e}",
            )

    def _on_config_changed(self, category: str) -> None:
        """Handle configuration changes."""
        try:
            if category == "menus":
                self.menu_factory = MenuFactory(Path("config"))
                print("[+] Menus configuration reloaded")
            elif category == "lists":
                self.list_factory = ListFactory(Path("config"))
                print("[+] Lists configuration reloaded")
            elif category == "tabs":
                self.tabs_factory = TabsFactory(Path("config"))
                print("[+] Tabs configuration reloaded")
            elif category == "panels":
                self.panel_factory = PanelFactory(Path("config"))
                print("[+] Panels configuration reloaded")
        except Exception as e:
            print(f"Warning: Failed to reload {category} configuration: {e}")

    # ------------------------------------------------------------------
    # Phase 5: Advanced Features
    # ------------------------------------------------------------------

    def _show_theme_editor(self) -> None:
        """Show live theme editor dialog."""
        print("🎨 Öffne Theme-Editor...")
        try:
            from widgetsystem.ui.theme_editor import ThemeEditorDialog
            dialog = ThemeEditorDialog(Path("config"))
            dialog.exec()
            print("  [+] Theme-Editor geschlossen")
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Theme-Editor konnte nicht geöffnet werden:\n{e}",
            )
            print(f"  [X] Fehler beim Oeffnen des Theme-Editors: {e}")

    def _show_color_picker(self) -> None:
        """Show ARGB color picker dialog."""
        print("🖌️ Öffne ARGB Color-Picker...")
        try:
            from widgetsystem.ui.argb_color_picker import ARGBColorPickerDialog
            dialog = ARGBColorPickerDialog("#FFFF0000")
            if dialog.exec():
                color = dialog.get_color()
                print(f"  [+] Farbe ausgewaehlt: {color}")
                # Copy to clipboard for easy use
                clipboard = QApplication.clipboard()
                clipboard.setText(color)
                QMessageBox.information(
                    self,
                    self.i18n_factory.translate("message.success", default="Success"),
                    f"Farbe in Zwischenablage kopiert:\n{color}",
                )
            else:
                print("  ℹ️ Color-Picker abgebrochen")
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Color-Picker konnte nicht geöffnet werden:\n{e}",
            )
            print(f"  [X] Fehler beim Oeffnen des Color-Pickers: {e}")

    def _show_widget_features_editor(self) -> None:
        """Show widget features editor dialog."""
        print("⚙️ Öffne Widget-Features Editor...")
        try:
            from widgetsystem.ui.widget_features_editor import WidgetFeaturesEditorDialog
            dialog = WidgetFeaturesEditorDialog(Path("config"))
            dialog.exec()
            print("  [+] Widget-Features Editor geschlossen")
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Widget-Features Editor konnte nicht geöffnet werden:\n{e}",
            )
            print(f"  [X] Fehler beim Oeffnen des Widget-Features Editors: {e}")

    def _show_plugin_manager(self) -> None:
        """Show plugin system information using PluginManagerDialog."""
        print("[+] Zeige Plugin-System Informationen...")
        try:
            dialog = PluginManagerDialog(
                self.plugin_registry,
                self.plugin_manager,
                parent=self,
            )
            dialog.exec()
            print("  [+] Plugin-System Dialog geschlossen")
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Plugin-System konnte nicht geöffnet werden:\n{e}",
            )
            print(f"  [X] Fehler beim Oeffnen des Plugin-Systems: {e}")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------


def main() -> None:
    """Application entry point."""
    app = QApplication(sys.argv)

    try:
        theme_factory = ThemeFactory(Path("config"))
        stylesheet = theme_factory.get_default_stylesheet()
        if stylesheet:
            app.setStyleSheet(stylesheet)
    except Exception as e:
        print(f"Warning: Failed to load default theme: {e}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
