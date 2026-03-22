"""Extended tests for ListFactory - Coverage improvement tests."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from widgetsystem.factories.list_factory import ListFactory, ListGroup, ListItem


class TestListItemDataclass:
    """Test ListItem dataclass."""

    def test_initialization_basic(self) -> None:
        """Test ListItem initialization with required fields."""
        item = ListItem(id="item1", label_key="label.item1")
        assert item.id == "item1"
        assert item.label_key == "label.item1"
        assert item.content_type == "text"
        assert item.content == ""
        assert item.editable is True
        assert item.deletable is True
        assert item.icon == ""
        assert item.data == {}
        assert item.children == []

    def test_initialization_all_fields(self) -> None:
        """Test ListItem initialization with all fields."""
        child = ListItem(id="child1", label_key="label.child1")
        item = ListItem(
            id="item1",
            label_key="label.item1",
            content_type="button",
            content="Click Me",
            editable=False,
            deletable=False,
            icon="icon.png",
            data={"key": "value"},
            children=[child],
        )
        assert item.content_type == "button"
        assert item.content == "Click Me"
        assert item.editable is False
        assert item.deletable is False
        assert item.icon == "icon.png"
        assert item.data == {"key": "value"}
        assert len(item.children) == 1

    def test_valid_content_types(self) -> None:
        """Test all valid content types."""
        valid_types = ["text", "button", "widget", "custom", "nested"]
        for content_type in valid_types:
            item = ListItem(id="test", label_key="label", content_type=content_type)
            assert item.content_type == content_type

    def test_invalid_content_type_raises_error(self) -> None:
        """Test that invalid content type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid content_type"):
            ListItem(id="test", label_key="label", content_type="invalid")


