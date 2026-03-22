"""Main application entry point with full factory integration."""

import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import PySide6QtAds as QtAds
from PySide6.QtCore import QByteArray, QSize, Qt, QTimer
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
from widgetsystem.enums import ActionName, DockArea, ResponsiveAction
from widgetsystem.factories.dnd_factory import DnDFactory
from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.layout_factory import LayoutDefinition, LayoutFactory
from widgetsystem.factories.list_factory import ListFactory
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.factories.panel_factory import PanelConfig, PanelFactory
from widgetsystem.factories.responsive_factory import ResponsiveFactory
from widgetsystem.factories.tabs_factory import Tab, TabGroup, TabsFactory
from widgetsystem.factories.theme_factory import ThemeDefinition, ThemeFactory
from widgetsystem.factories.ui_config_factory import UIConfigFactory
from widgetsystem.core.plugin_system import PluginManager, PluginRegistry
from widgetsystem.ui import ConfigurationPanel, InlayTitleBarController

# Import constants from inlay_titlebar
try:
    from widgetsystem.ui.inlay_titlebar import COLLAPSED_HEIGHT
except ImportError:
    COLLAPSED_HEIGHT = 3

# Spacing between titlebar and toolbar to prevent overlap
TITLEBAR_SPACING = 2  # pixels


