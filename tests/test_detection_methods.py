"""Test which method correctly detects closed widgets."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class MethodTest(QMainWindow):
    """Test detection methods."""
    
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
        self._check_all_widgets()
        
        # Close panel 2
        QTimer.singleShot(1000, self.close_and_check)
        QTimer.singleShot(3000, app.quit)
    
    def _check_all_widgets(self):
        """Check all widgets."""
        if hasattr(self.area, 'dockWidgets'):
            widgets = self.area.dockWidgets()
            print(f"Total widgets: {len(widgets)}")
            for i, widget in enumerate(widgets):
                self._check_widget(i+1, widget)
    
    def _check_widget(self, num, widget):
        """Check a single widget."""
        print(f"\n  Widget {num}: {widget.windowTitle() if hasattr(widget, 'windowTitle') else widget}")
        
        if hasattr(widget, 'isClosed'):
            print(f"    isClosed(): {widget.isClosed()}")
        else:
            print(f"    isClosed(): NOT AVAILABLE")
        
        if hasattr(widget, 'isVisible'):
            print(f"    isVisible(): {widget.isVisible()}")
        else:
            print(f"    isVisible(): NOT AVAILABLE")
        
        if hasattr(widget, 'isHidden'):
            print(f"    isHidden(): {widget.isHidden()}")
        else:
            print(f"    isHidden(): NOT AVAILABLE")
        
        if hasattr(widget, 'features'):
            print(f"    features(): {widget.features()}")
    
    def close_and_check(self):
        """Close panel 2 and check."""
        print("\n" + "="*60)
        print("Closing Panel 2...")
        self.dock2.close()
        print("Closed")
        
        print("\n" + "="*60)
        print("AFTER closing Panel 2:")
        print("="*60)
        self._check_all_widgets()
        print("\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MethodTest()
    window.show()
    sys.exit(app.exec())
