"""Extended tests for TabsFactory - Coverage improvement tests."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from widgetsystem.factories.tabs_factory import Tab, TabGroup, TabsFactory


class TestTabDataclass:
    """Test Tab dataclass."""

    def test_tab_initialization(self) -> None:
        """Test Tab initialization with all fields."""
        tab = Tab(
            id="test_tab",
            title_key="test.title",
            component="test_component",
            closable=True,
            active=False,
        )
        assert tab.id == "test_tab"
        assert tab.title_key == "test.title"
        assert tab.component == "test_component"
        assert tab.closable is True
        assert tab.active is False
        assert tab.children == []

    def test_tab_with_defaults(self) -> None:
        """Test Tab with default values."""
        tab = Tab(id="minimal", title_key="minimal.title")
        assert tab.id == "minimal"
        assert tab.component == ""
        assert tab.closable is True
        assert tab.active is False

    def test_tab_with_children(self) -> None:
        """Test Tab with nested children."""
        child1 = Tab(id="child1", title_key="child1.title")
        child2 = Tab(id="child2", title_key="child2.title")
        parent = Tab(
            id="parent",
            title_key="parent.title",
            children=[child1, child2],
        )
        assert len(parent.children) == 2
        assert parent.children[0].id == "child1"
        assert parent.children[1].id == "child2"


class TestTabGroupDataclass:
    """Test TabGroup dataclass."""

    def test_tab_group_initialization(self) -> None:
        """Test TabGroup initialization."""
        tab_group = TabGroup(
            id="test_group",
            title_key="test.group",
            dock_area="center",
            orientation="horizontal",
        )
        assert tab_group.id == "test_group"
        assert tab_group.title_key == "test.group"
        assert tab_group.dock_area == "center"
        assert tab_group.orientation == "horizontal"
        assert tab_group.tabs == []

    def test_tab_group_with_tabs(self) -> None:
        """Test TabGroup with tabs."""
        tabs = [
            Tab(id="tab1", title_key="tab1.title"),
            Tab(id="tab2", title_key="tab2.title"),
        ]
        tab_group = TabGroup(
            id="group",
            title_key="group.title",
            dock_area="left",
            orientation="vertical",
            tabs=tabs,
        )
        assert len(tab_group.tabs) == 2

    def test_tab_group_invalid_dock_area(self) -> None:
        """Test TabGroup with invalid dock_area raises error."""
        with pytest.raises(ValueError, match="Invalid dock_area"):
            TabGroup(
                id="test",
                title_key="test",
                dock_area="invalid_area",
                orientation="horizontal",
            )

    def test_tab_group_invalid_orientation(self) -> None:
        """Test TabGroup with invalid orientation raises error."""
        with pytest.raises(ValueError, match="Invalid orientation"):
            TabGroup(
                id="test",
                title_key="test",
                dock_area="center",
                orientation="diagonal",
            )

    def test_tab_group_valid_dock_areas(self) -> None:
        """Test all valid dock areas."""
        valid_areas = ["left", "right", "bottom", "center"]
        for area in valid_areas:
            tab_group = TabGroup(
                id=f"test_{area}",
                title_key="test",
                dock_area=area,
                orientation="horizontal",
            )
            assert tab_group.dock_area == area

    def test_tab_group_valid_orientations(self) -> None:
        """Test all valid orientations."""
        valid_orientations = ["horizontal", "vertical"]
        for orientation in valid_orientations:
            tab_group = TabGroup(
                id="test",
                title_key="test",
                dock_area="center",
                orientation=orientation,
            )
            assert tab_group.orientation == orientation


class TestTabsFactoryBasics:
    """Test basic TabsFactory functionality."""

    def test_initialization(self) -> None:
        """Test TabsFactory initialization."""
        factory = TabsFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.tabs_file == Path("config/tabs.json")
        assert factory._tab_groups_cache is None

    def test_initialization_with_path_object(self) -> None:
        """Test initialization with Path object."""
        factory = TabsFactory(config_path=Path("config"))
        assert factory.config_path == Path("config")


class TestLoadTabGroups:
    """Test tab group loading functionality."""

    def test_load_tab_groups_success(self) -> None:
        """Test successfully loading tab groups from config."""
        factory = TabsFactory(config_path="config")
        tab_groups = factory.load_tab_groups()
        assert isinstance(tab_groups, list)
        assert len(tab_groups) > 0
        assert all(isinstance(g, TabGroup) for g in tab_groups)

    def test_load_tab_groups_caches_result(self) -> None:
        """Test that load_tab_groups caches results."""
        factory = TabsFactory(config_path="config")
        factory.load_tab_groups()
        assert factory._tab_groups_cache is not None
        assert len(factory._tab_groups_cache) > 0

    def test_load_tab_groups_missing_file(self) -> None:
        """Test loading when file doesn't exist."""
        factory = TabsFactory(config_path="nonexistent")
        with pytest.raises(FileNotFoundError):
            factory.load_tab_groups()

    def test_load_tab_groups_invalid_json_type(self) -> None:
        """Test loading with invalid JSON structure (array instead of object)."""
        factory = TabsFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            with pytest.raises(ValueError, match="Tabs configuration must be a JSON object"):
                factory.load_tab_groups()

    def test_load_tab_groups_invalid_tab_groups_key(self) -> None:
        """Test loading when 'tab_groups' key is not an array."""
        factory = TabsFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data='{"tab_groups": "not an array"}')):
            with pytest.raises(ValueError, match="'tab_groups' must be an array"):
                factory.load_tab_groups()


