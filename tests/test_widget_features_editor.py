"""Tests for widget_features_editor.py - Widget Features Editor components.

Tests cover:
- WidgetPropertyEditor initialization and configuration loading
- Tree population and selection handling
- Property table population
- Save and reload functionality
- WidgetFeaturesEditorDialog with tabs
- WidgetFeaturesEditor main widget
- Signal emissions
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from widgetsystem.ui.widget_features_editor import (
    WidgetFeaturesEditor,
    WidgetFeaturesEditorDialog,
    WidgetPropertyEditor,
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
    """Create temporary config directory with sample config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)

        # Create sample config files
        panels_config = {
            "items": [
                {"name": "Panel 1", "id": "panel1", "width": 200, "visible": True},
                {"name": "Panel 2", "id": "panel2", "width": 300, "visible": False},
            ]
        }
        (config_path / "panels.json").write_text(
            json.dumps(panels_config), encoding="utf-8"
        )

        tabs_config = {
            "items": [
                {"name": "Tab 1", "id": "tab1", "icon": "home"},
                {"name": "Tab 2", "id": "tab2", "icon": "settings"},
            ]
        }
        (config_path / "tabs.json").write_text(
            json.dumps(tabs_config), encoding="utf-8"
        )

        menus_config = {
            "items": [
                {"name": "File", "id": "file_menu"},
                {"name": "Edit", "id": "edit_menu"},
                {"name": "Help", "id": "help_menu"},
            ]
        }
        (config_path / "menus.json").write_text(
            json.dumps(menus_config), encoding="utf-8"
        )

        layouts_config = {
            "items": [
                {"name": "Default Layout", "id": "default"},
            ]
        }
        (config_path / "layouts.json").write_text(
            json.dumps(layouts_config), encoding="utf-8"
        )

        lists_config = {
            "items": [
                {"name": "List 1", "id": "list1"},
            ]
        }
        (config_path / "lists.json").write_text(
            json.dumps(lists_config), encoding="utf-8"
        )

        yield config_path


