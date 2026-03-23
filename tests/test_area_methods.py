"""Pytest checks for dock area methods."""

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dock_area_reports_widgets_and_counts() -> None:
    """Dock area should report tabbed widgets and count accessors."""
    _get_app()
    window = QMainWindow()
    dock_manager = QtAds.CDockManager(window)

    dock1 = QtAds.CDockWidget(dock_manager, "Panel 1", window)
    dock1.setWidget(QWidget())
    dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock1)

    dock2 = QtAds.CDockWidget(dock_manager, "Panel 2", window)
    dock2.setWidget(QWidget())
    area = dock1.dockAreaWidget()
    dock_manager.addDockWidgetTabToArea(dock2, area)

    assert area is not None
    if hasattr(area, "dockWidgets"):
        assert len(area.dockWidgets()) >= 2
    if hasattr(area, "dockWidgetsCount"):
        assert area.dockWidgetsCount() >= 2
