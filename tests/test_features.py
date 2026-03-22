"""Test widget features after close."""

import sys
import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class FeaturesTest(QMainWindow):
    """Test features."""
    
    def __init__(self):
        super().__init__()
        self.dock_manager = QtAds.CDockManager(self)
        
        #Create panels
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1", self)
        self.dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        
        self.dock2 = QtAds.CDockWidget(self.dock_manager, "Panel 2", self)
        self.dock2.setWidget(QWidget())
        area = self.dock1.dockAreaWidget()
        self.dock_manager.addDockWidgetTabToArea(self.dock2, area)
        
        # List available feature constants
        print("\n" + "="*60)
        print("CDockWidget.DockWidgetFeature constants:")
        print("="*60)
        if hasattr(QtAds.CDockWidget, 'DockWidgetFeature'):
            for attr in dir(QtAds.CDockWidget.DockWidgetFeature):
                if not attr.startswith('_'):
                    val = getattr(QtAds.CDockWidget.DockWidgetFeature, attr)
                    print(f"  - {attr} = {val}")
        elif hasattr(QtAds.CDockWidget, 'eDockWidgetFeature'):
            for attr in dir(QtAds.CDockWidget.eDockWidgetFeature):
                if not attr.startswith('_'):
                    val = getattr(QtAds.CDockWidget.eDockWidgetFeature, attr)
                    print(f"  - {attr} = {val}")
        
        print("\n" + "="*60)
        print("BEFORE closing Panel 2:")
        print("="*60)
        self._check_widget("Panel 2", self.dock2)
        
        QTimer.singleShot(1000, self.close_and_check)
        QTimer.singleShot(3000, app.quit)
    
    def _check_widget(self, name, widget):
        """Check widget properties."""
        print(f"\n{name}:")
        
        if hasattr(widget, 'features'):
            print(f"  features(): {widget.features()}")
        
        if hasattr(widget, 'isClosed'):
            print(f"  isClosed(): {widget.isClosed()}")
        
        if hasattr(widget, 'isVisible'):
            print(f"  isVisible(): {widget.isVisible()}")
        
        if hasattr(widget, 'isHidden'):
            print(f"  isHidden(): {widget.isHidden()}")
        
        if hasattr(widget, 'testWidgetFeature'):
            # Try known features
            if hasattr(QtAds.CDockWidget, 'DockWidgetClosable'):
                closable = widget.testWidgetFeature(QtAds.CDockWidget.DockWidgetClosable)
                print(f"  testWidgetFeature(DockWidgetClosable): {closable}")
        
        # Check if widget() still exists
        if hasattr(widget, 'widget'):
            inner_widget = widget.widget()
            if inner_widget:
                print(f"  widget(): EXISTS (visible={inner_widget.isVisible()})")
            else:
                print(f"  widget(): None")
    
    def close_and_check(self):
        """Close and check."""
        print("\n" + "="*60)
        print("Closing Panel 2...")
        self.dock2.close()
        print("Closed")
        
        print("\n" + "="*60)
        print("AFTER closing Panel 2:")
        print("="*60)
        self._check_widget("Panel 2", self.dock2)
        print("\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FeaturesTest()
    window.show()
    sys.exit(app.exec())
