"""Live Theme Editor - Real-time theme editing and preview.

This module provides a UI component for editing application themes at runtime,
including color selection, ARGB support, and live preview capabilities.
"""

from collections.abc import Callable
import json
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from widgetsystem.factories.theme_factory import ThemeFactory


logger = logging.getLogger(__name__)


class ARGBColorButton(QPushButton):
    """Button widget for selecting ARGB colors with transparency support."""

    colorChanged = Signal(str)  # Emits hex color string #AARRGGBB

    def __init__(self, initial_color: str = "#FFFFFFFF", parent: QWidget | None = None) -> None:
        """Initialize ARGB color button.

        Args:
            initial_color: Initial color in #AARRGGBB format
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_color = initial_color
        self._update_display()
        self.clicked.connect(self._on_color_clicked)

    def _update_display(self) -> None:
        """Update button display based on current color."""
        try:
            # Parse ARGB format
            hex_val = self.current_color.lstrip("#")
            if len(hex_val) == 8:
                alpha = int(hex_val[0:2], 16)
                red = int(hex_val[2:4], 16)
                green = int(hex_val[4:6], 16)
                blue = int(hex_val[6:8], 16)
            else:
                # RGB format - add full alpha
                red = int(hex_val[0:2], 16)
                green = int(hex_val[2:4], 16)
                blue = int(hex_val[4:6], 16)
                alpha = 255

            # Set button color with transparency
            bg_color = f"rgb({red}, {green}, {blue})"
            alpha_percent = (alpha / 255) * 100

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {'white' if (red + green + blue) < 384 else 'black'};
                    border: 2px solid #ccc;
                    border-radius: 4px;
                    padding: 4px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 2px solid #999;
                }}
            """)

            # Display text
            self.setText(f"{self.current_color}\n({alpha_percent:.0f}% opacity)")
        except Exception as e:
            logger.exception("Error updating color button")
            self.setText("Select Color")

    def _on_color_clicked(self) -> None:
        """Handle color button click - show color dialog."""
        try:
            # Parse current color for initial value
            hex_val = self.current_color.lstrip("#")
            if len(hex_val) == 8:
                alpha = int(hex_val[0:2], 16)
                red = int(hex_val[2:4], 16)
                green = int(hex_val[4:6], 16)
                blue = int(hex_val[6:8], 16)
            else:
                red = int(hex_val[0:2], 16) if len(hex_val) >= 2 else 0
                green = int(hex_val[2:4], 16) if len(hex_val) >= 4 else 0
                blue = int(hex_val[4:6], 16) if len(hex_val) >= 6 else 0
                alpha = 255

            initial_color = QColor(red, green, blue, alpha)

            # Show color dialog
            color_dialog = QColorDialog(initial_color, self)
            if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
                selected_color = color_dialog.selectedColor()
                # Format as #AARRGGBB
                self.current_color = f"#{selected_color.alpha():02x}{selected_color.red():02x}{selected_color.green():02x}{selected_color.blue():02x}"
                self._update_display()
                self.colorChanged.emit(self.current_color)
        except Exception as e:
            logger.exception("Error selecting color")

    def set_color(self, color: str) -> None:
        """Set the current color.

        Args:
            color: Color in #AARRGGBB or #RRGGBB format
        """
        self.current_color = color
        self._update_display()