class MainWindow(QMainWindow):
    """Main application window with docking system and factory integration."""

    def __init__(self) -> None:
        """Initialize main window with all factories and UI components."""
        super().__init__()

        # Enable FULL window transparency with frameless window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        # Track drag position for window movement
        self._drag_pos: tuple[int, int] | None = None

        self.setWindowTitle("ADS Docking System - Transparent Themes")
        self.setMinimumSize(1200, 800)

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

        # Initialize Plugin System
        self._init_plugin_system()

        # Initialize Theme Manager
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.themeChanged.connect(self._on_theme_changed)

        # Create default theme profiles if they don't exist
        self.theme_factory.create_default_profiles()

        # Register theme profiles with ThemeManager
        self._register_theme_profiles()

        # Legacy state variables - delegated to controllers but kept for compatibility
        # These will be removed in future versions once all code uses controllers
        self.panel_counter = 0
        self._docks: list[Any] = []
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

        # Initialize custom gradient system (replaces QtAds default gradients)
        self.gradient_renderer = get_gradient_renderer()

        # Timer for continuous splitter width enforcement (catches DnD operations)
        self._splitter_timer = QTimer(self)
        self._splitter_timer.timeout.connect(self._set_narrow_splitters)
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
        self.dock_ctrl.dockAdded.connect(
            lambda dock_id, dock: self.tab_sys.track_dock_widget(dock_id, dock)
        )

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

        # =================================================================
        # Legacy compatibility - keep old references for gradual migration
        # =================================================================
        self._tab_color_controller = self.tab_sys.tab_color_controller
        self._floating_tracker = self.tab_sys.floating_tracker

        # Build UI with factories (delegates to controllers)
        self._initialize_dnd()
        self._initialize_responsive()
        self._create_menu()
        self._create_global_shortcuts()
        self.menuBar().hide()
        
        # Create Toolbar and dock areas FIRST
        self._create_toolbar()
        self._create_dock_areas()
        self._create_tab_groups()
        
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
        """Set all splitters to ultra-narrow width (1px).

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

        # Apply 1px to all splitters that aren't already 1px
        for splitter in splitters:
            if splitter.handleWidth() != 1:
                splitter.setHandleWidth(1)

    def _apply_custom_gradients(self) -> None:
        """Apply custom gradients to all dock areas, overriding QtAds defaults.

        QtAds renders gradients in C++ (CDockAreaWidget::paintEvent) which ignores
        most QSS properties. This method uses QSS stylesheet to disable those gradients
        by setting explicit background colors and applying CSS gradient overrides.
        """
        # Apply QSS that forces solid backgrounds, hiding QtAds gradients
        gradient_qss = """
        /* Override QtAds CDockAreaWidget gradients with custom styling */
        ads--CDockAreaWidget {
            background-color: #252525;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                        stop:0 #252525, 
                                        stop:1 #1A1A1A);
            color: #E0E0E0;
            border: 1px solid rgba(64, 64, 64, 0.5);
            margin: 0px;
            padding: 0px;
        }
        
        ads--CDockWidget {
            background-color: #252525;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                        stop:0 #252525, 
                                        stop:1 #1A1A1A);
            color: #E0E0E0;
            border: 1px solid rgba(64, 64, 64, 0.5);
            margin: 0px;
            padding: 0px;
        }
        
        ads--CDockAreaTitleBar {
            background-color: #3C4043;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                        stop:0 #3C4043, 
                                        stop:1 #2D2E31);
            color: #E0E0E0;
            border-bottom: 1px solid rgba(64, 64, 64, 0.5);
            margin: 0px;
            padding: 0px;
        }
        
        ads--CFloatingDockContainer {
            background-color: #2D2E31;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                        stop:0 #2D2E31, 
                                        stop:1 #202124);
            color: #E0E0E0;
            border: 1px solid rgba(64, 64, 64, 0.5);
            margin: 0px;
            padding: 0px;
        }
        """

        # Merge with existing theme stylesheet
        app = QApplication.instance()
        if isinstance(app, QApplication):
            current_stylesheet = app.styleSheet()
            # Prepend gradient overrides to ensure they take precedence
            merged_stylesheet = gradient_qss + "\n\n" + current_stylesheet
            app.setStyleSheet(merged_stylesheet)

            # Also apply to dock manager
            if hasattr(self, "dock_manager") and self.dock_manager:
                self.dock_manager.setStyleSheet(merged_stylesheet)

        print("[+] Custom gradients applied - QtAds default gradients overridden")

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

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)
        tab_widget.setTabsClosable(True)

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
        """Apply close button styling after tabs are fully created."""
        tab_bar = tab_widget.tabBar()
        # Use Qt standard close icon
        style = tab_widget.style()
        if style:
            close_icon = style.standardIcon(style.StandardPixmap.SP_TitleBarCloseButton)
        else:
            close_icon = QIcon()

        styled_count = 0
        for i in range(tab_bar.count()):
            close_btn = tab_bar.tabButton(i, tab_bar.ButtonPosition.RightSide)
            if close_btn and isinstance(close_btn, QAbstractButton):
                close_btn.setIcon(close_icon)
                close_btn.setIconSize(QSize(10, 10))
                close_btn.setFixedSize(QSize(14, 14))
                close_btn.setStyleSheet("""
                    background: transparent;
                    border: none;
                    border-radius: 3px;
                    padding: 0px;
                    margin: 0px;
                """)
                styled_count += 1
        print(f"[TAB_STYLE] Styled {styled_count} close buttons in tab widget")

    def _add_tab_recursive(self, parent_widget: QTabWidget, tab: Tab, depth: int = 0) -> None:
        """Recursively add tabs (handling nested children)."""
        # Translate tab name using i18n
        tab_name = self.i18n_factory.translate(tab.title_key, default=tab.id)

        if tab.children:
            # Tab has nested children - create sub-tab widget
            sub_tab_widget = QTabWidget()
            sub_tab_widget.setDocumentMode(True)
            sub_tab_widget.setTabsClosable(True)

            for child_tab in tab.children:
                self._add_tab_recursive(sub_tab_widget, child_tab, depth=depth + 1)

            parent_widget.addTab(sub_tab_widget, tab_name)
            # Style close buttons after tabs are added
            self._style_tab_widget(sub_tab_widget)
        else:
            # Leaf tab - add placeholder content
            content_widget = QWidget()
            parent_widget.addTab(content_widget, tab_name)

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
        """Initialize drag-and-drop system from DnDFactory configuration."""
        try:
            # Load drop zones
            drop_zones = self.dnd_factory.load_drop_zones()
            for zone in drop_zones:
                self.drop_zones_map[zone.area] = zone
                print(f"DnD: Registered drop zone '{zone.id}' for area '{zone.area}'")

            # Load DnD rules
            dnd_rules = self.dnd_factory.load_dnd_rules()
            for rule in dnd_rules:
                if rule.panel_id not in self.dnd_rules_map:
                    self.dnd_rules_map[rule.panel_id] = {}
                self.dnd_rules_map[rule.panel_id][rule.source_area] = rule.allowed_target_areas
                print(
                    f"DnD: Registered rule '{rule.id}' - {rule.panel_id} from {rule.source_area} -> {rule.allowed_target_areas}",
                )

            print(
                f"[+] DnD System initialized: {len(self.drop_zones_map)} zones, {len(self.dnd_rules_map)} panels",
            )
        except Exception as e:
            print(f"[!] Warning: Failed to load DnD configuration: {e}")

    def is_dnd_move_allowed(self, panel_id: str, source_area: str, target_area: str) -> bool:
        """Check if a panel is allowed to move from source to target area."""
        if panel_id not in self.dnd_rules_map:
            return True  # No restrictions for this panel

        panel_rules = self.dnd_rules_map[panel_id]
        if source_area not in panel_rules:
            return True  # No restrictions for this source area

        allowed_targets = panel_rules[source_area]
        if not allowed_targets:
            return False  # Explicit restriction

        return target_area in allowed_targets

    # ------------------------------------------------------------------
    # Responsive Design System
    # ------------------------------------------------------------------

    def _initialize_responsive(self) -> None:
        """Initialize responsive design system from ResponsiveFactory configuration."""
        try:
            breakpoints = self.responsive_factory.load_breakpoints()
            for bp in breakpoints:
                self.responsive_width_ranges[bp.id] = (bp.min_width, bp.max_width)
                print(
                    f"Responsive: Registered breakpoint '{bp.id}' ({bp.min_width}-{bp.max_width}px)",
                )

            rules = self.responsive_factory.load_responsive_rules()
            print(
                f"[+] Responsive System initialized: {len(breakpoints)} breakpoints, {len(rules)} rules",
            )
        except Exception as e:
            print(f"[!] Warning: Failed to load responsive configuration: {e}")

        # Check initial breakpoint on startup
        self.resizeEvent(None)

    def _get_current_breakpoint(self, width: int) -> str | None:
        """Determine current breakpoint based on window width."""
        for breakpoint_id, (min_width, max_width) in self.responsive_width_ranges.items():
            if min_width <= width <= max_width:
                return breakpoint_id
        return None

    def _apply_responsive_rules(self, breakpoint_id: str) -> None:
        """Apply panel visibility rules for the current breakpoint.

        Uses ResponsiveAction enum for type-safe action handling.
        """
        try:
            rules = self.responsive_factory.load_responsive_rules()
            for rule in rules:
                if rule.breakpoint != breakpoint_id:
                    continue

                # Find dock with matching panel_id
                dock = self._find_dock_by_panel_id(rule.panel_id)
                if dock is None:
                    continue

                # Apply rule action using ResponsiveAction enum
                action = rule.action.lower()
                if action == ResponsiveAction.HIDE.value:
                    dock.toggleView(False)
                elif action == ResponsiveAction.SHOW.value:
                    dock.toggleView(True)
                elif action == ResponsiveAction.COLLAPSE.value:
                    dock.setFloating(False)

                self.responsive_applied_rules.add(rule.id)
        except Exception as e:
            print(f"Warning: Failed to apply responsive rules: {e}")

    def _find_dock_by_panel_id(self, panel_id: str) -> Any:
        """Find a dock widget by panel ID (title matching)."""
        for dock in self.docks:
            if hasattr(dock, "windowTitle") and panel_id in dock.windowTitle():
                return dock
        return None

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
            save_action.triggered.connect(self._save_layout)
            self.addAction(save_action)

        if "load_layout" not in self.registered_action_names:
            load_action = QAction(
                self.i18n_factory.translate("menu.file.load", default="Load Layout"),
                self,
            )
            load_action.triggered.connect(self._load_layout)
            self.addAction(load_action)

        if "reset_layout" not in self.registered_action_names:
            reset_action = QAction(
                self.i18n_factory.translate("menu.file.reset", default="Reset Layout"),
                self,
            )
            reset_action.triggered.connect(self._reset_layout)
            self.addAction(reset_action)

        # Add configuration action
        config_action = QAction(
            self.i18n_factory.translate("menu.tools.config", default="Configuration"),
            self,
        )
        config_action.setShortcut("Ctrl+Shift+C")
        config_action.triggered.connect(self._show_configuration_panel)
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

                action.triggered.connect(handler)
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
            shortcut.activated.connect(handler)
            self.global_shortcuts.append(shortcut)

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

    # ------------------------------------------------------------------
    # Inlay Title Bar (Collapsible 3px->36px)
    # ------------------------------------------------------------------

    def _create_inlay_title_bar(self) -> None:
        """Install the hover-expand inlay title bar as a pure overlay.

        The title bar always stays on top and never shifts toolbar/dock content.
        """
        print("[TITLEBAR] Creating InlayTitleBar (overlay mode)...")
        self._inlay_controller = InlayTitleBarController(self)
        self._inlay_controller.install()
        self._inlay_controller.set_title("WidgetSystem - Advanced Docking")

        if self._inlay_controller.titlebar:
            tb = self._inlay_controller.titlebar
            print(f"[TITLEBAR] TitleBar created: {type(tb).__name__}")
            
            # Set initial geometry
            tb_height = tb.height()
            tb.setGeometry(0, 0, self.width(), tb_height)

            # Raise to top of Z-order (above toolbar and dock manager)
            tb.raise_()
            tb.setVisible(True)
            tb.update()

            print(f"[TITLEBAR] Geometry: {tb.geometry()}, Visible: {tb.isVisible()}")
            print("[TITLEBAR] OK - overlay mode, no layout shift on expand")
        else:
            print("[TITLEBAR] ERROR: titlebar is None!")

        # Initial layout sync only. Content does not react to hover expansion.
        self._sync_content_geometry(COLLAPSED_HEIGHT)
    
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

        content_top = COLLAPSED_HEIGHT + TITLEBAR_SPACING
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

        # Keep inlay titlebar spanning the full window width.
        if hasattr(self, "_inlay_controller") and self._inlay_controller.titlebar:
            tb = self._inlay_controller.titlebar
            tb.setGeometry(0, 0, w, tb.height())
            tb.raise_()

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

        # Responsive breakpoints
        new_breakpoint = self._get_current_breakpoint(w)
        if new_breakpoint and new_breakpoint != self.current_breakpoint:
            print(f"Responsive: Breakpoint changed to '{new_breakpoint}' (width={w}px)")
            self.current_breakpoint = new_breakpoint
            self.responsive_applied_rules.clear()
            self._apply_responsive_rules(new_breakpoint)

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
        """Create toolbar with dock management and menu buttons."""
        toolbar = QToolBar(self.i18n_factory.translate("toolbar.title", default="Dock Tools"))
        
        # Add top margin to create spacing below InlayTitleBar
        # TitleBar is 3px (collapsed) or 36px (expanded), we add 2px spacing
        toolbar.setStyleSheet(f"""
            QToolBar {{
                margin-top: {COLLAPSED_HEIGHT + TITLEBAR_SPACING}px;
                spacing: 2px;
            }}
        """)
        
        # Add toolbar to top area
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        # Store reference for positioning
        self._toolbar = toolbar

        # Use fixed toolbar labels here so they are not overridden by i18n entries.
        toolbar.addAction("+").triggered.connect(self._on_new_dock)
        toolbar.addAction("❐").triggered.connect(self._on_float_all)
        toolbar.addAction("▣").triggered.connect(self._on_dock_all)
        toolbar.addSeparator()
        toolbar.addAction("✕").triggered.connect(self._on_close_all)
        toolbar.addSeparator()

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

        toolbar.addSeparator()
        config_btn = QToolButton()
        config_btn.setText("⚙")
        config_btn.setToolTip(self.i18n_factory.translate("toolbar.config", default="Config"))
        config_btn.clicked.connect(self._show_configuration_panel)
        toolbar.addWidget(config_btn)

    def _populate_layouts_menu(self) -> None:
        """Populate layouts menu from LayoutFactory."""
        self.layouts_menu.clear()
        try:
            layouts = self.layout_factory.list_layouts()
            if not layouts:
                empty_action = self.layouts_menu.addAction(
                    self.i18n_factory.translate("layout.none_found", default="No layouts found"),
                )
                empty_action.setEnabled(False)
            else:
                for layout in layouts:
                    action = self.layouts_menu.addAction(layout.name)
                    action.triggered.connect(
                        lambda checked=False, layout=layout: self._load_named_layout(layout),
                    )

            self.layouts_menu.addSeparator()
            self.layouts_menu.addAction(
                self.i18n_factory.translate("layout.reload", default="Reload Layout List"),
            ).triggered.connect(self._reload_layouts_menu)
        except Exception as e:
            error_action = self.layouts_menu.addAction(f"Error: {str(e)[:30]}")
            error_action.setEnabled(False)

    def _reload_layouts_menu(self) -> None:
        """Reload layouts menu."""
        self._populate_layouts_menu()

    def _populate_themes_menu(self) -> None:
        """Populate themes menu from ThemeFactory (legacy) and ThemeManager."""
        self.themes_menu.clear()
        try:
            # Add themes from ThemeManager (includes both legacy and profiles)
            theme_names = self.theme_manager.theme_names()
            if not theme_names:
                empty_action = self.themes_menu.addAction(
                    self.i18n_factory.translate("theme.none_found", default="No themes found"),
                )
                empty_action.setEnabled(False)
            else:
                for theme_id in theme_names:
                    theme = self.theme_manager.get_theme(theme_id)
                    if theme:
                        action = self.themes_menu.addAction(theme.name)
                        action.triggered.connect(
                            lambda checked=False, tid=theme_id: (
                                self.theme_manager.set_current_theme(tid)
                            ),
                        )

            self.themes_menu.addSeparator()
            self.themes_menu.addAction(
                self.i18n_factory.translate("theme.reload", default="Reload Theme List"),
            ).triggered.connect(self._reload_themes_menu)
        except Exception as e:
            error_action = self.themes_menu.addAction(f"Error: {str(e)[:30]}")
            error_action.setEnabled(False)

    def _reload_themes_menu(self) -> None:
        """Reload themes menu by re-registering all themes."""
        # Clear and re-register all themes
        self.theme_manager.clear()
        self._register_theme_profiles()
        self._populate_themes_menu()

    # ------------------------------------------------------------------
    # Layout persistence
    # ------------------------------------------------------------------

    def _save_layout(self) -> None:
        """Save current layout to file."""
        try:
            state: QByteArray = self.dock_manager.saveState()
            print(f"[SAVE] State size: {len(state.data())} bytes")
            self.layout_file.parent.mkdir(parents=True, exist_ok=True)
            print(f"[SAVE] Target directory: {self.layout_file.parent}")
            self.layout_file.write_bytes(state.data())
            written_size = self.layout_file.stat().st_size
            print(f"[SAVE] Written to {self.layout_file}")
            print(f"[SAVE] Actual file size: {written_size} bytes")
            print("[SAVE] [+] Save completed successfully")
            QMessageBox.information(
                self,
                self.i18n_factory.translate("message.success", default="Success"),
                f"{self.i18n_factory.translate('message.layout_saved', default='Layout saved successfully.')}\n{self.layout_file}",
            )
        except Exception as exc:
            print(f"[SAVE] [X] Error: {exc}")
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Failed to save layout:\n{exc}",
            )

    def _load_layout(self) -> None:
        """Load layout from file."""
        try:
            print(f"[LOAD] Attempting to load from {self.layout_file}")
            if not self.layout_file.exists():
                print("[LOAD] [X] File does not exist")
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.warning", default="Warning"),
                    self.i18n_factory.translate(
                        "message.layout_not_found",
                        default="layout.xml not found.",
                    ),
                )
                return
            data = self.layout_file.read_bytes()
            print(f"[LOAD] Read {len(data)} bytes from file")
            restored = self.dock_manager.restoreState(QByteArray(data))
            print(f"[LOAD] restoreState returned: {restored}")
            if not restored:
                print("[LOAD] [X] restoreState failed")
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.warning", default="Warning"),
                    self.i18n_factory.translate(
                        "message.layout_restore_failed",
                        default="Layout could not be restored from file.",
                    ),
                )
                return
            print("[LOAD] [+] Layout restored successfully")
            QMessageBox.information(
                self,
                self.i18n_factory.translate("message.success", default="Success"),
                self.i18n_factory.translate(
                    "message.layout_loaded",
                    default="Layout loaded successfully.",
                ),
            )
        except Exception as exc:
            print(f"[LOAD] [X] Exception: {exc}")
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Failed to load layout:\n{exc}",
            )

    def _load_layout_on_startup(self) -> None:
        """Load the last saved layout silently on app start."""
        print("[STARTUP_LOAD] Starting layout restoration")
        try:
            print(f"[STARTUP_LOAD] Checking {self.layout_file}")
            if not self.layout_file.exists():
                print("[STARTUP_LOAD] [!] File does not exist, skipping restore")
                return
            print("[STARTUP_LOAD] File exists, attempting restore")
            data = self.layout_file.read_bytes()
            print(f"[STARTUP_LOAD] Read {len(data)} bytes")
            restored = self.dock_manager.restoreState(QByteArray(data))
            print(f"[STARTUP_LOAD] restoreState returned: {restored}")
            if not restored:
                print("[STARTUP_LOAD] [!] restoreState failed")
            else:
                print("[STARTUP_LOAD] [+] Restored successfully")
        except Exception as exc:
            print(f"[STARTUP_LOAD] [X] Exception: {exc}")

    def _load_named_layout(self, layout: LayoutDefinition) -> None:
        """Load a named layout from LayoutFactory."""
        try:
            if not layout.file_path.exists():
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.warning", default="Warning"),
                    self.i18n_factory.translate("message.file_not_found", default="File not found")
                    + f":\n{layout.file_path}",
                )
                return
            data = layout.file_path.read_bytes()
            restored = self.dock_manager.restoreState(QByteArray(data))
            if not restored:
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.warning", default="Warning"),
                    self.i18n_factory.translate(
                        "message.layout_restore_failed",
                        default="Layout could not be restored from file.",
                    ),
                )
                return
            QMessageBox.information(
                self,
                self.i18n_factory.translate("message.success", default="Success"),
                f"{self.i18n_factory.translate('message.layout_loaded', default='Layout loaded')}: {layout.name}",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                f"Failed to load layout:\n{exc}",
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

            # Rebuild dock areas and tab groups
            self._create_dock_areas()
            self._create_tab_groups()

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
                        generate_qss = getattr(profile, "generate_qss", None)
                        if not callable(generate_qss):
                            continue
                        theme = Theme(f"profile_{profile_id}", profile_name)
                        qss_content = None
                        try:
                            qss_content = generate_qss()
                        except Exception as e:
                            print(f"[!] Failed to generate QSS for profile '{profile_id}': {e}")
                            qss_content = None
                        if isinstance(qss_content, str):
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
                from PySide6.QtWidgets import QApplication
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
        """Show plugin system information."""
        print("🔌 Zeige Plugin-System Informationen...")
        try:
            # Create a simple info dialog for plugin system
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("🔌 Plugin-System")
            dialog.setGeometry(200, 200, 600, 400)

            layout = QVBoxLayout(dialog)

            title = QLabel("Plugin-System Status")
            from PySide6.QtGui import QFont
            font = QFont()
            font.setPointSize(14)
            font.setBold(True)
            title.setFont(font)
            layout.addWidget(title)

            # Plugin info
            info_text = QTextEdit()
            info_text.setReadOnly(True)

            try:
                from widgetsystem.core.plugin_system import PluginManager, PluginRegistry
                registry = PluginRegistry()
                manager = PluginManager(
                    plugin_dirs=[Path("plugins")],
                    registry=registry
                )

                plugin_info = f"""
