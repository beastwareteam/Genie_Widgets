"""Tests for ConfigurationPanel runtime editor behavior."""

from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.config_panel import ConfigurationPanel


def _get_app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _make_i18n_stub() -> I18nFactory:
    """Create an I18nFactory-typed stub for tests."""
    stub = MagicMock(spec=I18nFactory)
    stub.translate.side_effect = lambda _key, default="": default
    return cast("I18nFactory", stub)


def test_config_panel_add_menu_emits_config_changed() -> None:
    """Adding a menu via runtime editor emits the menus-changed signal."""
    _get_app()
    panel = ConfigurationPanel(Path("config"), _make_i18n_stub())

    panel.menu_factory = MagicMock()
    panel.menu_factory.add_menu_item.return_value = True

    emitted: list[str] = []
    panel.config_changed.connect(lambda category: emitted.append(category))

    with patch("widgetsystem.ui.config_panel.MenuFactory", return_value=panel.menu_factory):
        with patch("widgetsystem.ui.config_panel.QMessageBox.information") as info_box:
            panel._on_add_menu("Runtime Menu")
            info_box.assert_called_once()

    assert emitted == ["menus"]


def test_config_panel_add_panel_emits_config_changed() -> None:
    """Adding a panel via runtime editor emits the panels-changed signal."""
    _get_app()
    panel = ConfigurationPanel(Path("config"), _make_i18n_stub())

    panel.panel_factory = MagicMock()
    panel.panel_factory.add_panel.return_value = True

    emitted: list[str] = []
    panel.config_changed.connect(lambda category: emitted.append(category))

    with patch("widgetsystem.ui.config_panel.PanelFactory", return_value=panel.panel_factory):
        with patch("widgetsystem.ui.config_panel.QMessageBox.information") as info_box:
            panel._on_add_panel("Runtime Panel", "left")
            info_box.assert_called_once()

    assert emitted == ["panels"]
