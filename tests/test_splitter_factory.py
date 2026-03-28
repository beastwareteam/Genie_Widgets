"""Tests for splitter behavior and styling helpers."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QSplitter
import pytest

from widgetsystem.factories.splitter_factory import CornerSplitterHandle, SplitterFactory


pytestmark = [pytest.mark.isolated, pytest.mark.usefixtures("qapp")]


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide a QApplication instance."""
    application = QApplication.instance()
    if not isinstance(application, QApplication):
        application = QApplication([])
    assert isinstance(application, QApplication)
    return application


def test_apply_modern_behavior_sets_collapse_snap() -> None:
    """Modern behavior should mark splitters as collapsible with snap support."""
    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(QLabel("left"))
    splitter.addWidget(QLabel("right"))

    factory = SplitterFactory()
    factory.apply_modern_behavior(splitter, handle_width=2, min_remainder=6)

    assert splitter.handleWidth() == 2
    assert splitter.childrenCollapsible() is True
    assert splitter.property("ws_collapse_snap") == 12
    assert splitter.property("ws_min_remainder") == 6


def test_move_splitter_allows_full_collapse() -> None:
    """Native splitter movement should still allow full collapse at the edge."""
    application = QApplication.instance()
    assert isinstance(application, QApplication)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(QLabel("left"))
    splitter.addWidget(QLabel("right"))
    splitter.resize(220, 120)

    factory = SplitterFactory()
    factory.apply_modern_behavior(splitter, handle_width=2, min_remainder=6)
    splitter.show()
    application.processEvents()

    splitter.moveSplitter(0, 1)
    application.processEvents()

    sizes = splitter.sizes()
    assert sizes[0] == 0, "Linkes Panel sollte vollständig kollabieren"
    assert sizes[1] > 0, "Rechtes Panel sollte sichtbar bleiben"


def test_install_corner_handles_merges_connected_splitter_chain() -> None:
    """Kontaktierende Splitterketten sollten ein gemeinsames Corner-Handle teilen."""
    application = QApplication.instance()
    assert isinstance(application, QApplication)

    outer_splitter = QSplitter(Qt.Orientation.Vertical)
    top_splitter = QSplitter(Qt.Orientation.Horizontal)
    bottom_splitter = QSplitter(Qt.Orientation.Horizontal)

    top_splitter.addWidget(QLabel("oben links"))
    top_splitter.addWidget(QLabel("oben rechts"))
    bottom_splitter.addWidget(QLabel("unten links"))
    bottom_splitter.addWidget(QLabel("unten rechts"))

    outer_splitter.addWidget(top_splitter)
    outer_splitter.addWidget(bottom_splitter)
    outer_splitter.resize(240, 240)

    factory = SplitterFactory()
    for splitter in (outer_splitter, top_splitter, bottom_splitter):
        factory.apply_modern_behavior(splitter, handle_width=2, min_remainder=6)

    outer_splitter.show()
    application.processEvents()

    top_splitter.setSizes([120, 120])
    bottom_splitter.setSizes([120, 120])
    outer_splitter.setSizes([120, 120])
    application.processEvents()

    factory.install_corner_handles(outer_splitter)
    application.processEvents()

    handles = outer_splitter.findChildren(CornerSplitterHandle)
    assert len(handles) == 1, "Verbundene Splitter sollten ein Handle ergeben"

    corner_handle = handles[0]
    assert corner_handle.horizontal_binding_count() == 2, (
        "Beide X-Achsen-Splitter müssen gebunden sein"
    )
    assert corner_handle.vertical_binding_count() == 1, "Die gemeinsame Y-Achse muss gebunden sein"


def test_hierarchical_drag_cascade_collapses_forward_panel_in_positive_direction() -> None:
    """Horizontal cascade should continue in positive drag direction (right side)."""
    application = QApplication.instance()
    assert isinstance(application, QApplication)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(QLabel("p1"))
    splitter.addWidget(QLabel("p2"))
    splitter.addWidget(QLabel("p3"))
    splitter.addWidget(QLabel("p4"))
    splitter.resize(900, 120)

    factory = SplitterFactory()
    factory.apply_modern_behavior(splitter, handle_width=2, min_remainder=6)
    splitter.show()
    application.processEvents()

    splitter.setSizes([220, 220, 220, 220])
    application.processEvents()

    # Collapse primary right-adjacent panel at handle index 2 first.
    splitter.moveSplitter(splitter.width(), 2)
    application.processEvents()

    before_sizes = splitter.sizes()
    applied = factory.apply_hierarchical_drag_cascade(
        splitter,
        handle_index=2,
        direction=1,
        drag_step=90,
    )
    application.processEvents()
    after_sizes = splitter.sizes()

    assert applied is True, "Kaskade sollte in positiver Richtung ausgelöst werden"
    assert after_sizes[3] < before_sizes[3], "Panel vor der Maus (rechts) muss kollabieren"


