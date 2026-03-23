"""Test widget-level signals when closing."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class WidgetSignalTest(QMainWindow):
    """Test widget signals."""
    
    def __init__(self):
        super().__init__()
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.DockAreaHasTabsMenuButton, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True)
        
        self.dock_manager = QtAds.CDockManager(self)
        
        print("\nCreating test panel...")
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1", self)
        self.dock1.setWidget(QWidget())
        
        # Connect widget-level signals
        print("Connecting to CDockWidget signals...")
        
        if hasattr(self.dock1, 'closed'):
            print("  - Connected: dock1.closed")
            self.dock1.closed.connect(lambda: print("    [SIGNAL] dock1.closed"))
        else:
            print("  - NOT AVAILABLE: closed")
        
        if hasattr(self.dock1, 'viewToggled'):
            print("  - Connected: dock1.viewToggled")
            self.dock1.viewToggled.connect(lambda visible: print(f"    [SIGNAL] dock1.viewToggled: visible={visible}"))
        else:
            print("  - NOT AVAILABLE: viewToggled")
        
        if hasattr(self.dock1, 'closeRequested'):
            print("  - Connected: dock1.closeRequested")
            self.dock1.closeRequested.connect(lambda: print("    [SIGNAL] dock1.closeRequested"))
        else:
            print("  - NOT AVAILABLE: closeRequested")
        
        if hasattr(self.dock1, 'visibilityChanged'):
            print("  - Connected: dock1.visibilityChanged")
            self.dock1.visibilityChanged.connect(lambda visible: print(f"    [SIGNAL] dock1.visibilityChanged: visible={visible}"))
        else:
            print("  - NOT AVAILABLE: visibilityChanged")
        
        # Also try standard QObject destroyed signal
        self.dock1.destroyed.connect(lambda: print("    [SIGNAL] dock1.destroyed"))
        print("  - Connected: destroyed (QObject standard signal)")
        
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        print("  Panel added to dock\n")
        
        QTimer.singleShot(1500, self.close_dock)
        QTimer.singleShot(3000, app.quit)
    
    def close_dock(self):
        """Close the dock widget."""
        print("="*60)
        print("Calling dock1.close()...")
        print("="*60)
        self.dock1.close()
        print("close() called - check signals above")
        print("="*60 + "\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WidgetSignalTest()
    window.show()
    sys.exit(app.exec())
