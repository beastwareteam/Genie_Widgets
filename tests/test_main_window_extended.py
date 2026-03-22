"""Extended tests for MainWindow helper methods and entry point."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from widgetsystem.core.main import MainWindow
from widgetsystem.factories.layout_factory import LayoutDefinition
from widgetsystem.factories.theme_factory import ThemeDefinition


@pytest.fixture
def i18n_mock() -> MagicMock:
    """Provide i18n mock with predictable translation behavior."""
    mock = MagicMock()
    mock.translate.side_effect = lambda _key, default="": default or ""
    return mock


@pytest.fixture
def dummy_window(tmp_path: Path, i18n_mock: MagicMock) -> SimpleNamespace:
    """Create a lightweight self object for unbound MainWindow method tests."""
    dock_manager = MagicMock()
    state = MagicMock()
    state.data.return_value = b"dock-state"
    dock_manager.saveState.return_value = state
    dock_manager.restoreState.return_value = True

    tab_color_controller = MagicMock()

    return SimpleNamespace(
        dock_manager=dock_manager,
        i18n_factory=i18n_mock,
        layout_file=tmp_path / "layout.xml",
        docks=[],
        panel_counter=0,
        menu_factory=MagicMock(),
        list_factory=MagicMock(),
        tabs_factory=MagicMock(),
        panel_factory=MagicMock(),
        _create_empty_dock=MagicMock(),
        theme_factory=MagicMock(),
        theme_manager=MagicMock(),
        _tab_color_controller=tab_color_controller,
    )


class TestLayoutPersistenceHelpers:
    """Test layout persistence helpers from MainWindow."""

    def test_save_layout_success(self, dummy_window: SimpleNamespace) -> None:
        """Save layout writes bytes and shows info message."""
        with patch("widgetsystem.core.main.QMessageBox.information") as info_box:
            MainWindow._save_layout(dummy_window)  # type: ignore[arg-type]
            assert dummy_window.layout_file.exists()
            info_box.assert_called_once()

    def test_save_layout_exception(self, dummy_window: SimpleNamespace) -> None:
        """Save layout exceptions are shown as critical message."""
        dummy_window.layout_file = MagicMock()
        dummy_window.layout_file.parent = MagicMock()
        dummy_window.layout_file.parent.mkdir.side_effect = OSError("no write")

        with patch("widgetsystem.core.main.QMessageBox.critical") as critical_box:
            MainWindow._save_layout(dummy_window)  # type: ignore[arg-type]
            critical_box.assert_called_once()

    def test_load_layout_missing_file(self, dummy_window: SimpleNamespace) -> None:
        """Missing layout file triggers warning and returns early."""
        with patch("widgetsystem.core.main.QMessageBox.warning") as warning_box:
            MainWindow._load_layout(dummy_window)  # type: ignore[arg-type]
            warning_box.assert_called_once()
            dummy_window.dock_manager.restoreState.assert_not_called()

    def test_load_layout_restore_failed(self, dummy_window: SimpleNamespace) -> None:
        """restoreState failure triggers warning."""
        dummy_window.layout_file.write_bytes(b"x")
        dummy_window.dock_manager.restoreState.return_value = False

        with patch("widgetsystem.core.main.QMessageBox.warning") as warning_box:
            MainWindow._load_layout(dummy_window)  # type: ignore[arg-type]
            assert warning_box.call_count >= 1

    def test_load_layout_success(self, dummy_window: SimpleNamespace) -> None:
        """Successful load shows information dialog."""
        dummy_window.layout_file.write_bytes(b"valid-layout")

        with patch("widgetsystem.core.main.QMessageBox.information") as info_box:
            MainWindow._load_layout(dummy_window)  # type: ignore[arg-type]
            info_box.assert_called_once()

    def test_load_layout_exception(self, dummy_window: SimpleNamespace) -> None:
        """Load exceptions trigger critical message."""
        dummy_window.layout_file = MagicMock()
        dummy_window.layout_file.exists.return_value = True
        dummy_window.layout_file.read_bytes.side_effect = RuntimeError("read error")

        with patch("widgetsystem.core.main.QMessageBox.critical") as critical_box:
            MainWindow._load_layout(dummy_window)  # type: ignore[arg-type]
            critical_box.assert_called_once()

    def test_load_layout_on_startup_missing_file(self, dummy_window: SimpleNamespace) -> None:
        """Startup load returns silently when file is absent."""
        MainWindow._load_layout_on_startup(dummy_window)  # type: ignore[arg-type]
        dummy_window.dock_manager.restoreState.assert_not_called()

    def test_load_layout_on_startup_restore_attempt(self, dummy_window: SimpleNamespace) -> None:
        """Startup load attempts restore when file exists."""
        dummy_window.layout_file.write_bytes(b"state")
        MainWindow._load_layout_on_startup(dummy_window)  # type: ignore[arg-type]
        dummy_window.dock_manager.restoreState.assert_called_once()


class TestNamedLayoutAndThemeApply:
    """Test named layout and theme application helpers."""

    def test_load_named_layout_missing_file(self, dummy_window: SimpleNamespace) -> None:
        """Missing named layout file triggers warning."""
        layout = LayoutDefinition("l1", "Layout 1", Path("does_not_exist.xml"))

        with patch("widgetsystem.core.main.QMessageBox.warning") as warning_box:
            MainWindow._load_named_layout(dummy_window, layout)  # type: ignore[arg-type]
            warning_box.assert_called_once()

    def test_load_named_layout_restore_failed(
        self,
        dummy_window: SimpleNamespace,
        tmp_path: Path,
    ) -> None:
        """Named layout restore failure triggers warning."""
        file_path = tmp_path / "named.xml"
        file_path.write_bytes(b"layout")
        layout = LayoutDefinition("l1", "Layout 1", file_path)
        dummy_window.dock_manager.restoreState.return_value = False

        with patch("widgetsystem.core.main.QMessageBox.warning") as warning_box:
            MainWindow._load_named_layout(dummy_window, layout)  # type: ignore[arg-type]
            warning_box.assert_called_once()

    def test_load_named_layout_success(self, dummy_window: SimpleNamespace, tmp_path: Path) -> None:
        """Named layout success triggers information message."""
        file_path = tmp_path / "named.xml"
        file_path.write_bytes(b"layout")
        layout = LayoutDefinition("l1", "Layout 1", file_path)

        with patch("widgetsystem.core.main.QMessageBox.information") as info_box:
            MainWindow._load_named_layout(dummy_window, layout)  # type: ignore[arg-type]
            info_box.assert_called_once()

    def test_apply_theme_missing_file(self, dummy_window: SimpleNamespace) -> None:
        """Missing theme file triggers warning."""
        theme = ThemeDefinition("dark", "Dark", Path("missing.qss"))

        with patch("widgetsystem.core.main.QMessageBox.warning") as warning_box:
            MainWindow._apply_theme(dummy_window, theme)  # type: ignore[arg-type]
            warning_box.assert_called_once()

    def test_apply_theme_success(self, dummy_window: SimpleNamespace, tmp_path: Path) -> None:
        """Theme apply updates stylesheet and tab colors."""
        qss_file = tmp_path / "theme.qss"
        qss_file.write_text("QWidget { color: red; }", encoding="utf-8")
        theme = ThemeDefinition(
            "dark",
            "Dark",
            qss_file,
            tab_active_color="#111111",
            tab_inactive_color="#222222",
        )

        class FakeQApplication:
            _instance: "FakeQApplication | None" = None

            def __init__(self) -> None:
                self.setStyleSheet = MagicMock()

            @staticmethod
            def instance() -> "FakeQApplication | None":
                return FakeQApplication._instance

        fake_app = FakeQApplication()
        FakeQApplication._instance = fake_app

        with patch("widgetsystem.core.main.QApplication", new=FakeQApplication):
            with patch("widgetsystem.core.main.QMessageBox.information") as info_box:
                MainWindow._apply_theme(dummy_window, theme)  # type: ignore[arg-type]
                fake_app.setStyleSheet.assert_called_once()
                assert dummy_window._tab_color_controller.active_color == "#111111"
                assert dummy_window._tab_color_controller.inactive_color == "#222222"
                dummy_window._tab_color_controller.apply.assert_called_once()
                info_box.assert_called_once()

    def test_apply_theme_exception(self, dummy_window: SimpleNamespace) -> None:
        """Theme apply exceptions trigger critical message."""
        theme = ThemeDefinition("dark", "Dark", Path("missing.qss"))
        with patch("widgetsystem.core.main.Path.exists", side_effect=RuntimeError("boom")):
            with patch("widgetsystem.core.main.QMessageBox.critical") as critical_box:
                MainWindow._apply_theme(dummy_window, theme)  # type: ignore[arg-type]
                critical_box.assert_called_once()


class TestToolbarActionsAndConfig:
    """Test toolbar action helpers and config reload handling."""

    def test_on_new_dock_creates_dynamic_panel(self, dummy_window: SimpleNamespace) -> None:
        """New dock action increments counter and creates dock."""
        with patch("widgetsystem.core.main.QtAds.CenterDockWidgetArea", new=1):
            MainWindow._on_new_dock(dummy_window)  # type: ignore[arg-type]
            assert dummy_window.panel_counter == 1
            dummy_window.panel_factory.add_panel.assert_called_once()
            dummy_window._create_empty_dock.assert_called_once()

    def test_on_float_all_calls_set_floating(self, dummy_window: SimpleNamespace) -> None:
        """Float action sets all docks to floating."""
        d1 = MagicMock()
        d2 = MagicMock()
        dummy_window.docks = [d1, d2]
        MainWindow._on_float_all(dummy_window)  # type: ignore[arg-type]
        d1.setFloating.assert_called_once()
        d2.setFloating.assert_called_once()

    def test_on_dock_all_only_for_floating(self, dummy_window: SimpleNamespace) -> None:
        """Dock action re-docks only floating docks."""
        floating = MagicMock()
        floating.isFloating.return_value = True
        docked = MagicMock()
        docked.isFloating.return_value = False
        dummy_window.docks = [floating, docked]

        with patch("widgetsystem.core.main.QtAds.CenterDockWidgetArea", new=1):
            MainWindow._on_dock_all(dummy_window)  # type: ignore[arg-type]
            dummy_window.dock_manager.addDockWidget.assert_called_once_with(1, floating)

    def test_on_close_all_closes_all_docks(self, dummy_window: SimpleNamespace) -> None:
        """Close action closes each dock widget."""
        d1 = MagicMock()
        d2 = MagicMock()
        dummy_window.docks = [d1, d2]
        MainWindow._on_close_all(dummy_window)  # type: ignore[arg-type]
        d1.closeDockWidget.assert_called_once()
        d2.closeDockWidget.assert_called_once()

    @pytest.mark.parametrize(
        "category, attribute",
        [
            ("menus", "menu_factory"),
            ("lists", "list_factory"),
            ("tabs", "tabs_factory"),
            ("panels", "panel_factory"),
        ],
    )
    def test_on_config_changed_reloads_factory(
        self,
        dummy_window: SimpleNamespace,
        category: str,
        attribute: str,
    ) -> None:
        """Category updates replace respective factory."""
        before = getattr(dummy_window, attribute)
        MainWindow._on_config_changed(dummy_window, category)  # type: ignore[arg-type]
        after = getattr(dummy_window, attribute)
        assert before is not after

    def test_on_config_changed_exception_handled(self, dummy_window: SimpleNamespace) -> None:
        """Errors while reloading config are swallowed."""
        with patch("widgetsystem.core.main.MenuFactory", side_effect=RuntimeError("x")):
            MainWindow._on_config_changed(dummy_window, "menus")  # type: ignore[arg-type]


class TestThemeProfileHelper:
    """Test apply theme profile helper."""

    def test_apply_theme_profile_success(self, dummy_window: SimpleNamespace) -> None:
        """Successful profile selection shows information."""
        theme = MagicMock()
        theme.name = "Profile A"
        dummy_window.theme_manager.set_current_theme.return_value = True
        dummy_window.theme_manager.current_theme.return_value = theme

        with patch("widgetsystem.core.main.QMessageBox.information") as info_box:
            MainWindow._apply_theme_profile(dummy_window, "a")  # type: ignore[arg-type]
            info_box.assert_called_once()

    def test_apply_theme_profile_not_found(self, dummy_window: SimpleNamespace) -> None:
        """Unknown profile shows warning."""
        dummy_window.theme_manager.set_current_theme.return_value = False

        with patch("widgetsystem.core.main.QMessageBox.warning") as warning_box:
            MainWindow._apply_theme_profile(dummy_window, "missing")  # type: ignore[arg-type]
            warning_box.assert_called_once()


class TestMainEntryPoint:
    """Test main() entry point behavior."""

    def test_main_entry_point_applies_default_theme(self) -> None:
        """main applies theme and executes app loop."""
        fake_app = MagicMock()
        fake_app.exec.return_value = 0
        fake_window = MagicMock()
        fake_theme_factory = MagicMock()
        fake_theme_factory.get_default_stylesheet.return_value = "QWidget {}"

        with patch("widgetsystem.core.main.QApplication", return_value=fake_app):
            with patch("widgetsystem.core.main.ThemeFactory", return_value=fake_theme_factory):
                with patch("widgetsystem.core.main.MainWindow", return_value=fake_window):
                    with patch("widgetsystem.core.main.sys.exit") as exit_mock:
                        from widgetsystem.core import main as main_module

                        main_module.main()

                        fake_app.setStyleSheet.assert_called_once_with("QWidget {}")
                        fake_window.show.assert_called_once()
                        exit_mock.assert_called_once_with(0)

    def test_main_entry_point_theme_load_exception(self) -> None:
        """main continues if default theme load fails."""
        fake_app = MagicMock()
        fake_app.exec.return_value = 0
        fake_window = MagicMock()

        with (
            patch("widgetsystem.core.main.QApplication", return_value=fake_app),
            patch(
                "widgetsystem.core.main.ThemeFactory",
                side_effect=RuntimeError("theme fail"),
            ),
            patch("widgetsystem.core.main.MainWindow", return_value=fake_window),
        ):
            with patch("widgetsystem.core.main.sys.exit") as exit_mock:
                from widgetsystem.core import main as main_module

                main_module.main()

                fake_window.show.assert_called_once()
                exit_mock.assert_called_once_with(0)
