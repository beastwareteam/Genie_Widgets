"""Extended tests for UIConfigFactory - Coverage improvement tests."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from widgetsystem.factories.ui_config_factory import (
    UIConfigFactory,
    UIConfigPage,
    Widget,
    WidgetProperty,
)


class TestWidgetPropertyDataclass:
    """Test WidgetProperty dataclass."""

    def test_initialization_basic(self) -> None:
        """Test WidgetProperty initialization with required fields."""
        prop = WidgetProperty(name="test_prop", type="text")
        assert prop.name == "test_prop"
        assert prop.type == "text"
        assert prop.label_key == ""
        assert prop.default is None
        assert prop.required is False
        assert prop.options == []
        assert prop.placeholder == ""

    def test_initialization_all_fields(self) -> None:
        """Test WidgetProperty initialization with all fields."""
        options = [{"value": "opt1", "label": "Option 1"}]
        prop = WidgetProperty(
            name="color",
            type="select",
            label_key="config.color",
            default="#FF0000",
            required=True,
            options=options,
            placeholder="Select color",
        )
        assert prop.name == "color"
        assert prop.type == "select"
        assert prop.label_key == "config.color"
        assert prop.default == "#FF0000"
        assert prop.required is True
        assert prop.options == options
        assert prop.placeholder == "Select color"

    def test_valid_types(self) -> None:
        """Test all valid property types."""
        valid_types = ["text", "number", "boolean", "color", "select", "multiline"]
        for prop_type in valid_types:
            prop = WidgetProperty(name="test", type=prop_type)
            assert prop.type == prop_type

    def test_invalid_type_raises_error(self) -> None:
        """Test that invalid property type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid property type"):
            WidgetProperty(name="test", type="invalid")


