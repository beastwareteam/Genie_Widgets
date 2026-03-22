"""Factory classes for creating various UI components from configuration.

This module provides 10 factory classes for configuration-driven UI creation:
- LayoutFactory: Window layouts and dock arrangement
- ThemeFactory: Themes, colors, and stylesheets
- PanelFactory: Dock panel configurations
- MenuFactory: Menu bars and context menus
- TabsFactory: Tab groups and tab settings
- DnDFactory: Drag and drop behavior
- ResponsiveFactory: Responsive layout breakpoints
- I18nFactory: Internationalization
- ListFactory: List widgets with nesting
- UIConfigFactory: General UI configuration
"""

from widgetsystem.factories.dnd_factory import DnDFactory
from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.layout_factory import LayoutFactory
from widgetsystem.factories.list_factory import ListFactory
from widgetsystem.factories.menu_factory import MenuFactory
from widgetsystem.factories.panel_factory import PanelFactory
from widgetsystem.factories.responsive_factory import ResponsiveFactory
from widgetsystem.factories.tabs_factory import TabsFactory
from widgetsystem.factories.theme_factory import (
    SimpleThemeProfile,
    ThemeDefinition,
    ThemeFactory,
)
from widgetsystem.factories.ui_config_factory import UIConfigFactory

__all__ = [
    # All 10 Factories
    "DnDFactory",
    "I18nFactory",
    "LayoutFactory",
    "ListFactory",
    "MenuFactory",
    "PanelFactory",
    "ResponsiveFactory",
    "TabsFactory",
    "ThemeFactory",
    "UIConfigFactory",
    # Additional exports
    "SimpleThemeProfile",
    "ThemeDefinition",
]
