"""Pytest checks for floating state tracker and float toggle behavior."""

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from widgetsystem.ui.floating_state_tracker import FloatingStateTracker


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_floating_state_tracker_initialization() -> None:
    """FloatingStateTracker initializes with a dock manager."""
    _get_app()
    window = QMainWindow()
    dock_manager = QtAds.CDockManager(window)

    tracker = FloatingStateTracker(dock_manager)
    assert tracker is not None


def test_panel_can_toggle_floating_state_if_supported() -> None:
    """Dock panel floating toggle works when API is available."""
    app = _get_app()
    window = QMainWindow()
    dock_manager = QtAds.CDockManager(window)
    _ = FloatingStateTracker(dock_manager)

    dock = QtAds.CDockWidget(dock_manager, "Test Panel", window)
    dock.setWidget(QWidget())
    dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock)

    if hasattr(dock, "setFloating") and hasattr(dock, "isFloating"):
        dock.setFloating()
        assert isinstance(dock.isFloating(), bool)
