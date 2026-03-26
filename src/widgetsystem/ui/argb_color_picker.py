"""Advanced ARGB Color Picker widget with palette and hex input.

Provides a comprehensive color selection interface with:
- ARGB color preview
- Hex color input
- RGB/Alpha sliders
- Predefined color palette
- Quick color buttons
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory

# Predefined color palettes
QUICK_COLORS = [
    "#FF0000FF",  # Red
    "#FF00FF00",  # Green
    "#FF0000FF",  # Blue
    "#FFFFFF00",  # Yellow
    "#FFFF00FF",  # Magenta
    "#FF00FFFF",  # Cyan
    "#FFFF8800",  # Orange
    "#FF800080",  # Purple
    "#FFC0C0C0",  # Silver
    "#FF808080",  # Gray
    "#FF000000",  # Black
    "#FFFFFFFF",  # White
]


class ARGBColorPicker(QWidget):
    """Advanced ARGB color picker with palette and hex input.

    Signals:
        colorChanged: Emitted when color changes (#AARRGGBB format)
        colorSelected: Emitted when user confirms selection
    """

    colorChanged = Signal(str)
    colorSelected = Signal(str)

    def __init__(
        self,
        initial_color: str = "#FFFFFFFF",
        apply_callback: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
        i18n_factory: I18nFactory | None = None,
    ) -> None:
        """Initialize ARGB Color Picker.

        Args:
            initial_color: Initial color in #AARRGGBB format
            apply_callback: Optional callback for live preview
            parent: Parent widget
            i18n_factory: Optional i18n factory for UI text translation

        Raises:
            ValueError: If initial_color is not in valid hex format
        """
        super().__init__(parent)
        self.current_color = initial_color
        self.apply_callback = apply_callback
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        self._setup_ui()
        self._set_color(initial_color)
        logger.debug(f"ARGBColorPicker initialized with color: {initial_color}")

    def set_i18n_factory(self, i18n_factory: I18nFactory | None) -> None:
        """Set or update i18n factory and refresh visible texts."""
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()
        self._apply_translated_texts()
        self._set_color_internal(self.current_color)

    def _translate(self, key: str, default: str | None = None, **kwargs: object) -> str:
        """Translate a key using i18n factory with cache and fallback."""
        if not self._i18n_factory or not key:
            text = default or key
            return text.format(**kwargs) if kwargs else text

        cache_key = f"{key}|{sorted(kwargs.items())}" if kwargs else key
        if cache_key in self._translated_cache:
            return self._translated_cache[cache_key]

        translated = self._i18n_factory.translate(key, default=default or key, **kwargs)
        self._translated_cache[cache_key] = translated
        return translated

    def _setup_ui(self) -> None:
        """Set up user interface."""
        main_layout = QVBoxLayout(self)

        # Color preview section
        preview_group = self._create_preview_group()
        main_layout.addWidget(preview_group)

        # Color input section
        input_group = self._create_input_group()
        main_layout.addWidget(input_group)

        # RGB/Alpha sliders section
        sliders_group = self._create_sliders_group()
        main_layout.addWidget(sliders_group)

        # Quick colors section
        quick_group = self._create_quick_colors_group()
        main_layout.addWidget(quick_group)

        main_layout.addStretch()

    def _create_preview_group(self) -> QGroupBox:
        """Create color preview group."""
        group = QGroupBox(self._translate("argb.preview_group", "Color Preview"))
        layout = QVBoxLayout()

        # Current color preview
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(100)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        layout.addWidget(self.preview_label)

        # Color info
        self.info_label = QLabel()
        font = QFont()
        font.setPointSize(9)
        self.info_label.setFont(font)
        layout.addWidget(self.info_label)

        group.setLayout(layout)
        self.preview_group = group
        return group

    def _create_input_group(self) -> QGroupBox:
        """Create hex input group."""
        group = QGroupBox(self._translate("argb.hex_input_group", "Hex Color Input"))
        layout = QHBoxLayout()

        self.hex_label = QLabel(self._translate("argb.hex_label", "Hex #AARRGGBB:"))
        layout.addWidget(self.hex_label)

        self.hex_input = QLineEdit()
        self.hex_input.setMaxLength(9)
        self.hex_input.setPlaceholderText(
            self._translate("argb.hex_placeholder", "FFFFFFFF"),
        )
        self.hex_input.textChanged.connect(self._on_hex_changed)
        layout.addWidget(self.hex_input)

        layout.addStretch()
        group.setLayout(layout)
        self.input_group = group
        return group

    def _create_sliders_group(self) -> QGroupBox:
        """Create RGB/Alpha sliders group."""
        group = QGroupBox(self._translate("argb.components_group", "Color Components"))
        layout = QGridLayout()

        # Alpha slider
        self.alpha_label = QLabel(self._translate("argb.label.alpha", "Alpha (A):"))
        layout.addWidget(self.alpha_label, 0, 0)
        self.alpha_slider = self._create_slider(0, 255)
        self.alpha_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.alpha_slider, 0, 1)
        self.alpha_spin = QSpinBox()
        self.alpha_spin.setRange(0, 255)
        self.alpha_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.alpha_spin, 0, 2)

        # Red slider
        self.red_label = QLabel(self._translate("argb.label.red", "Red (R):"))
        layout.addWidget(self.red_label, 1, 0)
        self.red_slider = self._create_slider(0, 255)
        self.red_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.red_slider, 1, 1)
        self.red_spin = QSpinBox()
        self.red_spin.setRange(0, 255)
        self.red_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.red_spin, 1, 2)

        # Green slider
        self.green_label = QLabel(self._translate("argb.label.green", "Green (G):"))
        layout.addWidget(self.green_label, 2, 0)
        self.green_slider = self._create_slider(0, 255)
        self.green_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.green_slider, 2, 1)
        self.green_spin = QSpinBox()
        self.green_spin.setRange(0, 255)
        self.green_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.green_spin, 2, 2)

        # Blue slider
        self.blue_label = QLabel(self._translate("argb.label.blue", "Blue (B):"))
        layout.addWidget(self.blue_label, 3, 0)
        self.blue_slider = self._create_slider(0, 255)
        self.blue_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.blue_slider, 3, 1)
        self.blue_spin = QSpinBox()
        self.blue_spin.setRange(0, 255)
        self.blue_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.blue_spin, 3, 2)

        group.setLayout(layout)
        self.sliders_group = group
        return group

    def _create_quick_colors_group(self) -> QGroupBox:
        """Create quick colors buttons group."""
        group = QGroupBox(self._translate("argb.quick_colors_group", "Quick Colors"))
        layout = QGridLayout()

        for i, color in enumerate(QUICK_COLORS):
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(f"background-color: {color[3:]}; border: 1px solid #ccc;")
            btn.clicked.connect(lambda checked=False, c=color: self._set_color(c))
            layout.addWidget(btn, i // 4, i % 4)

        group.setLayout(layout)
        self.quick_group = group
        return group

    def _apply_translated_texts(self) -> None:
        """Refresh translated static texts in the picker."""
        self.preview_group.setTitle(self._translate("argb.preview_group", "Color Preview"))
        self.input_group.setTitle(self._translate("argb.hex_input_group", "Hex Color Input"))
        self.hex_label.setText(self._translate("argb.hex_label", "Hex #AARRGGBB:"))
        self.hex_input.setPlaceholderText(self._translate("argb.hex_placeholder", "FFFFFFFF"))
        self.sliders_group.setTitle(self._translate("argb.components_group", "Color Components"))
        self.alpha_label.setText(self._translate("argb.label.alpha", "Alpha (A):"))
        self.red_label.setText(self._translate("argb.label.red", "Red (R):"))
        self.green_label.setText(self._translate("argb.label.green", "Green (G):"))
        self.blue_label.setText(self._translate("argb.label.blue", "Blue (B):"))
        self.quick_group.setTitle(self._translate("argb.quick_colors_group", "Quick Colors"))

    @staticmethod
    def _create_slider(minimum: int, maximum: int) -> QSlider:
        """Create horizontal slider with range.

        Args:
            minimum: Minimum value
            maximum: Maximum value

        Returns:
            Configured QSlider
        """
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(25)
        return slider

    def _on_hex_changed(self, text: str) -> None:
        """Handle hex input change.

        Args:
            text: Current hex input text
        """
        if len(text) == 8 and text.startswith("#"):
            try:
                self._set_color(f"#{text}")
            except ValueError as exc:
                logger.debug(f"Invalid hex input: {text} - {exc}")

    def _on_slider_changed(self) -> None:
        """Handle slider value change."""
        self._update_from_sliders()

    def _on_spin_changed(self) -> None:
        """Handle spin box value change."""
        self._update_from_spinboxes()

    def _update_from_sliders(self) -> None:
        """Update color from slider values."""
        alpha = self.alpha_slider.value()
        red = self.red_slider.value()
        green = self.green_slider.value()
        blue = self.blue_slider.value()

        # Sync spinboxes
        self.alpha_spin.blockSignals(True)
        self.red_spin.blockSignals(True)
        self.green_spin.blockSignals(True)
        self.blue_spin.blockSignals(True)

        self.alpha_spin.setValue(alpha)
        self.red_spin.setValue(red)
        self.green_spin.setValue(green)
        self.blue_spin.setValue(blue)

        self.alpha_spin.blockSignals(False)
        self.red_spin.blockSignals(False)
        self.green_spin.blockSignals(False)
        self.blue_spin.blockSignals(False)

        color = f"#{alpha:02X}{red:02X}{green:02X}{blue:02X}"
        self._set_color_internal(color)

    def _update_from_spinboxes(self) -> None:
        """Update color from spinbox values."""
        alpha = self.alpha_spin.value()
        red = self.red_spin.value()
        green = self.green_spin.value()
        blue = self.blue_spin.value()

        # Sync sliders
        self.alpha_slider.blockSignals(True)
        self.red_slider.blockSignals(True)
        self.green_slider.blockSignals(True)
        self.blue_slider.blockSignals(True)

        self.alpha_slider.setValue(alpha)
        self.red_slider.setValue(red)
        self.green_slider.setValue(green)
        self.blue_slider.setValue(blue)

        self.alpha_slider.blockSignals(False)
        self.red_slider.blockSignals(False)
        self.green_slider.blockSignals(False)
        self.blue_slider.blockSignals(False)

        color = f"#{alpha:02X}{red:02X}{green:02X}{blue:02X}"
        self._set_color_internal(color)

    def _set_color(self, color: str) -> None:
        """Set color from hex string (#AARRGGBB).

        Args:
            color: Hex color string

        Raises:
            ValueError: If color format is invalid
        """
        if not color.startswith("#") or len(color) != 9:
            raise ValueError(
                f"Invalid color format: {color}. Expected #AARRGGBB"
            )

        try:
            int(color[1:], 16)
        except ValueError as exc:
            raise ValueError(f"Invalid hex color: {color}") from exc

        self._set_color_internal(color)

    def _set_color_internal(self, color: str) -> None:
        """Set color internally and update UI.

        Args:
            color: Hex color in #AARRGGBB format
        """
        self.current_color = color
        self.hex_input.blockSignals(True)
        self.hex_input.setText(color[1:])
        self.hex_input.blockSignals(False)

        # Parse components
        alpha = int(color[1:3], 16)
        red = int(color[3:5], 16)
        green = int(color[5:7], 16)
        blue = int(color[7:9], 16)

        # Update sliders
        self.alpha_slider.blockSignals(True)
        self.red_slider.blockSignals(True)
        self.green_slider.blockSignals(True)
        self.blue_slider.blockSignals(True)

        self.alpha_slider.setValue(alpha)
        self.red_slider.setValue(red)
        self.green_slider.setValue(green)
        self.blue_slider.setValue(blue)

        self.alpha_slider.blockSignals(False)
        self.red_slider.blockSignals(False)
        self.green_slider.blockSignals(False)
        self.blue_slider.blockSignals(False)

        # Update spinboxes
        self.alpha_spin.blockSignals(True)
        self.red_spin.blockSignals(True)
        self.green_spin.blockSignals(True)
        self.blue_spin.blockSignals(True)

        self.alpha_spin.setValue(alpha)
        self.red_spin.setValue(red)
        self.green_spin.setValue(green)
        self.blue_spin.setValue(blue)

        self.alpha_spin.blockSignals(False)
        self.red_spin.blockSignals(False)
        self.green_spin.blockSignals(False)
        self.blue_spin.blockSignals(False)

        # Update preview
        preview_color = QColor(red, green, blue, alpha)
        alpha_percent = int((alpha / 255) * 100)
        self.preview_label.setStyleSheet(
            f"background-color: rgba({red}, {green}, {blue}, {alpha}); border: 1px solid #ccc;"
        )
        self.info_label.setText(
            self._translate(
                "argb.info_line",
                "Color: {color} | RGB: ({red}, {green}, {blue}) | Alpha: {alpha_percent}%",
                color=color,
                red=red,
                green=green,
                blue=blue,
                alpha_percent=alpha_percent,
            ),
        )

        # Emit signals
        self.colorChanged.emit(color)

        # Apply callback if provided
        if self.apply_callback:
            try:
                self.apply_callback(color)
            except Exception as exc:
                logger.exception(f"Error in apply_callback: {exc}")

    def get_color(self) -> str:
        """Get current color.

        Returns:
            Hex color in #AARRGGBB format
        """
        return self.current_color

    def set_color(self, color: str) -> None:
        """Set color externally.

        Args:
            color: Hex color in #AARRGGBB format

        Raises:
            ValueError: If color format is invalid
        """
        try:
            self._set_color(color)
        except ValueError as exc:
            logger.error(f"Failed to set color: {exc}")


class ARGBColorPickerDialog(QDialog):
    """Dialog wrapper for ARGBColorPicker.

    Provides a convenient dialog interface for color selection.
    """

    def __init__(
        self,
        initial_color: str = "#FFFFFFFF",
        apply_callback: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
        i18n_factory: I18nFactory | None = None,
    ) -> None:
        """Initialize color picker dialog.

        Args:
            initial_color: Initial color in #AARRGGBB format
            apply_callback: Optional callback for live preview
            parent: Parent widget
            i18n_factory: Optional i18n factory for dialog text translation
        """
        super().__init__(parent)
        self._i18n_factory = i18n_factory
        self.setWindowTitle(self._translate("argb.dialog_title", "ARGB Color Picker"))
        self.setGeometry(100, 100, 500, 600)

        layout = QVBoxLayout(self)

        self.color_picker = ARGBColorPicker(
            initial_color,
            apply_callback,
            self,
            i18n_factory=i18n_factory,
        )
        layout.addWidget(self.color_picker)

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.cancel_button = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        if self.ok_button is not None:
            self.ok_button.setText(self._translate("dialog.ok", "OK"))
        if self.cancel_button is not None:
            self.cancel_button.setText(self._translate("dialog.cancel", "Cancel"))
        layout.addWidget(self.button_box)

        logger.debug(f"ARGBColorPickerDialog created with color: {initial_color}")

    def _translate(self, key: str, default: str | None = None) -> str:
        """Translate dialog text using i18n factory if available."""
        if not self._i18n_factory or not key:
            return default or key
        return self._i18n_factory.translate(key, default=default or key)

    def set_i18n_factory(self, i18n_factory: I18nFactory | None) -> None:
        """Set or update i18n factory and refresh visible texts."""
        self._i18n_factory = i18n_factory
        self.setWindowTitle(self._translate("argb.dialog_title", "ARGB Color Picker"))
        if self.ok_button is not None:
            self.ok_button.setText(self._translate("dialog.ok", "OK"))
        if self.cancel_button is not None:
            self.cancel_button.setText(self._translate("dialog.cancel", "Cancel"))
        self.color_picker.set_i18n_factory(i18n_factory)

    def get_color(self) -> str:
        """Get selected color.

        Returns:
            Hex color in #AARRGGBB format
        """
        return self.color_picker.get_color()
