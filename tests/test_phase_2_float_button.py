"""Test Phase 2 - Float Button Persistence.

Tests for FloatingStateTracker to ensure title bar buttons persist
correctly when panels are undocked and re-docked.
"""

import sys
from pathlib import Path

import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

# Import
sys.path.insert(0, str(Path(__file__).parent / "src"))

from widgetsystem.ui.floating_state_tracker import FloatingStateTracker


class Phase2TestWindow(QMainWindow):
    """Test window for Phase 2 - Float Button Persistence."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PHASE 2 TEST - Float Button Persistence")
        self.setMinimumSize(1000, 600)
        
        # QtAds Setup
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.DockAreaHasTabsMenuButton, True)
        
        self.dock_manager = QtAds.CDockManager(self)
        
        # Phase 2: Floating State Tracker
        self._floating_tracker = FloatingStateTracker(self.dock_manager)
        
        # Create test panel
        print("\n" + "="*60)
        print("STARTING: Create Test Panel")
        print("="*60)
        
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Test Panel", self)
        self.dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        
        # Schedule test actions
        QTimer.singleShot(2000, self.check_initial)
        QTimer.singleShot(4000, self.make_floating)
        QTimer.singleShot(6000, self.check_floating)
        QTimer.singleShot(8000, self.re_dock)
        QTimer.singleShot(10000, self.check_re_docked)
        QTimer.singleShot(12000, app.quit)
    
    def check_initial(self):
        """Check initial docked state."""
        print("\n" + "="*60)
        print("CHECK 1: Initial Docked State")
        print("="*60)
        self._check_float_button()
    
    def make_floating(self):
        """Make panel floating."""
        print("\n" + "="*60)
        print("ACTION: Making Panel Floating")
        print("="*60)
        
        if hasattr(self.dock1, 'setFloating'):
            self.dock1.setFloating(True)
            print("  -> Panel set to floating")
        else:
            print("  -> ERROR: setFloating method not available")
    
    def check_floating(self):
        """Check floating state."""
        print("\n" + "="*60)
        print("CHECK 2: Floating State")
        print("="*60)
        is_floating = self.dock1.isFloating() if hasattr(self.dock1, 'isFloating') else False
        print(f"  Panel isFloating: {is_floating}")
    
    def re_dock(self):
        """Re-dock the panel."""
        print("\n" + "="*60)
        print("ACTION: Re-Docking Panel")
        print("="*60)
        
        if hasattr(self.dock1, 'setFloating'):
            self.dock1.setFloating(False)
            print("  -> Panel re-docked")
        else:
            print("  -> ERROR: setFloating method not available")
    
    def check_re_docked(self):
        """Check re-docked state and float button."""
        print("\n" + "="*60)
        print("CHECK 3: Re-Docked State - Float Button Should Persist")
        print("="*60)
        
        is_floating = self.dock1.isFloating() if hasattr(self.dock1, 'isFloating') else False
        print(f"  Panel isFloating: {is_floating}")
        
        # Check if float button exists
        has_button = self._check_float_button()
        
        if has_button:
            print("\n  RESULT: PASS - Float button persists after re-docking")
        else:
            print("\n  RESULT: FAIL - Float button missing after re-docking")
        
        print("\n" + "="*60)
        print("TEST COMPLETE - Closing in 2 seconds")
        print("="*60 + "\n")
    
    def _check_float_button(self) -> bool:
        """Check if float button exists in title bar.
        
        Returns:
            True if button found, False otherwise
        """
        area = self.dock1.dockAreaWidget()
        if not area:
            print("  No dock area widget")
            return False
        
        title_bar = area.titleBar()
        if not title_bar:
            print("  No title bar")
            return False
        
        # Look for float button by objectName or class
        buttons = title_bar.findChildren(QWidget)
        float_button = None
        
        for button in buttons:
            # QtAds uses specific objectNames for buttons
            obj_name = button.objectName() if hasattr(button, 'objectName') else ""
            if 'float' in obj_name.lower() or 'detach' in obj_name.lower():
                float_button = button
                break
        
        if float_button:
            print(f"  Float button found: {float_button.objectName() if hasattr(float_button, 'objectName') else 'unnamed'}")
            return True
        else:
            print("  Float button NOT found")
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Phase2TestWindow()
    window.show()
    
    sys.exit(app.exec())
