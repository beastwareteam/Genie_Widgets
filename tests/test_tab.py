"""Test tab-related methods and tab bar."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class TabTest(QMainWindow):
    """Test tab methods."""
    
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
        print("BEFORE closing Panel 2:")
        print("="*60)
        self._check_widgets()
        
        QTimer.singleShot(1500, self.close_and_check)
        QTimer.singleShot(3500, app.quit)
    
    def _check_widgets(self):
        """Check widget states."""
        if hasattr(self.area, 'dockWidgets'):
            widgets = self.area.dockWidgets()
            print(f"\nTotal widgets: {len(widgets)}")
            
            for i, widget in enumerate(widgets):
                print(f"\n  Widget {i+1}: {widget.windowTitle()}")
                print(f"    isHidden(): {widget.isHidden() if hasattr(widget, 'isHidden') else 'N/A'}")
                print(f"    isClosed(): {widget.isClosed() if hasattr(widget, 'isClosed') else 'N/A'}")
                
                # Check tab widget
                if hasattr(widget, 'tabWidget'):
                    tab = widget.tabWidget()
                    if tab:
                        print(f"    tabWidget(): EXISTS")
                        if hasattr(tab, 'isVisible'):
                            print(f"      tab.isVisible(): {tab.isVisible()}")
                        if hasattr(tab, 'isHidden'):
                            print(f"      tab.isHidden(): {tab.isHidden()}")
                    else:
                        print(f"    tabWidget(): None")
                
                # Check if this is the current widget
                if hasattr(self.area, 'currentDockWidget'):
                    is_current = (self.area.currentDockWidget() == widget)
                    print(f"    isCurrentWidget: {is_current}")
    
    def close_and_check(self):
        """Close and check."""
        print("\n" + "="*60)
        print("Closing Panel 2...")
        self.dock2.close()
        print("Closed")
        
        print("\n" + "="*60)
        print("AFTER closing Panel 2:")
        print("="*60)
        self._check_widgets()
        print("\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TabTest()
    window.show()
    sys.exit(app.exec())
