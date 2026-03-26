"""Inlay Titlebar - Collapsible drag handle with window manipulation features.

Modern UI component that provides a slim 3px drag handle that expands to a full
titlebar on mouse hover, featuring window controls (minimize, maximize, close)
and drag-to-move functionality.

This is implemented as a separate top-level window that floats above the main window.
"""

from typing import Any

from PySide6.QtCore import QEasingCurve, QEvent, QPoint, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QCursor, QEnterEvent, QFont, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


class InlayTitleBar(QWidget):
    """Collapsible titlebar with drag handle and window controls.

    This is a separate top-level window that floats above the main window.

    Features:
    - 3px collapsed height (slim drag handle)
    - Expands to full titlebar on mouse hover
    - Window manipulation: minimize, maximize, close
    - Drag-to-move functionality
    - Smooth animations
    - Full window width
    """

    # Visual configuration
    COLLAPSED_HEIGHT = 3
    EXPANDED_HEIGHT = 35
    SPACING_TO_CONTENT = 2  # Additional spacing below titlebar
    ANIMATION_DURATION = 200  # milliseconds
    HOVER_DELAY = 100  # milliseconds before expanding
    COLLAPSE_DELAY = 300  # milliseconds before collapsing

    def __init__(self, parent_window: QWidget) -> None:
        """Initialize inlay titlebar as a child widget with layout integration.

        Args:
            parent_window: The main window to control
        """
        # Create as child widget of parent window
        super().__init__(parent_window)

        self._parent_window = parent_window
        self._drag_pos: QPoint | None = None
        self._is_expanded = False
        self._hover_timer = QTimer(self)
        self._collapse_timer = QTimer(self)
        self._is_maximized = False

        # Enable mouse tracking for hover detection
        self.setMouseTracking(True)

        # Make sure we're visible and can receive mouse events
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Setup UI
        self._setup_ui()
        self._setup_animations()
        self._setup_timers()

        # Initial state: collapsed
        # Total height includes spacing
        self._update_height()
        self._controls_widget.hide()

    def _install_parent_event_filter(self) -> None:
        """Install event filter on parent to track movements/resizes."""
        if self._parent_window:
            self._parent_window.installEventFilter(self)

    def eventFilter(self, obj: Any, event: Any) -> bool:
        """Track parent window events to update titlebar position.

        Args:
            obj: Object that emitted the event
            event: The event

        Returns:
            False to allow normal event processing
        """
        if obj == self._parent_window:
            if event.type() in (QEvent.Type.Move, QEvent.Type.Resize,  QEvent.Type.Show):
                self._update_geometry()
        return False

    def _setup_ui(self) -> None:
        """Setup UI elements."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)

        # Container for controls (hidden when collapsed)
        self._controls_widget = QWidget(self)
        controls_layout = QHBoxLayout(self._controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)

        # Window title
        self._title_label = QLabel("WidgetSystem", self._controls_widget)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self._title_label.setFont(title_font)
        controls_layout.addWidget(self._title_label)

        # Spacer
        controls_layout.addStretch()

        # Window control buttons
        self._minimize_btn = self._create_control_button("−", "Minimieren")
        self._maximize_btn = self._create_control_button("□", "Maximieren")
        self._close_btn = self._create_control_button("×", "Schließen")

        controls_layout.addWidget(self._minimize_btn)
        controls_layout.addWidget(self._maximize_btn)
        controls_layout.addWidget(self._close_btn)

        layout.addWidget(self._controls_widget)

        # Connect button actions
        self._minimize_btn.clicked.connect(self._on_minimize)
        self._maximize_btn.clicked.connect(self._on_maximize)
        self._close_btn.clicked.connect(self._on_close)

        # Apply stylesheet
        self._apply_stylesheet()

    def _create_control_button(self, text: str, tooltip: str) -> QPushButton:
        """Create a window control button.

        Args:
            text: Button text (symbol)
            tooltip: Button tooltip

        Returns:
            Configured QPushButton
        """
        btn = QPushButton(text, self._controls_widget)
        btn.setFixedSize(28, 24)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Button font
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        btn.setFont(font)

        return btn

    def _setup_animations(self) -> None:
        """Setup smooth height animations."""
        self._height_animation = QPropertyAnimation(self, b"maximumHeight")
        self._height_animation.setDuration(self.ANIMATION_DURATION)
        self._height_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Opacity animation for controls
        self._opacity_effect = QGraphicsOpacityEffect(self._controls_widget)
        self._controls_widget.setGraphicsEffect(self._opacity_effect)

        self._opacity_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._opacity_animation.setDuration(self.ANIMATION_DURATION)
        self._opacity_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def _setup_timers(self) -> None:
        """Setup hover and collapse timers."""
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._expand)

        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.timeout.connect(self._collapse)

    def _apply_stylesheet(self) -> None:
        """Apply visual styling."""
        self.setStyleSheet(
            f"""
            InlayTitleBar {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 0, 0, 255),
                    stop:1 rgba(200, 0, 0, 255)
                );
                border: none;
                border-bottom: {self.SPACING_TO_CONTENT}px solid transparent;
            }}

            QPushButton {{
                background: rgba(70, 70, 70, 150);
                border: 1px solid rgba(100, 100, 100, 100);
                border-radius: 3px;
                color: #FFFFFF;
                padding: 0px;
            }}

            QPushButton:hover {{
                background: rgba(90, 90, 90, 200);
                border: 1px solid rgba(120, 120, 120, 150);
            }}

            QPushButton:pressed {{
                background: rgba(50, 50, 50, 220);
            }}

            QPushButton#close_btn:hover {{
                background: rgba(200, 50, 50, 200);
                border: 1px solid rgba(220, 70, 70, 150);
            }}

            QLabel {{
                color: #FFFFFF;
                background: transparent;
            }}
            """
        )
        self._close_btn.setObjectName("close_btn")

    def _update_geometry(self) -> None:
        """Update position to span full parent window width at top."""
        if self._parent_window and self._parent_window.isVisible():
            # Position above parent window's top-left corner
            parent_pos = self._parent_window.mapToGlobal(QPoint(0, 0))
            # Height includes spacing to content
            total_height = self.COLLAPSED_HEIGHT if not self._is_expanded else self.EXPANDED_HEIGHT
            total_height += self.SPACING_TO_CONTENT
            self.setGeometry(
                parent_pos.x(),
                parent_pos.y(),
                self._parent_window.width(),
                total_height
            )

    def _expand(self) -> None:
        """Expand titlebar to show controls."""
        if self._is_expanded:
            return

        self._is_expanded = True
        self._collapse_timer.stop()

        # Animate height
        self._height_animation.setStartValue(self.COLLAPSED_HEIGHT)
        self._height_animation.setEndValue(self.EXPANDED_HEIGHT)
        self._height_animation.start()

        # Show and fade in controls
        self._controls_widget.show()
        self._opacity_animation.setStartValue(0.0)
        self._opacity_animation.setEndValue(1.0)
        self._opacity_animation.start()

        # Update cursor
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _collapse(self) -> None:
        """Collapse titlebar to slim handle."""
        if not self._is_expanded:
            return

        self._is_expanded = False
        self._hover_timer.stop()

        # Fade out controls first
        self._opacity_animation.setStartValue(1.0)
        self._opacity_animation.setEndValue(0.0)
        self._opacity_animation.finished.connect(self._on_fade_complete, Qt.ConnectionType.SingleShotConnection)
        self._opacity_animation.start()

        # Animate height
        self._height_animation.setStartValue(self.EXPANDED_HEIGHT)
        self._height_animation.setEndValue(self.COLLAPSED_HEIGHT)
        self._height_animation.start()

        # Update cursor
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def _on_fade_complete(self) -> None:
        """Hide controls after fade out animation."""
        if not self._is_expanded:
            self._controls_widget.hide()

    def enterEvent(self, event: QEnterEvent) -> None:
        """Handle mouse enter - start expand timer.

        Args:
            event: Enter event
        """
        self._collapse_timer.stop()
        self._hover_timer.start(self.HOVER_DELAY)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave - start collapse timer.

        Args:
            event: Leave event
        """
        self._hover_timer.stop()
        self._collapse_timer.start(self.COLLAPSE_DELAY)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press - start drag.

        Args:
            event: Mouse press event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._parent_window.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move - perform drag.

        Args:
            event: Mouse move event
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self._parent_window.move(new_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release - end drag.

        Args:
            event: Mouse release event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            event.accept()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double click - toggle maximize.

        Args:
            event: Mouse double click event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_maximize()
            event.accept()
        super().mouseDoubleClickEvent(event)

    def _on_minimize(self) -> None:
        """Handle minimize button click."""
        if self._parent_window:
            self._parent_window.showMinimized()

    def _on_maximize(self) -> None:
        """Handle maximize/restore button click."""
        if not self._parent_window:
            return

        if self._is_maximized:
            self._parent_window.showNormal()
            self._maximize_btn.setText("□")
            self._maximize_btn.setToolTip("Maximieren")
            self._is_maximized = False
        else:
            self._parent_window.showMaximized()
            self._maximize_btn.setText("❐")
            self._maximize_btn.setToolTip("Wiederherstellen")
            self._is_maximized = True

    def _on_close(self) -> None:
        """Handle close button click."""
        if self._parent_window:
            self._parent_window.close()

    def set_title(self, title: str) -> None:
        """Set window title text.

        Args:
            title: New window title
        """
        self._title_label.setText(title)

    def resizeEvent(self, event: Any) -> None:
        """Handle parent window resize.

        Args:
            event: Resize event
        """
        self._update_geometry()
        super().resizeEvent(event)

    def showEvent(self, event: Any) -> None:
        """Handle show event - ensure proper positioning.

        Args:
            event: Show event
        """
        self._update_geometry()
        super().showEvent(event)


class InlayTitleBarController:
    """Controller to manage inlay titlebar for a window.

    Handles installation, lifecycle, and integration with main window.
    """

    def __init__(self, main_window: QWidget) -> None:
        """Initialize controller.

        Args:
            main_window: The main window to add titlebar to
        """
        self.main_window = main_window
        self.titlebar: InlayTitleBar | None = None

    def install(self) -> None:
        """Install inlay titlebar on main window."""
        if self.titlebar is not None:
            return  # Already installed

        self.titlebar = InlayTitleBar(self.main_window)
        self.titlebar.show()
        self.titlebar.raise_()

        # Update on window resize
        if hasattr(self.main_window, "resizeEvent"):
            original_resize = self.main_window.resizeEvent

            def new_resize(event: Any) -> None:
                original_resize(event)
                if self.titlebar:
                    self.titlebar.setGeometry(
                        0,
                        0,
                        self.main_window.width(),
                        self.titlebar.height(),
                    )

            self.main_window.resizeEvent = new_resize  # type: ignore[method-assign]

    def uninstall(self) -> None:
        """Remove inlay titlebar from main window."""
        if self.titlebar:
            self.titlebar.deleteLater()
            self.titlebar = None

    def set_title(self, title: str) -> None:
        """Update window title.

        Args:
            title: New window title
        """
        if self.titlebar:
            self.titlebar.set_title(title)
