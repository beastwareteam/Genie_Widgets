"""Test for openedDockWidgets or similar methods."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class AreaMethodsTest(QMainWindow):
    """Test area methods."""
    
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
        
        print("\n" + "="*60)
        print("Available area methods:")
        print("="*60)
        for attr in dir(self.area):
            if not attr.startswith('_') and ('dock' in attr.lower() or 'widget' in attr.lower() or 'open' in attr.lower() or 'count' in attr.lower()):
                print(f"  - {attr}")
        
        print("\n" + "="*60)
        print("BEFORE closing:")
        print("="*60)
        self._check_area()
        
        QTimer.singleShot(1000, self.close_and_check)
        QTimer.singleShot(3500, app.quit)
    
    def _check_area(self):
        """Check area."""
        if hasattr(self.area, 'dockWidgets'):
            widgets = self.area.dockWidgets()
            print(f"dockWidgets(): {len(widgets)} widgets")
            for w in widgets:
                print(f"  - {w.windowTitle()}")
        
        if hasattr(self.area, 'dockWidgetsCount'):
            print(f"dockWidgetsCount(): {self.area.dockWidgetsCount()}")
        
        if hasattr(self.area, 'openedDockWidgets'):
            widgets = self.area.openedDockWidgets()
            print(f"openedDockWidgets(): {len(widgets)} widgets")
            for w in widgets:
                print(f"  - {w.windowTitle()}")
        
        if hasattr(self.area, 'openDockWidgetsCount'):
            print(f"openDockWidgetsCount(): {self.area.openDockWidgetsCount()}")
    
    def close_and_check(self):
        """Close and check."""
        print("\n" + "="*60)
        print("Closing Panel 2...")
        self.dock2.close()
        print("Closed")
        
        print("\n" + "="*60)
        print("IMMEDIATELY AFTER closing:")
        print("="*60)
        self._check_area()
        
        # Check after processed events
        QTimer.singleShot(100, self.delayed_check)
    
    def delayed_check(self):
        """Check after delay."""
        print("\n" + "="*60)
        print("AFTER 100ms (processed events):")
        print("="*60)
        self._check_area()
        print("\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AreaMethodsTest()
    window.show()
    sys.exit(app.exec())
