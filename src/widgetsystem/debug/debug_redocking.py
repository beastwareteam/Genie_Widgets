"""Debug script to analyze title bar state after re-docking.

This script helps identify:
1. Which buttons are present/visible in title bar after re-docking
2. Panel count in dock area after re-docking
3. Signals fired during re-docking operation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QApplication
from PySide6QtAds import CDockAreaWidget, CDockManager, CDockWidget

from widgetsystem.core.main import MainWindow


class RedockingDebugger:
    """Debugger for analyzing re-docking behavior."""

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize debugger with main window."""
        self.main_window = main_window
        self.dock_manager = main_window.dock_manager

        # Connect to all relevant signals
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect to dock manager signals to monitor events."""
        print("\n=== Connecting to Signals ===")

        # Dock widget signals
        self.dock_manager.dockWidgetAdded.connect(self._on_widget_added)
        self.dock_manager.dockWidgetRemoved.connect(self._on_widget_removed)

        # Dock area signals
        self.dock_manager.dockAreaCreated.connect(self._on_area_created)

        print("✓ Signal connections established")

    def _on_widget_added(self, dock_widget: Any) -> None:
        """Handle dock widget added signal."""
        widget_id = dock_widget.objectName()
        print(f"\n🔵 SIGNAL: dockWidgetAdded - {widget_id}")

        # Check if widget is floating or docked
        is_floating = dock_widget.isFloating()
        print(f"   Floating: {is_floating}")

        # Find dock area
        dock_area = dock_widget.dockAreaWidget()
        if dock_area:
            self._analyze_dock_area(dock_area, "after dockWidgetAdded")

    def _on_widget_removed(self, dock_widget: Any) -> None:
        """Handle dock widget removed signal."""
        widget_id = dock_widget.objectName()
        print(f"\n🔴 SIGNAL: dockWidgetRemoved - {widget_id}")

    def _on_area_created(self, dock_area: Any) -> None:
        """Handle dock area created signal."""
        print(f"\n🟢 SIGNAL: dockAreaCreated")
        self._analyze_dock_area(dock_area, "after dockAreaCreated")

    def _analyze_dock_area(self, dock_area: Any, context: str) -> None:
        """Analyze dock area state and title bar buttons."""
        print(f"\n=== Dock Area Analysis ({context}) ===")

        # Panel count
        panel_count = dock_area.dockWidgetsCount()
        print(f"Panel Count: {panel_count}")

        # List panels
        for i in range(panel_count):
            widget = dock_area.dockWidget(i)
            print(f"  - Panel {i+1}: {widget.objectName()}")

        # Title bar analysis
        title_bar = dock_area.titleBar()
        if not title_bar:
            print("⚠️  No title bar found")
            return

        print(f"\nTitle Bar: {title_bar}")
        print(f"  Visible: {title_bar.isVisible()}")
        print(f"  Enabled: {title_bar.isEnabled()}")

        # Find all buttons in title bar
        print("\n=== Title Bar Buttons ===")
        from PySide6QtAds import CTitleBarButton

        buttons = title_bar.findChildren(CTitleBarButton)
        print(f"Total buttons found: {len(buttons)}")

        for i, button in enumerate(buttons):
            obj_name = button.objectName()
            visible = button.isVisible()
            enabled = button.isEnabled()
            parent = button.parent()

            print(f"\nButton {i+1}:")
            print(f"  ObjectName: '{obj_name}'")
            print(f"  Visible: {visible}")
            print(f"  Enabled: {enabled}")
            print(f"  Parent: {parent.__class__.__name__}")
            print(f"  ToolTip: {button.toolTip()}")

            # Try to identify button type
            if obj_name == "tabsMenuButton":
                status = "✓ VISIBLE" if visible else "✗ HIDDEN"
                print(f"  → Tab Selector: {status}")
            elif "float" in obj_name.lower() or "detach" in obj_name.lower():
                status = "✓ VISIBLE" if visible else "✗ HIDDEN"
                print(f"  → Float Button: {status}")

    def analyze_current_state(self) -> None:
        """Analyze current state of all dock areas."""
        print("\n" + "="*60)
        print("=== CURRENT STATE ANALYSIS ===")
        print("="*60)

        dock_areas = self.dock_manager.openedDockAreas()
        print(f"\nTotal Dock Areas: {len(dock_areas)}")

        for i, dock_area in enumerate(dock_areas):
            print(f"\n--- Dock Area {i+1} ---")
            self._analyze_dock_area(dock_area, f"Current State Area {i+1}")


def main() -> None:
    """Run debug session."""
    import sys

    app = QApplication(sys.argv)

    # Create main window (no config_path parameter needed)
    window = MainWindow()
    window.show()

    # Create debugger
    debugger = RedockingDebugger(window)

    print("\n" + "="*60)
    print("DEBUG SESSION STARTED")
    print("="*60)
    print("\nInstructions:")
    print("1. Undock the 'left' panel (make it float)")
    print("2. Re-dock it by dragging it back")
    print("3. Watch the console output for signal events")
    print("4. Press Ctrl+C to analyze current state")
    print("="*60)

    # Schedule analysis after some time (or manually trigger with Ctrl+C)
    def analyze() -> None:
        debugger.analyze_current_state()
        # Keep running
        QTimer.singleShot(5000, analyze)

    QTimer.singleShot(3000, analyze)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
