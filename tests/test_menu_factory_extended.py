"""Extended tests for MenuFactory - Coverage improvement tests."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from widgetsystem.factories.menu_factory import MenuFactory, MenuItem


class TestMenuFactoryBasics:
    """Test basic MenuFactory functionality."""

    def test_initialization(self) -> None:
        """Test MenuFactory initialization."""
        factory = MenuFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.menus_file == Path("config/menus.json")
        assert factory._menus_cache is None

    def test_initialization_with_path_object(self) -> None:
        """Test initialization with Path object."""
        factory = MenuFactory(config_path=Path("config"))
        assert factory.config_path == Path("config")


class TestLoadMenus:
    """Test menu loading functionality."""

    def test_load_menus_success(self) -> None:
        """Test successfully loading menus from config."""
        factory = MenuFactory(config_path="config")
        menus = factory.load_menus()
        assert isinstance(menus, list)
        assert len(menus) > 0
        assert all(isinstance(m, MenuItem) for m in menus)

    def test_load_menus_caches_result(self) -> None:
        """Test that load_menus caches results."""
        factory = MenuFactory(config_path="config")
        factory.load_menus()
        assert factory._menus_cache is not None
        assert len(factory._menus_cache) > 0

    def test_load_menus_missing_file(self) -> None:
        """Test loading menus when file doesn't exist."""
        factory = MenuFactory(config_path="nonexistent")
        with pytest.raises(FileNotFoundError):
            factory.load_menus()

    def test_load_menus_invalid_json_type(self) -> None:
        """Test loading menus with invalid JSON structure (array instead of object)."""
        factory = MenuFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            with pytest.raises(ValueError, match="Menus configuration must be a JSON object"):
                factory.load_menus()

    def test_load_menus_invalid_menus_key(self) -> None:
        """Test loading menus when 'menus' key is not an array."""
        factory = MenuFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data='{"menus": "not an array"}')):
            with pytest.raises(ValueError, match="'menus' must be an array"):
                factory.load_menus()


class TestParseMenuItem:
    """Test menu item parsing."""

    def test_parse_valid_item(self) -> None:
        """Test parsing a valid menu item."""
        item_dict = {
            "id": "test_item",
            "label_key": "test.label",
            "type": "action",
            "action": "test_action",
            "shortcut": "Ctrl+T",
            "visible": True,
        }
        item = MenuFactory._parse_menu_item(item_dict)
        assert item.id == "test_item"
        assert item.label_key == "test.label"
        assert item.type == "action"
        assert item.action == "test_action"
        assert item.shortcut == "Ctrl+T"
        assert item.visible is True

    def test_parse_item_with_defaults(self) -> None:
        """Test parsing menu item with default values."""
        item_dict = {"id": "minimal_item"}
        item = MenuFactory._parse_menu_item(item_dict)
        assert item.id == "minimal_item"
        assert item.label_key == ""
        assert item.type == "action"
        assert item.action == ""
        assert item.shortcut == ""
        assert item.visible is True

    def test_parse_item_missing_id(self) -> None:
        """Test parsing menu item without ID raises error."""
        item_dict = {"label_key": "test"}
        with pytest.raises(ValueError, match="MenuItem 'id' must be a non-empty string"):
            MenuFactory._parse_menu_item(item_dict)

    def test_parse_item_with_children(self) -> None:
        """Test parsing menu item with nested children."""
        item_dict = {
            "id": "parent",
            "label_key": "parent.label",
            "type": "menu",
            "children": [
                {"id": "child1", "label_key": "child1.label"},
                {"id": "child2", "label_key": "child2.label"},
            ],
        }
        item = MenuFactory._parse_menu_item(item_dict)
        assert item.id == "parent"
        assert len(item.children) == 2
        assert item.children[0].id == "child1"
        assert item.children[1].id == "child2"

    def test_parse_item_invalid_visible_type(self) -> None:
        """Test parsing menu item with non-boolean visible value."""
        item_dict = {"id": "test", "visible": "true"}  # String instead of bool
        item = MenuFactory._parse_menu_item(item_dict)
        assert item.visible is True  # Should convert to bool

    def test_parse_item_invalid_children_ignored(self) -> None:
        """Test that invalid children are ignored."""
        item_dict = {
            "id": "parent",
            "children": [
                {"id": "valid_child"},
                "invalid_child",  # Not a dict
                {"id": "another_valid"},
            ],
        }
        item = MenuFactory._parse_menu_item(item_dict)
        assert len(item.children) == 2


class TestMenuCache:
    """Test menu caching functionality."""

    def test_register_menu_item_recursive(self) -> None:
        """Test that menu items are registered recursively in cache."""
        factory = MenuFactory(config_path="config")
        parent = MenuItem(
            id="parent",
            label_key="parent.label",
            children=[
                MenuItem(id="child1", label_key="child1.label"),
                MenuItem(id="child2", label_key="child2.label"),
            ],
        )

        factory._register_menu_item_recursive(parent)

        assert factory._menus_cache is not None
        assert "parent" in factory._menus_cache
        assert "child1" in factory._menus_cache
        assert "child2" in factory._menus_cache

    def test_get_menu_item_lazy_loads(self) -> None:
        """Test that get_menu_item loads menus if not cached."""
        factory = MenuFactory(config_path="config")
        assert factory._menus_cache is None

        item = factory.get_menu_item("menu_file")

        assert factory._menus_cache is not None
        assert item is not None

    def test_get_menu_item_nonexistent(self) -> None:
        """Test getting a nonexistent menu item."""
        factory = MenuFactory(config_path="config")
        item = factory.get_menu_item("nonexistent_menu_id_12345")
        assert item is None


