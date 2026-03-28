"""Tabs Factory - reads config/tabs.json and provides typed tab definitions with nesting."""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

from widgetsystem.core.config_validator import ConfigValidator

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory

logger = logging.getLogger(__name__)


class TabDefinition(TypedDict, total=False):
    """Type-safe tab configuration."""

    id: str
    title_key: str
    component: str
    closable: bool
    active: bool
    children: list["TabDefinition"]


class TabGroupDefinition(TypedDict, total=False):
    """Type-safe tab group configuration."""

    id: str
    title_key: str
    dock_area: str
    orientation: str
    tabs: list[TabDefinition]


@dataclass
class Tab:
    """Represents a single tab with optional nested children.

    Attributes:
        id: Unique tab identifier
        title_key: i18n key for tab title
        component: Component ID for content widget (from ComponentRegistry)
        closable: Whether tab can be closed
        movable: Whether tab can be dragged/reordered
        floatable: Whether tab can be floated to own window
        active: Whether tab is initially active
        icon: Optional icon path or icon name
        tooltip: Optional tooltip text or i18n key
        badge: Optional badge text (e.g., notification count)
        disabled: Whether tab is disabled
        config: Additional configuration passed to component
        children: Nested child tabs
    """

    id: str
    title_key: str
    component: str = ""
    closable: bool = True
    movable: bool = True
    floatable: bool = True
    active: bool = False
    icon: str = ""
    tooltip: str = ""
    badge: str = ""
    disabled: bool = False
    config: dict[str, Any] = field(default_factory=dict)
    children: list["Tab"] = field(default_factory=list)


