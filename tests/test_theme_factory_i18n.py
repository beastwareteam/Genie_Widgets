"""Tests for ThemeFactory internationalization support."""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.theme_factory import ThemeFactory


@pytest.fixture
def temp_config_dir_theme() -> Path:
    """Create a temporary config directory with theme test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        
        # Create i18n files
        i18n_de = {
            "theme.dark": "Dunkelheit",
            "theme.light": "Licht",
            "theme.ocean": "Meereswind",
            "theme.midnight": "Mitternachtsblau",
            "config.theme.default": "Standard",
            "config.theme.solid": "Fest",
        }
        
        i18n_en = {
            "theme.dark": "Darkness",
            "theme.light": "Light",
            "theme.ocean": "Ocean Breeze",
            "theme.midnight": "Midnight Blue",
            "config.theme.default": "Default",
            "config.theme.solid": "Solid",
        }
        
        (config_dir / "i18n.de.json").write_text(json.dumps(i18n_de, ensure_ascii=False), encoding="utf-8")
        (config_dir / "i18n.en.json").write_text(json.dumps(i18n_en, ensure_ascii=False), encoding="utf-8")
        
        # Create themes directory with QSS files
        (config_dir / "themes").mkdir()
        (config_dir / "themes" / "dark.qss").write_text("/* Dark Theme */")
        (config_dir / "themes" / "light.qss").write_text("/* Light Theme */")
        
        # Create themes.json with test data
        themes_config = {
            "default_theme": "dark",
            "themes": [
                {
                    "id": "dark",
                    "name": "Dark Theme",
                    "name_key": "theme.dark",
                    "stylesheet": "themes/dark.qss",
                    "tab_colors": {
                        "bar_bg": ["#1E1F21", "#252628"],
                        "bar_border": "#151617",
                        "inactive_text": "#A8A8A8",
                        "active_text": "#FFFFFF"
                    }
                },
                {
                    "id": "light",
                    "name": "Light Theme",
                    "name_key": "theme.light",
                    "stylesheet": "themes/light.qss"
                },
                {
                    "id": "ocean",
                    "name": "Ocean Breeze",
                    "name_key": "theme.ocean",
                    "stylesheet": "themes/dark.qss"
                },
                {
                    "id": "midnight",
                    "name": "Midnight Blue Pro",
                    "name_key": "theme.midnight",
                    "stylesheet": "themes/dark.qss"
                },
            ]
        }
        
        (config_dir / "themes.json").write_text(json.dumps(themes_config, indent=2, ensure_ascii=False), encoding="utf-8")
        
        yield config_dir


class TestThemeFactoryI18nBasics:
    """Test basic ThemeFactory i18n initialization."""

    def test_theme_factory_initializes_without_i18n(self, temp_config_dir_theme: Path) -> None:
        """ThemeFactory should initialize without i18n_factory."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        assert factory._i18n_factory is None
        assert factory._translated_cache == {}

    def test_theme_factory_initializes_with_i18n(self, temp_config_dir_theme: Path) -> None:
        """ThemeFactory should initialize with i18n_factory."""
        i18n = I18nFactory(config_path=temp_config_dir_theme)
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        assert factory._i18n_factory is i18n
        assert factory._translated_cache == {}

    def test_set_i18n_factory(self, temp_config_dir_theme: Path) -> None:
        """ThemeFactory should set i18n_factory after initialization."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        i18n = I18nFactory(config_path=temp_config_dir_theme)
        factory.set_i18n_factory(i18n)
        assert factory._i18n_factory is i18n

    def test_set_i18n_factory_clears_cache(self, temp_config_dir_theme: Path) -> None:
        """Setting i18n_factory should clear translation cache."""
        i18n = I18nFactory(config_path=temp_config_dir_theme)
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        
        # Populate cache
        factory._translate("theme.dark")
        assert len(factory._translated_cache) > 0
        
        # Set factory again
        factory.set_i18n_factory(i18n)
        assert factory._translated_cache == {}


class TestThemeFactoryNameTranslation:
    """Test theme name translation."""

    def test_get_theme_name_without_i18n(self, temp_config_dir_theme: Path) -> None:
        """Without i18n, should return the name field."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        themes = factory.list_themes()
        name = factory.get_theme_name(themes[0])
        assert name == "Dark Theme"

    def test_get_theme_name_with_i18n_german(self, temp_config_dir_theme: Path) -> None:
        """Should translate theme name to German."""
        i18n = I18nFactory(config_path=temp_config_dir_theme, locale="de")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        themes = factory.list_themes()
        name = factory.get_theme_name(themes[0])
        assert name == "Dunkelheit"

    def test_get_theme_name_with_i18n_english(self, temp_config_dir_theme: Path) -> None:
        """Should translate theme name to English."""
        i18n = I18nFactory(config_path=temp_config_dir_theme, locale="en")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        themes = factory.list_themes()
        name = factory.get_theme_name(themes[0])
        assert name == "Darkness"


