"""Focused i18n tests for UnifiedTabItem."""

from pathlib import Path
import sys

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QLabel, QTabWidget
import pytest


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.unified_tab_item import UnifiedTabItem


@pytest.fixture(scope="module")
def qapp_instance() -> QApplication:
    """Provide QApplication instance."""
    app = QApplication.instance()
    if app is None or not isinstance(app, QApplication):
        app = QApplication(sys.argv)
    return app


@pytest.mark.usefixtures("qapp_instance")
class TestUnifiedTabItemI18n:
    """Verify translated visible strings in unified tab item actions."""

    def _create_item(self, i18n_factory: I18nFactory) -> UnifiedTabItem:
        tab_widget = QTabWidget()
        content = QLabel("content")
        tab_widget.addTab(content, "My Tab")

        return UnifiedTabItem(
            tab_id="tab-1",
            title="My Tab",
            content_widget=content,
            parent_tab_widget=tab_widget,
            tab_index=0,
            config={"closable": True, "floatable": True},
            i18n_factory=i18n_factory,
        )

    def _collect_action_texts(self, item: UnifiedTabItem, monkeypatch: pytest.MonkeyPatch) -> list[str]:
        actions: list[str] = []

        class DummySignal:
            def connect(self, _callback: object) -> None:
                return None

        class DummyAction:
            def __init__(self, text: str, _menu: object) -> None:
                self.text = text
                self.triggered = DummySignal()

        class DummyMenu:
            def addAction(self, action: DummyAction) -> None:
                actions.append(action.text)

            def addSeparator(self) -> None:
                return None

            def exec(self, _pos: QPoint) -> None:
                return None

        monkeypatch.setattr("widgetsystem.ui.unified_tab_item.QMenu", DummyMenu)
        monkeypatch.setattr("widgetsystem.ui.unified_tab_item.QAction", DummyAction)

        item.show_context_menu(QPoint(0, 0))
        return actions

    def test_context_menu_uses_german_labels(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """German locale should render German context menu labels."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        item = self._create_item(i18n_de)

        actions = self._collect_action_texts(item, monkeypatch)

        assert actions == [
            "Schließen",
            "Andere schließen",
            "Tabs rechts schließen",
            "Auskoppeln",
            "Tab-Einstellungen...",
        ]

    def test_runtime_switch_updates_context_menu_labels(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Runtime locale switch should update context menu labels."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")
        item = self._create_item(i18n_de)

        item.set_i18n_factory(i18n_en)
        actions = self._collect_action_texts(item, monkeypatch)

        assert actions == [
            "Close",
            "Close Others",
            "Close Tabs to Right",
            "Float",
            "Tab Settings...",
        ]
