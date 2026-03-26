"""Custom floating title bar for CDockWidgets - Qt-native inline title bar for floating state."""

from typing import TYPE_CHECKING
from typing import Any

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
import PySide6QtAds as QtAds

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


class FloatingWindowPatcher(QObject):
    """Event filter that patches floating containers BEFORE they are shown.

    Intercepts QEvent::Show on CDockFloatingContainer widgets and applies
    FramelessWindowHint BEFORE the native window is created. This avoids
    Windows window handle recreation bugs.
    """

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize patcher.

        Args:
            parent: Parent object
        """
        super().__init__(parent)

    def eventFilter(self, obj: Any, event: Any) -> bool:
        """Intercept Show events on floating containers.

        Args:
            obj: Object that emitted the event
            event: The event

        Returns:
            False to allow normal event processing
        """
        # Check if this is a Show event on a CDockFloatingContainer
        if (
            event.type() == QEvent.Type.Show
            and hasattr(QtAds, "CDockFloatingContainer")
            and isinstance(obj, QtAds.CDockFloatingContainer)
            and not obj.property("_patched")
        ):
            # Mark as patched to avoid re-processing
            obj.setProperty("_patched", True)

            # Apply frameless window flags BEFORE show completes
            # This ensures clean window creation without OS decorations
            obj.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)

            # Add transparent move handle for drag-to-move
            # Child widgets already exist at this point
            handle = WindowMoveHandle(obj)
            handle.show()
            handle.raise_()

        # Always return False to allow normal event processing
        return False


class WindowMoveHandle(QWidget):
    """Transparent drag handle for moving frameless windows.

    This widget sits on top of the title bar and enables drag-to-move
    functionality for windows with FramelessWindowHint set.
    It's transparent to all mouse events except left-button drag.
    """

    def __init__(self, parent_window: QWidget) -> None:
        """Initialize move handle.

        Args:
            parent_window: The parent window to move
        """
        super().__init__(parent_window)
        self._parent_window = parent_window
        self._drag_pos: tuple[int, int] | None = None

        # Make transparent for mouse events outside of drag
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Fixed height matching typical QtAds title bar (28-32px)
        self.setFixedHeight(30)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        # Ensure it's on top
        self.raise_()

    def mousePressEvent(self, event: Any) -> None:
        """Start drag on left mouse button press.

        Args:
            event: Mouse press event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the offset from window's top-left corner to mouse position
            frame_pos = self._parent_window.frameGeometry().topLeft()
            mouse_pos = event.globalPosition().toPoint()
            self._drag_pos = (mouse_pos.x() - frame_pos.x(), mouse_pos.y() - frame_pos.y())
            event.accept()

    def mouseMoveEvent(self, event: Any) -> None:
        """Move window while dragging.

        Args:
            event: Mouse move event
        """
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            mouse_pos = event.globalPosition().toPoint()
            new_x = mouse_pos.x() - self._drag_pos[0]
            new_y = mouse_pos.y() - self._drag_pos[1]
            self._parent_window.move(new_x, new_y)
            event.accept()

    def mouseReleaseEvent(self, event: Any) -> None:
        """End drag on mouse release.

        Args:
            event: Mouse release event
        """
        self._drag_pos = None
        event.accept()

    def resizeEvent(self, _event: Any) -> None:
        """Adjust handle geometry when parent window resizes.

        Args:
            _event: Resize event
        """
        # Span full width, fixed height at top
        self.setGeometry(0, 0, self._parent_window.width(), 30)


