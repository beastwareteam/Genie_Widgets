"""Tests for ToolbarFactory."""

import pytest
from pathlib import Path

from widgetsystem.factories.toolbar_factory import (
    ToolbarConfig,
    ToolbarFactory,
    ToolbarItemConfig,
)


class TestToolbarItemConfig:
    """Tests for ToolbarItemConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default values for toolbar item."""
        item = ToolbarItemConfig()
        assert item.type == "action"
        assert item.action_id == ""
        assert item.menu_id == ""

    def test_action_item(self) -> None:
        """Test creating action item."""
        item = ToolbarItemConfig(
            type="action",
            action_id="action_save",
        )
        assert item.type == "action"
        assert item.action_id == "action_save"

    def test_menu_item(self) -> None:
        """Test creating menu item."""
        item = ToolbarItemConfig(
            type="menu",
            menu_id="layouts_menu",
            label_key="toolbar.layouts",
        )
        assert item.type == "menu"
        assert item.menu_id == "layouts_menu"
        assert item.label_key == "toolbar.layouts"


class TestToolbarConfig:
    """Tests for ToolbarConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default values for toolbar config."""
        config = ToolbarConfig(id="test", title_key="Test")
        assert config.area == "top"
        assert config.movable is True
        assert config.floatable is False
        assert config.icon_size == 24
        assert config.button_style == "icon_only"
        assert config.items == []

    def test_full_config(self) -> None:
        """Test creating config with all fields."""
        items = [
            ToolbarItemConfig(type="action", action_id="action_save"),
            ToolbarItemConfig(type="separator"),
        ]
        config = ToolbarConfig(
            id="main_toolbar",
            title_key="toolbar.title",
            area="bottom",
            movable=False,
            floatable=True,
            icon_size=32,
            button_style="text_beside_icon",
            items=items,
        )
        assert config.id == "main_toolbar"
        assert config.area == "bottom"
        assert config.icon_size == 32
        assert len(config.items) == 2

    def test_invalid_area_raises_error(self) -> None:
        """Test that invalid area raises ValueError."""
        with pytest.raises(ValueError, match="Invalid area"):
            ToolbarConfig(id="test", title_key="Test", area="invalid")


class TestToolbarFactory:
    """Tests for ToolbarFactory."""

    def test_load_toolbars_from_config(self) -> None:
        """Test loading toolbars from config file."""
        factory = ToolbarFactory(Path("config"))
        toolbars = factory.load_toolbars()

        assert len(toolbars) >= 1
        assert toolbars[0].id == "main_toolbar"

    def test_get_toolbar_config_by_id(self) -> None:
        """Test getting toolbar by ID."""
        factory = ToolbarFactory(Path("config"))
        factory.load_toolbars()

        config = factory.get_toolbar_config("main_toolbar")
        assert config is not None
        assert config.title_key == "toolbar.title"
        assert len(config.items) > 0

    def test_get_nonexistent_toolbar_returns_none(self) -> None:
        """Test getting nonexistent toolbar returns None."""
        factory = ToolbarFactory(Path("config"))
        factory.load_toolbars()

        config = factory.get_toolbar_config("nonexistent")
        assert config is None

    def test_toolbar_items_parsed_correctly(self) -> None:
        """Test that toolbar items are parsed correctly."""
        factory = ToolbarFactory(Path("config"))
        toolbars = factory.load_toolbars()

        main_toolbar = toolbars[0]
        items = main_toolbar.items

        # Check first item is action
        action_items = [i for i in items if i.type == "action"]
        assert len(action_items) > 0
        assert action_items[0].action_id.startswith("action_")

        # Check separators exist
        separator_items = [i for i in items if i.type == "separator"]
        assert len(separator_items) > 0

        # Check menu items exist
        menu_items = [i for i in items if i.type == "menu"]
        assert len(menu_items) >= 2  # layouts and themes

    def test_missing_config_file_returns_empty_list(self) -> None:
        """Test that missing config file returns empty list."""
        factory = ToolbarFactory(Path("nonexistent"))
        toolbars = factory.load_toolbars()
        assert toolbars == []

    def test_register_menu_creator(self) -> None:
        """Test registering menu creator callback."""
        factory = ToolbarFactory(Path("config"))

        called = {"count": 0}

        def mock_creator() -> None:
            called["count"] += 1
            return None

        factory.register_menu_creator("test_menu", mock_creator)
        assert "test_menu" in factory._menu_creators
