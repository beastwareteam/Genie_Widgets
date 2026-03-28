"""Configuration Panel - Dynamic UI configuration interface for all structural elements."""

from pathlib import Path
from typing import Any
from typing import Callable
from typing import cast

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.list_factory import ListFactory, ListGroup, ListItem
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.factories.panel_factory import PanelConfig, PanelFactory
from widgetsystem.factories.tabs_factory import Tab, TabsFactory
from widgetsystem.factories.ui_config_factory import UIConfigFactory


class ConfigurationPanel(QWidget):
    """Dynamic configuration panel for managing UI structures.

    Provides interfaces to create, edit, and delete:
    - Menus with nesting
    - Lists with nesting
    - Tab groups
    - Panels
    - Theme settings
    - Advanced settings (responsive design, DnD)
    """

    # Signals for structural changes
    config_changed = Signal(str)  # Emitted when configuration changes (category)
    item_added = Signal(str, str)  # Emitted when item is added (category, id)
    item_deleted = Signal(str, str)  # Emitted when item is deleted (category, id)
    item_selected = Signal(str, str)  # Emitted when item is selected (category, id)

    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize configuration panel."""
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory

        self.menu_tree: QTreeWidget | None = None
        self.list_tree: QTreeWidget | None = None
        self.tabs_tree: QTreeWidget | None = None
        self.panels_list: QListWidget | None = None
        self.config_tabs: QTabWidget | None = None
        self.panel_id_value: QLabel | None = None
        self.panel_name_key_input: QLineEdit | None = None
        self.panel_tooltip_key_input: QLineEdit | None = None
        self.panel_area_editor_combo: QComboBox | None = None
        self.panel_closable_editor: QCheckBox | None = None
        self.panel_movable_editor: QCheckBox | None = None
        self.panel_floatable_editor: QCheckBox | None = None
        self.panel_delete_on_close_editor: QCheckBox | None = None
        self.panel_dnd_enabled_editor: QCheckBox | None = None
        self.panel_responsive_hidden_input: QLineEdit | None = None
        self.panel_apply_btn: QPushButton | None = None
        self._selected_panel_id: str | None = None

        # Initialize factories
        self.list_factory = ListFactory(self.config_path)
        self.menu_factory = MenuFactory(self.config_path)
        self.tabs_factory = TabsFactory(self.config_path)
        self.panel_factory = PanelFactory(self.config_path)
        self.ui_config_factory = UIConfigFactory(self.config_path)

        # Setup UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the configuration panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Main tab widget for different configuration categories
        self.config_tabs = QTabWidget()
        layout.addWidget(self.config_tabs)

        self._rebuild_tabs()

    def _rebuild_tabs(self) -> None:
        """Rebuild translated category tabs."""
        if self.config_tabs is None:
            return

        self.config_tabs.clear()

        # Load all configuration pages
        try:
            categories = self.ui_config_factory.get_all_categories()

            for category in sorted(categories):
                pages = self.ui_config_factory.get_pages_by_category(category)
                if pages:
                    # Create tab for each category
                    category_widget = self._create_category_widget(category)
                    category_widget.setProperty("config_category", category)
                    tab_title = self.i18n_factory.translate(
                        f"config.{category}.title",
                        default=category.title(),
                    )
                    self.config_tabs.addTab(category_widget, tab_title)

        except Exception as e:
            error_label = QLabel(
                self.i18n_factory.translate(
                    "config.error_loading",
                    default="Error loading configuration: {error}",
                    error=str(e),
                ),
            )
            self.config_tabs.addTab(
                error_label,
                self.i18n_factory.translate("message.error", default="Error"),
            )

    def set_i18n_factory(self, i18n_factory: I18nFactory) -> None:
        """Set or update i18n factory and refresh translated UI texts."""
        self.i18n_factory = i18n_factory
        self._rebuild_tabs()

    @staticmethod
    def _connect_signal(signal: object, callback: Callable[..., None]) -> None:
        """Connect Qt signal with typed fallback for static analyzers."""
        cast(Any, signal).connect(callback)  # pyright: ignore[reportAttributeAccessIssue]  # pylint: disable=no-member

    def _create_category_widget(self, category: str) -> QWidget:
        """Create a widget for a configuration category."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        if category == "menus":
            self._setup_menus_editor(layout)
        elif category == "lists":
            self._setup_lists_editor(layout)
        elif category == "tabs":
            self._setup_tabs_editor(layout)
        elif category == "panels":
            self._setup_panels_editor(layout)
        elif category == "theme":
            self._setup_theme_selector(layout)
        elif category == "advanced":
            self._setup_advanced_settings(layout)
        else:
            layout.addWidget(
                QLabel(
                    self.i18n_factory.translate(
                        "config.category.fallback",
                        default="Configuration for {category}",
                        category=category,
                    ),
                ),
            )

        layout.addStretch()
        return widget

    def _setup_menus_editor(self, parent_layout: QVBoxLayout) -> None:
        """Setup menu editor interface."""
        title = QLabel(
            self.i18n_factory.translate("config.menu_editor.label", default="Menu Editor"),
        )
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        parent_layout.addWidget(title)

        # Splitter for menu tree and properties
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Menu tree on the left
        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderLabel(
            self.i18n_factory.translate("config.menus.tree_header", default="Menus"),
        )
        self.menu_tree.setMinimumWidth(250)

        try:
            menus = self.menu_factory.load_menus()
            for menu in menus:
                self._add_menu_to_tree(self.menu_tree, menu, None)
        except Exception:
            pass

        splitter.addWidget(self.menu_tree)

        # Properties panel on the right
        properties_widget = QWidget()
        props_layout = QFormLayout(properties_widget)

        menu_name_input = QLineEdit()
        menu_name_input.setPlaceholderText(
            self.i18n_factory.translate("config.menu_name", default="Menu name"),
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.menu_name", default="Name:"),
            menu_name_input,
        )

        menu_shortcut_input = QLineEdit()
        menu_shortcut_input.setPlaceholderText(
            self.i18n_factory.translate("config.menu_shortcut.placeholder", default="Ctrl+M"),
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.menu_shortcut", default="Shortcut:"),
            menu_shortcut_input,
        )

        add_menu_btn = QPushButton(self.i18n_factory.translate("button.add", default="Add Menu"))
        self._connect_signal(add_menu_btn.clicked, lambda: self._on_add_menu(menu_name_input.text()))
        props_layout.addRow(add_menu_btn)

        splitter.addWidget(properties_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        parent_layout.addWidget(splitter)

    def _add_menu_to_tree(
        self,
        parent: QTreeWidget | QTreeWidgetItem,
        menu: MenuItem,
        parent_item: QTreeWidgetItem | None,
    ) -> None:
        """Recursively add menu item to tree."""
        item = QTreeWidgetItem(parent) if parent_item is None else QTreeWidgetItem(parent_item)

        item.setText(0, menu.label_key)
        item.setData(0, Qt.ItemDataRole.UserRole, menu.id)

        for child in menu.children:
            self._add_menu_to_tree(parent, child, item)

    def _setup_lists_editor(self, parent_layout: QVBoxLayout) -> None:
        """Setup list editor interface."""
        title = QLabel(
            self.i18n_factory.translate("config.list_editor.label", default="List Editor"),
        )
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        parent_layout.addWidget(title)

        # Splitter for list tree and properties
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # List tree on the left
        self.list_tree = QTreeWidget()
        self.list_tree.setHeaderLabel(
            self.i18n_factory.translate("config.lists.tree_header", default="Lists"),
        )
        self.list_tree.setMinimumWidth(250)

        try:
            list_groups = self.list_factory.load_list_groups()
            for group in list_groups:
                self._add_list_to_tree(self.list_tree, group, None)
        except Exception:
            pass

        splitter.addWidget(self.list_tree)

        # Properties panel on the right
        properties_widget = QWidget()
        props_layout = QFormLayout(properties_widget)

        list_name_input = QLineEdit()
        list_name_input.setPlaceholderText(
            self.i18n_factory.translate("config.list_name", default="List name"),
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.list_name", default="Name:"),
            list_name_input,
        )

        list_type_combo = QComboBox()
        list_type_combo.addItem(
            self.i18n_factory.translate("config.list.type.vertical", default="Vertical"),
            "vertical",
        )
        list_type_combo.addItem(
            self.i18n_factory.translate("config.list.type.horizontal", default="Horizontal"),
            "horizontal",
        )
        list_type_combo.addItem(
            self.i18n_factory.translate("config.list.type.tree", default="Tree"),
            "tree",
        )
        list_type_combo.addItem(
            self.i18n_factory.translate("config.list.type.table", default="Table"),
            "table",
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.list_type", default="Type:"),
            list_type_combo,
        )

        sortable_check = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.list_sortable", default="Sortable:"),
            sortable_check,
        )

        searchable_check = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.list_searchable", default="Searchable:"),
            searchable_check,
        )

        add_list_btn = QPushButton(self.i18n_factory.translate("button.add", default="Add List"))
        self._connect_signal(
            add_list_btn.clicked,
            lambda: self._on_add_list(
                list_name_input.text(),
                str(list_type_combo.currentData() or "vertical"),
            ),
        )
        props_layout.addRow(add_list_btn)

        splitter.addWidget(properties_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        parent_layout.addWidget(splitter)

    def _add_list_to_tree(
        self,
        parent: QTreeWidget | QTreeWidgetItem,
        group: ListGroup,
        parent_item: QTreeWidgetItem | None,
    ) -> None:
        """Recursively add list item to tree."""
        if parent_item is None:
            group_item = QTreeWidgetItem(parent)
        else:
            group_item = QTreeWidgetItem(parent_item)

        group_item.setText(0, f"{group.title_key} ({group.list_type})")
        group_item.setData(0, Qt.ItemDataRole.UserRole, group.id)

        for item in group.items:
            self._add_item_to_tree(group_item, item)

    def _add_item_to_tree(self, parent: QTreeWidgetItem, item: ListItem) -> None:
        """Recursively add item to tree."""
        item_widget = QTreeWidgetItem(parent)
        item_widget.setText(0, item.label_key)
        item_widget.setData(0, Qt.ItemDataRole.UserRole, item.id)

        for child in item.children:
            self._add_item_to_tree(item_widget, child)

    def _refresh_lists_tree(self) -> None:
        """Refresh the list tree widget with current data from factory."""
        if self.list_tree is None:
            return

        # Clear the tree
        list_tree = self.list_tree
        list_tree.clear()

        try:
            # Re-populate with current data
            list_groups = self.list_factory.load_list_groups()
            for group in list_groups:
                self._add_list_to_tree(list_tree, group, None)
        except Exception:
            pass

    def _refresh_menus_tree(self) -> None:
        """Refresh the menu tree widget with current data from factory."""
        if self.menu_tree is None:
            return

        # Clear the tree
        menu_tree = self.menu_tree
        menu_tree.clear()

        try:
            # Re-populate with current data
            menus = self.menu_factory.load_menus()
            for menu in menus:
                self._add_menu_to_tree(menu_tree, menu, None)
        except Exception:
            pass

    def _refresh_tabs_tree(self) -> None:
        """Refresh the tabs tree widget with current data from factory."""
        if self.tabs_tree is None:
            return

        # Clear the tree
        tabs_tree = self.tabs_tree
        tabs_tree.clear()

        try:
            # Re-populate with current data
            tab_groups = self.tabs_factory.load_tab_groups()
            for group in tab_groups:
                group_item = QTreeWidgetItem(tabs_tree)
                group_item.setText(0, group.title_key)
                group_item.setData(0, Qt.ItemDataRole.UserRole, group.id)

                for tab in group.tabs:
                    self._add_tab_to_tree(group_item, tab)
        except Exception:
            pass

    def _refresh_panels_tree(self) -> None:
        """Refresh the panels list widget with current data from factory."""
        if self.panels_list is None:
            return

        selected_panel_id = self._selected_panel_id

        # Clear the list
        panels_list = self.panels_list
        panels_list.clear()

        try:
            # Re-populate with current data
            panels = self.panel_factory.load_panels()
            for panel in panels:
                item = QListWidgetItem(
                    self.i18n_factory.translate(panel.name_key, default=panel.id),
                )
                item.setData(Qt.ItemDataRole.UserRole, panel.id)
                panels_list.addItem(item)

            if selected_panel_id:
                for index in range(panels_list.count()):
                    candidate = panels_list.item(index)
                    candidate_id = candidate.data(Qt.ItemDataRole.UserRole)
                    if isinstance(candidate_id, str) and candidate_id == selected_panel_id:
                        panels_list.setCurrentItem(candidate)
                        break
        except Exception:
            pass

    def _set_panel_editor_enabled(self, enabled: bool) -> None:
        """Enable or disable selected-panel editor widgets."""
        editor_widgets: list[QWidget | None] = [
            self.panel_name_key_input,
            self.panel_tooltip_key_input,
            self.panel_area_editor_combo,
            self.panel_closable_editor,
            self.panel_movable_editor,
            self.panel_floatable_editor,
            self.panel_delete_on_close_editor,
            self.panel_dnd_enabled_editor,
            self.panel_responsive_hidden_input,
            self.panel_apply_btn,
        ]
        for widget in editor_widgets:
            if widget is not None:
                widget.setEnabled(enabled)

    def _populate_panel_editor(self, panel: PanelConfig) -> None:
        """Populate selected-panel editor fields from config."""
        if self.panel_id_value is not None:
            self.panel_id_value.setText(panel.id)
        if self.panel_name_key_input is not None:
            self.panel_name_key_input.setText(panel.name_key)
        if self.panel_tooltip_key_input is not None:
            self.panel_tooltip_key_input.setText(panel.tooltip_key)
        if self.panel_area_editor_combo is not None:
            index = self.panel_area_editor_combo.findData(panel.area)
            if index >= 0:
                self.panel_area_editor_combo.setCurrentIndex(index)
        if self.panel_closable_editor is not None:
            self.panel_closable_editor.setChecked(panel.closable)
        if self.panel_movable_editor is not None:
            self.panel_movable_editor.setChecked(panel.movable)
        if self.panel_floatable_editor is not None:
            self.panel_floatable_editor.setChecked(panel.floatable)
        if self.panel_delete_on_close_editor is not None:
            self.panel_delete_on_close_editor.setChecked(panel.delete_on_close)
        if self.panel_dnd_enabled_editor is not None:
            self.panel_dnd_enabled_editor.setChecked(panel.dnd_enabled)
        if self.panel_responsive_hidden_input is not None:
            self.panel_responsive_hidden_input.setText(",".join(panel.responsive_hidden_at or []))

    def _on_panel_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        """Load selected panel details into the editor."""
        if current is None:
            self._selected_panel_id = None
            if self.panel_id_value is not None:
                self.panel_id_value.setText("-")
            self._set_panel_editor_enabled(False)
            return

        panel_id = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(panel_id, str):
            return

        panel = self.panel_factory.get_panel(panel_id)
        if panel is None:
            return

        self._selected_panel_id = panel_id
        self._populate_panel_editor(panel)
        self._set_panel_editor_enabled(True)
        self.item_selected.emit("panels", panel_id)

    def _on_apply_selected_panel(self) -> None:
        """Apply current selected-panel editor values to configuration."""
        panel_id = self._selected_panel_id
        if not panel_id:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("dialog.warning", default="Warning"),
                self.i18n_factory.translate(
                    "config.validation.panel_selection_required",
                    default="Please select a panel first",
                ),
            )
            return

        if (
            self.panel_name_key_input is None
            or self.panel_tooltip_key_input is None
            or self.panel_area_editor_combo is None
            or self.panel_closable_editor is None
            or self.panel_movable_editor is None
            or self.panel_floatable_editor is None
            or self.panel_delete_on_close_editor is None
            or self.panel_dnd_enabled_editor is None
            or self.panel_responsive_hidden_input is None
        ):
            return

        responsive_hidden_at = [
            value.strip()
            for value in self.panel_responsive_hidden_input.text().split(",")
            if value.strip()
        ]

        success = self.panel_factory.update_panel(
            panel_id,
            name_key=self.panel_name_key_input.text().strip(),
            tooltip_key=self.panel_tooltip_key_input.text().strip(),
            area=str(self.panel_area_editor_combo.currentData() or "center"),
            closable=self.panel_closable_editor.isChecked(),
            movable=self.panel_movable_editor.isChecked(),
            floatable=self.panel_floatable_editor.isChecked(),
            delete_on_close=self.panel_delete_on_close_editor.isChecked(),
            dnd_enabled=self.panel_dnd_enabled_editor.isChecked(),
            responsive_hidden_at=responsive_hidden_at,
        )

        if not success:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                self.i18n_factory.translate(
                    "config.error.save_panel_failed",
                    default="Failed to save panel to configuration file",
                ),
            )
            return

        self.panel_factory = PanelFactory(self.config_path)
        self._refresh_panels_tree()
        self.config_changed.emit("panels")

    def select_config_item(self, category: str, item_id: str) -> bool:
        """Select a configuration item programmatically (automation helper).

        Args:
            category: Category name (currently supports: panels)
            item_id: Configuration item id

        Returns:
            True when a matching item was selected
        """
        if category != "panels" or self.panels_list is None:
            return False

        if self.config_tabs is not None:
            for index in range(self.config_tabs.count()):
                widget = self.config_tabs.widget(index)
                category_prop = widget.property("config_category") if widget is not None else None
                if category_prop == "panels":
                    self.config_tabs.setCurrentIndex(index)
                    break

        for index in range(self.panels_list.count()):
            item = self.panels_list.item(index)
            current_id = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(current_id, str) and current_id == item_id:
                self.panels_list.setCurrentItem(item)
                return True

        return False

    def get_selected_config_payload(self) -> dict[str, Any] | None:
        """Return selected configuration payload (automation helper).

        Returns:
            Selected panel configuration as a dictionary or None
        """
        if not self._selected_panel_id:
            return None

        panel = self.panel_factory.get_panel(self._selected_panel_id)
        if panel is None:
            return None

        return {
            "category": "panels",
            "id": panel.id,
            "name_key": panel.name_key,
            "tooltip_key": panel.tooltip_key,
            "area": panel.area,
            "closable": panel.closable,
            "movable": panel.movable,
            "floatable": panel.floatable,
            "delete_on_close": panel.delete_on_close,
            "dnd_enabled": panel.dnd_enabled,
            "responsive_hidden_at": panel.responsive_hidden_at or [],
        }

    def _setup_tabs_editor(self, parent_layout: QVBoxLayout) -> None:
        """Setup tab editor interface.

        Architectural note:
            This editor currently operates on persisted demo configuration from
            `config/tabs.json`. A full implementation for the original app must
            additionally integrate the runtime tab architecture, including:
            - `TabSubsystem`
            - `UnifiedTabManager`
            - `TabNavigationController`
            - `TabCommandController`

            Required implementation step:
            Runtime tab/container identities from the original application must be
            mapped to persisted config identities before full automation/editing can
            be considered complete. Until then, this editor remains a demo-oriented
            configuration surface and not the final architecture source of truth.
        """
        title = QLabel(self.i18n_factory.translate("config.tab_editor.label", default="Tab Editor"))
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        parent_layout.addWidget(title)

        architecture_note = QLabel(
            self.i18n_factory.translate(
                "config.tabs.architecture_note",
                default=(
                    "Demo-Hinweis: Die Tab-Bearbeitung arbeitet hier aktuell nur auf "
                    "Konfigurationsbasis. Für die Original-App ist zusätzlich eine "
                    "Anbindung an Runtime-Tabstrukturen und Tab-Controller notwendig."
                ),
            ),
        )
        architecture_note.setWordWrap(True)
        architecture_note.setStyleSheet(
            "color: #c8b48a; background-color: rgba(255, 196, 64, 0.08); "
            "border: 1px solid rgba(255, 196, 64, 0.22); border-radius: 4px; padding: 6px;"
        )
        parent_layout.addWidget(architecture_note)

        info = QLabel(
            self.i18n_factory.translate(
                "config.tabs.description",
                default="Create and manage tab groups",
            ),
        )
        parent_layout.addWidget(info)

        # Splitter for tab tree and properties
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tab tree on the left
        self.tabs_tree = QTreeWidget()
        self.tabs_tree.setHeaderLabel(
            self.i18n_factory.translate("config.tabs.tree_header", default="Tab Groups"),
        )
        self.tabs_tree.setMinimumWidth(250)

        try:
            tab_groups = self.tabs_factory.load_tab_groups()
            for group in tab_groups:
                group_item = QTreeWidgetItem(self.tabs_tree)
                group_item.setText(0, group.title_key)
                group_item.setData(0, Qt.ItemDataRole.UserRole, group.id)

                for tab in group.tabs:
                    self._add_tab_to_tree(group_item, tab)

        except Exception:
            pass

        splitter.addWidget(self.tabs_tree)

        # Properties panel on the right
        properties_widget = QWidget()
        props_layout = QFormLayout(properties_widget)

        tab_name_input = QLineEdit()
        tab_name_input.setPlaceholderText(
            self.i18n_factory.translate("config.tab_name", default="Tab name"),
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.tab_name", default="Name:"),
            tab_name_input,
        )

        tab_closable = QCheckBox()
        tab_closable.setChecked(True)
        props_layout.addRow(
            self.i18n_factory.translate("config.tab_closable", default="Closable:"),
            tab_closable,
        )

        add_tab_btn = QPushButton(self.i18n_factory.translate("button.add", default="Add Tab"))
        self._connect_signal(add_tab_btn.clicked, lambda: self._on_add_tab(tab_name_input.text()))
        props_layout.addRow(add_tab_btn)

        splitter.addWidget(properties_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        parent_layout.addWidget(splitter)

    def _add_tab_to_tree(self, parent: QTreeWidgetItem, tab: Tab) -> None:
        """Recursively add tab to tree."""
        tab_item = QTreeWidgetItem(parent)
        tab_item.setText(0, tab.title_key)
        tab_item.setData(0, Qt.ItemDataRole.UserRole, tab.id)

        for child in tab.children:
            self._add_tab_to_tree(tab_item, child)

    def _setup_panels_editor(self, parent_layout: QVBoxLayout) -> None:
        """Setup panel editor interface."""
        title = QLabel(
            self.i18n_factory.translate("config.panel_editor.label", default="Panel Editor"),
        )
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        parent_layout.addWidget(title)

        info = QLabel(
            self.i18n_factory.translate(
                "config.panels.description",
                default="Create and manage panels",
            ),
        )
        parent_layout.addWidget(info)

        # Panels list
        self.panels_list = QListWidget()

        try:
            panels = self.panel_factory.load_panels()
            for panel in panels:
                item = QListWidgetItem(
                    self.i18n_factory.translate(panel.name_key, default=panel.id),
                )
                item.setData(Qt.ItemDataRole.UserRole, panel.id)
                self.panels_list.addItem(item)
        except Exception:
            pass

        self._connect_signal(self.panels_list.currentItemChanged, self._on_panel_selection_changed)

        parent_layout.addWidget(self.panels_list)

        # Properties
        properties_widget = QWidget()
        props_layout = QFormLayout(properties_widget)

        panel_name_input = QLineEdit()
        panel_name_input.setPlaceholderText(
            self.i18n_factory.translate("config.panel_name", default="Panel name"),
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_name", default="Name:"),
            panel_name_input,
        )

        panel_area_combo = QComboBox()
        panel_area_combo.addItem(
            self.i18n_factory.translate("config.panel.area.left", default="Left"),
            "left",
        )
        panel_area_combo.addItem(
            self.i18n_factory.translate("config.panel.area.right", default="Right"),
            "right",
        )
        panel_area_combo.addItem(
            self.i18n_factory.translate("config.panel.area.bottom", default="Bottom"),
            "bottom",
        )
        panel_area_combo.addItem(
            self.i18n_factory.translate("config.panel.area.center", default="Center"),
            "center",
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_area", default="Area:"),
            panel_area_combo,
        )

        panel_closable = QCheckBox()
        panel_closable.setChecked(True)
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_closable", default="Closable:"),
            panel_closable,
        )

        add_panel_btn = QPushButton(self.i18n_factory.translate("button.add", default="Add Panel"))
        self._connect_signal(
            add_panel_btn.clicked,
            lambda: self._on_add_panel(
                panel_name_input.text(),
                str(panel_area_combo.currentData() or "left"),
            ),
        )
        props_layout.addRow(add_panel_btn)

        selected_header = QLabel(
            self.i18n_factory.translate(
                "config.panel.selected_header",
                default="Selected panel (inspect/edit)",
            ),
        )
        selected_header.setStyleSheet("font-weight: bold; padding-top: 6px;")
        props_layout.addRow(selected_header)

        self.panel_id_value = QLabel("-")
        props_layout.addRow(
            self.i18n_factory.translate("config.panel.id", default="ID:"),
            self.panel_id_value,
        )

        self.panel_name_key_input = QLineEdit()
        props_layout.addRow(
            self.i18n_factory.translate("config.panel.name_key", default="Name key:"),
            self.panel_name_key_input,
        )

        self.panel_tooltip_key_input = QLineEdit()
        props_layout.addRow(
            self.i18n_factory.translate("config.panel.tooltip_key", default="Tooltip key:"),
            self.panel_tooltip_key_input,
        )

        self.panel_area_editor_combo = QComboBox()
        self.panel_area_editor_combo.addItem(
            self.i18n_factory.translate("config.panel.area.left", default="Left"),
            "left",
        )
        self.panel_area_editor_combo.addItem(
            self.i18n_factory.translate("config.panel.area.right", default="Right"),
            "right",
        )
        self.panel_area_editor_combo.addItem(
            self.i18n_factory.translate("config.panel.area.bottom", default="Bottom"),
            "bottom",
        )
        self.panel_area_editor_combo.addItem(
            self.i18n_factory.translate("config.panel.area.center", default="Center"),
            "center",
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_area", default="Area:"),
            self.panel_area_editor_combo,
        )

        self.panel_closable_editor = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_closable", default="Closable:"),
            self.panel_closable_editor,
        )

        self.panel_movable_editor = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.panel.movable", default="Movable:"),
            self.panel_movable_editor,
        )

        self.panel_floatable_editor = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.panel.floatable", default="Floatable:"),
            self.panel_floatable_editor,
        )

        self.panel_delete_on_close_editor = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.panel.delete_on_close", default="Delete on close:"),
            self.panel_delete_on_close_editor,
        )

        self.panel_dnd_enabled_editor = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.panel.dnd_enabled", default="DnD enabled:"),
            self.panel_dnd_enabled_editor,
        )

        self.panel_responsive_hidden_input = QLineEdit()
        self.panel_responsive_hidden_input.setPlaceholderText("sm,md")
        props_layout.addRow(
            self.i18n_factory.translate(
                "config.panel.responsive_hidden_at",
                default="Hidden at breakpoints:",
            ),
            self.panel_responsive_hidden_input,
        )

        self.panel_apply_btn = QPushButton(
            self.i18n_factory.translate("button.apply", default="Apply"),
        )
        self._connect_signal(self.panel_apply_btn.clicked, self._on_apply_selected_panel)
        props_layout.addRow(self.panel_apply_btn)

        self._set_panel_editor_enabled(False)

        parent_layout.addWidget(properties_widget)

    def _setup_theme_selector(self, parent_layout: QVBoxLayout) -> None:
        """Setup theme selector interface."""
        title = QLabel(
            self.i18n_factory.translate("config.theme_selector.label", default="Theme Selection"),
        )
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        parent_layout.addWidget(title)

        theme_combo = QComboBox()
        theme_combo.addItem(
            self.i18n_factory.translate("config.theme.light", default="Light"),
            "light",
        )
        theme_combo.addItem(
            self.i18n_factory.translate("config.theme.dark", default="Dark"),
            "dark",
        )

        parent_layout.addWidget(
            QLabel(self.i18n_factory.translate("config.current_theme", default="Current Theme:")),
        )
        parent_layout.addWidget(theme_combo)

        apply_btn = QPushButton(self.i18n_factory.translate("button.apply", default="Apply"))
        self._connect_signal(apply_btn.clicked, lambda: self.config_changed.emit("theme"))
        parent_layout.addWidget(apply_btn)

    def _setup_advanced_settings(self, parent_layout: QVBoxLayout) -> None:
        """Setup advanced settings interface."""
        # Responsive Design
        responsive_group = QGroupBox(
            self.i18n_factory.translate("config.responsive.label", default="Responsive Design"),
        )
        resp_layout = QFormLayout(responsive_group)

        breakpoint_combo = QComboBox()
        breakpoint_combo.addItems(["xs", "sm", "md", "lg", "xl"])
        resp_layout.addRow(
            self.i18n_factory.translate("config.breakpoint", default="Breakpoint:"),
            breakpoint_combo,
        )

        parent_layout.addWidget(responsive_group)

        # Drag & Drop
        dnd_group = QGroupBox(
            self.i18n_factory.translate("config.dnd.label", default="Drag & Drop"),
        )
        dnd_layout = QFormLayout(dnd_group)

        dnd_enabled = QCheckBox()
        dnd_enabled.setChecked(True)
        dnd_layout.addRow(
            self.i18n_factory.translate("config.dnd_enabled", default="Enabled:"),
            dnd_enabled,
        )

        dnd_opacity = QDoubleSpinBox()
        dnd_opacity.setRange(0.0, 1.0)
        dnd_opacity.setSingleStep(0.1)
        dnd_opacity.setValue(0.7)
        dnd_layout.addRow(
            self.i18n_factory.translate("config.dnd_opacity", default="Opacity:"),
            dnd_opacity,
        )

        parent_layout.addWidget(dnd_group)

    # -----------------------------------------------------------------------
    # Event handlers
    # -----------------------------------------------------------------------

    def _on_add_menu(self, menu_name: str) -> None:
        """Add a new menu from input."""
        if not menu_name:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("dialog.warning", default="Warning"),
                self.i18n_factory.translate(
                    "config.validation.menu_name_required",
                    default="Please enter a menu name",
                ),
            )
            return

        try:
            # Create a valid ID from the name
            menu_id = menu_name.lower().replace(" ", "_")

            # Add to factory and save
            success = self.menu_factory.add_menu_item(
                menu_id=menu_id,
                label_key=f"menu.{menu_id}.label",
                menu_type="action",
            )

            if success:
                # Reload the factory
                self.menu_factory = MenuFactory(self.config_path)
                # Refresh the UI
                self._refresh_menus_tree()
                self.config_changed.emit("menus")
                QMessageBox.information(
                    self,
                    self.i18n_factory.translate("message.success", default="Success"),
                    self.i18n_factory.translate(
                        "config.message.menu_added",
                        default="Menu '{name}' added and saved!",
                        name=menu_name,
                    ),
                )
            else:
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.error", default="Error"),
                    self.i18n_factory.translate(
                        "config.error.save_menu_failed",
                        default="Failed to save menu to configuration file",
                    ),
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                self.i18n_factory.translate(
                    "config.error.add_menu_failed",
                    default="Failed to add menu: {error}",
                    error=str(e),
                ),
            )

    def _on_add_list(self, list_name: str, list_type: str) -> None:
        """Add a new list from input."""
        if not list_name:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("dialog.warning", default="Warning"),
                self.i18n_factory.translate(
                    "config.validation.list_name_required",
                    default="Please enter a list name",
                ),
            )
            return

        try:
            # Create a valid ID from the name
            list_id = list_name.lower().replace(" ", "_")

            # Add to factory and save
            success = self.list_factory.add_list_group(
                group_id=list_id,
                title_key=f"list.{list_id}.title",
                list_type=list_type,
                panel_id="center",
            )

            if success:
                # Reload the factory to reflect changes
                self.list_factory = ListFactory(self.config_path)
                # Refresh the UI tree
                self._refresh_lists_tree()
                self.config_changed.emit("lists")
                QMessageBox.information(
                    self,
                    self.i18n_factory.translate("message.success", default="Success"),
                    self.i18n_factory.translate(
                        "config.message.list_added",
                        default="List '{name}' ({type}) added and saved!",
                        name=list_name,
                        type=list_type,
                    ),
                )
            else:
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.error", default="Error"),
                    self.i18n_factory.translate(
                        "config.error.save_list_failed",
                        default="Failed to save list to configuration file",
                    ),
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                self.i18n_factory.translate(
                    "config.error.add_list_failed",
                    default="Failed to add list: {error}",
                    error=str(e),
                ),
            )

    def _on_add_tab(self, tab_name: str) -> None:
        """Add a new tab from input."""
        if not tab_name:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("dialog.warning", default="Warning"),
                self.i18n_factory.translate(
                    "config.validation.tab_name_required",
                    default="Please enter a tab name",
                ),
            )
            return

        try:
            # Create a valid ID from the name
            tab_id = tab_name.lower().replace(" ", "_")

            # Add to factory and save
            success = self.tabs_factory.add_tab_group(
                group_id=tab_id,
                title_key=f"tabs.{tab_id}.title",
                dock_area="center",
                orientation="horizontal",
            )

            if success:
                # Reload the factory
                self.tabs_factory = TabsFactory(self.config_path)
                # Refresh the UI
                self._refresh_tabs_tree()
                self.config_changed.emit("tabs")
                QMessageBox.information(
                    self,
                    self.i18n_factory.translate("message.success", default="Success"),
                    self.i18n_factory.translate(
                        "config.message.tab_added",
                        default="Tab '{name}' added and saved!",
                        name=tab_name,
                    ),
                )
            else:
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.error", default="Error"),
                    self.i18n_factory.translate(
                        "config.error.save_tab_failed",
                        default="Failed to save tab to configuration file",
                    ),
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                self.i18n_factory.translate(
                    "config.error.add_tab_failed",
                    default="Failed to add tab: {error}",
                    error=str(e),
                ),
            )

    def _on_add_panel(self, panel_name: str, panel_area: str) -> None:
        """Add a new panel from input."""
        if not panel_name:
            QMessageBox.warning(
                self,
                self.i18n_factory.translate("dialog.warning", default="Warning"),
                self.i18n_factory.translate(
                    "config.validation.panel_name_required",
                    default="Please enter a panel name",
                ),
            )
            return

        try:
            # Create a valid ID from the name
            panel_id = panel_name.lower().replace(" ", "_")

            # Add to factory and save
            success = self.panel_factory.add_panel(
                panel_id=panel_id,
                name_key=f"panel.{panel_id}.name",
                area=panel_area,
                closable=True,
                movable=True,
            )

            if success:
                # Reload the factory
                self.panel_factory = PanelFactory(self.config_path)
                # Refresh the UI
                self._selected_panel_id = panel_id
                self._refresh_panels_tree()
                self.select_config_item("panels", panel_id)
                self.config_changed.emit("panels")
                self.item_added.emit("panels", panel_id)
                QMessageBox.information(
                    self,
                    self.i18n_factory.translate("message.success", default="Success"),
                    self.i18n_factory.translate(
                        "config.message.panel_added",
                        default="Panel '{name}' ({area}) added and saved!",
                        name=panel_name,
                        area=panel_area,
                    ),
                )
            else:
                QMessageBox.warning(
                    self,
                    self.i18n_factory.translate("message.error", default="Error"),
                    self.i18n_factory.translate(
                        "config.error.save_panel_failed",
                        default="Failed to save panel to configuration file",
                    ),
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n_factory.translate("message.error", default="Error"),
                self.i18n_factory.translate(
                    "config.error.add_panel_failed",
                    default="Failed to add panel: {error}",
                    error=str(e),
                ),
            )
