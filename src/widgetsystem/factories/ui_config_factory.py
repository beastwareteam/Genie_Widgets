"""UI Configuration Factory - manages dynamic UI configuration and widget creation."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


class WidgetPropertyDefinition(TypedDict, total=False):
    """Type-safe widget property configuration."""

    name: str
    type: str  # "text", "number", "boolean", "color", "select", "multiline"
    label_key: str
    default: Any
    required: bool
    options: list[dict[str, str]]
    placeholder: str


class WidgetDefinition(TypedDict, total=False):
    """Type-safe widget configuration for UI builder."""

    id: str
    type: str  # "button", "input", "label", "list", "menu", "panel", "tabs"
    label_key: str
    properties: dict[str, WidgetPropertyDefinition]
    dnd_enabled: bool
    resizable: bool
    movable: bool
    container: bool  # Can contain other widgets


class UIConfigPageDefinition(TypedDict, total=False):
    """Type-safe UI configuration page."""

    id: str
    title_key: str
    description_key: str
    category: str  # "menus", "lists", "tabs", "panels", "theme"
    icon: str
    order: int
    widgets: list[WidgetDefinition]


@dataclass
class WidgetProperty:
    """Represents a widget property definition."""

    name: str
    type: str
    label_key: str = ""
    default: Any = None
    required: bool = False
    options: list[dict[str, str]] = field(default_factory=list)
    placeholder: str = ""

    def __post_init__(self) -> None:
        """Validate property configuration."""
        valid_types = {"text", "number", "boolean", "color", "select", "multiline"}
        if self.type not in valid_types:
            raise ValueError(f"Invalid property type '{self.type}'. Must be one of {valid_types}")


@dataclass
class Widget:
    """Represents a configurable widget definition."""

    id: str
    type: str
    label_key: str = ""
    properties: dict[str, WidgetProperty] = field(default_factory=dict)
    dnd_enabled: bool = True
    resizable: bool = False
    movable: bool = True
    container: bool = False

    def __post_init__(self) -> None:
        """Validate widget configuration."""
        valid_types = {"button", "input", "label", "list", "menu", "panel", "tabs", "custom"}
        if self.type not in valid_types:
            raise ValueError(f"Invalid widget type '{self.type}'. Must be one of {valid_types}")


@dataclass
class UIConfigPage:
    """Represents a configuration page in the UI builder."""

    id: str
    title_key: str
    description_key: str = ""
    category: str = "general"
    icon: str = ""
    order: int = 0
    widgets: list[Widget] = field(default_factory=list)


class UIConfigFactory:
    """Factory for loading and managing UI configuration definitions."""

    def __init__(self, config_path: str | Path = "config", i18n_factory: "I18nFactory | None" = None) -> None:
        """Initialize UIConfigFactory.

        Args:
            config_path: Path to configuration directory
            i18n_factory: Optional I18nFactory instance for translations
        """
        self.config_path = Path(config_path)
        self.config_file = self.config_path / "ui_config.json"
        self._pages_cache: dict[str, UIConfigPage] | None = None
        self._widgets_cache: dict[str, Widget] | None = None
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}

    def set_i18n_factory(self, i18n_factory: "I18nFactory") -> None:
        """Set internationalization factory and clear cache.

        Args:
            i18n_factory: I18nFactory instance for translations
        """
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()

    def _translate(self, key: str, default: str | None = None) -> str:
        """Translate a key using i18n factory.

        Args:
            key: Translation key
            default: Default value if translation not found

        Returns:
            Translated string or default/key
        """
        if not self._i18n_factory or not key:
            return default or key

        if key in self._translated_cache:
            return self._translated_cache[key]

        translated = self._i18n_factory.translate(key, default=key)
        self._translated_cache[key] = translated
        return translated

    def get_page_title(self, page: UIConfigPage) -> str:
        """Get translated title for a configuration page.

        Args:
            page: UIConfigPage instance

        Returns:
            Translated page title
        """
        return self._translate(page.title_key, page.title_key)

    def get_page_description(self, page: UIConfigPage) -> str:
        """Get translated description for a configuration page.

        Args:
            page: UIConfigPage instance

        Returns:
            Translated page description
        """
        return self._translate(page.description_key, "") if page.description_key else ""

    def get_widget_label(self, widget: Widget) -> str:
        """Get translated label for a widget.

        Args:
            widget: Widget instance

        Returns:
            Translated widget label
        """
        return self._translate(widget.label_key, widget.label_key) if widget.label_key else ""

    def get_property_label(self, prop: WidgetProperty) -> str:
        """Get translated label for a widget property.

        Args:
            prop: WidgetProperty instance

        Returns:
            Translated property label
        """
        return self._translate(prop.label_key, prop.label_key) if prop.label_key else ""

    def load_ui_config_pages(self) -> list[UIConfigPage]:
        """Load and parse all UI configuration pages from config."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"UI config file not found: {self.config_file}")

        with open(self.config_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("UI config must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        pages_raw: Any = raw_data.get("config_pages", [])
        if not isinstance(pages_raw, list):
            raise ValueError("'config_pages' must be an array")
        pages_list: list[Any] = pages_raw

        pages: list[UIConfigPage] = []
        for page_data in pages_list:
            if isinstance(page_data, dict):
                page = self._parse_config_page(cast("dict[str, Any]", page_data))
                pages.append(page)

        self._pages_cache = {page.id: page for page in pages}
        return pages

    def _parse_config_page(self, data: dict[str, Any]) -> UIConfigPage:
        """Parse a configuration page from raw data."""
        page_id: Any = data.get("id")
        title_key: Any = data.get("title_key")
        desc_key: Any = data.get("description_key", "")
        category: Any = data.get("category", "general")
        icon: Any = data.get("icon", "")
        order: Any = data.get("order", 0)

        if not isinstance(page_id, str):
            raise ValueError("Config page 'id' must be a string")
        if not isinstance(title_key, str):
            raise ValueError("Config page 'title_key' must be a string")

        widgets_raw: Any = data.get("widgets", [])
        if not isinstance(widgets_raw, list):
            widgets_raw = []
        widgets_list: list[Any] = widgets_raw

        widgets: list[Widget] = []
        for widget_data in widgets_list:
            if isinstance(widget_data, dict):
                widget = self._parse_widget(cast("dict[str, Any]", widget_data))
                widgets.append(widget)

        return UIConfigPage(
            id=page_id,
            title_key=title_key,
            description_key=str(desc_key),
            category=str(category),
            icon=str(icon),
            order=int(order),
            widgets=widgets,
        )

    def _parse_widget(self, data: dict[str, Any]) -> Widget:
        """Parse a widget definition from raw data."""
        widget_id: Any = data.get("id")
        widget_type: Any = data.get("type")
        label_key: Any = data.get("label_key", "")
        dnd_enabled: Any = data.get("dnd_enabled", True)
        resizable: Any = data.get("resizable", False)
        movable: Any = data.get("movable", True)
        container: Any = data.get("container", False)

        if not isinstance(widget_id, str):
            raise ValueError("Widget 'id' must be a string")
        if not isinstance(widget_type, str):
            raise ValueError("Widget 'type' must be a string")

        properties_raw: Any = data.get("properties", {})
        if not isinstance(properties_raw, dict):
            properties_raw = {}
        properties_dict: dict[str, Any] = cast("dict[str, Any]", properties_raw)

        properties: dict[str, WidgetProperty] = {}
        for prop_name, prop_data in properties_dict.items():
            if isinstance(prop_data, dict):
                prop = self._parse_widget_property(prop_name, cast("dict[str, Any]", prop_data))
                properties[prop_name] = prop

        return Widget(
            id=widget_id,
            type=widget_type,
            label_key=str(label_key),
            properties=properties,
            dnd_enabled=bool(dnd_enabled),
            resizable=bool(resizable),
            movable=bool(movable),
            container=bool(container),
        )

    def _parse_widget_property(self, name: str, data: dict[str, Any]) -> WidgetProperty:
        """Parse a widget property from raw data."""
        prop_type: Any = data.get("type", "text")
        label_key: Any = data.get("label_key", "")
        default: Any = data.get("default")
        required: Any = data.get("required", False)
        options_raw: Any = data.get("options", [])
        placeholder: Any = data.get("placeholder", "")

        if not isinstance(options_raw, list):
            options_raw = []
        options: list[dict[str, str]] = cast("list[dict[str, str]]", options_raw)

        return WidgetProperty(
            name=name,
            type=str(prop_type),
            label_key=str(label_key),
            default=default,
            required=bool(required),
            options=options,
            placeholder=str(placeholder),
        )

    def get_page_by_id(self, page_id: str) -> UIConfigPage | None:
        """Get a configuration page by ID."""
        if self._pages_cache is None:
            try:
                self.load_ui_config_pages()
            except (FileNotFoundError, ValueError, json.JSONDecodeError):
                return None

        return self._pages_cache.get(page_id) if self._pages_cache else None

    def get_pages_by_category(self, category: str) -> list[UIConfigPage]:
        """Get all pages in a specific category."""
        if self._pages_cache is None:
            try:
                self.load_ui_config_pages()
            except (FileNotFoundError, ValueError, json.JSONDecodeError):
                return []

        if self._pages_cache is None:
            return []

        return sorted(
            [page for page in self._pages_cache.values() if page.category == category],
            key=lambda p: p.order,
        )

    def get_all_categories(self) -> list[str]:
        """Get all available configuration categories."""
        if self._pages_cache is None:
            try:
                self.load_ui_config_pages()
            except (FileNotFoundError, ValueError, json.JSONDecodeError):
                return []

        if self._pages_cache is None:
            return []

        categories = set()
        for page in self._pages_cache.values():
            categories.add(page.category)
        return sorted(categories)
