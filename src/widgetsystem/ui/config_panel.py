"""Configuration Panel - Dynamic UI configuration interface for all structural elements."""

from pathlib import Path

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
from widgetsystem.factories.panel_factory import PanelFactory
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

        # Load all configuration pages
        try:
            categories = self.ui_config_factory.get_all_categories()

            for category in sorted(categories):
                pages = self.ui_config_factory.get_pages_by_category(category)
                if pages:
                    # Create tab for each category
                    category_widget = self._create_category_widget(category)
                    tab_title = self.i18n_factory.translate(
                        f"config.{category}.title",
                        default=category.title(),
                    )
                    self.config_tabs.addTab(category_widget, tab_title)

        except Exception as e:
            error_label = QLabel(f"Error loading configuration: {e}")
            self.config_tabs.addTab(error_label, "Error")

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
            layout.addWidget(QLabel(f"Configuration for {category}"))

        layout.addStretch()
        return widget

    def _setup_menus_editor(self, parent_layout: QVBoxLayout) -> None:
        """Setup menu editor interface."""
        title = QLabel(
            self.i18n_factory.translate("config.menu_editor.label", default="Menu Editor"),
        )
        # Style wird jetzt über Theme/Config gesetzt
        parent_layout.addWidget(title)

        # Splitter for menu tree and properties
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Menu tree on the left
        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderLabel("Menus")
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
        menu_shortcut_input.setPlaceholderText("Ctrl+M")
        props_layout.addRow(
            self.i18n_factory.translate("config.menu_shortcut", default="Shortcut:"),
            menu_shortcut_input,
        )

        add_menu_btn = QPushButton(self.i18n_factory.translate("button.add", default="Add Menu"))
        add_menu_btn.clicked.connect(lambda: self._on_add_menu(menu_name_input.text()))
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
        # Style wird jetzt über Theme/Config gesetzt
        parent_layout.addWidget(title)

        # Splitter for list tree and properties
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # List tree on the left
        self.list_tree = QTreeWidget()
        self.list_tree.setHeaderLabel("Lists")
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
        list_type_combo.addItems(["vertical", "horizontal", "tree", "table"])
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
        add_list_btn.clicked.connect(
            lambda: self._on_add_list(list_name_input.text(), list_type_combo.currentText()),
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
        except Exception:
            pass

    def _setup_tabs_editor(self, parent_layout: QVBoxLayout) -> None:
        """Setup tab editor interface."""
        title = QLabel(self.i18n_factory.translate("config.tab_editor.label", default="Tab Editor"))
        # Style wird jetzt über Theme/Config gesetzt
        parent_layout.addWidget(title)

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
        self.tabs_tree.setHeaderLabel("Tab Groups")
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
        add_tab_btn.clicked.connect(lambda: self._on_add_tab(tab_name_input.text()))
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
        # Style wird jetzt über Theme/Config gesetzt
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
        panel_area_combo.addItems(["left", "right", "bottom", "center"])
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
        add_panel_btn.clicked.connect(
            lambda: self._on_add_panel(panel_name_input.text(), panel_area_combo.currentText()),
        )
        props_layout.addRow(add_panel_btn)

        parent_layout.addWidget(properties_widget)

    def _setup_theme_selector(self, parent_layout: QVBoxLayout) -> None:
        """Setup theme selector interface."""
        title = QLabel(
            self.i18n_factory.translate("config.theme_selector.label", default="Theme Selection"),
        )
        # Style wird jetzt über Theme/Config gesetzt
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
        apply_btn.clicked.connect(lambda: self.config_changed.emit("theme"))
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
            QMessageBox.warning(self, "Warning", "Please enter a menu name")
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
                QMessageBox.information(self, "Success", f"Menu '{menu_name}' added and saved!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save menu to configuration file")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add menu: {e}")

    def _on_add_list(self, list_name: str, list_type: str) -> None:
        """Add a new list from input."""
        if not list_name:
            QMessageBox.warning(self, "Warning", "Please enter a list name")
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
                    "Success",
                    f"List '{list_name}' ({list_type}) added and saved!",
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to save list to configuration file")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add list: {e}")

    def _on_add_tab(self, tab_name: str) -> None:
        """Add a new tab from input."""
        if not tab_name:
            QMessageBox.warning(self, "Warning", "Please enter a tab name")
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
                QMessageBox.information(self, "Success", f"Tab '{tab_name}' added and saved!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save tab to configuration file")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add tab: {e}")

    def _on_add_panel(self, panel_name: str, panel_area: str) -> None:
        """Add a new panel from input."""
        if not panel_name:
            QMessageBox.warning(self, "Warning", "Please enter a panel name")
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
                self._refresh_panels_tree()
                self.config_changed.emit("panels")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Panel '{panel_name}' ({panel_area}) added and saved!",
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to save panel to configuration file")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add panel: {e}")
