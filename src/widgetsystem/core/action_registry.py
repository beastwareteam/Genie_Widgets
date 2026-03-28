"""Action Registry - Singleton that creates and caches QAction instances."""

from __future__ import annotations

import logging
import warnings
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QApplication, QStyle

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget

    from widgetsystem.factories.action_factory import ActionConfig, ActionFactory

logger = logging.getLogger(__name__)


# Map icon names to Qt standard icons
STANDARD_ICONS: dict[str, QStyle.StandardPixmap] = {
    "save": QStyle.StandardPixmap.SP_DialogSaveButton,
    "folder-open": QStyle.StandardPixmap.SP_DirOpenIcon,
    "refresh": QStyle.StandardPixmap.SP_BrowserReload,
    "sync": QStyle.StandardPixmap.SP_BrowserReload,
    "plus": QStyle.StandardPixmap.SP_FileDialogNewFolder,
    "times": QStyle.StandardPixmap.SP_DialogCloseButton,
    "close": QStyle.StandardPixmap.SP_DialogCloseButton,
    "cog": QStyle.StandardPixmap.SP_ComputerIcon,
    "settings": QStyle.StandardPixmap.SP_ComputerIcon,
    "undo": QStyle.StandardPixmap.SP_ArrowBack,
    "redo": QStyle.StandardPixmap.SP_ArrowForward,
    "window-restore": QStyle.StandardPixmap.SP_TitleBarNormalButton,
    "window-maximize": QStyle.StandardPixmap.SP_TitleBarMaxButton,
    "help": QStyle.StandardPixmap.SP_DialogHelpButton,
    "info": QStyle.StandardPixmap.SP_MessageBoxInformation,
    "warning": QStyle.StandardPixmap.SP_MessageBoxWarning,
    "error": QStyle.StandardPixmap.SP_MessageBoxCritical,
    "question": QStyle.StandardPixmap.SP_MessageBoxQuestion,
}

# Map icon names to Unicode/emoji fallbacks
ICON_FALLBACKS: dict[str, str] = {
    "save": "💾",
    "folder-open": "📂",
    "refresh": "🔄",
    "sync": "🔄",
    "plus": "+",
    "times": "✕",
    "close": "✕",
    "cog": "⚙",
    "settings": "⚙",
    "undo": "↶",
    "redo": "↷",
    "window-restore": "❐",
    "window-maximize": "▣",
    "palette": "🎨",
    "eyedropper": "🌈",
    "wrench": "🔧",
    "puzzle-piece": "🧩",
}