def test_hierarchical_drag_cascade_collapses_forward_panel_in_negative_direction() -> None:
    """Horizontal cascade should continue in negative drag direction (left side)."""
    application = QApplication.instance()
    assert isinstance(application, QApplication)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(QLabel("p1"))
    splitter.addWidget(QLabel("p2"))
    splitter.addWidget(QLabel("p3"))
    splitter.addWidget(QLabel("p4"))
    splitter.resize(900, 120)

    factory = SplitterFactory()
    factory.apply_modern_behavior(splitter, handle_width=2, min_remainder=6)
    splitter.show()
    application.processEvents()

    splitter.setSizes([220, 220, 220, 220])
    application.processEvents()

    # Collapse primary left-adjacent panel at handle index 2 first.
    splitter.moveSplitter(0, 2)
    application.processEvents()

    before_sizes = splitter.sizes()
    applied = factory.apply_hierarchical_drag_cascade(
        splitter,
        handle_index=2,
        direction=-1,
        drag_step=90,
    )
    application.processEvents()
    after_sizes = splitter.sizes()

    assert applied is True, "Kaskade sollte in negativer Richtung ausgelöst werden"
    assert after_sizes[0] < before_sizes[0], "Panel vor der Maus (links) muss kollabieren"


def test_hierarchical_drag_cascade_reopens_forward_panel_from_positive_edge() -> None:
    """When dragging away from right edge, right-side chain should reopen sequentially."""
    application = QApplication.instance()
    assert isinstance(application, QApplication)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(QLabel("p1"))
    splitter.addWidget(QLabel("p2"))
    splitter.addWidget(QLabel("p3"))
    splitter.addWidget(QLabel("p4"))
    splitter.resize(900, 120)

    factory = SplitterFactory()
    factory.apply_modern_behavior(splitter, handle_width=2, min_remainder=6)
    splitter.show()
    application.processEvents()

    splitter.setSizes([220, 220, 220, 220])
    application.processEvents()

    splitter.moveSplitter(splitter.width(), 2)
    application.processEvents()

    # Force next right-side panel close once, then verify reopening.
    factory.apply_hierarchical_drag_cascade(splitter, handle_index=2, direction=1, drag_step=90)
    application.processEvents()

    # Simulate dragging active handle away from the right edge (opening intent).
    splitter.moveSplitter(splitter.width() - 80, 2)
    application.processEvents()
    before_sizes = splitter.sizes()

    applied = factory.apply_hierarchical_drag_cascade(
        splitter,
        handle_index=2,
        direction=-1,
        drag_step=90,
        edge_hint="max",
    )
    application.processEvents()
    after_sizes = splitter.sizes()

    assert applied is True, "Wiederöffnen an der rechten Kette sollte ausgelöst werden"
    assert after_sizes[3] > before_sizes[3], "Rechtes Folgepanel muss wieder aufgehen"


def test_hierarchical_drag_cascade_reopens_forward_panel_from_negative_edge() -> None:
    """When dragging away from left edge, left-side chain should reopen sequentially."""
    application = QApplication.instance()
    assert isinstance(application, QApplication)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(QLabel("p1"))
    splitter.addWidget(QLabel("p2"))
    splitter.addWidget(QLabel("p3"))
    splitter.addWidget(QLabel("p4"))
    splitter.resize(900, 120)

    factory = SplitterFactory()
    factory.apply_modern_behavior(splitter, handle_width=2, min_remainder=6)
    splitter.show()
    application.processEvents()

    splitter.setSizes([220, 220, 220, 220])
    application.processEvents()

    splitter.moveSplitter(0, 2)
    application.processEvents()

    # Force next left-side panel close once, then verify reopening.
    factory.apply_hierarchical_drag_cascade(splitter, handle_index=2, direction=-1, drag_step=90)
    application.processEvents()
    before_sizes = splitter.sizes()

    applied = factory.apply_hierarchical_drag_cascade(
        splitter,
        handle_index=2,
        direction=1,
        drag_step=90,
    )
    application.processEvents()
    after_sizes = splitter.sizes()

    assert applied is True, "Wiederöffnen an der linken Kette sollte ausgelöst werden"
    assert after_sizes[0] > before_sizes[0], "Linkes Folgepanel muss wieder aufgehen"