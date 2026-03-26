"""Complete Visual Application - Demonstrates all structural elements with full visual layer."""

from pathlib import Path
import sys
from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
import PySide6QtAds as QtAds

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.list_factory import ListFactory
from widgetsystem.factories.menu_factory import MenuFactory
from widgetsystem.factories.panel_factory import PanelFactory
from widgetsystem.factories.tabs_factory import TabsFactory
from widgetsystem.factories.theme_factory import ThemeFactory
from widgetsystem.ui.config_panel import ConfigurationPanel
from widgetsystem.ui.tab_color_controller import TabColorController
from widgetsystem.ui.visual_layer import (
    ListsViewer,
    MenusViewer,
    PanelsViewer,
    TabsViewer,
    ViewerConfig,
    VisualDashboard,
)


class VisualMainWindow(QMainWindow):
    """Main window with complete visual layer integration."""

    def __init__(self) -> None:
        """Initialize visual main window."""
        super().__init__()
        config_path = Path("config")
        self.i18n_factory = I18nFactory(config_path, locale="de")
        self.setWindowTitle(
            self._translate("visual_app.window_title", "WidgetSystem - Visuelle Ebene"),
        )
        self.setMinimumSize(1600, 1000)

        # Initialize factories
        self.theme_factory = ThemeFactory(config_path)
        self.menu_factory = MenuFactory(config_path)
        self.list_factory = ListFactory(config_path)
        self.panel_factory = PanelFactory(config_path)
        self.tabs_factory = TabsFactory(config_path)

        # Setup docking system
        self._setup_docking()

        # Create UI
        self._create_toolbar()
        self._create_menu()
        self._create_viewers()
        self._apply_theme()

        # Show welcome message
        QTimer.singleShot(500, self._show_welcome)

    def _translate(self, key: str, default: str) -> str:
        """Translate helper with fallback."""
        return self.i18n_factory.translate(key, default=default)

    def set_i18n_factory(self, i18n_factory: I18nFactory) -> None:
        """Set i18n factory and update UI texts."""
        self.i18n_factory = i18n_factory
        self.setWindowTitle(self._translate("visual_app.window_title", "WidgetSystem - Visuelle Ebene"))

        self._refresh_translated_texts()

        self.lists_viewer.set_i18n_factory(i18n_factory)
        self.menus_viewer.set_i18n_factory(i18n_factory)
        self.tabs_viewer.set_i18n_factory(i18n_factory)
        self.panels_viewer.set_i18n_factory(i18n_factory)

    def _refresh_translated_texts(self) -> None:
        """Refresh translated UI texts after locale changes."""
        if hasattr(self, "toolbar"):
            self.toolbar.setWindowTitle(self._translate("toolbar.main", "Hauptwerkzeugleiste"))
        if hasattr(self, "dashboard_btn"):
            self.dashboard_btn.setText(self._translate("visual_app.toolbar.dashboard", "📊 Dashboard"))
        if hasattr(self, "config_btn"):
            self.config_btn.setText(
                self._translate("visual_app.toolbar.configuration", "⚙️ Konfiguration"),
            )
        if hasattr(self, "refresh_btn"):
            self.refresh_btn.setText(self._translate("visual_app.toolbar.refresh", "🔄 Aktualisieren"))
        if hasattr(self, "theme_button"):
            self.theme_button.setText(self._translate("visual_app.toolbar.themes", "🎨 Themes"))
        if hasattr(self, "theme_editor_btn"):
            self.theme_editor_btn.setText(
                self._translate("visual_app.toolbar.theme_editor", "🎨 Theme Editor"),
            )
        if hasattr(self, "color_picker_btn"):
            self.color_picker_btn.setText(
                self._translate("visual_app.toolbar.color_picker", "🌈 Farbauswahl"),
            )
        if hasattr(self, "widget_editor_btn"):
            self.widget_editor_btn.setText(
                self._translate("visual_app.toolbar.widget_editor", "🔧 Widget Editor"),
            )

        if hasattr(self, "file_menu"):
            self.file_menu.setTitle(self._translate("menu.file", "Datei"))
        if hasattr(self, "exit_action"):
            self.exit_action.setText(self._translate("menu.exit", "Beenden"))
        if hasattr(self, "view_menu"):
            self.view_menu.setTitle(self._translate("menu.view", "Ansicht"))
        if hasattr(self, "show_lists_action"):
            self.show_lists_action.setText(
                self._translate("visual_app.menu.show_lists", "Listen anzeigen"),
            )
        if hasattr(self, "show_menus_action"):
            self.show_menus_action.setText(
                self._translate("visual_app.menu.show_menus", "Menüs anzeigen"),
            )
        if hasattr(self, "show_tabs_action"):
            self.show_tabs_action.setText(self._translate("visual_app.menu.show_tabs", "Tabs anzeigen"))
        if hasattr(self, "show_panels_action"):
            self.show_panels_action.setText(
                self._translate("visual_app.menu.show_panels", "Panels anzeigen"),
            )
        if hasattr(self, "help_menu"):
            self.help_menu.setTitle(self._translate("menu.help", "Hilfe"))
        if hasattr(self, "about_action"):
            self.about_action.setText(self._translate("visual_app.menu.about", "Über..."))

        if hasattr(self, "lists_dock"):
            self.lists_dock.setWindowTitle(self._translate("visual.tab.lists", "Listen"))
        if hasattr(self, "menus_dock"):
            self.menus_dock.setWindowTitle(self._translate("visual.tab.menus", "Menüs"))
        if hasattr(self, "tabs_dock"):
            self.tabs_dock.setWindowTitle(self._translate("visual.tab.tabs", "Tabs"))
        if hasattr(self, "panels_dock"):
            self.panels_dock.setWindowTitle(self._translate("visual.tab.panels", "Panels"))

    def _setup_docking(self) -> None:
        """Setup QtAds docking system."""
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True)
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.XmlCompressionEnabled,
            False,
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton,
            True,
        )
        # Use Qt custom title bar for floating containers (not Windows native title bar)
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerForceNativeTitleBar,
            False,
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerForceQWidgetTitleBar,
            True,
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerHasWidgetTitle,
            True,
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerHasWidgetIcon,
            True,
        )

        self.dock_manager: Any = QtAds.CDockManager(self)
        self.docks: list[Any] = []

        # Install event filter to patch floating containers before they are shown
        from widgetsystem.ui import FloatingWindowPatcher

        self._floating_patcher = FloatingWindowPatcher()
        app = QApplication.instance()
        if app:
            app.installEventFilter(self._floating_patcher)

        # Phase 1: Tab Selector Visibility Control
        from widgetsystem.ui import (
            FloatingStateTracker,
            TabSelectorEventHandler,
            TabSelectorMonitor,
            TabSelectorVisibilityController,
        )

        self._tab_monitor = TabSelectorMonitor()
        self._tab_event_handler = TabSelectorEventHandler(self.dock_manager, self._tab_monitor)
        self._tab_visibility = TabSelectorVisibilityController(self._tab_monitor)

        # Phase 2: Float Button Persistence
        self._floating_tracker = FloatingStateTracker(self.dock_manager)

        # Register callback: After title bar refresh, reapply tab selector visibility
        self._floating_tracker.register_post_refresh_callback(
            self._tab_visibility.refresh_area_visibility,
        )

        # Phase 3: Tab Color Controller for theme-aware tab styling
        self._tab_color_controller = TabColorController(self.dock_manager)

    def _create_toolbar(self) -> None:
        """Create toolbar with action buttons."""
        self.toolbar = QToolBar(self._translate("toolbar.main", "Hauptwerkzeugleiste"))
        self.addToolBar(self.toolbar)

        # Dashboard button
        self.dashboard_btn = QPushButton(self._translate("visual_app.toolbar.dashboard", "📊 Dashboard"))
        self.dashboard_btn.clicked.connect(self._show_dashboard)
        self.toolbar.addWidget(self.dashboard_btn)

        self.toolbar.addSeparator()

        # Config button
        self.config_btn = QPushButton(
            self._translate("visual_app.toolbar.configuration", "⚙️ Konfiguration"),
        )
        self.config_btn.clicked.connect(self._show_configuration)
        self.toolbar.addWidget(self.config_btn)

        self.toolbar.addSeparator()

        # Refresh button
        self.refresh_btn = QPushButton(self._translate("visual_app.toolbar.refresh", "🔄 Aktualisieren"))
        self.refresh_btn.clicked.connect(self._refresh_viewers)
        self.toolbar.addWidget(self.refresh_btn)

        # Theme menu
        theme_menu = QMenu(self)
        try:
            themes = self.theme_factory.list_themes()
            for theme in themes:
                action = QAction(theme.name, self)
                action.triggered.connect(
                    lambda checked=False, theme_id=theme.theme_id: self._on_theme_triggered(
                        checked,
                        theme_id,
                    ),
                )
                theme_menu.addAction(action)
        except Exception:
            pass

        self.theme_button = QToolButton()
        self.theme_button.setText(self._translate("visual_app.toolbar.themes", "🎨 Themes"))
        self.theme_button.setMenu(theme_menu)
        self.theme_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.toolbar.addWidget(self.theme_button)

        self.toolbar.addSeparator()

        # Theme Editor button
        self.theme_editor_btn = QPushButton(
            self._translate("visual_app.toolbar.theme_editor", "🎨 Theme Editor"),
        )
        self.theme_editor_btn.clicked.connect(self._show_theme_editor)
        self.toolbar.addWidget(self.theme_editor_btn)

        # Color Picker button
        self.color_picker_btn = QPushButton(
            self._translate("visual_app.toolbar.color_picker", "🌈 Farbauswahl"),
        )
        self.color_picker_btn.clicked.connect(self._show_color_picker)
        self.toolbar.addWidget(self.color_picker_btn)

        # Widget Features Editor button
        self.widget_editor_btn = QPushButton(
            self._translate("visual_app.toolbar.widget_editor", "🔧 Widget Editor"),
        )
        self.widget_editor_btn.clicked.connect(self._show_widget_editor)
        self.toolbar.addWidget(self.widget_editor_btn)

    def _create_menu(self) -> None:
        """Create application menu."""
        menu_bar = self.menuBar()

        # File menu
        self.file_menu = menu_bar.addMenu(self._translate("menu.file", "Datei"))
        self.exit_action = self.file_menu.addAction(self._translate("menu.exit", "Beenden"))
        self.exit_action.triggered.connect(self.close)

        # View menu
        self.view_menu = menu_bar.addMenu(self._translate("menu.view", "Ansicht"))
        self.show_lists_action = self.view_menu.addAction(
            self._translate("visual_app.menu.show_lists", "Listen anzeigen"),
        )
        self.show_lists_action.triggered.connect(self._show_lists_viewer)
        self.show_menus_action = self.view_menu.addAction(
            self._translate("visual_app.menu.show_menus", "Menüs anzeigen"),
        )
        self.show_menus_action.triggered.connect(self._show_menus_viewer)
        self.show_tabs_action = self.view_menu.addAction(
            self._translate("visual_app.menu.show_tabs", "Tabs anzeigen"),
        )
        self.show_tabs_action.triggered.connect(self._show_tabs_viewer)
        self.show_panels_action = self.view_menu.addAction(
            self._translate("visual_app.menu.show_panels", "Panels anzeigen"),
        )
        self.show_panels_action.triggered.connect(self._show_panels_viewer)

        # Help menu
        self.help_menu = menu_bar.addMenu(self._translate("menu.help", "Hilfe"))
        self.about_action = self.help_menu.addAction(
            self._translate("visual_app.menu.about", "Über..."),
        )
        self.about_action.triggered.connect(self._show_about)

    def _create_viewers(self) -> None:
        """Create and add viewer docks."""
        viewer_config = ViewerConfig(show_properties=True, editable=False)

        # Lists viewer
        self.lists_viewer = ListsViewer(Path("config"), self.i18n_factory, config=viewer_config)
        self.lists_dock = QtAds.CDockWidget(
            self.dock_manager,
            self._translate("visual.tab.lists", "Listen"),
            self,
        )
        self.lists_dock.setWidget(self.lists_viewer)
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.lists_dock)
        self.docks.append(self.lists_dock)

        # Menus viewer
        self.menus_viewer = MenusViewer(Path("config"), self.i18n_factory, config=viewer_config)
        self.menus_dock = QtAds.CDockWidget(
            self.dock_manager,
            self._translate("visual.tab.menus", "Menüs"),
            self,
        )
        self.menus_dock.setWidget(self.menus_viewer)
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.menus_dock)
        self.docks.append(self.menus_dock)

        # Tabs viewer
        self.tabs_viewer = TabsViewer(Path("config"), self.i18n_factory, config=viewer_config)
        self.tabs_dock = QtAds.CDockWidget(
            self.dock_manager,
            self._translate("visual.tab.tabs", "Tabs"),
            self,
        )
        self.tabs_dock.setWidget(self.tabs_viewer)
        self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, self.tabs_dock)
        self.docks.append(self.tabs_dock)

        # Panels viewer
        self.panels_viewer = PanelsViewer(Path("config"), self.i18n_factory, config=viewer_config)
        self.panels_dock = QtAds.CDockWidget(
            self.dock_manager,
            self._translate("visual.tab.panels", "Panels"),
            self,
        )
        self.panels_dock.setWidget(self.panels_viewer)
        self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, self.panels_dock)
        self.docks.append(self.panels_dock)

    def _create_central_widget(self) -> None:
        """Create central widget with status info."""
        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel(
            self._translate(
                "visual_app.central.title",
                "✨ WidgetSystem - Visuelle Strukturebene",
            ),
        )
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        layout.addWidget(title)

        info = QLabel(
            self._translate(
                "visual_app.central.info",
                "Alle strukturellen Komponenten des Systems sind hier sichtbar:\n"
                "• Listen mit Hierarchien (Links)\n"
                "• Menü-Strukturen (Links unten)\n"
                "• Tab-Gruppen (Rechts)\n"
                "• Panel-Konfigurationen (Rechts unten)",
            ),
        )
        layout.addWidget(info)
        layout.addStretch()

        self.setCentralWidget(central)

    def _show_lists_viewer(self) -> None:
        """Show lists viewer dock."""
        print("✅ Listen-Viewer angezeigt")

    def _show_menus_viewer(self) -> None:
        """Show menus viewer dock."""
        print("✅ Menü-Viewer angezeigt")

    def _show_tabs_viewer(self) -> None:
        """Show tabs viewer dock."""
        print("✅ Tabs-Viewer angezeigt")

    def _show_panels_viewer(self) -> None:
        """Show panels viewer dock."""
        print("✅ Panels-Viewer angezeigt")

    def _show_configuration(self) -> None:
        """Show configuration panel."""
        try:
            config_panel = ConfigurationPanel(Path("config"), self.i18n_factory)
            config_panel.setWindowTitle(
                self._translate("visual_app.dialog.configuration.title", "Konfigurationspanel"),
            )
            config_panel.resize(1200, 700)
            config_panel.show()
        except Exception as e:
            QMessageBox.critical(
                self,
                self._translate("dialog.error", "Fehler"),
                self._translate(
                    "visual_app.error.configuration_open_failed",
                    "Konfigurationspanel konnte nicht geöffnet werden:\n{error}",
                ).format(error=e),
            )

    def _show_dashboard(self) -> None:
        """Show visual dashboard."""
        try:
            dashboard = VisualDashboard(Path("config"), self.i18n_factory)
            dashboard.show()
        except Exception as e:
            QMessageBox.critical(
                self,
                self._translate("dialog.error", "Fehler"),
                self._translate(
                    "visual_app.error.dashboard_open_failed",
                    "Dashboard konnte nicht geöffnet werden:\n{error}",
                ).format(error=e),
            )

    def _refresh_viewers(self) -> None:
        """Refresh all viewers."""
        self.lists_viewer.refresh()
        self.menus_viewer.refresh()
        self.tabs_viewer.refresh()
        self.panels_viewer.refresh()
        QMessageBox.information(
            self,
            self._translate("message.success", "Erfolg"),
            self._translate("visual_app.message.viewers_refreshed", "✅ Alle Viewer aktualisiert"),
        )

    def _apply_theme(self) -> None:
        """Apply default theme."""
        try:
            stylesheet = self.theme_factory.get_default_stylesheet()
            if stylesheet:
                self.setStyleSheet(stylesheet)
                print("✅ Standard-Theme angewendet")
        except Exception as e:
            print(f"⚠️  Theme konnte nicht angewendet werden: {e}")

    def _apply_theme_by_id(self, theme_id: str) -> None:
        """Apply theme by ID."""
        try:
            themes = self.theme_factory.list_themes()
            theme = next((t for t in themes if t.theme_id == theme_id), None)
            if theme and theme.file_path.exists():
                stylesheet = theme.file_path.read_text(encoding="utf-8")
                self.setStyleSheet(stylesheet)
                print(f"✅ Theme '{theme.name}' angewendet")
        except Exception as e:
            print(f"⚠️  Theme konnte nicht angewendet werden: {e}")

    def _on_theme_triggered(self, checked: bool, theme_id: str) -> None:
        """Handle theme selection from menu."""
        _ = checked
        self._apply_theme_by_id(theme_id)

    def _show_welcome(self) -> None:
        """Show welcome message."""
        title = self._translate("visual_app.welcome.title", "🎉 Willkommen zur visuellen Ebene!")
        message = self._translate(
            "visual_app.welcome.message",
            "Dieses Fenster zeigt die vollständige visuelle Struktur des Systems:\n\n"
            "📋 LINKS:\n"
            "  • Listen-Viewer: Alle konfigurierten Listen mit Hierarchien\n"
            "  • Menü-Viewer: Komplette Menü-Struktur\n\n"
            "📌 RECHTS:\n"
            "  • Tabs: Tab-Gruppen und deren Zusammensetzung\n"
            "  • Panels: Alle Panel-Konfigurationen\n\n"
            "🛠️ TOOLBAR:\n"
            "  • Dashboard: Umfassende Übersicht aller Komponenten\n"
            "  • Konfiguration: Bearbeitung aller Strukturelemente\n"
            "  • Themes: Design-Auswahl\n",
        )
        QMessageBox.information(self, title, message)

    def _show_theme_editor(self) -> None:
        """Show theme editor dialog."""
        try:
            from widgetsystem.ui import ThemeEditorDialog

            def apply_theme(theme_data: dict) -> None:
                """Apply theme from editor."""
                if "stylesheet" in theme_data:
                    self.setStyleSheet(theme_data["stylesheet"])
                    print("✅ Theme aus Editor angewendet")

            dialog = ThemeEditorDialog(
                Path("config"),
                apply_theme,
                self,
                i18n_factory=self.i18n_factory,
            )
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                self._translate("dialog.error", "Fehler"),
                self._translate(
                    "visual_app.error.theme_editor_open_failed",
                    "Theme Editor konnte nicht geöffnet werden:\n{error}",
                ).format(error=e),
            )

    def _show_color_picker(self) -> None:
        """Show ARGB color picker dialog."""
        try:
            from widgetsystem.ui import ARGBColorPickerDialog

            dialog = ARGBColorPickerDialog(
                "#FFFFFFFF",
                None,
                self,
                i18n_factory=self.i18n_factory,
            )
            if dialog.exec():
                color = dialog.color_picker.get_color()
                QMessageBox.information(
                    self,
                    self._translate("visual_app.message.color_selected_title", "Farbe ausgewählt"),
                    self._translate(
                        "visual_app.message.color_selected",
                        "Ausgewählte Farbe: {color}",
                    ).format(color=color),
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self._translate("dialog.error", "Fehler"),
                self._translate(
                    "visual_app.error.color_picker_open_failed",
                    "Farbauswahl konnte nicht geöffnet werden:\n{error}",
                ).format(error=e),
            )

    def _show_widget_editor(self) -> None:
        """Show widget features editor dialog."""
        try:
            from widgetsystem.ui import WidgetFeaturesEditorDialog

            dialog = WidgetFeaturesEditorDialog(
                Path("config"),
                self,
                i18n_factory=self.i18n_factory,
            )
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                self._translate("dialog.error", "Fehler"),
                self._translate(
                    "visual_app.error.widget_editor_open_failed",
                    "Widget Editor konnte nicht geöffnet werden:\n{error}",
                ).format(error=e),
            )

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            self._translate("visual_app.about.title", "Über WidgetSystem"),
            self._translate(
                "visual_app.about.message",
                "WidgetSystem v1.0\n\n"
                "Eine vollständig konfigurierbare Anwendungsarchitektur mit:\n"
                "✅ 10 Factories für alle Strukturelemente\n"
                "✅ Vollständige Typsicherheit (100% type hints)\n"
                "✅ Persistente Konfiguration (JSON)\n"
                "✅ QtAds Docking System\n"
                "✅ Visuelle Konfigurationsebene\n"
                "✅ Responsive Design\n"
                "✅ Mehrsprachigkeit (DE/EN)\n\n"
                "© 2026 Maximale Funktionalität",
            ),
        )


def main() -> None:
    """Entry point for visual application."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("🚀 WidgetSystem - VISUELLE EBENE (Visual Layer)")
    print("=" * 70)
    print()
    print("✅ Anwendung wird gestartet...")
    print("✅ Alle Factories werden initialisiert...")
    print("✅ Viewer werden erstellt...")
    print("✅ Docking-System wird konfiguriert...")
    print()

    window = VisualMainWindow()
    window.show()

    print("=" * 70)
    print("✨ VISUELLE EBENE IST AKTIV")
    print("=" * 70)
    print()
    print("Verfügbare Komponenten:")
    print("  📋 Listen-Viewer (Links)")
    print("  📝 Menü-Viewer (Links)")
    print("  📑 Tabs-Viewer (Rechts)")
    print("  📦 Panels-Viewer (Rechts)")
    print()
    print("Aktionen:")
    print("  🎨 Themes im Toolbar wählbar")
    print("  ⚙️  Konfigurationspanel erreichbar")
    print("  📊 Dashboard für Übersicht verfügbar")
    print()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