class ActionRegistry(QObject):
    """Centralized registry for QAction instances.

    Singleton that ensures the same QAction is used across menus and toolbars,
    keeping icons, shortcuts, and enabled states synchronized.
    """

    _instance: ActionRegistry | None = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize ActionRegistry.

        Use ActionRegistry.instance() to get the singleton instead of
        constructing directly.

        Args:
            parent: Parent widget for QActions
        """
        super().__init__(parent)
        self._actions: dict[str, QAction] = {}
        self._action_factory: ActionFactory | None = None
        self._handlers: dict[str, Callable[[], None]] = {}
        self._parent: QWidget | None = parent
        self._initialized = False

    @classmethod
    def instance(cls) -> ActionRegistry:
        """Get the singleton instance.

        Returns:
            The ActionRegistry singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        if cls._instance is not None:
            cls._instance._actions.clear()
            cls._instance._handlers.clear()
            cls._instance = None

    def initialize(
        self,
        action_factory: ActionFactory,
        parent: QWidget,
        handler_map: dict[str, Callable[[], None]] | None = None,
    ) -> None:
        """Initialize the registry with factory and parent widget.

        Args:
            action_factory: Factory for loading action configs
            parent: Parent widget for QActions (typically MainWindow)
            handler_map: Optional map of action names to handler functions
        """
        self._action_factory = action_factory
        self._parent = parent
        self.setParent(parent)

        if handler_map:
            self._handlers.update(handler_map)

        # Pre-create all actions
        self.create_all_actions()
        self._initialized = True

        logger.info(
            "ActionRegistry initialized with %d actions", len(self._actions)
        )

    def is_initialized(self) -> bool:
        """Check if the registry has been initialized.

        Returns:
            True if initialize() has been called
        """
        return self._initialized

    def register_handler(
        self, action_name: str, handler: Callable[[], None]
    ) -> None:
        """Register a handler for an action name.

        Args:
            action_name: The action name (from ActionConfig.action)
            handler: The callback function to invoke
        """
        self._handlers[action_name] = handler

        # Connect existing action if present
        for action in self._actions.values():
            config = self._get_action_config(action)
            if config and config.action == action_name:
                self._connect_handler(action, handler)

    def _get_action_config(self, action: QAction) -> ActionConfig | None:
        """Get the ActionConfig for a QAction.

        Args:
            action: The QAction

        Returns:
            ActionConfig or None
        """
        if not self._action_factory:
            return None
        action_id = action.data()
        if isinstance(action_id, str):
            return self._action_factory.get_action_config(action_id)
        return None

    def _connect_handler(
        self, action: QAction, handler: Callable[[], None]
    ) -> None:
        """Connect a handler to an action's triggered signal.

        Args:
            action: The QAction
            handler: The handler function
        """
        # Disconnect any existing connections first
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with suppress(RuntimeError):
                action.triggered.disconnect()

        # Connect new handler
        action.triggered.connect(lambda _checked=False: handler())

    def get_action(self, action_id: str) -> QAction | None:
        """Get or create a QAction by ID.

        Returns the cached instance, creating it if necessary.

        Args:
            action_id: The action ID from actions.json

        Returns:
            QAction or None if not found
        """
        # Return cached action
        if action_id in self._actions:
            return self._actions[action_id]

        # Create if we have a factory
        if not self._action_factory:
            logger.warning("ActionRegistry not initialized, cannot create action")
            return None

        config = self._action_factory.get_action_config(action_id)
        if not config:
            logger.warning("Action config not found: %s", action_id)
            return None

        return self._create_action(config)

    def _create_action(self, config: ActionConfig) -> QAction:
        """Create a QAction from config.

        Args:
            config: ActionConfig instance

        Returns:
            Configured QAction
        """
        action = QAction(self._parent)
        action.setData(config.id)

        # Set text
        if self._action_factory:
            label = self._action_factory.get_action_label(config)
            action.setText(label)

            tooltip = self._action_factory.get_action_tooltip(config)
            if tooltip:
                action.setToolTip(tooltip)

            status_tip = self._action_factory.get_action_status_tip(config)
            if status_tip:
                action.setStatusTip(status_tip)
        else:
            action.setText(config.label_key)

        # Set shortcut
        if config.shortcut:
            action.setShortcut(QKeySequence(config.shortcut))

        # Set icon
        icon = self._resolve_icon(config.icon)
        if not icon.isNull():
            action.setIcon(icon)

        # Set state
        action.setEnabled(config.enabled)
        action.setCheckable(config.checkable)
        action.setVisible(config.visible)

        # Connect handler if registered
        if config.action in self._handlers:
            self._connect_handler(action, self._handlers[config.action])

        # Cache and return
        self._actions[config.id] = action
        return action

    def _resolve_icon(self, icon_name: str) -> QIcon:
        """Resolve an icon name to a QIcon.

        Resolution order:
        1. Custom theme icons (themes/icons/{name}.svg)
        2. Qt standard icons
        3. Empty icon (text-only)

        Args:
            icon_name: Icon name from config

        Returns:
            QIcon (may be null if no icon found)
        """
        if not icon_name:
            return QIcon()

        # 1. Check custom theme icons
        icon_paths = [
            Path("themes/icons") / f"{icon_name}.svg",
            Path("themes/icons") / f"{icon_name}.png",
            Path("icons") / f"{icon_name}.svg",
            Path("icons") / f"{icon_name}.png",
        ]

        for icon_path in icon_paths:
            if icon_path.exists():
                return QIcon(str(icon_path))

        # 2. Check Qt standard icons
        if icon_name in STANDARD_ICONS:
            style = QApplication.style()
            if style:
                return style.standardIcon(STANDARD_ICONS[icon_name])

        # 3. Return empty icon
        return QIcon()

    def get_icon_fallback(self, icon_name: str) -> str:
        """Get a Unicode/emoji fallback for an icon.

        Use this when icons aren't available and you need text.

        Args:
            icon_name: Icon name from config

        Returns:
            Unicode character or empty string
        """
        return ICON_FALLBACKS.get(icon_name, "")

    def create_all_actions(self) -> None:
        """Pre-create all QActions from factory config."""
        if not self._action_factory:
            logger.warning("ActionRegistry not initialized, cannot create actions")
            return

        actions = self._action_factory.load_actions()
        for config in actions:
            if config.id not in self._actions:
                self._create_action(config)

        logger.info("Created %d actions", len(self._actions))

    def update_translations(self) -> None:
        """Refresh all action texts when language changes."""
        if not self._action_factory:
            return

        # Clear factory translation cache
        self._action_factory._translated_cache.clear()

        # Update each action
        for action_id, action in self._actions.items():
            config = self._action_factory.get_action_config(action_id)
            if config:
                action.setText(self._action_factory.get_action_label(config))
                tooltip = self._action_factory.get_action_tooltip(config)
                if tooltip:
                    action.setToolTip(tooltip)
                status_tip = self._action_factory.get_action_status_tip(config)
                if status_tip:
                    action.setStatusTip(status_tip)

        logger.info("Updated translations for %d actions", len(self._actions))

    def set_action_enabled(self, action_id: str, enabled: bool) -> None:
        """Enable or disable an action across all usages.

        Args:
            action_id: The action ID
            enabled: Whether the action should be enabled
        """
        action = self._actions.get(action_id)
        if action:
            action.setEnabled(enabled)

    def set_action_checked(self, action_id: str, checked: bool) -> None:
        """Set the checked state for a checkable action.

        Args:
            action_id: The action ID
            checked: Whether the action should be checked
        """
        action = self._actions.get(action_id)
        if action and action.isCheckable():
            action.setChecked(checked)

    def get_actions_by_category(self, category: str) -> list[QAction]:
        """Get all actions in a category.

        Args:
            category: Category name

        Returns:
            List of QAction instances
        """
        if not self._action_factory:
            return []

        actions: list[QAction] = []
        configs = self._action_factory.get_actions_by_category(category)

        for config in configs:
            action = self.get_action(config.id)
            if action:
                actions.append(action)

        return actions

    def list_action_ids(self) -> list[str]:
        """Get all registered action IDs.

        Returns:
            List of action IDs
        """
        return list(self._actions.keys())
