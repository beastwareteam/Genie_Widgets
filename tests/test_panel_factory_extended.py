"""Extended tests for PanelFactory - Coverage improvement tests."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from widgetsystem.factories.panel_factory import PanelConfig, PanelFactory


class TestPanelConfigDataclass:
    """Test PanelConfig dataclass."""

    def test_panel_config_initialization(self) -> None:
        """Test PanelConfig initialization with all fields."""
        panel = PanelConfig(
            id="test_panel",
            name_key="panel.test",
            area="left",
            closable=True,
            movable=True,
            floatable=False,
            delete_on_close=False,
            dnd_enabled=True,
            responsive_hidden_at=["mobile"],
        )
        assert panel.id == "test_panel"
        assert panel.name_key == "panel.test"
        assert panel.area == "left"
        assert panel.closable is True
        assert panel.movable is True
        assert panel.floatable is False
        assert panel.delete_on_close is False
        assert panel.dnd_enabled is True
        assert panel.responsive_hidden_at == ["mobile"]

    def test_panel_config_with_defaults(self) -> None:
        """Test PanelConfig with default values."""
        panel = PanelConfig(
            id="minimal",
            name_key="minimal.panel",
            area="center",
        )
        assert panel.id == "minimal"
        assert panel.closable is True
        assert panel.movable is True
        assert panel.floatable is False
        assert panel.delete_on_close is False
        assert panel.dnd_enabled is True
        assert panel.responsive_hidden_at == []

    def test_panel_config_invalid_area(self) -> None:
        """Test PanelConfig with invalid area raises error."""
        with pytest.raises(ValueError, match="Invalid area"):
            PanelConfig(
                id="test",
                name_key="test",
                area="invalid_area",
            )

    def test_panel_config_valid_areas(self) -> None:
        """Test all valid areas."""
        valid_areas = ["left", "right", "bottom", "center"]
        for area in valid_areas:
            panel = PanelConfig(
                id=f"test_{area}",
                name_key="test",
                area=area,
            )
            assert panel.area == area

    def test_panel_config_post_init_sets_empty_list(self) -> None:
        """Test that __post_init__ sets empty list when None."""
        panel = PanelConfig(
            id="test",
            name_key="test",
            area="center",
            responsive_hidden_at=None,
        )
        assert panel.responsive_hidden_at == []


class TestPanelFactoryBasics:
    """Test basic PanelFactory functionality."""

    def test_initialization(self) -> None:
        """Test PanelFactory initialization."""
        factory = PanelFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.panels_file == Path("config/panels.json")
        assert factory._panels_cache is None

    def test_initialization_with_path_object(self) -> None:
        """Test initialization with Path object."""
        factory = PanelFactory(config_path=Path("config"))
        assert factory.config_path == Path("config")


class TestLoadPanels:
    """Test panel loading functionality."""

    def test_load_panels_success(self) -> None:
        """Test successfully loading panels from config."""
        factory = PanelFactory(config_path="config")
        panels = factory.load_panels()
        assert isinstance(panels, list)
        assert len(panels) > 0
        assert all(isinstance(p, PanelConfig) for p in panels)

    def test_load_panels_caches_result(self) -> None:
        """Test that load_panels caches results."""
        factory = PanelFactory(config_path="config")
        panels = factory.load_panels()
        assert factory._panels_cache is not None
        assert len(factory._panels_cache) > 0

    def test_load_panels_missing_file(self) -> None:
        """Test loading when file doesn't exist."""
        factory = PanelFactory(config_path="nonexistent")
        with pytest.raises(FileNotFoundError):
            factory.load_panels()

    def test_load_panels_invalid_json_type(self) -> None:
        """Test loading with invalid JSON structure (array instead of object)."""
        factory = PanelFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            with pytest.raises(ValueError, match="Panels configuration must be a JSON object"):
                factory.load_panels()

    def test_load_panels_invalid_panels_key(self) -> None:
        """Test loading when 'panels' key is not an array."""
        factory = PanelFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data='{"panels": "not an array"}')):
            with pytest.raises(ValueError, match="'panels' must be an array"):
                factory.load_panels()


