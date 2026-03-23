"""Tests for ResponsiveController breakpoint handling."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from widgetsystem.controllers.responsive_controller import ResponsiveController


def test_responsive_controller_breakpoint_change_applies_rule() -> None:
    """Changing width updates breakpoint and applies matching rules."""
    responsive_factory = MagicMock()
    responsive_factory.load_breakpoints.return_value = [
        SimpleNamespace(id="sm", min_width=0, max_width=640),
        SimpleNamespace(id="lg", min_width=641, max_width=5000),
    ]
    responsive_factory.load_responsive_rules.return_value = [
        SimpleNamespace(id="rule_1", breakpoint="sm", panel_id="left_panel", action="hide"),
    ]

    dock = MagicMock()
    dock_controller = MagicMock()
    dock_controller.find_dock_by_title.return_value = dock

    controller = ResponsiveController(responsive_factory, dock_controller)

    applied: list[str] = []
    controller.ruleApplied.connect(lambda rule_id: applied.append(rule_id))

    controller.initialize()
    controller.update_for_width(500)

    assert controller.current_breakpoint == "sm"
    dock.toggleView.assert_called_once_with(False)
    assert "rule_1" in controller.applied_rules
    assert applied == ["rule_1"]


def test_responsive_controller_breakpoint_lookup() -> None:
    """Breakpoint lookup returns the expected breakpoint ID for widths."""
    responsive_factory = MagicMock()
    responsive_factory.load_breakpoints.return_value = [
        SimpleNamespace(id="mobile", min_width=0, max_width=767),
        SimpleNamespace(id="desktop", min_width=768, max_width=5000),
    ]
    responsive_factory.load_responsive_rules.return_value = []

    controller = ResponsiveController(responsive_factory, MagicMock())
    controller.initialize()

    assert controller.get_breakpoint_for_width(320) == "mobile"
    assert controller.get_breakpoint_for_width(1200) == "desktop"
