"""Focused i18n tests for ConfigurationPanel combo option labels/data."""

from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QComboBox, QVBoxLayout, QWidget
import pytest


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.config_panel import ConfigurationPanel


@pytest.fixture(scope="module")
def qapp_instance() -> QApplication:
    """Provide QApplication instance."""
    app = QApplication.instance()
    if app is None or not isinstance(app, QApplication):
        app = QApplication(sys.argv)
    return app


@pytest.mark.usefixtures("qapp_instance")
class TestConfigurationPanelI18nCombos:
    """Verify translated combo labels keep stable internal values."""

    def _find_target_combo(self, container: QWidget, expected_first_data: str) -> QComboBox:
        for combo in container.findChildren(QComboBox):
            if combo.count() > 0 and combo.itemData(0) == expected_first_data:
                return combo
        msg = f"No combo found with first item data '{expected_first_data}'"
        raise AssertionError(msg)

    def test_list_type_combo_translated_with_stable_data(self) -> None:
        """List type combo should show translated labels and raw internal values."""
        config_path = Path("config")
        panel = ConfigurationPanel(config_path, I18nFactory(config_path, locale="de"))

        container = QWidget()
        layout = QVBoxLayout(container)
        panel._setup_lists_editor(layout)

        combo_de = self._find_target_combo(container, "vertical")
        assert combo_de.itemText(0) == "Vertikal"
        assert combo_de.itemData(0) == "vertical"

        panel.set_i18n_factory(I18nFactory(config_path, locale="en"))
        container_en = QWidget()
        layout_en = QVBoxLayout(container_en)
        panel._setup_lists_editor(layout_en)

        combo_en = self._find_target_combo(container_en, "vertical")
        assert combo_en.itemText(0) == "Vertical"
        assert combo_en.itemData(0) == "vertical"

    def test_panel_area_combo_translated_with_stable_data(self) -> None:
        """Panel area combo should show translated labels and raw internal values."""
        config_path = Path("config")
        panel = ConfigurationPanel(config_path, I18nFactory(config_path, locale="de"))

        container = QWidget()
        layout = QVBoxLayout(container)
        panel._setup_panels_editor(layout)

        combo_de = self._find_target_combo(container, "left")
        assert combo_de.itemText(0) == "Links"
        assert combo_de.itemData(0) == "left"

        panel.set_i18n_factory(I18nFactory(config_path, locale="en"))
        container_en = QWidget()
        layout_en = QVBoxLayout(container_en)
        panel._setup_panels_editor(layout_en)

        combo_en = self._find_target_combo(container_en, "left")
        assert combo_en.itemText(0) == "Left"
        assert combo_en.itemData(0) == "left"
