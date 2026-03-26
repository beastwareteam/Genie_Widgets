"""Menu Factory - reads config/menus.json and provides typed menu definitions with nesting."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


class MenuItemDefinition(TypedDict, total=False):
    """Type-safe menu item configuration."""

    id: str
    label_key: str
    type: str
    action: str
    shortcut: str
    visible: bool
    children: list["MenuItemDefinition"]


@dataclass
class MenuItem:
    """Represents a single menu item with optional nested children."""

    id: str
    label_key: str = ""
    type: str = "action"
    action: str = ""
    shortcut: str = ""
    visible: bool = True
    tooltip_key: str = ""
    children: list["MenuItem"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate menu item configuration."""
        valid_types = {"menu", "action", "separator"}
        if self.type not in valid_types:
            raise ValueError(f"Invalid type '{self.type}'. Must be one of {valid_types}")


class MenuFactory:
    """Factory for loading and managing menu configurations with nesting support."""

    def __init__(
        self,
        config_path: str | Path = "config",
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize MenuFactory.

        Args:
            config_path: Path to configuration directory
            i18n_factory: Optional I18nFactory for translating menu labels/tooltips
        """
        self.config_path = Path(config_path)
        self.menus_file = self.config_path / "menus.json"
        self._menus_cache: dict[str, MenuItem] | None = None
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

    def get_menu_label(self, menu: MenuItem) -> str:
        """Get translated label for a menu item.

        Args:
            menu: MenuItem instance

        Returns:
            Translated menu label or fallback to label_key
        """
        return self._translate(menu.label_key, menu.label_key)

    def get_menu_tooltip(self, menu: MenuItem) -> str:
        """Get translated tooltip for a menu item.

        Args:
            menu: MenuItem instance

        Returns:
            Translated menu tooltip or empty string
        """
        return self._translate(menu.tooltip_key, "") if menu.tooltip_key else ""

    def load_menus(self) -> list[MenuItem]:
        """Load and parse all menus from config."""
        if not self.menus_file.exists():
            raise FileNotFoundError(f"Menus configuration file not found: {self.menus_file}")

        with open(self.menus_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Menus configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        menus_list_raw: Any = raw_data.get("menus", [])
        if not isinstance(menus_list_raw, list):
            raise ValueError("'menus' must be an array")
        menus_list: list[Any] = menus_list_raw

        menus: list[MenuItem] = []
        for item in menus_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            menu_item = self._parse_menu_item(item_dict)
            menus.append(menu_item)
            if self._menus_cache is None:
                self._menus_cache = {}
            self._register_menu_item_recursive(menu_item)

        return menus

    @staticmethod
    def _parse_menu_item(item_dict: dict[str, Any]) -> MenuItem:
        """Parse and validate a single menu item with nested support."""
        item_id: Any = item_dict.get("id")
        if not isinstance(item_id, str):
            raise ValueError("MenuItem 'id' must be a non-empty string")

        label_key: Any = item_dict.get("label_key", "")
        if not isinstance(label_key, str):
            label_key = ""

        tooltip_key: Any = item_dict.get("tooltip_key", "")
        if not isinstance(tooltip_key, str):
            tooltip_key = ""

        item_type: Any = item_dict.get("type", "action")
        if not isinstance(item_type, str):
            item_type = "action"

        action: Any = item_dict.get("action", "")
        if not isinstance(action, str):
            action = ""

        shortcut: Any = item_dict.get("shortcut", "")
        if not isinstance(shortcut, str):
            shortcut = ""

        visible: Any = item_dict.get("visible", True)

        children: list[MenuItem] = []
        children_list: Any = item_dict.get("children", [])
        if isinstance(children_list, list):
            for child_dict in children_list:
                if isinstance(child_dict, dict):
                    child_item = MenuFactory._parse_menu_item(cast("dict[str, Any]", child_dict))
                    children.append(child_item)

        return MenuItem(
            id=item_id,
            label_key=label_key,
            type=item_type,
            action=action,
            shortcut=shortcut,
            visible=bool(visible),
            tooltip_key=tooltip_key,
            children=children,
        )

    def _register_menu_item_recursive(self, menu_item: MenuItem) -> None:
        """Register a menu item and all its children in the cache."""
        if self._menus_cache is None:
            self._menus_cache = {}

        self._menus_cache[menu_item.id] = menu_item

        for child in menu_item.children:
            self._register_menu_item_recursive(child)

    def get_menu_item(self, item_id: str) -> MenuItem | None:
        """Get a specific menu item by ID (searches all levels)."""
        if self._menus_cache is None:
            self.load_menus()

        return self._menus_cache.get(item_id) if self._menus_cache else None

    def get_root_menus(self) -> list[MenuItem]:
        """Get only root menu items (no parent)."""
        if self._menus_cache is None:
            self.load_menus()

        if not self._menus_cache:
            return []

        with open(self.menus_file, encoding="utf-8") as f:
            raw_data = json.load(f)

        menus_list = raw_data.get("menus", [])
        root_menus: list[MenuItem] = []

        for item in menus_list:
            item_dict = cast("dict[str, Any]", item)
            menu_item = self._parse_menu_item(item_dict)
            root_menus.append(menu_item)

        return root_menus

    def find_actions(self) -> list[MenuItem]:
        """Find all menu items of type 'action'."""
        if self._menus_cache is None:
            self.load_menus()

        if not self._menus_cache:
            return []

        return [m for m in self._menus_cache.values() if m.type == "action"]

    def get_visible_items(self, parent_id: str | None = None) -> list[MenuItem]:
        """Get all visible menu items (optionally filtered by parent)."""
        if self._menus_cache is None:
            self.load_menus()

        if not self._menus_cache:
            return []

        if parent_id is None:
            return [m for m in self._menus_cache.values() if m.visible]

        parent = self.get_menu_item(parent_id)
        if not parent:
            return []

        return [child for child in parent.children if child.visible]

    def get_menu_hierarchy(self, menu_id: str) -> dict[str, Any]:
        """Get a menu and all its children as a nested dictionary."""
        menu_item = self.get_menu_item(menu_id)
        if not menu_item:
            return {}

        return self._menu_to_dict(menu_item)

    @staticmethod
    @staticmethod
    def _menu_to_dict(menu: MenuItem) -> dict[str, Any]:
        """Convert a MenuItem to a dictionary representation."""
        result: dict[str, Any] = {
            "id": menu.id,
            "label_key": menu.label_key,
            "type": menu.type,
            "action": menu.action,
            "shortcut": menu.shortcut,
            "visible": menu.visible,
        }

        # Only include optional fields if set
        if menu.tooltip_key:
            result["tooltip_key"] = menu.tooltip_key

        if menu.children:
            result["children"] = [MenuFactory._menu_to_dict(child) for child in menu.children]

        return result

    def list_shortcuts(self) -> dict[str, str]:
        """Get all shortcuts mapped to action IDs."""
        if self._menus_cache is None:
            self.load_menus()

        shortcuts: dict[str, str] = {}

        if self._menus_cache:
            for menu_item in self._menus_cache.values():
                if menu_item.shortcut and menu_item.action:
                    shortcuts[menu_item.id] = menu_item.shortcut

        return shortcuts

    def add_menu_item(
        self,
        menu_id: str,
        label_key: str,
        menu_type: str = "action",
        action: str = "",
        shortcut: str = "",
    ) -> bool:
        """Create and save new menu item."""
        try:
            new_menu = MenuItem(
                id=menu_id,
                label_key=label_key,
                type=menu_type,
                action=action,
                shortcut=shortcut,
            )

            if self._menus_cache is None:
                self.load_menus()

            if self._menus_cache is not None:
                self._menus_cache[menu_id] = new_menu

            return self.save_to_file()
        except Exception:
            return False

    def save_to_file(self) -> bool:
        """Serialize and write menus to file."""
        try:
            if self._menus_cache is None:
                return False

            data: dict[str, Any] = {
                "menus": [MenuFactory._menu_to_dict(menu) for menu in self._menus_cache.values()],
            }

            with open(self.menus_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False
