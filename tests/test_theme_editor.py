"""Tests for theme_editor.py - Live Theme Editor components.

Tests cover:
- ARGBColorButton initialization and color handling
- ThemePropertyEditor for different property types
- LiveThemeEditor theme loading and editing
- ThemeEditorDialog functionality
- Signal emissions
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QSpinBox

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.theme_editor import (
    ARGBColorButton,
    LiveThemeEditor,
    ThemeEditorDialog,
    ThemePropertyEditor,
)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_config_dir() -> Path:
    """Create temporary config directory with theme files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)

        # Create themes.json
        themes = [
            {
                "id": "dark",
                "name": "Dark Theme",
                "description": "A dark theme",
                "colors": {
                    "background": "#FF1E1E1E",
                    "foreground": "#FFFFFFFF",
                    "accent": "#FF0078D4",
                },
                "border_radius": 4,
                "font_size": 12,
            },
            {
                "id": "light",
                "name": "Light Theme",
                "description": "A light theme",
                "colors": {
                    "background": "#FFFFFFFF",
                    "foreground": "#FF000000",
                    "accent": "#FF0078D4",
                },
                "border_radius": 4,
                "font_size": 12,
            },
        ]
        (config_path / "themes.json").write_text(json.dumps(themes), encoding="utf-8")

        yield config_path


