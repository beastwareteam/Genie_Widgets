"""Extended tests for the gradient system."""

from __future__ import annotations

from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter, QRadialGradient
from PySide6.QtWidgets import QApplication

from widgetsystem.core.gradient_system import (
    GradientDefinition,
    GradientOverrideWidget,
    GradientRenderer,
    GradientStop,
    get_gradient_renderer,
)


def qapp() -> QApplication:
    """Return a QApplication instance for widget-based tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    assert isinstance(app, QApplication)
    return app


def test_gradient_definition_uses_default_stops() -> None:
    """Test default gradient initialization creates two default stops."""
    gradient = GradientDefinition()

    assert gradient.name == "Custom Gradient"
    assert len(gradient.stops) == 2
    assert gradient.stops[0].position == 0.0
    assert gradient.stops[1].position == 1.0


def test_to_qgradient_creates_horizontal_linear_gradient() -> None:
    """Test horizontal linear gradient creation."""
    gradient = GradientDefinition(direction="horizontal")

    qt_gradient = gradient.to_qgradient(QRect(0, 0, 100, 40))

    assert isinstance(qt_gradient, QLinearGradient)
    assert qt_gradient.start().x() == 0.0
    assert qt_gradient.start().y() == 0.0
    assert qt_gradient.finalStop().x() == 99.0
    assert qt_gradient.finalStop().y() == 0.0


def test_to_qgradient_creates_diagonal_linear_gradient() -> None:
    """Test diagonal linear gradient creation."""
    gradient = GradientDefinition(direction="diagonal")

    qt_gradient = gradient.to_qgradient(QRect(0, 0, 100, 50))

    assert isinstance(qt_gradient, QLinearGradient)
    assert qt_gradient.finalStop().x() == 99.0
    assert qt_gradient.finalStop().y() == 49.0


def test_to_qgradient_defaults_to_vertical_linear_gradient() -> None:
    """Test unknown direction falls back to vertical gradient."""
    gradient = GradientDefinition(direction="mystery")

    qt_gradient = gradient.to_qgradient(QRect(0, 0, 100, 50))

    assert isinstance(qt_gradient, QLinearGradient)
    assert qt_gradient.finalStop().x() == 0.0
    assert qt_gradient.finalStop().y() == 49.0


def test_to_qgradient_creates_radial_gradient() -> None:
    """Test radial gradient creation."""
    gradient = GradientDefinition(gradient_type="radial")

    qt_gradient = gradient.to_qgradient(QRect(0, 0, 100, 60))

    assert isinstance(qt_gradient, QRadialGradient)
    assert qt_gradient.center().x() == 50.0
    assert qt_gradient.center().y() == 30.0
    assert qt_gradient.radius() == 50.0


def test_to_qgradient_unknown_type_falls_back_to_linear() -> None:
    """Test unknown gradient type falls back to linear."""
    gradient = GradientDefinition(gradient_type="unknown")

    qt_gradient = gradient.to_qgradient(QRect(0, 0, 20, 10))

    assert isinstance(qt_gradient, QLinearGradient)


def test_from_colors_creates_two_stop_gradient() -> None:
    """Test helper creates a named two-color gradient."""
    gradient = GradientDefinition.from_colors(
        "#112233",
        "#445566",
        gradient_type="radial",
        direction="horizontal",
        name="Demo Gradient",
    )

    assert gradient.name == "Demo Gradient"
    assert gradient.gradient_type == "radial"
    assert gradient.direction == "horizontal"
    assert len(gradient.stops) == 2
    assert gradient.stops[0].color.name() == "#112233"
    assert gradient.stops[1].color.name() == "#445566"


def test_renderer_setters_replace_gradients() -> None:
    """Test renderer setter methods replace the stored gradients."""
    renderer = GradientRenderer()
    dock_gradient = GradientDefinition(name="Dock")
    floating_gradient = GradientDefinition(name="Floating")
    title_gradient = GradientDefinition(name="Title")

    renderer.set_dock_area_gradient(dock_gradient)
    renderer.set_floating_container_gradient(floating_gradient)
    renderer.set_titlebar_gradient(title_gradient)

    assert renderer.dock_area_gradient is dock_gradient
    assert renderer.floating_container_gradient is floating_gradient
    assert renderer.titlebar_gradient is title_gradient


def test_renderer_paint_methods_draw_nontransparent_pixels() -> None:
    """Test renderer paint methods draw onto the image for all surfaces."""
    renderer = GradientRenderer()
    image = QImage(40, 40, QImage.Format.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    rect = QRect(0, 0, 40, 40)

    renderer.paint_dock_area_background(painter, rect)
    renderer.paint_titlebar_background(painter, rect)
    renderer.paint_floating_container_background(painter, rect)
    painter.end()

    assert image.pixelColor(10, 10).alpha() > 0


def test_override_widget_paints_gradient_background() -> None:
    """Test the override widget paints a gradient during render."""
    qapp()
    widget = GradientOverrideWidget()
    widget.resize(40, 40)
    image = QImage(widget.size(), QImage.Format.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))

    widget.render(image)

    assert image.pixelColor(5, 5).alpha() > 0


def test_get_gradient_renderer_returns_shared_instance() -> None:
    """Test global gradient renderer accessor returns shared object."""
    first = get_gradient_renderer()
    second = get_gradient_renderer()

    assert first is second


def test_custom_gradient_stop_colors_are_applied() -> None:
    """Test explicit gradient stops are preserved in the Qt gradient."""
    gradient = GradientDefinition(
        stops=[
            GradientStop(0.0, QColor("#ff0000")),
            GradientStop(0.5, QColor("#00ff00")),
            GradientStop(1.0, QColor("#0000ff")),
        ]
    )

    qt_gradient = gradient.to_qgradient(QRect(0, 0, 10, 10))
    stops = qt_gradient.stops()

    assert len(stops) == 3
    assert stops[1][0] == 0.5
    assert stops[1][1].name() == "#00ff00"
