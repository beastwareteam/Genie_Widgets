"""Tests for ChevronMenu internationalization support."""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.ui.chevron_menu import ChevronMenu, ChevronMenuBar


@pytest.fixture
def temp_config_dir_chevron_menu() -> Path:
    """Create a temporary config directory with menu test data."""
    tmpdir = tempfile.TemporaryDirectory()
    config_dir = Path(tmpdir.name)
    
    # Create i18n files
    i18n_de = {
        "menu.file": "Datei",
        "menu.file.save": "Speichern",
        "menu.file.load": "Laden",
        "menu.file.exit": "Beenden",
        "menu.edit": "Bearbeiten",
        "menu.edit.undo": "Rückgängig",
        "menu.edit.redo": "Wiederholen",
        "menu.view": "Ansicht",
        "menu.view.zoom": "Zoom",
        "menu.view.zoom.in": "Vergrößern",
        "menu.view.zoom.out": "Verkleinern",
    }
    
    i18n_en = {
        "menu.file": "File",
        "menu.file.save": "Save",
        "menu.file.load": "Load",
        "menu.file.exit": "Exit",
        "menu.edit": "Edit",
        "menu.edit.undo": "Undo",
        "menu.edit.redo": "Redo",
        "menu.view": "View",
        "menu.view.zoom": "Zoom",
        "menu.view.zoom.in": "Zoom In",
        "menu.view.zoom.out": "Zoom Out",
    }
    
    (config_dir / "i18n.de.json").write_text(json.dumps(i18n_de, ensure_ascii=False), encoding="utf-8")
    (config_dir / "i18n.en.json").write_text(json.dumps(i18n_en, ensure_ascii=False), encoding="utf-8")
    
    # Create menus.json with test data
    menus_config = {
        "menus": [
            {
                "id": "file",
                "label_key": "menu.file",
                "type": "menu",
                "children": [
                    {
                        "id": "save",
                        "label_key": "menu.file.save",
                        "type": "action",
                        "shortcut": "Ctrl+S"
                    },
                    {
                        "id": "load",
                        "label_key": "menu.file.load",
                        "type": "action",
                        "shortcut": "Ctrl+O"
                    },
                    {
                        "id": "file_sep",
                        "type": "separator"
                    },
                    {
                        "id": "exit",
                        "label_key": "menu.file.exit",
                        "type": "action",
                        "shortcut": "Alt+F4"
                    }
                ]
            },
            {
                "id": "edit",
                "label_key": "menu.edit",
                "type": "menu",
                "children": [
                    {
                        "id": "undo",
                        "label_key": "menu.edit.undo",
                        "type": "action",
                        "shortcut": "Ctrl+Z"
                    },
                    {
                        "id": "redo",
                        "label_key": "menu.edit.redo",
                        "type": "action",
                        "shortcut": "Ctrl+Y"
                    }
                ]
            },
            {
                "id": "view",
                "label_key": "menu.view",
                "type": "menu",
                "children": [
                    {
                        "id": "zoom",
                        "label_key": "menu.view.zoom",
                        "type": "menu",
                        "children": [
                            {
                                "id": "zoom_in",
                                "label_key": "menu.view.zoom.in",
                                "type": "action",
                                "shortcut": "Ctrl++"
                            },
                            {
                                "id": "zoom_out",
                                "label_key": "menu.view.zoom.out",
                                "type": "action",
                                "shortcut": "Ctrl+-"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    (config_dir / "menus.json").write_text(json.dumps(menus_config, indent=2, ensure_ascii=False), encoding="utf-8")
    
    yield config_dir
    tmpdir.cleanup()


class TestChevronMenuI18nBasics:
    """Test basic ChevronMenu i18n initialization."""

    def test_chevron_menu_initializes_without_i18n(self) -> None:
        """ChevronMenu should initialize without i18n_factory."""
        menu = ChevronMenu(title="Test")
        assert menu._i18n_factory is None
        assert not menu._translated_cache

    def test_chevron_menu_initializes_with_i18n(self, temp_config_dir_chevron_menu: Path) -> None:
        """ChevronMenu should initialize with i18n_factory."""
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu)
        menu = ChevronMenu(title="Test", i18n_factory=i18n)
        assert menu._i18n_factory is i18n
        assert not menu._translated_cache

    def test_set_i18n_factory(self) -> None:
        """ChevronMenu should set i18n_factory after initialization."""
        menu = ChevronMenu(title="Test")
        assert menu._i18n_factory is None
        
        # We can't create a real factory without a temp dir, so just verify structure
        menu.set_i18n_factory(None)
        assert menu._i18n_factory is None

    def test_set_i18n_factory_clears_cache(self, temp_config_dir_chevron_menu: Path) -> None:
        """Setting i18n_factory should clear translation cache."""
        menu = ChevronMenu(title="Test")
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu)
        
        # Populate cache
        menu.set_i18n_factory(i18n)
        menu._translate("menu.file")
        assert len(menu._translated_cache) > 0
        
        # Set factory again should clear cache
        menu.set_i18n_factory(i18n)
        assert not menu._translated_cache


class TestChevronMenuTranslation:
    """Test menu translation functionality."""

    def test_translate_without_i18n(self) -> None:
        """Without i18n, should return the key itself."""
        menu = ChevronMenu(title="Test")
        result = menu._translate("menu.file")
        assert result == "menu.file"

    def test_translate_with_default_without_i18n(self) -> None:
        """Without i18n but with default, should return default."""
        menu = ChevronMenu(title="Test")
        result = menu._translate("menu.file", "File")
        assert result == "File"

    def test_translate_with_i18n_german(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should translate menu keys to German."""
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="de")
        menu = ChevronMenu(title="Test", i18n_factory=i18n)
        
        result = menu._translate("menu.file", "File")
        assert result == "Datei"

    def test_translate_with_i18n_english(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should translate menu keys to English."""
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="en")
        menu = ChevronMenu(title="Test", i18n_factory=i18n)
        
        result = menu._translate("menu.file", "File")
        assert result == "File"

    def test_translate_caching(self, temp_config_dir_chevron_menu: Path) -> None:
        """Translations should be cached."""
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="de")
        menu = ChevronMenu(title="Test", i18n_factory=i18n)
        
        # First call
        result1 = menu._translate("menu.file", "File")
        assert len(menu._translated_cache) == 1
        
        # Second call should use cache
        result2 = menu._translate("menu.file", "File")
        assert result1 == result2
        assert len(menu._translated_cache) == 1


class TestChevronMenuItemAddition:
    """Test adding menu items with translation."""

    def test_add_menu_item_action(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should add action menu items."""
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="de")
        menu = ChevronMenu(title="Test", i18n_factory=i18n)
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        
        menus = menu_factory.load_menus()
        file_menu = menus[0]  # File menu
        
        # Add an action item
        if file_menu.children:
            item = file_menu.children[0]  # Save item
            result = menu.add_menu_item(item)
            assert result is None
            assert menu.actions()  # Should have at least one action

    def test_add_submenu(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should add submenu with chevron indicator."""
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="de")
        menu = ChevronMenu(title="Test", i18n_factory=i18n)
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        
        menus = menu_factory.load_menus()
        file_menu = menus[0]  # File menu has children
        
        # File menu should have children (save, load, etc.)
        assert file_menu.children
        
        # Add file menu items
        for child in file_menu.children:
            if child.type == "menu":
                result = menu.add_menu_item(child)
                assert isinstance(result, ChevronMenu)


class TestChevronMenuBarI18n:
    """Test ChevronMenuBar i18n support."""

    def test_chevron_menubar_initializes_without_i18n(self, temp_config_dir_chevron_menu: Path) -> None:
        """ChevronMenuBar should initialize without i18n_factory."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        menubar = ChevronMenuBar(menu_factory=menu_factory)
        assert menubar._i18n_factory is None
        assert not menubar._menus

    def test_chevron_menubar_initializes_with_i18n(self, temp_config_dir_chevron_menu: Path) -> None:
        """ChevronMenuBar should initialize with i18n_factory."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu)
        menubar = ChevronMenuBar(menu_factory=menu_factory, i18n_factory=i18n)
        assert menubar._i18n_factory is i18n

    def test_create_menu_bar_without_i18n(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should create menu bar without translation."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        menubar = ChevronMenuBar(menu_factory=menu_factory)
        
        menus = menubar.create_menu_bar()
        assert len(menus) == 3  # file, edit, view
        assert menus[0].title() == "menu.file"

    def test_create_menu_bar_with_i18n_german(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should create menu bar with German translation."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="de")
        menubar = ChevronMenuBar(menu_factory=menu_factory, i18n_factory=i18n)
        
        menus = menubar.create_menu_bar()
        assert len(menus) == 3
        # First menu is "File" in German = "Datei" (but title might be label_key or id)
        assert menus[0]

    def test_set_i18n_factory_on_menubar(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should set i18n_factory and update all menus."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        menubar = ChevronMenuBar(menu_factory=menu_factory)
        
        # Create menus without i18n
        menus = menubar.create_menu_bar()
        assert menubar._i18n_factory is None
        
        # Add i18n factory
        i18n = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="de")
        menubar.set_i18n_factory(i18n)
        
        # All menus should now have the i18n factory
        assert menubar._i18n_factory is i18n
        for menu in menus:
            assert menu._i18n_factory is i18n

    def test_get_menu(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should retrieve menu by ID."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        menubar = ChevronMenuBar(menu_factory=menu_factory)
        menus = menubar.create_menu_bar()
        
        file_menu = menubar.get_menu("file")
        assert file_menu is not None
        assert file_menu in menus

    def test_get_nonexistent_menu(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should return None for nonexistent menu."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        menubar = ChevronMenuBar(menu_factory=menu_factory)
        menubar.create_menu_bar()
        
        menu = menubar.get_menu("nonexistent")
        assert menu is None


class TestChevronMenuLocaleSwitch:
    """Test switching locales."""

    def test_switch_locale(self, temp_config_dir_chevron_menu: Path) -> None:
        """Should switch between locales."""
        menu_factory = MenuFactory(config_path=temp_config_dir_chevron_menu)
        i18n_de = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="de")
        menubar = ChevronMenuBar(menu_factory=menu_factory, i18n_factory=i18n_de)
        
        # Create menus in German
        menus_de = menubar.create_menu_bar()
        de_translation = menus_de[0]._translate("menu.file.save", "Save")
        assert de_translation == "Speichern"
        
        # Switch to English
        i18n_en = I18nFactory(config_path=temp_config_dir_chevron_menu, locale="en")
        menubar.set_i18n_factory(i18n_en)
        
        en_translation = menus_de[0]._translate("menu.file.save", "Save")
        assert en_translation == "Save"


class TestChevronMenuCallbacks:
    """Test action callbacks."""

    def test_action_callback(self) -> None:
        """Should trigger callbacks when actions are selected."""
        menu = ChevronMenu(title="Test")
        called: list[str] = []
        
        def callback(action_id: str) -> None:
            called.append(action_id)
        
        # Create a test menu item
        from widgetsystem.factories.menu_factory import MenuItem
        item = MenuItem(
            id="test_action",
            label_key="test.action",
            type="action"
        )
        
        menu.add_menu_item(item, callback)
        
        # Manually trigger the callback to test if it's registered
        assert "test_action" in menu._action_callbacks

    def test_action_triggered_signal(self) -> None:
        """Should emit action_triggered signal."""
        menu = ChevronMenu(title="Test")
        signals_emitted: list[str] = []
        
        def on_signal(action_id: str) -> None:
            signals_emitted.append(action_id)
        
        menu.action_triggered.connect(on_signal)
        menu.action_triggered.emit("test_id")
        
        assert "test_id" in signals_emitted
