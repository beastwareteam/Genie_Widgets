"""Focused runtime i18n tests for ConfigurationPanel."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication, QWidget

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
class TestConfigurationPanelI18nRuntime:
    """Verify runtime locale switching for configuration tab titles."""

    def test_runtime_switch_updates_tab_titles(self) -> None:
        """Tab titles should refresh when swapping i18n factory at runtime."""
        config_path = Path("config")
        i18n_de = I18nFactory(config_path=config_path, locale="de")
        i18n_en = I18nFactory(config_path=config_path, locale="en")

        with (
            patch.object(
                ConfigurationPanel,
                "_create_category_widget",
                side_effect=lambda _category: QWidget(),
            ),
            patch(
                "widgetsystem.ui.config_panel.UIConfigFactory.get_all_categories",
                return_value=["menus", "lists"],
            ),
            patch(
                "widgetsystem.ui.config_panel.UIConfigFactory.get_pages_by_category",
                return_value=[{"id": "dummy"}],
            ),
        ):
            panel = ConfigurationPanel(config_path=config_path, i18n_factory=i18n_de)

            assert panel.config_tabs is not None
            initial_titles = [panel.config_tabs.tabText(i) for i in range(panel.config_tabs.count())]
            assert "Menückonfiguration" in initial_titles
            assert "Listenkonfiguration" in initial_titles

            panel.set_i18n_factory(i18n_en)

            switched_titles = [panel.config_tabs.tabText(i) for i in range(panel.config_tabs.count())]
            assert "Menu Configuration" in switched_titles
            assert "List Configuration" in switched_titles

    def test_runtime_switch_preserves_selected_category_tab(self) -> None:
        """Selected category tab should stay active after runtime locale switch."""
        config_path = Path("config")
        i18n_de = I18nFactory(config_path=config_path, locale="de")
        i18n_en = I18nFactory(config_path=config_path, locale="en")

        with (
            patch.object(
                ConfigurationPanel,
                "_create_category_widget",
                side_effect=lambda _category: QWidget(),
            ),
            patch(
                "widgetsystem.ui.config_panel.UIConfigFactory.get_all_categories",
                return_value=["menus", "lists"],
            ),
            patch(
                "widgetsystem.ui.config_panel.UIConfigFactory.get_pages_by_category",
                return_value=[{"id": "dummy"}],
            ),
        ):
            panel = ConfigurationPanel(config_path=config_path, i18n_factory=i18n_de)

            assert panel.config_tabs is not None
            panel.config_tabs.setCurrentIndex(1)
            assert panel.config_tabs.currentIndex() == 1

            panel.set_i18n_factory(i18n_en)

            assert panel.config_tabs.currentIndex() == 1
            assert panel.config_tabs.tabText(1) == "Menu Configuration"
