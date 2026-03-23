"""Test Theme Manager - Validates theme management functionality."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette

from widgetsystem.controllers.theme_controller import ThemeController
from widgetsystem.core.theme_manager import Theme, ThemeManager


def test_theme_initialization():
    """Test the initialization of the Theme class."""
    theme = Theme(theme_id="dark", name="Dark Theme")
    assert theme.theme_id == "dark"
    assert theme.name == "Dark Theme"
    assert theme.stylesheet == ""
    assert theme.palette is None
    assert theme.has_custom_palette is False
    assert theme.icons == {}
    assert theme.properties == {}
    print("✅ Theme initialization test passed.")


def test_theme_set_stylesheet():
    """Test setting a stylesheet in the Theme class."""
    theme = Theme(theme_id="dark", name="Dark Theme")
    theme.set_stylesheet("body { background-color: black; }")
    assert theme.stylesheet == "body { background-color: black; }"
    print("✅ Theme set_stylesheet test passed.")


def test_theme_set_palette():
    """Test setting a palette in the Theme class."""
    theme = Theme(theme_id="dark", name="Dark Theme")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#000000"))
    theme.set_palette(palette)
    assert theme.palette == palette
    assert theme.has_custom_palette is True
    print("✅ Theme set_palette test passed.")


def test_theme_controller_apply_and_reload(tmp_path: Path) -> None:
    """ThemeController applies and reloads themes via ThemeFactory."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    qss_file = tmp_path / "dark.qss"
    qss_file.write_text("QWidget { color: #fff; }", encoding="utf-8")

    theme_factory = MagicMock()
    theme_factory.list_themes.return_value = [
        SimpleNamespace(
            theme_id="dark",
            name="Dark",
            file_path=qss_file,
            tab_active_color="#111111",
            tab_inactive_color="#222222",
        ),
    ]
    theme_factory.list_profiles.return_value = []
    theme_factory.get_default_theme_id.return_value = "dark"

    tab_color_controller = MagicMock()

    # Clear ALL stale themeChanged connections from the ThemeManager singleton.
    # Tests that create MainWindow (and its internal ThemeController) run before this
    # file alphabetically and leave their _on_theme_manager_changed slots connected.
    # Those stale slots call app.setStyleSheet() on the full MainWindow widget tree,
    # which blocks the test thread for an unbounded time via StyleChange events.
    try:
        ThemeManager.instance().themeChanged.disconnect()
    except RuntimeError:
        pass  # no connections present

    controller = ThemeController(theme_factory, tab_color_controller=tab_color_controller)

    # Also disconnect this controller's slot to keep the test non-blocking.
    controller.theme_manager.themeChanged.disconnect(controller._on_theme_manager_changed)

    controller.theme_manager.clear()
    controller.register_all_themes()
    assert "dark" in controller.theme_names

    assert controller.apply("dark") is True

    theme_factory.create_default_profiles = MagicMock()
    controller.reload_themes()
    theme_factory.create_default_profiles.assert_called_once()
