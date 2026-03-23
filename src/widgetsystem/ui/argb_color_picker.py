"""Advanced ARGB Color Picker widget with palette and hex input.

Provides a comprehensive color selection interface with:
- ARGB color preview
- Hex color input
- RGB/Alpha sliders
- Predefined color palette
- Quick color buttons
"""

from collections.abc import Callable
import logging

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
    ) -> None:
        """Initialize ARGB Color Picker.

        Args:
            initial_color: Initial color in #AARRGGBB format
            apply_callback: Optional callback for live preview
            parent: Parent widget

        Raises:
            ValueError: If initial_color is not in valid hex format
        """
        super().__init__(parent)
        self.current_color = initial_color
        self.apply_callback = apply_callback
        self._setup_ui()
        self._set_color(initial_color)
        logger.debug("ARGBColorPicker initialized with color: %s", initial_color)

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
        group = QGroupBox("Color Preview")
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
        return group

    def _create_input_group(self) -> QGroupBox:
        """Create hex input group."""
        group = QGroupBox("Hex Color Input")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Hex #AARRGGBB:"))

        self.hex_input = QLineEdit()
        self.hex_input.setMaxLength(9)
        self.hex_input.setPlaceholderText("FFFFFFFF")
        self.hex_input.textChanged.connect(self._on_hex_changed)
        layout.addWidget(self.hex_input)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_sliders_group(self) -> QGroupBox:
        """Create RGB/Alpha sliders group."""
        group = QGroupBox("Color Components")
        layout = QGridLayout()

        # Alpha slider
        layout.addWidget(QLabel("Alpha (A):"), 0, 0)
        self.alpha_slider = self._create_slider(0, 255)
        self.alpha_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.alpha_slider, 0, 1)
        self.alpha_spin = QSpinBox()
        self.alpha_spin.setRange(0, 255)
        self.alpha_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.alpha_spin, 0, 2)

        # Red slider
        layout.addWidget(QLabel("Red (R):"), 1, 0)
        self.red_slider = self._create_slider(0, 255)
        self.red_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.red_slider, 1, 1)
        self.red_spin = QSpinBox()
        self.red_spin.setRange(0, 255)
        self.red_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.red_spin, 1, 2)

        # Green slider
        layout.addWidget(QLabel("Green (G):"), 2, 0)
        self.green_slider = self._create_slider(0, 255)
        self.green_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.green_slider, 2, 1)
        self.green_spin = QSpinBox()
        self.green_spin.setRange(0, 255)
        self.green_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.green_spin, 2, 2)

        # Blue slider
        layout.addWidget(QLabel("Blue (B):"), 3, 0)
        self.blue_slider = self._create_slider(0, 255)
        self.blue_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.blue_slider, 3, 1)
        self.blue_spin = QSpinBox()
        self.blue_spin.setRange(0, 255)
        self.blue_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self.blue_spin, 3, 2)

        group.setLayout(layout)
        return group

    def _create_quick_colors_group(self) -> QGroupBox:
        """Create quick colors buttons group."""
        group = QGroupBox("Quick Colors")
        layout = QGridLayout()

        for i, color in enumerate(QUICK_COLORS):
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(f"background-color: {color[3:]}; border: 1px solid #ccc;")
            btn.clicked.connect(lambda checked=False, c=color: self._set_color(c))
            layout.addWidget(btn, i // 4, i % 4)

        group.setLayout(layout)
        return group

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
                logger.debug("Invalid hex input: %s - %s", text, exc)

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
            f"Color: {color} | RGB: ({red}, {green}, {blue}) | Alpha: {alpha_percent}%"
        )

        # Emit signals
        self.colorChanged.emit(color)

        # Apply callback if provided
        if self.apply_callback:
            try:
                self.apply_callback(color)
            except Exception as exc:
                logger.exception("Error in apply_callback")

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
            logger.exception("Failed to set color")


class ARGBColorPickerDialog(QDialog):
    """Dialog wrapper for ARGBColorPicker.

    Provides a convenient dialog interface for color selection.
    """

    def __init__(
        self,
        initial_color: str = "#FFFFFFFF",
        apply_callback: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize color picker dialog.

        Args:
            initial_color: Initial color in #AARRGGBB format
            apply_callback: Optional callback for live preview
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("ARGB Color Picker")
        self.setGeometry(100, 100, 500, 600)

        layout = QVBoxLayout(self)

        self.color_picker = ARGBColorPicker(initial_color, apply_callback, self)
        layout.addWidget(self.color_picker)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        logger.debug("ARGBColorPickerDialog created with color: %s", initial_color)

    def get_color(self) -> str:
        """Get selected color.

        Returns:
            Hex color in #AARRGGBB format
        """
        return self.color_picker.get_color()
