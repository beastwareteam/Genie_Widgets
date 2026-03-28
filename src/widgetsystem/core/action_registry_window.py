"""Demo for Action Registry - centralized action management for menus and toolbars.

Features demonstrated:
- ActionFactory: Loading actions from config/actions.json
- ActionRegistry: Singleton for shared QAction instances
- ToolbarFactory: Creating toolbars from config
- StatusBar: Showing status tips on action hover
- Checkable Actions: Toggle buttons with state
- Context Menus: Right-click menus using registry actions
- Keyboard Shortcuts: Global shortcuts from config
- QFileDialog: Save/Load file dialogs
- QMessageBox: Confirmation dialogs
- Dark Theme: Consistent dark styling
"""

# ruff: noqa: I001
# pylint: disable=no-member

from collections.abc import Callable
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any, cast

import PySide6QtAds as QtAds
from PySide6.QtCore import QEasingCurve, QEvent, QMimeData, QPropertyAnimation, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QDrag, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QStyle,
)

from widgetsystem.core.action_registry import ActionRegistry
from widgetsystem.core.action_registry import STANDARD_ICONS
from widgetsystem.enums import ActionName
from widgetsystem.factories.action_factory import ActionFactory
from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.layout_factory import LayoutDefinition, LayoutFactory
from widgetsystem.factories.splitter_factory import (
    SplitterEventHandler,
    SplitterFactory,
)
from widgetsystem.factories.theme_factory import ThemeDefinition, ThemeFactory
from widgetsystem.factories.toolbar_factory import ToolbarFactory

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


# Dark theme stylesheet base (without splitter styling, which comes from SplitterFactory)
_DARK_STYLESHEET_BASE = """
QMainWindow, QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
}

QMenuBar {
    background-color: #3c3c3c;
    color: #e0e0e0;
    border-bottom: 1px solid #505050;
}

QMenuBar::item {
    background-color: #3c3c3c;
    color: #e0e0e0;
    padding: 4px 8px;
}

QMenuBar::item:selected {
    background-color: #505050;
    color: #ffffff;
}

QMenu {
    background-color: #3c3c3c;
    color: #e0e0e0;
    border: 1px solid #505050;
}

QMenu::item {
    background-color: #3c3c3c;
    color: #e0e0e0;
    padding: 6px 24px 6px 12px;
}

QMenu::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QMenu::item:!selected {
    background-color: #3c3c3c;
    color: #e0e0e0;
}

QMenu::item:disabled {
    background-color: #3c3c3c;
    color: #808080;
}

QMenu::separator {
    height: 1px;
    background-color: #505050;
    margin: 4px 8px;
}

QToolBar {
    background-color: #3c3c3c;
    border: none;
    spacing: 4px;
    padding: 4px;
}

QToolBar::separator {
    width: 1px;
    background-color: #505050;
    margin: 4px 2px;
}

/* Splitter styling is injected by SplitterFactory at initialization */

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}

QToolButton:hover {
    background-color: #505050;
    border: 1px solid #606060;
    color: #ffffff;
}

QToolButton:pressed {
    background-color: #404040;
    color: #ffffff;
}

QToolButton:checked {
    background-color: #0078d4;
    border: 1px solid #0078d4;
    color: #ffffff;
}

QToolButton::menu-indicator {
    image: none;
}

QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    border-top: 1px solid #005a9e;
}

QLabel {
    color: #e0e0e0;
}
"""


def _build_stylesheet_with_splitter_styling(splitter_factory: SplitterFactory) -> str:
    """Build complete stylesheet combining base styling with factory-generated splitter styles.

    Args:
        splitter_factory: SplitterFactory instance to get splitter styling from

    Returns:
        Complete stylesheet string with all components styled
    """
    return _DARK_STYLESHEET_BASE + splitter_factory.generate_stylesheet()


@dataclass
class CustomActionDefinition:
    """Typed runtime definition for persisted custom actions."""

    id: str
    name: str
    label: str
    message: str
    icon: str = ""
    description: str = "Benutzerdefinierte Laufzeit-Aktion"
    enabled: bool = True


