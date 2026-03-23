"""Pytest signal-availability checks for CDockManager."""

import PySide6QtAds as QtAds
from PySide6.QtWidgets import QApplication, QMainWindow


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dock_manager_exposes_expected_signal_attributes() -> None:
    """CDockManager should expose expected signal-style attributes."""
    _get_app()
    window = QMainWindow()
    dock_manager = QtAds.CDockManager(window)

    candidate_signals = [
        "dockWidgetRemoved",
        "dockWidgetAboutToBeRemoved",
        "dockAreaRemoved",
    ]
    available = [name for name in candidate_signals if hasattr(dock_manager, name)]

    assert len(available) >= 1

