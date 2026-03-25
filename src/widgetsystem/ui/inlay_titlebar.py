"""Inlay Title Bar - collapsed to 3px strip, expands on mouse hover.

The titlebar sits at the very top of the frameless window:
- Default: 3px colored strip (nearly invisible)
- On hover: smoothly expands to full height (~36px) revealing all controls
- Supports window drag, minimize, maximize/restore, close
- Emits contentOffsetChanged(int) so DockManager can adjust its geometry
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QCursor, QPainter, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

logger = logging.getLogger(__name__)

# ── Load dimensions from config ──────────────────────────────────────────────

def _load_titlebar_dimensions() -> tuple[int, int, int, int]:
    """Load titlebar dimensions from config."""
    try:
        from widgetsystem.factories.ui_dimensions_factory import UIDimensionsFactory
        dims = UIDimensionsFactory.get_instance().get()
        return (
            dims.titlebar.collapsed_height,
            dims.titlebar.collapsed_hit_height,
            dims.titlebar.expanded_height,
            dims.titlebar.animation_duration_ms,
        )
    except Exception:
        return (3, 6, 36, 160)

_dims = _load_titlebar_dimensions()
COLLAPSED_HEIGHT: int = _dims[0]
COLLAPSED_HIT_HEIGHT: int = _dims[1]
EXPANDED_HEIGHT: int = _dims[2]
ANIMATION_DURATION: int = _dims[3]


# ── Inlay Title Bar Widget ────────────────────────────────────────────────────

class InlayTitleBar(QWidget):
    """Thin strip at top of frameless window; expands on hover to show controls."""

    #: Emitted whenever the *visible* height changes (collapsed ↔ expanded).
    #: The integer payload is the new height in pixels.
    contentOffsetChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("InlayTitleBar")

        # Always on top inside the parent, no native frame
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMouseTracking(True)

        # Drag state
        self._drag_start_global: QPoint | None = None
        self._drag_start_window_pos: QPoint | None = None

        # Build child widgets
        self._build_ui()

        # Animate clipping with maximumHeight to avoid invisible children while expanding.
        self._anim = QPropertyAnimation(self, b"maximumHeight")
        self._anim.setDuration(ANIMATION_DURATION)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.finished.connect(self._on_anim_finished)

        self._expanded = False

        # Timer to check if mouse truly left the titlebar area (for collapse)
        self._collapse_timer = QTimer(self)
        self._collapse_timer.setInterval(50)  # Check every 50ms
        self._collapse_timer.timeout.connect(self._check_collapse)

        # No _hover_check_timer: it caused collapse→expand loops when moving
        # from titlebar to toolbar. Expansion relies solely on enterEvent.

        # Start collapsed: use larger hit area (8px) for easier hover
        self.setMinimumHeight(COLLAPSED_HIT_HEIGHT)
        self.setMaximumHeight(COLLAPSED_HIT_HEIGHT)
        self._set_content_visible(False)

        self._apply_style()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 4, 0)
        layout.setSpacing(2)

        # Window title
        self._title_label = QLabel("WidgetSystem")
        self._title_label.setObjectName("TitleLabel")
        self._title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._title_label)

        layout.addSpacerItem(
            QSpacerItem(8, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        )

        self._btn_min = self._make_button("─", "minimize")
        self._btn_max = self._make_button("□", "maximize")
        self._btn_close = self._make_button("✕", "close")

        layout.addWidget(self._btn_min)
        layout.addWidget(self._btn_max)
        layout.addWidget(self._btn_close)

        # Connect
        self._btn_min.clicked.connect(self._on_minimize)
        self._btn_max.clicked.connect(self._on_toggle_max)
        self._btn_close.clicked.connect(self._on_close)

    def _make_button(self, symbol: str, role: str) -> QPushButton:
        btn = QPushButton(symbol)
        btn.setObjectName(f"TitleBtn_{role}")
        btn.setFixedSize(QSize(32, EXPANDED_HEIGHT - 4))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        hover_bg = "rgba(196,43,28,0.90)" if role == "close" else "rgba(255,255,255,0.15)"
        press_bg = "rgba(140,20,20,0.90)" if role == "close" else "rgba(255,255,255,0.08)"

        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 3px;
                color: #E8E8E8;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI Symbol', 'Segoe UI', 'Arial', sans-serif;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background: {press_bg};
                color: #DDDDDD;
            }}
        """)
        
        return btn

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            #InlayTitleBar {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3C4043,
                    stop:1 #2D2E31
                );
                border-bottom: 1px solid rgba(80,80,80,0.6);
            }

            #TitleLabel {
                color: #E8E8E8;
                font-size: 10pt;
                font-weight: 500;
                letter-spacing: 0.5px;
                padding-left: 4px;
            }
        """)

    # ── Title text ────────────────────────────────────────────────────────────

    def set_title(self, title: str) -> None:
        self._title_label.setText(title)

    # ── Expand / Collapse ─────────────────────────────────────────────────────

    def _expand(self) -> None:
        if self._expanded:
            logger.debug("_expand() called but already expanded, skipping")
            return
        logger.debug("_expand() - Starting expansion animation")
        self._expanded = True

        # Make content visible before animation so it appears with the growing clip rect.
        self._set_content_visible(True)

        self._anim.stop()
        self._anim.setStartValue(self.maximumHeight())
        self._anim.setEndValue(EXPANDED_HEIGHT)
        self.setMinimumHeight(0)
        self._anim.start()
        self.contentOffsetChanged.emit(EXPANDED_HEIGHT)
        
        # Start collapse timer to watch for exit
        self._collapse_timer.start()

    def _collapse(self) -> None:
        if not self._expanded:
            logger.debug("_collapse() called but already collapsed, skipping")
            return
        logger.debug("_collapse() - Starting collapse animation")
        self._expanded = False
        self._collapse_timer.stop()

        # Hide content immediately
        self._set_content_visible(False)

        # Allow height to shrink
        self.setMinimumHeight(0)

        self._anim.stop()
        self._anim.setStartValue(self.maximumHeight())
        self._anim.setEndValue(COLLAPSED_HIT_HEIGHT)
        self._anim.start()

        self.contentOffsetChanged.emit(COLLAPSED_HEIGHT)

    def _on_anim_finished(self) -> None:
        if not self._expanded:
            self.setMinimumHeight(COLLAPSED_HIT_HEIGHT)
            self.setMaximumHeight(COLLAPSED_HIT_HEIGHT)
            self._set_content_visible(False)
            self._collapse_timer.stop()
        else:
            self.setMinimumHeight(EXPANDED_HEIGHT)
            self.setMaximumHeight(EXPANDED_HEIGHT)
            # Recheck if mouse is still over titlebar after expansion
            self._check_collapse()

    def _set_content_visible(self, visible: bool) -> None:
        self._title_label.setVisible(visible)
        self._btn_min.setVisible(visible)
        self._btn_max.setVisible(visible)
        self._btn_close.setVisible(visible)

    # ── Mouse event: hover detection ──────────────────────────────────────────

    def enterEvent(self, event: Any) -> None:  # noqa: ANN401
        """Mouse entered the titlebar area - expand it."""
        logger.debug("enterEvent triggered! Expanding...")
        super().enterEvent(event)
        self._collapse_timer.stop()
        self._expand()

    def leaveEvent(self, event: Any) -> None:  # noqa: ANN401
        """Mouse left the titlebar area - start collapse timer."""
        logger.debug("leaveEvent triggered! Starting collapse timer...")
        super().leaveEvent(event)
        if self._expanded:
            self._collapse_timer.start()

    def _check_collapse(self) -> None:
        """Timer callback: collapse only when cursor is truly outside the titlebar.

        Uses global screen coordinates so that hovering over child widgets
        (buttons, label) is correctly treated as still being inside the bar.
        Adds a small margin below to prevent flickering at the edge.
        """
        cursor_pos = QCursor.pos()

        # Build the titlebar rect in global screen coordinates with extra margin below.
        # mapToGlobal(QPoint(0, 0)) gives us the top-left corner on screen;
        # combining it with the widget's current size covers every child widget too.
        # Add 8px margin below to prevent collapse when cursor is near edge
        titlebar_global_rect = QRect(
            self.mapToGlobal(QPoint(0, 0)),
            QSize(self.width(), self.height() + 8),
        )

        is_inside = titlebar_global_rect.contains(cursor_pos)
        logger.debug(f"_check_collapse() - Cursor inside: {is_inside}")

        if not is_inside:
            logger.debug("_check_collapse() - Cursor outside, collapsing...")
            self._collapse_timer.stop()
            self._collapse()

    # ── Window drag via titlebar ──────────────────────────────────────────────

    def mousePressEvent(self, event: Any) -> None:  # noqa: ANN401
        if event.button() == Qt.MouseButton.LeftButton:
            # Stop collapse timer while dragging
            self._collapse_timer.stop()
            win = self._main_window()
            if win:
                self._drag_start_global = event.globalPosition().toPoint()
                self._drag_start_window_pos = win.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Any) -> None:  # noqa: ANN401
        if self._drag_start_global is not None:
            win = self._main_window()
            if win and not win.isMaximized():
                delta = event.globalPosition().toPoint() - self._drag_start_global
                win.move(self._drag_start_window_pos + delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:  # noqa: ANN401
        self._drag_start_global = None
        self._drag_start_window_pos = None

        # After dragging, check immediately if mouse left the titlebar
        if self._expanded:
            self._check_collapse()

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: Any) -> None:  # noqa: ANN401
        """Double-click title bar to toggle maximized."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_toggle_max()
        super().mouseDoubleClickEvent(event)

    # ── Button handlers ───────────────────────────────────────────────────────

    def _on_minimize(self) -> None:
        win = self._main_window()
        if win:
            win.showMinimized()

    def _on_toggle_max(self) -> None:
        win = self._main_window()
        if win:
            if win.isMaximized():
                win.showNormal()
                self._btn_max.setText("□")
            else:
                win.showMaximized()
                self._btn_max.setText("❐")

    def _on_close(self) -> None:
        win = self._main_window()
        if win:
            win.close()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _main_window(self) -> QMainWindow | None:
        """Walk up the widget hierarchy to find the QMainWindow."""
        p = self.parent()
        while p is not None:
            from PySide6.QtWidgets import QMainWindow as _QMW
            if isinstance(p, _QMW):
                return p  # type: ignore[return-value]
            p = p.parent()
        return None

    # ── Paint the thin 3-px indicator strip ───────────────────────────────────

    def paintEvent(self, event: Any) -> None:  # noqa: ANN401
        super().paintEvent(event)
        if not self._expanded and self.height() <= COLLAPSED_HIT_HEIGHT + 2:
            # Draw a subtle accent line across the full width
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            accent = QColor(80, 140, 220, 200)  # soft blue accent
            pen = QPen(accent)
            pen.setWidth(COLLAPSED_HEIGHT)
            painter.setPen(pen)
            mid_y = self.height() // 2
            painter.drawLine(0, mid_y, self.width(), mid_y)
            painter.end()


# ── Controller ────────────────────────────────────────────────────────────────

class InlayTitleBarController:
    """Installs and manages the InlayTitleBar for a QMainWindow."""

    def __init__(self, main_window: Any) -> None:
        self._win = main_window
        self.titlebar: InlayTitleBar | None = None

    def install(self) -> None:
        """Create the titlebar widget, parent it to the main window, and position it."""
        self.titlebar = InlayTitleBar(self._win)
        self.titlebar.raise_()
        self._position()

    def set_title(self, title: str) -> None:
        if self.titlebar:
            self.titlebar.set_title(title)

    def _position(self) -> None:
        """Place the titlebar at the very top of the window, full width."""
        if self.titlebar is None:
            return
        self.titlebar.setGeometry(0, 0, self._win.width(), COLLAPSED_HIT_HEIGHT)

    def on_resize(self, new_width: int) -> None:
        """Call this from the window's resizeEvent to keep width in sync."""
        if self.titlebar is None:
            return
        h = self.titlebar.height()
        self.titlebar.setGeometry(0, 0, new_width, h)
