"""Dock Slide-Out Controller – collapse each dock to a narrow arrow strip.

Default view
------------
Each controlled CDockAreaWidget collapses to a thin vertical strip
(STRIP_WIDTH px) that sits exactly where the panel lives in the layout.
An opaque overlay (_ArrowStrip) covers the strip and shows a ◁ arrow.

On hover
--------
The strip expands to *expanded_width* px (sliding out sideways); once
fully open the overlay hides and the normal panel content becomes visible.
Moving the cursor away reverses the animation.

The arrow stays at the panel's natural splitter position – it is NOT
a floating element at the window edge.

Usage::

    ctrl = DockSlideOutController(dock_area, expanded_width=280)
    self._slide_controllers.append(ctrl)   # keep alive
"""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTimer,
    QVariantAnimation,
    Qt,
)
from PySide6.QtGui import QColor, QCursor, QPainter
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

STRIP_WIDTH: int = 28          # px – width of the collapsed arrow strip
ANIMATION_DURATION: int = 200  # ms
COLLAPSE_CHECK_INTERVAL: int = 50
QWIDGETSIZE_MAX: int = 16_777_215


# ── Arrow Strip ───────────────────────────────────────────────────────────────


class _ArrowStrip(QWidget):
    """Opaque overlay parented to the dock area.

    Covers the dock area completely when collapsed so the messy
    title-bar content is not visible.  Shows ◁ centred vertically.
    """

    def __init__(self, dock_area: QWidget) -> None:
        super().__init__(dock_area)
        self.setObjectName("DockArrowStrip")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel("◁")
        self._label.setObjectName("DockArrowLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        self.setStyleSheet(
            """
            #DockArrowStrip {
                background: rgba(22, 30, 48, 0.96);
                border-right: 1px solid rgba(80, 120, 200, 0.35);
            }
            #DockArrowLabel {
                color: rgba(140, 175, 240, 0.92);
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
            """
        )
        self.hide()

    def paintEvent(self, event: Any) -> None:  # noqa: ANN401
        super().paintEvent(event)
        # Subtle right-edge accent line
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(QColor(80, 130, 220, 130))
        painter.drawLine(self.width() - 1, 8, self.width() - 1, self.height() - 8)
        painter.end()


# ── Controller ────────────────────────────────────────────────────────────────


