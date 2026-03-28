"""Extended tests for theme manager functionality."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pytest
from PySide6.QtGui import QIcon

from widgetsystem.core.theme_manager import Theme, ThemeManager


@pytest.fixture(autouse=True)
def reset_theme_manager_singleton() -> Generator[None, Any, Any]:
    """Reset the singleton state before and after each test."""
    ThemeManager._instance = None  # noqa: SLF001
    yield
    ThemeManager._instance = None  # noqa: SLF001


def test_theme_icon_roundtrip() -> None:
    """Test setting and retrieving a registered icon."""
    theme = Theme(theme_id="dark", name="Dark")
    icon = QIcon()

    theme.set_icon("save", icon)

    assert theme.get_icon("save").cacheKey() == icon.cacheKey()


def test_theme_get_icon_returns_empty_icon_for_missing_id() -> None:
    """Test `get_icon()` returns an empty icon for unknown IDs."""
    theme = Theme(theme_id="dark", name="Dark")

    icon = theme.get_icon("missing")

    assert isinstance(icon, QIcon)
    assert icon.isNull(), "Expected missing icon lookup to return an empty icon"


def test_theme_property_roundtrip_with_default() -> None:
    """Test setting and retrieving theme properties."""
    theme = Theme(theme_id="dark", name="Dark")
    theme.set_property("accent", "#ff00ff")

    assert theme.get_property("accent") == "#ff00ff"
    assert theme.get_property("missing", "fallback") == "fallback"


def test_theme_manager_instance_returns_singleton() -> None:
    """Test `instance()` returns the same manager every time."""
    first = ThemeManager.instance()
    second = ThemeManager.instance()

    assert first is second, "Expected `ThemeManager.instance()` to return a singleton"


def test_register_and_get_theme() -> None:
    """Test registering a theme makes it retrievable by ID."""
    manager = ThemeManager.instance()
    theme = Theme(theme_id="dark", name="Dark")

    manager.register_theme(theme)

    assert manager.get_theme("dark") is theme


def test_current_theme_is_none_when_not_set() -> None:
    """Test `current_theme()` returns `None` when no active theme exists."""
    manager = ThemeManager.instance()

    assert manager.current_theme() is None


def test_set_current_theme_emits_signal_and_returns_true() -> None:
    """Test activating a valid theme updates state and emits the signal."""
    manager = ThemeManager.instance()
    theme = Theme(theme_id="dark", name="Dark")
    emitted: list[Theme] = []

    manager.register_theme(theme)
    manager.themeChanged.connect(emitted.append)

    result = manager.set_current_theme("dark")

    assert result is True
    assert manager.current_theme_id == "dark"
    assert manager.current_theme() is theme
    assert emitted == [theme]


def test_set_current_theme_returns_false_for_unknown_theme() -> None:
    """Test activating an unknown theme fails without changing state."""
    manager = ThemeManager.instance()

    result = manager.set_current_theme("unknown")

    assert result is False
    assert manager.current_theme_id == ""


def test_theme_names_returns_registered_ids() -> None:
    """Test `theme_names()` returns all registered theme IDs."""
    manager = ThemeManager.instance()
    manager.register_theme(Theme(theme_id="dark", name="Dark"))
    manager.register_theme(Theme(theme_id="light", name="Light"))

    names = manager.theme_names()

    assert names == ["dark", "light"]


def test_clear_removes_all_themes_and_resets_current_theme() -> None:
    """Test `clear()` empties the registry and resets active theme state."""
    manager = ThemeManager.instance()
    manager.register_theme(Theme(theme_id="dark", name="Dark"))
    manager.set_current_theme("dark")

    manager.clear()

    assert manager.themes == {}
    assert manager.current_theme_id == ""
    assert manager.current_theme() is None
