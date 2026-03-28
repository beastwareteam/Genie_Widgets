"""Focused i18n tests for InlayTitleBar."""

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow

# Ensure src imports work in direct test execution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.inlay_titlebar import InlayTitleBar, InlayTitleBarController


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestInlayTitleBarI18n:
    """Verify visible titlebar strings are translated."""

    def test_german_tooltips_and_default_title(self, qapp: QApplication) -> None:
        """Default title and button tooltips should use German locale."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        window = QMainWindow()
        bar = InlayTitleBar(window, i18n_factory=i18n_de)

        assert bar._title_label.text() == "WidgetSystem"
        assert bar._btn_min.toolTip() == "Minimieren"
        assert bar._btn_max.toolTip() == "Maximieren"
        assert bar._btn_close.toolTip() == "Schließen"

    def test_runtime_switch_updates_tooltips(self, qapp: QApplication) -> None:
        """Runtime locale switch should refresh button tooltips."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")

        window = QMainWindow()
        bar = InlayTitleBar(window, i18n_factory=i18n_de)
        assert bar._btn_min.toolTip() == "Minimieren"

        bar.set_i18n_factory(i18n_en)

        assert bar._btn_min.toolTip() == "Minimize"
        assert bar._btn_max.toolTip() == "Maximize"
        assert bar._btn_close.toolTip() == "Close"

    def test_custom_title_is_preserved_on_locale_switch(self, qapp: QApplication) -> None:
        """Manual title should not be overwritten when locale changes."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")

        window = QMainWindow()
        bar = InlayTitleBar(window, i18n_factory=i18n_de)
        bar.set_title("My Custom Title")

        bar.set_i18n_factory(i18n_en)

        assert bar._title_label.text() == "My Custom Title"

    def test_controller_passes_i18n_to_titlebar(self, qapp: QApplication) -> None:
        """Controller should pass i18n factory into managed titlebar."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        window = QMainWindow()
        controller = InlayTitleBarController(window, i18n_factory=i18n_de)

        controller.install()

        assert controller.titlebar is not None
        assert controller.titlebar._btn_close.toolTip() == "Schließen"
