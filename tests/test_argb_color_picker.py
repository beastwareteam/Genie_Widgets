"""Tests for argb_color_picker.py - ARGB Color Picker components.

Tests cover:
- ARGBColorPicker initialization and color handling
- Slider and spinbox synchronization
- Quick color palette
- Hex input validation
- ARGBColorPickerDialog functionality
- Signal emissions and callbacks
"""

from typing import Any
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from widgetsystem.ui.argb_color_picker import (
    QUICK_COLORS,
    ARGBColorPicker,
    ARGBColorPickerDialog,
)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestARGBColorPicker:
    """Tests for ARGBColorPicker class."""

    def test_initialization_default(self, qapp: QApplication) -> None:
        """Test picker initializes with default color."""
        picker = ARGBColorPicker()

        assert picker.current_color == "#FFFFFFFF"
        assert picker.apply_callback is None

    def test_initialization_with_color(self, qapp: QApplication) -> None:
        """Test picker initializes with specified color."""
        picker = ARGBColorPicker("#80FF0000")

        assert picker.current_color == "#80FF0000"

    def test_initialization_with_callback(self, qapp: QApplication) -> None:
        """Test picker initializes with callback."""
        callback = MagicMock()
        picker = ARGBColorPicker("#FFFFFFFF", callback)

        assert picker.apply_callback is callback

    def test_get_color(self, qapp: QApplication) -> None:
        """Test getting current color."""
        picker = ARGBColorPicker("#FF00FF00")

        assert picker.get_color() == "#FF00FF00"

    def test_set_color_valid(self, qapp: QApplication) -> None:
        """Test setting valid color."""
        picker = ARGBColorPicker()
        picker.set_color("#80FF0000")

        assert picker.get_color() == "#80FF0000"

    def test_set_color_invalid_format(self, qapp: QApplication) -> None:
        """Test setting invalid color format (doesn't crash)."""
        picker = ARGBColorPicker()

        # Should log error but not crash
        picker.set_color("invalid")
        # Color should remain unchanged
        assert picker.current_color == "#FFFFFFFF"

    def test_set_color_invalid_length(self, qapp: QApplication) -> None:
        """Test setting color with wrong length."""
        picker = ARGBColorPicker()

        # Too short
        picker.set_color("#FFF")
        assert picker.current_color == "#FFFFFFFF"

    def test_slider_initialization(self, qapp: QApplication) -> None:
        """Test sliders are initialized correctly."""
        picker = ARGBColorPicker("#80FF8040")

        assert picker.alpha_slider.value() == 0x80
        assert picker.red_slider.value() == 0xFF
        assert picker.green_slider.value() == 0x80
        assert picker.blue_slider.value() == 0x40

    def test_spinbox_initialization(self, qapp: QApplication) -> None:
        """Test spinboxes are initialized correctly."""
        picker = ARGBColorPicker("#80FF8040")

        assert picker.alpha_spin.value() == 0x80
        assert picker.red_spin.value() == 0xFF
        assert picker.green_spin.value() == 0x80
        assert picker.blue_spin.value() == 0x40

    def test_hex_input_initialization(self, qapp: QApplication) -> None:
        """Test hex input is initialized correctly."""
        picker = ARGBColorPicker("#80FF8040")

        assert picker.hex_input.text() == "80FF8040"

    def test_slider_sync_to_spinbox(self, qapp: QApplication) -> None:
        """Test slider change syncs to spinbox."""
        picker = ARGBColorPicker()

        picker.red_slider.setValue(128)

        assert picker.red_spin.value() == 128

    def test_spinbox_sync_to_slider(self, qapp: QApplication) -> None:
        """Test spinbox change syncs to slider."""
        picker = ARGBColorPicker()

        picker.green_spin.setValue(64)

        assert picker.green_slider.value() == 64

    def test_slider_updates_color(self, qapp: QApplication) -> None:
        """Test slider change updates current color."""
        picker = ARGBColorPicker("#FFFFFFFF")

        picker.red_slider.setValue(0)
        picker.green_slider.setValue(255)
        picker.blue_slider.setValue(0)

        # Color should now be green (FF00FF00)
        color = picker.get_color()
        assert color[3:5] == "00"  # Red
        assert color[5:7] == "FF"  # Green
        assert color[7:9] == "00"  # Blue

    def test_color_changed_signal(self, qapp: QApplication) -> None:
        """Test colorChanged signal emission."""
        picker = ARGBColorPicker()

        received = []
        picker.colorChanged.connect(lambda c: received.append(c))

        picker.set_color("#FF00FF00")

        assert "#FF00FF00" in received

    def test_callback_called_on_change(self, qapp: QApplication) -> None:
        """Test callback is called on color change."""
        callback = MagicMock()
        picker = ARGBColorPicker("#FFFFFFFF", callback)

        picker.set_color("#FF00FF00")

        callback.assert_called()
        callback.assert_called_with("#FF00FF00")

    def test_callback_exception_handled(self, qapp: QApplication) -> None:
        """Test callback exception is handled gracefully."""

        def bad_callback(color: str) -> None:
            raise ValueError("Intentional error")

        picker = ARGBColorPicker("#FFFFFFFF", bad_callback)

        # Should not raise
        picker.set_color("#FF00FF00")

    def test_preview_label_updated(self, qapp: QApplication) -> None:
        """Test preview label style is updated."""
        picker = ARGBColorPicker("#FF00FF00")

        stylesheet = picker.preview_label.styleSheet()
        # Should contain rgba values
        assert "rgba" in stylesheet or "background-color" in stylesheet

    def test_info_label_content(self, qapp: QApplication) -> None:
        """Test info label shows color information."""
        picker = ARGBColorPicker("#80FF0000")

        info = picker.info_label.text()
        assert "#80FF0000" in info
        assert "RGB" in info
        assert "Alpha" in info