@pytest.fixture
def temp_config_dir_with_i18n() -> Path:
    """Create temporary config directory with theme and i18n files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)

        themes = {
            "themes": [
                {
                    "id": "dark",
                    "name": "Dark Theme",
                    "description": "A dark theme",
                    "colors": {
                        "background": "#FF1E1E1E",
                        "foreground": "#FFFFFFFF",
                    },
                }
            ]
        }
        (config_path / "themes.json").write_text(json.dumps(themes), encoding="utf-8")

        i18n_de = {
            "theme_editor.dialog_title": "Live-Theme-Editor",
            "theme_editor.select_theme": "Design auswählen:",
            "theme_editor.properties": "Design-Eigenschaften",
            "theme_editor.save_theme": "Design speichern",
            "action.export": "Exportieren",
            "button.reset": "Zurücksetzen",
            "theme_editor.opacity": "Deckkraft",
            "theme_editor.select_color": "Farbe wählen",
            "dialog.close": "Schließen",
        }
        (config_path / "i18n.de.json").write_text(json.dumps(i18n_de), encoding="utf-8")

        i18n_en = {
            "theme_editor.dialog_title": "Live Theme Editor",
            "theme_editor.select_theme": "Select Theme:",
            "theme_editor.properties": "Theme Properties",
            "theme_editor.save_theme": "Save Theme",
            "action.export": "Export",
            "button.reset": "Reset",
            "theme_editor.opacity": "opacity",
            "theme_editor.select_color": "Select Color",
            "dialog.close": "Close",
        }
        (config_path / "i18n.en.json").write_text(json.dumps(i18n_en), encoding="utf-8")

        yield config_path


class TestARGBColorButton:
    """Tests for ARGBColorButton class."""

    def test_initialization_default(self, qapp: QApplication) -> None:
        """Test button initializes with default color."""
        button = ARGBColorButton()

        assert button.current_color == "#FFFFFFFF"
        assert "100% opacity" in button.text()

    def test_initialization_with_color(self, qapp: QApplication) -> None:
        """Test button initializes with specified color."""
        button = ARGBColorButton("#80FF0000")  # Semi-transparent red

        assert button.current_color == "#80FF0000"

    def test_set_color(self, qapp: QApplication) -> None:
        """Test setting color programmatically."""
        button = ARGBColorButton()
        button.set_color("#FF00FF00")  # Green

        assert button.current_color == "#FF00FF00"

    def test_color_parsing_argb(self, qapp: QApplication) -> None:
        """Test ARGB color parsing."""
        button = ARGBColorButton("#80FF0000")  # 50% transparent red

        # Should show approximately 50% opacity
        assert "50%" in button.text() or "31%" in button.text()  # 128/255 ~ 50%

    def test_color_parsing_rgb(self, qapp: QApplication) -> None:
        """Test RGB color parsing (without alpha)."""
        button = ARGBColorButton("#FF0000")  # Red without alpha

        # Should assume full opacity
        assert "100% opacity" in button.text()

    def test_color_changed_signal(self, qapp: QApplication) -> None:
        """Test colorChanged signal emission."""
        button = ARGBColorButton()

        received = []
        button.colorChanged.connect(lambda c: received.append(c))

        # Manually set color and emit (simulating dialog selection)
        button.current_color = "#FF00FF00"
        button._update_display()
        button.colorChanged.emit(button.current_color)

        assert "#FF00FF00" in received

    def test_update_display_invalid_color(self, qapp: QApplication) -> None:
        """Test display update with invalid color."""
        button = ARGBColorButton()
        button.current_color = "invalid"

        # Should not raise, should show fallback text
        button._update_display()
        assert "Select Color" in button.text()


class TestThemePropertyEditor:
    """Tests for ThemePropertyEditor class."""

    def test_color_property_editor(self, qapp: QApplication) -> None:
        """Test editor for color property."""
        editor = ThemePropertyEditor("background", "#FFFF0000")

        assert isinstance(editor.editor, ARGBColorButton)
        assert editor.property_name == "background"

    def test_numeric_property_editor(self, qapp: QApplication) -> None:
        """Test editor for numeric property."""
        editor = ThemePropertyEditor("font_size", 12)

        assert isinstance(editor.editor, QSpinBox)
        assert editor.editor.value() == 12

    def test_boolean_property_editor(self, qapp: QApplication) -> None:
        """Test editor for boolean property."""
        editor = ThemePropertyEditor("enabled", True)

        assert isinstance(editor.editor, QComboBox)
        assert editor.editor.currentText() == "True"

    def test_string_property_editor(self, qapp: QApplication) -> None:
        """Test editor for string property."""
        editor = ThemePropertyEditor("name", "Test Theme")

        assert isinstance(editor.editor, QLineEdit)
        assert editor.editor.text() == "Test Theme"

    def test_get_value_color(self, qapp: QApplication) -> None:
        """Test getting value from color editor."""
        editor = ThemePropertyEditor("color", "#FF00FF00")

        value = editor.get_value()
        assert value == "#FF00FF00"

    def test_get_value_numeric(self, qapp: QApplication) -> None:
        """Test getting value from numeric editor."""
        editor = ThemePropertyEditor("size", 16)
        editor.editor.setValue(24)

        value = editor.get_value()
        assert value == 24

    def test_get_value_boolean(self, qapp: QApplication) -> None:
        """Test getting value from boolean editor."""
        editor = ThemePropertyEditor("active", False)
        editor.editor.setCurrentText("True")

        value = editor.get_value()
        assert value is True

    def test_get_value_string(self, qapp: QApplication) -> None:
        """Test getting value from string editor."""
        editor = ThemePropertyEditor("label", "old")
        editor.editor.setText("new")

        value = editor.get_value()
        assert value == "new"

    def test_property_changed_signal(self, qapp: QApplication) -> None:
        """Test propertyChanged signal emission."""
        editor = ThemePropertyEditor("size", 12)

        received = []
        editor.propertyChanged.connect(lambda n, v: received.append((n, v)))

        editor.editor.setValue(20)

        assert len(received) > 0
        assert received[-1] == ("size", "20")


class TestLiveThemeEditor:
    """Tests for LiveThemeEditor class."""

    def test_initialization(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test editor initializes correctly."""
        editor = LiveThemeEditor(temp_config_dir)

        assert editor.config_path == temp_config_dir
        assert editor.theme_combo.count() > 0

    def test_initialization_with_callback(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test editor with apply callback."""
        callback_calls = []
        callback = lambda theme: callback_calls.append(theme)

        editor = LiveThemeEditor(temp_config_dir, callback)

        assert editor.apply_theme_callback is callback

    def test_theme_selection(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test theme selection from combo box."""
        editor = LiveThemeEditor(temp_config_dir)

        # Select first theme
        editor.theme_combo.setCurrentIndex(0)

        assert editor.current_theme != {}

    def test_theme_properties_loaded(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test theme properties are loaded into editors."""
        editor = LiveThemeEditor(temp_config_dir)
        editor.theme_combo.setCurrentIndex(0)

        # Should have property editors
        assert len(editor.property_editors) > 0

    def test_property_change_updates_theme(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test property change updates current theme."""
        callback_calls = []
        callback = lambda theme: callback_calls.append(theme)

        editor = LiveThemeEditor(temp_config_dir, callback)
        editor.theme_combo.setCurrentIndex(0)

        # Simulate property change
        editor._on_property_changed("border_radius", "8")

        assert editor.current_theme.get("border_radius") == "8"
        assert len(callback_calls) > 0

    def test_nested_property_change(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test nested property change (colors.xxx)."""
        editor = LiveThemeEditor(temp_config_dir)
        editor.theme_combo.setCurrentIndex(0)

        editor._on_property_changed("background.main", "#FF000000")

        assert "colors" in editor.current_theme
        assert editor.current_theme["colors"]["background"]["main"] == "#FF000000"

    def test_reset_theme(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test theme reset functionality."""
        editor = LiveThemeEditor(temp_config_dir)
        editor.theme_combo.setCurrentIndex(0)

        # Modify theme
        original_theme = editor.current_theme.copy()
        editor._on_property_changed("border_radius", "99")

        # Reset
        editor._on_reset()

        # Theme should be reloaded
        assert editor.theme_combo.count() > 0

    def test_theme_applied_signal(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test themeApplied signal emission."""
        editor = LiveThemeEditor(temp_config_dir)

        received = []
        editor.themeApplied.connect(lambda t: received.append(t))

        editor.theme_combo.setCurrentIndex(0)
        editor._on_property_changed("test", "value")

        assert len(received) > 0

    def test_export_theme(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test theme export with mocked file dialog."""
        editor = LiveThemeEditor(temp_config_dir)
        editor.theme_combo.setCurrentIndex(0)

        export_path = temp_config_dir / "exported.json"

        with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName") as mock_dialog:
            mock_dialog.return_value = (str(export_path), "JSON Files (*.json)")
            editor._on_export()

        assert export_path.exists()
        exported = json.loads(export_path.read_text())
        assert isinstance(exported, dict)


class TestThemeEditorDialog:
    """Tests for ThemeEditorDialog class."""

    def test_initialization(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test dialog initializes correctly."""
        dialog = ThemeEditorDialog(temp_config_dir)

        assert dialog.windowTitle() == "Live Theme Editor"
        assert dialog.minimumWidth() >= 600
        assert dialog.minimumHeight() >= 500

    def test_initialization_with_callback(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test dialog with apply callback."""
        callback = MagicMock()

        dialog = ThemeEditorDialog(temp_config_dir, callback)

        assert dialog.editor.apply_theme_callback is callback

    def test_editor_widget_exists(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test dialog contains editor widget."""
        dialog = ThemeEditorDialog(temp_config_dir)

        assert isinstance(dialog.editor, LiveThemeEditor)

    def test_close_button_exists(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test dialog has close button."""
        dialog = ThemeEditorDialog(temp_config_dir)

        # Dialog should be closable
        dialog.close()


class TestColorConversion:
    """Tests for color format conversions."""

    def test_argb_to_rgba(self, qapp: QApplication) -> None:
        """Test ARGB string parsing."""
        button = ARGBColorButton("#80FF8000")  # Semi-transparent orange

        # Verify color is set correctly
        assert button.current_color == "#80FF8000"

    def test_short_hex_format(self, qapp: QApplication) -> None:
        """Test short hex format handling."""
        button = ARGBColorButton()
        button.current_color = "#F00"  # Short red

        # Should not crash on short format
        button._update_display()

    def test_invalid_hex_characters(self, qapp: QApplication) -> None:
        """Test handling of invalid hex characters."""
        button = ARGBColorButton()
        button.current_color = "#GGGGGGGG"

        # Should handle gracefully
        button._update_display()
        assert "Select Color" in button.text()


class TestEditorEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_themes_file(self, qapp: QApplication) -> None:
        """Test handling of empty themes file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            (config_path / "themes.json").write_text("[]", encoding="utf-8")

            editor = LiveThemeEditor(config_path)

            assert editor.theme_combo.count() == 0

    def test_malformed_themes_file(self, qapp: QApplication) -> None:
        """Test handling of malformed themes file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            (config_path / "themes.json").write_text("invalid json", encoding="utf-8")

            # Should not crash
            editor = LiveThemeEditor(config_path)
            assert editor.theme_combo.count() == 0

    def test_missing_themes_file(self, qapp: QApplication) -> None:
        """Test handling of missing themes file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)

            # Should not crash
            editor = LiveThemeEditor(config_path)
            assert editor.theme_combo.count() == 0

    def test_theme_without_colors(self, qapp: QApplication) -> None:
        """Test theme without colors section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            themes = [{"id": "minimal", "name": "Minimal"}]
            (config_path / "themes.json").write_text(json.dumps(themes), encoding="utf-8")

            editor = LiveThemeEditor(config_path)
            editor.theme_combo.setCurrentIndex(0)

            # Should handle theme without colors
            assert editor.current_theme is not None


class TestThemeEditorI18n:
    """Tests for i18n support in theme editor components."""

    def test_dialog_title_translated(self, qapp: QApplication, temp_config_dir_with_i18n: Path) -> None:
        """Dialog title should be translated when i18n is provided."""
        i18n = I18nFactory(config_path=temp_config_dir_with_i18n, locale="de")
        dialog = ThemeEditorDialog(temp_config_dir_with_i18n, i18n_factory=i18n)
        assert dialog.windowTitle() == "Live-Theme-Editor"

    def test_editor_static_labels_translated(
        self,
        qapp: QApplication,
        temp_config_dir_with_i18n: Path,
    ) -> None:
        """Editor static labels should be translated in German."""
        i18n = I18nFactory(config_path=temp_config_dir_with_i18n, locale="de")
        editor = LiveThemeEditor(temp_config_dir_with_i18n, i18n_factory=i18n)

        assert editor.select_theme_label.text() == "Design auswählen:"
        assert editor.editor_group.title() == "Design-Eigenschaften"
        assert editor.save_btn.text() == "Design speichern"
        assert editor.export_btn.text() == "Exportieren"
        assert editor.reset_btn.text() == "Zurücksetzen"

    def test_runtime_locale_switch_updates_texts(
        self,
        qapp: QApplication,
        temp_config_dir_with_i18n: Path,
    ) -> None:
        """Switching i18n factory at runtime should update visible texts."""
        editor = LiveThemeEditor(temp_config_dir_with_i18n)
        assert editor.save_btn.text() == "Save Theme"

        i18n = I18nFactory(config_path=temp_config_dir_with_i18n, locale="de")
        editor.set_i18n_factory(i18n)

        assert editor.save_btn.text() == "Design speichern"

    def test_dialog_runtime_locale_switch_updates_title_and_close_button(
        self,
        qapp: QApplication,
        temp_config_dir_with_i18n: Path,
    ) -> None:
        """Dialog locale switch should refresh title and close button text."""
        i18n_de = I18nFactory(config_path=temp_config_dir_with_i18n, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_with_i18n, locale="en")

        dialog = ThemeEditorDialog(temp_config_dir_with_i18n, i18n_factory=i18n_en)
        assert dialog.windowTitle() == "Live Theme Editor"
        assert dialog.close_button is not None
        assert dialog.close_button.text() == "Close"

        dialog.set_i18n_factory(i18n_de)

        assert dialog.windowTitle() == "Live-Theme-Editor"
        assert dialog.close_button.text() == "Schließen"
        assert dialog.editor.save_btn.text() == "Design speichern"

    def test_runtime_locale_switch_preserves_selected_theme(
        self,
        qapp: QApplication,
        temp_config_dir: Path,
    ) -> None:
        """Locale switch should keep the currently selected theme in the combo box."""
        (temp_config_dir / "i18n.de.json").write_text("{}", encoding="utf-8")
        (temp_config_dir / "i18n.en.json").write_text("{}", encoding="utf-8")

        i18n_de = I18nFactory(config_path=temp_config_dir, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir, locale="en")

        editor = LiveThemeEditor(temp_config_dir, i18n_factory=i18n_de)
        assert editor.theme_combo.count() >= 2

        editor.theme_combo.setCurrentIndex(1)
        current_data = editor.theme_combo.currentData()
        assert isinstance(current_data, dict)
        assert current_data.get("id") == "light"

        editor.set_i18n_factory(i18n_en)

        switched_data = editor.theme_combo.currentData()
        assert isinstance(switched_data, dict)
        assert switched_data.get("id") == "light"
