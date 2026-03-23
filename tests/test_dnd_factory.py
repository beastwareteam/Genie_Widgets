"""Test DnD Factory - Validates drag-and-drop factory functionality."""

from unittest.mock import MagicMock

from widgetsystem.controllers.dnd_controller import DnDController
from widgetsystem.factories.dnd_factory import DropZone
from widgetsystem.factories.dnd_factory import DnDRule


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


def test_dnd_controller_rules_allow_and_block_moves() -> None:
    """DnDController applies rules and blocks disallowed target areas."""
    factory = MagicMock()
    factory.load_drop_zones.return_value = [DropZone(id="z1", area="left")]
    factory.load_dnd_rules.return_value = [
        DnDRule(
            id="r1",
            panel_id="panel_a",
            source_area="left",
            allowed_target_areas=["center"],
        ),
    ]

    controller = DnDController(factory)
    blocked: list[tuple[str, str, str]] = []
    controller.moveBlocked.connect(
        lambda panel_id, source, target: blocked.append((panel_id, source, target))
    )

    controller.initialize()

    assert controller.is_move_allowed("panel_a", "left", "center") is True
    assert controller.is_move_allowed("panel_a", "left", "right") is False
    assert blocked == [("panel_a", "left", "right")]


def test_dnd_controller_get_allowed_targets_for_unknown_panel() -> None:
    """Unknown panels default to all dock areas as allowed targets."""
    factory = MagicMock()
    factory.load_drop_zones.return_value = []
    factory.load_dnd_rules.return_value = []

    controller = DnDController(factory)
    controller.initialize()

    targets = controller.get_allowed_targets("unknown", "left")
    assert set(targets) == {"left", "right", "center", "bottom", "top"}
