"""Tests for PluginManagerDialog."""

from pathlib import Path
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

from widgetsystem.ui.plugin_manager_dialog import PluginManagerDialog


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_plugin_manager_dialog_populates_info_text(tmp_path: Path) -> None:
    """Dialog shows factory, plugin, and plugin-directory information."""
    _get_app()

    existing_dir = tmp_path / "plugins"
    existing_dir.mkdir(parents=True, exist_ok=True)
    missing_dir = tmp_path / "missing_plugins"

    plugin_registry = SimpleNamespace(
        factories={"theme": object(), "layout": object()},
        plugins={"sample_plugin": SimpleNamespace(version="1.2.3")},
    )
    plugin_manager = SimpleNamespace(plugin_dirs=[existing_dir, missing_dir])

    dialog = PluginManagerDialog(plugin_registry, plugin_manager)
    content = dialog._info_text.toPlainText()

    assert dialog.windowTitle() == "Plugin-System"
    assert "Registrierte Factories" in content
    assert "sample_plugin (v1.2.3)" in content
    assert str(existing_dir) in content
    assert "[OK]" in content
    assert "[NICHT GEFUNDEN]" in content
