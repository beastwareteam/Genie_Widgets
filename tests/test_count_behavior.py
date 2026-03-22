"""Test if dockWidgetsCount() changes after close()."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class CountTest(QMainWindow):
    """Test count behavior."""
    
    def __init__(self):
        super().__init__()
        self.dock_manager = QtAds.CDockManager(self)
        
        # Create 2 panels
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1", self)
        self.dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        
        self.dock2 = QtAds.CDockWidget(self.dock_manager, "Panel 2", self)
        self.dock2.setWidget(QWidget())
        area = self.dock1.dockAreaWidget()
        self.dock_manager.addDockWidgetTabToArea(self.dock2, area)
        
        self.area = area
        
        # Check initial count
        count = self.area.dockWidgetsCount() if hasattr(self.area, 'dockWidgetsCount') else 0
        print(f"\nInitial count: {count}")
        
        # Close panel 2
        QTimer.singleShot(1000, self.close_and_check)
        QTimer.singleShot(3000, app.quit)
    
    def close_and_check(self):
        """Close panel 2 and check count."""
        print("\n" + "="*60)
        print("Closing Panel 2...")
        self.dock2.close()
        print("Closed")
        
        # Check count IMMEDIATELY after close
        count = self.area.dockWidgetsCount() if hasattr(self.area, 'dockWidgetsCount') else 0
        print(f"Count immediately after close(): {count}")
        
        # Check after a delay
        QTimer.singleShot(500, self.delayed_check)
        print("="*60 + "\n")
    
    def delayed_check(self):
        """Check count after delay."""
        count = self.area.dockWidgetsCount() if hasattr(self.area, 'dockWidgetsCount') else 0
        print(f"Count 500ms after close(): {count}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CountTest()
    window.show()
    sys.exit(app.exec())
