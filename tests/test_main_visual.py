"""Test ExtendedMainWindow - Validates the extended main window functionality."""

import sys

from PySide6.QtWidgets import QApplication

from widgetsystem.core.main_visual import ExtendedMainWindow


def test_extended_main_window_initialization():
    """Test the initialization of the ExtendedMainWindow class."""
    app_instance = QApplication.instance()
    app = app_instance if isinstance(app_instance, QApplication) else QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    try:
        # Initialize ExtendedMainWindow
        main_window = ExtendedMainWindow(enable_visual_layer=True)
        assert main_window.windowTitle() == "WidgetSystem - Erweitert (Config + Visual Layer)"
        assert main_window.minimumWidth() == 1400
        assert main_window.minimumHeight() == 900

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

        # Check if visual layer is enabled
        assert main_window.enable_visual_layer is True

        print("✅ ExtendedMainWindow initialization test passed.")

    except Exception as e:
        print(f"❌ Fehler: {e}")
        raise

    finally:
        app.quit()
