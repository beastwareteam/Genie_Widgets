"""Pytest smoke tests for theme system and profile-backed themes."""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from widgetsystem.core import Theme, ThemeManager
from widgetsystem.factories.theme_factory import ThemeFactory


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_theme_factory_profiles_are_accessible() -> None:
    """ThemeFactory can enumerate profile IDs."""
    _get_app()
    factory = ThemeFactory(Path("config"))

    profile_ids = factory.list_profiles()
    assert isinstance(profile_ids, list)


def test_theme_manager_can_register_and_activate_theme() -> None:
    """ThemeManager can register and switch to a synthetic theme."""
    _get_app()
    manager = ThemeManager.instance()

    theme = Theme("pytest_theme", "Pytest Theme")
    theme.set_stylesheet("QWidget { background: transparent; }")
    manager.register_theme(theme)
    manager.set_current_theme("pytest_theme")

    current = manager.current_theme()
    assert current is not None
    assert current.theme_id == "pytest_theme"
