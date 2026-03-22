"""Extended tests for ResponsiveFactory coverage improvement."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from widgetsystem.factories.responsive_factory import (
    Breakpoint,
    BreakpointType,
    ResponsiveFactory,
    ResponsiveRule,
)


class TestBreakpointTypeEnum:
    """Test BreakpointType enum values."""

    def test_breakpoint_type_values(self) -> None:
        """Enum contains expected responsive breakpoint values."""
        assert BreakpointType.DESKTOP.value == "desktop"
        assert BreakpointType.TABLET.value == "tablet"
        assert BreakpointType.MOBILE.value == "mobile"


class TestBreakpointDataclass:
    """Test Breakpoint dataclass behavior."""

    def test_breakpoint_valid_initialization(self) -> None:
        """Create valid breakpoint with all fields."""
        bp = Breakpoint(id="tablet", min_width=768, max_width=1199, name="Tablet")
        assert bp.id == "tablet"
        assert bp.min_width == 768
        assert bp.max_width == 1199
        assert bp.name == "Tablet"

    def test_breakpoint_defaults(self) -> None:
        """Default values are applied when omitted."""
        bp = Breakpoint(id="desktop")
        assert bp.min_width == 0
        assert bp.max_width == 99999
        assert bp.name == ""

    def test_breakpoint_negative_min_raises(self) -> None:
        """Negative min width is invalid."""
        with pytest.raises(ValueError, match="min_width must be non-negative"):
            Breakpoint(id="x", min_width=-1)

    def test_breakpoint_negative_max_raises(self) -> None:
        """Negative max width is invalid."""
        with pytest.raises(ValueError, match="max_width must be non-negative"):
            Breakpoint(id="x", max_width=-1)

    def test_breakpoint_min_greater_than_max_raises(self) -> None:
        """min_width cannot exceed max_width."""
        with pytest.raises(ValueError, match="min_width cannot exceed max_width"):
            Breakpoint(id="x", min_width=100, max_width=50)

    def test_breakpoint_matches_boundaries(self) -> None:
        """Width matching includes boundaries."""
        bp = Breakpoint(id="tablet", min_width=768, max_width=1199)
        assert bp.matches(768) is True
        assert bp.matches(1199) is True

    def test_breakpoint_matches_outside(self) -> None:
        """Width outside breakpoint returns False."""
        bp = Breakpoint(id="tablet", min_width=768, max_width=1199)
        assert bp.matches(767) is False
        assert bp.matches(1200) is False


class TestResponsiveRuleDataclass:
    """Test ResponsiveRule dataclass behavior."""

    def test_responsive_rule_valid(self) -> None:
        """Valid responsive rule initializes correctly."""
        rule = ResponsiveRule(id="r1", panel_id="left", breakpoint="mobile", action="hide")
        assert rule.id == "r1"
        assert rule.panel_id == "left"
        assert rule.breakpoint == "mobile"
        assert rule.action == "hide"

    def test_responsive_rule_invalid_action_raises(self) -> None:
        """Invalid action should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid action"):
            ResponsiveRule(id="r1", panel_id="left", breakpoint="mobile", action="invalid")


class TestResponsiveFactoryBasics:
    """Test initialization and basic members."""

    def test_factory_initialization(self) -> None:
        """Factory initializes internal paths and caches."""
        factory = ResponsiveFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.responsive_file == Path("config/responsive.json")
        assert factory._breakpoints_cache is None
        assert factory._rules_cache is None
        assert factory._current_breakpoint is None


