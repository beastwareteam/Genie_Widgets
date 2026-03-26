"""Widget Features Editor for runtime configuration editing.

Provides UI for editing widget-specific features like:
- Panel names and properties
- Tab configurations
- Menu items customization
- Widget positioning and visibility
"""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


class WidgetPropertyEditor(QWidget):
    """Editor for widget properties with persistence.

    Signals:
        propertyChanged: Emitted when property changes (widget_id, property_name, value)
        saved: Emitted when changes are saved to file
    """

    propertyChanged = Signal(str, str, str)
    saved = Signal(str)

    def __init__(
        self,
        config_path: Path,
        parent: QWidget | None = None,
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize Widget Property Editor.

        Args:
            config_path: Path to configuration directory
            parent: Parent widget
            i18n_factory: Optional i18n factory for UI text translation
        """
        super().__init__(parent)
        self.config_path = config_path
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        self.current_widget: dict[str, Any] | None = None
        self.widget_configs: dict[str, dict[str, Any]] = {}
        self._load_configs()
        self._setup_ui()
        logger.debug(f"WidgetPropertyEditor initialized with config path: {config_path}")

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory and refresh visible texts."""
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()
        self._apply_translated_texts()

    def _translate(self, key: str, default: str | None = None, **kwargs: object) -> str:
        """Translate key with fallback and interpolation."""
        if not self._i18n_factory or not key:
            text = default or key
            return text.format(**kwargs) if kwargs else text

        cache_key = f"{key}|{sorted(kwargs.items())}" if kwargs else key
        if cache_key in self._translated_cache:
            return self._translated_cache[cache_key]

        translated = self._i18n_factory.translate(key, default=default or key, **kwargs)
        self._translated_cache[cache_key] = translated
        return translated

    def _setup_ui(self) -> None:
        """Set up user interface."""
        layout = QVBoxLayout(self)

        # Main splitter for tree and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Widget tree
        tree_group = self._create_widget_tree_group()
        splitter.addWidget(tree_group)

        # Right: Property editor
        editor_group = self._create_property_editor_group()
        splitter.addWidget(editor_group)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter)

        # Bottom: Action buttons
        button_layout = QHBoxLayout()

        self._save_btn = QPushButton(
            self._translate("widget_features.button.save", "Save Changes"),
        )
        self._save_btn.clicked.connect(self._save_changes)
        button_layout.addWidget(self._save_btn)

        self._reset_btn = QPushButton(
            self._translate("widget_features.button.reload", "Reload Config"),
        )
        self._reset_btn.clicked.connect(self._reload_config)
        button_layout.addWidget(self._reset_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_widget_tree_group(self) -> QGroupBox:
        """Create widget tree view group.

        Returns:
            Configured QGroupBox with tree widget
        """
        group = QGroupBox(self._translate("widget_features.group.widgets", "Widgets"))
        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(
            self._translate("widget_features.tree.header", "Widget Hierarchy"),
        )
        self.tree.itemSelectionChanged.connect(self._on_tree_selection_changed)
        layout.addWidget(self.tree)

        group.setLayout(layout)
        self._tree_group = group
        return group

    def _create_property_editor_group(self) -> QGroupBox:
        """Create property editor group.

        Returns:
            Configured QGroupBox with property table
        """
        group = QGroupBox(self._translate("widget_features.group.properties", "Properties"))
        layout = QVBoxLayout()

        self.property_table = QTableWidget()
        self.property_table.setColumnCount(2)
        self.property_table.setHorizontalHeaderLabels(
            [
                self._translate("widget_features.table.property", "Property"),
                self._translate("widget_features.table.value", "Value"),
            ],
        )
        self.property_table.setColumnWidth(0, 150)
        self.property_table.setColumnWidth(1, 250)
        layout.addWidget(self.property_table)

        group.setLayout(layout)
        self._properties_group = group
        return group

    def _apply_translated_texts(self) -> None:
        """Refresh translated static texts."""
        self._save_btn.setText(self._translate("widget_features.button.save", "Save Changes"))
        self._reset_btn.setText(self._translate("widget_features.button.reload", "Reload Config"))
        self._tree_group.setTitle(self._translate("widget_features.group.widgets", "Widgets"))
        self.tree.setHeaderLabel(self._translate("widget_features.tree.header", "Widget Hierarchy"))
        self._properties_group.setTitle(
            self._translate("widget_features.group.properties", "Properties"),
        )
        self.property_table.setHorizontalHeaderLabels(
            [
                self._translate("widget_features.table.property", "Property"),
                self._translate("widget_features.table.value", "Value"),
            ],
        )

    def _load_configs(self) -> None:
        """Load all widget configurations from JSON files."""
        config_files = [
            "layouts.json",
            "panels.json",
            "tabs.json",
            "menus.json",
            "lists.json",
        ]

        for config_file in config_files:
            config_path = self.config_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.widget_configs[config_file] = data
                        logger.debug(f"Loaded config: {config_file}")
                except Exception as exc:
                    logger.error(f"Error loading {config_file}: {exc}")

    def _populate_tree(self) -> None:
        """Populate widget tree from loaded configurations."""
        self.tree.clear()

        for config_name, config_data in self.widget_configs.items():
            if not isinstance(config_data, dict):
                continue

            root = QTreeWidgetItem(self.tree)
            root.setText(0, config_name.replace(".json", "").title())
            root.setData(0, Qt.ItemDataRole.UserRole, config_name)

            # Add child items
            if "items" in config_data and isinstance(config_data["items"], list):
                for item in config_data["items"]:
                    if isinstance(item, dict) and "name" in item:
                        child = QTreeWidgetItem(root)
                        child.setText(0, item.get("name", "Unnamed"))
                        child.setData(0, Qt.ItemDataRole.UserRole, item)

    def _on_tree_selection_changed(self) -> None:
        """Handle tree selection change."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.property_table.setRowCount(0)
            return

        item = selected_items[0]
        widget_data = item.data(0, Qt.ItemDataRole.UserRole)

        if isinstance(widget_data, dict):
            self.current_widget = widget_data
            self._populate_properties(widget_data)

    def _populate_properties(self, widget_data: dict[str, Any]) -> None:
        """Populate property table with widget data.

        Args:
            widget_data: Widget configuration dictionary
        """
        self.property_table.setRowCount(0)

        row = 0
        for key, value in widget_data.items():
            if key.startswith("_"):
                continue

            self.property_table.insertRow(row)

            # Property name
            name_item = QTableWidgetItem(key)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_font = QFont()
            name_font.setBold(True)
            name_item.setFont(name_font)
            self.property_table.setItem(row, 0, name_item)

            # Property value
            value_item = QTableWidgetItem(str(value))
            self.property_table.setItem(row, 1, value_item)

            row += 1

    def _save_changes(self) -> None:
        """Save changes back to configuration files."""
        try:
            for config_file, config_data in self.widget_configs.items():
                config_path = self.config_path / config_file
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                    logger.info(f"Saved config: {config_file}")

            self.saved.emit(str(self.config_path))
            QMessageBox.information(
                self,
                self._translate("message.success", "Success"),
                self._translate(
                    "widget_features.message.saved",
                    "Configuration saved successfully!",
                ),
            )
        except Exception as exc:
            logger.exception(f"Error saving configuration: {exc}")
            QMessageBox.critical(
                self,
                self._translate("message.error", "Error"),
                self._translate(
                    "widget_features.error.save_failed",
                    "Failed to save: {error}",
                    error=str(exc),
                ),
            )

    def _reload_config(self) -> None:
        """Reload configuration from files."""
        self.widget_configs.clear()
        self._load_configs()
        self._populate_tree()
        self.property_table.setRowCount(0)
        logger.info("Configuration reloaded")

    def load_widgets(self) -> None:
        """Load and display widgets in tree."""
        self._populate_tree()


class WidgetFeaturesEditorDialog(QDialog):
    """Dialog for widget features editing.

    Provides a comprehensive interface for editing widget properties
    and configurations at runtime.
    """

    def __init__(
        self,
        config_path: Path,
        parent: QWidget | None = None,
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize Widget Features Editor Dialog.

        Args:
            config_path: Path to configuration directory
            parent: Parent widget
            i18n_factory: Optional i18n factory for dialog text translation
        """
        super().__init__(parent)
        self._config_path = config_path
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        self.setWindowTitle(
            self._translate("widget_features.dialog.title", "Widget Features Editor"),
        )
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout(self)

        # Tab widget for different editor views
        self.tabs = QTabWidget()

        # Property editor tab
        self.property_editor = WidgetPropertyEditor(config_path, self, i18n_factory=i18n_factory)
        self.property_editor.load_widgets()
        self.tabs.addTab(
            self.property_editor,
            self._translate("widget_features.tab.properties", "Properties"),
        )

        # Statistics tab
        self.stats_tab = self._create_statistics_tab(config_path)
        self.tabs.addTab(
            self.stats_tab,
            self._translate("widget_features.tab.statistics", "Statistics"),
        )

        layout.addWidget(self.tabs)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(self.reject)
        close_button = self.button_box.button(QDialogButtonBox.StandardButton.Close)
        if close_button is not None:
            close_button.setText(self._translate("dialog.close", "Close"))
        layout.addWidget(self.button_box)

        logger.debug(f"WidgetFeaturesEditorDialog created")

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory and refresh visible texts."""
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()

        self.setWindowTitle(
            self._translate("widget_features.dialog.title", "Widget Features Editor"),
        )

        self.property_editor.set_i18n_factory(i18n_factory)

        self.tabs.setTabText(
            0,
            self._translate("widget_features.tab.properties", "Properties"),
        )
        self.tabs.setTabText(
            1,
            self._translate("widget_features.tab.statistics", "Statistics"),
        )

        close_button = self.button_box.button(QDialogButtonBox.StandardButton.Close)
        if close_button is not None:
            close_button.setText(self._translate("dialog.close", "Close"))

        refreshed_stats_tab = self._create_statistics_tab(self._config_path)
        self.tabs.removeTab(1)
        self.tabs.insertTab(
            1,
            refreshed_stats_tab,
            self._translate("widget_features.tab.statistics", "Statistics"),
        )
        self.stats_tab = refreshed_stats_tab

    def _translate(self, key: str, default: str | None = None, **kwargs: object) -> str:
        """Translate key with fallback and interpolation."""
        if not self._i18n_factory or not key:
            text = default or key
            return text.format(**kwargs) if kwargs else text

        cache_key = f"{key}|{sorted(kwargs.items())}" if kwargs else key
        if cache_key in self._translated_cache:
            return self._translated_cache[cache_key]

        translated = self._i18n_factory.translate(key, default=default or key, **kwargs)
        self._translated_cache[cache_key] = translated
        return translated

    def _create_statistics_tab(self, config_path: Path) -> QWidget:
        """Create statistics tab.

        Args:
            config_path: Path to configuration directory

        Returns:
            Configured widget tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        stats_group = QGroupBox(
            self._translate("widget_features.stats.group", "Configuration Statistics"),
        )
        stats_layout = QVBoxLayout()

        try:
            # Count items from config files
            config_files = [
                "layouts.json",
                "panels.json",
                "tabs.json",
                "menus.json",
                "lists.json",
            ]

            total_items = 0
            stats_text = self._translate(
                "widget_features.stats.summary_html",
                "<b>Configuration Summary:</b><br>",
            )

            for config_file in config_files:
                config_path_file = config_path / config_file
                if config_path_file.exists():
                    with open(config_path_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "items" in data:
                            count = len(data.get("items", []))
                            total_items += count
                            stats_text += self._translate(
                                "widget_features.stats.file_line_html",
                                "<br>{file}: {count} items",
                                file=config_file,
                                count=count,
                            )

            stats_text += self._translate(
                "widget_features.stats.total_html",
                "<br><br><b>Total: {count} items</b>",
                count=total_items,
            )

            label = QLabel(stats_text)
            label.setWordWrap(True)
            stats_layout.addWidget(label)

        except Exception as exc:
            logger.exception(f"Error generating statistics: {exc}")
            label = QLabel(
                self._translate("widget_features.error.label", "Error: {error}", error=str(exc)),
            )
            stats_layout.addWidget(label)

        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        return widget


class WidgetFeaturesEditor(QWidget):
    """Main widget for features editing.

    Provides a complete interface for editing widget
    features and configuration at runtime.
    """

    updated = Signal()

    def __init__(
        self,
        config_path: Path,
        parent: QWidget | None = None,
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize Widget Features Editor.

        Args:
            config_path: Path to configuration directory
            parent: Parent widget
            i18n_factory: Optional i18n factory for UI text translation
        """
        super().__init__(parent)
        self.config_path = config_path
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        self._setup_ui()
        logger.debug(f"WidgetFeaturesEditor initialized with config path: {config_path}")

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory and refresh visible texts."""
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()
        self._header.setText(self._translate("widget_features.header", "Widget Features Editor"))
        self.editor.set_i18n_factory(i18n_factory)

    def _translate(self, key: str, default: str | None = None) -> str:
        """Translate key with fallback."""
        if not self._i18n_factory or not key:
            return default or key
        if key in self._translated_cache:
            return self._translated_cache[key]
        translated = self._i18n_factory.translate(key, default=default or key)
        self._translated_cache[key] = translated
        return translated

    def _setup_ui(self) -> None:
        """Set up user interface."""
        layout = QVBoxLayout(self)

        # Header
        self._header = QLabel(self._translate("widget_features.header", "Widget Features Editor"))
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self._header.setFont(header_font)
        layout.addWidget(self._header)

        # Property editor
        self.editor = WidgetPropertyEditor(self.config_path, self, i18n_factory=self._i18n_factory)
        self.editor.load_widgets()
        self.editor.saved.connect(lambda _config_name: self.updated.emit())
        layout.addWidget(self.editor)

    def refresh(self) -> None:
        """Refresh widget configuration."""
        self.editor._reload_config()