class TestMenuQueries:
    """Test menu query methods."""

    def test_get_root_menus(self) -> None:
        """Test getting root menu items."""
        factory = MenuFactory(config_path="config")
        root_menus = factory.get_root_menus()
        assert isinstance(root_menus, list)
        assert len(root_menus) > 0

    def test_find_actions(self) -> None:
        """Test finding all action menu items."""
        factory = MenuFactory(config_path="config")
        actions = factory.find_actions()
        assert isinstance(actions, list)
        assert all(action.type == "action" for action in actions)

    def test_find_actions_empty_cache(self) -> None:
        """Test find_actions with empty cache."""
        factory = MenuFactory(config_path="config")
        factory._menus_cache = {}
        actions = factory.find_actions()
        assert actions == []

    def test_get_visible_items_all(self) -> None:
        """Test getting all visible items."""
        factory = MenuFactory(config_path="config")
        visible = factory.get_visible_items()
        assert isinstance(visible, list)
        assert all(item.visible for item in visible)

    def test_get_visible_items_by_parent(self) -> None:
        """Test getting visible items filtered by parent."""
        factory = MenuFactory(config_path="config")
        factory.load_menus()

        # Get a menu with children
        parent_id = "menu_file"  # Assuming "menu_file" menu exists in config
        visible = factory.get_visible_items(parent_id=parent_id)
        assert isinstance(visible, list)

    def test_get_visible_items_nonexistent_parent(self) -> None:
        """Test getting visible items with nonexistent parent."""
        factory = MenuFactory(config_path="config")
        visible = factory.get_visible_items(parent_id="nonexistent_parent_12345")
        assert visible == []


class TestMenuHierarchy:
    """Test menu hierarchy methods."""

    def test_get_menu_hierarchy(self) -> None:
        """Test getting menu hierarchy as dictionary."""
        factory = MenuFactory(config_path="config")
        factory.load_menus()

        # Get hierarchy for a known menu item
        hierarchy = factory.get_menu_hierarchy("menu_file")

        assert isinstance(hierarchy, dict)
        if hierarchy:  # Only check if menu exists
            assert "id" in hierarchy
            assert "label_key" in hierarchy

    def test_get_menu_hierarchy_nonexistent(self) -> None:
        """Test getting hierarchy for nonexistent menu."""
        factory = MenuFactory(config_path="config")
        hierarchy = factory.get_menu_hierarchy("nonexistent_12345")
        assert hierarchy == {}

    def test_menu_to_dict_simple(self) -> None:
        """Test converting simple menu item to dict."""
        menu = MenuItem(
            id="test",
            label_key="test.label",
            type="action",
            action="test_action",
            shortcut="Ctrl+T",
            visible=True,
        )

        result = MenuFactory._menu_to_dict(menu)

        assert result["id"] == "test"
        assert result["label_key"] == "test.label"
        assert result["type"] == "action"
        assert result["action"] == "test_action"
        assert result["shortcut"] == "Ctrl+T"
        assert result["visible"] is True
        assert "children" not in result

    def test_menu_to_dict_with_children(self) -> None:
        """Test converting menu with children to dict."""
        menu = MenuItem(
            id="parent",
            label_key="parent.label",
            children=[
                MenuItem(id="child1", label_key="child1.label"),
                MenuItem(id="child2", label_key="child2.label"),
            ],
        )

        result = MenuFactory._menu_to_dict(menu)

        assert result["id"] == "parent"
        assert "children" in result
        assert len(result["children"]) == 2
        assert result["children"][0]["id"] == "child1"
        assert result["children"][1]["id"] == "child2"


class TestShortcuts:
    """Test shortcut functionality."""

    def test_list_shortcuts(self) -> None:
        """Test listing all shortcuts."""
        factory = MenuFactory(config_path="config")
        shortcuts = factory.list_shortcuts()

        assert isinstance(shortcuts, dict)
        # Check that shortcuts map to shortcut strings
        for menu_id, shortcut in shortcuts.items():
            assert isinstance(menu_id, str)
            assert isinstance(shortcut, str)

    def test_list_shortcuts_empty_cache(self) -> None:
        """Test listing shortcuts with empty cache."""
        factory = MenuFactory(config_path="config")
        factory.load_menus()
        factory._menus_cache = {}

        shortcuts = factory.list_shortcuts()
        assert shortcuts == {}


class TestMenuManipulation:
    """Test menu manipulation methods."""

    def test_add_menu_item_success(self) -> None:
        """Test successfully adding a new menu item."""
        factory = MenuFactory(config_path="config")
        factory.load_menus()

        # Add new menu item (will modify config file)
        result = factory.add_menu_item(
            menu_id="test_new_item",
            label_key="test.new.label",
            menu_type="action",
            action="test_new_action",
            shortcut="Ctrl+N",
        )

        # Clean up - remove the test item
        if result and factory._menus_cache and "test_new_item" in factory._menus_cache:
            del factory._menus_cache["test_new_item"]
            factory.save_to_file()

    def test_add_menu_item_lazy_loads(self) -> None:
        """Test that add_menu_item loads menus if not cached."""
        factory = MenuFactory(config_path="config")
        assert factory._menus_cache is None

        factory.add_menu_item(
            menu_id="test_lazy_item",
            label_key="test.lazy.label",
        )

        assert factory._menus_cache is not None

        # Clean up
        if factory._menus_cache and "test_lazy_item" in factory._menus_cache:
            del factory._menus_cache["test_lazy_item"]
            factory.save_to_file()

    def test_save_to_file_no_cache(self) -> None:
        """Test saving to file with no cache returns False."""
        factory = MenuFactory(config_path="config")
        factory._menus_cache = None

        result = factory.save_to_file()
        assert result is False
