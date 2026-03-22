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
from typing import Any, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
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


class WidgetPropertyEditor(QWidget):
    """Editor for widget properties with persistence.

    Signals:
        propertyChanged: Emitted when property changes (widget_id, property_name, value)
        saved: Emitted when changes are saved to file
    """

    propertyChanged = Signal(str, str, str)
    saved = Signal(str)

    def __init__(self, config_path: Path, parent: QWidget | None = None) -> None:
        """Initialize Widget Property Editor.

        Args:
            config_path: Path to configuration directory
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_path = config_path
        self.current_widget: dict[str, Any] | None = None
        self.widget_configs: dict[str, dict[str, Any]] = {}
        self._load_configs()
        self._setup_ui()
        logger.debug(f"WidgetPropertyEditor initialized with config path: {config_path}")

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
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self._save_changes)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reload Config")
        reset_btn.clicked.connect(self._reload_config)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_widget_tree_group(self) -> QGroupBox:
        """Create widget tree view group.

        Returns:
            Configured QGroupBox with tree widget
        """
        group = QGroupBox("Widgets")
        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Widget Hierarchy")
        self.tree.itemSelectionChanged.connect(self._on_tree_selection_changed)
        layout.addWidget(self.tree)

        group.setLayout(layout)
        return group

    def _create_property_editor_group(self) -> QGroupBox:
        """Create property editor group.

        Returns:
            Configured QGroupBox with property table
        """
        group = QGroupBox("Properties")
        layout = QVBoxLayout()

        self.property_table = QTableWidget()
        self.property_table.setColumnCount(2)
        self.property_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.property_table.setColumnWidth(0, 150)
        self.property_table.setColumnWidth(1, 250)
        layout.addWidget(self.property_table)

        group.setLayout(layout)
        return group

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
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
        except Exception as exc:
            logger.exception(f"Error saving configuration: {exc}")
            QMessageBox.critical(self, "Error", f"Failed to save: {exc}")

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
    ) -> None:
        """Initialize Widget Features Editor Dialog.

        Args:
            config_path: Path to configuration directory
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Widget Features Editor")
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout(self)

        # Tab widget for different editor views
        tabs = QTabWidget()

        # Property editor tab
        property_editor = WidgetPropertyEditor(config_path, self)
        property_editor.load_widgets()
        tabs.addTab(property_editor, "Properties")

        # Statistics tab
        stats_tab = self._create_statistics_tab(config_path)
        tabs.addTab(stats_tab, "Statistics")

        layout.addWidget(tabs)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        logger.debug(f"WidgetFeaturesEditorDialog created")

    def _create_statistics_tab(self, config_path: Path) -> QWidget:
        """Create statistics tab.

        Args:
            config_path: Path to configuration directory

        Returns:
            Configured widget tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        stats_group = QGroupBox("Configuration Statistics")
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
            stats_text = "<b>Configuration Summary:</b><br>"

            for config_file in config_files:
                config_path_file = config_path / config_file
                if config_path_file.exists():
                    with open(config_path_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "items" in data:
                            count = len(data.get("items", []))
                            total_items += count
                            stats_text += f"<br>{config_file}: {count} items"

            stats_text += f"<br><br><b>Total: {total_items} items</b>"

            label = QLabel(stats_text)
            label.setWordWrap(True)
            stats_layout.addWidget(label)

        except Exception as exc:
            logger.exception(f"Error generating statistics: {exc}")
            label = QLabel(f"Error: {exc}")
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
    ) -> None:
        """Initialize Widget Features Editor.

        Args:
            config_path: Path to configuration directory
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_path = config_path
        self._setup_ui()
        logger.debug(f"WidgetFeaturesEditor initialized with config path: {config_path}")

    def _setup_ui(self) -> None:
        """Set up user interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Widget Features Editor")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Property editor
        self.editor = WidgetPropertyEditor(self.config_path, self)
        self.editor.load_widgets()
        self.editor.saved.connect(self.updated.emit)
        layout.addWidget(self.editor)

    def refresh(self) -> None:
        """Refresh widget configuration."""
        self.editor._reload_config()
