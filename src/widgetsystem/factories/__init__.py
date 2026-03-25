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
- ComponentRegistry: Registry for tab content widgets
"""

from widgetsystem.factories.component_registry import (
    ComponentRegistry,
    get_component_registry,
)
from widgetsystem.factories.dnd_factory import DnDFactory
from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.layout_factory import LayoutFactory
from widgetsystem.factories.list_factory import ListFactory
from widgetsystem.factories.menu_factory import MenuFactory
from widgetsystem.factories.panel_factory import PanelFactory
from widgetsystem.factories.responsive_factory import ResponsiveFactory
from widgetsystem.factories.tabs_factory import Tab, TabGroup, TabsFactory
from widgetsystem.factories.theme_factory import (
    SimpleThemeProfile,
    TabColors,
    ThemeDefinition,
    ThemeFactory,
)
from widgetsystem.factories.ui_config_factory import UIConfigFactory
from widgetsystem.factories.ui_dimensions_factory import (
    CloseButtonDimensions,
    DockDimensions,
    TabsDimensions,
    TitlebarDimensions,
    ToolbarDimensions,
    UIDimensions,
    UIDimensionsFactory,
    WindowDimensions,
)
from widgetsystem.factories.qss_factory import QSSFactory

__all__ = [
    # All Factories + ComponentRegistry
    "ComponentRegistry",
    "DnDFactory",
    "I18nFactory",
    "LayoutFactory",
    "ListFactory",
    "MenuFactory",
    "PanelFactory",
    "QSSFactory",
    "ResponsiveFactory",
    "TabsFactory",
    "ThemeFactory",
    "UIConfigFactory",
    "UIDimensionsFactory",
    # Dimension dataclasses
    "CloseButtonDimensions",
    "DockDimensions",
    "TabsDimensions",
    "TitlebarDimensions",
    "ToolbarDimensions",
    "UIDimensions",
    "WindowDimensions",
    # Additional exports
    "get_component_registry",
    "SimpleThemeProfile",
    "Tab",
    "TabColors",
    "TabGroup",
    "ThemeDefinition",
]