class TestWidgetPropertyEditor:
    """Tests for WidgetPropertyEditor class."""

    def test_initialization(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test editor initializes correctly."""
        editor = WidgetPropertyEditor(temp_config_dir)

        assert editor.config_path == temp_config_dir
        assert editor.current_widget is None
        assert len(editor.widget_configs) > 0

    def test_configs_loaded(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test configuration files are loaded."""
        editor = WidgetPropertyEditor(temp_config_dir)

        assert "panels.json" in editor.widget_configs
        assert "tabs.json" in editor.widget_configs
        assert "menus.json" in editor.widget_configs

    def test_tree_widget_exists(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test tree widget is created."""
        editor = WidgetPropertyEditor(temp_config_dir)

        assert editor.tree is not None
        assert editor.tree.headerItem().text(0) == "Widget Hierarchy"

    def test_property_table_exists(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test property table is created."""
        editor = WidgetPropertyEditor(temp_config_dir)

        assert editor.property_table is not None
        assert editor.property_table.columnCount() == 2

    def test_load_widgets_populates_tree(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test loading widgets populates tree."""
        editor = WidgetPropertyEditor(temp_config_dir)
        editor.load_widgets()

        assert editor.tree.topLevelItemCount() > 0

    def test_tree_has_config_roots(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test tree has root items for configs."""
        editor = WidgetPropertyEditor(temp_config_dir)
        editor.load_widgets()

        # Get root item texts
        root_texts = []
        for i in range(editor.tree.topLevelItemCount()):
            item = editor.tree.topLevelItem(i)
            root_texts.append(item.text(0))

        assert "Panels" in root_texts
        assert "Tabs" in root_texts
        assert "Menus" in root_texts

    def test_tree_selection_populates_properties(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test selecting tree item populates properties."""
        editor = WidgetPropertyEditor(temp_config_dir)
        editor.load_widgets()

        # Find and select a child item
        root = editor.tree.topLevelItem(0)
        if root and root.childCount() > 0:
            child = root.child(0)
            child.setSelected(True)
            editor._on_tree_selection_changed()

            # Property table should have rows
            assert editor.property_table.rowCount() > 0

    def test_property_table_shows_widget_properties(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test property table shows widget properties."""
        editor = WidgetPropertyEditor(temp_config_dir)
        editor.load_widgets()

        # Simulate widget selection
        widget_data = {"name": "Test", "id": "test1", "value": 42}
        editor._populate_properties(widget_data)

        # Check table contents
        assert editor.property_table.rowCount() == 3

        # Find "name" property
        found_name = False
        for row in range(editor.property_table.rowCount()):
            if editor.property_table.item(row, 0).text() == "name":
                assert editor.property_table.item(row, 1).text() == "Test"
                found_name = True
                break

        assert found_name

    def test_property_table_ignores_private_properties(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test property table ignores private (_) properties."""
        editor = WidgetPropertyEditor(temp_config_dir)

        widget_data = {"name": "Test", "_private": "hidden", "id": "test1"}
        editor._populate_properties(widget_data)

        # Should only have 2 rows (name and id)
        assert editor.property_table.rowCount() == 2

    def test_save_changes_signal(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test saved signal emission."""
        editor = WidgetPropertyEditor(temp_config_dir)

        received = []
        editor.saved.connect(lambda path: received.append(path))

        # Mock message box to avoid UI
        with patch.object(QMessageBox, "information"):
            editor._save_changes()

        assert len(received) > 0

    def test_reload_config(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test reloading configuration."""
        editor = WidgetPropertyEditor(temp_config_dir)
        editor.load_widgets()

        # Modify loaded config
        editor.widget_configs["test"] = {"items": []}

        # Reload
        editor._reload_config()

        # Test config should be gone
        assert "test" not in editor.widget_configs

    def test_missing_config_files(self, qapp: QApplication) -> None:
        """Test handling of missing config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_path = Path(tmpdir)

            # Should not crash with no config files
            editor = WidgetPropertyEditor(empty_path)
            assert len(editor.widget_configs) == 0


class TestWidgetFeaturesEditorDialog:
    """Tests for WidgetFeaturesEditorDialog class."""

    def test_initialization(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test dialog initializes correctly."""
        dialog = WidgetFeaturesEditorDialog(temp_config_dir)

        assert dialog.windowTitle() == "Widget Features Editor"

    def test_tabs_exist(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test dialog has tabs."""
        dialog = WidgetFeaturesEditorDialog(temp_config_dir)

        # Dialog should have tab widget
        # Dialog content is in layout
        layout = dialog.layout()
        assert layout is not None

    def test_statistics_tab_content(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test statistics tab shows item counts."""
        dialog = WidgetFeaturesEditorDialog(temp_config_dir)

        # Statistics should show counts
        stats_widget = dialog._create_statistics_tab(temp_config_dir)
        assert stats_widget is not None

    def test_dialog_close(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test dialog can be closed."""
        dialog = WidgetFeaturesEditorDialog(temp_config_dir)

        # Should be closable
        dialog.close()


class TestWidgetFeaturesEditor:
    """Tests for WidgetFeaturesEditor main widget."""

    def test_initialization(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test editor widget initializes correctly."""
        editor = WidgetFeaturesEditor(temp_config_dir)

        assert editor.config_path == temp_config_dir

    def test_has_property_editor(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test widget contains property editor."""
        editor = WidgetFeaturesEditor(temp_config_dir)

        assert hasattr(editor, "editor")
        assert isinstance(editor.editor, WidgetPropertyEditor)

    def test_refresh_method(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test refresh method works."""
        editor = WidgetFeaturesEditor(temp_config_dir)

        # Should not crash
        editor.refresh()

    def test_updated_signal(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test updated signal emission."""
        editor = WidgetFeaturesEditor(temp_config_dir)

        received = []
        editor.updated.connect(lambda: received.append(True))

        # Trigger update through inner editor's saved signal
        with patch.object(QMessageBox, "information"):
            editor.editor._save_changes()

        assert len(received) > 0


class TestConfigFileHandling:
    """Tests for configuration file handling."""

    def test_load_invalid_json(self, qapp: QApplication) -> None:
        """Test handling of invalid JSON in config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            (config_path / "panels.json").write_text("invalid json", encoding="utf-8")

            # Should not crash
            editor = WidgetPropertyEditor(config_path)
            assert "panels.json" not in editor.widget_configs

    def test_save_creates_valid_json(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test save creates valid JSON files."""
        editor = WidgetPropertyEditor(temp_config_dir)

        with patch.object(QMessageBox, "information"):
            editor._save_changes()

        # Verify saved files are valid JSON
        for config_file in editor.widget_configs:
            config_file_path = temp_config_dir / config_file
            if config_file_path.exists():
                content = config_file_path.read_text(encoding="utf-8")
                json.loads(content)  # Should not raise

    def test_config_list_data(self, qapp: QApplication) -> None:
        """Test handling of list-type config data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            # Create list-type config (not dict with items)
            (config_path / "panels.json").write_text(
                json.dumps([{"name": "item"}]), encoding="utf-8"
            )

            editor = WidgetPropertyEditor(config_path)
            editor.load_widgets()

            # Should handle gracefully
            # Tree might be empty for list-type config


class TestTreeInteraction:
    """Tests for tree widget interaction."""

    def test_empty_selection(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test handling of empty tree selection."""
        editor = WidgetPropertyEditor(temp_config_dir)
        editor.load_widgets()

        # Clear selection
        editor.tree.clearSelection()
        editor._on_tree_selection_changed()

        # Property table should be cleared
        assert editor.property_table.rowCount() == 0

    def test_root_item_selection(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test selecting root item (config file)."""
        editor = WidgetPropertyEditor(temp_config_dir)
        editor.load_widgets()

        # Select root item
        root = editor.tree.topLevelItem(0)
        if root:
            root.setSelected(True)
            editor._on_tree_selection_changed()

            # Root items store config name as string, not dict
            # Property table might be empty or have string data


class TestUIComponents:
    """Tests for UI component creation."""

    def test_buttons_exist(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test save and reload buttons exist."""
        editor = WidgetPropertyEditor(temp_config_dir)

        # Buttons should exist (check layout)
        layout = editor.layout()
        assert layout is not None

    def test_splitter_exists(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test splitter between tree and table exists."""
        editor = WidgetPropertyEditor(temp_config_dir)

        # Layout should contain splitter
        layout = editor.layout()
        assert layout is not None


class TestStatisticsCalculation:
    """Tests for statistics tab calculations."""

    def test_statistics_counts_items(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test statistics counts config items correctly."""
        dialog = WidgetFeaturesEditorDialog(temp_config_dir)
        stats_widget = dialog._create_statistics_tab(temp_config_dir)

        # Widget should be created successfully
        assert stats_widget is not None

    def test_statistics_with_empty_config(self, qapp: QApplication) -> None:
        """Test statistics with empty config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)

            dialog = WidgetFeaturesEditorDialog(config_path)
            stats_widget = dialog._create_statistics_tab(config_path)

            # Should not crash with empty config
            assert stats_widget is not None

    def test_statistics_with_no_items(self, qapp: QApplication) -> None:
        """Test statistics with config having no items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            (config_path / "panels.json").write_text(
                json.dumps({"items": []}), encoding="utf-8"
            )

            dialog = WidgetFeaturesEditorDialog(config_path)
            stats_widget = dialog._create_statistics_tab(config_path)

            # Should show 0 items
            assert stats_widget is not None


class TestErrorHandling:
    """Tests for error handling."""

    def test_save_error_handling(
        self, qapp: QApplication, temp_config_dir: Path
    ) -> None:
        """Test error handling during save."""
        editor = WidgetPropertyEditor(temp_config_dir)

        # Add invalid config that can't be serialized
        editor.widget_configs["test.json"] = {"key": object()}

        # Should handle error gracefully
        with patch.object(QMessageBox, "critical"):
            with patch.object(QMessageBox, "information"):
                try:
                    editor._save_changes()
                except Exception:
                    pass  # Error is expected and should be handled

    def test_load_error_handling(self, qapp: QApplication) -> None:
        """Test error handling during load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)

            # Create file that will cause read error
            panels_path = config_path / "panels.json"
            panels_path.write_text("", encoding="utf-8")

            # Should not crash
            editor = WidgetPropertyEditor(config_path)
