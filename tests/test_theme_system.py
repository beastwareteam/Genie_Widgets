"""Test script for Theme System with ARGB support."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from widgetsystem.core import Theme, ThemeManager, ThemeProfile
from widgetsystem.factories.theme_factory import ThemeFactory


class ThemeTestWindow(QMainWindow):
    """Test window for theme system."""

    def __init__(self) -> None:
        """Initialize test window."""
        super().__init__()
        self.setWindowTitle("Theme System Test")
        self.setMinimumSize(800, 600)

        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0, 0))
        self.setPalette(palette)

        # Initialize factories
        self.theme_factory = ThemeFactory(Path("config"))
        self.theme_manager = ThemeManager.instance()

        # Create default profiles
        print("Creating default profiles...")
        self.theme_factory.create_default_profiles()

        # Register themes
        print("\nRegistering themes...")
        self._register_themes()

        # Setup UI
        self._setup_ui()

        print("\nTheme system initialized successfully! ✓")

    def _register_themes(self) -> None:
        """Register all available themes."""
        # Register profiles
        for profile_id in self.theme_factory.list_profiles():
            profile = self.theme_factory.load_profile(profile_id)
            if profile:
                theme = Theme(f"profile_{profile_id}", profile.name)
                theme.set_stylesheet(profile.generate_qss())
                theme.set_property("is_profile", True)
                theme.set_property("profile_id", profile_id)
                self.theme_manager.register_theme(theme)
                print(f"  ✓ Registered: {profile.name} (id: {profile_id})")

        # Connect signal
        self.theme_manager.themeChanged.connect(self._on_theme_changed)

        # Set default theme
        if self.theme_manager.theme_names():
            self.theme_manager.set_current_theme(self.theme_manager.theme_names()[0])

    def _setup_ui(self) -> None:
        """Setup test UI."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)

        # Title
        title = QLabel("🎨 Theme System Test")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Current theme label
        self.current_theme_label = QLabel()
        self.current_theme_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.current_theme_label)
        self._update_current_theme_label()

        # Theme buttons
        layout.addWidget(QLabel("Available Themes:"))

        for theme_id in self.theme_manager.theme_names():
            theme = self.theme_manager.get_theme(theme_id)
            if theme:
                btn = QPushButton(f"Apply: {theme.name}")
                btn.clicked.connect(
                    lambda checked=False, tid=theme_id: self.theme_manager.set_current_theme(tid)  # noqa: ARG005
                )
                layout.addWidget(btn)

        layout.addStretch()

        # Info
        info = QLabel(
            "✓ ARGB Transparency Support\n"
            "✓ Theme Manager with Signals\n"
            "✓ Profile-based Configuration\n"
            "✓ Global Color Transformations"
        )
        info.setStyleSheet("color: #00ff00; font-family: monospace;")
        layout.addWidget(info)

    def _on_theme_changed(self, theme: Theme) -> None:
        """Handle theme change.
        
        Args:
            theme: New theme
        """
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(theme.stylesheet)
            print(f"\n✓ Theme applied: {theme.name}")
            self._update_current_theme_label()

    def _update_current_theme_label(self) -> None:
        """Update current theme label."""
        current = self.theme_manager.current_theme()
        if current:
            self.current_theme_label.setText(f"Current Theme: {current.name}")
        else:
            self.current_theme_label.setText("Current Theme: None")


def main() -> None:
    """Run theme test application."""
    print("="*60)
    print("Theme System Test - ARGB & Transparency Support")
    print("="*60)

    app = QApplication(sys.argv)

    # Create and show window
    window = ThemeTestWindow()
    window.show()

    print("\nWindow shown. Try switching themes using the buttons!")
    print("Press Ctrl+C or close window to exit.\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
