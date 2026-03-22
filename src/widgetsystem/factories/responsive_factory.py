"""Responsive Factory - reads config/responsive.json and manages breakpoints/rules."""

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, TypedDict, cast


class BreakpointType(str, Enum):
    """Responsive design breakpoint types."""

    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class BreakpointDefinition(TypedDict, total=False):
    """Type-safe breakpoint configuration."""

    id: str
    min_width: int
    max_width: int
    name: str


class ResponsiveRuleDefinition(TypedDict, total=False):
    """Type-safe responsive rule configuration."""

    id: str
    panel_id: str
    breakpoint: str
    action: str


@dataclass
class Breakpoint:
    """Represents a responsive design breakpoint."""

    id: str
    min_width: int = 0
    max_width: int = 99999
    name: str = ""

    def __post_init__(self) -> None:
        """Validate breakpoint configuration."""
        if self.min_width < 0:
            raise ValueError("min_width must be non-negative")
        if self.max_width < 0:
            raise ValueError("max_width must be non-negative")
        if self.min_width > self.max_width:
            raise ValueError("min_width cannot exceed max_width")

    def matches(self, width: int) -> bool:
        """Check if a width matches this breakpoint."""
        return self.min_width <= width <= self.max_width


@dataclass
class ResponsiveRule:
    """Represents a responsive design rule for a panel."""

    id: str
    panel_id: str
    breakpoint: str
    action: str

    def __post_init__(self) -> None:
        """Validate responsive rule configuration."""
        valid_actions = {"hide", "show", "collapse"}
        if self.action not in valid_actions:
            raise ValueError(f"Invalid action '{self.action}'. Must be one of {valid_actions}")


class ResponsiveFactory:
    """Factory for loading and managing responsive design configurations."""

    def __init__(self, config_path: str | Path = "config") -> None:
        """Initialize ResponsiveFactory."""
        self.config_path = Path(config_path)
        self.responsive_file = self.config_path / "responsive.json"
        self._breakpoints_cache: dict[str, Breakpoint] | None = None
        self._rules_cache: dict[str, ResponsiveRule] | None = None
        self._current_breakpoint: Breakpoint | None = None

    def load_breakpoints(self) -> list[Breakpoint]:
        """Load and parse all breakpoints from config."""
        if not self.responsive_file.exists():
            raise FileNotFoundError(
                f"Responsive configuration file not found: {self.responsive_file}",
            )

        with open(self.responsive_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Responsive configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        breakpoints_list_raw: Any = raw_data.get("breakpoints", [])
        if not isinstance(breakpoints_list_raw, list):
            raise ValueError("'breakpoints' must be an array")
        breakpoints_list: list[Any] = breakpoints_list_raw

        breakpoints: list[Breakpoint] = []
        self._breakpoints_cache = {}

        for item in breakpoints_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            breakpoint = self._parse_breakpoint(item_dict)
            breakpoints.append(breakpoint)
            self._breakpoints_cache[breakpoint.id] = breakpoint

        return breakpoints

    def load_responsive_rules(self) -> list[ResponsiveRule]:
        """Load and parse all responsive rules from config."""
        if not self.responsive_file.exists():
            raise FileNotFoundError(
                f"Responsive configuration file not found: {self.responsive_file}",
            )

        with open(self.responsive_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Responsive configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        rules_list_raw: Any = raw_data.get("rules", [])
        if not isinstance(rules_list_raw, list):
            raise ValueError("'rules' must be an array")
        rules_list: list[Any] = rules_list_raw

        rules: list[ResponsiveRule] = []
        self._rules_cache = {}

        for item in rules_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            rule = self._parse_responsive_rule(item_dict)
            rules.append(rule)
            self._rules_cache[rule.id] = rule

        return rules

    @staticmethod
    def _parse_breakpoint(bp_dict: dict[str, Any]) -> Breakpoint:
        """Parse and validate a single breakpoint definition."""
        bp_id: Any = bp_dict.get("id")
        if not isinstance(bp_id, str):
            raise ValueError("Breakpoint 'id' must be a non-empty string")

        min_width: Any = bp_dict.get("min_width", 0)
        max_width: Any = bp_dict.get("max_width", 99999)
        name: Any = bp_dict.get("name", "")

        return Breakpoint(
            id=bp_id,
            min_width=int(min_width) if isinstance(min_width, (int, float)) else 0,
            max_width=int(max_width) if isinstance(max_width, (int, float)) else 99999,
            name=str(name) if isinstance(name, str) else "",
        )

    @staticmethod
    def _parse_responsive_rule(rule_dict: dict[str, Any]) -> ResponsiveRule:
        """Parse and validate a single responsive rule definition."""
        rule_id: Any = rule_dict.get("id")
        if not isinstance(rule_id, str):
            raise ValueError("Responsive rule 'id' must be a non-empty string")

        panel_id: Any = rule_dict.get("panel_id")
        if not isinstance(panel_id, str):
            raise ValueError(f"Responsive rule '{rule_id}' panel_id must be a string")

        breakpoint: Any = rule_dict.get("breakpoint", "desktop")
        action: Any = rule_dict.get("action", "hide")

        return ResponsiveRule(
            id=rule_id,
            panel_id=panel_id,
            breakpoint=str(breakpoint) if isinstance(breakpoint, str) else "desktop",
            action=str(action) if isinstance(action, str) else "hide",
        )

    def get_breakpoint(self, bp_id: str) -> Breakpoint | None:
        """Get a specific breakpoint by ID."""
        if self._breakpoints_cache is None:
            self.load_breakpoints()

        return self._breakpoints_cache.get(bp_id) if self._breakpoints_cache else None

    def list_breakpoint_ids(self) -> list[str]:
        """List all breakpoint IDs."""
        if self._breakpoints_cache is None:
            self.load_breakpoints()

        return list(self._breakpoints_cache.keys()) if self._breakpoints_cache else []

    def get_responsive_rule(self, rule_id: str) -> ResponsiveRule | None:
        """Get a specific responsive rule by ID."""
        if self._rules_cache is None:
            self.load_responsive_rules()

        return self._rules_cache.get(rule_id) if self._rules_cache else None

    def get_panel_rules(self, panel_id: str) -> list[ResponsiveRule]:
        """Get all responsive rules for a specific panel."""
        if self._rules_cache is None:
            self.load_responsive_rules()

        if not self._rules_cache:
            return []

        return [r for r in self._rules_cache.values() if r.panel_id == panel_id]