class ThemePropertyEditor(QWidget):
    """Editor for a single theme property."""

    propertyChanged = Signal(str, str)  # property_name, property_value

    def __init__(
        self,
        property_name: str,
        property_value: Any,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize theme property editor.

        Args:
            property_name: Name of the property
            property_value: Current value
            parent: Parent widget
        """
        super().__init__(parent)
        self.property_name = property_name
        self.property_value = property_value

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label
        label = QLabel(f"{property_name}:")
        label.setMinimumWidth(120)
        layout.addWidget(label)

        # Value editor based on type
        if isinstance(property_value, str) and (property_value.startswith("#")):
            # Color property
            self.editor = ARGBColorButton(str(property_value), self)
            self.editor.colorChanged.connect(self._on_value_changed)
        elif isinstance(property_value, bool):
            # Boolean property — must be checked before (int, float) because bool subclasses int
            self.editor = QComboBox(self)
            self.editor.addItems(["False", "True"])
            self.editor.setCurrentText(str(property_value))
            self.editor.currentTextChanged.connect(self._on_value_changed)
        elif isinstance(property_value, (int, float)):
            # Numeric property
            self.editor = QSpinBox(self)
            self.editor.setRange(-999, 9999)
            self.editor.setValue(int(property_value))
            self.editor.valueChanged.connect(self._on_value_changed)
        else:
            # String property
            self.editor = QLineEdit(self)
            self.editor.setText(str(property_value))
            self.editor.textChanged.connect(self._on_value_changed)

        layout.addWidget(self.editor)

    def _on_value_changed(self) -> None:
        """Handle value change."""
        if isinstance(self.editor, ARGBColorButton):
            new_value = self.editor.current_color
        elif isinstance(self.editor, QSpinBox):
            new_value = str(self.editor.value())
            self.editor: ARGBColorButton | QComboBox | QSpinBox | QLineEdit
        elif isinstance(self.editor, QComboBox):
            new_value = self.editor.currentText()
        else:
            new_value = self.editor.text()

        self.propertyChanged.emit(self.property_name, new_value)

    def get_value(self) -> Any:
        """Get current editor value."""
        if isinstance(self.editor, ARGBColorButton):
            return self.editor.current_color
        if isinstance(self.editor, QSpinBox):
            return self.editor.value()
        if isinstance(self.editor, QComboBox):
            return self.editor.currentText() == "True"
        return self.editor.text()


class LiveThemeEditor(QWidget):
    """Live theme editor widget for real-time theme customization."""

    themeApplied = Signal(dict)  # Emits theme dict

    def __init__(
        self,
        config_path: Path,
        apply_theme_callback: Callable[[dict[str, Any]], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize theme editor.

        Args:
            config_path: Path to config directory
            apply_theme_callback: Callback to apply theme (receives theme dict)
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_path = config_path
        self.apply_theme_callback = apply_theme_callback
        self.theme_factory = ThemeFactory(config_path)
        self.current_theme: dict[str, Any] = {}
        self.property_editors: dict[str, ThemePropertyEditor] = {}

        self._setup_ui()
        self._load_themes()

    def _setup_ui(self) -> None:
        """Setup the UI."""
        layout = QVBoxLayout(self)

        # Theme selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Theme:"))

        self.theme_combo = QComboBox(self)
        self.theme_combo.currentTextChanged.connect(self._on_theme_selected)
        selection_layout.addWidget(self.theme_combo)

        selection_layout.addStretch()
        layout.addLayout(selection_layout)

        # Property editor area
        self.editor_group = QGroupBox("Theme Properties", self)
        editor_layout = QVBoxLayout(self.editor_group)
        self.editor_layout = editor_layout
        layout.addWidget(self.editor_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.clicked.connect(self._on_reset)
        button_layout.addWidget(self.reset_btn)

        self.save_btn = QPushButton("Save Theme", self)
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)

        self.export_btn = QPushButton("Export", self)
        self.export_btn.clicked.connect(self._on_export)
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _load_themes(self) -> None:
        """Load available themes."""
        try:
            themes = self.theme_factory.load_themes()
            self.theme_combo.clear()
            for theme in themes:
                theme_name = theme.get("name", theme.get("id", "Unknown"))
                self.theme_combo.addItem(theme_name, theme)
        except Exception as e:
            logger.exception("Error loading themes")

    def _on_theme_selected(self, theme_name: str) -> None:
        """Handle theme selection."""
        try:
            index = self.theme_combo.currentIndex()
            if index >= 0:
                theme_data = self.theme_combo.itemData(index)
                if isinstance(theme_data, dict):
                    self._load_theme_properties(theme_data)
        except Exception as e:
            logger.exception("Error selecting theme")

    def _load_theme_properties(self, theme: dict[str, Any]) -> None:
        """Load theme properties into editors.

        Args:
            theme: Theme dictionary
        """
        # Clear existing editors
        while self.editor_layout.count() > 0:
            widget = self.editor_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        self.property_editors.clear()
        self.current_theme = theme

        # Create editors for theme properties
        colors = theme.get("colors", {})
        for color_name, color_value in colors.items():
            if isinstance(color_value, dict):
                # Nested color object
                for sub_name, sub_value in color_value.items():
                    prop_name = f"{color_name}.{sub_name}"
                    editor = ThemePropertyEditor(prop_name, sub_value, self)
                    editor.propertyChanged.connect(self._on_property_changed)
                    self.editor_layout.addWidget(editor)
                    self.property_editors[prop_name] = editor
            else:
                # Simple color value
                editor = ThemePropertyEditor(color_name, color_value, self)
                editor.propertyChanged.connect(self._on_property_changed)
                self.editor_layout.addWidget(editor)
                self.property_editors[color_name] = editor

        # Add other properties
        for prop_name, prop_value in theme.items():
            if prop_name not in ("id", "name", "colors", "description"):
                editor = ThemePropertyEditor(prop_name, prop_value, self)
                editor.propertyChanged.connect(self._on_property_changed)
                self.editor_layout.addWidget(editor)
                self.property_editors[prop_name] = editor

        self.editor_layout.addStretch()

    def _on_property_changed(self, property_name: str, property_value: str) -> None:
        """Handle property change.

        Args:
            property_name: Name of changed property
            property_value: New value
        """
        try:
            # Update theme dict
            if "." in property_name:
                # Nested property
                parts = property_name.split(".")
                if "colors" not in self.current_theme:
                    self.current_theme["colors"] = {}
                if not isinstance(self.current_theme["colors"].get(parts[0]), dict):
                    self.current_theme["colors"][parts[0]] = {}
                self.current_theme["colors"][parts[0]][parts[1]] = property_value
            else:
                # Top-level property
                self.current_theme[property_name] = property_value

            # Apply theme preview
            if self.apply_theme_callback:
                self.apply_theme_callback(self.current_theme)

            self.themeApplied.emit(self.current_theme)
        except Exception as e:
            logger.exception("Error applying theme change")

    def _on_reset(self) -> None:
        """Reset theme to original."""
        try:
            self._load_themes()
            self._on_theme_selected(self.theme_combo.currentText())
        except Exception as e:
            logger.exception("Error resetting theme")

    def _on_save(self) -> None:
        """Save current theme."""
        try:
            theme_name = self.theme_combo.currentText()
            if theme_name:
                # Save to themes.json
                themes_file = self.config_path / "themes.json"
                themes = json.loads(themes_file.read_text(encoding="utf-8"))

                # Find and update theme
                for theme in themes:
                    if theme.get("name") == theme_name:
                        theme.update(self.current_theme)
                        break

                themes_file.write_text(json.dumps(themes, indent=2), encoding="utf-8")
                logger.info("Theme saved: %s", theme_name)
        except Exception as e:
            logger.exception("Error saving theme")

    def _on_export(self) -> None:
        """Export current theme."""
        try:
            from PySide6.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Theme",
                str(self.config_path),
                "JSON Files (*.json)",
            )

            if file_path:
                Path(file_path).write_text(
                    json.dumps(self.current_theme, indent=2),
                    encoding="utf-8",
                )
                logger.info("Theme exported: %s", file_path)
        except Exception as e:
            logger.exception("Error exporting theme")


class ThemeEditorDialog(QDialog):
    """Dialog window for the theme editor."""

    def __init__(
        self,
        config_path: Path,
        apply_theme_callback: Callable[[dict[str, Any]], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize theme editor dialog.

        Args:
            config_path: Path to config directory
            apply_theme_callback: Callback to apply theme
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Live Theme Editor")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        self.editor = LiveThemeEditor(config_path, apply_theme_callback, self)
        layout.addWidget(self.editor)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            self,
        )
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