class TestParseTab:
    """Test tab parsing."""

    def test_parse_valid_tab(self) -> None:
        """Test parsing a valid tab."""
        tab_dict = {
            "id": "test_tab",
            "title_key": "test.title",
            "component": "test_component",
            "closable": True,
            "active": False,
        }
        tab = TabsFactory._parse_tab(tab_dict)
        assert tab.id == "test_tab"
        assert tab.title_key == "test.title"
        assert tab.component == "test_component"
        assert tab.closable is True
        assert tab.active is False

    def test_parse_tab_with_defaults(self) -> None:
        """Test parsing tab with default values."""
        tab_dict = {"id": "minimal_tab"}
        tab = TabsFactory._parse_tab(tab_dict)
        assert tab.id == "minimal_tab"
        assert tab.title_key == ""
        assert tab.component == ""
        assert tab.closable is True
        assert tab.active is False

    def test_parse_tab_missing_id(self) -> None:
        """Test parsing tab without ID raises error."""
        tab_dict = {"title_key": "test"}
        with pytest.raises(ValueError, match="Tab 'id' must be a non-empty string"):
            TabsFactory._parse_tab(tab_dict)

    def test_parse_tab_with_children(self) -> None:
        """Test parsing tab with nested children."""
        tab_dict = {
            "id": "parent",
            "title_key": "parent.title",
            "children": [
                {"id": "child1", "title_key": "child1.title"},
                {"id": "child2", "title_key": "child2.title"},
            ],
        }
        tab = TabsFactory._parse_tab(tab_dict)
        assert tab.id == "parent"
        assert len(tab.children) == 2
        assert tab.children[0].id == "child1"
        assert tab.children[1].id == "child2"

    def test_parse_tab_invalid_children_ignored(self) -> None:
        """Test that invalid children are ignored."""
        tab_dict = {
            "id": "parent",
            "children": [
                {"id": "valid_child"},
                "invalid_child",  # Not a dict
                {"id": "another_valid"},
            ],
        }
        tab = TabsFactory._parse_tab(tab_dict)
        assert len(tab.children) == 2


class TestParseTabGroup:
    """Test tab group parsing."""

    def test_parse_valid_tab_group(self) -> None:
        """Test parsing a valid tab group."""
        group_dict = {
            "id": "test_group",
            "title_key": "test.group",
            "dock_area": "left",
            "orientation": "vertical",
            "tabs": [
                {"id": "tab1", "title_key": "tab1.title"},
            ],
        }
        group = TabsFactory._parse_tab_group(group_dict)
        assert group.id == "test_group"
        assert group.title_key == "test.group"
        assert group.dock_area == "left"
        assert group.orientation == "vertical"
        assert len(group.tabs) == 1

    def test_parse_tab_group_with_defaults(self) -> None:
        """Test parsing tab group with default values."""
        group_dict = {"id": "minimal_group"}
        group = TabsFactory._parse_tab_group(group_dict)
        assert group.id == "minimal_group"
        assert group.dock_area == "center"
        assert group.orientation == "horizontal"

    def test_parse_tab_group_missing_id(self) -> None:
        """Test parsing tab group without ID raises error."""
        group_dict = {"title_key": "test"}
        with pytest.raises(ValueError, match="TabGroup 'id' must be a non-empty string"):
            TabsFactory._parse_tab_group(group_dict)

    def test_parse_tab_group_invalid_dock_area_type(self) -> None:
        """Test parsing tab group with invalid dock_area type."""
        group_dict = {
            "id": "test_group",
            "dock_area": 123,  # Not a string
        }
        with pytest.raises(ValueError, match="dock_area must be a string"):
            TabsFactory._parse_tab_group(group_dict)

    def test_parse_tab_group_invalid_orientation_type(self) -> None:
        """Test parsing tab group with invalid orientation type."""
        group_dict = {
            "id": "test_group",
            "orientation": 123,  # Not a string
        }
        with pytest.raises(ValueError, match="orientation must be a string"):
            TabsFactory._parse_tab_group(group_dict)


