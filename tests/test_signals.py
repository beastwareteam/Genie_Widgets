"""List all CDockManager signals."""

import sys
from pathlib import Path

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class SignalTestWindow(QMainWindow):
    """Test window to list signals."""
    
    def __init__(self):
        super().__init__()
        self.dock_manager = QtAds.CDockManager(self)
        
        print("\n" + "="*60)
        print("CDockManager Available Signals:")
        print("="* 60)
        
        # List all attributes
        for attr_name in dir(self.dock_manager):
            attr = getattr(self.dock_manager, attr_name)
            # Check if it looks like a signal (has connect method)
            if hasattr(attr, 'connect') and not callable(attr):
                print(f"  - {attr_name}")
        
        print("="*60 + "\n")
        
        # Create test widget and connect signals
        print("Connecting to signals and testing...")
        
        if hasattr(self.dock_manager, 'dockWidgetRemoved'):
            self.dock_manager.dockWidgetRemoved.connect(
                lambda w: print(f"  [Signal] dockWidgetRemoved: {w}")
            )
        
        if hasattr(self.dock_manager, 'dockWidgetAboutToBeRemoved'):
            self.dock_manager.dockWidgetAboutToBeRemoved.connect(
                lambda w: print(f"  [Signal] dockWidgetAboutToBeRemoved: {w}")
            )
            
        if hasattr(self.dock_manager, 'dockAreaRemoved'):
            self.dock_manager.dockAreaRemoved.connect(
                lambda a: print(f"  [Signal] dockAreaRemoved: {a}")
            )
        
        # Create and add widget
        print("\n1. Creating widget...")
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Test Panel", self)
        self.dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        print("   Widget created and added")
        
        # Close it
        print("\n2. Closing widget...")
        self.dock1.close()
        print("   Widget closed")
        
        print("\n3. Done - Check output above\n")
        app.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalTestWindow()
    window.show()
    sys.exit(app.exec())
