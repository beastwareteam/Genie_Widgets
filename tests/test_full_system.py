"""Pytest smoke tests for full system wiring."""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from widgetsystem.factories.dnd_factory import DnDFactory
from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.layout_factory import LayoutFactory
from widgetsystem.factories.list_factory import ListFactory
from widgetsystem.factories.menu_factory import MenuFactory
from widgetsystem.factories.panel_factory import PanelFactory
from widgetsystem.factories.responsive_factory import ResponsiveFactory
from widgetsystem.factories.tabs_factory import TabsFactory
from widgetsystem.factories.theme_factory import ThemeFactory
from widgetsystem.factories.ui_config_factory import UIConfigFactory
from widgetsystem.ui import ConfigurationPanel


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_factories_can_be_instantiated() -> None:
    """All major factories instantiate with config path."""
    config_path = Path("config")

    assert I18nFactory(config_path, locale="de") is not None
    assert ListFactory(config_path) is not None
    assert MenuFactory(config_path) is not None
    assert PanelFactory(config_path) is not None
    assert TabsFactory(config_path) is not None
    assert UIConfigFactory(config_path) is not None
    assert ThemeFactory(config_path) is not None
    assert LayoutFactory(config_path) is not None
    assert DnDFactory(config_path) is not None
    assert ResponsiveFactory(config_path) is not None


def test_core_config_data_loading() -> None:
    """Core config-centric factories can load structured data."""
    config_path = Path("config")

    lists = ListFactory(config_path)
    menus = MenuFactory(config_path)
    panels = PanelFactory(config_path)
    tabs = TabsFactory(config_path)
    ui_config = UIConfigFactory(config_path)

    assert isinstance(lists.load_list_groups(), list)
    assert isinstance(menus.load_menus(), list)
    assert isinstance(panels.load_panels(), list)
    assert isinstance(tabs.load_tab_groups(), list)
    assert isinstance(ui_config.load_ui_config_pages(), list)


def test_configuration_panel_creation() -> None:
    """ConfigurationPanel can be created with i18n factory."""
    _get_app()
    config_path = Path("config")
    i18n = I18nFactory(config_path, locale="de")

    panel = ConfigurationPanel(config_path, i18n)

    assert panel is not None
    assert panel.config_tabs.count() >= 1
