"""Focused runtime i18n tests for ChevronMenu."""

import json
import tempfile
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.ui.chevron_menu import ChevronMenu, ChevronMenuBar


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide QApplication instance for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def temp_config_dir_chevron_runtime() -> Path:
    """Create temporary config with menu + i18n data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        i18n_de = {
            "menu.file": "Datei",
            "menu.file.open": "Öffnen",
            "menu.parent": "Eltern",
            "menu.child": "Kind",
            "chevron_menu.tooltip.submenu_prefix": "Untermenü",
        }
        i18n_en = {
            "menu.file": "File",
            "menu.file.open": "Open",
            "menu.parent": "Parent",
            "menu.child": "Child",
            "chevron_menu.tooltip.submenu_prefix": "Submenu",
        }
        (config_dir / "i18n.de.json").write_text(json.dumps(i18n_de), encoding="utf-8")
        (config_dir / "i18n.en.json").write_text(json.dumps(i18n_en), encoding="utf-8")

        menus_config = {
            "menus": [
                {
                    "id": "file",
                    "label_key": "menu.file",
                    "type": "menu",
                    "children": [
                        {
                            "id": "open",
                            "label_key": "menu.file.open",
                            "type": "action",
                        }
                    ],
                }
            ]
        }
        (config_dir / "menus.json").write_text(
            json.dumps(menus_config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        yield config_dir


class TestChevronMenuRuntimeI18n:
    """Runtime i18n behavior for ChevronMenu and ChevronMenuBar."""

    def test_submenu_tooltip_prefix_translated(
        self,
        qapp: QApplication,
        temp_config_dir_chevron_runtime: Path,
    ) -> None:
        """Submenu tooltip prefix should use i18n translation."""
        i18n_de = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="de")
        menu = ChevronMenu(title="Test", i18n_factory=i18n_de)

        parent = MenuItem(
            id="parent",
            label_key="menu.parent",
            type="menu",
            children=[
                MenuItem(id="child", label_key="menu.child", type="action"),
            ],
        )

        menu.add_menu_item(parent)
        actions = menu.actions()
        assert len(actions) == 1
        assert actions[0].toolTip() == "Untermenü: Eltern"

    def test_menubar_title_updates_on_locale_switch(
        self,
        qapp: QApplication,
        temp_config_dir_chevron_runtime: Path,
    ) -> None:
        """Top-level menu title should be translated and update on switch."""
        i18n_de = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="en")
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_runtime)

        menu_bar = ChevronMenuBar(menu_factory=menu_factory, i18n_factory=i18n_de)
        menus = menu_bar.create_menu_bar()

        assert len(menus) == 1
        assert menus[0].title() == "Datei"

        menu_bar.set_i18n_factory(i18n_en)
        assert menus[0].title() == "File"

    def test_menubar_action_label_updates_on_locale_switch(
        self,
        qapp: QApplication,
        temp_config_dir_chevron_runtime: Path,
    ) -> None:
        """Existing action labels should update when locale changes at runtime."""
        i18n_de = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="en")
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_runtime)

        menu_bar = ChevronMenuBar(menu_factory=menu_factory, i18n_factory=i18n_de)
        menus = menu_bar.create_menu_bar()
        assert len(menus) == 1
        assert menus[0].actions()[0].text() == "Öffnen"

        menu_bar.set_i18n_factory(i18n_en)
        assert menus[0].actions()[0].text() == "Open"

    def test_menubar_title_falls_back_when_i18n_removed(
        self,
        qapp: QApplication,
        temp_config_dir_chevron_runtime: Path,
    ) -> None:
        """Top-level menu title should revert to fallback key when i18n is removed."""
        i18n_de = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="de")
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_runtime)

        menu_bar = ChevronMenuBar(menu_factory=menu_factory, i18n_factory=i18n_de)
        menus = menu_bar.create_menu_bar()
        assert len(menus) == 1
        assert menus[0].title() == "Datei"

        menu_bar.set_i18n_factory(None)
        assert menus[0].title() == "menu.file"

    def test_submenu_label_and_tooltip_update_on_locale_switch(
        self,
        qapp: QApplication,
        temp_config_dir_chevron_runtime: Path,
    ) -> None:
        """Existing submenu labels and tooltip prefix should update on locale switch."""
        i18n_de = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_chevron_runtime, locale="en")
        menu = ChevronMenu(title="Test", i18n_factory=i18n_de)

        parent = MenuItem(
            id="parent",
            label_key="menu.parent",
            type="menu",
            children=[
                MenuItem(id="child", label_key="menu.child", type="action"),
            ],
        )

        menu.add_menu_item(parent)
        action = menu.actions()[0]
        assert action.text() == "Eltern ▶"
        assert action.toolTip() == "Untermenü: Eltern"

        menu.set_i18n_factory(i18n_en)

        assert action.text() == "Parent ▶"
        assert action.toolTip() == "Submenu: Parent"
