"""Pytest checks for inlay titlebar button/widget visibility hooks."""

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from widgetsystem.ui.inlay_titlebar import COLLAPSED_HEIGHT, InlayTitleBarController


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_inlay_titlebar_can_be_installed() -> None:
    """Inlay titlebar controller creates a titlebar widget."""
    _get_app()
    window = QWidget()
    controller = InlayTitleBarController(window)
    controller.install()
    controller.set_title("Button Visibility Test")

    assert controller.titlebar is not None
    assert controller.titlebar.height() >= COLLAPSED_HEIGHT


def test_inlay_titlebar_contains_window_buttons_after_expand() -> None:
    """Expanding titlebar should expose at least one push-button control."""
    _get_app()
    window = QWidget()
    controller = InlayTitleBarController(window)
    controller.install()

    assert controller.titlebar is not None
    controller.titlebar._expand()
    buttons = controller.titlebar.findChildren(QPushButton)
    assert len(buttons) >= 1
