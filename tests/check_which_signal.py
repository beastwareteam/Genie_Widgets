"""Test which signals fire when closing a dock widget."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class SignalTestWindow(QMainWindow):
    """Test window."""
    
    def __init__(self):
        super().__init__()
        self.dock_manager = QtAds.CDockManager(self)
        
        # Connect ALL possible removal signals
        print("\nConnecting signals...")
        
        if hasattr(self.dock_manager, 'dockWidgetRemoved'):
            print("  - Connected: dockWidgetRemoved")
            self.dock_manager.dockWidgetRemoved.connect(
                lambda w: print(f"    [SIGNAL FIRED] dockWidgetRemoved: {w.windowTitle() if hasattr(w, 'windowTitle') else w}")
            )
        else:
            print("  - NOT AVAILABLE: dockWidgetRemoved")
        
        if hasattr(self.dock_manager, 'dockWidgetAboutToBeRemoved'):
            print("  - Connected: dockWidgetAboutToBeRemoved")
            self.dock_manager.dockWidgetAboutToBeRemoved.connect(
                lambda w: print(f"    [SIGNAL FIRED] dockWidgetAboutToBeRemoved: {w.windowTitle() if hasattr(w, 'windowTitle') else w}")
            )
        else:
            print("  - NOT AVAILABLE: dockWidgetAboutToBeRemoved")
        
        if hasattr(self.dock_manager, 'dockAreaRemoved'):
            print("  - Connected: dockAreaRemoved")
            self.dock_manager.dockAreaRemoved.connect(
                lambda a: print(f"    [SIGNAL FIRED] dockAreaRemoved: {a}")
            )
        else:
            print("  - NOT AVAILABLE: dockAreaRemoved")
        
        # Create widgets
        print("\nCreating 2 test panels...")
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1", self)
        self.dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        
        self.dock2 = QtAds.CDockWidget(self.dock_manager, "Panel 2", self)
        self.dock2.setWidget(QWidget())
        area = self.dock1.dockAreaWidget()
        self.dock_manager.addDockWidgetTabToArea(self.dock2, area)
        
        print("  Panels created")
        
        # Schedule close
        QTimer.singleShot(1000, self.close_panel)
        QTimer.singleShot(4000, app.quit)
    
    def close_panel(self):
        """Close panel 2."""
        print("\n" + "="*60)
        print("TEST 1: Closing Panel 2 with .close()...")
        print("="*60)
        self.dock2.close()
        print("close() called - Check for signals above")
        print("="*60 + "\n")
        
        # Try removeDockWidget
        QTimer.singleShot(1000, self.remove_panel)
    
    def remove_panel(self):
        """Remove panel 1."""
        print("\n" + "="*60)
        print("TEST 2: Removing Panel 1 with removeDockWidget()...")
        print("="* 60)
        self.dock_manager.removeDockWidget(self.dock1)
        print("removeDockWidget() called - Check for signals above")
        print("="*60 + "\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalTestWindow()
    window.show()
    sys.exit(app.exec())
