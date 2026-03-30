"""Title Bar Button Collapser.

Replaces action buttons in every CDockAreaTitleBar with a ◁ arrow.
Default: only the arrow is visible.
Hover anywhere on the title bar → buttons appear.
Cursor leaves the entire title bar → buttons collapse again.

Strategy
--------
* All direct-child QAbstractButton children of the title bar are hidden.
* A ◁ QPushButton (TitleBarArrowBtn) is placed at the right edge via
  setGeometry, updated on every Resize event.
* Enter on the title bar or the arrow → _do_expand().
* A cursor-poll timer checks whether the cursor has left the full title-bar
  rect; if so it calls _do_collapse().
"""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import (
    QEvent,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTimer,
    Qt,
    Slot,
)
from PySide6.QtGui import QCursor
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractButton, QPushButton, QToolButton, QWidget

logger = logging.getLogger(__name__)

CHECK_INTERVAL: int = 40   # ms – cursor-leave poll rate
ARROW_BTN_SIZE: int = 16   # px – width of the ◁ button itself
ARROW_MARGIN_RIGHT: int = 4   # px – gap between arrow and title-bar right edge
ARROW_VERTICAL_INSET: int = 3  # px – top/bottom inset


_CLOSE_NAMES = {"closeButton", "dockAreaCloseButton", "CloseButton", "DockAreaCloseButton"}


def _btn_stylesheet(object_name: str) -> str:
    """Inline stylesheet for a managed title-bar button."""
    base = (
        "QAbstractButton, QToolButton {"
        " background-color: rgb(25, 30, 52);"
        " border: 1px solid rgb(42, 55, 90);"
        " border-radius: 4px;"
        " color: #a0adcc;"
        " font-size: 12px;"
        " min-width: 20px; max-width: 20px;"
        " min-height: 20px; max-height: 20px;"
        " padding: 0px; margin: 0px;"
        " text-align: center;"
        "}"
    )
    if object_name in _CLOSE_NAMES:
        return (
            base
            + "QAbstractButton:hover, QToolButton:hover {"
            " background-color: rgba(200, 50, 50, 0.30);"
            " border-color: rgba(220, 70, 70, 0.60);"
            " color: #ff7070;"
            "}"
            "QAbstractButton:pressed, QToolButton:pressed {"
            " background-color: rgba(200, 50, 50, 0.50);"
            " border-color: rgba(220, 70, 70, 0.80);"
            " color: #ffffff;"
            "}"
        )
    return (
        base
        + "QAbstractButton:hover, QToolButton:hover {"
        " background-color: rgba(61, 127, 255, 0.20);"
        " border-color: rgba(61, 127, 255, 0.55);"
        " color: #d0daff;"
        "}"
        "QAbstractButton:pressed, QToolButton:pressed {"
        " background-color: rgba(61, 127, 255, 0.35);"
        " border-color: #3d7fff;"
        " color: #ffffff;"
        "}"
    )


# ── Per-area controller ───────────────────────────────────────────────────────


