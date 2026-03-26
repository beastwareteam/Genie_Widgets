"""Panel Factory - reads config/panels.json and provides typed panel definitions."""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

from widgetsystem.core.config_validator import ConfigValidator

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory

logger = logging.getLogger(__name__)


class PanelDefinition(TypedDict, total=False):
    """Type-safe panel configuration."""

    id: str
    name_key: str
    tooltip_key: str
    area: str
    closable: bool
    movable: bool
    floatable: bool
    delete_on_close: bool
    dnd_enabled: bool
    responsive_hidden_at: list[str]


@dataclass
class PanelConfig:
    """Parsed panel configuration with validation."""

    id: str
    name_key: str
    area: str
    closable: bool = True
    movable: bool = True
    floatable: bool = False
    delete_on_close: bool = False
    dnd_enabled: bool = True
    tooltip_key: str = ""
    responsive_hidden_at: list[str] | None = None

    def __post_init__(self) -> None:
        """Validate panel configuration."""
        valid_areas = {"left", "right", "bottom", "center"}
        if self.area not in valid_areas:
            raise ValueError(f"Invalid area '{self.area}'. Must be one of {valid_areas}")

        if self.responsive_hidden_at is None:
            self.responsive_hidden_at = []


class PanelFactory:
    """Factory for loading and managing panel configurations."""

    def __init__(
        self,
        config_path: str | Path = "config",
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize PanelFactory.

        Args:
            config_path: Path to configuration directory
            i18n_factory: Optional I18nFactory for translating panel names/tooltips
        """
        self.config_path = Path(config_path)
        self.panels_file = self.config_path / "panels.json"
        self._panels_cache: dict[str, PanelConfig] | None = None
        self._validator = ConfigValidator(self.config_path)
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}

    def set_i18n_factory(self, i18n_factory: "I18nFactory") -> None:
        """Set or update the I18nFactory instance.

        Args:
            i18n_factory: I18nFactory instance for translating strings
        """
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()

    def _translate(self, key: str, default: str | None = None) -> str:
        """Translate a key using i18n_factory if available.

        Args:
            key: Translation key
            default: Default value if key not found or no i18n_factory

        Returns:
            Translated string or default/key name
        """
        if not self._i18n_factory or not key:
            return default or key

        # Check cache first
        if key in self._translated_cache:
            return self._translated_cache[key]

        # Translate using factory
        translated = self._i18n_factory.translate(key, default=key)
        self._translated_cache[key] = translated
        return translated

    def get_panel_name(self, panel: PanelConfig) -> str:
        """Get translated name for a panel.

        Args:
            panel: PanelConfig instance

        Returns:
            Translated panel name or fallback to name_key
        """
        return self._translate(panel.name_key, panel.name_key)

    def get_panel_tooltip(self, panel: PanelConfig) -> str:
        """Get translated tooltip for a panel.

        Args:
            panel: PanelConfig instance

        Returns:
            Translated panel tooltip or empty string
        """
        return self._translate(panel.tooltip_key, "") if panel.tooltip_key else ""

    def load_panels(self) -> list[PanelConfig]:
        """Load and parse all panels from config with failsafe backup support."""
        if not self.panels_file.exists():
            raise FileNotFoundError(f"Panels configuration file not found: {self.panels_file}")

        # Use failsafe loading (auto-recovers from backup if main file is corrupted)
        try:
            raw_data_temp: Any = self._validator.load_with_failsafe(self.panels_file)
        except Exception as e:
            logger.warning(f"Failsafe load failed, trying direct load: {e}")
            with open(self.panels_file, encoding="utf-8") as f:
                raw_data_temp = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Panels configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        panels_list_raw: Any = raw_data.get("panels", [])
        if not isinstance(panels_list_raw, list):
            raise ValueError("'panels' must be an array")
        panels_list: list[Any] = panels_list_raw

        panels: list[PanelConfig] = []
        for item in panels_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            panel = self._parse_panel(item_dict)
            panels.append(panel)
            if self._panels_cache is None:
                self._panels_cache = {}
            self._panels_cache[panel.id] = panel

        return panels

    @staticmethod
    def _parse_panel(panel_dict: dict[str, Any]) -> PanelConfig:
        """Parse and validate a single panel definition."""
        panel_id: Any = panel_dict.get("id")
        if not isinstance(panel_id, str):
            raise ValueError("Panel 'id' must be a non-empty string")

        area: Any = panel_dict.get("area", "center")
        if not isinstance(area, str):
            raise ValueError(f"Panel '{panel_id}' area must be a string")

        name_key: Any = panel_dict.get("name_key", "")
        if not isinstance(name_key, str):
            name_key = ""

        tooltip_key: Any = panel_dict.get("tooltip_key", "")
        if not isinstance(tooltip_key, str):
            tooltip_key = ""

        closable: Any = panel_dict.get("closable", True)
        movable: Any = panel_dict.get("movable", True)
        floatable: Any = panel_dict.get("floatable", False)
        delete_on_close: Any = panel_dict.get("delete_on_close", False)
        dnd_enabled: Any = panel_dict.get("dnd_enabled", True)
        responsive_hidden_at_raw: Any = panel_dict.get("responsive_hidden_at", [])
        if not isinstance(responsive_hidden_at_raw, list):
            responsive_hidden_at_raw = []
        responsive_hidden_at_list: list[Any] = responsive_hidden_at_raw

        responsive_hidden_at: list[str] = []
        for raw_item in responsive_hidden_at_list:
            if isinstance(raw_item, str):
                responsive_hidden_at.append(raw_item)

        return PanelConfig(
            id=panel_id,
            name_key=name_key,
            area=area,
            closable=bool(closable),
            movable=bool(movable),
            floatable=bool(floatable),
            delete_on_close=bool(delete_on_close),
            dnd_enabled=bool(dnd_enabled),
            tooltip_key=tooltip_key,
            responsive_hidden_at=responsive_hidden_at,
        )

    def get_panel(self, panel_id: str) -> PanelConfig | None:
        """Get a specific panel by ID."""
        if self._panels_cache is None:
            self.load_panels()

        return self._panels_cache.get(panel_id) if self._panels_cache else None

    def get_panels_by_area(self, area: str) -> list[PanelConfig]:
        """Get all panels in a specific area."""
        if self._panels_cache is None:
            self.load_panels()

        if not self._panels_cache:
            return []

        return [p for p in self._panels_cache.values() if p.area == area]

    def list_panel_ids(self) -> list[str]:
        """List all panel IDs."""
        if self._panels_cache is None:
            self.load_panels()

        return list(self._panels_cache.keys()) if self._panels_cache else []

    def get_dnd_enabled_panels(self) -> list[PanelConfig]:
        """Get all panels with drag-and-drop enabled."""
        if self._panels_cache is None:
            self.load_panels()

        if not self._panels_cache:
            return []

        return [p for p in self._panels_cache.values() if p.dnd_enabled]

    def get_responsive_rules(self, panel_id: str) -> list[str]:
        """Get responsive breakpoints where a panel is hidden."""
        panel = self.get_panel(panel_id)
        if panel is None:
            return []
        if panel.responsive_hidden_at is None:
            return []
        return panel.responsive_hidden_at

    def add_panel(
        self,
        panel_id: str,
        name_key: str,
        area: str = "center",
        closable: bool = True,
        movable: bool = True,
    ) -> bool:
        """Create and save new panel."""
        try:
            new_panel = PanelConfig(
                id=panel_id,
                name_key=name_key,
                area=area,
                closable=closable,
                movable=movable,
                floatable=False,
                delete_on_close=False,
                dnd_enabled=True,
                responsive_hidden_at=[],
            )

            if self._panels_cache is None:
                self.load_panels()

            if self._panels_cache is not None:
                self._panels_cache[panel_id] = new_panel

            return self.save_to_file()
        except Exception:
            return False

    def save_to_file(self) -> bool:
        """Serialize and write panels to file."""
        try:
            if self._panels_cache is None:
                return False

            data: dict[str, Any] = {
                "panels": [self._panel_to_dict(panel) for panel in self._panels_cache.values()],
            }

            with open(self.panels_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False

    @staticmethod
    def _panel_to_dict(panel: PanelConfig) -> dict[str, Any]:
        """Convert PanelConfig to dictionary."""
        result: dict[str, Any] = {
            "id": panel.id,
            "name_key": panel.name_key,
            "area": panel.area,
            "closable": panel.closable,
            "movable": panel.movable,
            "floatable": panel.floatable,
            "delete_on_close": panel.delete_on_close,
            "dnd_enabled": panel.dnd_enabled,
            "responsive_hidden_at": panel.responsive_hidden_at or [],
        }

        # Only include optional fields if set
        if panel.tooltip_key:
            result["tooltip_key"] = panel.tooltip_key

        return result