class TestLoadBreakpoints:
    """Test loading breakpoint configuration."""

    def test_load_breakpoints_success(self) -> None:
        """Load breakpoints from project config."""
        factory = ResponsiveFactory(config_path="config")
        breakpoints = factory.load_breakpoints()
        assert len(breakpoints) >= 1
        assert all(isinstance(bp, Breakpoint) for bp in breakpoints)
        assert factory._breakpoints_cache is not None
        assert len(factory._breakpoints_cache) == len(breakpoints)

    def test_load_breakpoints_missing_file_raises(self) -> None:
        """Missing responsive config should raise FileNotFoundError."""
        factory = ResponsiveFactory(config_path="does_not_exist")
        with pytest.raises(FileNotFoundError, match="Responsive configuration file not found"):
            factory.load_breakpoints()

    def test_load_breakpoints_json_not_object_raises(self) -> None:
        """JSON root must be an object."""
        factory = ResponsiveFactory(config_path="config")
        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(
                    ValueError,
                    match="Responsive configuration must be a JSON object",
                ):
                    factory.load_breakpoints()

    def test_load_breakpoints_breakpoints_not_array_raises(self) -> None:
        """Breakpoints key must be an array."""
        factory = ResponsiveFactory(config_path="config")
        with patch("builtins.open", mock_open(read_data='{"breakpoints": "bad"}')):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ValueError, match="'breakpoints' must be an array"):
                    factory.load_breakpoints()

    def test_load_breakpoints_skips_non_dict_entries(self) -> None:
        """Non-dict entries are ignored."""
        factory = ResponsiveFactory(config_path="config")
        data = (
            '{"breakpoints": ['
            '{"id": "desktop", "min_width": 1200, "name": "Desktop"},'
            '"invalid",'
            '{"id": "mobile", "max_width": 767, "name": "Mobile"}'
            "]}"
        )
        with patch("builtins.open", mock_open(read_data=data)):
            with patch("pathlib.Path.exists", return_value=True):
                breakpoints = factory.load_breakpoints()
                assert len(breakpoints) == 2
                assert {bp.id for bp in breakpoints} == {"desktop", "mobile"}

    def test_load_breakpoints_invalid_entry_raises(self) -> None:
        """Invalid dict entry should bubble ValueError from parser."""
        factory = ResponsiveFactory(config_path="config")
        data = '{"breakpoints": [{"min_width": 0, "max_width": 100}]}'
        with patch("builtins.open", mock_open(read_data=data)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ValueError, match="Breakpoint 'id' must be a non-empty string"):
                    factory.load_breakpoints()


