"""Tests for UIConfigFactory internationalization support."""

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.ui_config_factory import UIConfigFactory


@pytest.fixture
def temp_config_dir_ui() -> Generator[Path, Any, Any]:
    """Create a temporary config directory with UI config test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Create i18n files
        i18n_de = {
            "config.page.appSettings": "Anwendungseinstellungen",
            "config.page.appSettings.desc": "Allgemeine Anwendungseinstellungen",
            "config.page.appearance": "Erscheinungsbild",
            "config.page.appearance.desc": "Visuelle Einstellungen",
            "config.widget.theme": "Theme",
            "config.widget.language": "Sprache",
            "config.widget.autoSave": "Automatisches Speichern",
            "config.property.color": "Farbe",
            "config.property.fontSize": "Schriftgröße",
            "config.property.enabled": "Aktiviert",
        }

        i18n_en = {
            "config.page.appSettings": "Application Settings",
            "config.page.appSettings.desc": "General application settings",
            "config.page.appearance": "Appearance",
            "config.page.appearance.desc": "Visual settings",
            "config.widget.theme": "Theme",
            "config.widget.language": "Language",
            "config.widget.autoSave": "Auto Save",
            "config.property.color": "Color",
            "config.property.fontSize": "Font Size",
            "config.property.enabled": "Enabled",
        }

        (config_dir / "i18n.de.json").write_text(json.dumps(i18n_de, ensure_ascii=False), encoding="utf-8")
        (config_dir / "i18n.en.json").write_text(json.dumps(i18n_en, ensure_ascii=False), encoding="utf-8")

        # Create ui_config.json with test data
        ui_config = {
            "config_pages": [
                {
                    "id": "app_settings",
                    "title_key": "config.page.appSettings",
                    "description_key": "config.page.appSettings.desc",
                    "category": "settings",
                    "icon": "settings.png",
                    "order": 1,
                    "widgets": [
                        {
                            "id": "theme_widget",
                            "type": "input",
                            "label_key": "config.widget.theme",
                            "dnd_enabled": False,
                            "resizable": False,
                            "movable": True,
                            "container": False,
                            "properties": {
                                "color": {
                                    "type": "color",
                                    "label_key": "config.property.color",
                                    "default": "#ffffff",
                                    "required": True,
                                    "options": [],
                                    "placeholder": ""
                                }
                            }
                        },
                        {
                            "id": "lang_widget",
                            "type": "input",
                            "label_key": "config.widget.language",
                            "dnd_enabled": True,
                            "resizable": False,
                            "movable": True,
                            "container": False,
                            "properties": {
                                "font_size": {
                                    "type": "number",
                                    "label_key": "config.property.fontSize",
                                    "default": 12,
                                    "required": False,
                                    "options": [],
                                    "placeholder": "Enter size"
                                }
                            }
                        }
                    ]
                },
                {
                    "id": "appearance",
                    "title_key": "config.page.appearance",
                    "description_key": "config.page.appearance.desc",
                    "category": "ui",
                    "icon": "appearance.png",
                    "order": 2,
                    "widgets": [
                        {
                            "id": "auto_save",
                            "type": "button",
                            "label_key": "config.widget.autoSave",
                            "dnd_enabled": False,
                            "resizable": False,
                            "movable": False,
                            "container": False,
                            "properties": {
                                "enabled": {
                                    "type": "boolean",
                                    "label_key": "config.property.enabled",
                                    "default": True,
                                    "required": False,
                                    "options": [],
                                    "placeholder": ""
                                }
                            }
                        }
                    ]
                }
            ]
        }

        (config_dir / "ui_config.json").write_text(json.dumps(ui_config, indent=2, ensure_ascii=False), encoding="utf-8")

        yield config_dir


class TestUIConfigFactoryI18nBasics:
    """Test basic UIConfigFactory i18n initialization."""

    def test_ui_config_factory_initializes_without_i18n(self, temp_config_dir_ui: Path) -> None:
        """UIConfigFactory should initialize without i18n_factory."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        assert factory._i18n_factory is None
        assert factory._translated_cache == {}

    def test_ui_config_factory_initializes_with_i18n(self, temp_config_dir_ui: Path) -> None:
        """UIConfigFactory should initialize with i18n_factory."""
        i18n = I18nFactory(config_path=temp_config_dir_ui)
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        assert factory._i18n_factory is i18n
        assert factory._translated_cache == {}

    def test_set_i18n_factory(self, temp_config_dir_ui: Path) -> None:
        """UIConfigFactory should set i18n_factory after initialization."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        i18n = I18nFactory(config_path=temp_config_dir_ui)
        factory.set_i18n_factory(i18n)
        assert factory._i18n_factory is i18n

    def test_set_i18n_factory_clears_cache(self, temp_config_dir_ui: Path) -> None:
        """Setting i18n_factory should clear translation cache."""
        i18n = I18nFactory(config_path=temp_config_dir_ui)
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        
        # Populate cache
        factory._translate("config.page.appSettings")
        assert len(factory._translated_cache) > 0
        
        # Set factory again
        factory.set_i18n_factory(i18n)
        assert factory._translated_cache == {}


class TestUIConfigFactoryPageTranslation:
    """Test page title and description translation."""

    def test_get_page_title_without_i18n(self, temp_config_dir_ui: Path) -> None:
        """Without i18n, should return the key itself."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        pages = factory.load_ui_config_pages()
        title = factory.get_page_title(pages[0])
        assert title == "config.page.appSettings"

    def test_get_page_title_with_i18n_german(self, temp_config_dir_ui: Path) -> None:
        """Should translate page title to German."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        pages = factory.load_ui_config_pages()
        title = factory.get_page_title(pages[0])
        assert title == "Anwendungseinstellungen"

    def test_get_page_title_with_i18n_english(self, temp_config_dir_ui: Path) -> None:
        """Should translate page title to English."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="en")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        pages = factory.load_ui_config_pages()
        title = factory.get_page_title(pages[0])
        assert title == "Application Settings"

    def test_get_page_description_without_i18n(self, temp_config_dir_ui: Path) -> None:
        """Without i18n, should return empty or the description key."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        pages = factory.load_ui_config_pages()
        desc = factory.get_page_description(pages[0])
        assert desc == "config.page.appSettings.desc" or desc == ""

    def test_get_page_description_with_i18n_german(self, temp_config_dir_ui: Path) -> None:
        """Should translate page description to German."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        pages = factory.load_ui_config_pages()
        desc = factory.get_page_description(pages[0])
        assert desc == "Allgemeine Anwendungseinstellungen"


