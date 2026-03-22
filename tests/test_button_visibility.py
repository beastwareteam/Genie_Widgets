"""Test script to verify window control buttons are visible when TitleBar expands.

This script:
1. Creates a minimal window with InlayTitleBar
2. Automatically expands the titlebar after 1 second
3. Checks button visibility and styling
4. Prints detailed button state information
"""

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.ui.inlay_titlebar import (
    COLLAPSED_HEIGHT,
    EXPANDED_HEIGHT,
    InlayTitleBarController,
)


def verify_buttons(controller: InlayTitleBarController) -> None:
    """Check if buttons are visible and have correct styling."""
    tb = controller.titlebar
    if not tb:
        print("ERROR: TitleBar is None!")
        return
    
    print("\n" + "="*60)
    print("BUTTON VISIBILITY TEST")
    print("="*60)
    
    # Check titlebar state
    print(f"\nTitleBar Height: {tb.height()}px (Expected: {EXPANDED_HEIGHT}px)")
    print(f"TitleBar Visible: {tb.isVisible()}")
    print(f"TitleBar Geometry: {tb.geometry()}")
    
    # Find all QPushButton children
    buttons = tb.findChildren(QPushButton)
    print(f"\nFound {len(buttons)} button(s)")
    
    for btn in buttons:
        obj_name = btn.objectName()
        text = btn.text()
        visible = btn.isVisible()
        geom = btn.geometry()
        stylesheet = btn.styleSheet()
        
        print(f"\n--- Button: {obj_name} ---")
        print(f"  Text/Symbol: '{text}' (Unicode: U+{ord(text):04X})")
        print(f"  Visible: {visible}")
        print(f"  Geometry: x={geom.x()}, y={geom.y()}, w={geom.width()}, h={geom.height()}")
        print(f"  Cursor: {btn.cursor().shape()}")
        print(f"  Font: {btn.font().toString()}")
        print(f"  Palette (ButtonText): {btn.palette().color(btn.palette().ColorRole.ButtonText).name()}")
        
        # Check if button has inline stylesheet
        if stylesheet:
            print(f"  Has inline stylesheet: {len(stylesheet)} chars")
        
        # Check parent stylesheet
        parent_style = tb.styleSheet()
        if obj_name in parent_style:
            print(f"  Found in parent stylesheet: YES")
            # Extract relevant section
            lines = [line.strip() for line in parent_style.split('\n') if obj_name in line]
            if lines:
                print(f"  Style selector: {lines[0]}")
    
    print("\n" + "="*60)
    print("EXPECTED STATE:")
    print("  - All 3 buttons should be VISIBLE")
    print("  - Symbols should be: - (minimize), [] (maximize), X (close)")
    print("  - Color should be bright gray (#D5D5D5) by default")
    print("  - On hover: white (#FFFFFF) with background")
    print("="*60 + "\n")


def main() -> None:
    app = QApplication(sys.argv)
    
    # Create minimal test window
    window = QWidget()
    window.setWindowTitle("Button Visibility Test")
    window.resize(500, 300)
    window.show()
    
    # Install titlebar
    controller = InlayTitleBarController(window)
    controller.install()
    controller.set_title("TEST: Button Visibility")
    
    if controller.titlebar:
        # Force expand immediately
        controller.titlebar._expand()
        print("\n[INFO] TitleBar expanded - buttons should now be visible")
        
        # Schedule verification
        QTimer.singleShot(500, lambda: verify_buttons(controller))
        
        # Exit after verification
        QTimer.singleShot(3000, app.quit)
    else:
        print("ERROR: TitleBar not created!")
        app.quit()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
