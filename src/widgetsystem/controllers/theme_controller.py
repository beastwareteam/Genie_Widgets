"""ThemeController - Unified theme management.

This controller consolidates ThemeFactory and ThemeManager into a
single entry point for all theme-related operations, eliminating
the dual code paths that previously existed.
"""

from collections.abc import Iterable
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from widgetsystem.core import Theme, ThemeManager


class ThemeController(QObject):
    """Unified controller for theme management.

    Consolidates ThemeFactory (data source) and ThemeManager (state holder)
    into a single API. Handles registration of legacy themes and profile
    themes, and provides a unified apply() method.

    Signals:
        themeApplied: Emitted when theme is applied (theme_id, theme_name)
        themeRegistered: Emitted when theme is registered (theme_id)
        themeError: Emitted on theme errors (error_message)
    """

    themeApplied = Signal(str, str)  # theme_id, theme_name
    themeRegistered = Signal(str)  # theme_id
    themeError = Signal(str)  # error_message

    def __init__(
        self,
        theme_factory: Any,
        tab_color_controller: Any | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Initialize ThemeController.

        Args:
            theme_factory: ThemeFactory for loading theme definitions
            tab_color_controller: Optional TabColorController for tab colors
            parent: Parent QObject
        """
        super().__init__(parent)

        self._theme_factory = theme_factory
        self._tab_color_controller = tab_color_controller

        # Get singleton ThemeManager instance
        self._theme_manager = ThemeManager.instance()

        # Connect to ThemeManager's signal
        self._theme_manager.themeChanged.connect(self._on_theme_manager_changed)

    @property
    def theme_manager(self) -> ThemeManager:
        """Get the ThemeManager instance."""
        return self._theme_manager

    @property
    def current_theme(self) -> Theme | None:
        """Get the current active theme."""
        return self._theme_manager.current_theme()

    @property
    def theme_names(self) -> list[str]:
        """Get list of registered theme names."""
        return self._theme_manager.theme_names()

    def set_tab_color_controller(self, controller: Any) -> None:
        """Set the tab color controller for theme color updates.

        Args:
            controller: TabColorController instance
        """
        self._tab_color_controller = controller

    def register_all_themes(self) -> None:
        """Register all themes from ThemeFactory.

        Registers both legacy QSS themes and profile themes.
        """
        self._register_legacy_themes()
        self._register_profile_themes()
        self._set_default_theme()

    def _register_legacy_themes(self) -> None:
        """Register legacy QSS themes from ThemeFactory."""
        list_themes = getattr(self._theme_factory, "list_themes", None)
        if not callable(list_themes):
            return

        theme_defs = list_themes()
        if not isinstance(theme_defs, Iterable):
            return

        for theme_def in theme_defs:
            try:
                theme = Theme(theme_def.theme_id, theme_def.name)
                if theme_def.file_path.exists():
                    theme.set_stylesheet(
                        theme_def.file_path.read_text(encoding="utf-8")
                    )
                    theme.set_property("tab_active_color", theme_def.tab_active_color)
                    theme.set_property(
                        "tab_inactive_color", theme_def.tab_inactive_color
                    )
                    self._theme_manager.register_theme(theme)
                    self.themeRegistered.emit(theme_def.theme_id)
                    print(f"[+] Registered legacy theme: {theme_def.name}")
            except Exception as e:
                print(f"Failed to register legacy theme '{theme_def.name}': {e}")
                self.themeError.emit(f"Failed to register '{theme_def.name}': {e}")

    def _register_profile_themes(self) -> None:
        """Register profile themes from ThemeFactory."""
        list_profiles = getattr(self._theme_factory, "list_profiles", None)
        load_profile = getattr(self._theme_factory, "load_profile", None)

        if not callable(list_profiles) or not callable(load_profile):
            return

        profile_ids = list_profiles()
        if not isinstance(profile_ids, Iterable):
            return

        for profile_id in profile_ids:
            try:
                profile = load_profile(profile_id)
                if not profile:
                    continue

                profile_name = getattr(profile, "name", None)
                if not isinstance(profile_name, str):
                    continue

                generate_qss = getattr(profile, "generate_qss", None)
                if not callable(generate_qss):
                    continue

                theme = Theme(f"profile_{profile_id}", profile_name)

                try:
                    qss_content = generate_qss()
                except Exception as e:
                    print(f"[!] Failed to generate QSS for profile '{profile_id}': {e}")
                    continue

                if isinstance(qss_content, str):
                    theme.set_stylesheet(qss_content)
                    theme.set_property("is_profile", True)
                    theme.set_property("profile_id", profile_id)
                    self._theme_manager.register_theme(theme)
                    self.themeRegistered.emit(f"profile_{profile_id}")
                    print(f"[+] Registered profile theme: {profile_name}")

            except Exception as e:
                print(f"[!] Failed to register profile theme '{profile_id}': {e}")
                self.themeError.emit(f"Failed to register profile '{profile_id}': {e}")

    def _set_default_theme(self) -> None:
        """Set the default theme from ThemeFactory configuration."""
        default_theme_id = self._theme_factory.get_default_theme_id()
        if default_theme_id:
            self._theme_manager.set_current_theme(default_theme_id)
        elif self._theme_manager.theme_names():
            # Fallback to first available theme
            self._theme_manager.set_current_theme(self._theme_manager.theme_names()[0])

    def apply(self, theme_id: str) -> bool:
        """Apply a theme by ID.

        This is the unified entry point for theme switching.

        Args:
            theme_id: Theme identifier

        Returns:
            True if theme was applied, False otherwise
        """
        return self._theme_manager.set_current_theme(theme_id)

    def apply_profile(self, profile_id: str) -> bool:
        """Apply a profile theme by ID.

        Args:
            profile_id: Profile identifier (without 'profile_' prefix)

        Returns:
            True if theme was applied, False otherwise
        """
        return self.apply(f"profile_{profile_id}")

    def get_theme(self, theme_id: str) -> Theme | None:
        """Get a theme by ID.

        Args:
            theme_id: Theme identifier

        Returns:
            Theme object or None
        """
        return self._theme_manager.get_theme(theme_id)

    def reload_themes(self) -> None:
        """Reload all themes from factory.

        Clears existing themes and re-registers all.
        """
        self._theme_manager.clear()
        self._theme_factory.create_default_profiles()
        self.register_all_themes()

    def _on_theme_manager_changed(self, theme: Theme) -> None:
        """Handle theme change from ThemeManager.

        Applies stylesheet and updates tab colors.

        Args:
            theme: New theme to apply
        """
        try:
            app = QApplication.instance()
            if not isinstance(app, QApplication):
                return

            # Apply stylesheet to application
            app.setStyleSheet(theme.stylesheet)

            # Apply custom palette if available
            if theme.has_custom_palette and theme.palette:
                app.setPalette(theme.palette)

            # Update tab colors
            if self._tab_color_controller:
                tab_active = theme.get_property("tab_active_color", "#E0E0E0")
                tab_inactive = theme.get_property("tab_inactive_color", "#BDBDBD")
                self._tab_color_controller.active_color = tab_active
                self._tab_color_controller.inactive_color = tab_inactive
                self._tab_color_controller.apply()

            print(f"[+] Theme applied: {theme.name}")
            print(f"  Stylesheet length: {len(theme.stylesheet)} chars")
            print(f"  Has rgba colors: {'rgba(' in theme.stylesheet}")

            self.themeApplied.emit(theme.theme_id, theme.name)

        except Exception as e:
            print(f"[!] Failed to apply theme '{theme.name}': {e}")
            self.themeError.emit(f"Failed to apply '{theme.name}': {e}")
