"""Test DnD Factory - Validates drag-and-drop factory functionality."""

from widgetsystem.factories.dnd_factory import DropZone


def test_drop_zone_initialization():
    """Test the initialization of the DropZone dataclass."""
    drop_zone = DropZone(
        id="zone1",
        area="left",
        orientation="vertical",
        allowed_panels=["panel1", "panel2"],
        nav_zone_width=30,
        snap_enabled=False,
    )
    assert drop_zone.id == "zone1"
    assert drop_zone.area == "left"
    assert drop_zone.orientation == "vertical"
    assert drop_zone.allowed_panels == ["panel1", "panel2"]
    assert drop_zone.nav_zone_width == 30
    assert drop_zone.snap_enabled is False
    print("✅ DropZone initialization test passed.")


def test_drop_zone_defaults():
    """Test the default values of the DropZone dataclass."""
    drop_zone = DropZone(id="zone2", area="right")
    assert drop_zone.id == "zone2"
    assert drop_zone.area == "right"
    assert drop_zone.orientation == "horizontal"
    assert drop_zone.allowed_panels == []
    assert drop_zone.nav_zone_width == 20
    assert drop_zone.snap_enabled is True
    print("✅ DropZone default values test passed.")
