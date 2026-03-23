"""Test MainWindow - Validates main application window functionality."""

from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from widgetsystem.controllers.layout_controller import LayoutController
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


def test_layout_controller_save_and_load_roundtrip(tmp_path: Path) -> None:
    """LayoutController can save and load layout state bytes."""
    dock_manager = MagicMock()
    state = MagicMock()
    state.data.return_value = b"layout-bytes"
    dock_manager.saveState.return_value = state
    dock_manager.restoreState.return_value = True

    layout_factory = MagicMock()
    layout_factory.get_default_layout_id.return_value = None
    layout_factory.list_layouts.return_value = []

    controller = LayoutController(dock_manager, layout_factory, MagicMock())
    target = tmp_path / "layout.xml"
    controller.layout_file = target

    assert controller.save() is True
    assert target.exists()
    assert controller.load() is True
    dock_manager.restoreState.assert_called()


def test_layout_controller_load_missing_file_fails(tmp_path: Path) -> None:
    """Loading a missing layout file returns False."""
    layout_factory = MagicMock()
    layout_factory.get_default_layout_id.return_value = None
    layout_factory.list_layouts.return_value = []

    controller = LayoutController(MagicMock(), layout_factory, MagicMock())
    controller.layout_file = tmp_path / "missing.xml"

    assert controller.load() is False


def test_main_window_reset_layout_recreates_dock_manager() -> None:
    """MainWindow reset layout recreates dock manager and rebuild helpers."""
    old_manager = MagicMock()
    new_manager = MagicMock()

    fake_window = SimpleNamespace(
        docks=[MagicMock()],
        dock_manager=old_manager,
        i18n_factory=MagicMock(),
        _reset_controller_states=MagicMock(),
        _configure_dock_flags=MagicMock(),
        _create_dock_areas=MagicMock(),
        _create_tab_groups=MagicMock(),
        _reinitialize_tab_controllers=MagicMock(),
    )
    fake_window.i18n_factory.translate.side_effect = lambda _k, default="": default

    with patch("widgetsystem.core.main.QtAds.CDockManager", return_value=new_manager):
        with patch("widgetsystem.core.main.QMessageBox.information") as info_box:
            MainWindow._reset_layout(fake_window)  # type: ignore[arg-type]

    old_manager.deleteLater.assert_called_once()
    assert fake_window.dock_manager is new_manager
    assert fake_window.docks == []
    fake_window._reset_controller_states.assert_called_once()
    fake_window._configure_dock_flags.assert_called_once()
    fake_window._create_dock_areas.assert_called_once()
    fake_window._create_tab_groups.assert_called_once()
    fake_window._reinitialize_tab_controllers.assert_called_once()
    info_box.assert_called_once()