class TestWidgetDataclass:
    """Test Widget dataclass."""

    def test_initialization_basic(self) -> None:
        """Test Widget initialization with required fields."""
        widget = Widget(id="test_widget", type="button")
        assert widget.id == "test_widget"
        assert widget.type == "button"
        assert widget.label_key == ""
        assert widget.properties == {}
        assert widget.dnd_enabled is True
        assert widget.resizable is False
        assert widget.movable is True
        assert widget.container is False

    def test_initialization_all_fields(self) -> None:
        """Test Widget initialization with all fields."""
        prop = WidgetProperty(name="text_prop", type="text")
        widget = Widget(
            id="custom_widget",
            type="custom",
            label_key="config.widget",
            properties={"text": prop},
            dnd_enabled=False,
            resizable=True,
            movable=False,
            container=True,
        )
        assert widget.id == "custom_widget"
        assert widget.type == "custom"
        assert widget.label_key == "config.widget"
        assert "text" in widget.properties
        assert widget.dnd_enabled is False
        assert widget.resizable is True
        assert widget.movable is False
        assert widget.container is True

    def test_valid_types(self) -> None:
        """Test all valid widget types."""
        valid_types = ["button", "input", "label", "list", "menu", "panel", "tabs", "custom"]
        for widget_type in valid_types:
            widget = Widget(id="test", type=widget_type)
            assert widget.type == widget_type

    def test_invalid_type_raises_error(self) -> None:
        """Test that invalid widget type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid widget type"):
            Widget(id="test", type="invalid")


class TestUIConfigPageDataclass:
    """Test UIConfigPage dataclass."""

    def test_initialization_basic(self) -> None:
        """Test UIConfigPage initialization with required fields."""
        page = UIConfigPage(id="test_page", title_key="config.title")
        assert page.id == "test_page"
        assert page.title_key == "config.title"
        assert page.description_key == ""
        assert page.category == "general"
        assert page.icon == ""
        assert page.order == 0
        assert page.widgets == []

    def test_initialization_all_fields(self) -> None:
        """Test UIConfigPage initialization with all fields."""
        widget = Widget(id="widget1", type="button")
        page = UIConfigPage(
            id="menus_page",
            title_key="config.menus.title",
            description_key="config.menus.desc",
            category="menus",
            icon="menu",
            order=5,
            widgets=[widget],
        )
        assert page.id == "menus_page"
        assert page.title_key == "config.menus.title"
        assert page.description_key == "config.menus.desc"
        assert page.category == "menus"
        assert page.icon == "menu"
        assert page.order == 5
        assert len(page.widgets) == 1


class TestUIConfigFactoryBasics:
    """Test basic UIConfigFactory functionality."""

    def test_initialization(self) -> None:
        """Test UIConfigFactory initialization."""
        factory = UIConfigFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.config_file == Path("config/ui_config.json")
        assert factory._pages_cache is None
        assert factory._widgets_cache is None

    def test_initialization_with_path_object(self) -> None:
        """Test initialization with Path object."""
        factory = UIConfigFactory(config_path=Path("config"))
        assert factory.config_path == Path("config")


class TestLoadUIConfigPages:
    """Test loading UI configuration pages."""

    def test_load_ui_config_pages_success(self) -> None:
        """Test successfully loading UI config pages."""
        factory = UIConfigFactory(config_path="config")
        pages = factory.load_ui_config_pages()

        assert isinstance(pages, list)
        assert len(pages) > 0
        assert all(isinstance(p, UIConfigPage) for p in pages)
        # Cache should be populated
        assert factory._pages_cache is not None
        assert len(factory._pages_cache) == len(pages)

    def test_load_ui_config_pages_missing_file(self) -> None:
        """Test loading when config file doesn't exist."""
        factory = UIConfigFactory(config_path="nonexistent")

        with pytest.raises(FileNotFoundError, match="UI config file not found"):
            factory.load_ui_config_pages()

    def test_load_ui_config_pages_invalid_json(self) -> None:
        """Test loading with invalid JSON raises error."""
        factory = UIConfigFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                factory.load_ui_config_pages()

    def test_load_ui_config_pages_not_a_dict(self) -> None:
        """Test loading when JSON is not a dict raises error."""
        factory = UIConfigFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            with pytest.raises(ValueError, match="UI config must be a JSON object"):
                factory.load_ui_config_pages()

    def test_load_ui_config_pages_config_pages_not_array(self) -> None:
        """Test loading when 'config_pages' is not an array."""
        factory = UIConfigFactory(config_path="config")

        json_data = '{"config_pages": "not an array"}'
        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'config_pages' must be an array"):
                factory.load_ui_config_pages()

    def test_load_ui_config_pages_skips_invalid_entries(self) -> None:
        """Test that invalid page entries are skipped."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [
                {"id": "page1", "title_key": "title1"},
                "invalid_entry",
                {"id": "page2", "title_key": "title2"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            pages = factory.load_ui_config_pages()
            assert len(pages) == 2
            assert pages[0].id == "page1"
            assert pages[1].id == "page2"


class TestParseConfigPage:
    """Test configuration page parsing."""

    def test_parse_page_missing_id(self) -> None:
        """Test parsing page with missing ID raises error."""
        factory = UIConfigFactory(config_path="config")

        json_data = '{"config_pages": [{"title_key": "title"}]}'
        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'id' must be a string"):
                factory.load_ui_config_pages()

    def test_parse_page_missing_title_key(self) -> None:
        """Test parsing page with missing title_key raises error."""
        factory = UIConfigFactory(config_path="config")

        json_data = '{"config_pages": [{"id": "page1"}]}'
        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="'title_key' must be a string"):
                factory.load_ui_config_pages()

    def test_parse_page_with_optional_fields(self) -> None:
        """Test parsing page with optional fields."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [{
                "id": "test_page",
                "title_key": "test.title",
                "description_key": "test.desc",
                "category": "test_cat",
                "icon": "test_icon",
                "order": 10
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            pages = factory.load_ui_config_pages()
            assert len(pages) == 1
            page = pages[0]
            assert page.description_key == "test.desc"
            assert page.category == "test_cat"
            assert page.icon == "test_icon"
            assert page.order == 10

    def test_parse_page_with_widgets(self) -> None:
        """Test parsing page with widget definitions."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [{
                "id": "page1",
                "title_key": "title",
                "widgets": [
                    {"id": "widget1", "type": "button"},
                    {"id": "widget2", "type": "input"}
                ]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            pages = factory.load_ui_config_pages()
            assert len(pages[0].widgets) == 2
            assert pages[0].widgets[0].id == "widget1"
            assert pages[0].widgets[1].id == "widget2"


class TestParseWidget:
    """Test widget parsing."""

    def test_parse_widget_missing_id(self) -> None:
        """Test parsing widget with missing ID raises error."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [{
                "id": "page1",
                "title_key": "title",
                "widgets": [{"type": "button"}]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="Widget 'id' must be a string"):
                factory.load_ui_config_pages()

    def test_parse_widget_missing_type(self) -> None:
        """Test parsing widget with missing type raises error."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [{
                "id": "page1",
                "title_key": "title",
                "widgets": [{"id": "widget1"}]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with pytest.raises(ValueError, match="Widget 'type' must be a string"):
                factory.load_ui_config_pages()

    def test_parse_widget_with_properties(self) -> None:
        """Test parsing widget with properties."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [{
                "id": "page1",
                "title_key": "title",
                "widgets": [{
                    "id": "widget1",
                    "type": "custom",
                    "properties": {
                        "name": {"type": "text", "required": true},
                        "count": {"type": "number", "default": 10}
                    }
                }]
            }]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            pages = factory.load_ui_config_pages()
            widget = pages[0].widgets[0]
            assert "name" in widget.properties
            assert "count" in widget.properties
            assert widget.properties["name"].required is True
            assert widget.properties["count"].default == 10


