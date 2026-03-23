"""Screenshot test: Capture the top edge of the window to verify TitleBar visibility.

This script:
1. Launches the main application
2. Waits 2 seconds for initialization
3. Takes a screenshot of the top 50px of the window
4. Saves it as 'titlebar_screenshot.png'
5. Analyzes pixel colors to detect the 3px strip
"""

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.core.main import MainWindow


def capture_titlebar_region(window: MainWindow) -> None:
    """Capture and analyze the top portion of the window."""
    try:
        from PySide6.QtGui import QPixmap
        
        # Get window position and size
        geom = window.geometry()
        x, y = geom.x(), geom.y()
        w = geom.width()
        
        # Capture top 50px of window
        screen = QApplication.primaryScreen()
        if screen:
            screenshot = screen.grabWindow(
                window.winId(),
                0,  # x offset
                0,  # y offset
                w,  # width
                50,  # height (top 50px)
            )
            
            # Save screenshot
            output_path = Path("titlebar_screenshot.png").resolve()
            screenshot.save(str(output_path))
            print(f"\n✅ Screenshot saved: {output_path}")
            print(f"   Size: {screenshot.width()}x{screenshot.height()}")
            
            # Analyze top 5 rows of pixels
            img = screenshot.toImage()
            print("\n📊 Pixel Analysis (top 5 rows):")
            
            for row in range(min(5, img.height())):
                # Sample pixels across the width
                samples = []
                for col in [0, w // 4, w // 2, 3 * w // 4, w - 1]:
                    if col < img.width():
                        pixel = img.pixelColor(col, row)
                        samples.append(f"#{pixel.red():02X}{pixel.green():02X}{pixel.blue():02X}")
                
                print(f"   Row {row}: {' | '.join(samples)}")
            
            # Check for blue accent color (expected in collapsed state)
            has_blue_accent = False
            for row in range(min(3, img.height())):
                for col in range(0, min(w, img.width()), 10):
                    pixel = img.pixelColor(col, row)
                    # Check for blueish color (R < 150, G > 100, B > 180)
                    if pixel.red() < 150 and pixel.green() > 100 and pixel.blue() > 180:
                        has_blue_accent = True
                        print(f"\n✅ Blue accent detected at ({col}, {row}): RGB({pixel.red()}, {pixel.green()}, {pixel.blue()})")
                        break
                if has_blue_accent:
                    break
            
            if not has_blue_accent:
                print("\n⚠️ No blue accent detected - TitleBar may not be visible!")
            
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
    
    # Exit after capture
    QTimer.singleShot(1000, QApplication.quit)


def main() -> None:
    app = QApplication(sys.argv)
    
    print("\n" + "="*60)
    print("TitleBar Screenshot Test")
    print("="*60)
    print("\nLaunching application and capturing top 50px...")
    print("Expected: 3px colored strip at very top")
    print("="*60 + "\n")
    
    window = MainWindow()
    window.show()
    
    # Wait 2 seconds for initialization, then capture
    QTimer.singleShot(2000, lambda: capture_titlebar_region(window))
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
