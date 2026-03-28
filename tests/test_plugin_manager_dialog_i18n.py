"""Tests for PluginManagerDialog i18n support."""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.plugin_manager_dialog import PluginManagerDialog


class _FakePlugin:
    def __init__(self, version: str = "1.0.0") -> None:
        self.version = version


class _FakeRegistry:
    def __init__(self) -> None:
        self.factories = {"menu": object(), "theme": object()}
        self.plugins = {"sample": _FakePlugin("2.1.0")}


class _FakeManager:
    def __init__(self) -> None:
        self.plugin_dirs = [Path("config/plugins"), Path("missing/plugins")]


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide QApplication for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestPluginManagerDialogI18n:
    """Plugin manager dialog should fully support i18n."""

    def test_dialog_german_texts(self, qapp: QApplication) -> None:
        """Dialog title and section headers should be German with de locale."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        dialog = PluginManagerDialog(
            plugin_registry=_FakeRegistry(),
            plugin_manager=_FakeManager(),
            i18n_factory=i18n_de,
        )

        assert dialog.windowTitle() == "Plugin-System"
        assert dialog.close_button is not None
        assert dialog.close_button.text() == "Schließen"
        info_text = dialog._info_text.toPlainText()
        assert "=== Registrierte Factories ===" in info_text
        assert "=== Geladene Plugins ===" in info_text
        assert "=== Plugin-Verzeichnisse ===" in info_text

    def test_dialog_english_texts(self, qapp: QApplication) -> None:
        """Dialog title and section headers should be English with en locale."""
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")
        dialog = PluginManagerDialog(
            plugin_registry=_FakeRegistry(),
            plugin_manager=_FakeManager(),
            i18n_factory=i18n_en,
        )

        assert dialog.windowTitle() == "Plugin System"
        assert dialog.close_button is not None
        assert dialog.close_button.text() == "Close"
        info_text = dialog._info_text.toPlainText()
        assert "=== Registered Factories ===" in info_text
        assert "=== Loaded Plugins ===" in info_text
        assert "=== Plugin Directories ===" in info_text

    def test_runtime_i18n_switch_updates_texts(self, qapp: QApplication) -> None:
        """Switching i18n factory at runtime should update title and content."""
        i18n_de = I18nFactory(config_path=Path("config"), locale="de")
        i18n_en = I18nFactory(config_path=Path("config"), locale="en")

        dialog = PluginManagerDialog(
            plugin_registry=_FakeRegistry(),
            plugin_manager=_FakeManager(),
            i18n_factory=i18n_de,
        )
        assert dialog.windowTitle() == "Plugin-System"
        assert dialog.close_button is not None
        assert dialog.close_button.text() == "Schließen"

        dialog.set_i18n_factory(i18n_en)

        assert dialog.windowTitle() == "Plugin System"
        assert dialog.close_button.text() == "Close"
        info_text = dialog._info_text.toPlainText()
        assert "=== Registered Factories ===" in info_text

    def test_fallback_without_i18n_factory(self, qapp: QApplication) -> None:
        """Dialog should use fallback strings when no i18n factory is provided."""
        dialog = PluginManagerDialog(
            plugin_registry=_FakeRegistry(),
            plugin_manager=_FakeManager(),
            i18n_factory=None,
        )

        assert dialog.windowTitle() == "Plugin-System"
        info_text = dialog._info_text.toPlainText()
        assert "=== Registrierte Factories ===" in info_text
