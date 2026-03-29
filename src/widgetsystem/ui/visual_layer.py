"""Visual Layer - Comprehensive UI viewers for all structural components."""

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


@dataclass
class ViewerConfig:
    """Configuration for viewers."""

    show_properties: bool = True
    show_icons: bool = True
    editable: bool = False
    max_depth: int = 10



from widgetsystem.factories.theme_factory import ThemeFactory

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
        self.theme_factory = ThemeFactory(self.config_path)
        self.theme_colors = self._get_theme_colors()
        self._setup_ui()
        self._load_lists()

    def _get_theme_colors(self) -> dict:
        themes = self.theme_factory.list_themes()
        if themes:
            return themes[0].colors or {}
        return {}

    def _setup_ui(self) -> None:
        """Setup UI with tree and properties."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.theme_factory = ThemeFactory(self.config_path)
        self.theme_colors = self._get_theme_colors()
        self._setup_ui()
        header = QLabel(self.i18n_factory.translate("visual.lists.title", default="Listen"))
        header_font = QFont()
    def _get_theme_colors(self) -> dict:
        themes = self.theme_factory.list_themes()
        if themes:
            return themes[0].colors or {}
        return {}
        header_font.setBold(True)
        header_font.setPointSize(12)
        header.setFont(header_font)
        layout.addWidget(header)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tree view
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(
            self.i18n_factory.translate("visual.lists.tree", default="Listen-Hierarchie"),
        )
        self.tree.setMinimumWidth(300)
        splitter.addWidget(self.tree)

        # Properties panel
        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QVBoxLayout(props_widget)

            props_title = QLabel("Eigenschaften")
            props_title_font = QFont()
            props_title_font.setBold(True)
            props_title.setFont(props_title_font)
            props_layout.addWidget(props_title)

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
            error_item.setText(0, f"❌ Fehler: {e}")

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

    def _setup_ui(self) -> None:
        """Setup UI with tree and properties."""
        layout = QVBoxLayout(self)
        margin = int(self.theme_colors.get("header_padding", 8))
        layout.setContentsMargins(margin, margin, margin, margin)

        # Header
        header = QLabel(self.i18n_factory.translate("visual.lists.title", default="Listen"))
        header_font = QFont()
        header_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
        header_font.setPointSize(int(self.theme_colors.get("header_font_size", 12)))
        header.setFont(header_font)
        layout.addWidget(header)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tree view
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(
            self.i18n_factory.translate("visual.lists.tree", default="Listen-Hierarchie"),
        )
        self.tree.setMinimumWidth(int(self.theme_colors.get("tree_min_width", 300)))
        splitter.addWidget(self.tree)

        # Properties panel
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

        layout.addWidget(splitter)


# Restore MenusViewer class definition
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
        self.theme_factory = ThemeFactory(self.config_path)
        self.theme_colors = self._get_theme_colors()
        self._setup_ui()
        self._load_menus()

    def _get_theme_colors(self) -> dict:
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
            self.i18n_factory.translate("visual.menus.tree", default="Menü-Struktur"),
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
        """Load menus from factory."""
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
            text = f"<b>Typ:</b> {item_type}<br><b>ID:</b> {item_id}"
            self.properties_text.setHtml(text)

    def refresh(self) -> None:
        """Refresh the viewer."""
        self.tree.clear()
        self._load_menus()

    def _load_menus(self) -> None:
        """Load menus from factory."""
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
            text = f"<b>Typ:</b> {item_type}<br><b>ID:</b> {item_id}"
            self.properties_text.setHtml(text)

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
        self.theme_factory = ThemeFactory(self.config_path)
        self.theme_colors = self._get_theme_colors()
        self._setup_ui()
        self._load_tabs()

    def _get_theme_colors(self) -> dict:
        themes = self.theme_factory.list_themes()
        if themes:
            return themes[0].colors or {}
        return {}
    def _setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        margin = int(self.theme_colors.get("header_padding", 8))
        layout.setContentsMargins(margin, margin, margin, margin)

        header = QLabel(self.i18n_factory.translate("visual.tabs.title", default="Tabs"))
        header_font = QFont()
        header_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
        header_font.setPointSize(int(self.theme_colors.get("header_font_size", 12)))
        header.setFont(header_font)
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(
            self.i18n_factory.translate("visual.tabs.tree", default="Tab-Gruppen"),
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
            error_item.setText(0, f"❌ Fehler: {e}")

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
            text = f"<b>Typ:</b> {item_type}<br><b>ID:</b> {item_id}"
            self.properties_text.setHtml(text)

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
        self.theme_factory = ThemeFactory(self.config_path)
        self.theme_colors = self._get_theme_colors()
        self._setup_ui()
        self._load_panels()

    def _get_theme_colors(self) -> dict:
        themes = self.theme_factory.list_themes()
        if themes:
            return themes[0].colors or {}
        return {}
    def _setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        margin = int(self.theme_colors.get("header_padding", 8))
        layout.setContentsMargins(margin, margin, margin, margin)

        header = QLabel(self.i18n_factory.translate("visual.panels.title", default="Panels"))
        header_font = QFont()
        header_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
        header_font.setPointSize(int(self.theme_colors.get("header_font_size", 12)))
        header.setFont(header_font)
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(int(self.theme_colors.get("list_min_width", 300)))
        splitter.addWidget(self.list_widget)

        if self.viewer_config.show_properties:
            props_widget = QWidget()
            props_layout = QFormLayout(props_widget)

            props_title = QLabel("Panel-Eigenschaften")
            props_title_font = QFont()
            props_title_font.setBold(bool(self.theme_colors.get("header_font_bold", True)))
            props_title.setFont(props_title_font)
            props_layout.addRow(props_title)

            props_layout.addRow("ID:", QLabel(""))
            props_layout.addRow("Name:", QLabel(""))
            props_layout.addRow("Area:", QLabel(""))
            props_layout.addRow("Beschreibung:", QLabel(""))

            props_widget.setMaximumWidth(int(self.theme_colors.get("properties_panel_max_width", 300)))
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
            error_item = QListWidgetItem(f"❌ Fehler: {e}")
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
                logger.debug(f"Selected panel: {panel_id}")
        except Exception:
            pass

    def refresh(self) -> None:
        """Refresh the viewer."""
        self.list_widget.clear()
        self._load_panels()


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

        # Tabs tab
        tabs_viewer = TabsViewer(self.config_path, self.i18n_factory)
        tabs.addTab(
            tabs_viewer,
            self.i18n_factory.translate("visual.tab.tabs", default="Tabs"),
        )

        # Panels tab
        panels_viewer = PanelsViewer(self.config_path, self.i18n_factory)
        tabs.addTab(
            panels_viewer,
            self.i18n_factory.translate("visual.tab.panels", default="Panels"),
        )

        layout.addWidget(tabs)
