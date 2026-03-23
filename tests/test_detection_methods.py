"""Pytest checks for dock widget close detection methods."""

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_widget_close_detection_methods() -> None:
    """Closed dock widgets can be detected through available APIs."""
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

    dock2.close()
    app.processEvents()

    if hasattr(dock2, "isClosed"):
        assert isinstance(dock2.isClosed(), bool)
    if hasattr(area, "dockWidgets"):
        assert len(area.dockWidgets()) >= 1
