"""Demo: Inlay TitleBar - Collapsible window control demonstration.

Shows the new 3px collapsible drag handle that expands on hover.
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.ui import InlayTitleBarController


class DemoWindow(QMainWindow):
    """Demo window showcasing InlayTitleBar."""

    def __init__(self) -> None:
        """Initialize demo window."""
        super().__init__()

        # Frameless window with transparency
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setGeometry(200, 200, 900, 600)

        # Setup content
        self._setup_content()

        # Install Inlay TitleBar
        self._inlay_controller = InlayTitleBarController(self)
        self._inlay_controller.install()
        self._inlay_controller.set_title("Inlay TitleBar Demo - Hover to expand")

    def _setup_content(self) -> None:
        """Setup demo content."""
        central = QWidget()
        central.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 240),
                    stop:1 rgba(25, 25, 25, 250)
                );
                border: 1px solid rgba(60, 60, 60, 200);
                border-radius: 8px;
            }
            QLabel {
                color: #E0E0E0;
                background: transparent;
                padding: 20px;
            }
        """
        )
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 60, 40, 40)  # Top margin for titlebar

        # Title
        title = QLabel("Inlay TitleBar Demo")
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            """
            <h3>Features:</h3>
            <ul>
                <li><b>3px Slim Handle</b> - Minimaler Platzverbrauch am oberen Rand</li>
                <li><b>Mouse Hover → Expand</b> - Bewegen Sie die Maus an den oberen Rand</li>
                <li><b>Vollständige Controls</b> - Minimieren, Maximieren, Schließen</li>
                <li><b>Drag & Drop</b> - Ziehen Sie das Fenster an der Titelleiste</li>
                <li><b>Smooth Animations</b> - 200ms Ein-/Ausklapp-Animation</li>
                <li><b>Auto-Collapse</b> - Automatisches Einklappen nach 300ms</li>
            </ul>
            
            <h3>Verwendung:</h3>
            <ol>
                <li>Bewegen Sie die Maus zum <b>oberen Rand</b> des Fensters</li>
                <li>Warten Sie 100ms → Titelleiste klappt aus</li>
                <li>Verwenden Sie die <b>Fenster-Buttons</b> oder <b>ziehen</b> Sie das Fenster</li>
                <li>Bewegen Sie die Maus weg → Titelleiste klappt ein</li>
                <li><b>Doppelklick</b> auf Titelleiste → Maximieren/Wiederherstellen</li>
            </ol>
            
            <p style="margin-top: 30px; font-size: 14pt;">
                <b>Tipp:</b> Der dünne 3px-Streifen am oberen Rand ist das eingeklappte Handle!
            </p>
            """
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11pt; line-height: 1.6;")
        layout.addWidget(instructions)

        layout.addStretch()


def main() -> None:
    """Run demo application."""
    app = QApplication(sys.argv)

    window = DemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
