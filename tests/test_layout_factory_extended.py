"""Extended tests for LayoutFactory - Coverage improvement tests."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from widgetsystem.factories.layout_factory import LayoutDefinition, LayoutFactory


class TestLayoutDefinitionDataclass:
    """Test LayoutDefinition dataclass."""

    def test_initialization(self) -> None:
        """Test LayoutDefinition initialization."""
        layout = LayoutDefinition(
            layout_id="test_layout",
            name="Test Layout",
            file_path=Path("data/layout.xml"),
        )
        assert layout.layout_id == "test_layout"
        assert layout.name == "Test Layout"
        assert layout.file_path == Path("data/layout.xml")

    def test_frozen_dataclass(self) -> None:
        """Test that LayoutDefinition is frozen (immutable)."""
        layout = LayoutDefinition(
            layout_id="test",
            name="Test",
            file_path=Path("test.xml"),
        )

        with pytest.raises(Exception):  # FrozenInstanceError in Python 3.10+
            layout.layout_id = "modified"  # type: ignore[misc]


class TestLayoutFactoryBasics:
    """Test basic LayoutFactory functionality."""

    def test_initialization(self) -> None:
        """Test LayoutFactory initialization."""
        factory = LayoutFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.layouts_file == Path("config/layouts.json")

    def test_initialization_with_path_object(self) -> None:
        """Test initialization with Path object."""
        factory = LayoutFactory(config_path=Path("config"))
        assert factory.config_path == Path("config")


class TestListLayouts:
    """Test layout listing functionality."""

    def test_list_layouts_success(self) -> None:
        """Test successfully listing layouts from config."""
        factory = LayoutFactory(config_path="config")
        layouts = factory.list_layouts()

        assert isinstance(layouts, list)
        assert len(layouts) > 0
        assert all(isinstance(layout, LayoutDefinition) for layout in layouts)

        # Check that file paths are resolved
        for layout in layouts:
            assert layout.file_path.is_absolute()

    def test_list_layouts_missing_file(self) -> None:
        """Test listing layouts when file doesn't exist."""
        factory = LayoutFactory(config_path="nonexistent")

        with pytest.raises(FileNotFoundError, match="Layout configuration file not found"):
            factory.list_layouts()

    def test_list_layouts_invalid_json(self) -> None:
        """Test listing layouts with invalid JSON returns empty list."""
        factory = LayoutFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                assert layouts == []

    def test_list_layouts_not_a_dict(self) -> None:
        """Test listing layouts when JSON is not a dict returns empty list."""
        factory = LayoutFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                assert layouts == []

    def test_list_layouts_layouts_not_array(self) -> None:
        """Test listing layouts when 'layouts' key is not an array."""
        factory = LayoutFactory(config_path="config")

        json_data = '{"layouts": "not an array"}'
        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                assert layouts == []

    def test_list_layouts_skips_invalid_entries(self) -> None:
        """Test that invalid layout entries are skipped."""
        factory = LayoutFactory(config_path="config")

        json_data = """{
            "layouts": [
                {"id": "layout1", "name": "Layout 1", "file": "layout1.xml"},
                "invalid_entry",
                {"id": "layout2", "name": "Layout 2", "file": "layout2.xml"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                assert len(layouts) == 2
                assert layouts[0].layout_id == "layout1"
                assert layouts[1].layout_id == "layout2"

    def test_list_layouts_skips_missing_required_fields(self) -> None:
        """Test that layouts with missing required fields are skipped."""
        factory = LayoutFactory(config_path="config")

        json_data = """{
            "layouts": [
                {"id": "layout1", "name": "Layout 1"},
                {"id": "layout2", "file": "layout2.xml"},
                {"name": "Layout 3", "file": "layout3.xml"},
                {"id": "layout4", "name": "Layout 4", "file": "layout4.xml"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                # Only layout4 has all required fields
                assert len(layouts) == 1
                assert layouts[0].layout_id == "layout4"

    def test_list_layouts_resolves_relative_paths(self) -> None:
        """Test that relative layout file paths are resolved to absolute."""
        factory = LayoutFactory(config_path="config")

        json_data = """{
            "layouts": [
                {"id": "layout1", "name": "Layout 1", "file": "data/layout.xml"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                assert len(layouts) == 1
                # Path should be resolved and absolute
                assert layouts[0].file_path.is_absolute()

    def test_list_layouts_handles_absolute_paths(self) -> None:
        """Test that absolute file paths are preserved."""
        factory = LayoutFactory(config_path="config")

        abs_path = "C:/absolute/path/layout.xml"
        json_data = f"""{{
            "layouts": [
                {{"id": "layout1", "name": "Layout 1", "file": "{abs_path}"}}
            ]
        }}"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                assert len(layouts) == 1
                assert layouts[0].file_path.is_absolute()

    def test_list_layouts_handles_os_error(self) -> None:
        """Test that OSError during file reading is handled."""
        factory = LayoutFactory(config_path="config")

        with patch("builtins.open", side_effect=OSError("File read error")):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                assert layouts == []

    def test_list_layouts_skips_non_string_fields(self) -> None:
        """Test that layouts with non-string fields are skipped."""
        factory = LayoutFactory(config_path="config")

        json_data = """{
            "layouts": [
                {"id": 123, "name": "Layout 1", "file": "layout1.xml"},
                {"id": "layout2", "name": 456, "file": "layout2.xml"},
                {"id": "layout3", "name": "Layout 3", "file": 789},
                {"id": "layout4", "name": "Layout 4", "file": "layout4.xml"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                layouts = factory.list_layouts()
                # Only layout4 should be valid
                assert len(layouts) == 1
                assert layouts[0].layout_id == "layout4"


class TestGetDefaultLayoutId:
    """Test default layout ID functionality."""

    def test_get_default_layout_id_success(self) -> None:
        """Test getting default layout ID from config."""
        factory = LayoutFactory(config_path="config")
        default_id = factory.get_default_layout_id()

        assert isinstance(default_id, str)
        assert len(default_id) > 0

    def test_get_default_layout_id_missing_file(self) -> None:
        """Test getting default layout ID when file doesn't exist."""
        factory = LayoutFactory(config_path="config")

        with patch("builtins.open", side_effect=OSError("File not found")):
            default_id = factory.get_default_layout_id()
            assert default_id is None

    def test_get_default_layout_id_invalid_json(self) -> None:
        """Test getting default layout ID with invalid JSON."""
        factory = LayoutFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="invalid json")):
            default_id = factory.get_default_layout_id()
            assert default_id is None

    def test_get_default_layout_id_not_a_dict(self) -> None:
        """Test getting default layout ID when JSON is not a dict."""
        factory = LayoutFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            default_id = factory.get_default_layout_id()
            assert default_id is None

    def test_get_default_layout_id_missing_key(self) -> None:
        """Test getting default layout ID when key is missing."""
        factory = LayoutFactory(config_path="config")

        json_data = '{"other_key": "value"}'
        with patch("builtins.open", mock_open(read_data=json_data)):
            default_id = factory.get_default_layout_id()
            assert default_id is None

    def test_get_default_layout_id_non_string_value(self) -> None:
        """Test getting default layout ID when value is not a string."""
        factory = LayoutFactory(config_path="config")

        json_data = '{"default_layout_id": 123}'
        with patch("builtins.open", mock_open(read_data=json_data)):
            default_id = factory.get_default_layout_id()
            assert default_id is None

    def test_get_default_layout_id_handles_json_decode_error(self) -> None:
        """Test that JSONDecodeError is handled gracefully."""
        factory = LayoutFactory(config_path="config")

        with patch("builtins.open", side_effect=json.JSONDecodeError("", "", 0)):
            default_id = factory.get_default_layout_id()
            assert default_id is None
