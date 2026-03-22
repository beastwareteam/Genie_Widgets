"""Test Theme Profile - Validates theme profile functionality."""

import json

from widgetsystem.core.theme_profile import ThemeColors


def test_theme_colors_initialization():
    """Test the initialization of ThemeColors dataclass."""
    theme_colors = ThemeColors()
    assert theme_colors.window_bg == "#00202124"
    assert theme_colors.splitter_handle == "#ff3c4043"
    assert theme_colors.splitter_width == 2
    assert theme_colors.tab_active_bg == "#cc3c4043"
    assert theme_colors.tab_active_border == "#ff8ab4f8"
    assert theme_colors.tab_active_text == "#ff8ab4f8"
    assert theme_colors.tab_inactive_bg == "#cc2d2e31"
    assert theme_colors.tab_inactive_text == "#ffbdc1c6"
    assert theme_colors.tab_padding == 4
    assert theme_colors.tab_border_radius == 0
    assert theme_colors.titlebar_bg == "#cc2d2e31"
    assert theme_colors.titlebar_text == "#ffe8eaed"
    assert theme_colors.titlebar_btn_hover == "#408ab4f8"
    assert theme_colors.btn_bg == "#40ffffff"
    assert theme_colors.btn_icon == "#ffe8eaed"
    assert theme_colors.floating_border == "#ff3c4043"
    print("✅ ThemeColors initialization test passed.")


def test_theme_colors_to_dict():
    """Test converting ThemeColors to a dictionary."""
    theme_colors = ThemeColors()
    theme_dict = theme_colors.__dict__
    assert theme_dict["window_bg"] == "#00202124"
    assert theme_dict["splitter_handle"] == "#ff3c4043"
    print("✅ ThemeColors to_dict test passed.")


def test_theme_colors_json_serialization():
    """Test JSON serialization of ThemeColors."""
    theme_colors = ThemeColors()
    theme_json = json.dumps(theme_colors.__dict__)
    assert "window_bg" in theme_json
    assert "#00202124" in theme_json
    print("✅ ThemeColors JSON serialization test passed.")
