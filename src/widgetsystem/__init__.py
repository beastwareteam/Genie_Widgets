"""WidgetSystem - Modular, configuration-driven GUI application with PySide6.

A flexible widget system using PySide6 Advanced Docking System.
"""

__version__ = "0.1.0"
__author__ = "WidgetSystem Team"

# Re-export main components for easier imports
from widgetsystem.core import (
    GradientDefinition,
    GradientRenderer,
    GradientStop,
    PluginManager,
    PluginRegistry,
    Theme,
    ThemeColors,
    ThemeManager,
    ThemeProfile,
    get_gradient_renderer,
)
from widgetsystem.factories.layout_factory import LayoutFactory
from widgetsystem.factories.theme_factory import ThemeFactory
from widgetsystem.ui import (
    ARGBColorButton,
    ARGBColorPicker,
    ARGBColorPickerDialog,
    ConfigurationPanel,
    FloatingStateTracker,
    InlayTitleBar,
    InlayTitleBarController,
    LiveThemeEditor,
    TabColorController,
    TabSelectorEventHandler,
    TabSelectorMonitor,
    TabSelectorVisibilityController,
    ThemeEditorDialog,
    ThemePropertyEditor,
    VisualDashboard,
    VisualMainWindow,
    WidgetFeaturesEditor,
    WidgetFeaturesEditorDialog,
    WidgetPropertyEditor,
)

__all__ = [
    # Core
    "GradientDefinition",
    "GradientRenderer",
    "GradientStop",
    "PluginManager",
    "PluginRegistry",
    "Theme",
    "ThemeColors",
    "ThemeManager",
    "ThemeProfile",
    "get_gradient_renderer",
    # Key Factories
    "LayoutFactory",
    "ThemeFactory",
    # UI Components
    "ARGBColorButton",
    "ARGBColorPicker",
    "ARGBColorPickerDialog",
    "ConfigurationPanel",
    "FloatingStateTracker",
    "InlayTitleBar",
    "InlayTitleBarController",
    "LiveThemeEditor",
    "TabColorController",
    "TabSelectorEventHandler",
    "TabSelectorMonitor",
    "TabSelectorVisibilityController",
    "ThemeEditorDialog",
    "ThemePropertyEditor",
    "VisualDashboard",
    "VisualMainWindow",
    "WidgetFeaturesEditor",
    "WidgetFeaturesEditorDialog",
    "WidgetPropertyEditor",
]
