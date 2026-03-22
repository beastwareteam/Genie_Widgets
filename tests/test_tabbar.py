"""Test tab bar directly."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class TabBarTest(QMainWindow):
    """Test tab bar."""
    
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
        print("Checking tab bar...")
        print("="*60)
        
        if hasattr(self.area, 'tabBar'):
            print("area.tabBar() method exists")
        else:
            print("NO area.tabBar() method")
        
        # Find tab bar via children
        for child in self.area.findChildren(QWidget):
            class_name = child.__class__.__name__
            if 'tab' in class_name.lower() or 'Tab' in class_name:
                print(f"Found: {class_name}")
                if hasattr(child, 'count'):
                    count = child.count()
                    print(f"  count(): {count}")
                if hasattr(child, 'tabCount'):
                    count = child.tabCount()
                    print(f"  tabCount(): {count}")
        
        print("\n" + "="*60)
        print("BEFORE closing:")
        print("="*60)
        self._check_tabs()
        
        QTimer.singleShot(1500, self.close_and_check)
        QTimer.singleShot(3500, app.quit)
    
    def _check_tabs(self):
        """Check tab count."""
        # Try to find tab bar and count visible tabs
        tab_bars = self.area.findChildren(QWidget)
        for tab_bar in tab_bars:
            if 'CDockArea' in tab_bar.__class__.__name__ and 'Tab' in tab_bar.__class__.__name__:
                print(f"\nFound tab bar: {tab_bar.__class__.__name__}")
                if hasattr(tab_bar, 'count'):
                    print(f"  count(): {tab_bar.count()}")
                if hasattr(tab_bar, 'visibleCount'):
                    print(f"  visibleCount(): {tab_bar.visibleCount()}")
    
    def close_and_check(self):
        """Close and check."""
        print("\n" + "="*60)
        print("Closing Panel 2...")
        self.dock2.close()
        print("Closed")
        
        # Small delay for UI update
        QTimer.singleShot(100, self.delayed_check)
    
    def delayed_check(self):
        """Check after delay."""
        print("\n" + "="*60)
        print("AFTER closing (with delay):")
        print("="*60)
        self._check_tabs()
        print("\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TabBarTest()
    window.show()
    sys.exit(app.exec())
