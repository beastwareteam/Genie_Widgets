"""UI components and visual layer for the WidgetSystem application."""

# Export UI components
from widgetsystem.ui.argb_color_picker import (
    ARGBColorPicker,
    ARGBColorPickerDialog,
)
from widgetsystem.ui.config_panel import ConfigurationPanel
from widgetsystem.ui.floating_state_tracker import FloatingStateTracker
from widgetsystem.ui.floating_titlebar import (
    CustomFloatingTitleBar,
    FloatingWindowPatcher,
    WindowMoveHandle,
)
from widgetsystem.ui.inlay_titlebar import InlayTitleBar, InlayTitleBarController
from widgetsystem.ui.tab_color_controller import TabColorController
from widgetsystem.ui.tab_selector_event_handler import TabSelectorEventHandler
from widgetsystem.ui.tab_selector_monitor import TabSelectorMonitor
from widgetsystem.ui.tab_selector_visibility_controller import TabSelectorVisibilityController
from widgetsystem.ui.theme_editor import (
    ARGBColorButton,
    LiveThemeEditor,
    ThemeEditorDialog,
    ThemePropertyEditor,
)
from widgetsystem.ui.visual_app import VisualMainWindow
from widgetsystem.ui.visual_layer import (
    ListsViewer,
    MenusViewer,
    PanelsViewer,
    TabsViewer,
    ViewerConfig,
    VisualDashboard,
)
from widgetsystem.ui.widget_features_editor import (
    WidgetFeaturesEditor,
    WidgetFeaturesEditorDialog,
    WidgetPropertyEditor,
)
from widgetsystem.ui.plugin_manager_dialog import PluginManagerDialog
from widgetsystem.ui.enhanced_tab_widget import EnhancedTabBar, EnhancedTabWidget
from widgetsystem.ui.tab_drop_indicator import TabDropIndicator, TabDropIndicatorController
from widgetsystem.ui.unified_tab_item import UnifiedTabItem
from widgetsystem.ui.undo_redo_widget import UndoRedoWidget, UndoRedoToolbar


__all__ = [
    "ARGBColorButton",
    "ARGBColorPicker",
    "ARGBColorPickerDialog",
    "ConfigurationPanel",
    "CustomFloatingTitleBar",
    "EnhancedTabBar",
    "EnhancedTabWidget",
    "FloatingStateTracker",
    "FloatingWindowPatcher",
    "InlayTitleBar",
    "InlayTitleBarController",
    "ListsViewer",
    "LiveThemeEditor",
    "MenusViewer",
    "PanelsViewer",
    "PluginManagerDialog",
    "TabColorController",
    "TabDropIndicator",
    "TabDropIndicatorController",
    "TabSelectorEventHandler",
    "TabSelectorMonitor",
    "TabSelectorVisibilityController",
    "TabsViewer",
    "ThemeEditorDialog",
    "ThemePropertyEditor",
    "UndoRedoToolbar",
    "UndoRedoWidget",
    "UnifiedTabItem",
    "ViewerConfig",
    "VisualDashboard",
    "VisualMainWindow",
    "WidgetFeaturesEditor",
    "WidgetFeaturesEditorDialog",
    "WidgetPropertyEditor",
    "WindowMoveHandle",
]
