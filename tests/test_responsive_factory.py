"""Test ResponsiveFactory - Validates responsive design functionality."""

from widgetsystem.factories.responsive_factory import Breakpoint


def test_breakpoint_initialization():
    """Test the initialization of the Breakpoint dataclass."""
    breakpoint = Breakpoint(id="bp1", min_width=768, max_width=1024, name="Tablet")
    assert breakpoint.id == "bp1"
    assert breakpoint.min_width == 768
    assert breakpoint.max_width == 1024
    assert breakpoint.name == "Tablet"
    print("✅ Breakpoint initialization test passed.")
