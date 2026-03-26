"""Action Factory - loads config/actions.json and provides typed action definitions."""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory

logger = logging.getLogger(__name__)


class ActionDefinition(TypedDict, total=False):
    """Type-safe action configuration from JSON."""

    id: str
    label_key: str
    tooltip_key: str
    status_tip_key: str
    icon: str
    shortcut: str
    action: str
    enabled: bool
    checkable: bool
    visible: bool
    category: str


@dataclass
class ActionConfig:
    """Parsed action configuration with validation."""

    id: str
    label_key: str
    action: str
    tooltip_key: str = ""
    status_tip_key: str = ""
    icon: str = ""
    shortcut: str = ""
    enabled: bool = True
    checkable: bool = False
    visible: bool = True
    category: str = "general"

    def __post_init__(self) -> None:
        """Validate action configuration."""
        if not self.id:
            raise ValueError("ActionConfig 'id' must be a non-empty string")
        if not self.action:
            raise ValueError(f"ActionConfig '{self.id}' must have an 'action' value")


class ActionFactory:
    """Factory for loading action configurations from JSON."""

    def __init__(
        self,
        config_path: str | Path = "config",
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize ActionFactory.

        Args:
            config_path: Path to configuration directory
            i18n_factory: Optional I18nFactory for translating action labels/tooltips
        """
        self.config_path = Path(config_path)
        self.actions_file = self.config_path / "actions.json"
        self._actions_cache: dict[str, ActionConfig] | None = None
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

        if key in self._translated_cache:
            return self._translated_cache[key]

        translated = self._i18n_factory.translate(key, default=key)
        self._translated_cache[key] = translated
        return translated

    def load_actions(self) -> list[ActionConfig]:
        """Load and parse all actions from config.

        Returns:
            List of ActionConfig instances

        Raises:
            FileNotFoundError: If actions.json doesn't exist
            ValueError: If config is invalid
        """
        if not self.actions_file.exists():
            logger.warning("Actions config file not found: %s", self.actions_file)
            return []

        with open(self.actions_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Actions configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        actions_list_raw: Any = raw_data.get("actions", [])
        if not isinstance(actions_list_raw, list):
            raise ValueError("'actions' must be an array")
        actions_list: list[Any] = actions_list_raw

        actions: list[ActionConfig] = []
        self._actions_cache = {}

        for item in actions_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            try:
                action = self._parse_action(item_dict)
                actions.append(action)
                self._actions_cache[action.id] = action
            except ValueError as e:
                logger.warning("Skipping invalid action: %s", e)

        logger.info("Loaded %d actions from %s", len(actions), self.actions_file)
        return actions

    @staticmethod
    def _parse_action(item_dict: dict[str, Any]) -> ActionConfig:
        """Parse and validate a single action from dict.

        Args:
            item_dict: Raw action dictionary from JSON

        Returns:
            ActionConfig instance

        Raises:
            ValueError: If required fields are missing
        """
        item_id: Any = item_dict.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise ValueError("Action 'id' must be a non-empty string")

        label_key: Any = item_dict.get("label_key", "")
        if not isinstance(label_key, str):
            label_key = ""

        action: Any = item_dict.get("action", "")
        if not isinstance(action, str):
            action = ""

        tooltip_key: Any = item_dict.get("tooltip_key", "")
        if not isinstance(tooltip_key, str):
            tooltip_key = ""

        status_tip_key: Any = item_dict.get("status_tip_key", "")
        if not isinstance(status_tip_key, str):
            status_tip_key = ""

        icon: Any = item_dict.get("icon", "")
        if not isinstance(icon, str):
            icon = ""

        shortcut: Any = item_dict.get("shortcut", "")
        if not isinstance(shortcut, str):
            shortcut = ""

        enabled: Any = item_dict.get("enabled", True)
        checkable: Any = item_dict.get("checkable", False)
        visible: Any = item_dict.get("visible", True)

        category: Any = item_dict.get("category", "general")
        if not isinstance(category, str):
            category = "general"

        return ActionConfig(
            id=item_id,
            label_key=label_key,
            action=action,
            tooltip_key=tooltip_key,
            status_tip_key=status_tip_key,
            icon=icon,
            shortcut=shortcut,
            enabled=bool(enabled),
            checkable=bool(checkable),
            visible=bool(visible),
            category=category,
        )

    def get_action_config(self, action_id: str) -> ActionConfig | None:
        """Get a specific action configuration by ID.

        Args:
            action_id: The action ID to look up

        Returns:
            ActionConfig or None if not found
        """
        if self._actions_cache is None:
            self.load_actions()

        return self._actions_cache.get(action_id) if self._actions_cache else None

    def get_actions_by_category(self, category: str) -> list[ActionConfig]:
        """Get all actions in a specific category.

        Args:
            category: Category name (e.g., "file", "dock", "tools")

        Returns:
            List of ActionConfig instances in that category
        """
        if self._actions_cache is None:
            self.load_actions()

        if not self._actions_cache:
            return []

        return [a for a in self._actions_cache.values() if a.category == category]

    def get_action_label(self, action: ActionConfig) -> str:
        """Get translated label for an action.

        Args:
            action: ActionConfig instance

        Returns:
            Translated action label or fallback to label_key
        """
        return self._translate(action.label_key, action.label_key)

    def get_action_tooltip(self, action: ActionConfig) -> str:
        """Get translated tooltip for an action.

        Args:
            action: ActionConfig instance

        Returns:
            Translated action tooltip or empty string
        """
        return self._translate(action.tooltip_key, "") if action.tooltip_key else ""

    def get_action_status_tip(self, action: ActionConfig) -> str:
        """Get translated status tip for an action.

        Args:
            action: ActionConfig instance

        Returns:
            Translated status tip or empty string
        """
        return (
            self._translate(action.status_tip_key, "")
            if action.status_tip_key
            else ""
        )

    def list_shortcuts(self) -> dict[str, str]:
        """Get all shortcuts mapped to action IDs.

        Returns:
            Dictionary mapping action IDs to shortcuts
        """
        if self._actions_cache is None:
            self.load_actions()

        shortcuts: dict[str, str] = {}
        if self._actions_cache:
            for action in self._actions_cache.values():
                if action.shortcut:
                    shortcuts[action.id] = action.shortcut

        return shortcuts

    def list_categories(self) -> list[str]:
        """Get all unique action categories.

        Returns:
            Sorted list of category names
        """
        if self._actions_cache is None:
            self.load_actions()

        if not self._actions_cache:
            return []

        categories = {a.category for a in self._actions_cache.values()}
        return sorted(categories)
