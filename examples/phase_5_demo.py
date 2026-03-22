"""Phase 5 Demo - Showcasing all new optional features.

Demonstrates:
- Phase 5a: Live Theme-Editor
- Phase 5b: ARGB Color-Picker
- Phase 5c: Widget-Features Editor
- Phase 5d: Plugin System
"""

from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from widgetsystem.ui import (
    ARGBColorButton,
    ARGBColorPicker,
    ARGBColorPickerDialog,
    LiveThemeEditor,
    WidgetFeaturesEditor,
)
from widgetsystem.core import PluginManager, PluginRegistry
from widgetsystem.factories.theme_factory import ThemeFactory


class Phase5DemoWindow(QMainWindow):
    """Main window showcasing all Phase 5 features."""

    def __init__(self) -> None:
        """Initialize Phase 5 demo window."""
        super().__init__()
        self.setWindowTitle("🚀 WidgetSystem - Phase 5 Demo | Alle neuen Features")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize demo components
        config_path = Path("config")
        self.theme_factory = ThemeFactory(config_path)
        self.plugin_registry = PluginRegistry()
        self.plugin_manager = PluginManager(registry=self.plugin_registry)

        # Create central widget with tabs
        self._setup_ui(config_path)

    def _setup_ui(self, config_path: Path) -> None:
        """Set up user interface with tabs for each phase.

        Args:
            config_path: Path to configuration directory
        """
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()

        # Tab 1: Theme-Editor (Phase 5a)
        theme_editor_tab = self._create_theme_editor_tab(config_path)
        tabs.addTab(theme_editor_tab, "📝 Phase 5a: Theme-Editor")

        # Tab 2: Color-Picker (Phase 5b)
        color_picker_tab = self._create_color_picker_tab()
        tabs.addTab(color_picker_tab, "🎨 Phase 5b: Color-Picker")

        # Tab 3: Widget-Features (Phase 5c)
        widget_features_tab = self._create_widget_features_tab(config_path)
        tabs.addTab(widget_features_tab, "⚙️ Phase 5c: Widget-Features")

        # Tab 4: Plugin-System (Phase 5d)
        plugin_system_tab = self._create_plugin_system_tab()
        tabs.addTab(plugin_system_tab, "🔌 Phase 5d: Plugin-System")

        # Tab 5: Info (Übersicht)
        info_tab = self._create_info_tab()
        tabs.addTab(info_tab, "ℹ️ Info")

        main_layout.addWidget(tabs)
        self.setCentralWidget(central_widget)

    def _create_theme_editor_tab(self, config_path: Path) -> QWidget:
        """Create theme editor tab (Phase 5a).

        Args:
            config_path: Path to configuration directory

        Returns:
            Configured widget tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QWidget()
        title_layout = QVBoxLayout(title)
        title_label = QWidget()
        title_label_layout = QVBoxLayout(title_label)
        from PySide6.QtWidgets import QLabel
        label = QLabel("Live Theme-Editor")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        title_label_layout.addWidget(label)

        desc = QLabel("""
        Bearbeite Themes in Echtzeit:
        - Live-Preview von Theme-Änderungen
        - ARGB-Farbwähler mit Transparenz
        - Automatische Property-Editoren
        - Speichern zu config/themes.json
        - Export als eigenständige JSON
        """)
        desc.setWordWrap(True)
        title_label_layout.addWidget(desc)
        layout.addWidget(title_label)

        # LiveThemeEditor widget
        theme_editor = LiveThemeEditor(config_path)
        layout.addWidget(theme_editor)

        return widget

    def _create_color_picker_tab(self) -> QWidget:
        """Create color picker tab (Phase 5b).

        Returns:
            Configured widget tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        from PySide6.QtWidgets import QLabel
        label = QLabel("ARGB Color-Picker")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        layout.addWidget(label)

        desc = QLabel("""
        Professioneller Color-Picker mit erweiterten Features:
        - Hex-Eingabe (#AARRGGBB)
        - RGB/Alpha Slider und Spinboxes
        - 12 Schnellfarben als Palette
        - Live-Preview mit Transparenzanzeige
        - Callback für Live-Anwendung
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Color picker widget
        color_picker = ARGBColorPicker(apply_callback=lambda c: print(f"Color selected: {c}"))
        layout.addWidget(color_picker)

        # Button to open dialog
        btn_layout = QVBoxLayout()
        btn = QPushButton("✨ Color-Picker als Dialog öffnen")
        btn.setFixedHeight(40)
        btn.clicked.connect(self._show_color_picker_dialog)
        btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        return widget

    def _create_widget_features_tab(self, config_path: Path) -> QWidget:
        """Create widget features editor tab (Phase 5c).

        Args:
            config_path: Path to configuration directory

        Returns:
            Configured widget tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        from PySide6.QtWidgets import QLabel
        label = QLabel("Widget-Features Editor")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        layout.addWidget(label)

        desc = QLabel("""
        Bearbeite Widget-Eigenschaften zur Laufzeit:
        - Property-Baum für alle Widget-Konfigurationen
        - Live-Bearbeitung von Panel-Namen und Einstellungen
        - Tab-Konfigurationen anpassen
        - Menü-Elemente customisieren
        - Änderungen speichern zu JSON-Dateien
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Widget features editor
        try:
            features_editor = WidgetFeaturesEditor(config_path)
            layout.addWidget(features_editor)
        except Exception as e:
            err_label = QLabel(f"Error: {e}")
            layout.addWidget(err_label)

        return widget

    def _create_plugin_system_tab(self) -> QWidget:
        """Create plugin system tab (Phase 5d).

        Returns:
            Configured widget tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        from PySide6.QtWidgets import QLabel
        label = QLabel("Plugin-System")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        layout.addWidget(label)

        desc = QLabel("""
        Dynamisches Plugin-System für erweiterbare Architektur:
        ✅ Automatische Plugin-Erkennung aus Verzeichnissen
        ✅ Factory-Registrierung und Lifecycle-Management
        ✅ Hot-Reload Fähigkeit für Plugins
        ✅ Plugin-Konfiguration und Validierung
        ✅ Signal-basierte Fehlerbehandlung
        
        API-Beispiel:
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Code example
        code = QLabel("""from widgetsystem.core import PluginManager, PluginRegistry

# Registry erstellen
registry = PluginRegistry()

# Manager mit Plugin-Verzeichnissen
manager = PluginManager(
    plugin_dirs=[Path("plugins")],
    registry=registry
)

# Alle Plugins entdecken und laden
loaded = manager.load_all_plugins()

# Plugin Runtime neu laden
manager.reload_plugin("my_plugin")

# Alle registrierten Factories abrufen
factories = registry.get_all_factories()
        """)
        code.setWordWrap(True)
        code_font = QFont("Courier")
        code_font.setPointSize(9)
        code.setFont(code_font)
        layout.addWidget(code)

        layout.addStretch()

        return widget

    def _create_info_tab(self) -> QWidget:
        """Create info tab with overview.

        Returns:
            Configured widget tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        from PySide6.QtWidgets import QLabel
        title = QLabel("🎉 WidgetSystem - Phase 5 Features")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        info_text = QLabel("""
        <b>PROJEKT-STABILISIERUNG ABGESCHLOSSEN ✅</b>
        
        <b>Phase 1-4: Basis-Stabilisierung</b>
        • 50+ Debug-Prints → Logging
        • Public API Exports (45+ Komponenten)
        • Error-Handling verifiziert
        • Test-Suite analysiert
        
        <b>Phase 5a: Live Theme-Editor (4 Klassen)</b>
        • ARGBColorButton - Farbwähler mit Transparenz
        • ThemePropertyEditor - Auto-Prop-Generierung
        • LiveThemeEditor - Echtzeit Theme-Bearbeitung
        • ThemeEditorDialog - Dialog-Wrapper
        
        <b>Phase 5b: ARGB Color-Picker (2 Klassen)</b>
        • Hex-Eingabe (#AARRGGBB Format)
        • RGB/Alpha Slider & Spinboxes
        • 12 vordefinierte Schnellfarben
        • Live-Preview mit Transparenz
        
        <b>Phase 5c: Widget-Features Editor (3 Klassen)</b>
        • WidgetPropertyEditor - Runtime-Bearbeitung
        • WidgetFeaturesEditor - Haupt-Widget
        • WidgetFeaturesEditorDialog - Stats & Dialog
        
        <b>Phase 5d: Plugin-System (2 Klassen)</b>
        • PluginRegistry - Factory-Verwaltung
        • PluginManager - Plugin-Discovery & Loader
        
        <b>Gesamt: 11 neue Klassen | ~2000 Zeilen Code</b>
        
        <b>Implementierte Features:</b>
        ✅ Type Hints auf allen neuen Klassen
        ✅ Google-Style Docstrings
        ✅ Vollständige Logging-Integration
        ✅ Signal-basierte Kommunikation
        ✅ Fehlerbehandlung durchgehend
        ✅ Live-Preview & Callbacks
        ✅ JSON Persistence
        ✅ Hot-Reload Fähigkeit
        """)
        info_text.setWordWrap(True)
        layout.addWidget(info_text)

        layout.addStretch()

        return widget

    def _show_color_picker_dialog(self) -> None:
        """Show color picker dialog."""
        dialog = ARGBColorPickerDialog("#FFFF0000")
        if dialog.exec() == 1:
            color = dialog.get_color()
            print(f"Selected color: {color}")


def main() -> None:
    """Run Phase 5 demo application."""
    app = QApplication(sys.argv)

    window = Phase5DemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
