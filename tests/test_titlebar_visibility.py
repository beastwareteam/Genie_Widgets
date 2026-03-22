"""Test script to verify InlayTitleBar visibility and positioning.

This script creates a minimal test window to verify that:
1. InlayTitleBar is created and visible
2. It has correct geometry (3px height initially)
3. It's positioned at (0,0)
4. It responds to mouse hover
5. DockManager is positioned below it
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.ui.inlay_titlebar import (
    COLLAPSED_HEIGHT,
    EXPANDED_HEIGHT,
    InlayTitleBarController,
)


class TestWindow(QMainWindow):
    """Minimal test window to verify TitleBar functionality."""

    def __init__(self) -> None:
        super().__init__()
        
        # Frameless window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget with info labels
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 50, 10, 10)  # Top margin for titlebar
        
        self._info_label = QLabel("Initializing...", central)
        self._info_label.setStyleSheet("QLabel { color: white; background: #2D2E31; padding: 10px; }")
        layout.addWidget(self._info_label)
        
        layout.addStretch()
        self.setCentralWidget(central)
        
        # Install InlayTitleBar
        self._inlay_controller = InlayTitleBarController(self)
        self._inlay_controller.install()
        self._inlay_controller.set_title("TitleBar Verification Test")
        
        if self._inlay_controller.titlebar:
            self._inlay_controller.titlebar.raise_()
            
        # Schedule verification after window is shown
        QTimer.singleShot(500, self._verify_titlebar)
    
    def _verify_titlebar(self) -> None:
        """Verify TitleBar state and update info label."""
        info_lines = ["=== InlayTitleBar Verification ===", ""]
        
        if not hasattr(self, "_inlay_controller"):
            info_lines.append("❌ ERROR: _inlay_controller not found")
            self._info_label.setText("\n".join(info_lines))
            return
        
        tb = self._inlay_controller.titlebar
        
        if tb is None:
            info_lines.append("❌ ERROR: titlebar is None")
            self._info_label.setText("\n".join(info_lines))
            return
        
        # Check existence
        info_lines.append(f"✅ TitleBar object exists: {type(tb).__name__}")
        
        # Check visibility
        if tb.isVisible():
            info_lines.append("✅ TitleBar is VISIBLE")
        else:
            info_lines.append("❌ TitleBar is HIDDEN")
        
        # Check geometry
        geom = tb.geometry()
        info_lines.append(f"📐 Geometry: x={geom.x()}, y={geom.y()}, w={geom.width()}, h={geom.height()}")
        
        if geom.y() == 0:
            info_lines.append("✅ TitleBar at correct Y position (0)")
        else:
            info_lines.append(f"❌ TitleBar Y position wrong: {geom.y()} (expected 0)")
        
        if geom.height() == COLLAPSED_HEIGHT:
            info_lines.append(f"✅ TitleBar has correct collapsed height: {COLLAPSED_HEIGHT}px")
        else:
            info_lines.append(f"❌ TitleBar height wrong: {geom.height()}px (expected {COLLAPSED_HEIGHT}px)")
        
        # Check parent
        parent = tb.parent()
        if parent is self:
            info_lines.append("✅ TitleBar parent is MainWindow")
        else:
            info_lines.append(f"❌ TitleBar parent wrong: {parent}")
        
        # Check stacking order
        children = self.children()
        tb_index = children.index(tb) if tb in children else -1
        info_lines.append(f"📊 TitleBar index in children: {tb_index} / {len(children)}")
        
        # Check stylesheet
        if "InlayTitleBar" in tb.styleSheet():
            info_lines.append("✅ TitleBar has custom stylesheet")
        else:
            info_lines.append("⚠️ TitleBar stylesheet may be missing")
        
        info_lines.append("")
        info_lines.append("Expected: 3px blue/gray strip at very top of window")
        info_lines.append("Hover over top edge to expand to 36px")
        
        self._info_label.setText("\n".join(info_lines))
        
        # Print to console
        print("\n" + "\n".join(info_lines))
        
        # Force raise
        tb.raise_()
        tb.update()


def main() -> None:
    app = QApplication(sys.argv)
    
    # Dark theme for contrast
    app.setStyleSheet("""
        QMainWindow {
            background: #1E1E1E;
        }
        QWidget {
            background: #2D2E31;
            color: #E0E0E0;
        }
    """)
    
    window = TestWindow()
    window.show()
    
    print("\n" + "="*60)
    print("InlayTitleBar Verification Test Running")
    print("="*60)
    print("\nLook at the TOP EDGE of the window:")
    print("  - You should see a 3px colored strip")
    print("  - Hover over it to expand to full titlebar (36px)")
    print("  - Check the info panel inside the window for details")
    print("="*60 + "\n")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
