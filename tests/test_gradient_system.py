"""Test Gradient System - Validates gradient-related classes and functionality."""

from PySide6.QtGui import QColor

from widgetsystem.core.gradient_system import GradientDefinition, GradientStop


def test_gradient_stop():
    """Test the GradientStop dataclass."""
    stop = GradientStop(position=0.5, color=QColor("#ff0000"))
    assert stop.position == 0.5
    assert stop.color.name() == "#ff0000"
    print("✅ GradientStop test passed.")


def test_gradient_definition_initialization():
    """Test the initialization of GradientDefinition."""
    stops = [
        GradientStop(position=0.0, color=QColor("#ff0000")),
        GradientStop(position=1.0, color=QColor("#0000ff")),
    ]
    gradient = GradientDefinition(gradient_type="linear", stops=stops, direction="horizontal")

    assert gradient.gradient_type == "linear"
    assert len(gradient.stops) == 2
    assert gradient.stops[0].color.name() == "#ff0000"
    assert gradient.stops[1].color.name() == "#0000ff"
    assert gradient.direction == "horizontal"
    print("✅ GradientDefinition initialization test passed.")
