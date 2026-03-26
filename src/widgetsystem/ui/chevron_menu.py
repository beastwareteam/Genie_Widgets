"""Chevron Menu - A menu component with visual indicators for nested items."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QWidget

    from widgetsystem.factories.i18n_factory import I18nFactory
    from widgetsystem.factories.menu_factory import MenuItem, MenuFactory

logger = logging.getLogger(__name__)

CHEVRON_OPEN = "▼"
CHEVRON_CLOSED = "▶"


class ChevronMenu(QMenu):
    """A QMenu that displays chevron indicators for submenus."""

    action_triggered = Signal(str)  # Signal(action_id)

    def __init__(
        self,
        title: str = "",
        parent: QWidget | None = None,
        i18n_factory: I18nFactory | None = None,
    ) -> None:
        """Initialize ChevronMenu.

        Args:
            title: Menu title
            parent: Parent widget
            i18n_factory: Optional i18n factory for label translation
        """
        super().__init__(title, parent)
        self._action_callbacks: dict[str, Callable[[str], None]] = {}
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        # Connect to triggered signal with proper type handling
        self.triggered.connect(self._on_action_triggered)

    def set_i18n_factory(self, i18n_factory: I18nFactory | None) -> None:
        """Set or update the i18n factory.

        Args:
            i18n_factory: Optional i18n factory instance
        """
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()

    def _translate(self, key: str, default: str | None = None) -> str:
        """Translate a key using the i18n factory.

        Args:
            key: Translation key
            default: Default value if key not found

        Returns:
            Translated string or default or key
        """
        if not self._i18n_factory or not key:
            return default or key
        if key in self._translated_cache:
            return self._translated_cache[key]
        result = self._i18n_factory.translate(key, default=default or key)
        self._translated_cache[key] = result
        return result

    def add_menu_item(
        self,
        item: MenuItem,
        callback: Callable[[str], None] | None = None,
    ) -> ChevronMenu | None:
        """Add a menu item with proper chevron handling.

        Args:
            item: MenuItem definition
            callback: Optional callback when action is triggered

        Returns:
            ChevronMenu if item has children, None otherwise
        """
        if item.type == "separator":
            self.addSeparator()
            return None

        if item.type == "menu" or (item.type == "action" and item.children):
            # This is a submenu
            label = self._translate(item.label_key, item.label_key)
            submenu = ChevronMenu(
                title=label,
                parent=self,
                i18n_factory=self._i18n_factory,
            )

            # Add children recursively
            for child in item.children:
                submenu.add_menu_item(child, callback)

            # Add submenu with chevron indicator
            menu_action = self.addMenu(submenu)
            if menu_action:
                menu_action.setText(f"{label} {CHEVRON_CLOSED}")
                submenu_prefix = self._translate(
                    "chevron_menu.tooltip.submenu_prefix",
                    "Submenu",
                )
                menu_action.setToolTip(f"{submenu_prefix}: {label}")

            return submenu

        if item.type == "action":
            # Regular action
            label = self._translate(item.label_key, item.label_key)
            action = self.addAction(label)
            action.setData(item.id)

            if item.shortcut:
                action.setShortcut(item.shortcut)

            if callback:
                self._action_callbacks[item.id] = callback
                action.triggered.connect(
                    lambda: self._on_action_triggered_with_callback(item.id, callback)
                )

            return None

        return None

    def _on_action_triggered(self, action: QAction) -> None:
        """Called when an action is triggered.

        Args:
            action: The triggered action
        """
        action_id = action.data()
        if action_id:
            self.action_triggered.emit(action_id)
            logger.debug("Chevron menu action triggered: %s", action_id)

    def _on_action_triggered_with_callback(
        self, action_id: str, callback: Callable[[str], None]
    ) -> None:
        """Call the callback for specific action.

        Args:
            action_id: The action ID
            callback: The callback to invoke
        """
        callback(action_id)


class ChevronMenuBar:
    """Helper class to create a menu bar from MenuFactory data."""

    def __init__(
        self,
        menu_factory: MenuFactory,
        i18n_factory: I18nFactory | None = None,
    ) -> None:
        """Initialize ChevronMenuBar.

        Args:
            menu_factory: MenuFactory instance
            i18n_factory: Optional i18n factory for label translation
        """
        self.menu_factory = menu_factory
        self._i18n_factory = i18n_factory
        self._menus: dict[str, ChevronMenu] = {}
        self._menu_label_keys: dict[str, str] = {}
        self._action_callbacks: dict[str, Callable[[str], None]] = {}

    def set_i18n_factory(self, i18n_factory: I18nFactory | None) -> None:
        """Set or update the i18n factory for all menus.

        Args:
            i18n_factory: Optional i18n factory instance
        """
        self._i18n_factory = i18n_factory
        for menu_id, menu in self._menus.items():
            menu.set_i18n_factory(i18n_factory)
            label_key = self._menu_label_keys.get(menu_id, menu_id)
            if i18n_factory and label_key:
                menu.setTitle(i18n_factory.translate(label_key, default=label_key))

    def create_menu_bar(
        self,
        menus: list[MenuItem] | None = None,
        callback: Callable[[str], None] | None = None,
    ) -> list[ChevronMenu]:
        """Create ChevronMenus from MenuItem definitions.

        Args:
            menus: List of MenuItems (uses factory default if None)
            callback: Global callback for all actions

        Returns:
            List of created ChevronMenu objects
        """
        if menus is None:
            menus = self.menu_factory.load_menus()

        result_menus = []
        for menu_item in menus:
            if menu_item.type != "separator":
                translated_title = (
                    self._i18n_factory.translate(menu_item.label_key, default=menu_item.label_key)
                    if self._i18n_factory and menu_item.label_key
                    else (menu_item.label_key or menu_item.id)
                )
                menu = ChevronMenu(
                    title=translated_title,
                    i18n_factory=self._i18n_factory,
                )

                # Add children
                for child in menu_item.children:
                    menu.add_menu_item(child, callback)

                if callback:
                    menu.action_triggered.connect(callback)

                self._menus[menu_item.id] = menu
                self._menu_label_keys[menu_item.id] = menu_item.label_key
                result_menus.append(menu)

        logger.info("Created %s chevron menus", len(result_menus))
        return result_menus

    def get_menu(self, menu_id: str) -> ChevronMenu | None:
        """Get a menu by ID.

        Args:
            menu_id: The menu ID

        Returns:
            ChevronMenu or None if not found
        """
        return self._menus.get(menu_id)

    def register_action_callback(
        self, action_id: str, callback: Callable[[str], None]
    ) -> None:
        """Register a callback for a specific action.

        Args:
            action_id: The action ID
            callback: The callback function
        """
        self._action_callbacks[action_id] = callback
