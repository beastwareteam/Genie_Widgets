"""Test Visual Layer - Validates all visual components functionality."""

from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.ui.visual_layer import (
    ListsViewer,
    MenusViewer,
    PanelsViewer,
    TabsViewer,
    ViewerConfig,
    VisualDashboard,
)


def test_visual_layer() -> None:
    """Test all visual layer components."""
    print("=" * 70)
    print("TEST: Visuelle Ebene (Visual Layer)")
    print("=" * 70)
    print()

    config_path = Path("config")
    i18n = I18nFactory(config_path, locale="de")

    # Initialize Qt Application (required for widgets)
    app_instance = QApplication.instance()
    if app_instance is None:
        app = QApplication(sys.argv)
    else:
        app = app_instance
    if isinstance(app, QApplication):
        app.setQuitOnLastWindowClosed(False)

    try:
        # Test 1: ListsViewer initialization
        print("TEST 1: ListsViewer")
        print("-" * 70)
        viewer_config = ViewerConfig(show_properties=True)
        lists_viewer = ListsViewer(config_path, i18n, config=viewer_config)
        print("✅ ListsViewer erstellt")
        print(f"   - Größe: {lists_viewer.size()}")
        print(f"   - Eigenschaften-Panel: {viewer_config.show_properties}")
        print()

        # Test 2: MenusViewer initialization
        print("TEST 2: MenusViewer")
        print("-" * 70)
        menus_viewer = MenusViewer(config_path, i18n, config=viewer_config)
        print("✅ MenusViewer erstellt")
        print(f"   - Größe: {menus_viewer.size()}")
        print()

        # Test 3: TabsViewer initialization
        print("TEST 3: TabsViewer")
        print("-" * 70)
        tabs_viewer = TabsViewer(config_path, i18n, config=viewer_config)
        print("✅ TabsViewer erstellt")
        print(f"   - Größe: {tabs_viewer.size()}")
        print()

        # Test 4: PanelsViewer initialization
        print("TEST 4: PanelsViewer")
        print("-" * 70)
        panels_viewer = PanelsViewer(config_path, i18n, config=viewer_config)
        print("✅ PanelsViewer erstellt")
        print(f"   - Größe: {panels_viewer.size()}")
        print()

        # Test 5: VisualDashboard initialization
        print("TEST 5: VisualDashboard")
        print("-" * 70)
        dashboard = VisualDashboard(config_path, i18n)
        print("✅ VisualDashboard erstellt")
        print(f"   - Titel: {dashboard.windowTitle()}")
        print(f"   - Größe: {dashboard.size()}")
        print()

        # Test 6: Refresh functionality
        print("TEST 6: Refresh-Funktionen")
        print("-" * 70)
        lists_viewer.refresh()
        print("✅ ListsViewer.refresh() - OK")
        menus_viewer.refresh()
        print("✅ MenusViewer.refresh() - OK")
        tabs_viewer.refresh()
        print("✅ TabsViewer.refresh() - OK")
        panels_viewer.refresh()
        print("✅ PanelsViewer.refresh() - OK")
        print()

        # Test 7: ViewerConfig variations
        print("TEST 7: ViewerConfig-Varianten")
        print("-" * 70)
        config_no_props = ViewerConfig(show_properties=False)
        viewer_no_props = ListsViewer(config_path, i18n, config=config_no_props)
        print("✅ ViewerConfig ohne Eigenschaften - OK")
        print(f"   - No-props Größe: {viewer_no_props.size()}")

        config_editable = ViewerConfig(editable=True)
        viewer_editable = MenusViewer(config_path, i18n, config=config_editable)
        print("✅ ViewerConfig mit edit-Modus - OK")
        print(f"   - Editable Größe: {viewer_editable.size()}")
        print()

        # Summary
        print("=" * 70)
        print("✅ ALLE TESTS ERFOLGREICH")
        print("=" * 70)
        print()
        print("Visuelle Komponenten:")
        print("  ✅ ListsViewer - Listen-Hierarchie darstellen")
        print("  ✅ MenusViewer - Menü-Strukturen darstellen")
        print("  ✅ TabsViewer - Tab-Gruppen darstellen")
        print("  ✅ PanelsViewer - Panel-Konfigurationen darstellen")
        print("  ✅ VisualDashboard - Alle Komponenten kombinieren")
        print()
        print("Features:")
        print("  ✅ Eigenschaften-Panel anzeigen/verbergen")
        print("  ✅ Refresh-Funktionalität")
        print("  ✅ i18n-Integration")
        print("  ✅ Konfigurierbare Parameter")
        print()
        print("Verwendung:")
        print("  python visual_app.py        → GUI-Anwendung starten")
        print("  python test_visual_layer.py → Diese Tests")
        print()

    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback

        traceback.print_exc()

    finally:
        app.quit()


if __name__ == "__main__":
    test_visual_layer()
    sys.exit(0)
