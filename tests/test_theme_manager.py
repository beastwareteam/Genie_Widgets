"""Test Theme Manager - Validates theme management functionality."""

from PySide6.QtGui import QColor, QPalette

from widgetsystem.core.theme_manager import Theme


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
