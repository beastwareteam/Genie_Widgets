"""Verify current InlayTitleBar button styling and spacing.

This script prints the actual CSS values applied to the buttons
to confirm the styling changes are loaded.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.ui.inlay_titlebar import InlayTitleBarController


def print_button_styles(controller: InlayTitleBarController) -> None:
    """Extract and print button CSS properties."""
    tb = controller.titlebar
    if not tb:
        print("ERROR: TitleBar is None!")
        return
    
    print("\n" + "="*70)
    print("CURRENT INLAY TITLEBAR STYLING")
    print("="*70)
    
    # Get full stylesheet
    full_style = tb.styleSheet()
    
    # Check for new color values
    if "#D5D5D5" in full_style:
        print("\n[OK] Button color updated to #D5D5D5 (bright gray)")
    else:
        print("\n[WARNING] Button color may still be old value")
    
    # Check for font-weight
    if "font-weight: 600" in full_style or "font-weight: 700" in full_style:
        print("[OK] Font weight increased (600/700 - bold)")
    else:
        print("[WARNING] Font weight not found")
    
    # Check for new Unicode symbols
    buttons = [(btn.objectName(), btn.text()) for btn in tb.findChildren(QPushButton)]
    print(f"\n[BUTTONS] Found {len(buttons)} buttons:")
    for name, text in buttons:
        unicode_code = f"U+{ord(text):04X}" if text else "EMPTY"
        print(f"  {name}: '{text}' ({unicode_code})")
    
    # Expected symbols
    expected = {
        "TitleBtn_minimize": ("−", "U+2212"),
        "TitleBtn_maximize": ("☐", "U+2610"),
        "TitleBtn_close": ("×", "U+00D7"),
    }
    
    print("\n[EXPECTED SYMBOLS]:")
    for btn_name, (symbol, code) in expected.items():
        actual = next((text for name, text in buttons if name == btn_name), None)
        if actual == symbol:
            print(f"  {btn_name}: OK - {symbol} ({code})")
        else:
            print(f"  {btn_name}: MISMATCH - Expected '{symbol}' but got '{actual}'")
    
    # Check spacing constant
    print("\n[SPACING]:")
    try:
        from widgetsystem.core.main import TITLEBAR_SPACING
        print(f"  TITLEBAR_SPACING = {TITLEBAR_SPACING}px (spacing between TitleBar and Toolbar)")
    except ImportError:
        print("  WARNING: TITLEBAR_SPACING constant not found!")
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("  - Button symbols should be: − (minus), ☐ (box), × (x)")
    print("  - Button color: #D5D5D5 (bright gray, good contrast)")
    print("  - Font weight: 600 (semibold) and 700 (bold)")
    print("  - Spacing: 2px gap between TitleBar and Toolbar")
    print("="*70 + "\n")
    
    QApplication.quit()


def main() -> None:
    app = QApplication(sys.argv)
    
    # Create minimal test window
    window = QWidget()
    window.resize(400, 200)
    window.show()
    
    # Install titlebar
    controller = InlayTitleBarController(window)
    controller.install()
    
    if controller.titlebar:
        # Force expand to see buttons
        controller.titlebar._expand()
        
        # Check styling after 500ms
        QTimer.singleShot(500, lambda: print_button_styles(controller))
    else:
        print("ERROR: TitleBar not created!")
        app.quit()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    from PySide6.QtWidgets import QPushButton
    main()