@dataclass
class TabGroup:
    """Represents a group of tabs in a dock area."""

    id: str
    title_key: str
    dock_area: str
    orientation: str
    tabs: list[Tab] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate tab group configuration."""
        valid_areas = {"left", "right", "bottom", "center"}
        if self.dock_area not in valid_areas:
            raise ValueError(f"Invalid dock_area '{self.dock_area}'. Must be one of {valid_areas}")

        valid_orientations = {"horizontal", "vertical"}
        if self.orientation not in valid_orientations:
            raise ValueError(
                f"Invalid orientation '{self.orientation}'. Must be one of {valid_orientations}",
            )


class TabsFactory:
    """Factory for loading and managing tab configurations with nesting support.

    Architectural note:
        This factory models the persisted tab configuration layer only.
        In the original application, complete tab automation/editing also depends on
        runtime structures managed by controllers such as `TabSubsystem`,
        `UnifiedTabManager`, `TabNavigationController`, and `TabCommandController`.

        As long as those runtime identities and container relationships are not
        bridged back into this persistence layer, any editor using `TabsFactory`
        should be treated as a demo/configuration surface rather than the final
        authoritative runtime tab model.
    """

    def __init__(
        self,
        config_path: str | Path = "config",
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize TabsFactory.

        Args:
            config_path: Path to configuration directory
            i18n_factory: Optional I18nFactory for translating tab titles/tooltips
        """
        self.config_path = Path(config_path)
        self.tabs_file = self.config_path / "tabs.json"
        self._tab_groups_cache: dict[str, TabGroup] | None = None
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

    def get_tab_title(self, tab: Tab) -> str:
        """Get translated title for a tab.

        Args:
            tab: Tab instance

        Returns:
            Translated tab title or fallback to title_key
        """
        return self._translate(tab.title_key, tab.title_key)

    def get_tab_tooltip(self, tab: Tab) -> str:
        """Get translated tooltip for a tab.

        Args:
            tab: Tab instance

        Returns:
            Translated tab tooltip or empty string
        """
        return self._translate(tab.tooltip, "") if tab.tooltip else ""

    def load_tab_groups(self) -> list[TabGroup]:
        """Load and parse all tab groups from config with failsafe backup support."""
        if not self.tabs_file.exists():
            raise FileNotFoundError(f"Tabs configuration file not found: {self.tabs_file}")

        # Use failsafe loading (auto-recovers from backup if main file is corrupted)
        try:
            raw_data_temp: Any = self._validator.load_with_failsafe(self.tabs_file)
        except Exception as e:
            logger.warning("Failsafe load failed, trying direct load: %s", e)
            with open(self.tabs_file, encoding="utf-8") as f:
                raw_data_temp = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Tabs configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        tab_groups_list_raw: Any = raw_data.get("tab_groups", [])
        if not isinstance(tab_groups_list_raw, list):
            raise ValueError("'tab_groups' must be an array")
        tab_groups_list: list[Any] = tab_groups_list_raw

        tab_groups: list[TabGroup] = []
        for item in tab_groups_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            tab_group = self._parse_tab_group(item_dict)
            tab_groups.append(tab_group)
            if self._tab_groups_cache is None:
                self._tab_groups_cache = {}
            self._tab_groups_cache[tab_group.id] = tab_group

        return tab_groups

    @staticmethod
    def _parse_tab(tab_dict: dict[str, Any]) -> Tab:
        """Parse and validate a single tab definition with nested support."""
        tab_id: Any = tab_dict.get("id")
        if not isinstance(tab_id, str):
            raise ValueError("Tab 'id' must be a non-empty string")

        title_key: Any = tab_dict.get("title_key", "")
        if not isinstance(title_key, str):
            title_key = ""

        component: Any = tab_dict.get("component", "")
        if not isinstance(component, str):
            component = ""

        closable: Any = tab_dict.get("closable", True)
        movable: Any = tab_dict.get("movable", True)
        floatable: Any = tab_dict.get("floatable", True)
        active: Any = tab_dict.get("active", False)

        # Optional properties
        icon: Any = tab_dict.get("icon", "")
        if not isinstance(icon, str):
            icon = ""

        tooltip: Any = tab_dict.get("tooltip", "")
        if not isinstance(tooltip, str):
            tooltip = ""

        badge: Any = tab_dict.get("badge", "")
        if not isinstance(badge, str):
            badge = str(badge) if badge else ""

        disabled: Any = tab_dict.get("disabled", False)

        config: Any = tab_dict.get("config", {})
        if not isinstance(config, dict):
            config = {}

        children: list[Tab] = []
        children_list_raw: Any = tab_dict.get("children", [])
        if isinstance(children_list_raw, list):
            children_list: list[Any] = children_list_raw
            for child_dict in children_list:
                if isinstance(child_dict, dict):
                    child_tab = TabsFactory._parse_tab(cast("dict[str, Any]", child_dict))
                    children.append(child_tab)

        return Tab(
            id=tab_id,
            title_key=title_key,
            component=component,
            closable=bool(closable),
            movable=bool(movable),
            floatable=bool(floatable),
            active=bool(active),
            icon=icon,
            tooltip=tooltip,
            badge=badge,
            disabled=bool(disabled),
            config=cast("dict[str, Any]", config),
            children=children,
        )

    @staticmethod
    def _parse_tab_group(group_dict: dict[str, Any]) -> TabGroup:
        """Parse and validate a single tab group definition."""
        group_id: Any = group_dict.get("id")
        if not isinstance(group_id, str):
            raise ValueError("TabGroup 'id' must be a non-empty string")

        title_key: Any = group_dict.get("title_key", "")
        if not isinstance(title_key, str):
            title_key = ""

        dock_area: Any = group_dict.get("dock_area", "center")
        if not isinstance(dock_area, str):
            raise ValueError(f"TabGroup '{group_id}' dock_area must be a string")

        orientation: Any = group_dict.get("orientation", "horizontal")
        if not isinstance(orientation, str):
            raise ValueError(f"TabGroup '{group_id}' orientation must be a string")

        tabs: list[Tab] = []
        tabs_list_raw: Any = group_dict.get("tabs", [])
        if isinstance(tabs_list_raw, list):
            tabs_list: list[Any] = tabs_list_raw
            for tab_dict in tabs_list:
                if isinstance(tab_dict, dict):
                    tab = TabsFactory._parse_tab(cast("dict[str, Any]", tab_dict))
                    tabs.append(tab)

        return TabGroup(
            id=group_id,
            title_key=title_key,
            dock_area=dock_area,
            orientation=orientation,
            tabs=tabs,
        )

    def get_tab_group(self, group_id: str) -> TabGroup | None:
        """Get a specific tab group by ID."""
        if self._tab_groups_cache is None:
            self.load_tab_groups()

        return self._tab_groups_cache.get(group_id) if self._tab_groups_cache else None

    def get_tab_groups_by_area(self, dock_area: str) -> list[TabGroup]:
        """Get all tab groups in a specific dock area."""
        if self._tab_groups_cache is None:
            self.load_tab_groups()

        if not self._tab_groups_cache:
            return []

        return [g for g in self._tab_groups_cache.values() if g.dock_area == dock_area]

    def find_tab_by_id(self, tab_id: str) -> Tab | None:
        """Find a tab by ID (searches recursively through nested children)."""
        if self._tab_groups_cache is None:
            self.load_tab_groups()

        if not self._tab_groups_cache:
            return None

        for tab_group in self._tab_groups_cache.values():
            result = self._find_tab_recursive(tab_group.tabs, tab_id)
            if result:
                return result

        return None

    @staticmethod
    def _find_tab_recursive(tabs: list[Tab], tab_id: str) -> Tab | None:
        """Recursively search for a tab in a list with nesting."""
        for tab in tabs:
            if tab.id == tab_id:
                return tab
            if tab.children:
                result = TabsFactory._find_tab_recursive(tab.children, tab_id)
                if result:
                    return result
        return None

    def list_tab_group_ids(self) -> list[str]:
        """List all tab group IDs."""
        if self._tab_groups_cache is None:
            self.load_tab_groups()

        return list(self._tab_groups_cache.keys()) if self._tab_groups_cache else []

    def get_flat_tab_list(self, group_id: str) -> list[Tab]:
        """Get a flattened list of all tabs in a group (including nested)."""
        tab_group = self.get_tab_group(group_id)
        if not tab_group:
            return []

        result: list[Tab] = []

        def flatten(tabs: list[Tab]) -> None:
            for tab in tabs:
                result.append(tab)
                if tab.children:
                    flatten(tab.children)

        flatten(tab_group.tabs)
        return result

    def add_tab_group(
        self,
        group_id: str,
        title_key: str,
        dock_area: str = "center",
        orientation: str = "horizontal",
    ) -> bool:
        """Create and save new tab group."""
        try:
            new_group = TabGroup(
                id=group_id,
                title_key=title_key,
                dock_area=dock_area,
                orientation=orientation,
                tabs=[],
            )

            if self._tab_groups_cache is None:
                self.load_tab_groups()

            if self._tab_groups_cache is not None:
                self._tab_groups_cache[group_id] = new_group

            return self.save_to_file()
        except Exception:
            return False

    def save_to_file(self) -> bool:
        """Serialize and write tab groups to file."""
        try:
            if self._tab_groups_cache is None:
                return False

            data: dict[str, Any] = {
                "tab_groups": [
                    self._tab_group_to_dict(group) for group in self._tab_groups_cache.values()
                ],
            }

            with open(self.tabs_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False

    @staticmethod
    def _tab_group_to_dict(group: TabGroup) -> dict[str, Any]:
        """Convert TabGroup to dictionary."""
        return {
            "id": group.id,
            "title_key": group.title_key,
            "dock_area": group.dock_area,
            "orientation": group.orientation,
            "tabs": [TabsFactory._tab_to_dict(tab) for tab in group.tabs],
        }

    @staticmethod
    def _tab_to_dict(tab: Tab) -> dict[str, Any]:
        """Convert Tab to dictionary."""
        result: dict[str, Any] = {
            "id": tab.id,
            "title_key": tab.title_key,
            "component": tab.component,
            "closable": tab.closable,
            "movable": tab.movable,
            "floatable": tab.floatable,
            "active": tab.active,
        }

        # Only include optional fields if set
        if tab.icon:
            result["icon"] = tab.icon
        if tab.tooltip:
            result["tooltip"] = tab.tooltip
        if tab.badge:
            result["badge"] = tab.badge
        if tab.disabled:
            result["disabled"] = tab.disabled
        if tab.config:
            result["config"] = tab.config

        if tab.children:
            result["children"] = [TabsFactory._tab_to_dict(child) for child in tab.children]

        return result
