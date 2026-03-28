"""Tests for UndoRedoWidget i18n support."""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from widgetsystem.core.undo_redo import UndoRedoManager
from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.undo_redo_widget import UndoRedoToolbar, UndoRedoWidget


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide QApplication for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestUndoRedoWidgetI18n:
    """Verify UndoRedoWidget translations and runtime switch."""

    def test_widget_german_labels(self, qapp: QApplication) -> None:
        """Widget should render German labels when i18n locale is de."""
        manager = UndoRedoManager()
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")

        widget = UndoRedoWidget(manager=manager, i18n_factory=i18n_de)

        assert widget._undo_btn.text() == "Rückgängig"
        assert widget._redo_btn.text() == "Wiederholen"
        assert widget._clear_btn.text() == "Löschen"
        assert widget._status_group.title() == "Status"
        assert widget._max_history_label.text() == "Max. Verlauf:"
        assert widget._undo_count_label.text().startswith("Rückgängig:")

    def test_widget_runtime_switch_to_english(self, qapp: QApplication) -> None:
        """Runtime i18n switch should update static and status texts."""
        manager = UndoRedoManager()
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")

        widget = UndoRedoWidget(manager=manager, i18n_factory=i18n_de)
        assert widget._undo_btn.text() == "Rückgängig"

        widget.set_i18n_factory(i18n_en)

        assert widget._undo_btn.text() == "Undo"
        assert widget._redo_btn.text() == "Redo"
        assert widget._clear_btn.text() == "Clear"
        assert widget._max_history_label.text() == "Max History:"
        assert widget._undo_count_label.text().startswith("Undo:")

    def test_toolbar_translations(self, qapp: QApplication) -> None:
        """Toolbar tooltips should be translated and switchable."""
        manager = UndoRedoManager()
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")

        toolbar = UndoRedoToolbar(manager=manager, i18n_factory=i18n_de)
        assert toolbar._undo_btn.toolTip() == "Rückgängig (Strg+Z)"
        assert toolbar._redo_btn.toolTip() == "Wiederholen (Strg+Y)"

        toolbar.set_i18n_factory(i18n_en)
        assert toolbar._undo_btn.toolTip() == "Undo (Ctrl+Z)"
        assert toolbar._redo_btn.toolTip() == "Redo (Ctrl+Y)"

    def test_widget_without_i18n_uses_fallbacks(self, qapp: QApplication) -> None:
        """Without i18n factory, widget should use fallback labels."""
        manager = UndoRedoManager()
        widget = UndoRedoWidget(manager=manager, i18n_factory=None)

        assert widget._undo_btn.text() == "Undo"
        assert widget._redo_btn.text() == "Redo"
        assert widget._clear_btn.text() == "Clear"
