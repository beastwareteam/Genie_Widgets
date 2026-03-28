"""Tests for MenuFactory i18n integration."""

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.menu_factory import MenuItem, MenuFactory


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create temporary config directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Create minimal i18n files
        i18n_de = {
            "menu.file": "Datei",
            "menu.file.new": "Neu",
            "menu.file.open": "Öffnen",
            "menu.file.save": "Speichern",
            "menu.edit": "Bearbeiten",
            "menu.edit.undo": "Rückgängig",
            "menu.edit.redo": "Wiederherstellen",
            "menu.help": "Hilfe",
            "tooltip.menu.new": "Neue Datei erstellen (Strg+N)",
            "tooltip.menu.save": "Datei speichern (Strg+S)",
            "tooltip.menu.undo": "Letzte Aktion rückgängig machen",
        }
        i18n_en = {
            "menu.file": "File",
            "menu.file.new": "New",
            "menu.file.open": "Open",
            "menu.file.save": "Save",
            "menu.edit": "Edit",
            "menu.edit.undo": "Undo",
            "menu.edit.redo": "Redo",
            "menu.help": "Help",
            "tooltip.menu.new": "Create new file (Ctrl+N)",
            "tooltip.menu.save": "Save file (Ctrl+S)",
            "tooltip.menu.undo": "Undo last action",
        }

        with open(config_dir / "i18n.de.json", "w", encoding="utf-8") as f:
            json.dump(i18n_de, f)
        with open(config_dir / "i18n.en.json", "w", encoding="utf-8") as f:
            json.dump(i18n_en, f)

        # Create test menus.json
        menus_config: dict[str, Any] = {
            "menus": [
                {
                    "id": "file",
                    "label_key": "menu.file",
                    "type": "menu",
                    "children": [
                        {
                            "id": "file_new",
                            "label_key": "menu.file.new",
                            "type": "action",
                            "action": "new_file",
                            "shortcut": "Ctrl+N",
                            "tooltip_key": "tooltip.menu.new",
                        },
                        {
                            "id": "file_open",
                            "label_key": "menu.file.open",
                            "type": "action",
                            "action": "open_file",
                        },
                        {
                            "id": "file_save",
                            "label_key": "menu.file.save",
                            "type": "action",
                            "action": "save_file",
                            "shortcut": "Ctrl+S",
                            "tooltip_key": "tooltip.menu.save",
                        },
                    ],
                },
                {
                    "id": "edit",
                    "label_key": "menu.edit",
                    "type": "menu",
                    "children": [
                        {
                            "id": "edit_undo",
                            "label_key": "menu.edit.undo",
                            "type": "action",
                            "action": "undo",
                            "shortcut": "Ctrl+Z",
                            "tooltip_key": "tooltip.menu.undo",
                        },
                        {
                            "id": "edit_redo",
                            "label_key": "menu.edit.redo",
                            "type": "action",
                            "action": "redo",
                            "shortcut": "Ctrl+Y",
                        },
                    ],
                },
                {
                    "id": "help",
                    "label_key": "menu.help",
                    "type": "menu",
                    "children": [],
                },
            ]
        }

        with open(config_dir / "menus.json", "w", encoding="utf-8") as f:
            json.dump(menus_config, f)

        yield config_dir


@pytest.fixture
def i18n_factory_de(temp_config_dir: Path) -> I18nFactory:
    """Create I18nFactory with German locale."""
    return I18nFactory(temp_config_dir, locale="de")


@pytest.fixture
def i18n_factory_en(temp_config_dir: Path) -> I18nFactory:
    """Create I18nFactory with English locale."""
    return I18nFactory(temp_config_dir, locale="en")


