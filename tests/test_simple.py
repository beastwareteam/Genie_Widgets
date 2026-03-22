"""Simple Test - Tab Selector Visibility (No Unicode)."""

import sys
from pathlib import Path

import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

# Import
sys.path.insert(0, str(Path(__file__).parent / "src"))

from widgetsystem.ui.tab_selector_monitor import TabSelectorMonitor
from widgetsystem.ui.tab_selector_event_handler import TabSelectorEventHandler
from widgetsystem.ui.tab_selector_visibility_controller import TabSelectorVisibilityController


class SimpleTestWindow(QMainWindow):
    """Simple Test Window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIMPLE TEST - Tab Selector")
        self.setMinimumSize(1000, 600)
        
        # QtAds Setup
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.DockAreaHasTabsMenuButton, True)
        
        self.dock_manager = QtAds.CDockManager(self)
        
        # Phase 1: Tab Selector Control
        self._tab_monitor = TabSelectorMonitor()
        self._tab_event_handler = TabSelectorEventHandler(self.dock_manager, self._tab_monitor)
        self._tab_visibility = TabSelectorVisibilityController(self._tab_monitor)
        
        # Start with 1 panel
        print("\n" + "="*60)
        print("STARTING: Create 1 Panel")
        print("="*60)
        
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1", self)
        self.dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        
        # Schedule actions
        QTimer.singleShot(2000, self.check_one_panel)
        QTimer.singleShot(4000, self.add_panel2)
        QTimer.singleShot(6000, self.check_two_panels)
        QTimer.singleShot(8000, self.remove_panel2)
        QTimer.singleShot(10000, self.check_one_panel_again)
        QTimer.singleShot(12000, app.quit)
    
    def check_one_panel(self):
        """Check with 1 panel."""
        print("\n" + "="*60)
        print("CHECK: 1 Panel - Button should be HIDDEN")
        print("="*60)
        self._check_button_state(expected_visible=False, expected_count=1)
    
    def add_panel2(self):
        """Add second panel."""
        print("\n" + "="*60)
        print("ACTION: Adding Panel 2 as Tab")
        print("="*60)
        
        self.dock2 = QtAds.CDockWidget(self.dock_manager, "Panel 2", self)
        self.dock2.setWidget(QWidget())
        
        area = self.dock1.dockAreaWidget()
        if area:
            self.dock_manager.addDockWidgetTabToArea(self.dock2, area)
            print("  -> Panel 2 added to same area")
        else:
            print("  -> ERROR: Could not find area")
    
    def check_two_panels(self):
        """Check with 2 panels."""
        print("\n" + "="*60)
        print("CHECK: 2 Panels - Button should be VISIBLE")
        print("="*60)
        self._check_button_state(expected_visible=True, expected_count=2)
    
    def remove_panel2(self):
        """Remove second panel."""
        print("\n" + "="*60)
        print("ACTION: Closing Panel 2")
        print("="*60)
        
        if hasattr(self, 'dock2'):
            self.dock2.close()
            print("  -> Panel 2 closed")
    
    def check_one_panel_again(self):
        """Check with 1 panel again."""
        print("\n" + "="*60)
        print("CHECK: 1 Panel Again - Button should be HIDDEN")
        print("="*60)
        self._check_button_state(expected_visible=False, expected_count=1)
        
        print("\n" + "="*60)
        print("TEST COMPLETE - Closing in 2 seconds")
        print("="*60 + "\n")
    
    def _check_button_state(self, expected_visible, expected_count):
        """Check button visibility state."""
        areas = self.dock_manager.openedDockAreas()
        
        for i, area in enumerate(areas):
            tab_count = area.dockWidgetsCount() if hasattr(area, 'dockWidgetsCount') else 0
            title_bar = area.titleBar()
            
            if title_bar:
                button = title_bar.findChild(QWidget, "tabsMenuButton")
                
                if button:
                    is_visible = button.isVisible()
                    
                    print(f"  Area {i}:")
                    print(f"    Tab Count: {tab_count}")
                    print(f"    Button Visible: {is_visible}")
                    print(f"    Expected Visible: {expected_visible}")
                    print(f"    Expected Count: {expected_count}")
                    
                    if tab_count == expected_count and is_visible == expected_visible:
                        print(f"    RESULT: PASS")
                    else:
                        print(f"    RESULT: FAIL")
                else:
                    print(f"  Area {i}: Button not found!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTestWindow()
    window.show()
    
    sys.exit(app.exec())
