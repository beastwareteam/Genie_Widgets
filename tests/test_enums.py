"""Tests for type-safe enums in widgetsystem.enums."""

from widgetsystem.enums import (
    ActionName,
    DockArea,
    PanelState,
    ResponsiveAction,
    RuleAction,
    ThemeMode,
)


def test_dock_area_values_are_stable() -> None:
    """DockArea values should match expected serialized strings."""
    assert DockArea.LEFT.value == "left"
    assert DockArea.RIGHT.value == "right"
    assert DockArea.CENTER.value == "center"
    assert DockArea.BOTTOM.value == "bottom"
    assert DockArea.TOP.value == "top"


def test_action_name_and_rule_action_membership() -> None:
    """String-to-enum conversion should work for configured action names."""
    assert ActionName("save_layout") is ActionName.SAVE_LAYOUT
    assert ActionName("show_plugin_manager") is ActionName.SHOW_PLUGIN_MANAGER
    assert RuleAction("allow") is RuleAction.ALLOW
    assert RuleAction("restrict") is RuleAction.RESTRICT


def test_theme_mode_panel_state_and_responsive_action_are_comparable() -> None:
    """Enums should behave as string enums for comparison and serialization."""
    assert ThemeMode.DARK == "dark"
    assert ThemeMode("system") is ThemeMode.SYSTEM
    assert PanelState("floating") is PanelState.FLOATING
    assert ResponsiveAction.HIDE.value == "hide"