class TestParsePanel:
    """Test panel parsing."""

    def test_parse_valid_panel(self) -> None:
        """Test parsing a valid panel."""
        panel_dict = {
            "id": "test_panel",
            "name_key": "panel.test",
            "area": "left",
            "closable": True,
            "movable": True,
            "floatable": False,
            "delete_on_close": False,
            "dnd_enabled": True,
            "responsive_hidden_at": ["mobile", "tablet"],
        }
        panel = PanelFactory._parse_panel(panel_dict)
        assert panel.id == "test_panel"
        assert panel.name_key == "panel.test"
        assert panel.area == "left"
        assert panel.closable is True
        assert panel.movable is True
        assert panel.floatable is False
        assert panel.delete_on_close is False
        assert panel.dnd_enabled is True
        assert panel.responsive_hidden_at == ["mobile", "tablet"]

    def test_parse_panel_with_defaults(self) -> None:
        """Test parsing panel with default values."""
        panel_dict = {
            "id": "minimal_panel",
            "name_key": "minimal.panel",
        }
        panel = PanelFactory._parse_panel(panel_dict)
        assert panel.id == "minimal_panel"
        assert panel.area == "center"
        assert panel.closable is True
        assert panel.movable is True
        assert panel.floatable is False

    def test_parse_panel_missing_id(self) -> None:
        """Test parsing panel without ID raises error."""
        panel_dict = {"name_key": "test"}
        with pytest.raises(ValueError, match="Panel 'id' must be a non-empty string"):
            PanelFactory._parse_panel(panel_dict)

    def test_parse_panel_invalid_area_type(self) -> None:
        """Test parsing panel with invalid area type."""
        panel_dict = {
            "id": "test_panel",
            "area": 123,  # Not a string
        }
        with pytest.raises(ValueError, match="area must be a string"):
            PanelFactory._parse_panel(panel_dict)

    def test_parse_panel_invalid_responsive_hidden_at(self) -> None:
        """Test parsing panel with invalid responsive_hidden_at (not array)."""
        panel_dict = {
            "id": "test_panel",
            "name_key": "test",
            "responsive_hidden_at": "not-a-list",
        }
        panel = PanelFactory._parse_panel(panel_dict)
        # Should default to empty list
        assert panel.responsive_hidden_at == []

    def test_parse_panel_filters_non_string_responsive_values(self) -> None:
        """Test that non-string values in responsive_hidden_at are filtered."""
        panel_dict = {
            "id": "test_panel",
            "name_key": "test",
            "responsive_hidden_at": ["mobile", 123, "tablet", None],
        }
        panel = PanelFactory._parse_panel(panel_dict)
        # Only string values should be kept
        assert panel.responsive_hidden_at == ["mobile", "tablet"]

    def test_parse_panel_boolean_conversions(self) -> None:
        """Test that non-boolean flags are converted to boolean."""
        panel_dict = {
            "id": "test_panel",
            "name_key": "test",
            "closable": "true",  # String instead of bool
            "movable": 1,  # Int instead of bool
            "floatable": 0,  # Int (falsy) instead of bool
        }
        panel = PanelFactory._parse_panel(panel_dict)
        assert panel.closable is True  # "true" is truthy
        assert panel.movable is True  # 1 is truthy
        assert panel.floatable is False  # 0 is falsy


class TestPanelQueries:
    """Test panel query methods."""

    def test_get_panel(self) -> None:
        """Test getting a specific panel."""
        factory = PanelFactory(config_path="config")
        factory.load_panels()

        panel = factory.get_panel("left_panel")
        assert panel is not None
        assert panel.id == "left_panel"

    def test_get_panel_lazy_loads(self) -> None:
        """Test that get_panel loads panels if not cached."""
        factory = PanelFactory(config_path="config")
        assert factory._panels_cache is None

        panel = factory.get_panel("left_panel")
        assert factory._panels_cache is not None
        assert panel is not None

    def test_get_panel_nonexistent(self) -> None:
        """Test getting a nonexistent panel."""
        factory = PanelFactory(config_path="config")
        panel = factory.get_panel("nonexistent_panel_12345")
        assert panel is None

    def test_get_panels_by_area(self) -> None:
        """Test getting panels by area."""
        factory = PanelFactory(config_path="config")
        panels = factory.get_panels_by_area("left")
        assert isinstance(panels, list)
        assert all(p.area == "left" for p in panels)

    def test_get_panels_by_area_empty(self) -> None:
        """Test getting panels for area with no panels."""
        factory = PanelFactory(config_path="config")
        panels = factory.get_panels_by_area("nonexistent_area")
        assert panels == []

    def test_get_panels_by_area_multiple_areas(self) -> None:
        """Test getting panels from different areas."""
        factory = PanelFactory(config_path="config")
        areas = ["left", "right", "bottom", "center"]

        for area in areas:
            panels = factory.get_panels_by_area(area)
            assert isinstance(panels, list)
            # Verify all panels in result are from the correct area
            assert all(p.area == area for p in panels)

    def test_list_panel_ids(self) -> None:
        """Test listing all panel IDs."""
        factory = PanelFactory(config_path="config")
        ids = factory.list_panel_ids()
        assert isinstance(ids, list)
        assert len(ids) > 0
        assert "left_panel" in ids

    def test_list_panel_ids_empty_cache(self) -> None:
        """Test listing panel IDs with empty cache loads data."""
        factory = PanelFactory(config_path="config")
        assert factory._panels_cache is None

        ids = factory.list_panel_ids()
        assert factory._panels_cache is not None
        assert isinstance(ids, list)

    def test_get_dnd_enabled_panels(self) -> None:
        """Test getting panels with DnD enabled."""
        factory = PanelFactory(config_path="config")
        dnd_panels = factory.get_dnd_enabled_panels()
        assert isinstance(dnd_panels, list)
        assert all(p.dnd_enabled for p in dnd_panels)

    def test_get_dnd_enabled_panels_empty_cache(self) -> None:
        """Test getting DnD panels with empty cache."""
        factory = PanelFactory(config_path="config")
        factory._panels_cache = {}

        dnd_panels = factory.get_dnd_enabled_panels()
        assert dnd_panels == []


