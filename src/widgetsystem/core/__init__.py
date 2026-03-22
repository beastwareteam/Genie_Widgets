"""Core functionality for the WidgetSystem application."""

# Export main application classes
# from .main import ...
# from .main_visual import ...

# Export theme system
from widgetsystem.core.gradient_system import (
    GradientDefinition,
    GradientRenderer,
    GradientStop,
    get_gradient_renderer,
)
from widgetsystem.core.plugin_system import (
    PluginManager,
    PluginRegistry,
)
from widgetsystem.core.theme_manager import Theme, ThemeManager
from widgetsystem.core.undo_redo import (
    CallbackCommand,
    Command,
    CompositeCommand,
    ConfigurationUndoManager,
    DictChangeCommand,
    ListChangeCommand,
    PropertyChangeCommand,
    UndoRedoManager,
)
from widgetsystem.core.config_io import (
    BackupManager,
    ConfigMetadata,
    ConfigurationExporter,
    ConfigurationImporter,
    ExportOptions,
    ImportOptions,
)
from widgetsystem.core.template_system import (
    ConfigurationTemplate,
    TemplateManager,
    TemplateMetadata,
)
from widgetsystem.core.theme_profile import ThemeColors, ThemeProfile


__all__ = [
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
]
