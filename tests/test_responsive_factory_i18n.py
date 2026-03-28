"""Tests for ResponsiveFactory internationalization support."""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.responsive_factory import ResponsiveFactory


@pytest.fixture
def temp_config_dir_responsive() -> Path:
    """Create a temporary config directory with responsive test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        
        # Create i18n files
        i18n_de = {
            "breakpoint.desktop": "Schreibtisch",
            "breakpoint.tablet": "Tablet",
            "breakpoint.mobile": "Mobil",
            "breakpoint.wide": "Breit",
            "config.breakpoint.small": "Klein",
            "config.breakpoint.large": "Groß",
        }
        
        i18n_en = {
            "breakpoint.desktop": "Desktop",
            "breakpoint.tablet": "Tablet",
            "breakpoint.mobile": "Mobile",
            "breakpoint.wide": "Wide",
            "config.breakpoint.small": "Small",
            "config.breakpoint.large": "Large",
        }
        
        (config_dir / "i18n.de.json").write_text(json.dumps(i18n_de, ensure_ascii=False), encoding="utf-8")
        (config_dir / "i18n.en.json").write_text(json.dumps(i18n_en, ensure_ascii=False), encoding="utf-8")
        
        # Create responsive.json with test data
        responsive_config = {
            "breakpoints": [
                {
                    "id": "desktop",
                    "min_width": 1200,
                    "name": "Desktop",
                    "name_key": "breakpoint.desktop"
                },
                {
                    "id": "tablet",
                    "min_width": 768,
                    "max_width": 1199,
                    "name": "Tablet",
                    "name_key": "breakpoint.tablet"
                },
                {
                    "id": "mobile",
                    "max_width": 767,
                    "name": "Mobile",
                    "name_key": "breakpoint.mobile"
                },
                {
                    "id": "wide",
                    "min_width": 1920,
                    "name": "Wide",
                    "name_key": "breakpoint.wide"
                }
            ],
            "rules": [
                {
                    "id": "rule_hide_left_mobile",
                    "panel_id": "left_panel",
                    "breakpoint": "mobile",
                    "action": "hide"
                },
                {
                    "id": "rule_hide_bottom_tablet",
                    "panel_id": "bottom_panel",
                    "breakpoint": "tablet",
                    "action": "hide"
                }
            ]
        }
        
        (config_dir / "responsive.json").write_text(json.dumps(responsive_config, indent=2, ensure_ascii=False), encoding="utf-8")
        
        yield config_dir


class TestResponsiveFactoryI18nBasics:
    """Test basic ResponsiveFactory i18n initialization."""

    def test_responsive_factory_initializes_without_i18n(self, temp_config_dir_responsive: Path) -> None:
        """ResponsiveFactory should initialize without i18n_factory."""
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive)
        assert factory._i18n_factory is None
        assert factory._translated_cache == {}

    def test_responsive_factory_initializes_with_i18n(self, temp_config_dir_responsive: Path) -> None:
        """ResponsiveFactory should initialize with i18n_factory."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive)
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        assert factory._i18n_factory is i18n
        assert factory._translated_cache == {}

    def test_set_i18n_factory(self, temp_config_dir_responsive: Path) -> None:
        """ResponsiveFactory should set i18n_factory after initialization."""
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive)
        i18n = I18nFactory(config_path=temp_config_dir_responsive)
        factory.set_i18n_factory(i18n)
        assert factory._i18n_factory is i18n

    def test_set_i18n_factory_clears_cache(self, temp_config_dir_responsive: Path) -> None:
        """Setting i18n_factory should clear translation cache."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive)
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        
        # Populate cache
        factory._translate("breakpoint.desktop")
        assert len(factory._translated_cache) > 0
        
        # Set factory again
        factory.set_i18n_factory(i18n)
        assert factory._translated_cache == {}


class TestResponsiveFactoryBreakpointTranslation:
    """Test breakpoint name translation."""

    def test_get_breakpoint_name_without_i18n(self, temp_config_dir_responsive: Path) -> None:
        """Without i18n, should return the name field."""
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive)
        breakpoints = factory.load_breakpoints()
        name = factory.get_breakpoint_name(breakpoints[0])
        assert name == "Desktop"

    def test_get_breakpoint_name_with_i18n_german(self, temp_config_dir_responsive: Path) -> None:
        """Should translate breakpoint name to German."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive, locale="de")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        breakpoints = factory.load_breakpoints()
        name = factory.get_breakpoint_name(breakpoints[0])
        assert name == "Schreibtisch"

    def test_get_breakpoint_name_with_i18n_english(self, temp_config_dir_responsive: Path) -> None:
        """Should translate breakpoint name to English."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive, locale="en")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        breakpoints = factory.load_breakpoints()
        name = factory.get_breakpoint_name(breakpoints[0])
        assert name == "Desktop"


class TestResponsiveFactoryLoadWithTranslation:
    """Test loading breakpoints with translation."""

    def test_load_breakpoints_without_i18n(self, temp_config_dir_responsive: Path) -> None:
        """Load breakpoints without i18n should work normally."""
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive)
        breakpoints = factory.load_breakpoints()
        assert len(breakpoints) == 4
        assert breakpoints[0].id == "desktop"
        assert breakpoints[1].id == "tablet"

    def test_load_breakpoints_with_i18n(self, temp_config_dir_responsive: Path) -> None:
        """Load breakpoints with i18n should preserve keys and structure."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive, locale="de")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        breakpoints = factory.load_breakpoints()
        
        # Keys preserved
        assert breakpoints[0].name_key == "breakpoint.desktop"
        
        # Translations work
        assert factory.get_breakpoint_name(breakpoints[0]) == "Schreibtisch"
        assert factory.get_breakpoint_name(breakpoints[1]) == "Tablet"

    def test_all_breakpoints_translated(self, temp_config_dir_responsive: Path) -> None:
        """All breakpoints should be translatable."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive, locale="en")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        breakpoints = factory.load_breakpoints()
        
        names = [factory.get_breakpoint_name(bp) for bp in breakpoints]
        assert "Desktop" in names
        assert "Tablet" in names
        assert "Mobile" in names
        assert "Wide" in names


class TestResponsiveFactoryLocaleSwitch:
    """Test switching locales."""

    def test_switch_locale_with_set_i18n_factory(self, temp_config_dir_responsive: Path) -> None:
        """Should switch locale by setting new i18n_factory."""
        i18n_de = I18nFactory(config_path=temp_config_dir_responsive, locale="de")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n_de)
        breakpoints = factory.load_breakpoints()
        
        name_de = factory.get_breakpoint_name(breakpoints[0])
        assert name_de == "Schreibtisch"
        
        # Switch to English
        i18n_en = I18nFactory(config_path=temp_config_dir_responsive, locale="en")
        factory.set_i18n_factory(i18n_en)
        
        name_en = factory.get_breakpoint_name(breakpoints[0])
        assert name_en == "Desktop"

    def test_cache_cleared_on_locale_switch(self, temp_config_dir_responsive: Path) -> None:
        """Cache should be cleared when switching locales."""
        i18n_de = I18nFactory(config_path=temp_config_dir_responsive, locale="de")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n_de)
        breakpoints = factory.load_breakpoints()
        
        # Translate to populate cache
        factory.get_breakpoint_name(breakpoints[0])
        cache_size_de = len(factory._translated_cache)
        assert cache_size_de > 0
        
        # Switch to English (should clear cache)
        i18n_en = I18nFactory(config_path=temp_config_dir_responsive, locale="en")
        factory.set_i18n_factory(i18n_en)
        assert factory._translated_cache == {}


class TestResponsiveFactoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir_responsive: Path) -> None:
        """Should return default when factory is None."""
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive)
        result = factory._translate("nonexistent.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir_responsive: Path) -> None:
        """Should return key when factory is None and no default."""
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive)
        result = factory._translate("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translate_empty_key(self, temp_config_dir_responsive: Path) -> None:
        """Should handle empty keys gracefully."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive)
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        result = factory._translate("")
        assert result == ""

    def test_get_breakpoint_name_without_name_key(self, temp_config_dir_responsive: Path) -> None:
        """Should return name field when name_key is empty."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive, locale="de")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        
        # Create breakpoint without name_key
        from widgetsystem.factories.responsive_factory import Breakpoint
        bp = Breakpoint(
            id="test",
            min_width=1024,
            max_width=1920,
            name="Original Name",
            name_key=""
        )
        
        name = factory.get_breakpoint_name(bp)
        assert name == "Original Name"

    def test_caching_works_for_repeated_translations(self, temp_config_dir_responsive: Path) -> None:
        """Should cache translations and return cached values."""
        i18n = I18nFactory(config_path=temp_config_dir_responsive, locale="de")
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n)
        
        key = "breakpoint.desktop"
        result1 = factory._translate(key)
        cache_size_1 = len(factory._translated_cache)
        
        result2 = factory._translate(key)
        cache_size_2 = len(factory._translated_cache)
        
        assert result1 == result2
        assert cache_size_1 == cache_size_2

    def test_multiple_factory_instances_independent(self, temp_config_dir_responsive: Path) -> None:
        """Multiple ResponsiveFactory instances should be independent."""
        i18n_de = I18nFactory(config_path=temp_config_dir_responsive, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_responsive, locale="en")
        
        factory_de = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n_de)
        factory_en = ResponsiveFactory(config_path=temp_config_dir_responsive, i18n_factory=i18n_en)
        
        breakpoints_de = factory_de.load_breakpoints()
        breakpoints_en = factory_en.load_breakpoints()
        
        name_de = factory_de.get_breakpoint_name(breakpoints_de[0])
        name_en = factory_en.get_breakpoint_name(breakpoints_en[0])
        
        assert name_de == "Schreibtisch"
        assert name_en == "Desktop"
        assert name_de != name_en

    def test_load_responsive_rules(self, temp_config_dir_responsive: Path) -> None:
        """Should load responsive rules without requiring i18n."""
        factory = ResponsiveFactory(config_path=temp_config_dir_responsive)
        rules = factory.load_responsive_rules()
        assert len(rules) == 2
        assert rules[0].id == "rule_hide_left_mobile"
