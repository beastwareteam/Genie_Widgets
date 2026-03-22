"""Controller layer for WidgetSystem.

This module provides specialized controllers that encapsulate distinct
responsibilities extracted from MainWindow. Each controller manages
a single concern and communicates via Qt signals.

Architecture:
    MainWindow (Coordinator)
        |
        +-- DockController      - Dock lifecycle management
        +-- LayoutController    - Layout persistence
        +-- ThemeController     - Theme switching
        +-- DnDController       - Drag & drop rules
        +-- ResponsiveController- Breakpoint handling
        +-- ShortcutController  - Keyboard shortcuts
        +-- TabSubsystem        - Tab monitoring & colors
"""

# Controllers will be imported as they are implemented
# from widgetsystem.controllers.dock_controller import DockController
# from widgetsystem.controllers.layout_controller import LayoutController
# from widgetsystem.controllers.theme_controller import ThemeController
# from widgetsystem.controllers.dnd_controller import DnDController
# from widgetsystem.controllers.responsive_controller import ResponsiveController
# from widgetsystem.controllers.shortcut_controller import ShortcutController
# from widgetsystem.controllers.tab_subsystem import TabSubsystem

__all__: list[str] = []