class DockSlideOutController(QObject):
    """Manages the collapse / expand of a single CDockAreaWidget.

    Animation strategy
    ------------------
    Both *minimumWidth* and *maximumWidth* are driven together so the
    QSplitter is forced to give exactly the animated value on every frame.
    The _ArrowStrip overlay covers the panel during animation so the
    partially-visible title bar is never seen.
    """

    def __init__(
        self,
        dock_area: Any,
        expanded_width: int = 280,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent or dock_area)

        self._area = dock_area
        self._expanded_width = expanded_width
        self._expanded = False

        # Overlay strip (child of dock_area so it moves with the panel)
        self._strip = _ArrowStrip(dock_area)

        # Animate min+max width simultaneously
        self._anim: QVariantAnimation = QVariantAnimation(self)
        self._anim.setDuration(ANIMATION_DURATION)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.valueChanged.connect(self._on_width_value)
        self._anim.finished.connect(self._on_anim_finished)

        # Collapse-check timer
        self._collapse_timer = QTimer(self)
        self._collapse_timer.setInterval(COLLAPSE_CHECK_INTERVAL)
        self._collapse_timer.timeout.connect(self._check_collapse)

        # Event filters
        dock_area.installEventFilter(self)
        self._strip.installEventFilter(self)

        # Collapse on first event-loop tick.
        # _setup_slide_out_panels is already delayed past restoreState so
        # self._area is guaranteed to be a live C++ object here.
        QTimer.singleShot(0, self._apply_collapsed_state)

    # ── Animation value handler ───────────────────────────────────────────────

    def _on_width_value(self, value: int) -> None:
        """Called each animation frame – locks panel to exact pixel width."""
        try:
            self._area.setMinimumWidth(value)
            self._area.setMaximumWidth(value)
            # Keep the strip overlay in sync with the current width
            if self._strip.isVisible():
                self._strip.resize(value, self._area.height())
                self._strip.raise_()
        except RuntimeError:
            self._anim.stop()

    def _on_anim_finished(self) -> None:
        try:
            if not self._expanded:
                # Fully collapsed – lock to strip width and show arrow
                self._area.setMinimumWidth(STRIP_WIDTH)
                self._area.setMaximumWidth(STRIP_WIDTH)
                self._strip.setGeometry(0, 0, STRIP_WIDTH, self._area.height())
                self._strip.show()
                self._strip.raise_()
            else:
                # Fully expanded – release constraints, hide strip → content visible
                self._area.setMinimumWidth(0)
                self._area.setMaximumWidth(QWIDGETSIZE_MAX)
                self._strip.hide()
        except RuntimeError:
            pass

    # ── Collapse / Expand ─────────────────────────────────────────────────────

    def _apply_collapsed_state(self) -> None:
        """Collapse immediately without animation (startup)."""
        try:
            self._expanded = False
            self._anim.stop()
            self._area.setMinimumWidth(STRIP_WIDTH)
            self._area.setMaximumWidth(STRIP_WIDTH)
            self._strip.setGeometry(0, 0, STRIP_WIDTH, self._area.height())
            self._strip.show()
            self._strip.raise_()
        except RuntimeError:
            pass

    def _expand(self) -> None:
        if self._expanded:
            return
        self._expanded = True
        self._collapse_timer.stop()

        try:
            # Show strip during animation so title bar innards are covered
            self._strip.setGeometry(0, 0, STRIP_WIDTH, self._area.height())
            self._strip.show()
            self._strip.raise_()
        except RuntimeError:
            self._expanded = False
            return

        self._anim.stop()
        self._anim.setStartValue(STRIP_WIDTH)
        self._anim.setEndValue(self._expanded_width)
        self._anim.start()

        self._collapse_timer.start()

    def _collapse(self) -> None:
        if not self._expanded:
            return
        self._expanded = False
        self._collapse_timer.stop()

        try:
            current_w = max(STRIP_WIDTH, min(self._area.width(), self._expanded_width))
            # Show strip immediately to cover content during collapse
            self._strip.setGeometry(0, 0, current_w, self._area.height())
            self._strip.show()
            self._strip.raise_()
            self._area.setMinimumWidth(current_w)
            self._area.setMaximumWidth(current_w)
        except RuntimeError:
            return

        self._anim.stop()
        self._anim.setStartValue(current_w)
        self._anim.setEndValue(STRIP_WIDTH)
        self._anim.start()

    # ── Collapse check ────────────────────────────────────────────────────────

    def _check_collapse(self) -> None:
        """Collapse when cursor leaves both the panel and the strip."""
        cursor = QCursor.pos()
        for w in (self._area, self._strip):
            try:
                r = QRect(w.mapToGlobal(QPoint(0, 0)), QSize(w.width(), w.height()))
                if r.contains(cursor):
                    return
            except RuntimeError:
                pass
        self._collapse_timer.stop()
        self._collapse()

    # ── Event filter ──────────────────────────────────────────────────────────

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: ANN001
        try:
            t = event.type()

            if obj is self._strip or obj is self._area:
                if t == QEvent.Type.Enter:
                    self._collapse_timer.stop()
                    self._expand()
                elif t == QEvent.Type.Leave:
                    if self._expanded:
                        self._collapse_timer.start()
                elif t == QEvent.Type.Resize and obj is self._area:
                    # Keep strip full-height when dock area is resized
                    if self._strip.isVisible():
                        self._strip.resize(self._strip.width(), self._area.height())
        except RuntimeError:
            pass

        return False