class CustomFloatingTitleBar(QWidget):
    """Custom title bar for floating CDockWidgets.

    Provides a Qt-native inline title bar with:
    - Dock name/title
    - Close button
    - Pin/Dock button
    - Drag-to-move functionality
    """

    close_requested = Signal()
    dock_requested = Signal()

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize custom floating title bar.

        Args:
            title: Title to display
            parent: Parent widget
        """
        super().__init__(parent)

        self.title_text = title
        self._drag_start_pos = None
        self._i18n_factory = i18n_factory
        self._translation_cache: dict[str, str] = {}

        self._setup_ui()
        self._setup_style()

    def _translate(self, key: str, default: str) -> str:
        """Translate a key with fallback and cache."""
        if not key:
            return default

        if key in self._translation_cache:
            return self._translation_cache[key]

        if self._i18n_factory is None:
            self._translation_cache[key] = default
            return default

        translated = self._i18n_factory.translate(key, default=default)
        self._translation_cache[key] = translated
        return translated

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory and refresh translated texts."""
        self._i18n_factory = i18n_factory
        self._translation_cache.clear()
        self._refresh_translated_texts()

    def _refresh_translated_texts(self) -> None:
        """Refresh translated visible texts."""
        self.dock_button.setToolTip(
            self._translate("floating_titlebar.tooltip.dock", "Zurück ins Dock"),
        )
        self.close_button.setToolTip(
            self._translate("floating_titlebar.tooltip.close", "Schließen"),
        )

    def _setup_ui(self) -> None:
        """Setup UI layout and widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Title label
        self.title_label = QLabel(self.title_text)
        title_font = QFont()
        title_font.setPointSize(10)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        # Stretch
        layout.addStretch()

        # Pin/Dock button
        self.dock_button = QPushButton("📌")
        self.dock_button.setMaximumWidth(32)
        self.dock_button.setMaximumHeight(26)
        self.dock_button.setToolTip(
            self._translate("floating_titlebar.tooltip.dock", "Zurück ins Dock"),
        )
        self.dock_button.clicked.connect(self.dock_requested.emit)
        layout.addWidget(self.dock_button)

        # Close button
        self.close_button = QPushButton("✕")
        self.close_button.setMaximumWidth(32)
        self.close_button.setMaximumHeight(26)
        self.close_button.setToolTip(
            self._translate("floating_titlebar.tooltip.close", "Schließen"),
        )
        self.close_button.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.close_button)

        # Set fixed height
        self.setMaximumHeight(32)
        self.setMinimumHeight(32)

    def _setup_style(self) -> None:
        """Setup default styling."""
        # Will be updated from theme via stylesheet
        self.setStyleSheet("""
            CustomFloatingTitleBar {
                background-color: #2b2b2b;
                border-bottom: 1px solid #1a1a1a;
            }
            CustomFloatingTitleBar QLabel {
                color: #ffffff;
            }
            CustomFloatingTitleBar QPushButton {
                background-color: #3c3c3c;
                border: none;
                border-radius: 3px;
                color: #ffffff;
                font-weight: bold;
                padding: 2px;
            }
            CustomFloatingTitleBar QPushButton:hover {
                background-color: #4c4c4c;
            }
            CustomFloatingTitleBar QPushButton:pressed {
                background-color: #5c5c5c;
            }
        """)

    def update_theme_style(self, stylesheet: str) -> None:
        """Update styling from theme stylesheet.

        Args:
            stylesheet: QSS stylesheet content
        """
        # Apply custom styles on top of theme
        self.setStyleSheet(stylesheet)

    def set_title(self, title: str) -> None:
        """Update title text.

        Args:
            title: New title
        """
        self.title_text = title
        self.title_label.setText(title)

    def mousePressEvent(self, event: Any) -> None:
        """Start drag operation on title bar press.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Get parent window
            window = self.window()
            if window:
                self._drag_start_pos = event.globalPos() - window.pos()
                event.accept()

    def mouseMoveEvent(self, event: Any) -> None:
        """Handle title bar drag to move window.

        Args:
            event: Mouse event
        """
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            window = self.window()  # type: ignore[unreachable]
            if window:
                new_pos = event.globalPos() - self._drag_start_pos
                window.move(new_pos)
                event.accept()

    def mouseReleaseEvent(self, event: Any) -> None:
        """End drag operation.

        Args:
            event: Mouse event
        """
        self._drag_start_pos = None
        event.accept()
