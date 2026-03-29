"""Custom Gradient System - Render custom gradients for dock areas, replacing QtAds default."""

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget


@dataclass
class GradientStop:
    """A single stop in a gradient (position and color)."""

    position: float  # 0.0 to 1.0
    color: QColor  # Color at this position


class GradientDefinition:
    """Defines a custom gradient with multiple color stops.

    Supports:
    - Linear gradients (horizontal, vertical, diagonal)
    - Radial gradients (circular, elliptical)
    - Custom color stops
    - ARGB colors with transparency
    """

    def __init__(
        self,
        gradient_type: str = "linear",  # "linear" or "radial"
        stops: list[GradientStop] | None = None,
        direction: str = "vertical",  # "horizontal", "vertical", "diagonal"
        name: str = "Custom Gradient",
    ) -> None:
        """Initialize gradient definition.

        Args:
            gradient_type: "linear" or "radial"
            stops: List of gradient stops (color1, color2, etc.)
            direction: "horizontal", "vertical", or "diagonal"
            name: Display name for this gradient
        """
        self.gradient_type = gradient_type
        self.direction = direction
        self.name = name
        self.stops = stops or [
            GradientStop(0.0, QColor(0, 0, 0, 0)),  # Transparent top
            GradientStop(1.0, QColor(0, 0, 0, 0)),  # Transparent bottom
        ]

    def to_qgradient(self, rect: QRect) -> QLinearGradient | QRadialGradient:
        """Convert to Qt gradient object for rendering.

        Args:
            rect: Widget rectangle to apply gradient to

        Returns:
            QLinearGradient or QRadialGradient ready for painting
        """
        if self.gradient_type == "linear":
            return self._create_linear_gradient(rect)
        if self.gradient_type == "radial":
            return self._create_radial_gradient(rect)
        # Default to linear
        return self._create_linear_gradient(rect)

    def _create_linear_gradient(self, rect: QRect) -> QLinearGradient:
        """Create a linear gradient based on direction.

        Args:
            rect: Widget rectangle

        Returns:
            Configured QLinearGradient
        """
        if self.direction == "horizontal":
            # Left to right
            gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        elif self.direction == "diagonal":
            # Top-left to bottom-right
            gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
        else:
            # Vertical (default) - Top to bottom
            gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())

        # Add all color stops
        for stop in self.stops:
            gradient.setColorAt(stop.position, stop.color)

        return gradient

    def _create_radial_gradient(self, rect: QRect) -> QRadialGradient:
        """Create a radial gradient from center.

        Args:
            rect: Widget rectangle

        Returns:
            Configured QRadialGradient
        """
        center_x = rect.left() + rect.width() // 2
        center_y = rect.top() + rect.height() // 2
        radius = max(rect.width(), rect.height()) // 2

        gradient = QRadialGradient(center_x, center_y, radius)

        # Add all color stops
        for stop in self.stops:
            gradient.setColorAt(stop.position, stop.color)

        return gradient

    @staticmethod
    def from_colors(
        color1: str,
        color2: str,
        gradient_type: str = "linear",
        direction: str = "vertical",
        name: str = "Gradient",
    ) -> "GradientDefinition":
        """Create a simple 2-color gradient from hex strings.

        Args:
            color1: Hex color for start (e.g., "#252525")
            color2: Hex color for end (e.g., "#1A1A1A")
            gradient_type: "linear" or "radial"
            direction: "horizontal", "vertical", or "diagonal"
            name: Display name

        Returns:
            New GradientDefinition
        """
        stops = [
            GradientStop(0.0, QColor(color1)),
            GradientStop(1.0, QColor(color2)),
        ]
        return GradientDefinition(
            gradient_type=gradient_type,
            stops=stops,
            direction=direction,
            name=name,
        )


class GradientRenderer:
    """Applies custom gradients to dock area widgets, overriding QtAds defaults."""

    def __init__(self, dock_area_gradient: GradientDefinition = None, floating_container_gradient: GradientDefinition = None, titlebar_gradient: GradientDefinition = None) -> None:
        """Initialisiert den GradientRenderer ausschließlich mit Theme/Config-Objekten.
        Keine festen Farben mehr im Code.
        """
        self.dock_area_gradient = dock_area_gradient
        self.floating_container_gradient = floating_container_gradient
        self.titlebar_gradient = titlebar_gradient

    def paint_dock_area_background(
        self,
        painter: QPainter,
        rect: QRect,
        gradient: GradientDefinition | None = None,
    ) -> None:
        """Paint a dock area background with custom gradient.

        Args:
            painter: QPainter to draw with
            rect: Rectangle to fill
            gradient: Custom gradient (uses dock_area_gradient if None)
        """
        if gradient is None:
            gradient = self.dock_area_gradient

        qt_gradient = gradient.to_qgradient(rect)
        brush = QBrush(qt_gradient)
        painter.fillRect(rect, brush)

    def paint_titlebar_background(self, painter: QPainter, rect: QRect) -> None:
        """Paint a title bar background with custom gradient.

        Args:
            painter: QPainter to draw with
            rect: Rectangle to fill
        """
        qt_gradient = self.titlebar_gradient.to_qgradient(rect)
        brush = QBrush(qt_gradient)
        painter.fillRect(rect, brush)

    def paint_floating_container_background(self, painter: QPainter, rect: QRect) -> None:
        """Paint a floating container background with custom gradient.

        Args:
            painter: QPainter to draw with
            rect: Rectangle to fill
        """
        qt_gradient = self.floating_container_gradient.to_qgradient(rect)
        brush = QBrush(qt_gradient)
        painter.fillRect(rect, brush)

    def set_dock_area_gradient(self, gradient: GradientDefinition) -> None:
        """Set custom gradient for dock areas.

        Args:
            gradient: New gradient definition
        """
        self.dock_area_gradient = gradient

    def set_floating_container_gradient(self, gradient: GradientDefinition) -> None:
        """Set custom gradient for floating containers.

        Args:
            gradient: New gradient definition
        """
        self.floating_container_gradient = gradient

    def set_titlebar_gradient(self, gradient: GradientDefinition) -> None:
        """Set custom gradient for title bars.

        Args:
            gradient: New gradient definition
        """
        self.titlebar_gradient = gradient


class GradientOverrideWidget(QWidget):
    """Wrapper widget that applies custom gradient background, hiding QtAds gradient.

    This widget acts as a background layer that renders the custom gradient
    BEFORE QtAds renders its gradient, effectively overriding it.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.gradient_renderer = GradientRenderer()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

    def paintEvent(self, event: Any) -> None:
        """Paint custom gradient background, overriding QSS/QtAds.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw custom gradient instead of QtAds default
        self.gradient_renderer.paint_dock_area_background(painter, self.rect())

        painter.end()


# Global renderer instance - shared across all windows
_gradient_renderer = GradientRenderer()


def get_gradient_renderer() -> GradientRenderer:
    """Get the global gradient renderer instance.

    Returns:
        Shared GradientRenderer
    """
    return _gradient_renderer
