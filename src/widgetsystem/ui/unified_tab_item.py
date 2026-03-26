"""UnifiedTabItem - Base class for all tab items with consistent features.

Every tab (dock tab, sub-tab, nested tab) gets the same functionality:
- Closable (with config support)
- Movable (drag to reorder)
- Floatable (extract as floating window)
- Context menu (close, float, settings)
- Configuration persistence
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QObject, QPoint, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QTabBar, QTabWidget, QWidget

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


class UnifiedTabItem(QObject):
    """Unified tab item with full feature parity.

    Wraps a tab in a QTabWidget and provides:
    - Close functionality with persistence
    - Float to window
    - Context menu
    - Configuration sync

    Signals:
        closeRequested: Tab close requested (can be vetoed)
        closed: Tab was closed
        floatRequested: User wants to float this tab
        configChanged: Tab configuration changed
    """

    closeRequested = Signal(str)  # tab_id
    closed = Signal(str)  # tab_id
    floatRequested = Signal(str)  # tab_id
    configChanged = Signal(str, dict)  # tab_id, config

    def __init__(
        self,
        tab_id: str,
        title: str,
        content_widget: QWidget,
        parent_tab_widget: QTabWidget,
        tab_index: int,
        config: dict[str, Any] | None = None,
        i18n_factory: "I18nFactory | None" = None,
        parent: QObject | None = None,
    ) -> None:
        """Initialize UnifiedTabItem.

        Args:
            tab_id: Unique tab identifier
            title: Display title
            content_widget: Content widget for this tab
            parent_tab_widget: Parent QTabWidget
            tab_index: Index in parent
            config: Tab configuration
            parent: Parent QObject
        """
        super().__init__(parent)

        self.tab_id = tab_id
        self.title = title
        self.content_widget = content_widget
        self.parent_tab_widget = parent_tab_widget
        self._tab_index = tab_index
        self._config = config or {}
        self._i18n_factory = i18n_factory
        self._translation_cache: dict[str, str] = {}

        # Extract config values
        self._closable = self._config.get("closable", True)
        self._movable = self._config.get("movable", True)
        self._floatable = self._config.get("floatable", True)
        self._icon_path = self._config.get("icon", "")
        self._tooltip = self._config.get("tooltip", "")

        # Store reference in widget for lookup
        content_widget.setProperty("unified_tab_item", self)
        content_widget.setProperty("tab_id", tab_id)

        # Setup context menu on tab bar
        self._setup_context_menu()

    def _translate(self, key: str, default: str) -> str:
        """Translate key using i18n factory with fallback and cache."""
        if not key:
            return default

        if key in self._translation_cache:
            return self._translation_cache[key]

        if self._i18n_factory is None:
            self._translation_cache[key] = default
            return default

        translated = self._i18n_factory.translate(key, default=default)
        self._translation_cache[key] = translated
        return translated

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory for runtime locale switching."""
        self._i18n_factory = i18n_factory
        self._translation_cache.clear()

    @property
    def tab_index(self) -> int:
        """Get current tab index (may change after reordering)."""
        # Find current index by content widget
        for i in range(self.parent_tab_widget.count()):
            if self.parent_tab_widget.widget(i) is self.content_widget:
                self._tab_index = i
                return i
        return self._tab_index

    @property
    def is_closable(self) -> bool:
        """Check if tab is closable."""
        return self._closable

    @property
    def is_movable(self) -> bool:
        """Check if tab is movable."""
        return self._movable

    @property
    def is_floatable(self) -> bool:
        """Check if tab is floatable."""
        return self._floatable

    @property
    def config(self) -> dict[str, Any]:
        """Get current configuration."""
        return dict(self._config)

    def _setup_context_menu(self) -> None:
        """Setup context menu for this tab."""
        tab_bar = self.parent_tab_widget.tabBar()
        if tab_bar:
            if not bool(tab_bar.property("_context_menu_installed")):
                self._install_context_menu(tab_bar)

    def _install_context_menu(self, tab_bar: QTabBar) -> None:
        """Install context menu handler on tab bar.

        Args:
            tab_bar: The tab bar widget

        """
        from PySide6.QtCore import Qt

        tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(tab_bar, pos)
        )
        tab_bar.setProperty("_context_menu_installed", True)

    def _show_context_menu(self, tab_bar: QTabBar, pos: QPoint) -> None:
        """Show context menu for tab at position.

        Args:
            tab_bar: The tab bar
            pos: Click position
        """
        # Find which tab was clicked
        clicked_index = tab_bar.tabAt(pos)
        if clicked_index < 0:
            return

        # Check if this is our tab
        if clicked_index != self.tab_index:
            # Let the correct tab handle it
            widget = self.parent_tab_widget.widget(clicked_index)
            if widget:
                item = widget.property("unified_tab_item")
                if item and isinstance(item, UnifiedTabItem):
                    item.show_context_menu(tab_bar.mapToGlobal(pos))
            return

        self.show_context_menu(tab_bar.mapToGlobal(pos))

    def show_context_menu(self, global_pos: QPoint) -> None:
        """Public wrapper to show this tab item's own context menu."""
        self._show_own_context_menu(global_pos)

    def _connect_action(self, action: QAction, callback: Callable[..., object]) -> None:
        """Connect QAction signal with type-safe fallback."""
        cast(Any, action.triggered).connect(callback)

    def _show_own_context_menu(self, global_pos: QPoint) -> None:
        """Show context menu for this specific tab.

        Args:
            global_pos: Global screen position
        """
        menu = QMenu()

        # Close action
        if self._closable:
            close_action = QAction(self._translate("unified_tab.action.close", "Close"), menu)
            self._connect_action(close_action, self.close)
            menu.addAction(close_action)

            close_others = QAction(
                self._translate("unified_tab.action.close_others", "Close Others"),
                menu,
            )
            self._connect_action(close_others, self._close_other_tabs)
            menu.addAction(close_others)

            close_right = QAction(
                self._translate("unified_tab.action.close_right", "Close Tabs to Right"),
                menu,
            )
            self._connect_action(close_right, self._close_tabs_to_right)
            menu.addAction(close_right)

            menu.addSeparator()

        # Float action
        if self._floatable:
            float_action = QAction(self._translate("unified_tab.action.float", "Float"), menu)
            self._connect_action(float_action, self._request_float)
            menu.addAction(float_action)
            menu.addSeparator()

        # Settings
        settings_action = QAction(
            self._translate("unified_tab.action.settings", "Tab Settings..."),
            menu,
        )
        self._connect_action(settings_action, self._show_settings)
        menu.addAction(settings_action)

        menu.exec(global_pos)

    def close(self) -> bool:
        """Close this tab.

        Returns:
            True if closed, False if vetoed
        """
        if not self._closable:
            return False

        # Emit request (can be vetoed by connected handlers)
        self.closeRequested.emit(self.tab_id)

        # Actually close
        idx = self.tab_index
        if idx >= 0:
            self.parent_tab_widget.removeTab(idx)
            self.closed.emit(self.tab_id)
            return True

        return False

    def _close_other_tabs(self) -> None:
        """Close all other tabs in parent."""
        my_idx = self.tab_index
        # Close from end to start to preserve indices
        for i in range(self.parent_tab_widget.count() - 1, -1, -1):
            if i != my_idx:
                widget = self.parent_tab_widget.widget(i)
                if widget:
                    item = widget.property("unified_tab_item")
                    if item and isinstance(item, UnifiedTabItem) and item.is_closable:
                        item.close()

    def _close_tabs_to_right(self) -> None:
        """Close tabs to the right of this one."""
        my_idx = self.tab_index
        # Close from end
        for i in range(self.parent_tab_widget.count() - 1, my_idx, -1):
            widget = self.parent_tab_widget.widget(i)
            if widget:
                item = widget.property("unified_tab_item")
                if item and isinstance(item, UnifiedTabItem) and item.is_closable:
                    item.close()

    def _request_float(self) -> None:
        """Request to float this tab."""
        self.floatRequested.emit(self.tab_id)

    def _show_settings(self) -> None:
        """Show settings dialog for this tab."""
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout
        from PySide6.QtWidgets import QCheckBox, QLineEdit, QFormLayout

        dialog = QDialog(self.parent_tab_widget)
        dialog_title = self._translate(
            "unified_tab.settings.window_title",
            "Tab Settings - {title}",
        ).format(title=self.title)
        dialog.setWindowTitle(dialog_title)
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        # Title edit
        title_edit = QLineEdit(self.title)
        form.addRow(
            self._translate("unified_tab.settings.field.title", "Title") + ":",
            title_edit,
        )

        # Closable
        closable_cb = QCheckBox()
        closable_cb.setChecked(self._closable)
        form.addRow(
            self._translate("unified_tab.settings.field.closable", "Closable") + ":",
            closable_cb,
        )

        # Movable
        movable_cb = QCheckBox()
        movable_cb.setChecked(self._movable)
        form.addRow(
            self._translate("unified_tab.settings.field.movable", "Movable") + ":",
            movable_cb,
        )

        # Floatable
        floatable_cb = QCheckBox()
        floatable_cb.setChecked(self._floatable)
        form.addRow(
            self._translate("unified_tab.settings.field.floatable", "Floatable") + ":",
            floatable_cb,
        )

        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        cast(Any, buttons.accepted).connect(  # pyright: ignore[reportAttributeAccessIssue]  # pylint: disable=no-member
            dialog.accept,
        )
        cast(Any, buttons.rejected).connect(  # pyright: ignore[reportAttributeAccessIssue]  # pylint: disable=no-member
            dialog.reject,
        )
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply changes
            new_title = title_edit.text()
            if new_title != self.title:
                self.title = new_title
                self.parent_tab_widget.setTabText(self.tab_index, new_title)

            self._closable = closable_cb.isChecked()
            self._movable = movable_cb.isChecked()
            self._floatable = floatable_cb.isChecked()

            # Update config
            self._config["closable"] = self._closable
            self._config["movable"] = self._movable
            self._config["floatable"] = self._floatable
            self._config["title"] = new_title

            self.configChanged.emit(self.tab_id, self._config)

    def set_icon(self, icon: QIcon | str) -> None:
        """Set tab icon.

        Args:
            icon: QIcon or path string
        """
        if isinstance(icon, str):
            icon = QIcon(icon)
        self.parent_tab_widget.setTabIcon(self.tab_index, icon)

    def set_tooltip(self, tooltip: str) -> None:
        """Set tab tooltip.

        Args:
            tooltip: Tooltip text
        """
        self._tooltip = tooltip
        self.parent_tab_widget.setTabToolTip(self.tab_index, tooltip)

    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable tab.

        Args:
            enabled: Enable state
        """
        self.parent_tab_widget.setTabEnabled(self.tab_index, enabled)

    def set_visible(self, visible: bool) -> None:
        """Show/hide tab.

        Args:
            visible: Visibility state
        """
        self.parent_tab_widget.setTabVisible(self.tab_index, visible)

    def activate(self) -> None:
        """Activate (select) this tab."""
        self.parent_tab_widget.setCurrentIndex(self.tab_index)

    def to_dict(self) -> dict[str, Any]:
        """Export configuration to dict for persistence.

        Returns:
            Configuration dictionary
        """
        return {
            "id": self.tab_id,
            "title": self.title,
            "closable": self._closable,
            "movable": self._movable,
            "floatable": self._floatable,
            "icon": self._icon_path,
            "tooltip": self._tooltip,
            "visible": self.parent_tab_widget.isTabVisible(self.tab_index),
            "enabled": self.parent_tab_widget.isTabEnabled(self.tab_index),
        }
