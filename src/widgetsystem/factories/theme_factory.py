"""Theme factory for managing theme definitions and loading theme configurations."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

# Import the complete ThemeProfile from core (not duplicated here)
from widgetsystem.core.theme_profile import ThemeProfile


@dataclass
class ThemeDefinition:
    """Represents a theme definition.

    Attributes:
        theme_id: Unique identifier for the theme
        name: Display name for the theme
        file_path: Path to the theme stylesheet file
        tab_active_color: Color for active tabs (hex format)
        tab_inactive_color: Color for inactive tabs (hex format)
    """

    theme_id: str
    name: str
    file_path: Path
    tab_active_color: str = "#E0E0E0"
    tab_inactive_color: str = "#BDBDBD"


class ThemeFactory:
    """Factory for creating theme-related instances from JSON configuration.
    
    Loads theme definitions from themes.json and provides methods
    to retrieve specific themes, stylesheets, and color configurations.
    """

    def __init__(self, config_path: Path | str) -> None:
        """Initialize factory with configuration directory.

        Args:
            config_path: Path to the config directory containing themes.json
        """
        self.config_path = Path(config_path)
        self.themes_file = self.config_path / "themes.json"
        self._cache: dict[str, Any] = {}

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
            
            # Support both "file" and "stylesheet" keys
            file_path = theme.get("file") or theme.get("stylesheet")

            if not (theme_id and name and file_path):
                continue

            # Resolve file path relative to config_path
            resolved_path = (self.config_path / file_path).resolve()

            # Get tab colors with defaults
            tab_colors = theme.get("tab_colors", {})
            if not isinstance(tab_colors, dict):
                tab_colors = {}

            tab_active = tab_colors.get("active", "#E0E0E0")
            tab_inactive = tab_colors.get("inactive", "#BDBDBD")

            themes.append(
                ThemeDefinition(
                    theme_id=theme_id,
                    name=name,
                    file_path=resolved_path,
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
        """Get tab colors from the default theme.

        Returns:
            Tuple of (active_color, inactive_color)
        """
        theme = self.get_default_theme()
        if theme:
            return (theme.tab_active_color, theme.tab_inactive_color)
        return ("#E0E0E0", "#BDBDBD")

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
            return ThemeProfile.load_from_json_file(profile_file)
        except (json.JSONDecodeError, OSError, KeyError):
            return None

    def save_profile(self, profile: ThemeProfile, profile_id: str | None = None) -> bool:
        """Save a theme profile.

        Args:
            profile: ThemeProfile instance to save
            profile_id: Optional ID for the profile (uses profile.name if not provided)

        Returns:
            True if successful, False otherwise
        """
        profiles_dir = self.config_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)

        # Use profile name as ID if not provided
        save_id = profile_id if profile_id else profile.name.lower().replace(" ", "_")
        profile_file = profiles_dir / f"{save_id}.json"
        
        try:
            profile.save_to_json_file(profile_file)
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