Plugin-Registry Status:
• Registrierte Factories: {len(registry.get_all_factories())}
• Geladene Plugins: {len(registry.get_all_plugins())}

Plugin-Manager Status:
• Plugin-Verzeichnisse: {len(manager.plugin_dirs)}
• Registry verbunden: {'Ja' if manager.registry else 'Nein'}

API-Beispiel:
```python
from widgetsystem.core import PluginManager, PluginRegistry

# Registry erstellen
registry = PluginRegistry()

# Manager mit Plugin-Verzeichnissen
manager = PluginManager(
    plugin_dirs=[Path("plugins")],
    registry=registry
)

# Alle Plugins laden
loaded = manager.load_all_plugins()

# Factory registrieren
registry.register_factory("my_factory", MyFactoryClass)
```

Features:
[+] Automatische Plugin-Erkennung
[+] Factory-Registrierung & Lifecycle
[+] Hot-Reload Faehigkeit
[+] Signal-basierte Fehlerbehandlung
[+] Konfigurationsmanagement
                """
            except ImportError:
                plugin_info = """
Plugin-System nicht verfuegbar.

Um das Plugin-System zu aktivieren:
1. Installieren Sie die Plugin-System Dependencies
2. Starten Sie die Anwendung neu

Features (wenn aktiviert):
[+] Automatische Plugin-Erkennung
[+] Factory-Registrierung & Lifecycle
[+] Hot-Reload Faehigkeit
[+] Signal-basierte Fehlerbehandlung
[+] Konfigurationsmanagement
                """

            info_text.setPlainText(plugin_info)
            layout.addWidget(info_text)

            # Close button
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

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
