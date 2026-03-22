"""ShortcutController - Keyboard shortcuts and action management.

This controller manages QShortcut and QAction registration,
preventing duplicates and providing a centralized API.
"""

from typing import Any, Callable

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from widgetsystem.enums import ActionName


class ShortcutController(QObject):
    """Controller for keyboard shortcuts and actions.

    Manages shortcut and action registration with duplicate prevention.

    Signals:
        actionRegistered: Emitted when an action is registered (action_name)
        shortcutRegistered: Emitted when a shortcut is registered (key_sequence)
    """

    actionRegistered = Signal(str)  # action_name
    shortcutRegistered = Signal(str)  # key_sequence

    def __init__(
        self,
        menu_factory: Any,
        i18n_factory: Any,
        parent: QWidget,
    ) -> None:
        """Initialize ShortcutController.

        Args:
            menu_factory: MenuFactory for menu configurations
            i18n_factory: I18nFactory for translations
            parent: Parent widget (typically MainWindow)
        """
        super().__init__(parent)

        self._menu_factory = menu_factory
        self._i18n_factory = i18n_factory
        self._parent = parent

        # Registries
        self._actions: dict[str, QAction] = {}
        self._shortcuts: list[QShortcut] = []
        self._registered_action_names: set[str] = set()
        self._registered_shortcuts: set[str] = set()

        # Action handlers
        self._handlers: dict[str, Callable[[], None]] = {}

    @property
    def actions(self) -> dict[str, QAction]:
        """Get registered actions (read-only copy)."""
        return dict(self._actions)

    @property
    def shortcuts(self) -> list[QShortcut]:
        """Get registered shortcuts (read-only copy)."""
        return list(self._shortcuts)

    @property
    def registered_action_names(self) -> set[str]:
        """Get set of registered action names."""
        return set(self._registered_action_names)

    @property
    def registered_shortcuts(self) -> set[str]:
        """Get set of registered shortcut keys."""
        return set(self._registered_shortcuts)

    def register_handler(
        self,
        action_name: str | ActionName,
        handler: Callable[[], None],
    ) -> None:
        """Register a handler for an action name.

        Args:
            action_name: Action identifier
            handler: Handler function
        """
        if isinstance(action_name, ActionName):
            action_name = action_name.value
        self._handlers[action_name] = handler

    def register_handlers(
        self,
        handlers: dict[str | ActionName, Callable[[], None]],
    ) -> None:
        """Register multiple handlers at once.

        Args:
            handlers: Mapping of action names to handlers
        """
        for name, handler in handlers.items():
            self.register_handler(name, handler)

    def get_handler(self, action_name: str | ActionName) -> Callable[[], None] | None:
        """Get handler for an action name.

        Args:
            action_name: Action identifier

        Returns:
            Handler function or None
        """
        if isinstance(action_name, ActionName):
            action_name = action_name.value
        return self._handlers.get(action_name)

    def create_global_shortcuts(
        self,
        shortcut_map: dict[str, Callable[[], None]],
    ) -> None:
        """Create application-wide global shortcuts.

        Args:
            shortcut_map: Mapping of key sequences to handlers
        """
        for key_sequence, handler in shortcut_map.items():
            if key_sequence.lower() in self._registered_shortcuts:
                continue

            shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(handler)
            self._shortcuts.append(shortcut)
            self._registered_shortcuts.add(key_sequence.lower())
            self.shortcutRegistered.emit(key_sequence)

    def create_action(
        self,
        action_id: str,
        label: str,
        handler: Callable[[], None],
        shortcut: str | None = None,
    ) -> QAction:
        """Create and register an action.

        Args:
            action_id: Unique action identifier
            label: Display label
            handler: Handler function
            shortcut: Optional keyboard shortcut

        Returns:
            Created QAction
        """
        if action_id in self._actions:
            return self._actions[action_id]

        action = QAction(label, self._parent)

        if shortcut:
            shortcut_key = shortcut.lower()
            if shortcut_key not in self._registered_shortcuts:
                action.setShortcut(shortcut)
                self._registered_shortcuts.add(shortcut_key)

        action.triggered.connect(handler)
        self._parent.addAction(action)

        self._actions[action_id] = action
        self._registered_action_names.add(action_id)
        self.actionRegistered.emit(action_id)

        return action

    def register_menu_actions(self) -> None:
        """Register menu item actions from MenuFactory."""
        try:
            menus = self._menu_factory.load_menus()
            for menu_item in menus:
                self._register_menu_item(menu_item)
        except Exception as e:
            print(f"Warning: Failed to load menus from factory: {e}")

    def _register_menu_item(self, menu_item: Any) -> None:
        """Register a single menu item and its children."""
        if (
            menu_item.type == "action"
            and menu_item.action
            and menu_item.id not in self._actions
        ):
            handler = self.get_handler(menu_item.action)
            if handler:
                label = self._i18n_factory.translate(
                    menu_item.label_key, default=menu_item.id
                )
                shortcut = menu_item.shortcut.strip() if menu_item.shortcut else None

                # Skip layout action shortcuts (handled separately)
                layout_actions = {
                    ActionName.SAVE_LAYOUT.value,
                    ActionName.LOAD_LAYOUT.value,
                    ActionName.RESET_LAYOUT.value,
                }
                if menu_item.action in layout_actions:
                    shortcut = None

                self.create_action(menu_item.id, label, handler, shortcut)
                self._registered_action_names.add(menu_item.action)

        for child in menu_item.children:
            self._register_menu_item(child)

    def register_default_layout_actions(
        self,
        save_handler: Callable[[], None],
        load_handler: Callable[[], None],
        reset_handler: Callable[[], None],
    ) -> None:
        """Register default layout actions if not already registered.

        Args:
            save_handler: Handler for save layout
            load_handler: Handler for load layout
            reset_handler: Handler for reset layout
        """
        if ActionName.SAVE_LAYOUT.value not in self._registered_action_names:
            self.create_action(
                "save_layout",
                self._i18n_factory.translate("menu.file.save", default="Save Layout"),
                save_handler,
            )

        if ActionName.LOAD_LAYOUT.value not in self._registered_action_names:
            self.create_action(
                "load_layout",
                self._i18n_factory.translate("menu.file.load", default="Load Layout"),
                load_handler,
            )

        if ActionName.RESET_LAYOUT.value not in self._registered_action_names:
            self.create_action(
                "reset_layout",
                self._i18n_factory.translate("menu.file.reset", default="Reset Layout"),
                reset_handler,
            )

    def reset(self) -> None:
        """Reset shortcut controller state."""
        # Clear shortcuts
        for shortcut in self._shortcuts:
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self._shortcuts.clear()

        # Clear actions
        for action in self._actions.values():
            action.deleteLater()
        self._actions.clear()

        # Clear registries
        self._registered_action_names.clear()
        self._registered_shortcuts.clear()
