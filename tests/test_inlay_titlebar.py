"""Tests for InlayTitleBar component.

Tests the collapsible drag handle with window manipulation features.
"""

import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QMainWindow

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.ui.inlay_titlebar import (
    COLLAPSED_HIT_HEIGHT,
    EXPANDED_HEIGHT,
    InlayTitleBar,
    InlayTitleBarController,
)


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def main_window(qapp: QApplication) -> QMainWindow:
    """Create a test main window."""
    window = QMainWindow()
    window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
    window.setGeometry(100, 100, 800, 600)
    window.show()
    QApplication.processEvents()
    return window


@pytest.fixture
def titlebar(main_window: QMainWindow) -> InlayTitleBar:
    """Create InlayTitleBar instance with proper geometry."""
    bar = InlayTitleBar(main_window)
    bar.setGeometry(0, 0, main_window.width(), COLLAPSED_HIT_HEIGHT)
    bar.show()
    QApplication.processEvents()
    return bar


@pytest.fixture
def controller(main_window: QMainWindow) -> InlayTitleBarController:
    """Create InlayTitleBarController instance."""
    ctrl = InlayTitleBarController(main_window)
    return ctrl


class TestInlayTitleBar:
    """Tests for InlayTitleBar widget."""

    def test_initialization(self, titlebar: InlayTitleBar) -> None:
        """Test titlebar initialization."""
        assert titlebar is not None
        assert titlebar.isVisible()
        assert titlebar.height() == COLLAPSED_HIT_HEIGHT

    def test_collapsed_state(self, titlebar: InlayTitleBar) -> None:
        """Test initial collapsed state."""
        assert titlebar.height() == COLLAPSED_HIT_HEIGHT
        assert not titlebar._expanded
        assert not titlebar._btn_min.isVisible()

    def test_hover_triggers_expansion(self, titlebar: InlayTitleBar, qapp: QApplication) -> None:
        """Test that mouse hover triggers expansion."""
        titlebar.enterEvent(None)  # type: ignore[arg-type]

        # Expansion is triggered; collapse-guard timer should be active
        assert titlebar._expanded
        assert titlebar._collapse_timer.isActive()

    def test_leave_triggers_collapse(self, titlebar: InlayTitleBar, qapp: QApplication) -> None:
        """Test that mouse leave triggers collapse."""
        # First expand so leaveEvent has something to react to
        titlebar._expanded = True

        titlebar.leaveEvent(None)  # type: ignore[arg-type]

        assert titlebar._collapse_timer.isActive()

    def test_expand_method(self, titlebar: InlayTitleBar, qapp: QApplication) -> None:
        """Test manual expansion."""
        titlebar._expand()

        assert titlebar._expanded
        assert titlebar._anim.state() != 0  # Animation running

    def test_collapse_method(self, titlebar: InlayTitleBar, qapp: QApplication) -> None:
        """Test manual collapse."""
        titlebar._expand()  # properly expand first
        QApplication.processEvents()

        titlebar._collapse()

        assert not titlebar._expanded
        assert titlebar._anim.state() != 0  # Animation running

    def test_set_title(self, titlebar: InlayTitleBar) -> None:
        """Test setting window title."""
        test_title = "Test Application"
        titlebar.set_title(test_title)

        assert titlebar._title_label.text() == test_title

    def test_minimize_button(self, titlebar: InlayTitleBar, main_window: QMainWindow) -> None:
        """Test minimize button functionality."""
        main_window.show()
        titlebar._on_minimize()

        # Window should be minimized
        assert main_window.isMinimized()

    def test_close_button(self, titlebar: InlayTitleBar, main_window: QMainWindow) -> None:
        """Test close button functionality."""
        main_window.show()
        titlebar._on_close()

        # Window should be closed/hidden
        # Note: close() may just hide the window in tests
        assert not main_window.isVisible() or main_window.isHidden()

    def test_maximize_toggle(self, titlebar: InlayTitleBar, main_window: QMainWindow) -> None:
        """Test that _on_toggle_max updates the button text when not maximized."""
        initial_text = titlebar._btn_max.text()

        titlebar._on_toggle_max()
        QApplication.processEvents()

        # In a frameless test window the OS may not honour maximized state,
        # but the button text must always change on the first undirected toggle.
        assert titlebar._btn_max.text() != initial_text

    def test_drag_functionality(self, titlebar: InlayTitleBar, main_window: QMainWindow) -> None:
        """Test drag-to-move functionality."""
        # Simulate mouse press
        press_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(100, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        titlebar.mousePressEvent(press_event)

        assert titlebar._drag_start_global is not None

        # Simulate mouse release
        release_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPoint(100, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        titlebar.mouseReleaseEvent(release_event)

        assert titlebar._drag_start_global is None

    def test_width_spans_window(self, main_window: QMainWindow) -> None:
        """Test that titlebar spans full window width after installation via controller."""
        ctrl = InlayTitleBarController(main_window)
        ctrl.install()
        QApplication.processEvents()

        assert ctrl.titlebar is not None
        assert ctrl.titlebar.width() == main_window.width()

    def test_positioned_at_top(self, titlebar: InlayTitleBar, main_window: QMainWindow) -> None:
        """Test that titlebar is positioned at top of window."""
        main_window.show()
        QApplication.processEvents()

        assert titlebar.y() == 0


class TestInlayTitleBarController:
    """Tests for InlayTitleBarController."""

    def test_initialization(self, controller: InlayTitleBarController) -> None:
        """Test controller initialization."""
        assert controller is not None
        assert controller.titlebar is None

    def test_install(self, controller: InlayTitleBarController, main_window: QMainWindow) -> None:
        """Test titlebar installation."""
        controller.install()
        QApplication.processEvents()

        assert controller.titlebar is not None
        assert controller.titlebar.isVisible()

    def test_double_install_prevention(
        self, controller: InlayTitleBarController, main_window: QMainWindow
    ) -> None:
        """Test that double installation is a no-op (same object returned)."""
        controller.install()
        first_titlebar = controller.titlebar

        controller.install()  # second call must be a no-op
        second_titlebar = controller.titlebar

        assert first_titlebar is second_titlebar

    def test_uninstall(self, controller: InlayTitleBarController, main_window: QMainWindow) -> None:
        """Test titlebar removal."""
        controller.install()
        assert controller.titlebar is not None

        controller.uninstall()
        assert controller.titlebar is None

    def test_set_title_via_controller(
        self, controller: InlayTitleBarController, main_window: QMainWindow
    ) -> None:
        """Test setting title through controller."""
        controller.install()

        test_title = "Controller Test"
        controller.set_title(test_title)

        assert controller.titlebar is not None
        assert controller.titlebar._title_label.text() == test_title

    def test_set_title_before_install(
        self, controller: InlayTitleBarController, main_window: QMainWindow
    ) -> None:
        """Test that setting title before install doesn't crash."""
        # Should not raise exception
        controller.set_title("Test")

        # Now install and check
        controller.install()
        controller.set_title("After Install")

        assert controller.titlebar is not None
        assert controller.titlebar._title_label.text() == "After Install"


class TestInlayTitleBarIntegration:
    """Integration tests for InlayTitleBar in real scenarios."""

    def test_full_lifecycle(self, main_window: QMainWindow, qapp: QApplication) -> None:
        """Test complete lifecycle: install, use, uninstall."""
        controller = InlayTitleBarController(main_window)

        # Install
        controller.install()
        QApplication.processEvents()
        assert controller.titlebar is not None
        assert controller.titlebar.isVisible()

        # Use
        controller.set_title("Lifecycle Test")
        QApplication.processEvents()

        # Trigger expansion
        controller.titlebar._expand()
        QApplication.processEvents()

        # Trigger collapse
        controller.titlebar._collapse()
        QApplication.processEvents()

        # Uninstall
        controller.uninstall()
        assert controller.titlebar is None

    def test_window_resize_updates_titlebar(
        self, main_window: QMainWindow, qapp: QApplication
    ) -> None:
        """Test that on_resize() keeps titlebar width in sync."""
        controller = InlayTitleBarController(main_window)
        controller.install()
        QApplication.processEvents()

        assert controller.titlebar is not None

        # Explicitly notify controller of new width
        controller.on_resize(1200)
        assert controller.titlebar.width() == 1200

        controller.on_resize(900)
        assert controller.titlebar.width() == 900


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