class TestMenuFactoryI18nBasics:
    """Test basic i18n initialization and setup."""

    def test_menu_factory_initializes_without_i18n(self, temp_config_dir: Path) -> None:
        """Test MenuFactory can be initialized without i18n_factory."""
        factory = MenuFactory(temp_config_dir)
        assert factory._i18n_factory is None
        assert factory._translated_cache == {}

    def test_menu_factory_initializes_with_i18n(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test MenuFactory initializes with i18n_factory."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        assert factory._i18n_factory is i18n_factory_de
        assert factory._translated_cache == {}

    def test_set_i18n_factory(self, temp_config_dir: Path, i18n_factory_de: I18nFactory) -> None:
        """Test setting i18n_factory after initialization."""
        factory = MenuFactory(temp_config_dir)
        assert factory._i18n_factory is None

        factory.set_i18n_factory(i18n_factory_de)
        assert factory._i18n_factory is i18n_factory_de

    def test_set_i18n_factory_clears_cache(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test setting i18n_factory clears translation cache."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        factory._translated_cache["test.key"] = "test_value"

        i18n_factory_en = I18nFactory(temp_config_dir, locale="en")
        factory.set_i18n_factory(i18n_factory_en)

        assert factory._translated_cache == {}


class TestMenuFactoryMenuLabelTranslation:
    """Test translating menu labels."""

    def test_get_menu_label_without_i18n(self, temp_config_dir: Path) -> None:
        """Test get_menu_label returns key as fallback without i18n."""
        factory = MenuFactory(temp_config_dir)
        menu = MenuItem(id="file", label_key="menu.file", type="menu")

        label = factory.get_menu_label(menu)
        assert label == "menu.file"

    def test_get_menu_label_with_i18n_german(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_menu_label translates to German."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        menu = MenuItem(id="file", label_key="menu.file", type="menu")

        label = factory.get_menu_label(menu)
        assert label == "Datei"

    def test_get_menu_label_with_i18n_english(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_menu_label translates to English."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        menu = MenuItem(id="help", label_key="menu.help", type="menu")

        label = factory.get_menu_label(menu)
        assert label == "Help"

    def test_get_menu_label_nested_menu(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_menu_label works on nested menu items."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        menu = MenuItem(id="file_new", label_key="menu.file.new", type="action")

        label = factory.get_menu_label(menu)
        assert label == "Neu"


class TestMenuFactoryTooltipTranslation:
    """Test translating menu tooltips."""

    def test_get_menu_tooltip_without_i18n(self, temp_config_dir: Path) -> None:
        """Test get_menu_tooltip returns key as fallback without i18n."""
        factory = MenuFactory(temp_config_dir)
        menu = MenuItem(
            id="file_save",
            label_key="menu.file.save",
            type="action",
            tooltip_key="tooltip.menu.save",
        )

        tooltip = factory.get_menu_tooltip(menu)
        assert tooltip == "tooltip.menu.save"

    def test_get_menu_tooltip_with_i18n_german(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_menu_tooltip translates to German."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        menu = MenuItem(
            id="file_save",
            label_key="menu.file.save",
            type="action",
            tooltip_key="tooltip.menu.save",
        )

        tooltip = factory.get_menu_tooltip(menu)
        assert tooltip == "Datei speichern (Strg+S)"

    def test_get_menu_tooltip_with_i18n_english(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_menu_tooltip translates to English."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        menu = MenuItem(
            id="file_new",
            label_key="menu.file.new",
            type="action",
            tooltip_key="tooltip.menu.new",
        )

        tooltip = factory.get_menu_tooltip(menu)
        assert tooltip == "Create new file (Ctrl+N)"

    def test_get_menu_tooltip_empty_returns_empty(self, temp_config_dir: Path) -> None:
        """Test get_menu_tooltip with empty tooltip returns empty."""
        factory = MenuFactory(temp_config_dir)
        menu = MenuItem(id="test", label_key="menu.test", type="action", tooltip_key="")

        tooltip = factory.get_menu_tooltip(menu)
        assert tooltip == ""


class TestMenuFactoryLoadWithTranslation:
    """Test loading menus and translating them."""

    def test_load_menus_without_i18n(self, temp_config_dir: Path) -> None:
        """Test loading menus without i18n works."""
        factory = MenuFactory(temp_config_dir)
        menus = factory.load_menus()

        assert len(menus) == 3
        assert menus[0].id == "file"
        assert menus[0].label_key == "menu.file"
        assert len(menus[0].children) == 3

    def test_load_menus_with_i18n(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test loading menus with i18n_factory."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        menus = factory.load_menus()

        assert len(menus) == 3
        assert menus[0].id == "file"

        # Check we can translate the menu label
        label = factory._translate(menus[0].label_key)
        assert label == "Datei"

    def test_nested_menu_labels_translated(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test nested menu item labels are translated."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        menus = factory.load_menus()

        file_menu = menus[0]
        assert file_menu.id == "file"

        # Check first child
        new_item = file_menu.children[0]
        assert new_item.id == "file_new"
        label = factory.get_menu_label(new_item)
        assert label == "New"

    def test_tooltip_translation_on_loaded_menu(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test tooltips are translated for loaded menu items."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        menus = factory.load_menus()

        file_menu = menus[0]
        save_item = file_menu.children[2]

        assert save_item.id == "file_save"
        assert save_item.tooltip_key == "tooltip.menu.save"

        tooltip = factory.get_menu_tooltip(save_item)
        assert tooltip == "Datei speichern (Strg+S)"


class TestMenuFactoryRootMenus:
    """Test root menus translation."""

    def test_get_root_menus_with_translation(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_root_menus returns menus with translation support."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        root_menus = factory.get_root_menus()

        assert len(root_menus) == 3
        labels = [factory.get_menu_label(m) for m in root_menus]
        assert "File" in labels
        assert "Edit" in labels
        assert "Help" in labels


class TestMenuFactoryEdgeCases:
    """Test edge cases and error handling."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir: Path) -> None:
        """Test _translate with None factory uses default."""
        factory = MenuFactory(temp_config_dir, i18n_factory=None)

        result = factory._translate("missing.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir: Path) -> None:
        """Test _translate with None factory returns key."""
        factory = MenuFactory(temp_config_dir, i18n_factory=None)

        result = factory._translate("missing.key")
        assert result == "missing.key"

    def test_translate_empty_key(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test _translate with empty key."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)

        result = factory._translate("", default="fallback")
        assert result == "fallback"

    def test_menu_item_serialization_with_tooltip(
        self, temp_config_dir: Path
    ) -> None:
        """Test MenuItem with tooltip_key serializes correctly."""
        menu = MenuItem(
            id="test",
            label_key="menu.test",
            type="action",
            tooltip_key="tooltip.test",
        )

        menu_dict = MenuFactory._menu_to_dict(menu)
        
        assert menu_dict["id"] == "test"
        assert menu_dict["tooltip_key"] == "tooltip.test"

    def test_menu_item_serialization_without_tooltip(
        self, temp_config_dir: Path
    ) -> None:
        """Test MenuItem without tooltip_key doesn't include it in dict."""
        menu = MenuItem(
            id="test",
            label_key="menu.test",
            type="menu",
            tooltip_key="",
        )

        menu_dict = MenuFactory._menu_to_dict(menu)
        
        assert menu_dict["id"] == "test"
        assert "tooltip_key" not in menu_dict

    def test_multiple_factory_instances_independent(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory, i18n_factory_en: I18nFactory
    ) -> None:
        """Test multiple factory instances maintain independent caches."""
        factory_de = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        factory_en = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_en)

        menu = MenuItem(id="file", label_key="menu.file", type="menu")

        label_de = factory_de.get_menu_label(menu)
        label_en = factory_en.get_menu_label(menu)

        assert label_de == "Datei"
        assert label_en == "File"

    def test_caching_works_for_repeated_translations(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test translation caching works correctly."""
        factory = MenuFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        menu = MenuItem(id="file", label_key="menu.file", type="menu")

        # First call populates cache
        label1 = factory.get_menu_label(menu)
        assert "menu.file" in factory._translated_cache

        # Second call uses cached value
        label2 = factory.get_menu_label(menu)
        assert label1 == label2 == "Datei"