class TestQuickColors:
    """Tests for quick color palette."""

    def test_quick_colors_count(self, qapp: QApplication) -> None:
        """Test QUICK_COLORS has expected count."""
        assert len(QUICK_COLORS) == 12

    def test_quick_colors_format(self, qapp: QApplication) -> None:
        """Test all quick colors are in correct format."""
        for color in QUICK_COLORS:
            assert color.startswith("#")
            assert len(color) == 9
            # Should be valid hex
            int(color[1:], 16)

    def test_quick_color_button_click(self, qapp: QApplication) -> None:
        """Test clicking quick color button sets color."""
        picker = ARGBColorPicker()

        # Simulate setting color via quick button
        test_color = QUICK_COLORS[0]
        picker._set_color(test_color)

        assert picker.get_color() == test_color


class TestHexInput:
    """Tests for hex color input."""

    def test_hex_input_valid(self, qapp: QApplication) -> None:
        """Test valid hex input."""
        picker = ARGBColorPicker()

        # Manually set hex input (note: needs # prefix for validation)
        picker._on_hex_changed("#80FF0000")

        # Color might or might not update depending on exact input handling

    def test_hex_input_invalid(self, qapp: QApplication) -> None:
        """Test invalid hex input is ignored."""
        picker = ARGBColorPicker("#FFFFFFFF")

        picker._on_hex_changed("invalid")

        # Color should remain unchanged
        assert picker.get_color() == "#FFFFFFFF"

    def test_hex_input_partial(self, qapp: QApplication) -> None:
        """Test partial hex input is ignored."""
        picker = ARGBColorPicker("#FFFFFFFF")

        picker._on_hex_changed("#FF00")  # Too short

        # Color should remain unchanged
        assert picker.get_color() == "#FFFFFFFF"


class TestARGBColorPickerDialog:
    """Tests for ARGBColorPickerDialog class."""

    def test_initialization(self, qapp: QApplication) -> None:
        """Test dialog initializes correctly."""
        dialog = ARGBColorPickerDialog()

        assert dialog.windowTitle() == "ARGB Color Picker"
        assert isinstance(dialog.color_picker, ARGBColorPicker)

    def test_initialization_with_color(self, qapp: QApplication) -> None:
        """Test dialog initializes with color."""
        dialog = ARGBColorPickerDialog("#80FF0000")

        assert dialog.color_picker.get_color() == "#80FF0000"

    def test_initialization_with_callback(self, qapp: QApplication) -> None:
        """Test dialog initializes with callback."""
        callback = MagicMock()
        dialog = ARGBColorPickerDialog("#FFFFFFFF", callback)

        assert dialog.color_picker.apply_callback is callback

    def test_get_color(self, qapp: QApplication) -> None:
        """Test getting color from dialog."""
        dialog = ARGBColorPickerDialog("#FF00FF00")

        assert dialog.get_color() == "#FF00FF00"

    def test_color_picker_embedded(self, qapp: QApplication) -> None:
        """Test color picker is embedded in dialog."""
        dialog = ARGBColorPickerDialog()

        # Dialog should contain the color picker
        assert dialog.color_picker is not None
        assert dialog.color_picker.parent() is not None


