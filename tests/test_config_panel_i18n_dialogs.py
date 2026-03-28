"""Tests for ConfigurationPanel dialog i18n behavior."""

from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.config_panel import ConfigurationPanel


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide a QApplication instance for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def config_panel_de(qapp: QApplication) -> ConfigurationPanel:
    """Create ConfigurationPanel with German i18n using project config."""
    config_path = Path("config")
    i18n = I18nFactory(config_path=config_path, locale="de")
    panel = ConfigurationPanel(config_path=config_path, i18n_factory=i18n)
    return panel


class TestConfigurationPanelDialogI18n:
    """Verify dialog texts use i18n translations."""

    def test_add_menu_empty_name_shows_translated_warning(
        self,
        config_panel_de: ConfigurationPanel,
    ) -> None:
        """Empty menu name should show translated warning dialog."""
        with patch("widgetsystem.ui.config_panel.QMessageBox.warning") as warning_mock:
            config_panel_de._on_add_menu("")

        warning_mock.assert_called_once()
        _, title, message = warning_mock.call_args.args
        assert title == "Warnung"
        assert message == "Bitte einen Menünamen eingeben"

    def test_add_list_empty_name_shows_translated_warning(
        self,
        config_panel_de: ConfigurationPanel,
    ) -> None:
        """Empty list name should show translated warning dialog."""
        with patch("widgetsystem.ui.config_panel.QMessageBox.warning") as warning_mock:
            config_panel_de._on_add_list("", "vertical")

        warning_mock.assert_called_once()
        _, title, message = warning_mock.call_args.args
        assert title == "Warnung"
        assert message == "Bitte einen Listennamen eingeben"

    def test_add_tab_empty_name_shows_translated_warning(
        self,
        config_panel_de: ConfigurationPanel,
    ) -> None:
        """Empty tab name should show translated warning dialog."""
        with patch("widgetsystem.ui.config_panel.QMessageBox.warning") as warning_mock:
            config_panel_de._on_add_tab("")

        warning_mock.assert_called_once()
        _, title, message = warning_mock.call_args.args
        assert title == "Warnung"
        assert message == "Bitte einen Tab-Namen eingeben"

    def test_add_panel_empty_name_shows_translated_warning(
        self,
        config_panel_de: ConfigurationPanel,
    ) -> None:
        """Empty panel name should show translated warning dialog."""
        with patch("widgetsystem.ui.config_panel.QMessageBox.warning") as warning_mock:
            config_panel_de._on_add_panel("", "left")

        warning_mock.assert_called_once()
        _, title, message = warning_mock.call_args.args
        assert title == "Warnung"
        assert message == "Bitte einen Panelnamen eingeben"
