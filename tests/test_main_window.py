"""Test MainWindow - Validates main application window functionality."""

import sys

from PySide6.QtWidgets import QApplication

from widgetsystem.core.main import MainWindow


def test_main_window_initialization():
    """Test the initialization of the MainWindow class."""
    app_instance = QApplication.instance()
    app = app_instance if isinstance(app_instance, QApplication) else QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    try:
        # Initialize MainWindow
        main_window = MainWindow()
        assert main_window.windowTitle() == "ADS Docking System - Transparent Themes"
        assert main_window.minimumWidth() == 1200
        assert main_window.minimumHeight() == 800

        # Check if factories are initialized
        assert main_window.layout_factory is not None
        assert main_window.theme_factory is not None
        assert main_window.panel_factory is not None
        assert main_window.menu_factory is not None
        assert main_window.tabs_factory is not None
        assert main_window.dnd_factory is not None
        assert main_window.responsive_factory is not None
        assert main_window.i18n_factory is not None
        assert main_window.list_factory is not None
        assert main_window.ui_config_factory is not None

        # Check if ThemeManager is connected
        assert main_window.theme_manager is not None
        assert main_window.theme_manager.themeChanged is not None

        print("✅ MainWindow initialization test passed.")

    except Exception as e:
        print(f"❌ Fehler: {e}")
        raise

    finally:
        app.quit()