class TestUIConfigFactoryWidgetTranslation:
    """Test widget and property translation."""

    def test_get_widget_label_without_i18n(self, temp_config_dir_ui: Path) -> None:
        """Without i18n, should return the key itself."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        pages = factory.load_ui_config_pages()
        label = factory.get_widget_label(pages[0].widgets[0])
        assert label == "config.widget.theme"

    def test_get_widget_label_with_i18n_german(self, temp_config_dir_ui: Path) -> None:
        """Should translate widget label to German."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        pages = factory.load_ui_config_pages()
        label = factory.get_widget_label(pages[0].widgets[0])
        assert label == "Theme"

    def test_get_property_label_without_i18n(self, temp_config_dir_ui: Path) -> None:
        """Without i18n, should return the key itself."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        pages = factory.load_ui_config_pages()
        widget = pages[0].widgets[0]
        prop = widget.properties["color"]
        label = factory.get_property_label(prop)
        assert label == "config.property.color"

    def test_get_property_label_with_i18n_english(self, temp_config_dir_ui: Path) -> None:
        """Should translate property label to English."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="en")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        pages = factory.load_ui_config_pages()
        widget = pages[0].widgets[0]
        prop = widget.properties["color"]
        label = factory.get_property_label(prop)
        assert label == "Color"