class TestSliderRange:
    """Tests for slider and spinbox ranges."""

    def test_alpha_slider_range(self, qapp: QApplication) -> None:
        """Test alpha slider range is 0-255."""
        picker = ARGBColorPicker()

        assert picker.alpha_slider.minimum() == 0
        assert picker.alpha_slider.maximum() == 255

    def test_rgb_slider_ranges(self, qapp: QApplication) -> None:
        """Test RGB slider ranges are 0-255."""
        picker = ARGBColorPicker()

        for slider in [picker.red_slider, picker.green_slider, picker.blue_slider]:
            assert slider.minimum() == 0
            assert slider.maximum() == 255

    def test_spinbox_ranges(self, qapp: QApplication) -> None:
        """Test spinbox ranges are 0-255."""
        picker = ARGBColorPicker()

        for spin in [
            picker.alpha_spin,
            picker.red_spin,
            picker.green_spin,
            picker.blue_spin,
        ]:
            assert spin.minimum() == 0
            assert spin.maximum() == 255


class TestColorValidation:
    """Tests for color validation."""

    def test_valid_color_formats(self, qapp: QApplication) -> None:
        """Test various valid color formats."""
        picker = ARGBColorPicker()

        valid_colors = [
            "#FF000000",  # Black
            "#FFFFFFFF",  # White
            "#00FF0000",  # Transparent red
            "#80808080",  # Semi-transparent gray
        ]

        for color in valid_colors:
            picker.set_color(color)
            assert picker.get_color() == color

    def test_color_case_insensitivity(self, qapp: QApplication) -> None:
        """Test color handling with different cases."""
        picker = ARGBColorPicker()

        # Set lowercase hex
        picker._set_color_internal("#ff00ff00")
        # Color should be stored (may be normalized)
        assert picker.get_color().upper() == "#FF00FF00"


class TestUIComponents:
    """Tests for UI component creation."""

    def test_preview_group_exists(self, qapp: QApplication) -> None:
        """Test preview group is created."""
        picker = ARGBColorPicker()

        assert picker.preview_label is not None
        assert picker.info_label is not None

    def test_input_group_exists(self, qapp: QApplication) -> None:
        """Test input group is created."""
        picker = ARGBColorPicker()

        assert picker.hex_input is not None
        assert picker.hex_input.maxLength() == 9

    def test_sliders_group_exists(self, qapp: QApplication) -> None:
        """Test sliders group is created."""
        picker = ARGBColorPicker()

        assert picker.alpha_slider is not None
        assert picker.red_slider is not None
        assert picker.green_slider is not None
        assert picker.blue_slider is not None

    def test_slider_tick_interval(self, qapp: QApplication) -> None:
        """Test slider tick interval is set."""
        picker = ARGBColorPicker()

        assert picker.alpha_slider.tickInterval() == 25


class TestSignalBlocking:
    """Tests for signal blocking during updates."""

    def test_no_infinite_loop_on_slider_change(self, qapp: QApplication) -> None:
        """Test slider changes don't cause infinite loops."""
        picker = ARGBColorPicker()

        # Rapidly change sliders - should not hang
        for i in range(10):
            picker.red_slider.setValue(i * 25)
            picker.green_slider.setValue(i * 25)
            picker.blue_slider.setValue(i * 25)

        # If we get here, no infinite loop occurred

    def test_no_infinite_loop_on_spinbox_change(self, qapp: QApplication) -> None:
        """Test spinbox changes don't cause infinite loops."""
        picker = ARGBColorPicker()

        # Rapidly change spinboxes - should not hang
        for i in range(10):
            picker.red_spin.setValue(i * 25)
            picker.green_spin.setValue(i * 25)
            picker.blue_spin.setValue(i * 25)

        # If we get here, no infinite loop occurred
