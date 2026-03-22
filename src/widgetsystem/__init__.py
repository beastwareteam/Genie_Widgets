"""WidgetSystem - Modular, configuration-driven GUI application with PySide6.

A comprehensive widget system using PySide6 Advanced Docking System (QtAds).

Core Systems:
- Plugin System: Dynamic factory registration with hot-reload
- Undo/Redo: Command pattern for reversible operations
- Import/Export: Configuration backup and restore
- Template System: Pre-built configuration templates
- Theme System: ARGB colors, gradients, profiles

Factories (10):
- LayoutFactory, ThemeFactory, PanelFactory, MenuFactory, TabsFactory
- DnDFactory, ResponsiveFactory, I18nFactory, ListFactory, UIConfigFactory

UI Components:
- InlayTitleBar, FloatingTitlebar, ARGBColorPicker, ThemeEditor
- WidgetFeaturesEditor, ConfigurationPanel, TabSelector components
"""

__version__ = "1.0.0"
__author__ = "WidgetSystem Team"

# =============================================================================
# Core Systems
# =============================================================================
from widgetsystem.core import (
    # Gradient System
    GradientDefinition,
    GradientRenderer,
    GradientStop,
    get_gradient_renderer,
    # Plugin System
    PluginManager,
    PluginRegistry,
    # Theme System
    Theme,
    ThemeColors,
    ThemeManager,
    ThemeProfile,
    # Undo/Redo System
    CallbackCommand,
    Command,
    CompositeCommand,
    ConfigurationUndoManager,
    DictChangeCommand,
    ListChangeCommand,
    PropertyChangeCommand,
    UndoRedoManager,
    # Config Import/Export
    BackupManager,
    ConfigMetadata,
    ConfigurationExporter,
    ConfigurationImporter,
    ExportOptions,
    ImportOptions,
    # Template System
    ConfigurationTemplate,
    TemplateManager,
    TemplateMetadata,
)

# =============================================================================
# Factory Classes (all 10)
# =============================================================================
from widgetsystem.factories import (
    DnDFactory,
    I18nFactory,
    LayoutFactory,
    ListFactory,
    MenuFactory,
    PanelFactory,
    ResponsiveFactory,
    TabsFactory,
    ThemeFactory,
    UIConfigFactory,
)

# =============================================================================
# UI Components
# =============================================================================
from widgetsystem.ui import (
    # Color Picker
    ARGBColorButton,
    ARGBColorPicker,
    ARGBColorPickerDialog,
    # Configuration
    ConfigurationPanel,
    # Floating Windows
    CustomFloatingTitleBar,
    FloatingStateTracker,
    FloatingWindowPatcher,
    WindowMoveHandle,
    # Titlebar
    InlayTitleBar,
    InlayTitleBarController,
    # Theme Editor
    LiveThemeEditor,
    ThemeEditorDialog,
    ThemePropertyEditor,
    # Tab System
    TabColorController,
    TabSelectorEventHandler,
    TabSelectorMonitor,
    TabSelectorVisibilityController,
    # Main Windows
    VisualDashboard,
    VisualMainWindow,
    # Widget Editor
    WidgetFeaturesEditor,
    WidgetFeaturesEditorDialog,
    WidgetPropertyEditor,
    # Config Viewers
    ListsViewer,
    MenusViewer,
    PanelsViewer,
    TabsViewer,
    ViewerConfig,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    # ==========================================================================
    # Core Systems
    # ==========================================================================
    # Gradient System
    "GradientDefinition",
    "GradientRenderer",
    "GradientStop",
    "get_gradient_renderer",
    # Plugin System
    "PluginManager",
    "PluginRegistry",
    # Theme System
    "Theme",
    "ThemeColors",
    "ThemeManager",
    "ThemeProfile",
    # Undo/Redo System
    "CallbackCommand",
    "Command",
    "CompositeCommand",
    "ConfigurationUndoManager",
    "DictChangeCommand",
    "ListChangeCommand",
    "PropertyChangeCommand",
    "UndoRedoManager",
    # Config Import/Export
    "BackupManager",
    "ConfigMetadata",
    "ConfigurationExporter",
    "ConfigurationImporter",
    "ExportOptions",
    "ImportOptions",
    # Template System
    "ConfigurationTemplate",
    "TemplateManager",
    "TemplateMetadata",
    # ==========================================================================
    # Factory Classes (all 10)
    # ==========================================================================
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
    # ==========================================================================
    # UI Components
    # ==========================================================================
    # Color Picker
    "ARGBColorButton",
    "ARGBColorPicker",
    "ARGBColorPickerDialog",
    # Configuration
    "ConfigurationPanel",
    # Floating Windows
    "CustomFloatingTitleBar",
    "FloatingStateTracker",
    "FloatingWindowPatcher",
    "WindowMoveHandle",
    # Titlebar
    "InlayTitleBar",
    "InlayTitleBarController",
    # Theme Editor
    "LiveThemeEditor",
    "ThemeEditorDialog",
    "ThemePropertyEditor",
    # Tab System
    "TabColorController",
    "TabSelectorEventHandler",
    "TabSelectorMonitor",
    "TabSelectorVisibilityController",
    # Main Windows
    "VisualDashboard",
    "VisualMainWindow",
    # Widget Editor
    "WidgetFeaturesEditor",
    "WidgetFeaturesEditorDialog",
    "WidgetPropertyEditor",
    # Config Viewers
    "ListsViewer",
    "MenusViewer",
    "PanelsViewer",
    "TabsViewer",
    "ViewerConfig",
]
