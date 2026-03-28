"""Extended tests for ThemeProfile - covers all methods and branches."""

from __future__ import annotations

from dataclasses import asdict
import json
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication
import pytest

from widgetsystem.core.theme_profile import ThemeColors, ThemeProfile


if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.isolated, pytest.mark.usefixtures("qapp")]


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide QApplication instance for the module."""
    application = QApplication.instance()
    if not isinstance(application, QApplication):
        application = QApplication([])
    assert isinstance(application, QApplication)
    return application


# ---------------------------------------------------------------------------
# ThemeColors - dataclass
# ---------------------------------------------------------------------------


def test_theme_colors_default_tab_border_radius():
    """tab_border_radius should default to 4 (not 0)."""
    assert ThemeColors().tab_border_radius == 4


def test_theme_colors_asdict_contains_all_keys():
    """asdict(ThemeColors()) should include all expected keys."""
    d = asdict(ThemeColors())
    assert "window_bg" in d
    assert "splitter_width" in d
    assert "tab_active_bg" in d
    assert "overlay_border_width" in d
    assert "tab_drop_insert_width" in d


def test_theme_colors_custom_values():
    """Custom field values should be stored as given."""
    colors = ThemeColors(window_bg="#ff000000", splitter_width=5)
    assert colors.window_bg == "#ff000000"
    assert colors.splitter_width == 5


def test_theme_colors_integer_and_string_fields():
    """Integer and string fields should have correct types."""
    c = ThemeColors()
    assert isinstance(c.splitter_width, int)
    assert isinstance(c.tab_padding, int)
    assert isinstance(c.window_bg, str)


# ---------------------------------------------------------------------------
# ThemeProfile - init
# ---------------------------------------------------------------------------


def test_theme_profile_default_name():
    """Default name should be 'Custom Profile'."""
    profile = ThemeProfile()
    assert profile.name == "Custom Profile"


def test_theme_profile_custom_name():
    """Custom name should be stored."""
    profile = ThemeProfile("My Dark Theme")
    assert profile.name == "My Dark Theme"


def test_theme_profile_default_transforms():
    """Default transform values should be identity."""
    profile = ThemeProfile()
    assert profile.global_hue == 0
    assert profile.global_saturation == 1.0
    assert profile.global_brightness == 1.0


def test_theme_profile_has_theme_colors_instance():
    """colors attribute should be a ThemeColors instance."""
    profile = ThemeProfile()
    assert isinstance(profile.colors, ThemeColors)


# ---------------------------------------------------------------------------
# as_qss_color
# ---------------------------------------------------------------------------


def test_as_qss_color_opaque():
    """Opaque ARGB color should produce rgba with alpha 255."""
    profile = ThemeProfile()
    result = profile.as_qss_color("#ff3c4043")
    assert result.startswith("rgba(")
    assert result.endswith(")")
    # alpha component should be 255
    alpha = int(result.rstrip(")").split(",")[-1].strip())
    assert alpha == 255


def test_as_qss_color_transparent():
    """Fully transparent color should produce rgba with alpha 0."""
    profile = ThemeProfile()
    result = profile.as_qss_color("#00202124")
    alpha = int(result.rstrip(")").split(",")[-1].strip())
    assert alpha == 0


def test_as_qss_color_partial_alpha():
    """Partial alpha (#cc...) should produce alpha between 1 and 254."""
    profile = ThemeProfile()
    result = profile.as_qss_color("#cc3c4043")
    alpha = int(result.rstrip(")").split(",")[-1].strip())
    assert 1 <= alpha <= 254


def test_as_qss_color_format():
    """Result should follow rgba(R, G, B, A) format."""
    profile = ThemeProfile()
    result = profile.as_qss_color("#ffff0000")
    assert result.startswith("rgba(")
    parts = result[5:-1].split(",")
    assert len(parts) == 4
    for part in parts:
        assert part.strip().isdigit()


# ---------------------------------------------------------------------------
# apply_global_transforms
# ---------------------------------------------------------------------------


def test_apply_global_transforms_identity():
    """With default transforms, color should be returned nearly unchanged."""
    profile = ThemeProfile()
    original = "#ff3c4043"
    result = profile.apply_global_transforms(original)
    # Should start with # and be 9 characters (#AARRGGBB)
    assert result.startswith("#")
    assert len(result) == 9


def test_apply_global_transforms_hue_shift():
    """Non-zero hue shift should modify hue component."""
    profile_a = ThemeProfile()
    profile_b = ThemeProfile()
    profile_b.global_hue = 90  # 90-degree shift

    color = "#ff80ff40"  # saturated green-ish
    result_a = profile_a.apply_global_transforms(color)
    result_b = profile_b.apply_global_transforms(color)
    assert result_a != result_b


def test_apply_global_transforms_brightness_below_zero_clamps():
    """Brightness multiplier of 0 should clamp value to 0 (black, opaque)."""
    profile = ThemeProfile()
    profile.global_brightness = 0.0
    result = profile.apply_global_transforms("#ffffffff")
    # All channels should be clamped to 0 → black
    from PySide6.QtGui import QColor

    color = QColor(result)
    assert color.valueF() == pytest.approx(0.0, abs=1e-3)


def test_apply_global_transforms_saturation_zero_gives_gray():
    """Saturation=0 should produce a gray (saturation=0) color."""
    profile = ThemeProfile()
    profile.global_saturation = 0.0
    result = profile.apply_global_transforms("#ff80ff40")  # saturated color

    from PySide6.QtGui import QColor

    color = QColor(result)
    assert color.saturationF() == pytest.approx(0.0, abs=1e-3)


def test_apply_global_transforms_brightness_clamped_at_one():
    """Brightness > 1.0 should clamp to 1.0 (max brightness)."""
    profile = ThemeProfile()
    profile.global_brightness = 100.0
    result = profile.apply_global_transforms("#ff404040")  # mid-gray

    from PySide6.QtGui import QColor

    color = QColor(result)
    assert color.valueF() == pytest.approx(1.0, abs=1e-3)


# ---------------------------------------------------------------------------
# generate_qss
# ---------------------------------------------------------------------------


def test_generate_qss_returns_string():
    """generate_qss should return a non-empty string."""
    profile = ThemeProfile("Test")
    qss = profile.generate_qss()
    assert isinstance(qss, str)
    assert len(qss) > 100


def test_generate_qss_contains_profile_name():
    """QSS output should contain the profile name."""
    profile = ThemeProfile("MyProfileName")
    qss = profile.generate_qss()
    assert "MyProfileName" in qss


def test_generate_qss_contains_expected_selectors():
    """QSS should contain key Qt and ads selectors."""
    qss = ThemeProfile().generate_qss()
    for selector in ["QMainWindow", "ads--CDockManager", "QTabBar", "QMenu", "QToolBar"]:
        assert selector in qss, f"Missing selector: {selector}"


def test_generate_qss_contains_rgba():
    """QSS should contain rgba() color values."""
    qss = ThemeProfile().generate_qss()
    assert "rgba(" in qss


# ---------------------------------------------------------------------------
# to_json / from_json roundtrip
# ---------------------------------------------------------------------------


def test_to_json_returns_valid_json():
    """to_json should return parseable JSON."""
    profile = ThemeProfile("RoundTrip")
    data = json.loads(profile.to_json())
    assert data["name"] == "RoundTrip"
    assert "colors" in data
    assert "global" in data


def test_to_json_global_keys():
    """JSON global section should have hue, saturation, brightness."""
    data = json.loads(ThemeProfile().to_json())
    assert "hue" in data["global"]
    assert "saturation" in data["global"]
    assert "brightness" in data["global"]


def test_from_json_restores_name():
    """from_json should restore the profile name."""
    json_str = ThemeProfile("Restored").to_json()
    profile = ThemeProfile.from_json(json_str)
    assert profile.name == "Restored"


def test_from_json_restores_colors():
    """from_json should restore custom color values."""
    original = ThemeProfile()
    original.colors.window_bg = "#ff112233"
    json_str = original.to_json()
    restored = ThemeProfile.from_json(json_str)
    assert restored.colors.window_bg == "#ff112233"


def test_from_json_restores_global_transforms():
    """from_json should restore global hue/saturation/brightness."""
    original = ThemeProfile()
    original.global_hue = 45
    original.global_saturation = 0.8
    original.global_brightness = 1.2
    restored = ThemeProfile.from_json(original.to_json())
    assert restored.global_hue == 45
    assert restored.global_saturation == pytest.approx(0.8)
    assert restored.global_brightness == pytest.approx(1.2)


def test_from_json_missing_name_uses_default():
    """from_json with no name field should use default."""
    json_str = json.dumps({"colors": {}, "global": {}})
    profile = ThemeProfile.from_json(json_str)
    assert profile.name == "Imported Profile"


def test_from_json_missing_global_uses_defaults():
    """from_json with empty global section should keep identity transforms."""
    json_str = json.dumps({"name": "X", "colors": {}, "global": {}})
    profile = ThemeProfile.from_json(json_str)
    assert profile.global_hue == 0
    assert profile.global_saturation == pytest.approx(1.0)
    assert profile.global_brightness == pytest.approx(1.0)


def test_from_json_unknown_color_key_ignored():
    """from_json should ignore color keys that do not exist on ThemeColors."""
    json_str = json.dumps(
        {"name": "X", "colors": {"nonexistent_field": "#ff000000"}, "global": {}}
    )
    # Should not raise
    profile = ThemeProfile.from_json(json_str)
    assert profile.name == "X"


# ---------------------------------------------------------------------------
# save_to_file / load_from_file
# ---------------------------------------------------------------------------


def test_save_and_load_file_roundtrip(tmp_path: Path):
    """save_to_file then load_from_file should restore all values."""
    original = ThemeProfile("FileTest")
    original.colors.splitter_width = 7
    original.global_hue = 120

    file_path = tmp_path / "profile.json"
    original.save_to_file(file_path)

    loaded = ThemeProfile.load_from_file(file_path)
    assert loaded.name == "FileTest"
    assert loaded.colors.splitter_width == 7
    assert loaded.global_hue == 120


def test_save_to_file_creates_file(tmp_path: Path):
    """save_to_file should create a JSON file on disk."""
    file_path = tmp_path / "out.json"
    ThemeProfile("FS").save_to_file(file_path)
    assert file_path.exists()
    data = json.loads(file_path.read_text(encoding="utf-8"))
    assert data["name"] == "FS"