class TestUIConfigFactoryLoadWithTranslation:
    """Test loading UI config with translation."""

    def test_load_pages_without_i18n(self, temp_config_dir_ui: Path) -> None:
        """Load pages without i18n should work normally."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        pages = factory.load_ui_config_pages()
        assert len(pages) == 2
        assert pages[0].id == "app_settings"
        assert pages[1].id == "appearance"

    def test_load_pages_with_i18n(self, temp_config_dir_ui: Path) -> None:
        """Load pages with i18n should preserve keys and structure."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        pages = factory.load_ui_config_pages()
        
        # Keys preserved
        assert pages[0].title_key == "config.page.appSettings"
        assert pages[0].description_key == "config.page.appSettings.desc"
        
        # Translations work
        assert factory.get_page_title(pages[0]) == "Anwendungseinstellungen"
        assert factory.get_page_description(pages[0]) == "Allgemeine Anwendungseinstellungen"

    def test_all_widgets_translated(self, temp_config_dir_ui: Path) -> None:
        """All widgets should be translatable."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="en")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        pages = factory.load_ui_config_pages()
        
        page = pages[0]
        labels = [factory.get_widget_label(widget) for widget in page.widgets]
        assert "Theme" in labels
        assert "Language" in labels


class TestUIConfigFactoryLocaleSwitch:
    """Test switching locales."""

    def test_switch_locale_with_set_i18n_factory(self, temp_config_dir_ui: Path) -> None:
        """Should switch locale by setting new i18n_factory."""
        i18n_de = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n_de)
        pages = factory.load_ui_config_pages()
        
        title_de = factory.get_page_title(pages[0])
        assert title_de == "Anwendungseinstellungen"
        
        # Switch to English
        i18n_en = I18nFactory(config_path=temp_config_dir_ui, locale="en")
        factory.set_i18n_factory(i18n_en)
        
        title_en = factory.get_page_title(pages[0])
        assert title_en == "Application Settings"

    def test_cache_cleared_on_locale_switch(self, temp_config_dir_ui: Path) -> None:
        """Cache should be cleared when switching locales."""
        i18n_de = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n_de)
        pages = factory.load_ui_config_pages()
        
        # Translate to populate cache
        factory.get_page_title(pages[0])
        cache_size_de = len(factory._translated_cache)
        assert cache_size_de > 0
        
        # Switch to English (should clear cache)
        i18n_en = I18nFactory(config_path=temp_config_dir_ui, locale="en")
        factory.set_i18n_factory(i18n_en)
        assert factory._translated_cache == {}


class TestUIConfigFactoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir_ui: Path) -> None:
        """Should return default when factory is None."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        result = factory._translate("nonexistent.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir_ui: Path) -> None:
        """Should return key when factory is None and no default."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        result = factory._translate("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translate_empty_key(self, temp_config_dir_ui: Path) -> None:
        """Should handle empty keys gracefully."""
        i18n = I18nFactory(config_path=temp_config_dir_ui)
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        result = factory._translate("")
        assert result == ""

    def test_caching_works_for_repeated_translations(self, temp_config_dir_ui: Path) -> None:
        """Should cache translations and return cached values."""
        i18n = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        factory = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n)
        
        key = "config.page.appSettings"
        result1 = factory._translate(key)
        cache_size_1 = len(factory._translated_cache)
        
        result2 = factory._translate(key)
        cache_size_2 = len(factory._translated_cache)
        
        assert result1 == result2
        assert cache_size_1 == cache_size_2

    def test_multiple_factory_instances_independent(self, temp_config_dir_ui: Path) -> None:
        """Multiple UIConfigFactory instances should be independent."""
        i18n_de = I18nFactory(config_path=temp_config_dir_ui, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_ui, locale="en")
        
        factory_de = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n_de)
        factory_en = UIConfigFactory(config_path=temp_config_dir_ui, i18n_factory=i18n_en)
        
        pages_de = factory_de.load_ui_config_pages()
        pages_en = factory_en.load_ui_config_pages()
        
        title_de = factory_de.get_page_title(pages_de[0])
        title_en = factory_en.get_page_title(pages_en[0])
        
        assert title_de == "Anwendungseinstellungen"
        assert title_en == "Application Settings"
        assert title_de != title_en

    def test_get_page_by_category(self, temp_config_dir_ui: Path) -> None:
        """Should get pages by category without i18n issues."""
        factory = UIConfigFactory(config_path=temp_config_dir_ui)
        pages = factory.get_pages_by_category("settings")
        assert len(pages) == 1
        assert pages[0].id == "app_settings"
