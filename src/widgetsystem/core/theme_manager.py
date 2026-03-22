"""Theme Manager - central theme registry with signal-based updates."""

from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QPalette


class Theme:
    """Theme definition with palette, stylesheet, icons, and properties."""

    def __init__(self, theme_id: str, name: str) -> None:
        """Initialize theme.

        Args:
            theme_id: Unique theme identifier
            name: Display name for theme
        """
        self.theme_id = theme_id
        self.name = name
        self.stylesheet: str = ""
        self.palette: QPalette | None = None
        self.has_custom_palette: bool = False
        self.icons: dict[str, QIcon] = {}
        self.properties: dict[str, Any] = {}

    def set_stylesheet(self, stylesheet: str) -> None:
        """Set theme stylesheet.

        Args:
            stylesheet: QSS stylesheet content
        """
        self.stylesheet = stylesheet

    def set_palette(self, palette: QPalette) -> None:
        """Set custom palette for theme.

        Args:
            palette: Qt palette to use
        """
        self.palette = palette
        self.has_custom_palette = True

    def set_icon(self, icon_id: str, icon: QIcon) -> None:
        """Register an icon for this theme.

        Args:
            icon_id: Icon identifier
            icon: QIcon instance
        """
        self.icons[icon_id] = icon

    def get_icon(self, icon_id: str) -> QIcon:
        """Get icon by ID, returns empty icon if not found.

        Args:
            icon_id: Icon identifier

        Returns:
            Icon instance or empty icon
        """
        return self.icons.get(icon_id, QIcon())

    def set_property(self, name: str, value: Any) -> None:
        """Set custom theme property.

        Args:
            name: Property name
            value: Property value
        """
        self.properties[name] = value

    def get_property(self, name: str, default: Any = None) -> Any:
        """Get theme property by name.

        Args:
            name: Property name
            default: Default value if property not found

        Returns:
            Property value or default
        """
        return self.properties.get(name, default)


class ThemeManager(QObject):
    """Singleton theme manager with signal-based updates."""

    themeChanged = Signal(object)  # Emits Theme instance

    _instance: "ThemeManager | None" = None

    def __init__(self) -> None:
        """Initialize theme manager (use instance() instead)."""
        super().__init__()
        self.themes: dict[str, Theme] = {}
        self.current_theme_id: str = ""

    @classmethod
    def instance(cls) -> "ThemeManager":
        """Get singleton instance.

        Returns:
            ThemeManager singleton instance
        """
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def register_theme(self, theme: Theme) -> None:
        """Register a theme in the manager.

        Args:
            theme: Theme instance to register
        """
        self.themes[theme.theme_id] = theme

    def current_theme(self) -> Theme | None:
        """Get currently active theme.

        Returns:
            Current theme or None if not set
        """
        return self.themes.get(self.current_theme_id)

    def get_theme(self, theme_id: str) -> Theme | None:
        """Get theme by ID.

        Args:
            theme_id: Theme identifier

        Returns:
            Theme instance or None if not found
        """
        return self.themes.get(theme_id)

    def set_current_theme(self, theme_id: str) -> bool:
        """Set active theme and emit signal.

        Args:
            theme_id: Theme identifier to activate

        Returns:
            True if theme was set, False if not found
        """
        if theme_id not in self.themes:
            return False

        self.current_theme_id = theme_id
        theme = self.themes[theme_id]
        self.themeChanged.emit(theme)
        return True

    def theme_names(self) -> list[str]:
        """Get list of all registered theme IDs.

        Returns:
            List of theme identifiers
        """
        return list(self.themes.keys())

    def clear(self) -> None:
        """Clear all registered themes."""
        self.themes.clear()
        self.current_theme_id = ""
