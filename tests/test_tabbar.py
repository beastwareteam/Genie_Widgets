"""Pytest checks for tabbar-related API in dock areas."""

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_tabbar_related_api_exists_on_area() -> None:
    """Dock area should expose tab-related API after tabbing two docks."""
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
    assert hasattr(area, "findChildren")
    assert hasattr(area, "dockWidgetsCount") or hasattr(area, "dockWidgets")
