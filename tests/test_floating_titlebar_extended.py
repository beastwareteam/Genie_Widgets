"""Extended tests for floating_titlebar module."""

from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

from widgetsystem.ui import floating_titlebar as ft


class _Point:
    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    def x(self) -> int:
        return self._x

    def y(self) -> int:
        return self._y


class _Frame:
    def __init__(self, point: _Point) -> None:
        self._point = point

    def topLeft(self) -> _Point:
        return self._point


class _GlobalPos:
    def __init__(self, point: _Point) -> None:
        self._point = point

    def toPoint(self) -> _Point:
        return self._point


class _MousePos:
    def __init__(self, marker: str) -> None:
        self._marker = marker

    def __sub__(self, _other: object) -> str:
        return self._marker


class TestFloatingWindowPatcher:
    """Tests for FloatingWindowPatcher event filter."""

    def test_event_filter_patches_floating_container_on_show(self) -> None:
        """Show event on floating container applies patching logic."""
        patcher = ft.FloatingWindowPatcher()

        class FakeContainer:
            def __init__(self) -> None:
                self._props: dict[str, object] = {}
                self.flags = None

            def property(self, name: str) -> object:
                return self._props.get(name, False)

            def setProperty(self, name: str, value: object) -> None:
                self._props[name] = value

            def setWindowFlags(self, flags: object) -> None:
                self.flags = flags

        obj = FakeContainer()
        event = Mock()
        event.type.return_value = ft.QEvent.Type.Show

        handle = MagicMock()
        with patch.object(ft.QtAds, "CDockFloatingContainer", FakeContainer, create=True):
            with patch("widgetsystem.ui.floating_titlebar.WindowMoveHandle", return_value=handle):
                result = patcher.eventFilter(obj, event)

        assert result is False
        assert obj.property("_patched") is True
        handle.show.assert_called_once()
        handle.raise_.assert_called_once()

    def test_event_filter_non_show_event_no_patch(self) -> None:
        """Non-show events return False without patching."""
        patcher = ft.FloatingWindowPatcher()
        obj = Mock()
        event = Mock()
        event.type.return_value = ft.QEvent.Type.Hide

        assert patcher.eventFilter(obj, event) is False


class TestWindowMoveHandleMethods:
    """Tests for WindowMoveHandle mouse/resize handlers."""

    def test_mouse_press_sets_drag_position(self) -> None:
        """Left click stores drag offset and accepts event."""
        parent_window = Mock()
        parent_window.frameGeometry.return_value = _Frame(_Point(10, 20))

        handle = SimpleNamespace(_parent_window=parent_window, _drag_pos=None)
        event = Mock()
        event.button.return_value = ft.Qt.MouseButton.LeftButton
        event.globalPosition.return_value = _GlobalPos(_Point(30, 50))

        ft.WindowMoveHandle.mousePressEvent(handle, event)  # type: ignore[arg-type]

        assert handle._drag_pos == (20, 30)
        event.accept.assert_called_once()

    def test_mouse_move_moves_parent_window_when_dragging(self) -> None:
        """Dragging with left button moves parent window."""
        parent_window = Mock()
        handle = SimpleNamespace(_parent_window=parent_window, _drag_pos=(5, 7))
        event = Mock()
        event.buttons.return_value = ft.Qt.MouseButton.LeftButton
        event.globalPosition.return_value = _GlobalPos(_Point(20, 40))

        ft.WindowMoveHandle.mouseMoveEvent(handle, event)  # type: ignore[arg-type]

        parent_window.move.assert_called_once_with(15, 33)
        event.accept.assert_called_once()

    def test_mouse_release_clears_drag_state(self) -> None:
        """Mouse release clears drag position."""
        handle = SimpleNamespace(_drag_pos=(1, 2))
        event = Mock()

        ft.WindowMoveHandle.mouseReleaseEvent(handle, event)  # type: ignore[arg-type]

        assert handle._drag_pos is None
        event.accept.assert_called_once()

    def test_resize_event_updates_geometry(self) -> None:
        """Resize handler spans full width at top."""
        parent_window = Mock()
        parent_window.width.return_value = 400
        handle = SimpleNamespace(_parent_window=parent_window, setGeometry=Mock())

        ft.WindowMoveHandle.resizeEvent(handle, Mock())  # type: ignore[arg-type]

        handle.setGeometry.assert_called_once_with(0, 0, 400, 30)


