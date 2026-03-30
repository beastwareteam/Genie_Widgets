
"""Visual Layer - Comprehensive UI viewers for all structural components."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QTextEdit,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.list_factory import ListFactory, ListItem
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.factories.theme_factory import ThemeFactory



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
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory
        self.viewer_config = config or ViewerConfig()
        self.list_factory = ListFactory(self.config_path)
        self.theme_factory = ThemeFactory(self.config_path)
        self.theme_colors: dict[str, Any] = self._get_theme_colors()
        self._setup_ui()
        self._load_lists()

    def _get_theme_colors(self) -> dict[str, Any]:
        themes = self.theme_factory.list_themes()
        if themes:
            return themes[0].colors or {}
        return {}

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        margin = int(self.theme_colors.get("header_padding", 8))
        layout.setContentsMargins(margin, margin, margin, margin)

        header = QLabel(self.i18n_factory.translate("visual.lists.title", default="Listen"))
        header_font = QFont()
        header_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
        header_font.setPointSize(int(self.theme_colors.get("header_font_size", 12)))
        header.setFont(header_font)
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(
            self.i18n_factory.translate("visual.lists.tree", default="Listen-Hierarchie")
        )
        self.tree.setMinimumWidth(int(self.theme_colors.get("tree_min_width", 300)))
        splitter.addWidget(self.tree)

        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QVBoxLayout(props_widget)

            props_title = QLabel("Eigenschaften")
            props_title_font = QFont()
            props_title_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
            props_title.setFont(props_title_font)
            props_layout.addWidget(props_title)

            self.properties_text = QTextEdit()
            self.properties_text.setReadOnly(True)
            self.properties_text.setMaximumWidth(int(self.theme_colors.get("properties_panel_max_width", 300)))
            props_layout.addWidget(self.properties_text)
            props_layout.addStretch()

            splitter.addWidget(props_widget)
            self.tree.itemSelectionChanged.connect(self._on_item_selected)

        layout.addWidget(splitter)

    def _load_lists(self) -> None:
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
            error_item.setText(0, f"❌ Fehler: {e}")

    def _add_items_recursive(
        self,
        parent: QTreeWidgetItem,
        items: list[ListItem],
        depth: int,
    ) -> None:
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
        selected = self.tree.selectedItems()
        if not selected:
            self.properties_text.clear()
            return
        item = selected[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)
        self.properties_text.setText(str(data))

# ...existing code for MenusViewer, VisualDashboard, etc. (ensure only one definition each, with type hints)...


class MenusViewer(QWidget):
    """Viewer for menu structure with full hierarchy."""
    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
        config: ViewerConfig | None = None,
    ) -> None:
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory
        self.viewer_config = config or ViewerConfig()
        self.menu_factory = MenuFactory(self.config_path)
        self.theme_factory = ThemeFactory(self.config_path)
        self.theme_colors: dict[str, Any] = self._get_theme_colors()
        self._setup_ui()
        self._load_menus()

    def _get_theme_colors(self) -> dict[str, Any]:
        themes = self.theme_factory.list_themes()
        if themes:
            return themes[0].colors or {}
        return {}

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        margin = int(self.theme_colors.get("header_padding", 8))
        layout.setContentsMargins(margin, margin, margin, margin)

        header = QLabel(self.i18n_factory.translate("visual.menus.title", default="Menüs"))
        header_font = QFont()
        header_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
        header_font.setPointSize(int(self.theme_colors.get("header_font_size", 12)))
        header.setFont(header_font)
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(
            self.i18n_factory.translate("visual.menus.tree", default="Menü-Struktur")
        )
        self.tree.setMinimumWidth(int(self.theme_colors.get("tree_min_width", 300)))
        splitter.addWidget(self.tree)

        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QVBoxLayout(props_widget)

            props_title = QLabel("Eigenschaften")
            props_title_font = QFont()
            props_title_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
            props_title.setFont(props_title_font)
            props_layout.addWidget(props_title)

            self.properties_text = QTextEdit()
            self.properties_text.setReadOnly(True)
            self.properties_text.setMaximumWidth(int(self.theme_colors.get("properties_panel_max_width", 300)))
            props_layout.addWidget(self.properties_text)
            props_layout.addStretch()

            splitter.addWidget(props_widget)
            self.tree.itemSelectionChanged.connect(self._on_item_selected)

        layout.addWidget(splitter)

    def _load_menus(self) -> None:
        try:
            menus = self.menu_factory.load_menus()
            for menu in menus:
                self._add_menu_item(self.tree, menu)
            self.tree.expandAll()
        except Exception as e:
            error_item = QTreeWidgetItem(self.tree)
            error_item.setText(0, f"❌ Fehler: {e}")

    def _add_menu_item(
        self,
        parent: QTreeWidget | QTreeWidgetItem,
        menu: MenuItem,
        depth: int = 0,
    ) -> None:
        if depth >= self.viewer_config.max_depth:
            return
        item = QTreeWidgetItem(parent)
        text = self.i18n_factory.translate(menu.label_key, default=menu.id)
        item.setText(0, text)
        item.setData(0, Qt.ItemDataRole.UserRole, ("menu", menu.id))
        if menu.children:
            for child in menu.children:
                self._add_menu_item(item, child, depth + 1)

    def _on_item_selected(self) -> None:
        selected = self.tree.selectedItems()
        if not selected:
            self.properties_text.clear()
            return
        item = selected[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)
        self.properties_text.setText(str(data))




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
        self.setWindowTitle(
            self.i18n_factory.translate("visual.dashboard.title", default="Visuelles Dashboard"),
        )
        self.setMinimumSize(1400, 900)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        tabs = QTabWidget()

        # Lists tab
        lists_viewer = ListsViewer(self.config_path, self.i18n_factory)
        tabs.addTab(
            lists_viewer,
            self.i18n_factory.translate("visual.tab.lists", default="Listen"),
        )

        # Menus tab
        menus_viewer = MenusViewer(self.config_path, self.i18n_factory)
        tabs.addTab(
            menus_viewer,
            self.i18n_factory.translate("visual.tab.menus", default="Menüs"),
        )



        layout.addWidget(tabs)