class TestGetPageById:
    """Test getting pages by ID."""

    def test_get_page_by_id_success(self) -> None:
        """Test getting a page by ID."""
        factory = UIConfigFactory(config_path="config")
        pages = factory.load_ui_config_pages()

        if pages:
            page_id = pages[0].id
            result = factory.get_page_by_id(page_id)
            assert result is not None
            assert result.id == page_id

    def test_get_page_by_id_not_found(self) -> None:
        """Test getting page with nonexistent ID."""
        factory = UIConfigFactory(config_path="config")
        factory.load_ui_config_pages()

        result = factory.get_page_by_id("nonexistent_page")
        assert result is None

    def test_get_page_by_id_auto_loads(self) -> None:
        """Test that get_page_by_id auto-loads config if not cached."""
        factory = UIConfigFactory(config_path="config")
        # Don't call load_ui_config_pages()

        result = factory.get_page_by_id("menus_config")
        if result:
            assert result.id == "menus_config"
            assert factory._pages_cache is not None

    def test_get_page_by_id_handles_errors(self) -> None:
        """Test that get_page_by_id handles load errors gracefully."""
        factory = UIConfigFactory(config_path="nonexistent")

        result = factory.get_page_by_id("any_id")
        assert result is None


class TestGetPagesByCategory:
    """Test getting pages by category."""

    def test_get_pages_by_category_success(self) -> None:
        """Test getting pages by category."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [
                {"id": "page1", "title_key": "t1", "category": "menus", "order": 2},
                {"id": "page2", "title_key": "t2", "category": "lists", "order": 1},
                {"id": "page3", "title_key": "t3", "category": "menus", "order": 1}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            factory.load_ui_config_pages()

            menus = factory.get_pages_by_category("menus")
            assert len(menus) == 2
            # Should be sorted by order
            assert menus[0].id == "page3"  # order 1
            assert menus[1].id == "page1"  # order 2

    def test_get_pages_by_category_empty(self) -> None:
        """Test getting pages for category with no pages."""
        factory = UIConfigFactory(config_path="config")
        factory.load_ui_config_pages()

        result = factory.get_pages_by_category("nonexistent_category")
        assert result == []

    def test_get_pages_by_category_auto_loads(self) -> None:
        """Test that get_pages_by_category auto-loads config."""
        factory = UIConfigFactory(config_path="config")

        result = factory.get_pages_by_category("menus")
        assert isinstance(result, list)

    def test_get_pages_by_category_handles_errors(self) -> None:
        """Test that get_pages_by_category handles load errors."""
        factory = UIConfigFactory(config_path="nonexistent")

        result = factory.get_pages_by_category("menus")
        assert result == []


class TestGetAllCategories:
    """Test getting all categories."""

    def test_get_all_categories_success(self) -> None:
        """Test getting all unique categories."""
        factory = UIConfigFactory(config_path="config")

        json_data = """{
            "config_pages": [
                {"id": "page1", "title_key": "t1", "category": "menus"},
                {"id": "page2", "title_key": "t2", "category": "lists"},
                {"id": "page3", "title_key": "t3", "category": "menus"},
                {"id": "page4", "title_key": "t4", "category": "tabs"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            factory.load_ui_config_pages()

            categories = factory.get_all_categories()
            assert len(categories) == 3
            assert "menus" in categories
            assert "lists" in categories
            assert "tabs" in categories
            # Should be sorted
            assert categories == sorted(categories)

    def test_get_all_categories_auto_loads(self) -> None:
        """Test that get_all_categories auto-loads config."""
        factory = UIConfigFactory(config_path="config")

        categories = factory.get_all_categories()
        assert isinstance(categories, list)

    def test_get_all_categories_handles_errors(self) -> None:
        """Test that get_all_categories handles load errors."""
        factory = UIConfigFactory(config_path="nonexistent")

        result = factory.get_all_categories()
        assert result == []
