"""Type-safe enumerations for WidgetSystem.

This module replaces magic strings with typed enums to catch errors at
compile time rather than runtime. All enums inherit from str for
JSON serialization compatibility.
"""

from enum import Enum


class DockArea(str, Enum):
    """Valid dock widget areas in the layout."""

    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    BOTTOM = "bottom"
    TOP = "top"


class ActionName(str, Enum):
    """Named actions that can be triggered via menu, toolbar, or shortcuts."""

    # Layout actions
    SAVE_LAYOUT = "save_layout"
    LOAD_LAYOUT = "load_layout"
    RESET_LAYOUT = "reset_layout"

    # Dock actions
    SAVE_DOCK = "save_dock"
    LOAD_DOCK = "load_dock"
    NEW_DOCK = "new_dock"
    FLOAT_ALL = "float_all"
    DOCK_ALL = "dock_all"
    CLOSE_ALL = "close_all"

    # Editor/Dialog actions
    SHOW_THEME_EDITOR = "show_theme_editor"
    SHOW_COLOR_PICKER = "show_color_picker"
    SHOW_WIDGET_FEATURES_EDITOR = "show_widget_features_editor"
    SHOW_PLUGIN_MANAGER = "show_plugin_manager"

    # Tab operations (CLI automation)
    MOVE_TAB = "move_tab"
    NEST_TAB = "nest_tab"
    UNNEST_TAB = "unnest_tab"
    FLOAT_TAB = "float_tab"
    CLOSE_TAB = "close_tab"
    ACTIVATE_TAB = "activate_tab"


class ResponsiveAction(str, Enum):
    """Actions applied to panels at responsive breakpoints."""

    HIDE = "hide"
    SHOW = "show"
    COLLAPSE = "collapse"


class RuleAction(str, Enum):
    """Actions for DnD rules."""

    ALLOW = "allow"
    DENY = "deny"
    RESTRICT = "restrict"


class ThemeMode(str, Enum):
    """Theme color modes."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class PanelState(str, Enum):
    """State of a dock panel."""

    DOCKED = "docked"
    FLOATING = "floating"
    HIDDEN = "hidden"
    TABBED = "tabbed"
