"""PluginManagerDialog - Dialog for plugin system information.

Extracted from MainWindow._show_plugin_manager() to follow
the pattern of separate dialog classes.
"""

from typing import Any

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PluginManagerDialog(QDialog):
    """Dialog displaying plugin system status and information."""

    def __init__(
        self,
        plugin_registry: Any,
        plugin_manager: Any,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize PluginManagerDialog.

        Args:
            plugin_registry: PluginRegistry instance
            plugin_manager: PluginManager instance
            parent: Parent widget
        """
        super().__init__(parent)

        self._plugin_registry = plugin_registry
        self._plugin_manager = plugin_manager

        self._setup_ui()
        self._populate_info()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle("Plugin-System")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Plugin-System Status")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Info text
        self._info_text = QTextEdit()
        self._info_text.setReadOnly(True)
        layout.addWidget(self._info_text)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def _populate_info(self) -> None:
        """Populate the info text with plugin system status."""
        lines = []

        # Factory information
        lines.append("=== Registrierte Factories ===")
        factories = getattr(self._plugin_registry, "factories", {})
        if factories:
            for name in sorted(factories.keys()):
                lines.append(f"  - {name}")
        else:
            lines.append("  (keine)")

        lines.append("")

        # Plugin information
        lines.append("=== Geladene Plugins ===")
        plugins = getattr(self._plugin_registry, "plugins", {})
        if plugins:
            for name, plugin in plugins.items():
                version = getattr(plugin, "version", "?")
                lines.append(f"  - {name} (v{version})")
        else:
            lines.append("  (keine)")

        lines.append("")

        # Plugin directories
        lines.append("=== Plugin-Verzeichnisse ===")
        plugin_dirs = getattr(self._plugin_manager, "plugin_dirs", [])
        if plugin_dirs:
            for d in plugin_dirs:
                exists = d.exists() if hasattr(d, "exists") else False
                status = "[OK]" if exists else "[NICHT GEFUNDEN]"
                lines.append(f"  - {d} {status}")
        else:
            lines.append("  (keine konfiguriert)")

        self._info_text.setPlainText("\n".join(lines))
