"""Tests for ListFactory internationalization support."""

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.list_factory import ListFactory


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary config directory with test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        
        # Create i18n files
        i18n_de = {
            "list.items": "Elemente",
            "list.item.first": "Erstes Element",
            "list.item.second": "Zweites Element",
            "list.item.nested": "Verschachteltes Element",
            "config.list.main": "Hauptliste",
            "config.list.secondary": "Sekundärliste",
            "config.item.name": "Name",
            "config.item.description": "Beschreibung",
            "config.item.options": "Optionen",
        }
        
        i18n_en = {
            "list.items": "Items",
            "list.item.first": "First Item",
            "list.item.second": "Second Item",
            "list.item.nested": "Nested Item",
            "config.list.main": "Main List",
            "config.list.secondary": "Secondary List",
            "config.item.name": "Name",
            "config.item.description": "Description",
            "config.item.options": "Options",
        }
        
        (config_dir / "i18n.de.json").write_text(json.dumps(i18n_de, ensure_ascii=False), encoding="utf-8")
        (config_dir / "i18n.en.json").write_text(json.dumps(i18n_en, ensure_ascii=False), encoding="utf-8")
        
        # Create lists.json with test data
        lists_config = {
            "list_groups": [
                {
                    "id": "main_list",
                    "title_key": "config.list.main",
                    "list_type": "vertical",
                    "dock_panel_id": "panel_1",
                    "sortable": True,
                    "filterable": True,
                    "searchable": True,
                    "multi_select": False,
                    "items": [
                        {
                            "id": "item_1",
                            "label_key": "list.item.first",
                            "content_type": "text",
                            "content": "First item content",
                            "editable": True,
                            "deletable": True,
                            "icon": "icons/item1.png",
                            "data": {},
                            "children": [
                                {
                                    "id": "item_1_1",
                                    "label_key": "list.item.nested",
                                    "content_type": "text",
                                    "content": "Nested content",
                                    "editable": True,
                                    "deletable": True,
                                    "icon": "",
                                    "data": {},
                                    "children": [],
                                }
                            ],
                        },
                        {
                            "id": "item_2",
                            "label_key": "list.item.second",
                            "content_type": "text",
                            "content": "Second item content",
                            "editable": False,
                            "deletable": True,
                            "icon": "",
                            "data": {},
                            "children": [],
                        },
                    ],
                },
                {
                    "id": "secondary_list",
                    "title_key": "config.list.secondary",
                    "list_type": "horizontal",
                    "dock_panel_id": "panel_2",
                    "sortable": False,
                    "filterable": False,
                    "searchable": False,
                    "multi_select": True,
                    "items": [
                        {
                            "id": "item_3",
                            "label_key": "config.item.name",
                            "content_type": "button",
                            "content": "Name Button",
                            "editable": True,
                            "deletable": True,
                            "icon": "icons/name.png",
                            "data": {},
                            "children": [],
                        }
                    ],
                },
            ]
        }
        
        (config_dir / "lists.json").write_text(json.dumps(lists_config, indent=2, ensure_ascii=False))
        
        yield config_dir


class TestListFactoryI18nBasics:
    """Test basic ListFactory i18n initialization and setup."""

    def test_list_factory_initializes_without_i18n(self, temp_config_dir: Path) -> None:
        """ListFactory should initialize without i18n_factory."""
        factory = ListFactory(config_path=temp_config_dir)
        assert factory._i18n_factory is None
        assert factory._translated_cache == {}

    def test_list_factory_initializes_with_i18n(self, temp_config_dir: Path) -> None:
        """ListFactory should initialize with i18n_factory."""
        i18n = I18nFactory(config_path=temp_config_dir)
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        assert factory._i18n_factory is i18n
        assert factory._translated_cache == {}

    def test_set_i18n_factory(self, temp_config_dir: Path) -> None:
        """ListFactory should set i18n_factory after initialization."""
        factory = ListFactory(config_path=temp_config_dir)
        i18n = I18nFactory(config_path=temp_config_dir)
        factory.set_i18n_factory(i18n)
        assert factory._i18n_factory is i18n

    def test_set_i18n_factory_clears_cache(self, temp_config_dir: Path) -> None:
        """Setting i18n_factory should clear translation cache."""
        i18n = I18nFactory(config_path=temp_config_dir)
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        
        # Populate cache
        factory._translate("list.item.first")
        assert len(factory._translated_cache) > 0
        
        # Set factory again
        factory.set_i18n_factory(i18n)
        assert factory._translated_cache == {}


class TestListFactoryGroupTitleTranslation:
    """Test list group title translation."""

    def test_get_list_group_title_without_i18n(self, temp_config_dir: Path) -> None:
        """Without i18n, should return the key itself."""
        factory = ListFactory(config_path=temp_config_dir)
        groups = factory.load_list_groups()
        title = factory.get_list_group_title(groups[0])
        assert title == "config.list.main"

    def test_get_list_group_title_with_i18n_german(self, temp_config_dir: Path) -> None:
        """Should translate list group title to German."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="de")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        title = factory.get_list_group_title(groups[0])
        assert title == "Hauptliste"

    def test_get_list_group_title_with_i18n_english(self, temp_config_dir: Path) -> None:
        """Should translate list group title to English."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="en")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        title = factory.get_list_group_title(groups[0])
        assert title == "Main List"