class ActionRegistryDemo(QMainWindow):
    """Demo window showing all ActionRegistry capabilities."""

    _corner_settle_count: int

    def __init__(self) -> None:
        """Initialize the demo window."""
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle("Action Registry Demo - Full Features")
        self.setGeometry(100, 100, 1000, 700)

        self.log_text = QTextEdit()
        self.status_bar = QStatusBar()
        self.toolbars: list[QToolBar] = []
        self.layouts_menu = QMenu(self)
        self.themes_menu = QMenu(self)
        self.dock_manager: Any = None
        self.docks: list[Any] = []
        self._custom_actions: dict[str, QAction] = {}
        self._custom_action_definitions: dict[str, CustomActionDefinition] = {}
        self._panel_counter: int = 0
        self._panel_toolbar_object_counter: int = 0
        self._splitter_timer = QTimer(self)
        self._corner_handle_timer = QTimer(self)
        self._corner_handle_timer.setSingleShot(True)
        self._splitter_handle_width = 6
        self._splitter_min_remainder = 18
        self._dock_splitters_auto_collapse_enabled = True
        self._dock_splitters_hierarchical_collapse_enabled = True
        self._splitter_animation_steps = 14
        self._splitter_animation_interval_ms = 16
        self._splitter_animation_timers: list[QTimer] = []
        self._splitter_known_ids: set[int] = set()
        self._splitter_last_positions: dict[tuple[int, int], int] = {}
        self._corner_settle_count: int = 0
        self._toolbar_slide_animations: list[QPropertyAnimation] = []
        self._panel_toolbar_scroll_areas: dict[int, QScrollArea] = {}
        self._panel_toolbar_slide_buttons: dict[int, tuple[QToolButton, QToolButton]] = {}
        self._toolbar_drag_start_pos: dict[int, Any] = {}
        self._toolbar_drag_action: dict[int, QAction] = {}
        self._configuration_panel: Any | None = None

        # Initialize factories
        config_path = WORKSPACE_ROOT / "config"
        self.i18n_factory = I18nFactory(config_path, locale="en")
        self.action_factory = ActionFactory(config_path, self.i18n_factory)
        self.layout_factory = LayoutFactory(config_path, self.i18n_factory)
        self.theme_factory = ThemeFactory(config_path, self.i18n_factory)
        self.toolbar_factory = ToolbarFactory(config_path, self.i18n_factory)
        self.custom_actions_config_path = config_path / "custom_actions.json"

        # Initialize SplitterFactory with event handler
        self.splitter_factory = SplitterFactory()
        self.splitter_event_handler = SplitterEventHandler(self)
        self.splitter_factory.configure_handler(self.splitter_event_handler)
        self.splitter_event_handler.set_factory(self.splitter_factory)
        self.splitter_event_handler.set_restore_callback(self._on_splitter_restored)
        self.splitter_event_handler.set_min_remainder(self._splitter_min_remainder)
        self._corner_handles_enabled: bool = True  # Enabled by default

        # Initialize ActionRegistry
        self.action_registry = ActionRegistry.instance()
        self.action_registry.initialize(
            action_factory=self.action_factory,
            parent=self,
            handler_map=self._build_handlers(),
        )
        self._load_custom_actions()

        # Setup UI
        self._setup_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._setup_context_menu()
        self._add_checkable_actions()

        # Apply stylesheet with splitter styling
        stylesheet = _build_stylesheet_with_splitter_styling(self.splitter_factory)
        self.setStyleSheet(stylesheet)

        # Initial log
        self._log("ActionRegistry Demo initialized")
        self._log(f"Loaded {len(self.action_registry.list_action_ids())} actions from config")
        self._log(f"Categories: {', '.join(self.action_factory.list_categories())}")
        self._log("Right-click anywhere for context menu!")

    def _build_handlers(self) -> dict[str, Callable[[], None]]:
        """Build action handlers aligned with ActionName enum (same standard as MainWindow)."""
        return {
            ActionName.SAVE_LAYOUT.value: self._on_save_layout,
            ActionName.LOAD_LAYOUT.value: self._on_load_layout,
            ActionName.RESET_LAYOUT.value: self._on_reset_layout,
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

    def _connect_signal(self, signal: Any, handler: Callable[..., object]) -> None:
        """Connect a Qt signal to a handler with runtime safety."""
        connect_method = getattr(signal, "connect", None)
        if callable(connect_method):
            connect_method(handler)

    def _setup_ui(self) -> None:
        """Setup central CDockManager with demo dock panels (ADS standard)."""
        config_flags = QtAds.CDockManager.eConfigFlag
        requested_flags: list[tuple[str, bool]] = [
            ("OpaqueSplitterResize", True),
            ("XmlCompressionEnabled", False),
            ("AllTabsHaveCloseButton", True),
            ("DockAreaHasCloseButton", True),
            ("DockAreaHasUndockButton", True),
            ("DisableTabTextEliding", True),
            ("FloatingContainerForceQWidgetTitleBar", True),
        ]
        for flag_name, enabled in requested_flags:
            flag = getattr(config_flags, flag_name, None)
            if flag is not None:
                QtAds.CDockManager.setConfigFlag(flag, enabled)

        self.dock_manager = QtAds.CDockManager(self)
        self.dock_manager.installEventFilter(self)
        self.setCentralWidget(self.dock_manager)

        actions_dock = self._create_actions_dock()
        self.dock_manager.addDockWidget(QtAds.CenterDockWidgetArea, actions_dock)
        self.docks.append(actions_dock)

        log_dock = self._create_log_dock()
        self.dock_manager.addDockWidget(QtAds.BottomDockWidgetArea, log_dock)
        self.docks.append(log_dock)

        casting_dock = self._create_casting_toolbar_dock()
        self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, casting_dock)
        self.docks.append(casting_dock)

        left_dock = self._create_info_dock("📁 Left Tools", "Left area panel")
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, left_dock)
        self.docks.append(left_dock)

        top_dock = self._create_info_dock("📌 Top Monitor", "Top area panel")
        self.dock_manager.addDockWidget(QtAds.TopDockWidgetArea, top_dock)
        self.docks.append(top_dock)

        right_aux_dock = self._create_info_dock("🧭 Right Aux", "Second right area panel")
        self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, right_aux_dock)
        self.docks.append(right_aux_dock)

        bottom_aux_dock = self._create_info_dock("📊 Bottom Aux", "Second bottom area panel")
        self.dock_manager.addDockWidget(QtAds.BottomDockWidgetArea, bottom_aux_dock)
        self.docks.append(bottom_aux_dock)

        self._initialize_modern_splitters()

    def _create_dock_widget(self, title: str) -> Any:
        """Create CDockWidget with compatibility for different QtAds signatures."""
        try:
            return QtAds.CDockWidget(self.dock_manager, title, self)
        except (TypeError, AttributeError):
            pass

        try:
            return QtAds.CDockWidget(self.dock_manager, title)
        except (TypeError, AttributeError):
            pass

        try:
            return QtAds.CDockWidget(title, self)
        except (TypeError, AttributeError):
            pass

        return QtAds.CDockWidget(title)

    def _initialize_modern_splitters(self) -> None:
        """Upgrade splitters to modern curtain-like behavior with DnD persistence."""
        self._splitter_timer.setSingleShot(True)
        self._set_modern_splitter_behavior()
        self._connect_signal(self._splitter_timer.timeout, self._set_modern_splitter_behavior)
        self._connect_signal(
            self._corner_handle_timer.timeout,
            lambda: self.splitter_factory.install_corner_handles(self.dock_manager)
            if self.dock_manager is not None
            else None,
        )
        # Single settle timer: fire once after layout has fully stabilised.
        # The old pattern (4 rapid-fire timers at 120/350/700/1200 ms) caused
        # repeated install_corner_handles calls before async deleteLater had
        # finished, producing ghost/shadow overlay widgets.
        self._schedule_splitter_refresh(1200)

    def _schedule_splitter_refresh(self, delay_ms: int = 60) -> None:
        """Debounced splitter refresh to avoid continuous heavy polling."""
        self._splitter_timer.stop()
        self._splitter_timer.start(max(16, delay_ms))

    def _ensure_splitter_connections(self, splitter: QSplitter) -> None:
        """Connect splitter signals once to avoid repeated runtime overhead."""
        if bool(splitter.property("ws_splitter_moved_connected")):
            return

        self._connect_signal(
            splitter.splitterMoved,
            lambda pos, index, tracked_splitter=splitter: self._on_splitter_moved_runtime(
                tracked_splitter,
                pos,
                index,
            ),
        )
        splitter.installEventFilter(self)
        splitter.setProperty("ws_splitter_moved_connected", True)

    def resizeEvent(self, event: Any) -> None:
        """Refresh splitter overlays when the main window size changes."""
        super().resizeEvent(event)
        if (
            self.dock_manager is not None
            and self._corner_handles_enabled
            and not self.splitter_factory.is_corner_drag_active()
        ):
            # Only sync (reposition existing handles), never reinstall on resize.
            # Reinstalling during resize causes ghost handles because the previous
            # handles are removed asynchronously while new ones are already created.
            self.splitter_factory.sync_corner_handles()
            self._schedule_splitter_refresh(60)

    def _on_splitter_moved_runtime(self, splitter: QSplitter, pos: int, index: int) -> None:
        """Fast runtime callback for splitter movement (low-latency path)."""
        self.splitter_event_handler.on_splitter_moved(splitter)

        if index > 0:
            key = (id(splitter), index)
            self._splitter_last_positions[key] = pos

        if (
            self._corner_handles_enabled
            and not self.splitter_factory.has_corner_handles()
            and not self.splitter_factory.is_corner_drag_active()
            and self.dock_manager is not None
        ):
            self._schedule_splitter_refresh(20)
            return

        self.splitter_factory.sync_corner_handles()

    def _set_modern_splitter_behavior(self) -> None:
        """Configure all splitters in the dock manager with modern behavior (delegated to factory)."""
        if self.dock_manager is None:
            return

        splitters = self.dock_manager.findChildren(QSplitter)
        current_ids = {id(splitter) for splitter in splitters}

        for splitter in splitters:
            self.splitter_factory.apply_modern_behavior(
                splitter,
                handle_width=self._splitter_handle_width,
                min_remainder=self._splitter_min_remainder,
                allow_auto_collapse=self._dock_splitters_auto_collapse_enabled,
                hierarchical_collapse=self._dock_splitters_hierarchical_collapse_enabled,
            )
            self.splitter_event_handler.track_splitter(splitter)
            self._ensure_splitter_connections(splitter)
            self.splitter_factory.update_handle_tooltips(splitter)

        # Corner handle update strategy:
        # - Full reinstall only when splitter COUNT changes (panels opened/closed)
        # - Sync only (reposition existing handles) during normal movement/resize
        # - Never reinstall while drag is active (prevents ghost handles)
        # Ghost handles occur when install_corner_handles is called too rapidly:
        # clear_corner_handles removes old handles via deleteLater (async) while
        # new ones are already placed - both visible briefly = ghost effect.
        _CORNER_SETTLE_PASSES = 3
        if (
            hasattr(self, "_corner_handles_enabled")
            and self._corner_handles_enabled
            and not self.splitter_factory.is_corner_drag_active()
        ):
            settle_count = getattr(self, "_corner_settle_count", 0)
            count_changed = len(current_ids) != len(self._splitter_known_ids)
            if count_changed or settle_count < _CORNER_SETTLE_PASSES:
                # Debounced reinstall: restart the timer so rapid consecutive
                # calls collapse into one. Using a dedicated QTimer instead of
                # raw QTimer.singleShot prevents overlapping install calls that
                # create ghost handles (old handles deleted async while new ones
                # are already placed).
                self._corner_handle_timer.stop()
                self._corner_handle_timer.start(80)
                self._corner_settle_count = settle_count + 1
            else:
                self.splitter_factory.sync_corner_handles()

        self._splitter_known_ids = current_ids

    def _on_splitter_restored(self, splitter: QSplitter, mode: str) -> None:
        """Called when splitter is restored via double-click (from event handler callback)."""
        _ = splitter
        self._log(f"Splitter per Doppelklick wiederhergestellt ({mode})")

    def _toggle_corner_handles(self) -> None:
        """Toggle corner handles for multi-axis splitter movement.
        
        This is a manual setting that the user can enable/disable via menu.
        """
        self._corner_handles_enabled = not self._corner_handles_enabled

        if self._corner_handles_enabled:
            self.splitter_factory.install_corner_handles(self.dock_manager)
            self._log("✓ Corner Handles enabled - click & drag corners to move 2 splitters simultaneously")
        else:
            self.splitter_factory.clear_corner_handles()
            self._log("✗ Corner Handles disabled")

        self._schedule_splitter_refresh()

    def _curtain_snap(self, side: str) -> None:
        """Animate splitters like curtains with smooth resistance near the end."""
        if self.dock_manager is None:
            return

        self._stop_splitter_animations()
        splitters = self.dock_manager.findChildren(QSplitter)
        for splitter in splitters:
            target_sizes = self._build_curtain_target_sizes(splitter, side)
            if target_sizes is None:
                continue
            self._animate_splitter_sizes(splitter, target_sizes)

        self._log(f"Curtain snap applied: {side}")

    def _build_curtain_target_sizes(self, splitter: Any, side: str) -> list[int] | None:
        """Build target sizes with a small remainder so collapsed panes stay usable (delegated to factory)."""
        return self.splitter_factory.build_curtain_sizes(
            splitter,
            side,
            min_remainder=self._splitter_min_remainder,
            handle_width=self._splitter_handle_width,
        )

    def _animate_splitter_sizes(self, splitter: Any, target_sizes: list[int]) -> None:
        """Animate splitter sizes in steps with ease-out resistance."""
        start_sizes = splitter.sizes()
        if len(start_sizes) != len(target_sizes):
            return

        timer = QTimer(self)
        self._splitter_animation_timers.append(timer)
        state = {"step": 0}

        def animate_step() -> None:
            state["step"] += 1
            progress = state["step"] / self._splitter_animation_steps
            eased = 1 - (1 - progress) ** 3

            interpolated_sizes = [
                max(
                    self._splitter_min_remainder,
                    round(start + ((target - start) * eased)),
                )
                for start, target in zip(start_sizes, target_sizes, strict=False)
            ]

            dominant_index = max(range(len(target_sizes)), key=target_sizes.__getitem__)
            remainder_sum = sum(
                size for index, size in enumerate(interpolated_sizes) if index != dominant_index
            )
            total = sum(start_sizes)
            interpolated_sizes[dominant_index] = max(
                self._splitter_min_remainder,
                total - remainder_sum,
            )

            splitter.setSizes(interpolated_sizes)

            if state["step"] >= self._splitter_animation_steps:
                splitter.setSizes(target_sizes)
                timer.stop()
                if timer in self._splitter_animation_timers:
                    self._splitter_animation_timers.remove(timer)
                timer.deleteLater()

        self._connect_signal(timer.timeout, animate_step)
        timer.start(self._splitter_animation_interval_ms)

    def _stop_splitter_animations(self) -> None:
        """Stop any running splitter animations before a new curtain move starts."""
        while self._splitter_animation_timers:
            timer = self._splitter_animation_timers.pop()
            timer.stop()
            timer.deleteLater()

    def _create_actions_dock(self) -> Any:
        """Create dock panel listing all registered actions."""
        dock = self._create_dock_widget("Actions")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header = QLabel("Registered Actions (from config/actions.json)")
        header.setStyleSheet("font-weight: bold; padding-bottom: 4px;")
        layout.addWidget(header)

        list_widget = QListWidget()
        list_widget.setAlternatingRowColors(True)
        for config in self.action_factory.load_actions():
            label = self.action_factory.get_action_label(config)
            entry = f"{label}  [{config.id}]"
            if config.shortcut:
                entry += f"  ({config.shortcut})"
            list_widget.addItem(entry)
        layout.addWidget(list_widget)

        dock.setWidget(container)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)
        return dock

    def _create_info_dock(self, title: str, info_text: str) -> Any:
        """Create lightweight info dock used to build richer splitter topology."""
        dock = self._create_dock_widget(title)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        label = QLabel(info_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 12px; padding: 6px;")
        layout.addWidget(label)

        dock.setWidget(container)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)
        return dock

    def _create_log_dock(self) -> Any:
        """Create activity log dock panel."""
        dock = self._create_dock_widget("📝 Activity Log @ Bottom")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        header = QLabel("📝 System Activity Log")
        header.setStyleSheet(
            "font-weight: bold; padding: 8px; background-color: #404040; "
            "border-radius: 4px; font-size: 12px;"
        )
        layout.addWidget(header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00;"
            "font-family: Consolas, Monaco, monospace; font-size: 11px;"
        )
        layout.addWidget(self.log_text)
        
        container.setLayout(layout)
        dock.setWidget(container)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)
        return dock

    def _create_casting_toolbar_dock(self) -> Any:
        """Create panel with its own toolbar and dynamic toolbutton casting."""
        dock = self._create_dock_widget("⚙️ Toolbar @ Right")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QLabel("⚙️ Panel Toolbar - Doppelklick: Aktion hinzufügen")
        header.setStyleSheet(
            "font-weight: bold; padding: 8px; background-color: #404040; "
            "border-radius: 4px; font-size: 12px;"
        )
        layout.addWidget(header)
        
        info_label = QLabel("← →  Drag left edge to resize (or use buttons below)")
        info_label.setStyleSheet(
            "color: #ffaa00; font-size: 10px; padding: 4px; "
            "background-color: #3a3a3a; border-radius: 2px;"
        )
        layout.addWidget(info_label)

        panel_toolbar = QToolBar("Panel Toolbar", container)
        panel_toolbar.setMovable(True)
        panel_toolbar.setIconSize(QSize(18, 18))
        panel_toolbar.setAcceptDrops(True)
        panel_toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        panel_toolbar.installEventFilter(self)
        self._connect_signal(
            panel_toolbar.customContextMenuRequested,
            lambda pos, toolbar=panel_toolbar: self._show_panel_toolbar_context_menu(toolbar, pos),
        )

        slide_row = QHBoxLayout()
        slide_row.setContentsMargins(0, 0, 0, 0)
        slide_row.setSpacing(4)

        slide_left_button = QToolButton(container)
        slide_left_button.setText("◀")
        slide_left_button.setAutoRaise(True)
        slide_left_button.setToolTip("Toolbar nach links schieben")
        slide_row.addWidget(slide_left_button)

        toolbar_scroll = QScrollArea(container)
        toolbar_scroll.setWidget(panel_toolbar)
        toolbar_scroll.setWidgetResizable(False)
        toolbar_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        toolbar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        toolbar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        toolbar_scroll.setMinimumHeight(42)
        slide_row.addWidget(toolbar_scroll, 1)

        slide_right_button = QToolButton(container)
        slide_right_button.setText("▶")
        slide_right_button.setAutoRaise(True)
        slide_right_button.setToolTip("Toolbar nach rechts schieben")
        slide_row.addWidget(slide_right_button)

        self._connect_signal(
            slide_left_button.clicked,
            lambda checked=False, scroll_area=toolbar_scroll: self._slide_panel_toolbar(scroll_area, -1),
        )
        self._connect_signal(
            slide_right_button.clicked,
            lambda checked=False, scroll_area=toolbar_scroll: self._slide_panel_toolbar(scroll_area, 1),
        )

        scrollbar = toolbar_scroll.horizontalScrollBar()
        self._connect_signal(
            scrollbar.rangeChanged,
            lambda minimum, maximum, scroll_area=toolbar_scroll, left_button=slide_left_button, right_button=slide_right_button: self._update_panel_toolbar_slide_buttons(
                scroll_area,
                left_button,
                right_button,
            ),
        )

        toolbar_key = id(panel_toolbar)
        self._panel_toolbar_scroll_areas[toolbar_key] = toolbar_scroll
        self._panel_toolbar_slide_buttons[toolbar_key] = (slide_left_button, slide_right_button)
        self._connect_signal(
            scrollbar.valueChanged,
            lambda value, scroll_area=toolbar_scroll, left_button=slide_left_button, right_button=slide_right_button: self._update_panel_toolbar_slide_buttons(
                scroll_area,
                left_button,
                right_button,
            ),
        )

        layout.addLayout(slide_row)

        action_list = QListWidget()
        action_list.setAlternatingRowColors(True)
        for action_id in self.action_registry.list_action_ids():
            action_list.addItem(action_id)
        self._connect_signal(
            action_list.itemDoubleClicked,
            lambda item, toolbar=panel_toolbar, action_widget=action_list: self._add_action_to_panel_toolbar(
                toolbar,
                action_widget,
            ),
        )
        layout.addWidget(action_list)

        add_button = QPushButton("Toolbutton hinzufügen")
        self._connect_signal(
            add_button.clicked,
            lambda checked=False: self._add_action_to_panel_toolbar(panel_toolbar, action_list),
        )
        layout.addWidget(add_button)

        curtain_left_button = QPushButton("Vorhang: nach links")
        self._connect_signal(curtain_left_button.clicked, lambda checked=False: self._curtain_snap("left"))
        layout.addWidget(curtain_left_button)

        curtain_right_button = QPushButton("Vorhang: nach rechts")
        self._connect_signal(curtain_right_button.clicked, lambda checked=False: self._curtain_snap("right"))
        layout.addWidget(curtain_right_button)

        dock.setWidget(container)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)
        self._update_panel_toolbar_slide_buttons(toolbar_scroll, slide_left_button, slide_right_button)
        return dock

    def _add_action_to_panel_toolbar(self, panel_toolbar: QToolBar, action_list: QListWidget) -> None:
        """Add selected registry action as a toolbutton to the panel toolbar."""
        selected = action_list.currentItem()
        if selected is None:  # type: ignore[unreachable]
            self._log("Casting Toolbar: Keine Action ausgewählt")
            return

        action_id = selected.text().strip()
        action = self.action_registry.get_action(action_id)
        if action is None:  # type: ignore[unreachable]
            self._log(f"Casting Toolbar: Action nicht gefunden ({action_id})")
            return

        panel_action = self._create_panel_toolbar_action(panel_toolbar, action_id, action)
        panel_toolbar.addAction(panel_action)
        panel_toolbar.adjustSize()
        self._refresh_panel_toolbar_ui(panel_toolbar)
        self._log(f"Casting Toolbar: Toolbutton hinzugefügt ({action_id})")

    def _slide_panel_toolbar(self, scroll_area: QScrollArea, direction: int) -> None:
        """Slide the panel toolbar horizontally instead of exposing scrollbars."""
        scrollbar = scroll_area.horizontalScrollBar()
        maximum = scrollbar.maximum()
        if maximum <= 0:
            return

        page_step = max(scroll_area.viewport().width() - 40, 80)
        target_value = scrollbar.value() + (page_step * direction)
        target_value = max(0, min(maximum, target_value))

        animation = QPropertyAnimation(scrollbar, b"value", self)
        animation.setDuration(180)
        animation.setStartValue(scrollbar.value())
        animation.setEndValue(target_value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def cleanup() -> None:
            if animation in self._toolbar_slide_animations:
                self._toolbar_slide_animations.remove(animation)
            animation.deleteLater()

        self._toolbar_slide_animations.append(animation)
        self._connect_signal(animation.finished, cleanup)
        animation.start()

    def _update_panel_toolbar_slide_buttons(
        self,
        scroll_area: QScrollArea,
        left_button: QToolButton,
        right_button: QToolButton,
    ) -> None:
        """Enable slide buttons only when hidden toolbar actions exist off-screen."""
        scrollbar = scroll_area.horizontalScrollBar()
        maximum = scrollbar.maximum()
        has_overflow = maximum > 0
        left_button.setVisible(has_overflow)
        right_button.setVisible(has_overflow)
        left_button.setEnabled(has_overflow and scrollbar.value() > 0)
        right_button.setEnabled(has_overflow and scrollbar.value() < maximum)

    def _refresh_panel_toolbar_ui(self, panel_toolbar: QToolBar) -> None:
        """Refresh toolbar size and slide button state after structural changes."""
        panel_toolbar.adjustSize()
        toolbar_key = id(panel_toolbar)
        scroll_area = self._panel_toolbar_scroll_areas.get(toolbar_key)
        buttons = self._panel_toolbar_slide_buttons.get(toolbar_key)
        if scroll_area is not None and buttons is not None:
            self._update_panel_toolbar_slide_buttons(scroll_area, buttons[0], buttons[1])

    def eventFilter(self, watched: Any, event: Any) -> bool:
        """Handle drag-and-drop switching for panel toolbar actions and separators.
        
        Note: Splitter handle double-click is now delegated to SplitterEventHandler.
        """
        event_type = event.type()

        if watched is self.dock_manager or isinstance(watched, QSplitter):
            if event_type in {
                QEvent.Type.Resize,
                QEvent.Type.Move,
                QEvent.Type.Show,
                QEvent.Type.LayoutRequest,
            }:
                if self._corner_handles_enabled and not self.splitter_factory.is_corner_drag_active():
                    self._schedule_splitter_refresh(16)

        if isinstance(watched, QToolBar):
            if event_type == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self._toolbar_drag_start_pos[id(watched)] = event.pos()
                action = watched.actionAt(event.pos())
                if action is not None:
                    self._toolbar_drag_action[id(watched)] = action

            elif event_type == QEvent.Type.MouseMove and event.buttons() & Qt.MouseButton.LeftButton:
                drag_action = self._toolbar_drag_action.get(id(watched))
                start_pos = self._toolbar_drag_start_pos.get(id(watched))
                if (
                    drag_action is not None
                    and start_pos is not None
                    and (event.pos() - start_pos).manhattanLength() >= QApplication.startDragDistance()
                ):
                    self._start_toolbar_action_drag(watched, drag_action)
                    return True

            elif event_type in {QEvent.Type.DragEnter, QEvent.Type.DragMove}:
                if event.source() is watched:
                    event.acceptProposedAction()
                    return True

            elif event_type == QEvent.Type.Drop:
                if event.source() is watched:
                    self._apply_toolbar_drop_switch(watched, event.pos())
                    event.acceptProposedAction()
                    return True

            elif event_type == QEvent.Type.MouseButtonRelease:
                self._toolbar_drag_start_pos.pop(id(watched), None)
                self._toolbar_drag_action.pop(id(watched), None)

        return super().eventFilter(watched, event)

    def _start_toolbar_action_drag(self, toolbar: QToolBar, action: QAction) -> None:
        """Start drag operation for a toolbar action or separator."""
        self._toolbar_drag_action[id(toolbar)] = action
        drag = QDrag(toolbar)
        mime_data = QMimeData()
        mime_data.setText("panel_toolbar_action")
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)

    def _apply_toolbar_drop_switch(self, toolbar: QToolBar, drop_pos: Any) -> None:
        """Switch positions of dragged and target actions, including separators."""
        dragged_action = self._toolbar_drag_action.get(id(toolbar))
        if dragged_action is None:
            return

        actions = list(toolbar.actions())
        if dragged_action not in actions:
            return
        
        # dragged_action is guaranteed to be in actions from here

        target_action = toolbar.actionAt(drop_pos)
        if target_action is None:
            actions.remove(dragged_action)
            actions.append(dragged_action)
        elif target_action is not dragged_action and target_action in actions:
            dragged_index = actions.index(dragged_action)
            target_index = actions.index(target_action)
            actions[dragged_index], actions[target_index] = actions[target_index], actions[dragged_index]
        else:
            return

        toolbar.clear()
        for reordered_action in actions:
            toolbar.addAction(reordered_action)
        self._refresh_panel_toolbar_ui(toolbar)
        self._refresh_panel_toolbar_ui(toolbar)

    def _create_panel_toolbar_action(
        self,
        panel_toolbar: QToolBar,
        action_id: str,
        source_action: QAction,
        source_kind: str = "registry",
    ) -> QAction:
        """Create editable proxy action for a panel-local toolbar button."""
        object_id = self._next_panel_toolbar_object_id()
        panel_action = QAction(source_action.icon(), source_action.text(), panel_toolbar)
        panel_action.setEnabled(source_action.isEnabled())
        panel_action.setCheckable(source_action.isCheckable())
        panel_action.setChecked(source_action.isChecked())
        panel_action.setStatusTip(source_action.statusTip())
        panel_action.setToolTip(source_action.toolTip())
        panel_action.setData(
            {
                "object_id": object_id,
                "source_action_kind": source_kind,
                "source_action_id": action_id,
                "default_text": source_action.text(),
                "default_icon": source_action.icon(),
                "icon_source": "default",
            }
        )
        self._connect_signal(
            panel_action.triggered,
            lambda checked=False, proxy_action=panel_action: self._trigger_panel_toolbar_proxy_action(
                proxy_action,
            ),
        )
        return panel_action

    def _next_panel_toolbar_object_id(self) -> str:
        """Create a new unique ID for a panel-local toolbar object."""
        self._panel_toolbar_object_counter += 1
        return f"panel_toolbar_object_{self._panel_toolbar_object_counter}"

    def _trigger_panel_toolbar_proxy_action(self, proxy_action: QAction) -> None:
        """Trigger the currently selected source action for a panel-local proxy action."""
        data = proxy_action.data()
        if not isinstance(data, dict):
            return

        source_kind = data.get("source_action_kind", "registry")
        source_action_id = data.get("source_action_id", "")
        if not isinstance(source_action_id, str) or not source_action_id:
            return

        source_action = self._resolve_source_action(source_kind, source_action_id)
        if source_action is None:
            self._log(f"Casting Toolbar: Quellaktion fehlt ({source_kind} :: {source_action_id})")
            return

        source_action.trigger()

    def _show_panel_toolbar_context_menu(self, panel_toolbar: QToolBar, pos: Any) -> None:
        """Show edit menu for a panel-local toolbar button on right click."""
        action = panel_toolbar.actionAt(pos)
        menu = QMenu(panel_toolbar)

        if action is None:
            clear_action = menu.addAction("Alle Toolbuttons entfernen")
            chosen = menu.exec(panel_toolbar.mapToGlobal(pos))
            if chosen == clear_action:
                panel_toolbar.clear()
                self._log("Casting Toolbar: Alle Toolbuttons entfernt")
            return
        
        # action is guaranteed not None from here

        edit_action = menu.addAction("Aktion bearbeiten")
        reset_action = menu.addAction("Aktion zurücksetzen")
        menu.addSeparator()
        remove_action = menu.addAction("Toolbutton entfernen")

        chosen = menu.exec(panel_toolbar.mapToGlobal(pos))
        if chosen == edit_action:
            self._edit_panel_toolbar_action(action)
        elif chosen == reset_action:
            self._reset_panel_toolbar_action(action)
            self._reset_panel_toolbar_icon(action)
        elif chosen == remove_action:
            panel_toolbar.removeAction(action)
            action.deleteLater()
            self._log("Casting Toolbar: Toolbutton entfernt")

    def _edit_panel_toolbar_action(self, action: QAction) -> None:
        """Edit label and icon for a panel-local toolbar button in one modal."""
        options = self._get_icon_picker_options()
        binding_options = self._get_action_binding_options()
        action_data = action.data() if isinstance(action.data(), dict) else {}
        panel_toolbar = self._get_panel_toolbar_from_action(action)
        dialog = QDialog(self)
        dialog.setWindowTitle("Aktion bearbeiten")
        dialog.setModal(True)
        dialog.resize(460, 640)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        intro_label = QLabel(
            "Panel-Objekt = eigener Toolbar-Button.\n"
            "Action-Bindung = welche Aktion beim Klick ausgeführt wird.\n"
            "Registry referenziert vorhandene Aktionen, Custom erzeugt neue Laufzeit-Aktionen mit ID."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("color: #b0b0b0; font-size: 11px; padding-bottom: 4px;")
        layout.addWidget(intro_label)

        object_id_label = QLabel("Panel-Objekt-ID")
        layout.addWidget(object_id_label)

        object_id_value = QLineEdit(str(action_data.get("object_id", "panel_toolbar_object_unknown")))
        object_id_value.setReadOnly(True)
        layout.addWidget(object_id_value)

        name_label = QLabel("Beschriftung")
        layout.addWidget(name_label)

        text_input = QLineEdit(action.text() or "")
        layout.addWidget(text_input)

        separator_label = QLabel("Separator-Anordnung")
        layout.addWidget(separator_label)

        separator_mode_combo = QComboBox()
        separator_mode_combo.addItem("Kein Separator", "none")
        separator_mode_combo.addItem("Separator links", "left")
        separator_mode_combo.addItem("Separator rechts", "right")
        separator_mode_combo.addItem("Separator links + rechts", "both")
        current_separator_mode = action_data.get("separator_mode", "none")
        separator_index = separator_mode_combo.findData(current_separator_mode)
        separator_mode_combo.setCurrentIndex(max(separator_index, 0))
        layout.addWidget(separator_mode_combo)

        icon_size_label = QLabel("Toolbar Pixelgröße (Icon)")
        layout.addWidget(icon_size_label)

        toolbar_size_spin = QSpinBox()
        toolbar_size_spin.setRange(14, 64)
        current_icon_size = panel_toolbar.iconSize().width() if panel_toolbar is not None else 18
        toolbar_size_spin.setValue(current_icon_size if current_icon_size > 0 else 18)
        toolbar_size_spin.setSuffix(" px")
        layout.addWidget(toolbar_size_spin)

        binding_label = QLabel("Auszuführende Action")
        layout.addWidget(binding_label)

        binding_hint = QLabel("Filterbar, kompakt und per Slide/Page steuerbar.")
        binding_hint.setStyleSheet("color: #909090; font-size: 11px;")
        layout.addWidget(binding_hint)

        binding_filter = QLineEdit()
        binding_filter.setPlaceholderText("Action suchen...")
        layout.addWidget(binding_filter)

        binding_list = QListWidget()
        binding_list.setUniformItemSizes(True)
        binding_list.setIconSize(QSize(16, 16))
        binding_list.setMaximumHeight(170)
        binding_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        current_binding = self._get_current_action_binding_label(action, binding_options)
        self._populate_binding_list(binding_list, binding_options, current_binding, "")
        layout.addWidget(binding_list, 1)

        binding_nav = QHBoxLayout()
        binding_up_button = QToolButton(dialog)
        binding_up_button.setText("▲")
        binding_up_button.setToolTip("Action-Liste nach oben sliden")
        self._connect_signal(
            binding_up_button.clicked,
            lambda checked=False, list_widget=binding_list: self._slide_list_widget(list_widget, -1),
        )
        binding_nav.addWidget(binding_up_button)
        binding_down_button = QToolButton(dialog)
        binding_down_button.setText("▼")
        binding_down_button.setToolTip("Action-Liste nach unten sliden")
        self._connect_signal(
            binding_down_button.clicked,
            lambda checked=False, list_widget=binding_list: self._slide_list_widget(list_widget, 1),
        )
        binding_nav.addWidget(binding_down_button)
        binding_nav.addStretch()
        layout.addLayout(binding_nav)

        self._connect_signal(
            binding_filter.textChanged,
            lambda text, list_widget=binding_list, options_list=binding_options, current=current_binding: self._populate_binding_list(
                list_widget,
                options_list,
                current,
                text,
            ),
        )

        create_custom_button = QPushButton("Custom Action anlegen")
        self._connect_signal(
            create_custom_button.clicked,
            lambda checked=False, action_list=binding_list: self._open_custom_action_editor(action_list),
        )
        layout.addWidget(create_custom_button)

        icon_label = QLabel("Icon")
        layout.addWidget(icon_label)

        icon_hint = QLabel("Projekt-, System- und Ursprungsicon in kompakter, scrollbarer Liste.")
        icon_hint.setStyleSheet("color: #909090; font-size: 11px;")
        layout.addWidget(icon_hint)

        icon_filter = QLineEdit()
        icon_filter.setPlaceholderText("Icon suchen...")
        layout.addWidget(icon_filter)

        icon_list = QListWidget()
        icon_list.setUniformItemSizes(True)
        icon_list.setIconSize(QSize(16, 16))
        icon_list.setMaximumHeight(190)
        icon_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        current_option = self._get_current_icon_option_label(action, options)
        self._populate_icon_list(icon_list, options, current_option, action)
        layout.addWidget(icon_list, 1)

        icon_nav = QHBoxLayout()
        icon_up_button = QToolButton(dialog)
        icon_up_button.setText("▲")
        icon_up_button.setToolTip("Icon-Liste nach oben sliden")
        self._connect_signal(
            icon_up_button.clicked,
            lambda checked=False, list_widget=icon_list: self._slide_list_widget(list_widget, -1),
        )
        icon_nav.addWidget(icon_up_button)
        icon_down_button = QToolButton(dialog)
        icon_down_button.setText("▼")
        icon_down_button.setToolTip("Icon-Liste nach unten sliden")
        self._connect_signal(
            icon_down_button.clicked,
            lambda checked=False, list_widget=icon_list: self._slide_list_widget(list_widget, 1),
        )
        icon_nav.addWidget(icon_down_button)
        icon_nav.addStretch()
        layout.addLayout(icon_nav)

        self._connect_signal(
            icon_filter.textChanged,
            lambda text, list_widget=icon_list, options_list=options, current=current_option, proxy_action=action: self._populate_icon_list(
                list_widget,
                options_list,
                current,
                proxy_action,
                text,
            ),
        )

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        self._connect_signal(button_box.accepted, dialog.accept)
        self._connect_signal(button_box.rejected, dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_text = text_input.text().strip() or (action.text() or "Toolbutton")
        selected_binding_item = binding_list.currentItem()
        selected_binding = (
            selected_binding_item.text() if selected_binding_item is not None else binding_options[0]
        )
        selected_item = icon_list.currentItem()
        selected_option = selected_item.text() if selected_item is not None else options[0]

        resolved_source_action = self._resolve_binding_option_action(selected_binding)
        binding_kind, binding_action_id = self._parse_binding_option(selected_binding)
        if resolved_source_action is not None and binding_action_id:
            data = action.data()
            if isinstance(data, dict):
                data["source_action_kind"] = binding_kind
                data["source_action_id"] = binding_action_id
                data["default_text"] = resolved_source_action.text()
                data["default_icon"] = resolved_source_action.icon()
                action.setData(data)

        action.setText(new_text)
        action.setToolTip(new_text)

        selected_separator_mode = separator_mode_combo.currentData()
        if isinstance(selected_separator_mode, str) and panel_toolbar is not None:
            self._apply_action_separator_mode(panel_toolbar, action, selected_separator_mode)

        if panel_toolbar is not None:
            toolbar_size_px = toolbar_size_spin.value()
            panel_toolbar.setIconSize(QSize(toolbar_size_px, toolbar_size_px))
            self._refresh_panel_toolbar_ui(panel_toolbar)

        if selected_option == "Standard :: Ursprungsicon":
            self._reset_panel_toolbar_icon(action)
        else:
            icon = self._resolve_picker_icon(selected_option)
            if not icon.isNull():
                action.setIcon(icon)
                data = action.data()
                if isinstance(data, dict):
                    data["icon_source"] = selected_option
                    action.setData(data)

        self._log(f"Casting Toolbar: Aktion bearbeitet ({new_text})")

    def _get_panel_toolbar_from_action(self, action: QAction) -> QToolBar | None:
        """Resolve the owning panel toolbar for an action."""
        parent = action.parent()
        return parent if isinstance(parent, QToolBar) else None

    def _apply_action_separator_mode(
        self,
        panel_toolbar: QToolBar,
        action: QAction,
        separator_mode: str,
    ) -> None:
        """Apply separator placement around a toolbar action (left/right/both/none)."""
        data = action.data()
        if not isinstance(data, dict):
            return
        object_id = data.get("object_id")
        if not isinstance(object_id, str) or not object_id:
            return

        self._remove_owned_separators(panel_toolbar, object_id)
        if separator_mode in {"left", "both"}:
            left_separator = panel_toolbar.insertSeparator(action)
            left_separator.setData({"separator_owner": object_id, "separator_side": "left"})

        if separator_mode in {"right", "both"}:
            actions = panel_toolbar.actions()
            try:
                current_index = actions.index(action)
            except ValueError:
                current_index = -1

            next_action = actions[current_index + 1] if current_index >= 0 and current_index + 1 < len(actions) else None
            if next_action is None:
                right_separator = panel_toolbar.addSeparator()
            else:
                right_separator = panel_toolbar.insertSeparator(next_action)
            right_separator.setData({"separator_owner": object_id, "separator_side": "right"})

        data["separator_mode"] = separator_mode
        action.setData(data)
        self._refresh_panel_toolbar_ui(panel_toolbar)

    def _remove_owned_separators(self, panel_toolbar: QToolBar, object_id: str) -> None:
        """Remove separators that belong to one toolbar object ID."""
        for toolbar_action in list(panel_toolbar.actions()):
            if not toolbar_action.isSeparator():
                continue
            separator_data = toolbar_action.data()
            if isinstance(separator_data, dict) and separator_data.get("separator_owner") == object_id:
                panel_toolbar.removeAction(toolbar_action)

    def _populate_binding_list(
        self,
        binding_list: QListWidget,
        options: list[str],
        current_option: str,
        filter_text: str,
    ) -> None:
        """Populate the action binding list with consistent icon previews and filtering."""
        binding_list.clear()
        filtered_options = self._filter_selector_options(options, filter_text)
        current_row = 0
        for index, option in enumerate(filtered_options):
            binding_item = QListWidgetItem(option)
            binding_item.setIcon(self._get_binding_option_icon(option))
            binding_list.addItem(binding_item)
            if option == current_option:
                current_row = index

        if binding_list.count() > 0:
            binding_list.setCurrentRow(current_row)

    def _populate_icon_list(
        self,
        icon_list: QListWidget,
        options: list[str],
        current_option: str,
        proxy_action: QAction,
        filter_text: str = "",
    ) -> None:
        """Populate the icon selector list with consistent previews and filtering."""
        icon_list.clear()
        filtered_options = self._filter_selector_options(options, filter_text)
        current_row = 0
        for index, option in enumerate(filtered_options):
            item = QListWidgetItem(option)
            item.setIcon(self._get_icon_option_preview(option, proxy_action))
            icon_list.addItem(item)
            if option == current_option:
                current_row = index

        if icon_list.count() > 0:
            icon_list.setCurrentRow(current_row)

    def _filter_selector_options(self, options: list[str], filter_text: str) -> list[str]:
        """Filter selector options case-insensitively for compact modals."""
        normalized = filter_text.strip().lower()
        if not normalized:
            return options
        return [option for option in options if normalized in option.lower()]

    def _slide_list_widget(self, list_widget: QListWidget, direction: int) -> None:
        """Slide a list vertically by roughly one page without changing modal size."""
        scrollbar = list_widget.verticalScrollBar()
        page_step = max(scrollbar.pageStep() - 20, 40)
        target_value = scrollbar.value() + (page_step * direction)
        scrollbar.setValue(max(scrollbar.minimum(), min(scrollbar.maximum(), target_value)))

    def _get_binding_option_icon(self, option: str) -> QIcon:
        """Return a consistent icon preview for an action binding option."""
        resolved_action = self._resolve_binding_option_action(option)
        if resolved_action is not None and not resolved_action.icon().isNull():
            return resolved_action.icon()

        style = QApplication.style()
        if style is None:
            return QIcon()

        source_kind, source_action_id = self._parse_binding_option(option)
        if source_kind == "custom":
            return style.standardIcon(QStyle.StandardPixmap.SP_CommandLink)

        config = self.action_factory.get_action_config(source_action_id)
        if config is not None and config.icon:
            registry_action = self.action_registry.get_action(source_action_id)
            if registry_action is not None and not registry_action.icon().isNull():
                return registry_action.icon()

        # Fallback if icon not found
        return style.standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView)

    def _get_icon_option_preview(self, option: str, proxy_action: QAction) -> QIcon:
        """Return a consistent icon preview for icon picker options."""
        if option == "Standard :: Ursprungsicon":
            data = proxy_action.data()
            if isinstance(data, dict):
                default_icon = data.get("default_icon")
                if isinstance(default_icon, QIcon) and not default_icon.isNull():
                    return default_icon
            return proxy_action.icon() if not proxy_action.icon().isNull() else self._fallback_preview_icon()

        resolved_icon = self._resolve_picker_icon(option)
        if not resolved_icon.isNull():
            return resolved_icon
        return self._fallback_preview_icon()

    def _fallback_preview_icon(self) -> QIcon:
        """Return a stable fallback preview icon when no source icon exists."""
        style = QApplication.style()
        if style is None:
            return QIcon()
        # Fallback icon
        return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def _open_custom_action_editor(self, binding_list: QListWidget) -> None:
        """Create a custom action at runtime and append it to the binding selector."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Custom Action anlegen")
        dialog.setModal(True)
        dialog.resize(420, 220)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        intro_label = QLabel(
            "Hier wird eine vollständig neue Runtime-Action mit eigener ID angelegt.\n"
            "Diese ID ist die technische Referenz für Binding, Registry-Erweiterung und spätere Wiederverwendung."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("color: #b0b0b0; font-size: 11px; padding-bottom: 4px;")
        layout.addWidget(intro_label)

        id_label = QLabel("Action-ID")
        layout.addWidget(id_label)
        action_id_input = QLineEdit("custom.")
        action_id_input.setPlaceholderText("z. B. custom.export_pdf")
        layout.addWidget(action_id_input)

        label_label = QLabel("Beschriftung")
        layout.addWidget(label_label)
        label_input = QLineEdit()
        layout.addWidget(label_input)

        message_label = QLabel("Ausführungsnachricht")
        layout.addWidget(message_label)
        message_input = QLineEdit()
        layout.addWidget(message_input)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        self._connect_signal(button_box.accepted, dialog.accept)
        self._connect_signal(button_box.rejected, dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        action_id = action_id_input.text().strip()
        label = label_input.text().strip()
        message = message_input.text().strip()
        if not action_id or not label:
            self._log("Custom Action: ID und Beschriftung sind erforderlich")
            return

        self._register_custom_action(action_id, label, message)
        option = f"Custom :: {action_id}"
        if not binding_list.findItems(option, Qt.MatchFlag.MatchExactly):
            binding_list.addItem(option)
        matching_items = binding_list.findItems(option, Qt.MatchFlag.MatchExactly)
        if matching_items:
            binding_list.setCurrentItem(matching_items[0])

    def _register_custom_action(self, action_id: str, label: str, message: str) -> QAction:
        """Register a runtime custom action independent from actions.json."""
        custom_action = self._custom_actions.get(action_id)
        if custom_action is None:
            custom_action = QAction(self)
            self._custom_actions[action_id] = custom_action
            self._connect_signal(
                custom_action.triggered,
                lambda checked=False, custom_id=action_id: self._trigger_custom_action(custom_id),
            )

        custom_action.setText(label)
        custom_action.setToolTip(message or label)
        custom_action.setStatusTip(message or label)
        custom_action.setEnabled(True)
        self._custom_action_definitions[action_id] = CustomActionDefinition(
            id=action_id,
            name=label,
            label=label,
            message=message or f"Custom Action ausgeführt: {label}",
        )
        self._save_custom_actions()
        self._log(f"Custom Action registriert ({action_id})")
        return custom_action

    def _trigger_custom_action(self, action_id: str) -> None:
        """Execute a runtime custom action."""
        custom_definition = self._custom_action_definitions.get(action_id)
        message = (
            custom_definition.message
            if custom_definition is not None
            else f"Custom Action ausgeführt: {action_id}"
        )
        self._log(message)

    def _load_custom_actions(self) -> None:
        """Load persisted custom actions from config/custom_actions.json."""
        if not self.custom_actions_config_path.exists():
            return

        try:
            raw_data = json.loads(self.custom_actions_config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            self._log(f"Custom Actions konnten nicht geladen werden: {error}")
            return

        custom_actions_data = raw_data.get("custom_actions", [])
        if not isinstance(custom_actions_data, list):
            return

        for item in custom_actions_data:
            if not isinstance(item, dict):
                continue

            action_id = item.get("id")
            label = item.get("label") or item.get("name")
            message = item.get("message")
            if not isinstance(action_id, str) or not action_id:
                continue
            if not isinstance(label, str) or not label:
                continue
            if not isinstance(message, str):
                message = f"Custom Action ausgeführt: {label}"

            self._register_custom_action(action_id, label, message)

    def _save_custom_actions(self) -> None:
        """Persist custom actions to config/custom_actions.json."""
        payload = {
            "custom_actions": [
                asdict(definition)
                for _, definition in sorted(self._custom_action_definitions.items())
            ]
        }

        try:
            self.custom_actions_config_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError as error:
            self._log(f"Custom Actions konnten nicht gespeichert werden: {error}")

    def _get_action_binding_options(self) -> list[str]:
        """Return all registry and runtime custom actions for modal binding selection."""
        registry_options = [f"Registry :: {action_id}" for action_id in self.action_registry.list_action_ids()]
        custom_options = [f"Custom :: {action_id}" for action_id in sorted(self._custom_actions)]
        return [*registry_options, *custom_options]

    def _parse_binding_option(self, option: str) -> tuple[str, str]:
        """Parse a binding option label into source kind and source id."""
        if option.startswith("Custom :: "):
            return ("custom", option.split("::", maxsplit=1)[1].strip())
        return ("registry", option.split("::", maxsplit=1)[1].strip())

    def _resolve_binding_option_action(self, option: str) -> QAction | None:
        """Resolve a modal binding option label to its QAction instance."""
        source_kind, source_action_id = self._parse_binding_option(option)
        return self._resolve_source_action(source_kind, source_action_id)

    def _resolve_source_action(self, source_kind: Any, source_action_id: str) -> QAction | None:
        """Resolve a source action from registry or runtime custom actions."""
        if source_kind == "custom":
            return self._custom_actions.get(source_action_id)
        return self.action_registry.get_action(source_action_id)

    def _get_current_action_binding_label(self, action: QAction, options: list[str]) -> str:
        """Get the current action binding label for the edit modal."""
        data = action.data()
        if isinstance(data, dict):
            source_kind = data.get("source_action_kind", "registry")
            source_action_id = data.get("source_action_id", "")
            if isinstance(source_action_id, str) and source_action_id:
                option = f"{'Custom' if source_kind == 'custom' else 'Registry'} :: {source_action_id}"
                if option in options:
                    return option
        return options[0] if options else ""

    def _reset_panel_toolbar_action(self, action: QAction) -> None:
        """Reset a panel-local toolbar button label to its source action text."""
        data = action.data()
        if not isinstance(data, dict):
            return
        default_text = data.get("default_text")
        if isinstance(default_text, str) and default_text:
            action.setText(default_text)
            action.setToolTip(default_text)
            self._log(f"Casting Toolbar: Toolbutton zurückgesetzt ({default_text})")

    def _reset_panel_toolbar_icon(self, action: QAction) -> None:
        """Reset panel-local toolbar icon to the original action icon."""
        data = action.data()
        if not isinstance(data, dict):
            return
        default_icon = data.get("default_icon")
        if isinstance(default_icon, QIcon):
            action.setIcon(default_icon)
            data["icon_source"] = "default"
            action.setData(data)
            self._log("Casting Toolbar: Icon zurückgesetzt")

    def _get_icon_picker_options(self) -> list[str]:
        """Return all selectable icon options from project and system sources."""
        project_icons = [f"Projekt :: {name}" for name in self._list_project_icon_names()]
        system_icons = [f"System :: {name}" for name in self._list_system_icon_names()]
        return ["Standard :: Ursprungsicon", *project_icons, *system_icons]

    def _list_project_icon_names(self) -> list[str]:
        """List available project icon base names from themes/icons."""
        icons_path = WORKSPACE_ROOT / "themes" / "icons"
        if not icons_path.exists():
            return []
        names = {path.stem for path in icons_path.iterdir() if path.suffix.lower() in {".svg", ".png"}}
        return sorted(names)

    def _list_system_icon_names(self) -> list[str]:
        """List all available Qt standard pixmap names for the current style."""
        try:
            return sorted(item.name for item in QStyle.StandardPixmap)
        except TypeError:
            return sorted(STANDARD_ICONS)

    def _resolve_picker_icon(self, option: str) -> QIcon:
        """Resolve an icon picker option to an actual QIcon."""
        if option == "Standard :: Ursprungsicon":
            return QIcon()

        if option.startswith("Projekt :: "):
            icon_name = option.split("::", maxsplit=1)[1].strip()
            for suffix in (".svg", ".png"):
                path = WORKSPACE_ROOT / "themes" / "icons" / f"{icon_name}{suffix}"
                if path.exists():
                    return QIcon(str(path))
            return QIcon()

        if option.startswith("System :: "):
            pixmap_name = option.split("::", maxsplit=1)[1].strip()
            style = QApplication.style()
            if style and hasattr(QStyle.StandardPixmap, pixmap_name):
                pixmap = getattr(QStyle.StandardPixmap, pixmap_name)
                return style.standardIcon(pixmap)

        return QIcon()

    def _get_current_icon_option_label(self, action: QAction, options: list[str]) -> str:
        """Get the currently selected icon option label for a panel toolbar action."""
        data = action.data()
        if isinstance(data, dict):
            icon_source = data.get("icon_source")
            if isinstance(icon_source, str) and icon_source in options:
                return icon_source
        return options[0]

    def _add_registry_action(self, menu: QMenu, action_id: str) -> None:
        """Add an action from the registry to a menu if available."""
        action = self.action_registry.get_action(action_id)
        if action is not None:
            menu.addAction(action)

    def _get_action_id_by_name(self, action_name: str) -> str | None:
        """Resolve action ID from action name defined in actions.json."""
        for config in self.action_factory.load_actions():
            if config.action == action_name:
                return config.id
        return None

    def _create_menu_bar(self) -> None:
        """Create menu bar from ActionFactory categories and shared actions."""
        menubar = self.menuBar()

        category_menus: list[tuple[str, str]] = [
            ("file", "&File"),
            ("edit", "&Edit"),
            ("dock", "&View"),
            ("view", "&View"),
            ("tools", "&Tools"),
        ]

        actions_by_category: dict[str, list[Any]] = {key: [] for key, _ in category_menus}
        for config in self.action_factory.load_actions():
            if config.category in actions_by_category:
                actions_by_category[config.category].append(config)

        created_menus: dict[str, QMenu] = {}
        for category, title in category_menus:
            if not actions_by_category.get(category):
                continue
            menu = created_menus.get(title)
            if menu is None:
                menu = menubar.addMenu(title)
                created_menus[title] = menu

            for action_config in actions_by_category[category]:
                self._add_registry_action(menu, action_config.id)

            if category == "file":
                menu.addSeparator()
                exit_action = QAction("E&xit", self)
                exit_action.setShortcut(QKeySequence.StandardKey.Quit)
                exit_action.setStatusTip("Exit the application")
                self._connect_signal(exit_action.triggered, self.close)
                menu.addAction(exit_action)

        # Splitter options menu
        self._create_splitter_menu()

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.setStatusTip("About this demo")
        self._connect_signal(about_action.triggered, self._show_about)
        help_menu.addAction(about_action)

    def _create_splitter_menu(self) -> None:
        """Add Splitter options to menu bar."""
        menubar = self.menuBar()
        splitter_menu = menubar.addMenu("&Splitter")

        # Corner Handles option
        corner_handles_action = QAction("&Corner Handles", self)
        corner_handles_action.setCheckable(True)
        corner_handles_action.setChecked(self._corner_handles_enabled)
        corner_handles_action.setStatusTip("Enable/Disable simultaneous multi-axis splitter movement")
        self._connect_signal(
            corner_handles_action.triggered,
            self._toggle_corner_handles,
        )
        splitter_menu.addAction(corner_handles_action)

    def _create_toolbar(self) -> None:
        """Create configured toolbars via ToolbarFactory."""
        self.toolbar_factory.register_menu_creator("layouts_menu", self._create_layouts_menu)
        self.toolbar_factory.register_menu_creator("themes_menu", self._create_themes_menu)

        self.toolbars = self.toolbar_factory.create_all_toolbars(
            action_registry=self.action_registry,
            parent=self,
        )

        if not self.toolbars:
            toolbar = QToolBar("Main Toolbar")
            toolbar.setMovable(False)
            toolbar.setIconSize(QSize(20, 20))
            self.addToolBar(toolbar)
            self._add_toolbar_action(toolbar, "action_save_layout")
            self._add_toolbar_action(toolbar, "action_load_layout")
            self._add_toolbar_action(toolbar, "action_refresh")

    def _create_layouts_menu(self) -> QMenu:
        """Create layouts menu from LayoutFactory definitions."""
        menu = QMenu("Layouts", self)
        layouts = self.layout_factory.list_layouts()

        for layout in layouts:
            action = QAction(self.layout_factory.get_layout_name(layout), self)
            action.setStatusTip(str(layout.file_path))
            self._connect_signal(
                action.triggered,
                lambda checked=False, layout_def=layout: self._apply_layout(layout_def),
            )
            menu.addAction(action)

        self.layouts_menu = menu
        return menu

    def _create_themes_menu(self) -> QMenu:
        """Create themes menu from ThemeFactory definitions."""
        menu = QMenu("Themes", self)
        themes = self.theme_factory.list_themes()

        for theme in themes:
            action = QAction(self.theme_factory.get_theme_name(theme), self)
            action.setStatusTip(str(theme.file_path))
            self._connect_signal(action.triggered, lambda checked=False, t=theme: self._apply_theme(t))
            menu.addAction(action)

        self.themes_menu = menu
        return menu

    def _apply_layout(self, layout: LayoutDefinition) -> None:
        """Apply layout selection (demo integration)."""
        exists = layout.file_path.exists()
        status = "found" if exists else "missing"
        self._log(f"Apply Layout: {layout.layout_id} ({status})")
        self.status_bar.showMessage(f"Layout selected: {layout.name} ({status})", 4000)

    def _apply_theme(self, theme: ThemeDefinition) -> None:
        """Apply theme stylesheet from theme definition."""
        if not theme.file_path.exists():
            self._log(f"Theme file missing: {theme.file_path}")
            self.status_bar.showMessage(f"Theme file missing: {theme.name}", 4000)
            return

        try:
            stylesheet = theme.file_path.read_text(encoding="utf-8")
            app = QApplication.instance()
            if app is not None:
                cast("QApplication", app).setStyleSheet(stylesheet)
            self._log(f"Theme applied: {theme.theme_id}")
            self.status_bar.showMessage(f"Theme applied: {theme.name}", 4000)
        except OSError as error:
            self._log(f"Theme apply failed: {error}")
            self.status_bar.showMessage(f"Theme apply failed: {theme.name}", 4000)

    def _add_toolbar_action(self, toolbar: QToolBar, action_id: str) -> None:
        """Add action to toolbar without changing shared menu action labels."""
        action = self.action_registry.get_action(action_id)
        if action:
            if action.icon().isNull():
                config = self.action_factory.get_action_config(action_id)
                if config:
                    fallback = self.action_registry.get_icon_fallback(config.icon)
                    if fallback:
                        toolbar_action = QAction(fallback, self)
                        toolbar_action.setEnabled(action.isEnabled())
                        self._connect_signal(toolbar_action.triggered, action.trigger)
                        toolbar.addAction(toolbar_action)
                        return

            toolbar.addAction(action)

    def _create_status_bar(self) -> None:
        """Create hidden status bar (no hint elements visible)."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.hide()

    def _setup_context_menu(self) -> None:
        """Enable context menu on the central widget."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._connect_signal(self.customContextMenuRequested, self._show_context_menu)

    def _show_context_menu(self, pos: Any) -> None:
        """Show context menu with registry actions."""
        menu = QMenu(self)

        # Quick actions submenu
        quick_menu = menu.addMenu("Quick Actions")
        save_action = self.action_registry.get_action("action_save_layout")
        load_action = self.action_registry.get_action("action_load_layout")
        refresh_action = self.action_registry.get_action("action_refresh")
        if save_action:
            quick_menu.addAction(save_action)
        if load_action:
            quick_menu.addAction(load_action)
        if refresh_action:
            quick_menu.addAction(refresh_action)

        # View submenu
        view_menu = menu.addMenu("View")
        float_action = self.action_registry.get_action("action_float_all")
        dock_action = self.action_registry.get_action("action_dock_all")
        if float_action:
            view_menu.addAction(float_action)
        if dock_action:
            view_menu.addAction(dock_action)

        menu.addSeparator()

        # Tools submenu
        tools_menu = menu.addMenu("Tools")
        theme_action = self.action_registry.get_action("action_show_theme_editor")
        config_action = self.action_registry.get_action("action_show_configuration")
        if theme_action:
            tools_menu.addAction(theme_action)
        if config_action:
            tools_menu.addAction(config_action)

        menu.exec(self.mapToGlobal(pos))

    def _add_checkable_actions(self) -> None:
        """Add custom checkable actions (defined via actions.json with checkable: true)."""

    # ------------------------------------------------------------------
    # ADS dock operations
    # ------------------------------------------------------------------

    def _on_new_dock(self) -> None:
        """Create a new dynamic dock panel."""
        if self.dock_manager is None:
            return
        self._panel_counter += 1
        dock = self._create_dock_widget(f"Panel {self._panel_counter}")
        label = QLabel(f"Dynamic Panel {self._panel_counter}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dock.setWidget(label)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
        dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)
        self.dock_manager.addDockWidget(QtAds.CenterDockWidgetArea, dock)
        self.docks.append(dock)
        self._log(f"New dock panel created: Panel {self._panel_counter}")
        self._schedule_splitter_refresh(80)

    def _on_float_all(self) -> None:
        """Float all dock panels."""
        for dock in list(self.docks):
            dock.setFloating()
        self._log("All panels set to floating")

    def _on_dock_all(self) -> None:
        """Dock all floating panels back to center."""
        if self.dock_manager is None:
            return
        for dock in list(self.docks):
            if dock.isFloating():
                self.dock_manager.addDockWidget(QtAds.CenterDockWidgetArea, dock)
        self._log("All floating panels docked")
        self._schedule_splitter_refresh(80)

    # ------------------------------------------------------------------
    # Tool dialog openers (same lazy-import pattern as MainWindow)
    # ------------------------------------------------------------------

    def _show_theme_editor(self) -> None:
        """Open the live theme editor dialog."""
        try:
            from widgetsystem.ui.theme_editor import ThemeEditorDialog

            dialog = ThemeEditorDialog(WORKSPACE_ROOT / "config")
            dialog.exec()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Theme editor could not be opened:\n{exc}")

    def _show_color_picker(self) -> None:
        """Open the ARGB color picker dialog."""
        try:
            from widgetsystem.ui.argb_color_picker import ARGBColorPickerDialog

            dialog = ARGBColorPickerDialog("#FFFF0000")
            if dialog.exec():
                color = dialog.get_color()
                clipboard = QApplication.clipboard()
                clipboard.setText(color)
                self._log(f"Color copied to clipboard: {color}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Color picker could not be opened:\n{exc}")

    def _show_widget_features_editor(self) -> None:
        """Open the widget features editor dialog."""
        try:
            from widgetsystem.ui.widget_features_editor import WidgetFeaturesEditorDialog

            dialog = WidgetFeaturesEditorDialog(WORKSPACE_ROOT / "config")
            dialog.exec()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Widget features editor could not be opened:\n{exc}")

    def _show_plugin_manager(self) -> None:
        """Open the plugin manager dialog."""
        try:
            from widgetsystem.ui.plugin_manager_dialog import PluginManagerDialog

            dialog = PluginManagerDialog(None, None, parent=self)
            dialog.exec()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Plugin manager could not be opened:\n{exc}")

    def _show_configuration_panel(self) -> None:
        """Open the configuration panel as a dock widget."""
        if self.dock_manager is None:
            return
        for dock in self.docks:
            if dock.windowTitle() == "Configuration":
                dock.toggleView(True)
                existing_widget = dock.widget()
                if existing_widget is not None:
                    self._configuration_panel = existing_widget
                return
        try:
            from widgetsystem.ui.config_panel import ConfigurationPanel

            config_path = WORKSPACE_ROOT / "config"
            panel = ConfigurationPanel(config_path, self.i18n_factory)
            self._configuration_panel = panel
            dock = self._create_dock_widget("Configuration")
            dock.setWidget(panel)
            dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetClosable, True)
            dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetMovable, True)
            dock.setFeature(QtAds.CDockWidget.DockWidgetFeature.DockWidgetFloatable, True)
            self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, dock)
            self.docks.append(dock)
            self._log("Configuration panel opened")
            self._schedule_splitter_refresh(80)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Configuration panel could not be opened:\n{exc}")

    def select_configuration_item(self, category: str, item_id: str) -> bool:
        """Select a configuration item in the Configuration panel.

        Args:
            category: Configuration category (e.g., "panels")
            item_id: Item identifier in that category

        Returns:
            True if selection was applied
        """
        if self._configuration_panel is None:
            self._show_configuration_panel()

        panel = self._configuration_panel
        if panel is None or not hasattr(panel, "select_config_item"):
            return False

        try:
            return bool(panel.select_config_item(category, item_id))
        except Exception:
            return False

    def get_selected_configuration_payload(self) -> dict[str, Any] | None:
        """Return currently selected configuration payload from Configuration panel.

        Returns:
            Dictionary payload of selected item or None
        """
        panel = self._configuration_panel
        if panel is None or not hasattr(panel, "get_selected_config_payload"):
            return None

        try:
            payload = panel.get_selected_config_payload()
        except Exception:
            return None

        if isinstance(payload, dict):
            return payload
        return None

    # Action handlers
    def _on_action(self, name: str, message: str = "") -> None:
        """Generic action handler."""
        self._log(f"Action: {name}")
        self.status_bar.showMessage(message or f"Executed: {name}", 3000)

    def _on_save_layout(self) -> None:
        """Handle save layout with file dialog."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Layout",
            "",
            "Layout Files (*.json);;All Files (*)",
        )
        if filename:
            self._log(f"Save Layout: {filename}")
            self.status_bar.showMessage(f"Layout saved to: {filename}", 3000)
            QMessageBox.information(self, "Success", f"Layout saved to:\n{filename}")

    def _on_load_layout(self) -> None:
        """Handle load layout with file dialog."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Layout",
            "",
            "Layout Files (*.json);;All Files (*)",
        )
        if filename:
            self._log(f"Load Layout: {filename}")
            self.status_bar.showMessage(f"Layout loaded from: {filename}", 3000)

    def _on_reset_layout(self) -> None:
        """Handle reset layout with confirmation."""
        reply = QMessageBox.question(
            self,
            "Reset Layout",
            "Are you sure you want to reset the layout to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._log("Layout reset to defaults")
            self.status_bar.showMessage("Layout reset to defaults", 3000)

    def _on_close_all(self) -> None:
        """Close all dock panels."""
        for dock in list(self.docks):
            dock.closeDockWidget()
        self._log("All panels closed")

    def _on_undo(self) -> None:
        """Handle undo."""
        self._log("Undo")
        self.status_bar.showMessage("Undo: No more actions to undo", 3000)

    def _on_redo(self) -> None:
        """Handle redo."""
        self._log("Redo")
        self.status_bar.showMessage("Redo: No more actions to redo", 3000)

    def _on_refresh(self) -> None:
        """Handle refresh — reload action registry state."""
        self._log(f"Refresh: {len(self.action_registry.list_action_ids())} actions active")

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Action Registry Demo",
            "<h3>Action Registry Demo</h3>"
            "<p>A demonstration of the centralized action management system.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>ActionFactory - loads from config/actions.json</li>"
            "<li>ActionRegistry - singleton for shared QActions</li>"
            "<li>ToolbarFactory - config-driven toolbars</li>"
            "<li>StatusBar - status tips on hover</li>"
            "<li>Context Menus - right-click support</li>"
            "<li>Checkable Actions - toggle states</li>"
            "<li>File Dialogs - save/load</li>"
            "<li>Message Boxes - confirmations</li>"
            "</ul>"
            "<p>Part of the WidgetSystem project.</p>",
        )

    def _log(self, message: str) -> None:
        """Add message to log."""
        self.log_text.append(f"> {message}")
        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main() -> None:
    """Run the demo."""
    # Reset singleton for clean demo
    ActionRegistry.reset_instance()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ActionRegistryDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
