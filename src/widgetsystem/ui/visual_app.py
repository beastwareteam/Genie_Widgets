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


    ViewerConfig,
    VisualDashboard,
)


class VisualMainWindow(QMainWindow):
    """Main window with complete visual layer integration."""

    def __init__(self) -> None:
        """Initialize visual main window."""
        super().__init__()
        self.setWindowTitle("WidgetSystem - Visuelle Ebene")
        self.setMinimumSize(1600, 1000)

        # Initialize factories
        config_path = Path("config")
        self.i18n_factory = I18nFactory(config_path, locale="de")
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
        toolbar = QToolBar(
            self.i18n_factory.translate("toolbar.main", default="Hauptwerkzeugleiste"),
        )
        self.addToolBar(toolbar)

        # Dashboard button
        dashboard_btn = QPushButton("📊 Dashboard")
        dashboard_btn.clicked.connect(self._show_dashboard)
        toolbar.addWidget(dashboard_btn)

        toolbar.addSeparator()

        # Config button
        config_btn = QPushButton("⚙️ Konfiguration")
        config_btn.clicked.connect(self._show_configuration)
        toolbar.addWidget(config_btn)

        toolbar.addSeparator()

        # Refresh button
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.clicked.connect(self._refresh_viewers)
        toolbar.addWidget(refresh_btn)

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

        theme_button = QToolButton()
        theme_button.setText("🎨 Themes")
        theme_button.setMenu(theme_menu)
        theme_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(theme_button)

        toolbar.addSeparator()

        # Theme Editor button
        theme_editor_btn = QPushButton("🎨 Theme Editor")
        theme_editor_btn.clicked.connect(self._show_theme_editor)
        toolbar.addWidget(theme_editor_btn)

        # Color Picker button
        color_picker_btn = QPushButton("🌈 Farbauswahl")
        color_picker_btn.clicked.connect(self._show_color_picker)
        toolbar.addWidget(color_picker_btn)

        # Widget Features Editor button
        widget_editor_btn = QPushButton("🔧 Widget Editor")
        widget_editor_btn.clicked.connect(self._show_widget_editor)
        toolbar.addWidget(widget_editor_btn)

    def _create_menu(self) -> None:
        """Create application menu."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu(self.i18n_factory.translate("menu.file", default="Datei"))
        exit_action = file_menu.addAction(
            self.i18n_factory.translate("menu.exit", default="Beenden"),
        )
        exit_action.triggered.connect(self.close)

        # View menu
        view_menu = menu_bar.addMenu(self.i18n_factory.translate("menu.view", default="Ansicht"))
        show_lists_action = view_menu.addAction("Listen anzeigen")
        show_lists_action.triggered.connect(self._show_lists_viewer)
        show_menus_action = view_menu.addAction("Menüs anzeigen")
        show_menus_action.triggered.connect(self._show_menus_viewer)
        show_tabs_action = view_menu.addAction("Tabs anzeigen")
        show_tabs_action.triggered.connect(self._show_tabs_viewer)
        show_panels_action = view_menu.addAction("Panels anzeigen")
        show_panels_action.triggered.connect(self._show_panels_viewer)

        # Help menu
        help_menu = menu_bar.addMenu(self.i18n_factory.translate("menu.help", default="Hilfe"))
        about_action = help_menu.addAction("Über...")
        about_action.triggered.connect(self._show_about)

    def _create_viewers(self) -> None:
        """Create and add viewer docks."""
        viewer_config = ViewerConfig(show_properties=True, editable=False)

        # Lists viewer
        self.lists_viewer = ListsViewer(Path("config"), self.i18n_factory, config=viewer_config)
        lists_dock = QtAds.CDockWidget(self.dock_manager, "Listen", self)
        lists_dock.setWidget(self.lists_viewer)
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, lists_dock)
        self.docks.append(lists_dock)

        # Menus viewer
        self.menus_viewer = MenusViewer(Path("config"), self.i18n_factory, config=viewer_config)
        menus_dock = QtAds.CDockWidget(self.dock_manager, "Menüs", self)
        menus_dock.setWidget(self.menus_viewer)
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, menus_dock)
        self.docks.append(menus_dock)

        # Tabs viewer
        # self.tabs_viewer = TabsViewer(Path("config"), self.i18n_factory, config=viewer_config)
        tabs_dock = QtAds.CDockWidget(self.dock_manager, "Tabs", self)
        tabs_dock.setWidget(self.tabs_viewer)
        self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, tabs_dock)
        self.docks.append(tabs_dock)

        # Panels viewer
        # self.panels_viewer = PanelsViewer(Path("config"), self.i18n_factory, config=viewer_config)
        panels_dock = QtAds.CDockWidget(self.dock_manager, "Panels", self)
        panels_dock.setWidget(self.panels_viewer)
        self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, panels_dock)
        self.docks.append(panels_dock)

    def _create_central_widget(self) -> None:
        """Create central widget with status info."""
        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel("✨ WidgetSystem - Visuelle Strukturebene")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        layout.addWidget(title)

        info = QLabel(
            "Alle strukturellen Komponenten des Systems sind hier sichtbar:\n"
            "• Listen mit Hierarchien (Links)\n"
            "• Menü-Strukturen (Links unten)\n"
            "• Tab-Gruppen (Rechts)\n"
            "• Panel-Konfigurationen (Rechts unten)",
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
            config_panel.setWindowTitle("Konfigurationspanel")
            config_panel.resize(1200, 700)
            config_panel.show()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Konfigurationspanel konnte nicht geöffnet werden:\n{e}",
            )

    def _show_dashboard(self) -> None:
        """Show visual dashboard."""
        try:
            dashboard = VisualDashboard(Path("config"), self.i18n_factory)
            dashboard.show()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Dashboard konnte nicht geöffnet werden:\n{e}")

    def _refresh_viewers(self) -> None:
        """Refresh all viewers."""
        self.lists_viewer.refresh()
        self.menus_viewer.refresh()
        self.tabs_viewer.refresh()
        self.panels_viewer.refresh()
        QMessageBox.information(self, "Erfolg", "✅ Alle Viewer aktualisiert")

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
        title = "🎉 Willkommen zur visuellen Ebene!"
        message = (
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
            "  • Themes: Design-Auswahl\n"
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

            dialog = ThemeEditorDialog(Path("config"), apply_theme, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Theme Editor konnte nicht geöffnet werden:\n{e}",
            )

    def _show_color_picker(self) -> None:
        """Show ARGB color picker dialog."""
        try:
            from widgetsystem.ui import ARGBColorPickerDialog

            dialog = ARGBColorPickerDialog("#FFFFFFFF", None, self)
            if dialog.exec():
                color = dialog.color_picker.get_color()
                QMessageBox.information(
                    self,
                    "Farbe ausgewählt",
                    f"Ausgewählte Farbe: {color}",
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Farbauswahl konnte nicht geöffnet werden:\n{e}",
            )

    def _show_widget_editor(self) -> None:
        """Show widget features editor dialog."""
        try:
            from widgetsystem.ui import WidgetFeaturesEditorDialog

            dialog = WidgetFeaturesEditorDialog(Path("config"), self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Widget Editor konnte nicht geöffnet werden:\n{e}",
            )

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "Über WidgetSystem",
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
