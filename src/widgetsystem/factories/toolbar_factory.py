"""Toolbar Factory - loads config/toolbar.json and creates QToolBar instances."""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QToolBar, QToolButton

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow, QWidget

    from widgetsystem.core.action_registry import ActionRegistry
    from widgetsystem.factories.i18n_factory import I18nFactory

logger = logging.getLogger(__name__)


class ToolbarItemDefinition(TypedDict, total=False):
    """Type-safe toolbar item configuration from JSON."""

    type: str
    action_id: str
    menu_id: str
    widget_id: str
    icon: str
    label_key: str


class ToolbarDefinition(TypedDict, total=False):
    """Type-safe toolbar configuration from JSON."""

    id: str
    title_key: str
    area: str
    movable: bool
    floatable: bool
    icon_size: int
    button_style: str
    items: list[ToolbarItemDefinition]


@dataclass
class ToolbarItemConfig:
    """Parsed toolbar item configuration."""

    type: str = "action"
    action_id: str = ""
    menu_id: str = ""
    widget_id: str = ""
    icon: str = ""
    label_key: str = ""


@dataclass
class ToolbarConfig:
    """Parsed toolbar configuration."""

    id: str
    title_key: str
    area: str = "top"
    movable: bool = True
    floatable: bool = False
    icon_size: int = 24
    button_style: str = "icon_only"
    items: list[ToolbarItemConfig] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate toolbar configuration."""
        valid_areas = {"top", "bottom", "left", "right"}
        if self.area not in valid_areas:
            raise ValueError(f"Invalid area '{self.area}'. Must be one of {valid_areas}")

        valid_styles = {"icon_only", "text_only", "text_beside_icon", "text_under_icon"}
        if self.button_style not in valid_styles:
            self.button_style = "icon_only"


# Map area strings to Qt ToolBarArea
TOOLBAR_AREAS = {
    "top": Qt.ToolBarArea.TopToolBarArea,
    "bottom": Qt.ToolBarArea.BottomToolBarArea,
    "left": Qt.ToolBarArea.LeftToolBarArea,
    "right": Qt.ToolBarArea.RightToolBarArea,
}

# Map button style strings to Qt ToolButtonStyle
BUTTON_STYLES = {
    "icon_only": Qt.ToolButtonStyle.ToolButtonIconOnly,
    "text_only": Qt.ToolButtonStyle.ToolButtonTextOnly,
    "text_beside_icon": Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
    "text_under_icon": Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
}

# Icon fallbacks for menu buttons
MENU_ICON_FALLBACKS = {
    "layouts_menu": "▤",
    "themes_menu": "✦",
    "grid": "▤",
    "palette": "✦",
}


class ToolbarFactory:
    """Factory for creating toolbars from JSON configuration."""

    def __init__(
        self,
        config_path: str | Path = "config",
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize ToolbarFactory.

        Args:
            config_path: Path to configuration directory
            i18n_factory: Optional I18nFactory for translating toolbar labels
        """
        self.config_path = Path(config_path)
        self.toolbar_file = self.config_path / "toolbar.json"
        self._toolbars_cache: dict[str, ToolbarConfig] | None = None
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        self._menu_creators: dict[str, Any] = {}

    def set_i18n_factory(self, i18n_factory: "I18nFactory") -> None:
        """Set or update the I18nFactory instance.

        Args:
            i18n_factory: I18nFactory instance for translating strings
        """
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()

    def register_menu_creator(
        self,
        menu_id: str,
        creator: Any,
    ) -> None:
        """Register a menu creator function for a menu_id.

        Args:
            menu_id: The menu ID from toolbar.json
            creator: Callable that returns a QMenu or populates one
        """
        self._menu_creators[menu_id] = creator

    def _translate(self, key: str, default: str | None = None) -> str:
        """Translate a key using i18n_factory if available."""
        if not self._i18n_factory or not key:
            return default or key

        if key in self._translated_cache:
            return self._translated_cache[key]

        translated = self._i18n_factory.translate(key, default=key)
        self._translated_cache[key] = translated
        return translated

    def load_toolbars(self) -> list[ToolbarConfig]:
        """Load and parse all toolbars from config.

        Returns:
            List of ToolbarConfig instances
        """
        if not self.toolbar_file.exists():
            logger.warning("Toolbar config file not found: %s", self.toolbar_file)
            return []

        with open(self.toolbar_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Toolbar configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        toolbars_list_raw: Any = raw_data.get("toolbars", [])
        if not isinstance(toolbars_list_raw, list):
            raise ValueError("'toolbars' must be an array")
        toolbars_list: list[Any] = toolbars_list_raw

        toolbars: list[ToolbarConfig] = []
        self._toolbars_cache = {}

        for item in toolbars_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            try:
                toolbar = self._parse_toolbar(item_dict)
                toolbars.append(toolbar)
                self._toolbars_cache[toolbar.id] = toolbar
            except ValueError as e:
                logger.warning("Skipping invalid toolbar: %s", e)

        logger.info("Loaded %d toolbars from %s", len(toolbars), self.toolbar_file)
        return toolbars

    @staticmethod
    def _parse_toolbar(item_dict: dict[str, Any]) -> ToolbarConfig:
        """Parse and validate a single toolbar from dict."""
        toolbar_id: Any = item_dict.get("id")
        if not isinstance(toolbar_id, str) or not toolbar_id:
            raise ValueError("Toolbar 'id' must be a non-empty string")

        title_key: Any = item_dict.get("title_key", "")
        if not isinstance(title_key, str):
            title_key = ""

        area: Any = item_dict.get("area", "top")
        if not isinstance(area, str):
            area = "top"

        movable: Any = item_dict.get("movable", True)
        floatable: Any = item_dict.get("floatable", False)

        icon_size: Any = item_dict.get("icon_size", 24)
        if not isinstance(icon_size, int):
            icon_size = 24

        button_style: Any = item_dict.get("button_style", "icon_only")
        if not isinstance(button_style, str):
            button_style = "icon_only"

        # Parse items
        items: list[ToolbarItemConfig] = []
        items_raw: Any = item_dict.get("items", [])
        if isinstance(items_raw, list):
            for item in items_raw:
                if isinstance(item, dict):
                    items.append(ToolbarFactory._parse_toolbar_item(item))

        return ToolbarConfig(
            id=toolbar_id,
            title_key=title_key,
            area=area,
            movable=bool(movable),
            floatable=bool(floatable),
            icon_size=icon_size,
            button_style=button_style,
            items=items,
        )

    @staticmethod
    def _parse_toolbar_item(item_dict: dict[str, Any]) -> ToolbarItemConfig:
        """Parse a single toolbar item."""
        item_type: Any = item_dict.get("type", "action")
        if not isinstance(item_type, str):
            item_type = "action"

        action_id: Any = item_dict.get("action_id", "")
        if not isinstance(action_id, str):
            action_id = ""

        menu_id: Any = item_dict.get("menu_id", "")
        if not isinstance(menu_id, str):
            menu_id = ""

        widget_id: Any = item_dict.get("widget_id", "")
        if not isinstance(widget_id, str):
            widget_id = ""

        icon: Any = item_dict.get("icon", "")
        if not isinstance(icon, str):
            icon = ""

        label_key: Any = item_dict.get("label_key", "")
        if not isinstance(label_key, str):
            label_key = ""

        return ToolbarItemConfig(
            type=item_type,
            action_id=action_id,
            menu_id=menu_id,
            widget_id=widget_id,
            icon=icon,
            label_key=label_key,
        )

    def get_toolbar_config(self, toolbar_id: str) -> ToolbarConfig | None:
        """Get a specific toolbar configuration by ID."""
        if self._toolbars_cache is None:
            self.load_toolbars()

        return self._toolbars_cache.get(toolbar_id) if self._toolbars_cache else None

    def create_toolbar(
        self,
        config: ToolbarConfig,
        action_registry: "ActionRegistry",
        parent: "QWidget",
    ) -> QToolBar:
        """Create a QToolBar from configuration.

        Args:
            config: ToolbarConfig instance
            action_registry: ActionRegistry for getting QActions
            parent: Parent widget

        Returns:
            Configured QToolBar
        """
        # Create toolbar with translated title
        title = self._translate(config.title_key, config.id)
        toolbar = QToolBar(title, parent)
        toolbar.setObjectName(config.id)

        # Configure toolbar
        toolbar.setMovable(config.movable)
        toolbar.setFloatable(config.floatable)

        # Set icon size
        from PySide6.QtCore import QSize
        toolbar.setIconSize(QSize(config.icon_size, config.icon_size))

        # Set button style
        if config.button_style in BUTTON_STYLES:
            toolbar.setToolButtonStyle(BUTTON_STYLES[config.button_style])

        # Apply minimal styling
        toolbar.setStyleSheet("""
            QToolBar {
                margin: 0px;
                padding: 0px;
                spacing: 2px;
            }
        """)

        # Add items
        for item in config.items:
            self._add_toolbar_item(toolbar, item, action_registry, parent)

        logger.info("Created toolbar '%s' with %d items", config.id, len(config.items))
        return toolbar

    def _add_toolbar_item(
        self,
        toolbar: QToolBar,
        item: ToolbarItemConfig,
        action_registry: "ActionRegistry",
        parent: "QWidget",
    ) -> None:
        """Add a single item to the toolbar."""
        if item.type == "separator":
            toolbar.addSeparator()

        elif item.type == "spacer":
            from PySide6.QtWidgets import QWidget as SpacerWidget
            spacer = SpacerWidget()
            spacer.setSizePolicy(
                spacer.sizePolicy().horizontalPolicy(),
                spacer.sizePolicy().verticalPolicy(),
            )
            from PySide6.QtWidgets import QSizePolicy
            spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            toolbar.addWidget(spacer)

        elif item.type == "action":
            action = action_registry.get_action(item.action_id)
            if action:
                # If no icon, use fallback text
                if action.icon().isNull():
                    fallback = action_registry.get_icon_fallback(
                        self._get_action_icon_name(action_registry, item.action_id)
                    )
                    if fallback:
                        action.setText(fallback)
                toolbar.addAction(action)
            else:
                logger.warning("Action not found for toolbar: %s", item.action_id)

        elif item.type == "menu":
            button = QToolButton(parent)

            # Set icon/text
            icon_fallback = MENU_ICON_FALLBACKS.get(
                item.menu_id, MENU_ICON_FALLBACKS.get(item.icon, "☰")
            )
            button.setText(icon_fallback)

            # Set tooltip
            if item.label_key:
                tooltip = self._translate(item.label_key, item.menu_id)
                button.setToolTip(tooltip)

            # Create or get menu
            menu = self._get_or_create_menu(item.menu_id, parent)
            button.setMenu(menu)
            button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

            toolbar.addWidget(button)

    def _get_action_icon_name(
        self, action_registry: "ActionRegistry", action_id: str
    ) -> str:
        """Get the icon name for an action."""
        if action_registry._action_factory:
            config = action_registry._action_factory.get_action_config(action_id)
            if config:
                return config.icon
        return ""

    def _get_or_create_menu(self, menu_id: str, parent: "QWidget") -> QMenu:
        """Get or create a menu for a menu_id.

        Args:
            menu_id: The menu ID
            parent: Parent widget

        Returns:
            QMenu instance
        """
        # Check if we have a creator registered
        if menu_id in self._menu_creators:
            creator = self._menu_creators[menu_id]
            if callable(creator):
                result = creator()
                if isinstance(result, QMenu):
                    return result

        # Create empty menu as placeholder
        menu = QMenu(menu_id, parent)
        menu.setObjectName(menu_id)
        return menu

    def create_all_toolbars(
        self,
        action_registry: "ActionRegistry",
        parent: "QMainWindow",
    ) -> list[QToolBar]:
        """Create all configured toolbars and add them to the main window.

        Args:
            action_registry: ActionRegistry for getting QActions
            parent: QMainWindow to add toolbars to

        Returns:
            List of created QToolBar instances
        """
        configs = self.load_toolbars()
        toolbars: list[QToolBar] = []

        for config in configs:
            toolbar = self.create_toolbar(config, action_registry, parent)

            # Add to main window in correct area
            area = TOOLBAR_AREAS.get(config.area, Qt.ToolBarArea.TopToolBarArea)
            parent.addToolBar(area, toolbar)

            toolbars.append(toolbar)

        return toolbars