class _AreaCollapser(QObject):
    """Manages arrow ↔ buttons toggle for one CDockAreaWidget."""

    def __init__(self, dock_area: Any, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._area = dock_area
        self._arrow: QPushButton | None = None
        self._buttons: list[QWidget] = []
        self._open = False

        self._collapse_timer = QTimer(self)
        self._collapse_timer.setInterval(CHECK_INTERVAL)
        self._collapse_timer.timeout.connect(self._check_collapse)

        # Give the title bar time to be fully laid out before setup
        QTimer.singleShot(100, self._setup)

    # ── Setup / refresh ───────────────────────────────────────────────────────

    def _setup(self) -> None:
        tb = self._title_bar()
        if tb is None:
            return

        # Remove leftover arrow from a previous setup
        if self._arrow is not None:
            self._arrow.deleteLater()
            self._arrow = None
        self._buttons = []

        # Collect ALL direct-child action buttons.
        # FindDirectChildrenOnly skips the tab-close buttons that live
        # deeper inside CDockTabBar.
        self._buttons = [
            btn
            for btn in tb.findChildren(
                QAbstractButton,
                options=Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if btn.objectName() != "TitleBarArrowBtn"
        ]

        if not self._buttons:
            return

        # Replace QtAds icon-based rendering with text symbols and apply
        # a direct stylesheet so buttons are visually identical to all
        # other themed buttons (InlayTitleBar, toolbar, etc.).
        _SYMBOLS: dict[str, str] = {
            "tabsMenuButton":        "▾",
            "detachGroupButton":     "❐",
            "dockAreaAutoHideButton": "◂",
            "dockAreaMinimizeButton": "─",
            "dockAreaCloseButton":   "✕",
            "closeButton":           "✕",
        }
        for btn in self._buttons:
            try:
                name = btn.objectName()
                symbol = _SYMBOLS.get(name, "✕" if name in _CLOSE_NAMES else "•")
                # Clear icon and switch to text-only rendering
                btn.setIcon(QIcon())
                if isinstance(btn, QToolButton):
                    btn.setToolButtonStyle(
                        Qt.ToolButtonStyle.ToolButtonTextOnly
                    )
                btn.setText(symbol)
                btn.setStyleSheet(_btn_stylesheet(name))
            except RuntimeError:
                pass

        # Build the arrow button as a child of the title bar
        arrow = QPushButton("◁", tb)
        arrow.setObjectName("TitleBarArrowBtn")
        arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        arrow.setFlat(True)
        arrow.setStyleSheet(
            """
            QPushButton#TitleBarArrowBtn {
                color: rgba(150, 185, 245, 0.82);
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton#TitleBarArrowBtn:hover {
                color: rgba(210, 230, 255, 1.0);
            }
            """
        )
        # Arrow Enter triggers expand
        arrow.installEventFilter(self)
        self._arrow = arrow

        # Title bar Enter/Leave/Resize events
        tb.installEventFilter(self)

        self._reposition_arrow()
        self._do_collapse()

        # Re-position after layout has fully settled
        QTimer.singleShot(150, self._reposition_arrow)

    def refresh(self) -> None:
        """Re-run setup after a title-bar recreation (re-dock / float)."""
        self._open = False
        self._collapse_timer.stop()
        QTimer.singleShot(100, self._setup)

    # ── Arrow geometry ────────────────────────────────────────────────────────

    def _reposition_arrow(self) -> None:
        tb = self._title_bar()
        if tb is None or self._arrow is None:
            return
        tbw = tb.width()
        tbh = max(tb.height(), 20)
        if tbw < 2:
            # Title bar not sized yet – try again shortly
            QTimer.singleShot(80, self._reposition_arrow)
            return
        self._arrow.setGeometry(
            tbw - ARROW_BTN_SIZE - ARROW_MARGIN_RIGHT, 0, ARROW_BTN_SIZE, tbh
        )
        self._arrow.raise_()

    # ── Collapse / expand ─────────────────────────────────────────────────────

    def _do_collapse(self) -> None:
        self._open = False
        self._collapse_timer.stop()
        for btn in self._buttons:
            try:
                btn.setVisible(False)
            except RuntimeError:
                pass
        if self._arrow is not None:
            self._arrow.show()
            self._arrow.raise_()

    def _do_expand(self) -> None:
        if self._open:
            return
        self._open = True
        if self._arrow is not None:
            self._arrow.hide()

        # Determine how many dock widgets share this area (for tabsMenuButton)
        try:
            tab_count = self._area.dockWidgetsCount()
        except (RuntimeError, AttributeError):
            tab_count = 2  # fallback: assume multi-tab

        for btn in self._buttons:
            try:
                name = btn.objectName()
                if name == "tabsMenuButton":
                    btn.setVisible(tab_count > 1)
                else:
                    btn.setVisible(True)
            except RuntimeError:
                pass
        self._collapse_timer.start()

    # ── Collapse check ────────────────────────────────────────────────────────

    def _check_collapse(self) -> None:
        """Collapse only when cursor has left the entire title bar."""
        cursor = QCursor.pos()
        tb = self._title_bar()
        if tb is not None:
            try:
                r = QRect(
                    tb.mapToGlobal(QPoint(0, 0)),
                    QSize(tb.width(), tb.height()),
                )
                if r.contains(cursor):
                    return  # still on the title bar – stay open
            except RuntimeError:
                pass
        self._collapse_timer.stop()
        self._do_collapse()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _title_bar(self) -> QWidget | None:
        try:
            if hasattr(self._area, "titleBar"):
                return self._area.titleBar()  # type: ignore[return-value]
        except RuntimeError:
            pass
        return None

    # ── Event filter ──────────────────────────────────────────────────────────

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: ANN001
        try:
            t = event.type()
            if obj is self._arrow:
                # Arrow entered → expand
                if t == QEvent.Type.Enter:
                    self._do_expand()
            else:
                # Title bar events
                if t == QEvent.Type.Enter:
                    self._do_expand()
                elif t == QEvent.Type.Leave:
                    # Start the poll; collapse fires when cursor leaves the
                    # full title-bar rect (not just the button area)
                    if self._open:
                        self._collapse_timer.start()
                elif t == QEvent.Type.Resize:
                    self._reposition_arrow()
        except RuntimeError:
            pass
        return False


# ── Manager ───────────────────────────────────────────────────────────────────


class TitleBarButtonCollapserManager(QObject):
    """Installs _AreaCollapser on every CDockAreaWidget – now and in future."""

    def __init__(self, dock_manager: Any, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._dock_manager = dock_manager
        self._collapsers: dict[int, _AreaCollapser] = {}

        QTimer.singleShot(0, self._install_on_all_existing)

        try:
            dock_manager.dockWidgetAdded.connect(self._on_dock_widget_added)
        except Exception:  # noqa: BLE001
            pass

    @Slot()
    def _install_on_all_existing(self) -> None:
        try:
            for dock in self._dock_manager.openedDockWidgets():
                self._ensure_collapser(dock)
        except Exception:  # noqa: BLE001
            pass

    @Slot(object)
    def _on_dock_widget_added(self, dock_widget: Any) -> None:
        QTimer.singleShot(0, lambda: self._ensure_collapser(dock_widget))

    def _ensure_collapser(self, dock_widget: Any) -> None:
        try:
            area = dock_widget.dockAreaWidget()
            if area is None:
                return
            key = id(area)
            if key not in self._collapsers:
                self._collapsers[key] = _AreaCollapser(area, parent=self)
        except RuntimeError:
            pass

    def refresh_area(self, area: Any) -> None:
        """Called by FloatingStateTracker after a title-bar recreation."""
        try:
            key = id(area)
            if key in self._collapsers:
                self._collapsers[key].refresh()
            else:
                self._collapsers[key] = _AreaCollapser(area, parent=self)
        except RuntimeError:
            pass
