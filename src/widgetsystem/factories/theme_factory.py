"""Theme factory for managing theme definitions and loading theme configurations."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
import json

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


@dataclass
class TabColors:
    """Complete tab color configuration for unified Dock/QTabBar styling.

    All colors are stored as hex strings (#RRGGBB or #AARRGGBB).
    Gradients are stored as lists [top, upper, lower, bottom].
    Borders are stored as lists [top, left, right].
    """

    # Tab bar background gradient [top, bottom]
    bar_bg: list[str] = field(default_factory=lambda: ["#1E1F21", "#252628"])
    bar_border: str = "#151617"

    # Tab gradients [top, upper, lower, bottom]
    inactive_gradient: list[str] = field(
        default_factory=lambda: ["#4E5155", "#45484C", "#36393D", "#2E3134"]
    )
    active_gradient: list[str] = field(
        default_factory=lambda: ["#5C6066", "#52565B", "#42464A", "#3A3D41"]
    )
    hover_gradient: list[str] = field(
        default_factory=lambda: ["#5A5E63", "#505458", "#404448", "#38393D"]
    )

    # Tab borders [top, left, right] for 3D effect
    inactive_borders: list[str] = field(
        default_factory=lambda: ["#5A5D62", "#4A4D52", "#28292C"]
    )
    active_borders: list[str] = field(
        default_factory=lambda: ["#707580", "#5C6065", "#35383C"]
    )
    hover_borders: list[str] = field(
        default_factory=lambda: ["#686D73", "#555A5F", "#303235"]
    )

    # Text colors
    inactive_text: str = "#A8A8A8"
    active_text: str = "#FFFFFF"
    hover_text: str = "#E0E0E0"

    # Accent border (bottom of active tab)
    accent_border: str = "#5294D6"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TabColors":
        """Create TabColors from dictionary (e.g., from JSON)."""
        defaults = cls()
        return cls(
            bar_bg=data.get("bar_bg", defaults.bar_bg),
            bar_border=data.get("bar_border", defaults.bar_border),
            inactive_gradient=data.get("inactive_gradient", defaults.inactive_gradient),
            active_gradient=data.get("active_gradient", defaults.active_gradient),
            hover_gradient=data.get("hover_gradient", defaults.hover_gradient),
            inactive_borders=data.get("inactive_borders", defaults.inactive_borders),
            active_borders=data.get("active_borders", defaults.active_borders),
            hover_borders=data.get("hover_borders", defaults.hover_borders),
            inactive_text=data.get("inactive_text", defaults.inactive_text),
            active_text=data.get("active_text", defaults.active_text),
            hover_text=data.get("hover_text", defaults.hover_text),
            accent_border=data.get("accent_border", defaults.accent_border),
        )


@dataclass
class ThemeDefinition:
    """Represents a theme definition.

    Attributes:
        theme_id: Unique identifier for the theme
        name: Display name for the theme
        name_key: i18n key for the theme name (optional)
        file_path: Path to the theme stylesheet file
        tab_colors: Complete tab color configuration
        tab_active_color: Legacy - color for active tabs (hex format)
        tab_inactive_color: Legacy - color for inactive tabs (hex format)
    """

    theme_id: str
    name: str
    file_path: Path
    name_key: str = ""
    tab_colors: TabColors = field(default_factory=TabColors)
    # Legacy fields for backwards compatibility
    tab_active_color: str = "#E0E0E0"
    tab_inactive_color: str = "#BDBDBD"


class SimpleThemeProfile:
    """Simple theme profile for basic theme configuration.

    A lightweight profile containing theme ID and name.
    For full ARGB color support, use widgetsystem.core.ThemeProfile instead.
    """

    def __init__(self, profile_id: str, name: str) -> None:
        """Initialize simple theme profile.

        Args:
            profile_id: Unique identifier for the profile
            name: Display name for the profile
        """
        self.profile_id = profile_id
        self.name = name

    @staticmethod
    def load_from_file(file_path: Path) -> "SimpleThemeProfile":
        """Load a simple theme profile from a JSON file.

        Args:
            file_path: Path to the profile JSON file

        Returns:
            SimpleThemeProfile instance

        Raises:
            json.JSONDecodeError: If file contains invalid JSON
            OSError: If file cannot be read
        """
        data = json.loads(file_path.read_text(encoding="utf-8"))
        profile = SimpleThemeProfile(data.get("id", ""), data.get("name", ""))
        return profile

    def save_to_file(self, file_path: Path) -> None:
        """Save simple theme profile to a JSON file.

        Args:
            file_path: Path where the profile should be saved
        """
        data = {"id": self.profile_id, "name": self.name}
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def generate_qss(self) -> str:
        """Generate QSS stylesheet content from profile.

        Returns:
            QSS stylesheet as a string (empty for simple profiles)
        """
        return ""


# Backwards compatibility alias
ThemeProfile = SimpleThemeProfile


class ThemeFactory:
    """Factory for creating theme-related instances from JSON configuration.

    Loads theme definitions from themes.json and provides methods
    to retrieve specific themes, stylesheets, and color configurations.
    """

    def __init__(self, config_path: Path | str, i18n_factory: "I18nFactory | None" = None) -> None:
        """Initialize factory with configuration directory.

        Args:
            config_path: Path to the config directory containing themes.json
            i18n_factory: Optional I18nFactory instance for translations
        """
        self.config_path = Path(config_path)
        self.themes_file = self.config_path / "themes.json"
        self._cache: dict[str, Any] = {}
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

    def get_theme_name(self, theme: ThemeDefinition) -> str:
        """Get translated name for a theme.

        Args:
            theme: ThemeDefinition instance

        Returns:
            Translated theme name
        """
        if theme.name_key:
            return self._translate(theme.name_key, theme.name)
        return theme.name

    def load_themes(self) -> list[dict[str, Any]]:
        """Load all themes from configuration file.

        Returns:
            List of theme definitions as dictionaries

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If configuration is invalid JSON
        """
        if not self.themes_file.exists():
            return []

        try:
            config_data = json.loads(self.themes_file.read_text(encoding="utf-8"))
            if not isinstance(config_data, dict):
                return []
            themes = config_data.get("themes", [])
            if not isinstance(themes, list):
                return []
            return themes
        except (json.JSONDecodeError, OSError):
            return []

    def list_themes(self) -> list[ThemeDefinition]:
        """List all available themes from the configuration file.

        Returns:
            List of ThemeDefinition objects
        """
        themes_data = self.load_themes()
        themes = []

        for theme in themes_data:
            if not isinstance(theme, dict):
                continue

            # Check for required fields
            theme_id = theme.get("id")
            name = theme.get("name")
            name_key = theme.get("name_key", "")

            # Support both "file" and "stylesheet" keys
            file_path = theme.get("file") or theme.get("stylesheet")

            if not (theme_id and name and file_path):
                continue

            # Resolve file path relative to config_path
            resolved_path = (self.config_path / file_path).resolve()

            # Get tab colors with defaults
            tab_colors_data = theme.get("tab_colors", {})
            if not isinstance(tab_colors_data, dict):
                tab_colors_data = {}

            # Parse into TabColors dataclass
            tab_colors = TabColors.from_dict(tab_colors_data)

            # Legacy fields for backwards compatibility
            tab_active = tab_colors_data.get("active_text", tab_colors.active_text)
            tab_inactive = tab_colors_data.get("inactive_text", tab_colors.inactive_text)

            themes.append(
                ThemeDefinition(
                    theme_id=theme_id,
                    name=name,
                    name_key=str(name_key),
                    file_path=resolved_path,
                    tab_colors=tab_colors,
                    tab_active_color=tab_active,
                    tab_inactive_color=tab_inactive,
                )
            )

        return themes

    def get_default_theme_id(self) -> str | None:
        """Get the default theme ID from the configuration.

        Returns:
            Default theme ID or None if not configured
        """
        if not self.themes_file.exists():
            return None

        try:
            config_data = json.loads(self.themes_file.read_text(encoding="utf-8"))
            if not isinstance(config_data, dict):
                return None
            return config_data.get("default_theme")
        except (json.JSONDecodeError, OSError):
            return None

    def get_default_theme(self) -> ThemeDefinition | None:
        """Get the default theme definition.

        Returns:
            ThemeDefinition for the default theme, or None if not found
        """
        default_id = self.get_default_theme_id()
        if not default_id:
            return None

        themes = self.list_themes()
        for theme in themes:
            if theme.theme_id == default_id:
                return theme

        return None

    def get_default_stylesheet(self) -> str:
        """Get the stylesheet content of the default theme.

        Returns:
            Stylesheet content as a string, or empty string if not found
        """
        theme = self.get_default_theme()
        if not theme:
            return ""

        try:
            if theme.file_path.exists():
                return theme.file_path.read_text(encoding="utf-8")
        except OSError:
            pass

        return ""

    def get_tab_colors(self) -> tuple[str, str]:
        """Get tab colors from the default theme (legacy).

        Returns:
            Tuple of (active_color, inactive_color)
        """
        theme = self.get_default_theme()
        if theme:
            return (theme.tab_active_color, theme.tab_inactive_color)
        return ("#E0E0E0", "#BDBDBD")

    def get_full_tab_colors(self) -> TabColors:
        """Get complete tab color configuration from the default theme.

        Returns:
            TabColors instance with all tab styling colors
        """
        theme = self.get_default_theme()
        if theme:
            return theme.tab_colors
        return TabColors()

    def apply_tab_colors_to_theme_colors(self, theme_colors: Any) -> None:
        """Apply TabColors from config to a ThemeColors instance.

        This synchronizes the JSON-based tab colors with the ThemeProfile's
        ThemeColors dataclass for unified styling.

        Args:
            theme_colors: ThemeColors instance from theme_profile.py
        """
        tab = self.get_full_tab_colors()

        # Map TabColors to ThemeColors attributes
        if len(tab.bar_bg) >= 2:
            theme_colors.tab_bar_bg_top = tab.bar_bg[0]
            theme_colors.tab_bar_bg_bottom = tab.bar_bg[1]
        theme_colors.tab_bar_border = tab.bar_border

        # Inactive gradient
        if len(tab.inactive_gradient) >= 4:
            theme_colors.tab_gradient_top = tab.inactive_gradient[0]
            theme_colors.tab_gradient_upper = tab.inactive_gradient[1]
            theme_colors.tab_gradient_lower = tab.inactive_gradient[2]
            theme_colors.tab_gradient_bottom = tab.inactive_gradient[3]

        # Active gradient
        if len(tab.active_gradient) >= 4:
            theme_colors.tab_active_gradient_top = tab.active_gradient[0]
            theme_colors.tab_active_gradient_upper = tab.active_gradient[1]
            theme_colors.tab_active_gradient_lower = tab.active_gradient[2]
            theme_colors.tab_active_gradient_bottom = tab.active_gradient[3]

        # Hover gradient
        if len(tab.hover_gradient) >= 4:
            theme_colors.tab_hover_gradient_top = tab.hover_gradient[0]
            theme_colors.tab_hover_gradient_upper = tab.hover_gradient[1]
            theme_colors.tab_hover_gradient_lower = tab.hover_gradient[2]
            theme_colors.tab_hover_gradient_bottom = tab.hover_gradient[3]

        # Borders (3D effect)
        if len(tab.inactive_borders) >= 3:
            theme_colors.tab_border_highlight = tab.inactive_borders[0]
            theme_colors.tab_border_left = tab.inactive_borders[1]
            theme_colors.tab_border_shadow = tab.inactive_borders[2]

        if len(tab.active_borders) >= 3:
            theme_colors.tab_active_border_highlight = tab.active_borders[0]
            theme_colors.tab_active_border_left = tab.active_borders[1]
            theme_colors.tab_active_border_shadow = tab.active_borders[2]

        if len(tab.hover_borders) >= 3:
            theme_colors.tab_hover_border_highlight = tab.hover_borders[0]
            theme_colors.tab_hover_border_left = tab.hover_borders[1]
            theme_colors.tab_hover_border_shadow = tab.hover_borders[2]

        # Text colors
        theme_colors.tab_inactive_text = tab.inactive_text
        theme_colors.tab_active_text = tab.active_text
        theme_colors.tab_hover_text = tab.hover_text
        theme_colors.tab_active_border = tab.accent_border

    def list_profiles(self) -> list[str]:
        """List all available profile IDs.

        Returns:
            List of profile IDs
        """
        profiles_dir = self.config_path / "profiles"
        if not profiles_dir.exists():
            return []

        profile_ids = []
        for profile_file in profiles_dir.glob("*.json"):
            profile_ids.append(profile_file.stem)

        return profile_ids

    def load_profile(self, profile_id: str) -> ThemeProfile | None:
        """Load a theme profile by ID.

        Args:
            profile_id: The profile ID to load

        Returns:
            ThemeProfile instance or None if not found
        """
        profile_file = self.config_path / "profiles" / f"{profile_id}.json"
        if not profile_file.exists():
            return None

        try:
            return ThemeProfile.load_from_file(profile_file)
        except json.JSONDecodeError:
            return None

    def save_profile(self, profile: ThemeProfile, profile_id: str) -> bool:
        """Save a theme profile.

        Args:
            profile: ThemeProfile instance to save
            profile_id: ID for the profile

        Returns:
            True if successful, False otherwise
        """
        profiles_dir = self.config_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)

        profile_file = profiles_dir / f"{profile_id}.json"
        try:
            profile.save_to_file(profile_file)
            return True
        except OSError:
            return False

    def create_default_profiles(self) -> None:
        """Create default theme profiles if they do not exist.

        Ensures the profiles directory exists and is ready
        for storing theme profile configurations.
        """
        profiles_dir = self.config_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)