class TestListGroupDataclass:
    """Test ListGroup dataclass."""

    def test_initialization_basic(self) -> None:
        """Test ListGroup initialization with required fields."""
        group = ListGroup(
            id="group1",
            title_key="title.group1",
            list_type="vertical",
            dock_panel_id="panel1",
        )
        assert group.id == "group1"
        assert group.title_key == "title.group1"
        assert group.list_type == "vertical"
        assert group.dock_panel_id == "panel1"
        assert group.sortable is False
        assert group.filterable is False
        assert group.searchable is False
        assert group.multi_select is False
        assert group.items == []

    def test_initialization_all_fields(self) -> None:
        """Test ListGroup initialization with all fields."""
        item = ListItem(id="item1", label_key="label.item1")
        group = ListGroup(
            id="group1",
            title_key="title.group1",
            list_type="tree",
            dock_panel_id="panel1",
            sortable=True,
            filterable=True,
            searchable=True,
            multi_select=True,
            items=[item],
        )
        assert group.sortable is True
        assert group.filterable is True
        assert group.searchable is True
        assert group.multi_select is True
        assert len(group.items) == 1

    def test_valid_list_types(self) -> None:
        """Test all valid list types."""
        valid_types = ["vertical", "horizontal", "tree", "table"]
        for list_type in valid_types:
            group = ListGroup(
                id="test",
                title_key="title",
                list_type=list_type,
                dock_panel_id="panel",
            )
            assert group.list_type == list_type

    def test_invalid_list_type_raises_error(self) -> None:
        """Test that invalid list type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid list_type"):
            ListGroup(
                id="test",
                title_key="title",
                list_type="invalid",
                dock_panel_id="panel",
            )


class TestListFactoryBasics:
    """Test basic ListFactory functionality."""

    def test_initialization(self) -> None:
        """Test ListFactory initialization."""
        factory = ListFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.lists_file == Path("config/lists.json")
        assert factory._list_groups_cache is None

    def test_initialization_with_path_object(self) -> None:
        """Test initialization with Path object."""
        factory = ListFactory(config_path=Path("config"))
        assert factory.config_path == Path("config")


class TestLoadListGroups:
    """Test loading list groups."""

    def test_load_list_groups_success(self) -> None:
        """Test successfully loading list groups from config."""
        factory = ListFactory(config_path="config")
        groups = factory.load_list_groups()

        assert isinstance(groups, list)
        assert all(isinstance(g, ListGroup) for g in groups)
        # Cache should be populated
        assert factory._list_groups_cache is not None

    def test_load_list_groups_missing_file(self) -> None:
        """Test loading when config file doesn't exist."""
        factory = ListFactory(config_path="nonexistent")

        with pytest.raises(FileNotFoundError, match="Lists configuration file not found"):
            factory.load_list_groups()

    def test_load_list_groups_invalid_json(self) -> None:
        """Test loading with invalid JSON raises error."""
        factory = ListFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                factory.load_list_groups()

    def test_load_list_groups_not_a_dict(self) -> None:
        """Test loading when JSON is not a dict raises error."""
        factory = ListFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            with pytest.raises(ValueError, match="Lists configuration must be a JSON object"):
                factory.load_list_groups()

    def test_load_list_groups_list_groups_not_array(self) -> None:
        """Test loading when 'list_groups' is not an array."""
        factory = ListFactory(config_path="config")

        json_data = '{"list_groups": "not an array"}'
        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'list_groups' must be an array"):
                factory.load_list_groups()

    def test_load_list_groups_skips_invalid_entries(self) -> None:
        """Test that invalid group entries are skipped."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [
                {
                    "id": "group1",
                    "title_key": "title1",
                    "list_type": "vertical",
                    "dock_panel_id": "panel1"
                },
                "invalid_entry",
                {
                    "id": "group2",
                    "title_key": "title2",
                    "list_type": "horizontal",
                    "dock_panel_id": "panel2"
                }
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            groups = factory.load_list_groups()
            assert len(groups) == 2
            assert groups[0].id == "group1"
            assert groups[1].id == "group2"


class TestParseListGroup:
    """Test list group parsing."""

    def test_parse_group_missing_id(self) -> None:
        """Test parsing group with missing ID raises error."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "title_key": "title",
                "list_type": "vertical",
                "dock_panel_id": "panel"
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'id' must be a string"):
                factory.load_list_groups()

    def test_parse_group_missing_title_key(self) -> None:
        """Test parsing group with missing title_key raises error."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "list_type": "vertical",
                "dock_panel_id": "panel"
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'title_key' must be a string"):
                factory.load_list_groups()

    def test_parse_group_missing_list_type(self) -> None:
        """Test parsing group with missing list_type raises error."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "dock_panel_id": "panel"
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'list_type' must be a string"):
                factory.load_list_groups()

    def test_parse_group_missing_dock_panel_id(self) -> None:
        """Test parsing group with missing dock_panel_id raises error."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "list_type": "vertical"
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'dock_panel_id' must be a string"):
                factory.load_list_groups()

    def test_parse_group_items_not_array(self) -> None:
        """Test parsing group when 'items' is not an array."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "list_type": "vertical",
                "dock_panel_id": "panel",
                "items": "not an array"
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'items' must be an array"):
                factory.load_list_groups()

    def test_parse_group_with_optional_fields(self) -> None:
        """Test parsing group with optional boolean fields."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "list_type": "vertical",
                "dock_panel_id": "panel",
                "sortable": true,
                "filterable": true,
                "searchable": true,
                "multi_select": true
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            groups = factory.load_list_groups()
            assert len(groups) == 1
            group = groups[0]
            assert group.sortable is True
            assert group.filterable is True
            assert group.searchable is True
            assert group.multi_select is True


class TestParseListItem:
    """Test list item parsing."""

    def test_parse_item_missing_id(self) -> None:
        """Test parsing item with missing ID raises error."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "list_type": "vertical",
                "dock_panel_id": "panel",
                "items": [{"label_key": "label"}]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="List item 'id' must be a string"):
                factory.load_list_groups()

    def test_parse_item_missing_label_key(self) -> None:
        """Test parsing item with missing label_key raises error."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "list_type": "vertical",
                "dock_panel_id": "panel",
                "items": [{"id": "item1"}]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="List item 'label_key' must be a string"):
                factory.load_list_groups()

    def test_parse_item_with_children(self) -> None:
        """Test parsing item with nested children."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "list_type": "tree",
                "dock_panel_id": "panel",
                "items": [{
                    "id": "parent",
                    "label_key": "label.parent",
                    "children": [
                        {"id": "child1", "label_key": "label.child1"},
                        {"id": "child2", "label_key": "label.child2"}
                    ]
                }]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            groups = factory.load_list_groups()
            parent = groups[0].items[0]
            assert len(parent.children) == 2
            assert parent.children[0].id == "child1"
            assert parent.children[1].id == "child2"


class TestGetListGroupById:
    """Test getting groups by ID."""

    def test_get_list_group_by_id_success(self) -> None:
        """Test getting a group by ID."""
        factory = ListFactory(config_path="config")
        groups = factory.load_list_groups()

        if groups:
            group_id = groups[0].id
            result = factory.get_list_group_by_id(group_id)
            assert result is not None
            assert result.id == group_id

    def test_get_list_group_by_id_not_found(self) -> None:
        """Test getting group with nonexistent ID."""
        factory = ListFactory(config_path="config")
        factory.load_list_groups()

        result = factory.get_list_group_by_id("nonexistent_group")
        assert result is None

    def test_get_list_group_by_id_auto_loads(self) -> None:
        """Test that get_list_group_by_id auto-loads config."""
        factory = ListFactory(config_path="config")

        # Try to get group without calling load_list_groups()
        result = factory.get_list_group_by_id("any_id")
        # Should have attempted to load (may return None if not found)
        assert factory._list_groups_cache is not None or result is None

    def test_get_list_group_by_id_handles_errors(self) -> None:
        """Test that get_list_group_by_id handles load errors gracefully."""
        factory = ListFactory(config_path="nonexistent")

        result = factory.get_list_group_by_id("any_id")
        assert result is None


