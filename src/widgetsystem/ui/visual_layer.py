"""Visual Layer - Comprehensive UI viewers for all structural components."""

import logging
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.list_factory import ListFactory, ListItem
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.factories.panel_factory import PanelFactory
from widgetsystem.factories.tabs_factory import TabsFactory

logger = logging.getLogger(__name__)


@dataclass
class ViewerConfig:
    """Configuration for viewers."""

    show_properties: bool = True
    show_icons: bool = True
    editable: bool = False
    max_depth: int = 10


class ListsViewer(QWidget):
    """Viewer for list groups and items with full hierarchy visualization."""

    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
        config: ViewerConfig | None = None,
    ) -> None:
        """Initialize lists viewer."""
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory
        self.viewer_config = config or ViewerConfig()
        self.list_factory = ListFactory(self.config_path)
        self._setup_ui()
        self._load_lists()

    def _setup_ui(self) -> None:
        """Setup UI with tree and properties."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        self._header = QLabel(self._translate("visual.lists.title", "Listen"))
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        self._header.setFont(header_font)
        layout.addWidget(self._header)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tree view
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(self._translate("visual.lists.tree", "Listen-Hierarchie"))
        self.tree.setMinimumWidth(300)
        splitter.addWidget(self.tree)

        # Properties panel
        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QVBoxLayout(props_widget)

            self._props_title = QLabel(self._translate("visual.properties.title", "Eigenschaften"))
            props_title_font = QFont()
            props_title_font.setBold(True)
            self._props_title.setFont(props_title_font)
            props_layout.addWidget(self._props_title)

            self.properties_text = QTextEdit()
            self.properties_text.setReadOnly(True)
            self.properties_text.setMaximumWidth(300)
            props_layout.addWidget(self.properties_text)
            props_layout.addStretch()

            splitter.addWidget(props_widget)

            # Connect selection
            self.tree.itemSelectionChanged.connect(self._on_item_selected)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def _load_lists(self) -> None:
        """Load lists from factory and populate tree."""
        try:
            list_groups = self.list_factory.load_list_groups()
            for group in list_groups:
                group_item = QTreeWidgetItem(self.tree)
                group_item.setText(
                    0,
                    self.i18n_factory.translate(group.title_key, default=group.id),
                )
                group_item.setData(0, Qt.ItemDataRole.UserRole, ("group", group.id))
                self._add_items_recursive(group_item, group.items, 0)

            self.tree.expandAll()
        except Exception as e:
            error_item = QTreeWidgetItem(self.tree)
            error_item.setText(
                0,
                self._translate("visual.error.label", "❌ Fehler: {error}").format(error=e),
            )

    def _add_items_recursive(
        self,
        parent: QTreeWidgetItem,
        items: list[ListItem],
        depth: int,
    ) -> None:
        """Recursively add items to tree."""
        if depth >= self.viewer_config.max_depth:
            return

        for item in items:
            child_item = QTreeWidgetItem(parent)
            text = self.i18n_factory.translate(item.label_key, default=item.id)
            if item.content:
                text += f" ({item.content})"
            child_item.setText(0, text)
            child_item.setData(0, Qt.ItemDataRole.UserRole, ("item", item.id))

            if item.children:
                self._add_items_recursive(child_item, item.children, depth + 1)

    def _on_item_selected(self) -> None:
        """Update properties panel when tree item selected."""
        if not self.viewer_config.show_properties:
            return

        items = self.tree.selectedItems()
        if not items:
            self.properties_text.clear()
            return

        selected_item = items[0]
        data = selected_item.data(0, Qt.ItemDataRole.UserRole)

        if data and isinstance(data, tuple):
            item_type, item_id = data
            text = (
                f"<b>{self._translate('visual.properties.type', 'Typ')}:</b> {item_type}"
                f"<br><b>{self._translate('visual.properties.id', 'ID')}:</b> {item_id}"
            )
            self.properties_text.setHtml(text)

    def _translate(self, key: str, default: str) -> str:
        """Translate helper with fallback."""
        return self.i18n_factory.translate(key, default=default)

    def set_i18n_factory(self, i18n_factory: I18nFactory) -> None:
        """Set i18n factory and refresh UI texts."""
        self.i18n_factory = i18n_factory
        self._header.setText(self._translate("visual.lists.title", "Listen"))
        self.tree.setHeaderLabel(self._translate("visual.lists.tree", "Listen-Hierarchie"))
        if hasattr(self, "_props_title"):
            self._props_title.setText(self._translate("visual.properties.title", "Eigenschaften"))
        self.refresh()

    def refresh(self) -> None:
        """Refresh the viewer."""
        self.tree.clear()
        self._load_lists()


class MenusViewer(QWidget):
    """Viewer for menu structure with full hierarchy."""

    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
        config: ViewerConfig | None = None,
    ) -> None:
        """Initialize menus viewer."""
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory
        self.viewer_config = config or ViewerConfig()
        self.menu_factory = MenuFactory(self.config_path)
        self._setup_ui()
        self._load_menus()

    def _setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._header = QLabel(self._translate("visual.menus.title", "Menüs"))
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        self._header.setFont(header_font)
        layout.addWidget(self._header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(self._translate("visual.menus.tree", "Menü-Struktur"))
        self.tree.setMinimumWidth(300)
        splitter.addWidget(self.tree)

        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QVBoxLayout(props_widget)

            self._props_title = QLabel(self._translate("visual.properties.title", "Eigenschaften"))
            props_title_font = QFont()
            props_title_font.setBold(True)
            self._props_title.setFont(props_title_font)
            props_layout.addWidget(self._props_title)

            self.properties_text = QTextEdit()
            self.properties_text.setReadOnly(True)
            self.properties_text.setMaximumWidth(300)
            props_layout.addWidget(self.properties_text)
            props_layout.addStretch()

            splitter.addWidget(props_widget)
            self.tree.itemSelectionChanged.connect(self._on_item_selected)

        layout.addWidget(splitter)

    def _load_menus(self) -> None:
        """Load menus from factory."""
        try:
            menus = self.menu_factory.load_menus()
            for menu in menus:
                self._add_menu_item(self.tree, menu)
            self.tree.expandAll()
        except Exception as e:
            error_item = QTreeWidgetItem(self.tree)
            error_item.setText(
                0,
                self._translate("visual.error.label", "❌ Fehler: {error}").format(error=e),
            )

    def _add_menu_item(
        self,
        parent: QTreeWidget | QTreeWidgetItem,
        menu: MenuItem,
        depth: int = 0,
    ) -> None:
        """Recursively add menu items to tree."""
        if depth >= self.viewer_config.max_depth:
            return

        item = QTreeWidgetItem(parent)
        label = self.i18n_factory.translate(menu.label_key, default=menu.id)
        menu_type = getattr(menu, "menu_type", None)
        text = f"{label} [{menu_type}]" if menu_type else label
        item.setText(0, text)
        item.setData(0, Qt.ItemDataRole.UserRole, ("menu", menu.id))

        for child in menu.children:
            self._add_menu_item(item, child, depth + 1)

    def _on_item_selected(self) -> None:
        """Update properties panel."""
        if not self.viewer_config.show_properties:
            return

        items = self.tree.selectedItems()
        if not items:
            self.properties_text.clear()
            return

        selected_item = items[0]
        data = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if data and isinstance(data, tuple):
            item_type, item_id = data
            text = (
                f"<b>{self._translate('visual.properties.type', 'Typ')}:</b> {item_type}"
                f"<br><b>{self._translate('visual.properties.id', 'ID')}:</b> {item_id}"
            )
            self.properties_text.setHtml(text)

    def _translate(self, key: str, default: str) -> str:
        """Translate helper with fallback."""
        return self.i18n_factory.translate(key, default=default)

    def set_i18n_factory(self, i18n_factory: I18nFactory) -> None:
        """Set i18n factory and refresh UI texts."""
        self.i18n_factory = i18n_factory
        self._header.setText(self._translate("visual.menus.title", "Menüs"))
        self.tree.setHeaderLabel(self._translate("visual.menus.tree", "Menü-Struktur"))
        if hasattr(self, "_props_title"):
            self._props_title.setText(self._translate("visual.properties.title", "Eigenschaften"))
        self.refresh()

    def refresh(self) -> None:
        """Refresh the viewer."""
        self.tree.clear()
        self._load_menus()


class TabsViewer(QWidget):
    """Viewer for tab groups and tabs."""

    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
        config: ViewerConfig | None = None,
    ) -> None:
        """Initialize tabs viewer."""
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory
        self.viewer_config = config or ViewerConfig()
        self.tabs_factory = TabsFactory(self.config_path)
        self._setup_ui()
        self._load_tabs()

    def _setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._header = QLabel(self._translate("visual.tabs.title", "Tabs"))
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        self._header.setFont(header_font)
        layout.addWidget(self._header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(self._translate("visual.tabs.tree", "Tab-Gruppen"))
        self.tree.setMinimumWidth(300)
        splitter.addWidget(self.tree)

        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QVBoxLayout(props_widget)

            self._props_title = QLabel(self._translate("visual.properties.title", "Eigenschaften"))
            props_title_font = QFont()
            props_title_font.setBold(True)
            self._props_title.setFont(props_title_font)
            props_layout.addWidget(self._props_title)

            self.properties_text = QTextEdit()
            self.properties_text.setReadOnly(True)
            self.properties_text.setMaximumWidth(300)
            props_layout.addWidget(self.properties_text)
            props_layout.addStretch()

            splitter.addWidget(props_widget)
            self.tree.itemSelectionChanged.connect(self._on_item_selected)

        layout.addWidget(splitter)

    def _load_tabs(self) -> None:
        """Load tabs from factory."""
        try:
            tab_groups = self.tabs_factory.load_tab_groups()
            for group in tab_groups:
                group_item = QTreeWidgetItem(self.tree)
                group_item.setText(
                    0,
                    self.i18n_factory.translate(group.title_key, default=group.id),
                )
                group_item.setData(0, Qt.ItemDataRole.UserRole, ("group", group.id))

                for tab in group.tabs:
                    tab_item = QTreeWidgetItem(group_item)
                    tab_item.setText(
                        0,
                        self.i18n_factory.translate(tab.title_key, default=tab.id),
                    )
                    tab_item.setData(0, Qt.ItemDataRole.UserRole, ("tab", tab.id))

            self.tree.expandAll()
        except Exception as e:
            error_item = QTreeWidgetItem(self.tree)
            error_item.setText(
                0,
                self._translate("visual.error.label", "❌ Fehler: {error}").format(error=e),
            )

    def _on_item_selected(self) -> None:
        """Update properties panel."""
        if not self.viewer_config.show_properties:
            return

        items = self.tree.selectedItems()
        if not items:
            self.properties_text.clear()
            return

        selected_item = items[0]
        data = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if data and isinstance(data, tuple):
            item_type, item_id = data
            text = (
                f"<b>{self._translate('visual.properties.type', 'Typ')}:</b> {item_type}"
                f"<br><b>{self._translate('visual.properties.id', 'ID')}:</b> {item_id}"
            )
            self.properties_text.setHtml(text)

    def _translate(self, key: str, default: str) -> str:
        """Translate helper with fallback."""
        return self.i18n_factory.translate(key, default=default)

    def set_i18n_factory(self, i18n_factory: I18nFactory) -> None:
        """Set i18n factory and refresh UI texts."""
        self.i18n_factory = i18n_factory
        self._header.setText(self._translate("visual.tabs.title", "Tabs"))
        self.tree.setHeaderLabel(self._translate("visual.tabs.tree", "Tab-Gruppen"))
        if hasattr(self, "_props_title"):
            self._props_title.setText(self._translate("visual.properties.title", "Eigenschaften"))
        self.refresh()

    def refresh(self) -> None:
        """Refresh the viewer."""
        self.tree.clear()
        self._load_tabs()


class PanelsViewer(QWidget):
    """Viewer for panel configurations."""

    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
        config: ViewerConfig | None = None,
    ) -> None:
        """Initialize panels viewer."""
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory
        self.viewer_config = config or ViewerConfig()
        self.panel_factory = PanelFactory(self.config_path)
        self._setup_ui()
        self._load_panels()

    def _setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._header = QLabel(self._translate("visual.panels.title", "Panels"))
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        self._header.setFont(header_font)
        layout.addWidget(self._header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(300)
        splitter.addWidget(self.list_widget)

        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QFormLayout(props_widget)

            self._props_title = QLabel(
                self._translate("visual.panels.properties.title", "Panel-Eigenschaften"),
            )
            props_title_font = QFont()
            props_title_font.setBold(True)
            self._props_title.setFont(props_title_font)
            props_layout.addRow(self._props_title)

            self._id_label = QLabel("")
            self._name_label = QLabel("")
            self._area_label = QLabel("")
            self._description_label = QLabel("")

            self._id_field_label = QLabel(self._translate("visual.properties.id", "ID") + ":")
            self._name_field_label = QLabel(
                self._translate("visual.panels.field.name", "Name") + ":",
            )
            self._area_field_label = QLabel(
                self._translate("visual.panels.field.area", "Area") + ":",
            )
            self._description_field_label = QLabel(
                self._translate("visual.panels.field.description", "Beschreibung") + ":",
            )

            props_layout.addRow(self._id_field_label, self._id_label)
            props_layout.addRow(
                self._name_field_label,
                self._name_label,
            )
            props_layout.addRow(
                self._area_field_label,
                self._area_label,
            )
            props_layout.addRow(
                self._description_field_label,
                self._description_label,
            )

            props_widget.setMaximumWidth(300)
            splitter.addWidget(props_widget)

            self.list_widget.itemSelectionChanged.connect(self._on_item_selected)

        layout.addWidget(splitter)

    def _load_panels(self) -> None:
        """Load panels from factory."""
        try:
            panels = self.panel_factory.load_panels()
            for panel in panels:
                panel_name_key = getattr(panel, "name_key", "title_key")
                panel_name = self.i18n_factory.translate(panel_name_key, default=panel.id)
                item = QListWidgetItem(panel_name)
                item.setData(Qt.ItemDataRole.UserRole, panel.id)
                self.list_widget.addItem(item)
        except Exception as e:
            error_item = QListWidgetItem(
                self._translate("visual.error.label", "❌ Fehler: {error}").format(error=e),
            )
            self.list_widget.addItem(error_item)

    def _on_item_selected(self) -> None:
        """Update properties panel."""
        items = self.list_widget.selectedItems()
        if not items:
            return

        item = items[0]
        panel_id = item.data(Qt.ItemDataRole.UserRole)

        try:
            panel = self.panel_factory.get_panel(panel_id)
            if panel:
                # Update properties (simplified)
                logger.debug("Selected panel: %s", panel_id)
        except Exception:
            pass

    def refresh(self) -> None:
        """Refresh the viewer."""
        self.list_widget.clear()
        self._load_panels()

    def _translate(self, key: str, default: str) -> str:
        """Translate helper with fallback."""
        return self.i18n_factory.translate(key, default=default)

    def set_i18n_factory(self, i18n_factory: I18nFactory) -> None:
        """Set i18n factory and refresh UI texts."""
        self.i18n_factory = i18n_factory
        self._header.setText(self._translate("visual.panels.title", "Panels"))
        if hasattr(self, "_props_title"):
            self._props_title.setText(
                self._translate("visual.panels.properties.title", "Panel-Eigenschaften"),
            )
            self._id_field_label.setText(self._translate("visual.properties.id", "ID") + ":")
            self._name_field_label.setText(
                self._translate("visual.panels.field.name", "Name") + ":",
            )
            self._area_field_label.setText(
                self._translate("visual.panels.field.area", "Area") + ":",
            )
            self._description_field_label.setText(
                self._translate("visual.panels.field.description", "Beschreibung") + ":",
            )
        self.refresh()


class VisualDashboard(QWidget):
    """Complete dashboard showing all structural elements."""

    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize dashboard."""
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory
        self.setWindowTitle(self._translate("visual.dashboard.title", "Visuelles Dashboard"))
        self.setMinimumSize(1400, 900)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Lists tab
        self.lists_viewer = ListsViewer(self.config_path, self.i18n_factory)
        self.tabs.addTab(
            self.lists_viewer,
            self._translate("visual.tab.lists", "Listen"),
        )

        # Menus tab
        self.menus_viewer = MenusViewer(self.config_path, self.i18n_factory)
        self.tabs.addTab(
            self.menus_viewer,
            self._translate("visual.tab.menus", "Menüs"),
        )

        # Tabs tab
        self.tabs_viewer = TabsViewer(self.config_path, self.i18n_factory)
        self.tabs.addTab(
            self.tabs_viewer,
            self._translate("visual.tab.tabs", "Tabs"),
        )

        # Panels tab
        self.panels_viewer = PanelsViewer(self.config_path, self.i18n_factory)
        self.tabs.addTab(
            self.panels_viewer,
            self._translate("visual.tab.panels", "Panels"),
        )

        layout.addWidget(self.tabs)

    def _translate(self, key: str, default: str) -> str:
        """Translate helper with fallback."""
        return self.i18n_factory.translate(key, default=default)

    def set_i18n_factory(self, i18n_factory: I18nFactory) -> None:
        """Set i18n factory and refresh all dashboard texts."""
        self.i18n_factory = i18n_factory
        self.setWindowTitle(self._translate("visual.dashboard.title", "Visuelles Dashboard"))

        self.lists_viewer.set_i18n_factory(i18n_factory)
        self.menus_viewer.set_i18n_factory(i18n_factory)
        self.tabs_viewer.set_i18n_factory(i18n_factory)
        self.panels_viewer.set_i18n_factory(i18n_factory)

        self.tabs.setTabText(0, self._translate("visual.tab.lists", "Listen"))
        self.tabs.setTabText(1, self._translate("visual.tab.menus", "Menüs"))
        self.tabs.setTabText(2, self._translate("visual.tab.tabs", "Tabs"))
        self.tabs.setTabText(3, self._translate("visual.tab.panels", "Panels"))
