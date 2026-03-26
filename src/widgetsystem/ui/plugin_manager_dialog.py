"""PluginManagerDialog - Dialog for plugin system information.

Extracted from MainWindow._show_plugin_manager() to follow
the pattern of separate dialog classes.
"""

from typing import TYPE_CHECKING, Any

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


class PluginManagerDialog(QDialog):
    """Dialog displaying plugin system status and information."""

    def __init__(
        self,
        plugin_registry: Any,
        plugin_manager: Any,
        parent: QWidget | None = None,
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize PluginManagerDialog.

        Args:
            plugin_registry: PluginRegistry instance
            plugin_manager: PluginManager instance
            parent: Parent widget
            i18n_factory: Optional i18n factory for translating UI text
        """
        super().__init__(parent)

        self._plugin_registry = plugin_registry
        self._plugin_manager = plugin_manager
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}

        self._setup_ui()
        self._populate_info()

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory and refresh visible texts."""
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()
        self._setup_translated_texts()
        self._populate_info()

    def _translate(self, key: str, default: str | None = None, **kwargs: Any) -> str:
        """Translate a key with optional interpolation and cache."""
        if not self._i18n_factory or not key:
            text = default or key
            return text.format(**kwargs) if kwargs else text

        cache_key = f"{key}|{sorted(kwargs.items())}" if kwargs else key
        if cache_key in self._translated_cache:
            return self._translated_cache[cache_key]

        translated = self._i18n_factory.translate(key, default=default or key, **kwargs)
        self._translated_cache[cache_key] = translated
        return translated

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle(self._translate("plugin_manager.title", "Plugin-System"))
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Title
        self._title_label = QLabel(
            self._translate("plugin_manager.status_title", "Plugin-System Status"),
        )
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self._title_label.setFont(font)
        layout.addWidget(self._title_label)

        # Info text
        self._info_text = QTextEdit()
        self._info_text.setReadOnly(True)
        layout.addWidget(self._info_text)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(  # pyright: ignore[reportAttributeAccessIssue]  # pylint: disable=no-member
            self.accept,
        )
        self.close_button = self.button_box.button(QDialogButtonBox.StandardButton.Close)
        if self.close_button is not None:
            self.close_button.setText(self._translate("dialog.close", "Close"))
        layout.addWidget(self.button_box)

    def _setup_translated_texts(self) -> None:
        """Refresh static translated UI texts."""
        self.setWindowTitle(self._translate("plugin_manager.title", "Plugin-System"))
        self._title_label.setText(
            self._translate("plugin_manager.status_title", "Plugin-System Status"),
        )
        if self.close_button is not None:
            self.close_button.setText(self._translate("dialog.close", "Close"))

    def _populate_info(self) -> None:
        """Populate the info text with plugin system status."""
        lines = []

        # Factory information
        lines.append(self._translate("plugin_manager.section.factories", "=== Registrierte Factories ==="))
        factories = getattr(self._plugin_registry, "factories", {})
        if factories:
            for name in sorted(factories.keys()):
                lines.append(f"  - {name}")
        else:
            lines.append(self._translate("plugin_manager.none", "  (keine)"))

        lines.append("")

        # Plugin information
        lines.append(self._translate("plugin_manager.section.plugins", "=== Geladene Plugins ==="))
        plugins = getattr(self._plugin_registry, "plugins", {})
        if plugins:
            for name, plugin in plugins.items():
                version = getattr(plugin, "version", "?")
                lines.append(f"  - {name} (v{version})")
        else:
            lines.append(self._translate("plugin_manager.none", "  (keine)"))

        lines.append("")

        # Plugin directories
        lines.append(
            self._translate("plugin_manager.section.directories", "=== Plugin-Verzeichnisse ==="),
        )
        plugin_dirs = getattr(self._plugin_manager, "plugin_dirs", [])
        if plugin_dirs:
            for d in plugin_dirs:
                exists = d.exists() if hasattr(d, "exists") else False
                status = (
                    self._translate("plugin_manager.dir_status.ok", "[OK]")
                    if exists
                    else self._translate("plugin_manager.dir_status.missing", "[NICHT GEFUNDEN]")
                )
                lines.append(f"  - {d} {status}")
        else:
            lines.append(
                self._translate(
                    "plugin_manager.none_configured",
                    "  (keine konfiguriert)",
                ),
            )

        self._info_text.setPlainText("\n".join(lines))