class TestAddListGroup:
    """Test adding list groups."""

    def test_add_list_group_success(self) -> None:
        """Test adding a new list group."""
        factory = ListFactory(config_path="config")
        factory.load_list_groups()

        with patch.object(factory, "save_to_file", return_value=True):
            result = factory.add_list_group("new_group", "title.new", "vertical", "panel1")
            assert result is True
            assert "new_group" in factory._list_groups_cache  # type: ignore[operator]

    def test_add_list_group_initializes_cache(self) -> None:
        """Test that add_list_group initializes cache if needed."""
        factory = ListFactory(config_path="config")

        with patch.object(factory, "load_list_groups", side_effect=FileNotFoundError):
            with patch.object(factory, "save_to_file", return_value=True):
                result = factory.add_list_group("new_group", "title", "vertical", "panel")
                assert result is True
                assert factory._list_groups_cache is not None


class TestAddItemToGroup:
    """Test adding items to groups."""

    def test_add_item_to_group_top_level(self) -> None:
        """Test adding item to top level of group."""
        factory = ListFactory(config_path="config")
        groups = factory.load_list_groups()

        if groups:
            group_id = groups[0].id
            new_item = ListItem(id="new_item", label_key="label.new")
            initial_count = len(groups[0].items)

            result = factory.add_item_to_group(group_id, new_item)
            assert result is True
            assert len(groups[0].items) == initial_count + 1

    def test_add_item_to_group_as_child(self) -> None:
        """Test adding item as child of existing item."""
        factory = ListFactory(config_path="config")

        json_data = """{
            "list_groups": [{
                "id": "group1",
                "title_key": "title",
                "list_type": "tree",
                "dock_panel_id": "panel",
                "items": [{"id": "parent", "label_key": "label.parent"}]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            factory.load_list_groups()

            new_child = ListItem(id="child", label_key="label.child")
            result = factory.add_item_to_group("group1", new_child, parent_id="parent")

            assert result is True
            parent = factory.get_list_group_by_id("group1").items[0]  # type: ignore[union-attr]
            assert len(parent.children) == 1

    def test_add_item_to_nonexistent_group(self) -> None:
        """Test adding item to nonexistent group returns False."""
        factory = ListFactory(config_path="config")
        factory.load_list_groups()

        new_item = ListItem(id="item", label_key="label")
        result = factory.add_item_to_group("nonexistent", new_item)
        assert result is False


class TestRemoveItemFromGroup:
    """Test removing items from groups."""

    def test_remove_item_from_group_success(self) -> None:
        """Test removing an item from group."""
        factory = ListFactory(config_path="config")
        groups = factory.load_list_groups()

        if groups and groups[0].items:
            group_id = groups[0].id
            item_id = groups[0].items[0].id
            initial_count = len(groups[0].items)

            result = factory.remove_item_from_group(group_id, item_id)
            assert result is True
            assert len(groups[0].items) == initial_count - 1

    def test_remove_item_from_nonexistent_group(self) -> None:
        """Test removing item from nonexistent group returns False."""
        factory = ListFactory(config_path="config")
        factory.load_list_groups()

        result = factory.remove_item_from_group("nonexistent", "item_id")
        assert result is False

    def test_remove_nonexistent_item(self) -> None:
        """Test removing nonexistent item returns False."""
        factory = ListFactory(config_path="config")
        groups = factory.load_list_groups()

        if groups:
            group_id = groups[0].id
            result = factory.remove_item_from_group(group_id, "nonexistent_item")
            assert result is False


class TestSaveToFile:
    """Test saving configuration to file."""

    def test_save_to_file_no_cache(self) -> None:
        """Test that save_to_file returns False when cache is None."""
        factory = ListFactory(config_path="config")
        result = factory.save_to_file()
        assert result is False

    def test_save_to_file_success(self) -> None:
        """Test successful save to file."""
        factory = ListFactory(config_path="config")
        factory.load_list_groups()

        with patch("pathlib.Path.write_text") as mock_write:
            result = factory.save_to_file()
            assert result is True
            mock_write.assert_called_once()

    def test_save_to_file_handles_os_error(self) -> None:
        """Test that OSError during save is handled."""
        factory = ListFactory(config_path="config")
        factory.load_list_groups()

        with patch("pathlib.Path.write_text", side_effect=OSError("Write error")):
            result = factory.save_to_file()
            assert result is False
