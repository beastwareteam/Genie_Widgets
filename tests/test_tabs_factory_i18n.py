"""Tests for TabsFactory i18n integration."""

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.tabs_factory import Tab, TabGroup, TabsFactory


@pytest.fixture
def temp_config_dir() -> Generator[Path, Any, None]:
    """Create temporary config directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Create minimal i18n files
        i18n_de = {
            "tabs.workspace": "Arbeitsbereich",
            "tabs.tools": "Werkzeuge",
            "tab.editor": "Editor",
            "tab.console": "Konsole",
            "tab.debug": "Debugger",
            "tab.settings": "Einstellungen",
            "tooltip.editor": "Editor für Dateien",
            "tooltip.console": "Ausgabe-Konsole",
        }
        i18n_en = {
            "tabs.workspace": "Workspace",
            "tabs.tools": "Tools",
            "tab.editor": "Editor",
            "tab.console": "Console",
            "tab.debug": "Debugger",
            "tab.settings": "Settings",
            "tooltip.editor": "File editor",
            "tooltip.console": "Output console",
        }

        with open(config_dir / "i18n.de.json", "w", encoding="utf-8") as f:
            json.dump(i18n_de, f)
        with open(config_dir / "i18n.en.json", "w", encoding="utf-8") as f:
            json.dump(i18n_en, f)

        # Create test tabs.json
        tabs_config: dict[str, Any] = {
            "tab_groups": [
                {
                    "id": "workspace",
                    "title_key": "tabs.workspace",
                    "dock_area": "center",
                    "orientation": "horizontal",
                    "tabs": [
                        {
                            "id": "editor",
                            "title_key": "tab.editor",
                            "component": "editor_widget",
                            "tooltip": "tooltip.editor",
                            "closable": True,
                        },
                        {
                            "id": "console",
                            "title_key": "tab.console",
                            "component": "console_widget",
                            "tooltip": "tooltip.console",
                            "closable": True,
                            "children": [
                                {
                                    "id": "console_error",
                                    "title_key": "tab.console",
                                    "component": "console_error",
                                }
                            ],
                        },
                    ],
                },
                {
                    "id": "tools",
                    "title_key": "tabs.tools",
                    "dock_area": "right",
                    "orientation": "vertical",
                    "tabs": [
                        {
                            "id": "debug",
                            "title_key": "tab.debug",
                            "component": "debug_widget",
                        },
                        {
                            "id": "settings",
                            "title_key": "tab.settings",
                            "component": "settings_widget",
                        },
                    ],
                },
            ]
        }

        with open(config_dir / "tabs.json", "w", encoding="utf-8") as f:
            json.dump(tabs_config, f)

        yield config_dir


@pytest.fixture
def i18n_factory_de(temp_config_dir: Path) -> I18nFactory:
    """Create I18nFactory with German locale."""
    return I18nFactory(temp_config_dir, locale="de")


@pytest.fixture
def i18n_factory_en(temp_config_dir: Path) -> I18nFactory:
    """Create I18nFactory with English locale."""
    return I18nFactory(temp_config_dir, locale="en")


class TestTabsFactoryI18nBasics:
    """Test basic i18n initialization and setup."""

    def test_tabs_factory_initializes_without_i18n(self, temp_config_dir: Path) -> None:
        """Test TabsFactory can be initialized without i18n_factory."""
        factory = TabsFactory(temp_config_dir)
        assert factory._i18n_factory is None
        assert factory._translated_cache == {}

    def test_tabs_factory_initializes_with_i18n(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test TabsFactory initializes with i18n_factory."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        assert factory._i18n_factory is i18n_factory_de
        assert factory._translated_cache == {}

    def test_set_i18n_factory(self, temp_config_dir: Path, i18n_factory_de: I18nFactory) -> None:
        """Test setting i18n_factory after initialization."""
        factory = TabsFactory(temp_config_dir)
        assert factory._i18n_factory is None

        factory.set_i18n_factory(i18n_factory_de)
        assert factory._i18n_factory is i18n_factory_de

    def test_set_i18n_factory_clears_cache(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test setting i18n_factory clears translation cache."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        factory._translated_cache["test.key"] = "test_value"

        i18n_factory_en = I18nFactory(temp_config_dir, locale="en")
        factory.set_i18n_factory(i18n_factory_en)

        assert factory._translated_cache == {}


class TestTabsFactoryTabTitleTranslation:
    """Test translating tab titles."""

    def test_get_tab_title_without_i18n(self, temp_config_dir: Path) -> None:
        """Test get_tab_title returns key as fallback without i18n."""
        factory = TabsFactory(temp_config_dir)
        tab = Tab(id="test", title_key="tab.editor", component="editor")

        title = factory.get_tab_title(tab)
        assert title == "tab.editor"

    def test_get_tab_title_with_i18n_german(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_tab_title translates to German."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        tab = Tab(id="editor", title_key="tab.editor", component="editor")

        title = factory.get_tab_title(tab)
        assert title == "Editor"

    def test_get_tab_title_with_i18n_english(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_tab_title translates to English."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        tab = Tab(id="editor", title_key="tab.editor", component="editor")

        title = factory.get_tab_title(tab)
        assert title == "Editor"

    def test_get_tab_title_empty_key_returns_empty(self, temp_config_dir: Path) -> None:
        """Test get_tab_title with empty key returns empty."""
        factory = TabsFactory(temp_config_dir)
        tab = Tab(id="test", title_key="", component="test")

        title = factory.get_tab_title(tab)
        assert title == ""

    def test_get_tab_title_caching(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test translation results are cached."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        tab = Tab(id="editor", title_key="tab.editor", component="editor")

        title1 = factory.get_tab_title(tab)
        assert "tab.editor" in factory._translated_cache

        title2 = factory.get_tab_title(tab)
        assert title1 == title2


class TestTabsFactoryTooltipTranslation:
    """Test translating tab tooltips."""

    def test_get_tab_tooltip_without_i18n(self, temp_config_dir: Path) -> None:
        """Test get_tab_tooltip returns key as fallback without i18n."""
        factory = TabsFactory(temp_config_dir)
        tab = Tab(id="test", title_key="tab.editor", component="editor", tooltip="tooltip.editor")

        tooltip = factory.get_tab_tooltip(tab)
        assert tooltip == "tooltip.editor"

    def test_get_tab_tooltip_with_i18n_german(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_tab_tooltip translates to German."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        tab = Tab(id="editor", title_key="tab.editor", component="editor", tooltip="tooltip.editor")

        tooltip = factory.get_tab_tooltip(tab)
        assert tooltip == "Editor für Dateien"

    def test_get_tab_tooltip_with_i18n_english(
        self, temp_config_dir: Path, i18n_factory_en: I18nFactory
    ) -> None:
        """Test get_tab_tooltip translates to English."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_en)
        tab = Tab(id="editor", title_key="tab.editor", component="editor", tooltip="tooltip.editor")

        tooltip = factory.get_tab_tooltip(tab)
        assert tooltip == "File editor"

    def test_get_tab_tooltip_empty_returns_empty(self, temp_config_dir: Path) -> None:
        """Test get_tab_tooltip with empty tooltip returns empty."""
        factory = TabsFactory(temp_config_dir)
        tab = Tab(id="test", title_key="tab.test", component="test", tooltip="")

        tooltip = factory.get_tab_tooltip(tab)
        assert tooltip == ""

    def test_get_tab_tooltip_missing_key(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test get_tab_tooltip with missing key returns key."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        tab = Tab(id="test", title_key="tab.test", component="test", tooltip="tooltip.missing")

        tooltip = factory.get_tab_tooltip(tab)
        assert tooltip == "tooltip.missing"


class TestTabsFactoryLocaleSwitch:
    """Test switching locales and updating translations."""

    def test_switching_locale_updates_translations(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory, i18n_factory_en: I18nFactory
    ) -> None:
        """Test switching locale updates translation results."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        tab = Tab(id="editor", title_key="tab.editor", component="editor")

        title_de = factory.get_tab_title(tab)
        assert title_de == "Editor"

        # Switch to English
        factory.set_i18n_factory(i18n_factory_en)
        title_en = factory.get_tab_title(tab)
        assert title_en == "Editor"

    def test_cache_cleared_on_locale_switch(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test translation cache is cleared when switching locales."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        tab = Tab(id="editor", title_key="tab.editor", component="editor")

        factory.get_tab_title(tab)
        assert len(factory._translated_cache) > 0

        factory.set_i18n_factory(i18n_factory_de)
        assert len(factory._translated_cache) == 0


class TestTabsFactoryLoadWithTranslation:
    """Test loading tab groups and translating them."""

    def test_load_tab_groups_without_i18n(self, temp_config_dir: Path) -> None:
        """Test loading tab groups without i18n works."""
        factory = TabsFactory(temp_config_dir)
        groups = factory.load_tab_groups()

        assert len(groups) == 2
        assert groups[0].id == "workspace"
        assert groups[0].title_key == "tabs.workspace"

    def test_load_tab_groups_with_i18n(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test loading tab groups with i18n_factory."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        groups = factory.load_tab_groups()

        assert len(groups) == 2
        assert groups[0].id == "workspace"

        # Check we can translate the group title
        title = factory._translate(groups[0].title_key)
        assert title == "Arbeitsbereich"

    def test_translate_nested_tabs(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test translating nested tabs."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        groups = factory.load_tab_groups()

        # Find console tab with children
        console_tab = None
        for tab in groups[0].tabs:
            if tab.id == "console":
                console_tab = tab
                break

        assert console_tab is not None
        assert len(console_tab.children) > 0

        # Check translations work for nested tabs
        for child in console_tab.children:
            title = factory.get_tab_title(child)
            assert title == "Konsole"


class TestTabsFactoryEdgeCases:
    """Test edge cases and error handling."""

    def test_translate_with_none_factory_and_default(self, temp_config_dir: Path) -> None:
        """Test _translate with None factory uses default."""
        factory = TabsFactory(temp_config_dir, i18n_factory=None)

        result = factory._translate("missing.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_with_none_factory_no_default(self, temp_config_dir: Path) -> None:
        """Test _translate with None factory returns key."""
        factory = TabsFactory(temp_config_dir, i18n_factory=None)

        result = factory._translate("missing.key")
        assert result == "missing.key"

    def test_translate_empty_key(self, temp_config_dir: Path, i18n_factory_de: I18nFactory) -> None:
        """Test _translate with empty key."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)

        result = factory._translate("", default="fallback")
        assert result == "fallback"

    def test_tab_group_title_translation(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory
    ) -> None:
        """Test translating TabGroup title_key."""
        factory = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        group = TabGroup(
            id="test",
            title_key="tabs.workspace",
            dock_area="center",
            orientation="horizontal",
        )

        title = factory._translate(group.title_key)
        assert title == "Arbeitsbereich"

    def test_multiple_factory_instances_independent(
        self, temp_config_dir: Path, i18n_factory_de: I18nFactory, i18n_factory_en: I18nFactory
    ) -> None:
        """Test multiple factory instances maintain independent caches."""
        factory_de = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_de)
        factory_en = TabsFactory(temp_config_dir, i18n_factory=i18n_factory_en)

        tab = Tab(id="test", title_key="tab.editor", component="test")

        title_de = factory_de.get_tab_title(tab)
        title_en = factory_en.get_tab_title(tab)

        assert title_de == "Editor"
        assert title_en == "Editor"
        assert len(factory_de._translated_cache) == len(factory_en._translated_cache)
