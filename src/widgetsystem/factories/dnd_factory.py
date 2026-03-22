"""DnD Factory - reads config/dnd.json and provides drop zone definitions with rules."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, TypedDict, cast


class DropZoneDefinition(TypedDict, total=False):
    """Type-safe drop zone configuration."""

    id: str
    area: str
    orientation: str
    allowed_panels: list[str]
    nav_zone_width: int
    snap_enabled: bool


class DnDRuleDefinition(TypedDict, total=False):
    """Type-safe DnD rule configuration."""

    id: str
    panel_id: str
    source_area: str
    allowed_target_areas: list[str]


@dataclass
class DropZone:
    """Represents a drop zone for drag-and-drop operations."""

    id: str
    area: str
    orientation: str = "horizontal"
    allowed_panels: list[str] = field(default_factory=list)
    nav_zone_width: int = 20
    snap_enabled: bool = True

    def __post_init__(self) -> None:
        """Validate drop zone configuration."""
        valid_areas = {"left", "right", "bottom", "center"}
        if self.area not in valid_areas:
            raise ValueError(f"Invalid area '{self.area}'. Must be one of {valid_areas}")

        valid_orientations = {"horizontal", "vertical"}
        if self.orientation not in valid_orientations:
            raise ValueError(
                f"Invalid orientation '{self.orientation}'. Must be one of {valid_orientations}",
            )

        if self.nav_zone_width < 0:
            raise ValueError("nav_zone_width must be non-negative")


@dataclass
class DnDRule:
    """Represents a drag-and-drop restriction rule."""

    id: str
    panel_id: str
    source_area: str
    allowed_target_areas: list[str] = field(default_factory=list)

    def allows_move(self, target_area: str) -> bool:
        """Check if this rule allows moving to a target area."""
        if not self.allowed_target_areas:
            return False

        return target_area in self.allowed_target_areas


class DnDFactory:
    """Factory for loading and managing drag-and-drop configurations."""

    def __init__(self, config_path: str | Path = "config") -> None:
        """Initialize DnDFactory."""
        self.config_path = Path(config_path)
        self.dnd_file = self.config_path / "dnd.json"
        self._drop_zones_cache: dict[str, DropZone] | None = None
        self._rules_cache: dict[str, DnDRule] | None = None

    def load_drop_zones(self) -> list[DropZone]:
        """Load and parse all drop zones from config."""
        if not self.dnd_file.exists():
            raise FileNotFoundError(f"DnD configuration file not found: {self.dnd_file}")

        with open(self.dnd_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("DnD configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        drop_zones_list_raw: Any = raw_data.get("drop_zones", [])
        if not isinstance(drop_zones_list_raw, list):
            raise ValueError("'drop_zones' must be an array")
        drop_zones_list: list[Any] = drop_zones_list_raw

        drop_zones: list[DropZone] = []
        self._drop_zones_cache = {}

        for item in drop_zones_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            drop_zone = self._parse_drop_zone(item_dict)
            drop_zones.append(drop_zone)
            self._drop_zones_cache[drop_zone.id] = drop_zone

        return drop_zones

    def load_dnd_rules(self) -> list[DnDRule]:
        """Load and parse all DnD rules from config."""
        if not self.dnd_file.exists():
            raise FileNotFoundError(f"DnD configuration file not found: {self.dnd_file}")

        with open(self.dnd_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("DnD configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        # Support both "rules" and "dnd_rules" keys for backwards compatibility
        rules_list_raw: Any = raw_data.get("rules") or raw_data.get("dnd_rules", [])
        if not isinstance(rules_list_raw, list):
            raise ValueError("'dnd_rules' must be an array")
        rules_list: list[Any] = rules_list_raw

        rules: list[DnDRule] = []
        self._rules_cache = {}

        for item in rules_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            rule = self._parse_dnd_rule(item_dict)
            rules.append(rule)
            self._rules_cache[rule.id] = rule

        return rules

    @staticmethod
    def _parse_drop_zone(zone_dict: dict[str, Any]) -> DropZone:
        """Parse and validate a single drop zone definition."""
        zone_id: Any = zone_dict.get("id")
        if not isinstance(zone_id, str):
            raise ValueError("DropZone 'id' must be a non-empty string")

        area: Any = zone_dict.get("area", "center")
        if not isinstance(area, str):
            raise ValueError(f"DropZone '{zone_id}' area must be a string")

        orientation: Any = zone_dict.get("orientation", "horizontal")
        allowed_panels_raw: Any = zone_dict.get("allowed_panels", [])
        if not isinstance(allowed_panels_raw, list):
            allowed_panels_raw = []
        allowed_panels_list: list[Any] = allowed_panels_raw

        nav_zone_width: Any = zone_dict.get("nav_zone_width", 20)
        snap_enabled: Any = zone_dict.get("snap_enabled", True)

        allowed_panels: list[str] = []
        for item in allowed_panels_list:
            if isinstance(item, str):
                allowed_panels.append(item)

        return DropZone(
            id=zone_id,
            area=area,
            orientation=str(orientation) if isinstance(orientation, str) else "horizontal",
            allowed_panels=allowed_panels,
            nav_zone_width=int(nav_zone_width) if isinstance(nav_zone_width, (int, float)) else 20,
            snap_enabled=bool(snap_enabled),
        )

    @staticmethod
    def _parse_dnd_rule(rule_dict: dict[str, Any]) -> DnDRule:
        """Parse and validate a single DnD rule definition."""
        rule_id: Any = rule_dict.get("id")
        if not isinstance(rule_id, str):
            raise ValueError("DnDRule 'id' must be a non-empty string")

        panel_id: Any = rule_dict.get("panel_id")
        if not isinstance(panel_id, str):
            raise ValueError(f"DnDRule '{rule_id}' panel_id must be a string")

        source_area: Any = rule_dict.get("source_area", "center")
        allowed_target_areas_raw: Any = rule_dict.get("allowed_target_areas", [])
        if not isinstance(allowed_target_areas_raw, list):
            allowed_target_areas_raw = []
        allowed_target_areas_list: list[Any] = allowed_target_areas_raw

        allowed_target_areas: list[str] = []
        for item in allowed_target_areas_list:
            if isinstance(item, str):
                allowed_target_areas.append(item)

        return DnDRule(
            id=rule_id,
            panel_id=panel_id,
            source_area=str(source_area) if isinstance(source_area, str) else "center",
            allowed_target_areas=allowed_target_areas,
        )

    def get_drop_zone(self, zone_id: str) -> DropZone | None:
        """Get a specific drop zone by ID."""
        if self._drop_zones_cache is None:
            self.load_drop_zones()

        return self._drop_zones_cache.get(zone_id) if self._drop_zones_cache else None

    def list_drop_zone_ids(self) -> list[str]:
        """List all drop zone IDs."""
        if self._drop_zones_cache is None:
            self.load_drop_zones()

        return list(self._drop_zones_cache.keys()) if self._drop_zones_cache else []

    def get_dnd_rule(self, rule_id: str) -> DnDRule | None:
        """Get a specific DnD rule by ID."""
        if self._rules_cache is None:
            self.load_dnd_rules()

        return self._rules_cache.get(rule_id) if self._rules_cache else None

    def get_panel_rules(self, panel_id: str) -> list[DnDRule]:
        """Get all DnD rules for a specific panel."""
        if self._rules_cache is None:
            self.load_dnd_rules()

        if not self._rules_cache:
            return []

        return [r for r in self._rules_cache.values() if r.panel_id == panel_id]