class TestListFactoryItemLabelTranslation:
    """Test list item label translation."""

    def test_get_list_item_label_without_i18n(self, temp_config_dir: Path) -> None:
        """Without i18n, should return the key itself."""
        factory = ListFactory(config_path=temp_config_dir)
        groups = factory.load_list_groups()
        label = factory.get_list_item_label(groups[0].items[0])
        assert label == "list.item.first"

    def test_get_list_item_label_with_i18n_german(self, temp_config_dir: Path) -> None:
        """Should translate list item label to German."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="de")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        label = factory.get_list_item_label(groups[0].items[0])
        assert label == "Erstes Element"

    def test_get_list_item_label_with_i18n_english(self, temp_config_dir: Path) -> None:
        """Should translate list item label to English."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="en")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        label = factory.get_list_item_label(groups[0].items[0])
        assert label == "First Item"


class TestListFactoryLoadWithTranslation:
    """Test loading list groups with translation."""

    def test_load_groups_without_i18n(self, temp_config_dir: Path) -> None:
        """Load groups without i18n should work normally."""
        factory = ListFactory(config_path=temp_config_dir)
        groups = factory.load_list_groups()
        assert len(groups) == 2
        assert groups[0].id == "main_list"
        assert groups[1].id == "secondary_list"

    def test_load_groups_with_i18n(self, temp_config_dir: Path) -> None:
        """Load groups with i18n should preserve both keys and structure."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="de")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        
        # Keys preserved
        assert groups[0].title_key == "config.list.main"
        assert groups[0].items[0].label_key == "list.item.first"
        
        # Translations work
        assert factory.get_list_group_title(groups[0]) == "Hauptliste"
        assert factory.get_list_item_label(groups[0].items[0]) == "Erstes Element"

    def test_nested_item_labels_translated(self, temp_config_dir: Path) -> None:
        """Nested item labels should be translatable."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="de")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        
        nested_item = groups[0].items[0].children[0]
        label = factory.get_list_item_label(nested_item)
        assert label == "Verschachteltes Element"

    def test_all_items_translated_in_group(self, temp_config_dir: Path) -> None:
        """All items in a group should be translatable."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="en")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        
        group = groups[0]
        labels = [factory.get_list_item_label(item) for item in group.items]
        assert "First Item" in labels
        assert "Second Item" in labels


class TestListFactoryLocaleSwitch:
    """Test switching locales."""

    def test_switch_locale_with_set_i18n_factory(self, temp_config_dir: Path) -> None:
        """Should switch locale by setting new i18n_factory."""
        i18n_de = I18nFactory(config_path=temp_config_dir, locale="de")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n_de)
        groups = factory.load_list_groups()
        
        title_de = factory.get_list_group_title(groups[0])
        assert title_de == "Hauptliste"
        
        # Switch to English
        i18n_en = I18nFactory(config_path=temp_config_dir, locale="en")
        factory.set_i18n_factory(i18n_en)
        
        title_en = factory.get_list_group_title(groups[0])
        assert title_en == "Main List"

    def test_cache_cleared_on_locale_switch(self, temp_config_dir: Path) -> None:
        """Cache should be cleared when switching locales."""
        i18n_de = I18nFactory(config_path=temp_config_dir, locale="de")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n_de)
        groups = factory.load_list_groups()
        
        # Translate to populate cache
        factory.get_list_group_title(groups[0])
        cache_size_de = len(factory._translated_cache)
        assert cache_size_de > 0
        
        # Switch to English (should clear cache)
        i18n_en = I18nFactory(config_path=temp_config_dir, locale="en")
        factory.set_i18n_factory(i18n_en)
        assert factory._translated_cache == {}


class TestListFactoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir: Path) -> None:
        """Should return default when factory is None."""
        factory = ListFactory(config_path=temp_config_dir)
        result = factory._translate("nonexistent.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir: Path) -> None:
        """Should return key when factory is None and no default."""
        factory = ListFactory(config_path=temp_config_dir)
        result = factory._translate("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translate_empty_key(self, temp_config_dir: Path) -> None:
        """Should handle empty keys gracefully."""
        i18n = I18nFactory(config_path=temp_config_dir)
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        result = factory._translate("")
        assert result == ""

    def test_caching_works_for_repeated_translations(self, temp_config_dir: Path) -> None:
        """Should cache translations and return cached values."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="de")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        
        key = "list.item.first"
        result1 = factory._translate(key)
        cache_size_1 = len(factory._translated_cache)
        
        result2 = factory._translate(key)
        cache_size_2 = len(factory._translated_cache)
        
        assert result1 == result2
        assert cache_size_1 == cache_size_2

    def test_multiple_factory_instances_independent(self, temp_config_dir: Path) -> None:
        """Multiple ListFactory instances should be independent."""
        i18n_de = I18nFactory(config_path=temp_config_dir, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir, locale="en")
        
        factory_de = ListFactory(config_path=temp_config_dir, i18n_factory=i18n_de)
        factory_en = ListFactory(config_path=temp_config_dir, i18n_factory=i18n_en)
        
        groups_de = factory_de.load_list_groups()
        groups_en = factory_en.load_list_groups()
        
        title_de = factory_de.get_list_group_title(groups_de[0])
        title_en = factory_en.get_list_group_title(groups_en[0])
        
        assert title_de == "Hauptliste"
        assert title_en == "Main List"
        assert title_de != title_en

    def test_get_list_item_label_all_items_in_secondary_list(self, temp_config_dir: Path) -> None:
        """Should translate items from secondary list."""
        i18n = I18nFactory(config_path=temp_config_dir, locale="en")
        factory = ListFactory(config_path=temp_config_dir, i18n_factory=i18n)
        groups = factory.load_list_groups()
        
        secondary_group = groups[1]
        label = factory.get_list_item_label(secondary_group.items[0])
        assert label == "Name"