class TestPanelProperties:
    """Test panel property access and validation."""

    def test_panel_closable_property(self) -> None:
        """Test accessing closable property."""
        factory = PanelFactory(config_path="config")
        panels = factory.load_panels()

        # Check that we can access closable property
        for panel in panels:
            assert isinstance(panel.closable, bool)

    def test_panel_movable_property(self) -> None:
        """Test accessing movable property."""
        factory = PanelFactory(config_path="config")
        panels = factory.load_panels()

        for panel in panels:
            assert isinstance(panel.movable, bool)

    def test_panel_floatable_property(self) -> None:
        """Test accessing floatable property."""
        factory = PanelFactory(config_path="config")
        panels = factory.load_panels()

        for panel in panels:
            assert isinstance(panel.floatable, bool)

    def test_panel_responsive_hidden_at_property(self) -> None:
        """Test accessing responsive_hidden_at property."""
        factory = PanelFactory(config_path="config")
        panels = factory.load_panels()

        for panel in panels:
            assert isinstance(panel.responsive_hidden_at, list)


class TestPanelResponsiveAndPersistence:
    """Test responsive rule access and persistence helpers."""

    def test_get_responsive_rules_existing(self) -> None:
        """Responsive rules are returned for existing panel."""
        factory = PanelFactory(config_path="config")
        rules = factory.get_responsive_rules("left_panel")
        assert isinstance(rules, list)

    def test_get_responsive_rules_missing_panel(self) -> None:
        """Missing panel returns empty responsive rule list."""
        factory = PanelFactory(config_path="config")
        assert factory.get_responsive_rules("unknown_panel") == []

    def test_get_responsive_rules_none_hidden_at(self) -> None:
        """None responsive_hidden_at returns empty list."""
        factory = PanelFactory(config_path="config")
        panel = PanelConfig(id="x", name_key="x", area="left", responsive_hidden_at=None)
        with patch.object(factory, "get_panel", return_value=panel):
            assert factory.get_responsive_rules("x") == []

    def test_add_panel_success(self) -> None:
        """Adding a valid panel stores it and persists."""
        factory = PanelFactory(config_path="config")
        factory.load_panels()
        with patch.object(factory, "save_to_file", return_value=True):
            result = factory.add_panel("dynamic_panel", "panel.dynamic", area="center")
            assert result is True
            assert factory._panels_cache is not None
            assert "dynamic_panel" in factory._panels_cache

    def test_add_panel_load_failure_returns_false(self) -> None:
        """Add panel returns False if loading cache fails."""
        factory = PanelFactory(config_path="config")
        with patch.object(factory, "load_panels", side_effect=RuntimeError("load error")):
            assert factory.add_panel("x", "x") is False

    def test_add_panel_invalid_area_returns_false(self) -> None:
        """Add panel catches PanelConfig validation errors."""
        factory = PanelFactory(config_path="config")
        assert factory.add_panel("x", "x", area="invalid") is False

    def test_save_to_file_with_none_cache(self) -> None:
        """save_to_file returns False when no cache is available."""
        factory = PanelFactory(config_path="config")
        assert factory.save_to_file() is False

    def test_save_to_file_success(self) -> None:
        """save_to_file writes serialized panel json successfully."""
        factory = PanelFactory(config_path="config")
        factory.load_panels()
        assert factory.save_to_file() is True

    def test_save_to_file_exception_returns_false(self) -> None:
        """save_to_file returns False if writing fails."""
        factory = PanelFactory(config_path="config")
        factory.load_panels()
        with patch("builtins.open", side_effect=OSError("write error")):
            assert factory.save_to_file() is False

    def test_panel_to_dict_serialization(self) -> None:
        """_panel_to_dict includes all expected fields."""
        panel = PanelConfig(
            id="p1",
            name_key="panel.p1",
            area="right",
            closable=False,
            movable=False,
            floatable=True,
            delete_on_close=True,
            dnd_enabled=False,
            responsive_hidden_at=["mobile"],
        )
        serialized = PanelFactory._panel_to_dict(panel)
        assert serialized["id"] == "p1"
        assert serialized["name_key"] == "panel.p1"
        assert serialized["area"] == "right"
        assert serialized["closable"] is False
        assert serialized["movable"] is False
        assert serialized["floatable"] is True
        assert serialized["delete_on_close"] is True
        assert serialized["dnd_enabled"] is False
        assert serialized["responsive_hidden_at"] == ["mobile"]
