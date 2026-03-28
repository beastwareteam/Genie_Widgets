"""i18n tests for visual layer components."""

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.visual_layer import (
    ListsViewer,
    MenusViewer,
    PanelsViewer,
    TabsViewer,
    ViewerConfig,
    VisualDashboard,
)


@pytest.fixture
def qapp_fixture() -> QApplication:
    """Ensure QApplication exists for widget tests."""
    app_instance = QApplication.instance()
    if app_instance is None:
        app = QApplication(sys.argv)
    else:
        app = app_instance
    assert isinstance(app, QApplication)
    app.setQuitOnLastWindowClosed(False)
    return app


class TestVisualLayerI18n:
    """Validate visual layer i18n behavior."""

    def test_lists_viewer_german_labels(self, qapp_fixture: QApplication) -> None:
        """ListsViewer shows German labels with DE locale."""
        _ = qapp_fixture
        i18n_de = I18nFactory(Path("config"), locale="de")
        viewer = ListsViewer(Path("config"), i18n_de, config=ViewerConfig(show_properties=True))
        labels = [label.text() for label in viewer.findChildren(QLabel)]

        assert "Listen" in labels
        assert viewer.tree.headerItem().text(0) == "Listen-Hierarchie"
        assert "Eigenschaften" in labels

    def test_lists_viewer_runtime_locale_switch(self, qapp_fixture: QApplication) -> None:
        """ListsViewer updates static labels when locale changes at runtime."""
        _ = qapp_fixture
        i18n_de = I18nFactory(Path("config"), locale="de")
        i18n_en = I18nFactory(Path("config"), locale="en")
        viewer = ListsViewer(Path("config"), i18n_de, config=ViewerConfig(show_properties=True))

        viewer.set_i18n_factory(i18n_en)
        labels = [label.text() for label in viewer.findChildren(QLabel)]

        assert "Lists" in labels
        assert viewer.tree.headerItem().text(0) == "List Hierarchy"
        assert "Properties" in labels

    def test_dashboard_runtime_locale_switch_updates_title_and_tabs(
        self,
        qapp_fixture: QApplication,
    ) -> None:
        """VisualDashboard updates window title and tab names on runtime locale switch."""
        _ = qapp_fixture
        i18n_de = I18nFactory(Path("config"), locale="de")
        i18n_en = I18nFactory(Path("config"), locale="en")
        dashboard = VisualDashboard(Path("config"), i18n_de)

        assert dashboard.windowTitle() == "Visuelles Dashboard"
        assert dashboard.tabs.tabText(0) == "Listen"
        assert dashboard.tabs.tabText(1) == "Menüs"

        dashboard.set_i18n_factory(i18n_en)

        assert dashboard.windowTitle() == "Visual Dashboard"
        assert dashboard.tabs.tabText(0) == "Lists"
        assert dashboard.tabs.tabText(1) == "Menus"

    def test_panels_viewer_runtime_locale_switch_updates_properties_title(
        self,
        qapp_fixture: QApplication,
    ) -> None:
        """PanelsViewer updates panel properties title when locale changes."""
        _ = qapp_fixture
        i18n_de = I18nFactory(Path("config"), locale="de")
        i18n_en = I18nFactory(Path("config"), locale="en")
        viewer = PanelsViewer(Path("config"), i18n_de, config=ViewerConfig(show_properties=True))
        labels_before = [label.text() for label in viewer.findChildren(QLabel)]

        assert "Panel-Eigenschaften" in labels_before

        viewer.set_i18n_factory(i18n_en)
        labels_after = [label.text() for label in viewer.findChildren(QLabel)]

        assert "Panel Properties" in labels_after

    def test_panels_viewer_runtime_locale_switch_updates_field_labels(
        self,
        qapp_fixture: QApplication,
    ) -> None:
        """PanelsViewer updates properties field labels when locale changes."""
        _ = qapp_fixture
        i18n_de = I18nFactory(Path("config"), locale="de")
        i18n_en = I18nFactory(Path("config"), locale="en")
        viewer = PanelsViewer(Path("config"), i18n_de, config=ViewerConfig(show_properties=True))

        labels_before = [label.text() for label in viewer.findChildren(QLabel)]
        assert "Bereich:" in labels_before
        assert "Beschreibung:" in labels_before

        viewer.set_i18n_factory(i18n_en)

        labels_after = [label.text() for label in viewer.findChildren(QLabel)]
        assert "Area:" in labels_after
        assert "Description:" in labels_after

    @pytest.mark.parametrize("viewer_class", [ListsViewer, MenusViewer, TabsViewer])
    def test_tree_viewers_runtime_locale_switch_updates_selected_properties_text(
        self,
        qapp_fixture: QApplication,
        viewer_class: type[ListsViewer] | type[MenusViewer] | type[TabsViewer],
    ) -> None:
        """Tree viewers keep selected item and update properties text on locale switch."""
        _ = qapp_fixture
        i18n_de = I18nFactory(Path("config"), locale="de")
        i18n_en = I18nFactory(Path("config"), locale="en")
        viewer = viewer_class(Path("config"), i18n_de, config=ViewerConfig(show_properties=True))

        first_item = viewer.tree.topLevelItem(0)
        assert first_item is not None
        viewer.tree.setCurrentItem(first_item)

        assert "Typ" in viewer.properties_text.toHtml()

        viewer.set_i18n_factory(i18n_en)

        assert viewer.tree.currentItem() is not None
        assert "Type" in viewer.properties_text.toHtml()
