"""Tests for LayoutFactory internationalization support."""

from collections.abc import Generator
import json
import tempfile
from pathlib import Path

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.layout_factory import LayoutDefinition, LayoutFactory

# pylint: disable=protected-access


@pytest.fixture
def temp_config_dir_layout() -> Generator[Path, None, None]:
    """Create a temporary config directory with layout test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Create i18n files
        i18n_de = {
            "layout.name.default": "Standard",
            "layout.name.custom": "Benutzerdefiniert",
            "layout.name.compact": "Kompakt",
            "layout.name.wide": "Breit",
            "config.layout.main": "Hauptdatei",
            "config.layout.alt": "Alte Datei",
        }

        i18n_en = {
            "layout.name.default": "Default",
            "layout.name.custom": "Custom",
            "layout.name.compact": "Compact",
            "layout.name.wide": "Wide",
            "config.layout.main": "Main File",
            "config.layout.alt": "Alternate File",
        }

        (config_dir / "i18n.de.json").write_text(
            json.dumps(i18n_de, ensure_ascii=False),
            encoding="utf-8",
        )
        (config_dir / "i18n.en.json").write_text(
            json.dumps(i18n_en, ensure_ascii=False),
            encoding="utf-8",
        )

        # Create test XML layout files
        layout_xml = '<?xml version="1.0"?><ui><MainWindow></MainWindow></ui>'
        (config_dir / "layout.xml").write_text(layout_xml)
        (config_dir / "layout_alt.xml").write_text(layout_xml)

        # Create layouts.json with test data
        layouts_config = {
            "default_layout_id": "default",
            "layouts": [
                {
                    "id": "default",
                    "name": "Default Layout",
                    "name_key": "layout.name.default",
                    "file": "layout.xml"
                },
                {
                    "id": "custom",
                    "name": "Custom Layout",
                    "name_key": "layout.name.custom",
                    "file": "layout_alt.xml"
                },
                {
                    "id": "compact",
                    "name": "Compact",
                    "name_key": "layout.name.compact",
                    "file": "layout.xml"
                },
                {
                    "id": "wide",
                    "name": "Wide",
                    "name_key": "layout.name.wide",
                    "file": "layout_alt.xml"
                },
            ]
        }

        (config_dir / "layouts.json").write_text(
            json.dumps(layouts_config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        yield config_dir



class TestLayoutFactoryI18nBasics:
    """Test basic LayoutFactory i18n initialization."""

    def test_layout_factory_initializes_without_i18n(self, temp_config_dir_layout: Path) -> None:
        """LayoutFactory should initialize without i18n_factory."""
        factory = LayoutFactory(config_path=temp_config_dir_layout)
        assert factory._i18n_factory is None
        assert not factory._translated_cache

    def test_layout_factory_initializes_with_i18n(self, temp_config_dir_layout: Path) -> None:
        """LayoutFactory should initialize with i18n_factory."""
        i18n = I18nFactory(config_path=temp_config_dir_layout)
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)
        assert factory._i18n_factory is i18n
        assert not factory._translated_cache

    def test_set_i18n_factory(self, temp_config_dir_layout: Path) -> None:
        """LayoutFactory should set i18n_factory after initialization."""
        factory = LayoutFactory(config_path=temp_config_dir_layout)
        i18n = I18nFactory(config_path=temp_config_dir_layout)
        factory.set_i18n_factory(i18n)
        assert factory._i18n_factory is i18n

    def test_set_i18n_factory_clears_cache(self, temp_config_dir_layout: Path) -> None:
        """Setting i18n_factory should clear translation cache."""
        i18n = I18nFactory(config_path=temp_config_dir_layout)
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)

        # Populate cache
        factory._translate("layout.name.default")
        assert len(factory._translated_cache) > 0

        # Set factory again
        factory.set_i18n_factory(i18n)
        assert not factory._translated_cache


class TestLayoutFactoryNameTranslation:
    """Test layout name translation."""

    def test_get_layout_name_without_i18n(self, temp_config_dir_layout: Path) -> None:
        """Without i18n, should return the name field."""
        factory = LayoutFactory(config_path=temp_config_dir_layout)
        layouts = factory.list_layouts()
        name = factory.get_layout_name(layouts[0])
        assert name == "Default Layout"

    def test_get_layout_name_with_i18n_german(self, temp_config_dir_layout: Path) -> None:
        """Should translate layout name to German."""
        i18n = I18nFactory(config_path=temp_config_dir_layout, locale="de")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)
        layouts = factory.list_layouts()
        name = factory.get_layout_name(layouts[0])
        assert name == "Standard"

    def test_get_layout_name_with_i18n_english(self, temp_config_dir_layout: Path) -> None:
        """Should translate layout name to English."""
        i18n = I18nFactory(config_path=temp_config_dir_layout, locale="en")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)
        layouts = factory.list_layouts()
        name = factory.get_layout_name(layouts[0])
        assert name == "Default"


class TestLayoutFactoryLoadWithTranslation:
    """Test loading layouts with translation."""

    def test_load_layouts_without_i18n(self, temp_config_dir_layout: Path) -> None:
        """Load layouts without i18n should work normally."""
        factory = LayoutFactory(config_path=temp_config_dir_layout)
        layouts = factory.list_layouts()
        assert len(layouts) == 4
        assert layouts[0].layout_id == "default"
        assert layouts[1].layout_id == "custom"

    def test_load_layouts_with_i18n(self, temp_config_dir_layout: Path) -> None:
        """Load layouts with i18n should preserve both keys and structure."""
        i18n = I18nFactory(config_path=temp_config_dir_layout, locale="de")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)
        layouts = factory.list_layouts()

        # Keys preserved
        assert layouts[0].name_key == "layout.name.default"

        # Translations work
        assert factory.get_layout_name(layouts[0]) == "Standard"
        assert factory.get_layout_name(layouts[1]) == "Benutzerdefiniert"

    def test_all_layouts_translated(self, temp_config_dir_layout: Path) -> None:
        """All layouts should be translatable."""
        i18n = I18nFactory(config_path=temp_config_dir_layout, locale="en")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)
        layouts = factory.list_layouts()

        names = [factory.get_layout_name(layout) for layout in layouts]
        assert "Default" in names
        assert "Custom" in names
        assert "Compact" in names
        assert "Wide" in names


class TestLayoutFactoryLocaleSwitch:
    """Test switching locales."""

    def test_switch_locale_with_set_i18n_factory(self, temp_config_dir_layout: Path) -> None:
        """Should switch locale by setting new i18n_factory."""
        i18n_de = I18nFactory(config_path=temp_config_dir_layout, locale="de")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n_de)
        layouts = factory.list_layouts()

        name_de = factory.get_layout_name(layouts[0])
        assert name_de == "Standard"

        # Switch to English
        i18n_en = I18nFactory(config_path=temp_config_dir_layout, locale="en")
        factory.set_i18n_factory(i18n_en)

        name_en = factory.get_layout_name(layouts[0])
        assert name_en == "Default"

    def test_cache_cleared_on_locale_switch(self, temp_config_dir_layout: Path) -> None:
        """Cache should be cleared when switching locales."""
        i18n_de = I18nFactory(config_path=temp_config_dir_layout, locale="de")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n_de)
        layouts = factory.list_layouts()

        # Translate to populate cache
        factory.get_layout_name(layouts[0])
        cache_size_de = len(factory._translated_cache)
        assert cache_size_de > 0

        # Switch to English (should clear cache)
        i18n_en = I18nFactory(config_path=temp_config_dir_layout, locale="en")
        factory.set_i18n_factory(i18n_en)
        assert not factory._translated_cache


class TestLayoutFactoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir_layout: Path) -> None:
        """Should return default when factory is None."""
        factory = LayoutFactory(config_path=temp_config_dir_layout)
        result = factory._translate("nonexistent.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir_layout: Path) -> None:
        """Should return key when factory is None and no default."""
        factory = LayoutFactory(config_path=temp_config_dir_layout)
        result = factory._translate("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translate_empty_key(self, temp_config_dir_layout: Path) -> None:
        """Should handle empty keys gracefully."""
        i18n = I18nFactory(config_path=temp_config_dir_layout)
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)
        result = factory._translate("")
        assert result == ""

    def test_get_layout_name_without_name_key(self, temp_config_dir_layout: Path) -> None:
        """Should return name field when name_key is empty."""
        i18n = I18nFactory(config_path=temp_config_dir_layout, locale="de")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)

        # Create layout without name_key
        layout = LayoutDefinition(
            layout_id="test",
            name="Original Name",
            name_key="",
            file_path=Path("layout.xml"),
        )

        name = factory.get_layout_name(layout)
        assert name == "Original Name"

    def test_caching_works_for_repeated_translations(self, temp_config_dir_layout: Path) -> None:
        """Should cache translations and return cached values."""
        i18n = I18nFactory(config_path=temp_config_dir_layout, locale="de")
        factory = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n)

        key = "layout.name.default"
        result1 = factory._translate(key)
        cache_size_1 = len(factory._translated_cache)

        result2 = factory._translate(key)
        cache_size_2 = len(factory._translated_cache)

        assert result1 == result2
        assert cache_size_1 == cache_size_2

    def test_multiple_factory_instances_independent(self, temp_config_dir_layout: Path) -> None:
        """Multiple LayoutFactory instances should be independent."""
        i18n_de = I18nFactory(config_path=temp_config_dir_layout, locale="de")
        i18n_en = I18nFactory(config_path=temp_config_dir_layout, locale="en")

        factory_de = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n_de)
        factory_en = LayoutFactory(config_path=temp_config_dir_layout, i18n_factory=i18n_en)

        layouts_de = factory_de.list_layouts()
        layouts_en = factory_en.list_layouts()

        name_de = factory_de.get_layout_name(layouts_de[0])
        name_en = factory_en.get_layout_name(layouts_en[0])

        assert name_de == "Standard"
        assert name_en == "Default"
        assert name_de != name_en

    def test_get_default_layout_id(self, temp_config_dir_layout: Path) -> None:
        """Should get default layout ID without requiring i18n."""
        factory = LayoutFactory(config_path=temp_config_dir_layout)
        default_id = factory.get_default_layout_id()
        assert default_id == "default"
