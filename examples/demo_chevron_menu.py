"""Demo for Chevron Menu module - test hierarchical menus with visual indicators."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget
from PySide6.QtCore import Qt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.ui.chevron_menu import ChevronMenu, ChevronMenuBar


def create_sample_menu() -> list[MenuItem]:
    """Create a sample menu structure for testing."""
    return [
        MenuItem(
            id="file_menu",
            label_key="File",
            type="menu",
            action="",
            shortcut="",
            children=[
                MenuItem(
                    id="file_new",
                    label_key="New",
                    type="action",
                    action="new",
                    shortcut="Ctrl+N",
                ),
                MenuItem(
                    id="file_open",
                    label_key="Open",
                    type="action",
                    action="open",
                    shortcut="Ctrl+O",
                ),
                MenuItem(
                    id="file_sep1",
                    label_key="",
                    type="separator",
                    action="",
                    shortcut="",
                ),
                MenuItem(
                    id="file_exit",
                    label_key="Exit",
                    type="action",
                    action="exit",
                    shortcut="Alt+F4",
                ),
            ],
        ),
        MenuItem(
            id="edit_menu",
            label_key="Edit",
            type="menu",
            action="",
            shortcut="",
            children=[
                MenuItem(
                    id="edit_undo",
                    label_key="Undo",
                    type="action",
                    action="undo",
                    shortcut="Ctrl+Z",
                ),
                MenuItem(
                    id="edit_redo",
                    label_key="Redo",
                    type="action",
                    action="redo",
                    shortcut="Ctrl+Y",
                ),
            ],
        ),
        MenuItem(
            id="view_menu",
            label_key="View",
            type="menu",
            action="",
            shortcut="",
            children=[
                MenuItem(
                    id="view_zoom_in",
                    label_key="Zoom In",
                    type="action",
                    action="zoom_in",
                    shortcut="Ctrl++",
                ),
                MenuItem(
                    id="view_zoom_out",
                    label_key="Zoom Out",
                    type="action",
                    action="zoom_out",
                    shortcut="Ctrl+-",
                ),
                MenuItem(
                    id="view_sep1",
                    label_key="",
                    type="separator",
                    action="",
                    shortcut="",
                ),
                MenuItem(
                    id="view_fullscreen",
                    label_key="Fullscreen",
                    type="action",
                    action="fullscreen",
                    shortcut="F11",
                ),
            ],
        ),
    ]


class ChevronMenuDemo(QMainWindow):
    """Demo window for Chevron Menu module."""

    def __init__(self) -> None:
        """Initialize the demo window."""
        super().__init__()
        self.setWindowTitle("Chevron Menu Demo")
        self.setGeometry(100, 100, 600, 400)

        # Setup UI
        Central_widget = QWidget()
        self.setCentralWidget(Central_widget)
        layout = QVBoxLayout(Central_widget)

        # Title
        title = QLabel("Chevron Menu with Hierarchical Structure")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        # Info label
        info = QLabel(
            "Click menu buttons below to see hierarchical menus with chevron indicators"
        )
        layout.addWidget(info)

        # Create sample menus
        sample_menus = create_sample_menu()

        # Create menu buttons
        for menu_item in sample_menus:
            btn = QPushButton(f"📋 {menu_item.label_key}")
            chevron_menu = ChevronMenu(title=menu_item.label_key)

            # Add children to menu
            for child in menu_item.children:
                chevron_menu.add_menu_item(
                    child, callback=self._on_menu_action_triggered
                )

            # Connect button to show menu
            btn.clicked.connect(
                lambda m=chevron_menu: self._show_menu(m)
            )
            layout.addWidget(btn)

        # Status label
        self.status_label = QLabel("Ready. Click a menu button...")
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _show_menu(self, menu: ChevronMenu) -> None:
        """Show the menu at cursor position.

        Args:
            menu: The menu to show
        """
        cursor = self.mapFromGlobal(self.cursor().pos())
        menu.popup(self.mapToGlobal(cursor))

    def _on_menu_action_triggered(self, action_id: str) -> None:
        """Handle menu action triggered.

        Args:
            action_id: The triggered action ID
        """
        self.status_label.setText(f"Action triggered: {action_id}")
        print(f"[+] Menu action: {action_id}")


def main() -> None:
    """Run the demo."""
    app = QApplication(sys.argv)

    window = ChevronMenuDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