class TestLoadResponsiveRules:
    """Test loading responsive rules configuration."""

    def test_load_rules_success(self) -> None:
        """Load rules from project config."""
        factory = ResponsiveFactory(config_path="config")
        rules = factory.load_responsive_rules()
        assert len(rules) >= 1
        assert all(isinstance(rule, ResponsiveRule) for rule in rules)
        assert factory._rules_cache is not None
        assert len(factory._rules_cache) == len(rules)

    def test_load_rules_missing_file_raises(self) -> None:
        """Missing responsive config should raise FileNotFoundError."""
        factory = ResponsiveFactory(config_path="does_not_exist")
        with pytest.raises(FileNotFoundError, match="Responsive configuration file not found"):
            factory.load_responsive_rules()

    def test_load_rules_json_not_object_raises(self) -> None:
        """JSON root must be object for rules loading."""
        factory = ResponsiveFactory(config_path="config")
        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(
                    ValueError,
                    match="Responsive configuration must be a JSON object",
                ):
                    factory.load_responsive_rules()

    def test_load_rules_rules_not_array_raises(self) -> None:
        """Rules key must be an array."""
        factory = ResponsiveFactory(config_path="config")
        with patch("builtins.open", mock_open(read_data='{"rules": "bad"}')):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ValueError, match="'rules' must be an array"):
                    factory.load_responsive_rules()

    def test_load_rules_skips_non_dict_entries(self) -> None:
        """Non-dict rule entries are ignored."""
        factory = ResponsiveFactory(config_path="config")
        data = (
            '{"rules": ['
            '{"id": "r1", "panel_id": "left", "breakpoint": "mobile", "action": "hide"},'
            "42,"
            '{"id": "r2", "panel_id": "bottom", "breakpoint": "tablet", "action": "show"}'
            "]}"
        )
        with patch("builtins.open", mock_open(read_data=data)):
            with patch("pathlib.Path.exists", return_value=True):
                rules = factory.load_responsive_rules()
                assert len(rules) == 2
                assert {r.id for r in rules} == {"r1", "r2"}

    def test_load_rules_invalid_rule_raises(self) -> None:
        """Invalid rule dict should bubble ValueError from parser."""
        factory = ResponsiveFactory(config_path="config")
        data = '{"rules": [{"panel_id": "left", "action": "hide"}]}'
        with patch("builtins.open", mock_open(read_data=data)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(
                    ValueError,
                    match="Responsive rule 'id' must be a non-empty string",
                ):
                    factory.load_responsive_rules()


class TestParserHelpers:
    """Test static parser helpers."""

    def test_parse_breakpoint_non_numeric_width_defaults(self) -> None:
        """Non-numeric widths fallback to defaults."""
        bp = ResponsiveFactory._parse_breakpoint(
            {"id": "x", "min_width": "bad", "max_width": "bad", "name": 1},
        )
        assert bp.min_width == 0
        assert bp.max_width == 99999
        assert bp.name == ""

    def test_parse_rule_non_string_fields_default(self) -> None:
        """Non-string breakpoint/action fallback to defaults."""
        rule = ResponsiveFactory._parse_responsive_rule(
            {"id": "r1", "panel_id": "left", "breakpoint": 1, "action": 2},
        )
        assert rule.breakpoint == "desktop"
        assert rule.action == "hide"

    def test_parse_rule_missing_panel_id_raises(self) -> None:
        """Rule parser requires string panel_id."""
        with pytest.raises(ValueError, match="panel_id must be a string"):
            ResponsiveFactory._parse_responsive_rule({"id": "r1"})


class TestQueryMethods:
    """Test factory query methods and lazy-loading behavior."""

    def test_get_breakpoint_existing(self) -> None:
        """Fetch existing breakpoint by ID."""
        factory = ResponsiveFactory(config_path="config")
        bp = factory.get_breakpoint("desktop")
        assert bp is not None
        assert bp.id == "desktop"

    def test_get_breakpoint_missing(self) -> None:
        """Unknown breakpoint ID returns None."""
        factory = ResponsiveFactory(config_path="config")
        assert factory.get_breakpoint("unknown") is None

    def test_list_breakpoint_ids(self) -> None:
        """List breakpoint IDs from cache/load."""
        factory = ResponsiveFactory(config_path="config")
        ids = factory.list_breakpoint_ids()
        assert isinstance(ids, list)
        assert "desktop" in ids

    def test_get_responsive_rule_existing(self) -> None:
        """Fetch existing rule by ID."""
        factory = ResponsiveFactory(config_path="config")
        rule = factory.get_responsive_rule("rule_hide_left_mobile")
        assert rule is not None
        assert rule.id == "rule_hide_left_mobile"

    def test_get_responsive_rule_missing(self) -> None:
        """Unknown rule ID returns None."""
        factory = ResponsiveFactory(config_path="config")
        assert factory.get_responsive_rule("unknown") is None

    def test_get_panel_rules_existing(self) -> None:
        """Get all rules for an existing panel."""
        factory = ResponsiveFactory(config_path="config")
        rules = factory.get_panel_rules("left_panel")
        assert isinstance(rules, list)
        assert len(rules) >= 1
        assert all(rule.panel_id == "left_panel" for rule in rules)

    def test_get_panel_rules_empty(self) -> None:
        """No rules for unknown panel returns empty list."""
        factory = ResponsiveFactory(config_path="config")
        assert factory.get_panel_rules("not_existing_panel") == []

    def test_get_panel_rules_with_empty_cache_returns_empty(self) -> None:
        """When rules cache exists but empty, returns empty list."""
        factory = ResponsiveFactory(config_path="config")
        factory._rules_cache = {}
        assert factory.get_panel_rules("left_panel") == []


class TestJsonDecodeErrors:
    """Test JSON decode behavior from loaders."""

    def test_load_breakpoints_json_decode_error(self) -> None:
        """Invalid JSON should raise decode error."""
        factory = ResponsiveFactory(config_path="config")
        with patch("builtins.open", side_effect=json.JSONDecodeError("msg", "doc", 0)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(json.JSONDecodeError):
                    factory.load_breakpoints()

    def test_load_rules_json_decode_error(self) -> None:
        """Invalid JSON should raise decode error for rules."""
        factory = ResponsiveFactory(config_path="config")
        with patch("builtins.open", side_effect=json.JSONDecodeError("msg", "doc", 0)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(json.JSONDecodeError):
                    factory.load_responsive_rules()
