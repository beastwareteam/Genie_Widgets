"""Extended tests for visual_app helpers and entry points."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from widgetsystem.ui.visual_app import VisualMainWindow


def _make_signal() -> SimpleNamespace:
    return SimpleNamespace(connect=MagicMock())


def _make_button() -> MagicMock:
    button = MagicMock()
    button.clicked = _make_signal()
    return button


def _make_action() -> MagicMock:
    action = MagicMock()
    action.triggered = _make_signal()
    return action


def _dummy_window() -> SimpleNamespace:
    i18n = MagicMock()
    i18n.translate.side_effect = lambda _key, default="": default or ""

    def _translate(key: str, default: str) -> str:
        return i18n.translate(key, default=default)

    return SimpleNamespace(
        i18n_factory=i18n,
        _translate=_translate,
        theme_factory=MagicMock(),
        dock_manager=MagicMock(),
        docks=[],
        addToolBar=MagicMock(),
        menuBar=MagicMock(),
        setStyleSheet=MagicMock(),
        setCentralWidget=MagicMock(),
        close=MagicMock(),
        _show_dashboard=MagicMock(),
        _show_configuration=MagicMock(),
        _refresh_viewers=MagicMock(),
        _show_theme_editor=MagicMock(),
        _show_color_picker=MagicMock(),
        _show_widget_editor=MagicMock(),
        _show_lists_viewer=MagicMock(),
        _show_menus_viewer=MagicMock(),
        _show_tabs_viewer=MagicMock(),
        _show_panels_viewer=MagicMock(),
        _show_about=MagicMock(),
    )


class TestVisualAppToolbarAndMenu:
    """Test toolbar and menu creation paths."""

    def test_create_toolbar_with_themes(self) -> None:
        """Toolbar creates action widgets and theme entries."""
        window = _dummy_window()
        window.theme_factory.list_themes.return_value = [
            SimpleNamespace(name="Dark", theme_id="dark"),
            SimpleNamespace(name="Light", theme_id="light"),
        ]

        toolbar = MagicMock()
        theme_menu = MagicMock()
        theme_button = MagicMock()

        with (
            patch("widgetsystem.ui.visual_app.QToolBar", return_value=toolbar),
            patch(
                "widgetsystem.ui.visual_app.QPushButton",
                side_effect=lambda *_: _make_button(),
            ),
            patch("widgetsystem.ui.visual_app.QMenu", return_value=theme_menu),
            patch(
                "widgetsystem.ui.visual_app.QAction",
                side_effect=lambda *_: _make_action(),
            ),
            patch(
                "widgetsystem.ui.visual_app.QToolButton",
                return_value=theme_button,
            ),
        ):
            VisualMainWindow._create_toolbar(window)  # type: ignore[arg-type]

        window.addToolBar.assert_called_once_with(toolbar)
        assert toolbar.addWidget.call_count >= 4
        assert theme_menu.addAction.call_count == 2

    def test_create_toolbar_theme_list_exception_is_ignored(self) -> None:
        """Theme loading errors do not break toolbar creation."""
        window = _dummy_window()
        window.theme_factory.list_themes.side_effect = RuntimeError("theme error")

        toolbar = MagicMock()
        with (
            patch("widgetsystem.ui.visual_app.QToolBar", return_value=toolbar),
            patch(
                "widgetsystem.ui.visual_app.QPushButton",
                side_effect=lambda *_: _make_button(),
            ),
            patch("widgetsystem.ui.visual_app.QMenu", return_value=MagicMock()),
        ):
            with patch("widgetsystem.ui.visual_app.QToolButton", return_value=MagicMock()):
                VisualMainWindow._create_toolbar(window)  # type: ignore[arg-type]

        window.addToolBar.assert_called_once_with(toolbar)

    def test_create_menu(self) -> None:
        """Menu creation wires file/view/help actions."""
        window = _dummy_window()

        file_menu = MagicMock()
        view_menu = MagicMock()
        help_menu = MagicMock()
        file_menu.addAction.side_effect = lambda *_: _make_action()
        view_menu.addAction.side_effect = lambda *_: _make_action()
        help_menu.addAction.side_effect = lambda *_: _make_action()

        menu_bar = MagicMock()
        menu_bar.addMenu.side_effect = [file_menu, view_menu, help_menu]
        window.menuBar.return_value = menu_bar

        VisualMainWindow._create_menu(window)  # type: ignore[arg-type]

        assert menu_bar.addMenu.call_count == 3
        assert file_menu.addAction.call_count == 1
        assert view_menu.addAction.call_count == 4
        assert help_menu.addAction.call_count == 1


class TestVisualAppViewersAndCentral:
    """Test viewer dock creation and central widget."""

    def test_create_viewers(self) -> None:
        """Create all four configured viewer docks."""
        window = _dummy_window()

        lists_viewer = MagicMock()
        menus_viewer = MagicMock()
        tabs_viewer = MagicMock()
        panels_viewer = MagicMock()

        dock_objects = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

        with patch("widgetsystem.ui.visual_app.ViewerConfig", return_value=MagicMock()):
            with patch("widgetsystem.ui.visual_app.ListsViewer", return_value=lists_viewer):
                with patch("widgetsystem.ui.visual_app.MenusViewer", return_value=menus_viewer):
                    with patch("widgetsystem.ui.visual_app.TabsViewer", return_value=tabs_viewer):
                        with patch(
                            "widgetsystem.ui.visual_app.PanelsViewer",
                            return_value=panels_viewer,
                        ):
                            with patch(
                                "widgetsystem.ui.visual_app.QtAds.CDockWidget",
                                side_effect=dock_objects,
                            ):
                                with patch(
                                    "widgetsystem.ui.visual_app.QtAds.LeftDockWidgetArea",
                                    new=1,
                                ):
                                    with patch(
                                        "widgetsystem.ui.visual_app.QtAds.RightDockWidgetArea",
                                        new=2,
                                    ):
                                        VisualMainWindow._create_viewers(window)  # type: ignore[arg-type]

        assert len(window.docks) == 4
        assert window.dock_manager.addDockWidget.call_count == 4

    def test_create_central_widget(self) -> None:
        """Central widget creation builds labels and assigns it."""
        window = _dummy_window()

        central_widget = MagicMock()
        layout = MagicMock()
        title_label = MagicMock()
        info_label = MagicMock()
        title_font = MagicMock()

        with patch("widgetsystem.ui.visual_app.QWidget", return_value=central_widget):
            with patch("widgetsystem.ui.visual_app.QVBoxLayout", return_value=layout):
                with patch(
                    "widgetsystem.ui.visual_app.QLabel",
                    side_effect=[title_label, info_label],
                ):
                    with patch("widgetsystem.ui.visual_app.QFont", return_value=title_font):
                        VisualMainWindow._create_central_widget(window)  # type: ignore[arg-type]

        window.setCentralWidget.assert_called_once_with(central_widget)
        assert layout.addWidget.call_count >= 2
        layout.addStretch.assert_called_once()


class TestVisualAppActionsAndDialogs:
    """Test show/refresh/theme helper methods."""

    def test_show_configuration_success(self) -> None:
        """Configuration panel is shown when creation succeeds."""
        window = _dummy_window()
        panel = MagicMock()

        with patch("widgetsystem.ui.visual_app.ConfigurationPanel", return_value=panel):
            VisualMainWindow._show_configuration(window)  # type: ignore[arg-type]

        panel.setWindowTitle.assert_called_once()
        panel.resize.assert_called_once()
        panel.show.assert_called_once()

    def test_show_configuration_exception(self) -> None:
        """Configuration panel errors show critical message."""
        window = _dummy_window()

        with (
            patch(
                "widgetsystem.ui.visual_app.ConfigurationPanel",
                side_effect=RuntimeError("cfg"),
            ),
            patch("widgetsystem.ui.visual_app.QMessageBox.critical") as critical_box,
        ):
            VisualMainWindow._show_configuration(window)  # type: ignore[arg-type]
            critical_box.assert_called_once()

    def test_show_dashboard_success(self) -> None:
        """Dashboard is shown when creation succeeds."""
        window = _dummy_window()
        dashboard = MagicMock()

        with patch("widgetsystem.ui.visual_app.VisualDashboard", return_value=dashboard):
            VisualMainWindow._show_dashboard(window)  # type: ignore[arg-type]

        dashboard.show.assert_called_once()

    def test_show_dashboard_exception(self) -> None:
        """Dashboard errors show critical message."""
        window = _dummy_window()

        with patch("widgetsystem.ui.visual_app.VisualDashboard", side_effect=RuntimeError("dash")):
            with patch("widgetsystem.ui.visual_app.QMessageBox.critical") as critical_box:
                VisualMainWindow._show_dashboard(window)  # type: ignore[arg-type]
                critical_box.assert_called_once()

    def test_refresh_viewers(self) -> None:
        """Refresh updates all viewers and shows info dialog."""
        window = _dummy_window()
        window.lists_viewer = MagicMock()
        window.menus_viewer = MagicMock()
        window.tabs_viewer = MagicMock()
        window.panels_viewer = MagicMock()

        with patch("widgetsystem.ui.visual_app.QMessageBox.information") as info_box:
            VisualMainWindow._refresh_viewers(window)  # type: ignore[arg-type]

        window.lists_viewer.refresh.assert_called_once()
        window.menus_viewer.refresh.assert_called_once()
        window.tabs_viewer.refresh.assert_called_once()
        window.panels_viewer.refresh.assert_called_once()
        info_box.assert_called_once()

    def test_apply_theme_success(self) -> None:
        """Default theme is applied when stylesheet exists."""
        window = _dummy_window()
        window.theme_factory.get_default_stylesheet.return_value = "QWidget {}"

        VisualMainWindow._apply_theme(window)  # type: ignore[arg-type]
        window.setStyleSheet.assert_called_once_with("QWidget {}")

    def test_apply_theme_exception(self) -> None:
        """Theme apply errors are swallowed."""
        window = _dummy_window()
        window.theme_factory.get_default_stylesheet.side_effect = RuntimeError("theme")

        VisualMainWindow._apply_theme(window)  # type: ignore[arg-type]

    def test_apply_theme_by_id_success(self, tmp_path: Path) -> None:
        """Theme by ID reads stylesheet and applies it."""
        window = _dummy_window()
        qss = tmp_path / "t.qss"
        qss.write_text("QWidget { color: blue; }", encoding="utf-8")
        window.theme_factory.list_themes.return_value = [
            SimpleNamespace(theme_id="dark", name="Dark", file_path=qss),
        ]

        VisualMainWindow._apply_theme_by_id(window, "dark")  # type: ignore[arg-type]
        window.setStyleSheet.assert_called_once()

    def test_apply_theme_by_id_no_match(self) -> None:
        """No matching theme ID results in no stylesheet apply."""
        window = _dummy_window()
        window.theme_factory.list_themes.return_value = []

        VisualMainWindow._apply_theme_by_id(window, "missing")  # type: ignore[arg-type]
        window.setStyleSheet.assert_not_called()

    def test_on_theme_triggered_delegates(self) -> None:
        """Theme trigger delegates to _apply_theme_by_id."""
        window = _dummy_window()
        window._apply_theme_by_id = MagicMock()

        VisualMainWindow._on_theme_triggered(window, False, "dark")  # type: ignore[arg-type]
        window._apply_theme_by_id.assert_called_once_with("dark")

    def test_show_welcome(self) -> None:
        """Welcome dialog is displayed."""
        window = _dummy_window()
        with patch("widgetsystem.ui.visual_app.QMessageBox.information") as info_box:
            VisualMainWindow._show_welcome(window)  # type: ignore[arg-type]
            info_box.assert_called_once()

    def test_show_about(self) -> None:
        """About dialog is displayed."""
        window = _dummy_window()
        with patch("widgetsystem.ui.visual_app.QMessageBox.about") as about_box:
            VisualMainWindow._show_about(window)  # type: ignore[arg-type]
            about_box.assert_called_once()

    def test_show_theme_editor_passes_i18n_factory(self) -> None:
        """Theme editor dialog receives the active i18n factory."""
        window = _dummy_window()
        dialog = MagicMock()

        with patch("widgetsystem.ui.ThemeEditorDialog", return_value=dialog) as dialog_cls:
            VisualMainWindow._show_theme_editor(window)  # type: ignore[arg-type]

        dialog_cls.assert_called_once()
        assert dialog_cls.call_args.kwargs["i18n_factory"] is window.i18n_factory
        dialog.exec.assert_called_once()

    def test_show_color_picker_passes_i18n_factory(self) -> None:
        """ARGB color picker dialog receives the active i18n factory."""
        window = _dummy_window()
        dialog = MagicMock()
        dialog.exec.return_value = False

        with patch("widgetsystem.ui.ARGBColorPickerDialog", return_value=dialog) as dialog_cls:
            VisualMainWindow._show_color_picker(window)  # type: ignore[arg-type]

        dialog_cls.assert_called_once()
        assert dialog_cls.call_args.kwargs["i18n_factory"] is window.i18n_factory
        dialog.exec.assert_called_once()

    def test_show_widget_editor_passes_i18n_factory(self) -> None:
        """Widget features dialog receives the active i18n factory."""
        window = _dummy_window()
        dialog = MagicMock()

        with patch("widgetsystem.ui.WidgetFeaturesEditorDialog", return_value=dialog) as dialog_cls:
            VisualMainWindow._show_widget_editor(window)  # type: ignore[arg-type]

        dialog_cls.assert_called_once()
        assert dialog_cls.call_args.kwargs["i18n_factory"] is window.i18n_factory
        dialog.exec.assert_called_once()


class TestVisualAppI18nRuntime:
    """Test runtime locale updates for VisualMainWindow."""

    def test_set_i18n_factory_refreshes_toolbar_menu_and_docks(self) -> None:
        """Locale switch updates translated texts and propagates to viewers."""
        window = _dummy_window()
        new_i18n = MagicMock()
        new_i18n.translate.side_effect = lambda key, default="": f"tr:{key}" if key else default
        window._translate = lambda key, default: window.i18n_factory.translate(  # type: ignore[attr-defined]
            key,
            default=default,
        )

        window.setWindowTitle = MagicMock()
        window.toolbar = MagicMock()
        window.dashboard_btn = MagicMock()
        window.config_btn = MagicMock()
        window.refresh_btn = MagicMock()
        window.theme_button = MagicMock()
        window.theme_editor_btn = MagicMock()
        window.color_picker_btn = MagicMock()
        window.widget_editor_btn = MagicMock()

        window.file_menu = MagicMock()
        window.exit_action = MagicMock()
        window.view_menu = MagicMock()
        window.show_lists_action = MagicMock()
        window.show_menus_action = MagicMock()
        window.show_tabs_action = MagicMock()
        window.show_panels_action = MagicMock()
        window.help_menu = MagicMock()
        window.about_action = MagicMock()

        window.lists_dock = MagicMock()
        window.menus_dock = MagicMock()
        window.tabs_dock = MagicMock()
        window.panels_dock = MagicMock()

        window.lists_viewer = MagicMock()
        window.menus_viewer = MagicMock()
        window.tabs_viewer = MagicMock()
        window.panels_viewer = MagicMock()
        window._refresh_translated_texts = lambda: VisualMainWindow._refresh_translated_texts(  # type: ignore[attr-defined]
            window,
        )

        VisualMainWindow.set_i18n_factory(window, new_i18n)  # type: ignore[arg-type]

        window.setWindowTitle.assert_called_once_with("tr:visual_app.window_title")
        window.dashboard_btn.setText.assert_called_once_with("tr:visual_app.toolbar.dashboard")
        window.file_menu.setTitle.assert_called_once_with("tr:menu.file")
        window.about_action.setText.assert_called_once_with("tr:visual_app.menu.about")
        window.lists_dock.setWindowTitle.assert_called_once_with("tr:visual.tab.lists")

        window.lists_viewer.set_i18n_factory.assert_called_once_with(new_i18n)
        window.menus_viewer.set_i18n_factory.assert_called_once_with(new_i18n)
        window.tabs_viewer.set_i18n_factory.assert_called_once_with(new_i18n)
        window.panels_viewer.set_i18n_factory.assert_called_once_with(new_i18n)


class TestVisualAppPrintHelpers:
    """Test simple viewer print helper methods."""

    def test_show_lists_viewer_print(self) -> None:
        window = _dummy_window()
        VisualMainWindow._show_lists_viewer(window)  # type: ignore[arg-type]

    def test_show_menus_viewer_print(self) -> None:
        window = _dummy_window()
        VisualMainWindow._show_menus_viewer(window)  # type: ignore[arg-type]

    def test_show_tabs_viewer_print(self) -> None:
        window = _dummy_window()
        VisualMainWindow._show_tabs_viewer(window)  # type: ignore[arg-type]

    def test_show_panels_viewer_print(self) -> None:
        window = _dummy_window()
        VisualMainWindow._show_panels_viewer(window)  # type: ignore[arg-type]


class TestVisualAppMainEntry:
    """Test visual_app.main() behavior."""

    def test_main_entry_runs_event_loop(self) -> None:
        """Entry point creates app and exits with exec return code."""
        fake_app = MagicMock()
        fake_app.exec.return_value = 0
        fake_window = MagicMock()

        with patch("widgetsystem.ui.visual_app.QApplication", return_value=fake_app):
            with patch("widgetsystem.ui.visual_app.VisualMainWindow", return_value=fake_window):
                with patch("widgetsystem.ui.visual_app.sys.exit") as exit_mock:
                    from widgetsystem.ui import visual_app as module

                    module.main()

                    fake_window.show.assert_called_once()
                    exit_mock.assert_called_once_with(0)
