"""Tests for PanelFactory i18n integration."""

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.panel_factory import PanelConfig, PanelFactory


@pytest.fixture
def temp_config_dir() -> Generator[Path, Any, Any]:
    """Create temporary config directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Create minimal i18n files
        i18n_de = {
            "panel.explorer": "Explorer",
            "panel.properties": "Eigenschaften",
            "panel.console": "Konsole",
            "panel.output": "Ausgabe",
            "panel.debug": "Debugger",
            "tooltip.explorer": "Projekt-Explorer anzeigen",
            "tooltip.properties": "Element-Eigenschaften anzeigen",
            "tooltip.console": "Fehler und Ausgaben anzeigen",
            "tooltip.output": "Build-Ausgabe anzeigen",
            "tooltip.debug": "Variablen und Call-Stack anzeigen",
        }
        i18n_en = {
            "panel.explorer": "Explorer",
            "panel.properties": "Properties",
            "panel.console": "Console",
            "panel.output": "Output",
            "panel.debug": "Debugger",
            "tooltip.explorer": "Show project explorer",
            "tooltip.properties": "Show element properties",
            "tooltip.console": "Show errors and output",
            "tooltip.output": "Show build output",
            "tooltip.debug": "Show variables and call stack",
        }

        with open(config_dir / "i18n.de.json", "w", encoding="utf-8") as f:
            json.dump(i18n_de, f)
        with open(config_dir / "i18n.en.json", "w", encoding="utf-8") as f:
            json.dump(i18n_en, f)

        # Create test panels.json
        panels_config: dict[str, Any] = {
            "panels": [
                {
                    "id": "explorer",
                    "name_key": "panel.explorer",
                    "tooltip_key": "tooltip.explorer",
                    "area": "left",
                    "closable": False,
                    "dnd_enabled": True,
                },
                {
                    "id": "properties",
                    "name_key": "panel.properties",
                    "tooltip_key": "tooltip.properties",
                    "area": "right",
                    "closable": True,
                    "dnd_enabled": True,
                },
                {
                    "id": "console",
                    "name_key": "panel.console",
                    "tooltip_key": "tooltip.console",
                    "area": "bottom",
                    "closable": True,
                },
                {
                    "id": "output",
                    "name_key": "panel.output",
                    "tooltip_key": "tooltip.output",
                    "area": "bottom",
                    "closable": True,
                },
                {
                    "id": "debug",
                    "name_key": "panel.debug",
                    "tooltip_key": "tooltip.debug",
                    "area": "right",
                    "closable": False,
                },
            ]
        }

        with open(config_dir / "panels.json", "w", encoding="utf-8") as f:
            json.dump(panels_config, f)

        yield config_dir


@pytest.fixture
def i18n_factory_de(temp_config_dir: Path) -> I18nFactory:
    """Create I18nFactory with German locale."""
    return I18nFactory(temp_config_dir, locale="de")


@pytest.fixture
def i18n_factory_en(temp_config_dir: Path) -> I18nFactory:
    """Create I18nFactory with English locale."""
    return I18nFactory(temp_config_dir, locale="en")


class TestPanelFactoryI18nBasics:
    """Test basic i18n initialization and setup."""

    def test_panel_factory_initializes_without_i18n(self, temp_config_dir: Path) -> None:
        """Test PanelFactory can be initialized without i18n_factory."""
        factory = PanelFactory(temp_config_dir)
        assert factory._i18n_factory is None
        assert factory._translated_cache == {}

    def test_panel_factory_initializes_with_i18n(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test PanelFactory initializes with i18n_factory."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        assert factory._i18n_factory is i18n_factory_de
        assert factory._translated_cache == {}

    def test_set_i18n_factory(self, temp_config_dir: Path, i18n_factory_de: I18nFactory) -> None:
        """Test setting i18n_factory after initialization."""
        factory = PanelFactory(temp_config_dir)
        assert factory._i18n_factory is None

        factory.set_i18n_factory(i18n_factory_de)
        assert factory._i18n_factory is i18n_factory_de

    def test_set_i18n_factory_clears_cache(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test setting i18n_factory clears translation cache."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        factory._translated_cache["test.key"] = "test_value"

        i18n_factory_en = I18nFactory(temp_config_dir, locale="en")
        factory.set_i18n_factory(i18n_factory_en)

        assert factory._translated_cache == {}


class TestPanelFactoryPanelNameTranslation:
    """Test translating panel names."""

    def test_get_panel_name_without_i18n(self, temp_config_dir: Path) -> None:
        """Test get_panel_name returns key as fallback without i18n."""
        factory = PanelFactory(temp_config_dir)
        panel = PanelConfig(id="test", name_key="panel.explorer", area="left")

        name = factory.get_panel_name(panel)
        assert name == "panel.explorer"

    def test_get_panel_name_with_i18n_german(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_panel_name translates to German."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panel = PanelConfig(id="explorer", name_key="panel.explorer", area="left")

        name = factory.get_panel_name(panel)
        assert name == "Explorer"

    def test_get_panel_name_with_i18n_english(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_panel_name translates to English."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        panel = PanelConfig(id="properties", name_key="panel.properties", area="right")

        name = factory.get_panel_name(panel)
        assert name == "Properties"

    def test_get_panel_name_empty_key_returns_empty(self, temp_config_dir: Path) -> None:
        """Test get_panel_name with empty key returns empty."""
        factory = PanelFactory(temp_config_dir)
        panel = PanelConfig(id="test", name_key="", area="left")

        name = factory.get_panel_name(panel)
        assert name == ""

    def test_get_panel_name_caching(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test translation results are cached."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panel = PanelConfig(id="explorer", name_key="panel.explorer", area="left")

        name1 = factory.get_panel_name(panel)
        assert "panel.explorer" in factory._translated_cache

        name2 = factory.get_panel_name(panel)
        assert name1 == name2


class TestPanelFactoryTooltipTranslation:
    """Test translating panel tooltips."""

    def test_get_panel_tooltip_without_i18n(self, temp_config_dir: Path) -> None:
        """Test get_panel_tooltip returns key as fallback without i18n."""
        factory = PanelFactory(temp_config_dir)
        panel = PanelConfig(
            id="test",
            name_key="panel.explorer",
            area="left",
            tooltip_key="tooltip.explorer",
        )

        tooltip = factory.get_panel_tooltip(panel)
        assert tooltip == "tooltip.explorer"

    def test_get_panel_tooltip_with_i18n_german(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_panel_tooltip translates to German."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panel = PanelConfig(
            id="explorer",
            name_key="panel.explorer",
            area="left",
            tooltip_key="tooltip.explorer",
        )

        tooltip = factory.get_panel_tooltip(panel)
        assert tooltip == "Projekt-Explorer anzeigen"

    def test_get_panel_tooltip_with_i18n_english(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_panel_tooltip translates to English."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        panel = PanelConfig(
            id="properties",
            name_key="panel.properties",
            area="right",
            tooltip_key="tooltip.properties",
        )

        tooltip = factory.get_panel_tooltip(panel)
        assert tooltip == "Show element properties"

    def test_get_panel_tooltip_empty_returns_empty(self, temp_config_dir: Path) -> None:
        """Test get_panel_tooltip with empty tooltip returns empty."""
        factory = PanelFactory(temp_config_dir)
        panel = PanelConfig(id="test", name_key="panel.test", area="left", tooltip_key="")

        tooltip = factory.get_panel_tooltip(panel)
        assert tooltip == ""

    def test_get_panel_tooltip_missing_key(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_panel_tooltip with missing key returns key."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panel = PanelConfig(
            id="test",
            name_key="panel.test",
            area="left",
            tooltip_key="tooltip.missing",
        )

        tooltip = factory.get_panel_tooltip(panel)
        assert tooltip == "tooltip.missing"


class TestPanelFactoryLocaleSwitch:
    """Test switching locales and updating translations."""

    def test_switching_locale_updates_translations(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory, i18n_factory_en: I18nFactory
    ) -> None:
        """Test switching locale updates translation results."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panel = PanelConfig(id="explorer", name_key="panel.explorer", area="left")

        name_de = factory.get_panel_name(panel)
        assert name_de == "Explorer"

        # Switch to English
        factory.set_i18n_factory(i18n_factory_en)
        name_en = factory.get_panel_name(panel)
        assert name_en == "Explorer"

    def test_cache_cleared_on_locale_switch(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test translation cache is cleared when switching locales."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panel = PanelConfig(id="explorer", name_key="panel.explorer", area="left")

        factory.get_panel_name(panel)
        assert len(factory._translated_cache) > 0

        factory.set_i18n_factory(i18n_factory_de)
        assert len(factory._translated_cache) == 0


class TestPanelFactoryLoadWithTranslation:
    """Test loading panels and translating them."""

    def test_load_panels_without_i18n(self, temp_config_dir: Path) -> None:
        """Test loading panels without i18n works."""
        factory = PanelFactory(temp_config_dir)
        panels = factory.load_panels()

        assert len(panels) == 5
        assert panels[0].id == "explorer"
        assert panels[0].name_key == "panel.explorer"
        assert panels[0].tooltip_key == "tooltip.explorer"

    def test_load_panels_with_i18n(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test loading panels with i18n_factory."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panels = factory.load_panels()

        assert len(panels) == 5
        assert panels[0].id == "explorer"

        # Check we can translate the panel name
        name = factory._translate(panels[0].name_key)
        assert name == "Explorer"

    def test_all_panel_names_translated(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test all loaded panels can be translated."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panels = factory.load_panels()

        expected_names = {
            "explorer": "Explorer",
            "properties": "Eigenschaften",
            "console": "Konsole",
            "output": "Ausgabe",
            "debug": "Debugger",
        }

        for panel in panels:
            name = factory.get_panel_name(panel)
            assert name == expected_names[panel.id]

    def test_all_panel_tooltips_translated(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test all loaded panel tooltips can be translated."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        panels = factory.load_panels()

        expected_tooltips = {
            "explorer": "Projekt-Explorer anzeigen",
            "properties": "Element-Eigenschaften anzeigen",
            "console": "Fehler und Ausgaben anzeigen",
            "output": "Build-Ausgabe anzeigen",
            "debug": "Variablen und Call-Stack anzeigen",
        }

        for panel in panels:
            tooltip = factory.get_panel_tooltip(panel)
            assert tooltip == expected_tooltips[panel.id]


class TestPanelFactoryByArea:
    """Test translation with panels filtered by area."""

    def test_get_panels_by_area_with_translation(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_panels_by_area returns panels with translation support."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        right_panels = factory.get_panels_by_area("right")

        assert len(right_panels) == 2
        names = [factory.get_panel_name(p) for p in right_panels]
        assert "Properties" in names
        assert "Debugger" in names

    def test_get_panels_by_area_left(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_panels_by_area for left area."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        left_panels = factory.get_panels_by_area("left")

        assert len(left_panels) == 1
        assert left_panels[0].id == "explorer"
        assert factory.get_panel_name(left_panels[0]) == "Explorer"


class TestPanelFactoryEdgeCases:
    """Test edge cases and error handling."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir: Path) -> None:
        """Test _translate with None factory uses default."""
        factory = PanelFactory(temp_config_dir, i18n_factory=None)

        result = factory._translate("missing.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir: Path) -> None:
        """Test _translate with None factory returns key."""
        factory = PanelFactory(temp_config_dir, i18n_factory=None)

        result = factory._translate("missing.key")
        assert result == "missing.key"

    def test_translate_empty_key(self, temp_config_dir: Path, i18n_factory_de: I18nFactory) -> None:
        """Test _translate with empty key."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)

        result = factory._translate("", default="fallback")
        assert result == "fallback"

    def test_panel_with_missing_tooltip_key(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test panel without tooltip_key has empty string default."""
        factory = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)

        # Create panel without tooltip_key
        panel = PanelConfig(id="test", name_key="panel.test", area="left")
        assert panel.tooltip_key == ""

        tooltip = factory.get_panel_tooltip(panel)
        assert tooltip == ""

    def test_multiple_factory_instances_independent(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory, i18n_factory_en: I18nFactory
    ) -> None:
        """Test multiple factory instances maintain independent caches."""
        factory_de = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        factory_en = PanelFactory(temp_config_dir, i18n_factory=i18n_factory_en)

        panel = PanelConfig(id="explorer", name_key="panel.explorer", area="left")

        name_de = factory_de.get_panel_name(panel)
        name_en = factory_en.get_panel_name(panel)

        assert name_de == "Explorer"
        assert name_en == "Explorer"
        assert len(factory_de._translated_cache) == len(factory_en._translated_cache)

    def test_panel_config_serialization_with_tooltip(
        self, temp_config_dir: Path
    ) -> None:
        """Test PanelConfig with tooltip_key serializes correctly."""
        panel = PanelConfig(
            id="test",
            name_key="panel.test",
            area="left",
            tooltip_key="tooltip.test",
        )

        panel_dict = PanelFactory._panel_to_dict(panel)
        
        assert panel_dict["id"] == "test"
        assert panel_dict["tooltip_key"] == "tooltip.test"

    def test_panel_config_serialization_without_tooltip(
        self, temp_config_dir: Path
    ) -> None:
        """Test PanelConfig without tooltip_key doesn't include it in dict."""
        panel = PanelConfig(
            id="test",
            name_key="panel.test",
            area="left",
            tooltip_key="",
        )

        panel_dict = PanelFactory._panel_to_dict(panel)
        
        assert panel_dict["id"] == "test"
        assert "tooltip_key" not in panel_dict