class TestCustomFloatingTitleBarMethods:
    """Tests for CustomFloatingTitleBar helper methods."""

    def test_setup_ui_creates_controls(self) -> None:
        """UI setup creates label and action buttons."""
        dock_signal = SimpleNamespace(emit=Mock())
        close_signal = SimpleNamespace(emit=Mock())
        title_label = Mock()
        dock_button = Mock()
        dock_button.clicked = SimpleNamespace(connect=Mock())
        close_button = Mock()
        close_button.clicked = SimpleNamespace(connect=Mock())

        bar = SimpleNamespace(
            title_text="My Title",
            dock_requested=dock_signal,
            close_requested=close_signal,
            setMaximumHeight=Mock(),
            setMinimumHeight=Mock(),
        )

        with patch("widgetsystem.ui.floating_titlebar.QHBoxLayout", return_value=Mock()):
            with patch("widgetsystem.ui.floating_titlebar.QLabel", return_value=title_label):
                with patch("widgetsystem.ui.floating_titlebar.QFont", return_value=Mock()):
                    with patch(
                        "widgetsystem.ui.floating_titlebar.QPushButton",
                        side_effect=[dock_button, close_button],
                    ):
                        ft.CustomFloatingTitleBar._setup_ui(bar)  # type: ignore[arg-type]

        assert bar.title_label == title_label
        assert bar.dock_button == dock_button
        assert bar.close_button == close_button
        bar.setMaximumHeight.assert_called_once_with(32)
        bar.setMinimumHeight.assert_called_once_with(32)

    def test_setup_style_sets_stylesheet(self) -> None:
        """Style setup applies default stylesheet."""
        bar = SimpleNamespace(setStyleSheet=Mock())
        ft.CustomFloatingTitleBar._setup_style(bar)  # type: ignore[arg-type]
        bar.setStyleSheet.assert_called_once()

    def test_update_theme_style(self) -> None:
        """Theme style update forwards stylesheet string."""
        bar = SimpleNamespace(setStyleSheet=Mock())
        ft.CustomFloatingTitleBar.update_theme_style(bar, "QWidget {}")  # type: ignore[arg-type]
        bar.setStyleSheet.assert_called_once_with("QWidget {}")

    def test_set_title_updates_label(self) -> None:
        """Setting title updates internal text and label widget."""
        label = Mock()
        bar = SimpleNamespace(title_text="old", title_label=label)

        ft.CustomFloatingTitleBar.set_title(bar, "new")  # type: ignore[arg-type]

        assert bar.title_text == "new"
        label.setText.assert_called_once_with("new")

    def test_mouse_press_starts_drag(self) -> None:
        """Mouse press stores drag offset and accepts event."""
        window = Mock()
        window.pos.return_value = _MousePos("offset")
        event = Mock()
        event.button.return_value = ft.Qt.MouseButton.LeftButton
        event.globalPos.return_value = _MousePos("ignored")

        bar = SimpleNamespace(window=Mock(return_value=window), _drag_start_pos=None)
        ft.CustomFloatingTitleBar.mousePressEvent(bar, event)  # type: ignore[arg-type]

        assert bar._drag_start_pos == "ignored"
        event.accept.assert_called_once()

    def test_mouse_move_moves_window(self) -> None:
        """Mouse move with drag state moves parent window."""
        window = Mock()
        event = Mock()
        event.buttons.return_value = ft.Qt.MouseButton.LeftButton
        event.globalPos.return_value = _MousePos("moved")

        bar = SimpleNamespace(window=Mock(return_value=window), _drag_start_pos=object())
        ft.CustomFloatingTitleBar.mouseMoveEvent(bar, event)  # type: ignore[arg-type]

        window.move.assert_called_once_with("moved")
        event.accept.assert_called_once()

    def test_mouse_release_clears_drag(self) -> None:
        """Mouse release clears drag state."""
        bar = SimpleNamespace(_drag_start_pos=object())
        event = Mock()

        ft.CustomFloatingTitleBar.mouseReleaseEvent(bar, event)  # type: ignore[arg-type]

        assert bar._drag_start_pos is None
        event.accept.assert_called_once()
