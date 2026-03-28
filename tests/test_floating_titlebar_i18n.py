"""Focused i18n tests for CustomFloatingTitleBar."""

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.floating_titlebar import CustomFloatingTitleBar


@pytest.fixture(scope="module")
def qapp_instance() -> QApplication:
    """Provide QApplication instance."""
    app = QApplication.instance()
    if app is None or not isinstance(app, QApplication):
        app = QApplication(sys.argv)
    return app


@pytest.mark.usefixtures("qapp_instance")
class TestCustomFloatingTitleBarI18n:
    """Verify translated tooltips for floating title bar controls."""

    def test_german_tooltips(self) -> None:
        """Default German locale should provide German tooltips."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        bar = CustomFloatingTitleBar("My Dock", i18n_factory=i18n_de)

        assert bar.dock_button.toolTip() == "Zurück ins Dock"
        assert bar.close_button.toolTip() == "Schließen"

    def test_runtime_switch_updates_tooltips(self) -> None:
        """Runtime locale switch should refresh visible tooltips."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")

        bar = CustomFloatingTitleBar("My Dock", i18n_factory=i18n_de)
        assert bar.dock_button.toolTip() == "Zurück ins Dock"

        bar.set_i18n_factory(i18n_en)

        assert bar.dock_button.toolTip() == "Back to Dock"
        assert bar.close_button.toolTip() == "Close"
