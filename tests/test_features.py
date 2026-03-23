"""Pytest coverage for dock widget feature behavior."""

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dock_widget_features_available() -> None:
    """Dock widgets expose feature API and widget container."""
    _get_app()
    window = QMainWindow()
    dock_manager = QtAds.CDockManager(window)

    dock = QtAds.CDockWidget(dock_manager, "Panel", window)
    dock.setWidget(QWidget())
    dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock)

    assert dock.widget() is not None
    assert hasattr(dock, "features")
    assert hasattr(dock, "close")


def test_tabbed_dock_widgets_can_be_created() -> None:
    """Two dock widgets can be placed in the same area as tabs."""
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
    assert hasattr(area, "dockWidgets")
    widgets = area.dockWidgets() if hasattr(area, "dockWidgets") else []
    assert len(widgets) >= 2
