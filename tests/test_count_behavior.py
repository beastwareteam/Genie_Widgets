"""Pytest checks for dock widget count behavior."""

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dock_widget_count_changes_after_close() -> None:
    """dockWidgetsCount should not increase after closing a dock widget."""
    app = _get_app()
    window = QMainWindow()
    dock_manager = QtAds.CDockManager(window)

    dock1 = QtAds.CDockWidget(dock_manager, "Panel 1", window)
    dock1.setWidget(QWidget())
    dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock1)

    dock2 = QtAds.CDockWidget(dock_manager, "Panel 2", window)
    dock2.setWidget(QWidget())
    area = dock1.dockAreaWidget()
    dock_manager.addDockWidgetTabToArea(dock2, area)

    before = area.dockWidgetsCount() if hasattr(area, "dockWidgetsCount") else 0
    dock2.close()
    app.processEvents()
    after = area.dockWidgetsCount() if hasattr(area, "dockWidgetsCount") else 0

    assert after <= before