class TestTabGroupQueries:
    """Test tab group query methods."""

    def test_get_tab_group(self) -> None:
        """Test getting a specific tab group."""
        factory = TabsFactory(config_path="config")
        factory.load_tab_groups()

        group = factory.get_tab_group("main_tabs")
        assert group is not None
        assert group.id == "main_tabs"

    def test_get_tab_group_lazy_loads(self) -> None:
        """Test that get_tab_group loads groups if not cached."""
        factory = TabsFactory(config_path="config")
        assert factory._tab_groups_cache is None

        group = factory.get_tab_group("main_tabs")
        assert factory._tab_groups_cache is not None
        assert group is not None

    def test_get_tab_group_nonexistent(self) -> None:
        """Test getting a nonexistent tab group."""
        factory = TabsFactory(config_path="config")
        group = factory.get_tab_group("nonexistent_group_12345")
        assert group is None

    def test_get_tab_groups_by_area(self) -> None:
        """Test getting tab groups by dock area."""
        factory = TabsFactory(config_path="config")
        groups = factory.get_tab_groups_by_area("center")
        assert isinstance(groups, list)
        assert all(g.dock_area == "center" for g in groups)

    def test_get_tab_groups_by_area_empty(self) -> None:
        """Test getting tab groups for area with no groups."""
        factory = TabsFactory(config_path="config")
        groups = factory.get_tab_groups_by_area("nonexistent_area")
        assert groups == []

    def test_list_tab_group_ids(self) -> None:
        """Test listing all tab group IDs."""
        factory = TabsFactory(config_path="config")
        ids = factory.list_tab_group_ids()
        assert isinstance(ids, list)
        assert len(ids) > 0
        assert "main_tabs" in ids


class TestTabSearch:
    """Test tab search functionality."""

    def test_find_tab_by_id(self) -> None:
        """Test finding a tab by ID."""
        factory = TabsFactory(config_path="config")
        tab = factory.find_tab_by_id("tab_overview")
        assert tab is not None
        assert tab.id == "tab_overview"

    def test_find_tab_by_id_nested(self) -> None:
        """Test finding a nested tab by ID."""
        factory = TabsFactory(config_path="config")
        tab = factory.find_tab_by_id("subtab_charts")
        assert tab is not None
        assert tab.id == "subtab_charts"

    def test_find_tab_by_id_nonexistent(self) -> None:
        """Test finding nonexistent tab returns None."""
        factory = TabsFactory(config_path="config")
        tab = factory.find_tab_by_id("nonexistent_tab_12345")
        assert tab is None

    def test_find_tab_recursive(self) -> None:
        """Test recursive tab search."""
        tabs = [
            Tab(
                id="parent",
                title_key="parent.title",
                children=[
                    Tab(id="child1", title_key="child1.title"),
                    Tab(
                        id="child2",
                        title_key="child2.title",
                        children=[
                            Tab(id="grandchild", title_key="grandchild.title"),
                        ],
                    ),
                ],
            ),
        ]

        result = TabsFactory._find_tab_recursive(tabs, "grandchild")
        assert result is not None
        assert result.id == "grandchild"

    def test_find_tab_recursive_not_found(self) -> None:
        """Test recursive search returns None when not found."""
        tabs = [
            Tab(id="tab1", title_key="tab1.title"),
            Tab(id="tab2", title_key="tab2.title"),
        ]

        result = TabsFactory._find_tab_recursive(tabs, "nonexistent")
        assert result is None


class TestFlattenTabs:
    """Test tab flattening functionality."""

    def test_get_flat_tab_list(self) -> None:
        """Test getting flattened list of tabs."""
        factory = TabsFactory(config_path="config")
        flat_tabs = factory.get_flat_tab_list("main_tabs")
        assert isinstance(flat_tabs, list)
        assert len(flat_tabs) > 0
        # Should include parent and nested tabs
        assert any(tab.id == "tab_overview" for tab in flat_tabs)
        assert any(tab.id == "subtab_charts" for tab in flat_tabs)

    def test_get_flat_tab_list_nonexistent_group(self) -> None:
        """Test flattening nonexistent group returns empty list."""
        factory = TabsFactory(config_path="config")
        flat_tabs = factory.get_flat_tab_list("nonexistent_group")
        assert flat_tabs == []

    def test_get_flat_tab_list_empty_group(self) -> None:
        """Test flattening empty group."""
        factory = TabsFactory(config_path="config")
        flat_tabs = factory.get_flat_tab_list("tabwidget")
        # tabwidget has no tabs
        assert flat_tabs == []