class TestThemeFactoryLoadWithTranslation:
    """Test loading themes with translation."""

    def test_load_themes_without_i18n(self, temp_config_dir_theme: Path) -> None:
        """Load themes without i18n should work normally."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        themes = factory.list_themes()
        assert len(themes) == 4
        assert themes[0].theme_id == "dark"
        assert themes[1].theme_id == "light"

    def test_load_themes_with_i18n(self, temp_config_dir_theme: Path) -> None:
        """Load themes with i18n should preserve both keys and structure."""
        i18n = I18nFactory(config_path=temp_config_dir_theme, locale="de")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        themes = factory.list_themes()
        
        # Keys preserved
        assert themes[0].name_key == "theme.dark"
        
        # Translations work
        assert factory.get_theme_name(themes[0]) == "Dunkelheit"
        assert factory.get_theme_name(themes[1]) == "Licht"

    def test_all_themes_translated(self, temp_config_dir_theme: Path) -> None:
        """All themes should be translatable."""
        i18n = I18nFactory(config_path=temp_config_dir_theme, locale="en")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        themes = factory.list_themes()
        
        names = [factory.get_theme_name(theme) for theme in themes]
        assert "Darkness" in names
        assert "Light" in names
        assert "Ocean Breeze" in names
        assert "Midnight Blue" in names


class TestThemeFactoryLocaleSwitch:
    """Test switching locales."""

    def test_switch_locale_with_set_i18n_factory(self, temp_config_dir_theme: Path) -> None:
        """Should switch locale by setting new i18n_factory."""
        i18n_de = I18nFactory(config_path=temp_config_dir_theme, locale="de")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n_de)
        themes = factory.list_themes()
        
        name_de = factory.get_theme_name(themes[0])
        assert name_de == "Dunkelheit"
        
        # Switch to English
        i18n_en = I18nFactory(config_path=temp_config_dir_theme, locale="en")
        factory.set_i18n_factory(i18n_en)
        
        name_en = factory.get_theme_name(themes[0])
        assert name_en == "Darkness"

    def test_cache_cleared_on_locale_switch(self, temp_config_dir_theme: Path) -> None:
        """Cache should be cleared when switching locales."""
        i18n_de = I18nFactory(config_path=temp_config_dir_theme, locale="de")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n_de)
        themes = factory.list_themes()
        
        # Translate to populate cache
        factory.get_theme_name(themes[0])
        cache_size_de = len(factory._translated_cache)
        assert cache_size_de > 0
        
        # Switch to English (should clear cache)
        i18n_en = I18nFactory(config_path=temp_config_dir_theme, locale="en")
        factory.set_i18n_factory(i18n_en)
        assert factory._translated_cache == {}


class TestThemeFactoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir_theme: Path) -> None:
        """Should return default when factory is None."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        result = factory._translate("nonexistent.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir_theme: Path) -> None:
        """Should return key when factory is None and no default."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        result = factory._translate("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translate_empty_key(self, temp_config_dir_theme: Path) -> None:
        """Should handle empty keys gracefully."""
        i18n = I18nFactory(config_path=temp_config_dir_theme)
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        result = factory._translate("")
        assert result == ""

    def test_get_theme_name_without_name_key(self, temp_config_dir_theme: Path) -> None:
        """Should return name field when name_key is empty."""
        i18n = I18nFactory(config_path=temp_config_dir_theme, locale="de")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        
        # Create theme without name_key
        from widgetsystem.factories.theme_factory import ThemeDefinition
        theme = ThemeDefinition(
            theme_id="test",
            name="Original Name",
            name_key="",
            file_path=Path("themes/dark.qss")
        )
        
        name = factory.get_theme_name(theme)
        assert name == "Original Name"

    def test_caching_works_for_repeated_translations(self, temp_config_dir_theme: Path) -> None:
        """Should cache translations and return cached values."""
        i18n = I18nFactory(config_path=temp_config_dir_theme, locale="de")
        factory = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n)
        
        key = "theme.dark"
        result1 = factory._translate(key)
        cache_size_1 = len(factory._translated_cache)
        
        result2 = factory._translate(key)
        cache_size_2 = len(factory._translated_cache)
        
        assert result1 == result2
        assert cache_size_1 == cache_size_2

    def test_multiple_factory_instances_independent(self, temp_config_dir_theme: Path) -> None:
        """Multiple ThemeFactory instances should be independent."""
        i18n_de = I18nFactory(config_path=temp_config_dir_theme, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_theme, locale="en")
        
        factory_de = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n_de)
        factory_en = ThemeFactory(config_path=temp_config_dir_theme, i18n_factory=i18n_en)
        
        themes_de = factory_de.list_themes()
        themes_en = factory_en.list_themes()
        
        name_de = factory_de.get_theme_name(themes_de[0])
        name_en = factory_en.get_theme_name(themes_en[0])
        
        assert name_de == "Dunkelheit"
        assert name_en == "Darkness"
        assert name_de != name_en

    def test_get_default_theme_id(self, temp_config_dir_theme: Path) -> None:
        """Should get default theme ID without requiring i18n."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        default_id = factory.get_default_theme_id()
        assert default_id == "dark"

    def test_get_default_theme(self, temp_config_dir_theme: Path) -> None:
        """Should get default theme without requiring i18n."""
        factory = ThemeFactory(config_path=temp_config_dir_theme)
        default_theme = factory.get_default_theme()
        assert default_theme is not None
        assert default_theme.theme_id == "dark"
