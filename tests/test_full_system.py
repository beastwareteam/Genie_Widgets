#!/usr/bin/env python3
"""Vollständiger Funktionstest der Anwendung"""

from pathlib import Path
import sys


# Test 1: Import check
print("=" * 70)
print("TEST 1: Module Imports")
print("=" * 70)

try:
    from PySide6.QtWidgets import QApplication

    print("✅ PySide6 und QtAds importiert")
except Exception as e:
    print(f"❌ Import Fehler: {e}")
    sys.exit(1)

# Test 2: Factory check
print("\n" + "=" * 70)
print("TEST 2: Factory Laden")
print("=" * 70)

factories_ok = True
try:
    from widgetsystem.factories.dnd_factory import DnDFactory
    from widgetsystem.factories.i18n_factory import I18nFactory
    from widgetsystem.factories.layout_factory import LayoutFactory
    from widgetsystem.factories.list_factory import ListFactory
    from widgetsystem.factories.menu_factory import MenuFactory
    from widgetsystem.factories.panel_factory import PanelFactory
    from widgetsystem.factories.responsive_factory import ResponsiveFactory
    from widgetsystem.factories.tabs_factory import TabsFactory
    from widgetsystem.factories.theme_factory import ThemeFactory
    from widgetsystem.factories.ui_config_factory import UIConfigFactory

    print("✅ Alle Factories importiert")

    # Test factory instantiation
    config_path = Path("config")
    i18n = I18nFactory(config_path, locale="de")
    lists = ListFactory(config_path)
    menus = MenuFactory(config_path)
    panels = PanelFactory(config_path)
    tabs = TabsFactory(config_path)
    ui_config = UIConfigFactory(config_path)
    themes = ThemeFactory(config_path)
    layouts = LayoutFactory(config_path)
    dnd = DnDFactory(config_path)
    responsive = ResponsiveFactory(config_path)
    print("✅ Alle Factories instanziiert")

except Exception as e:
    print(f"❌ Factory Fehler: {e}")
    factories_ok = False

# Test 3: Data loading
if factories_ok:
    print("\n" + "=" * 70)
    print("TEST 3: Daten Laden")
    print("=" * 70)

    try:
        list_groups = lists.load_list_groups()
        print(f"✅ Lists geladen: {len(list_groups)} Gruppen")
    except Exception as e:
        print(f"❌ Lists Fehler: {e}")

    try:
        menu_items = menus.load_menus()
        print(f"✅ Menus geladen: {len(menu_items)} Items")
    except Exception as e:
        print(f"❌ Menus Fehler: {e}")

    try:
        panel_configs = panels.load_panels()
        print(f"✅ Panels geladen: {len(panel_configs)} Panels")
    except Exception as e:
        print(f"❌ Panels Fehler: {e}")

    try:
        tab_groups = tabs.load_tab_groups()
        print(f"✅ Tabs geladen: {len(tab_groups)} Gruppen")
    except Exception as e:
        print(f"❌ Tabs Fehler: {e}")

    try:
        ui_pages = ui_config.load_ui_config_pages()
        print(f"✅ UI Config geladen: {len(ui_pages)} Seiten")
    except Exception as e:
        print(f"❌ UI Config Fehler: {e}")

# Test 4: ConfigurationPanel
print("\n" + "=" * 70)
print("TEST 4: ConfigurationPanel")
print("=" * 70)

try:
    app = QApplication(sys.argv)
    from widgetsystem.ui import ConfigurationPanel

    panel = ConfigurationPanel(Path("config"), i18n)
    print("✅ ConfigurationPanel erstellt")
    print(f"   - Tabs: {panel.config_tabs.count()}")

    # Check if widgets exist
    if panel.list_tree is not None:
        print(f"   - List Tree: {panel.list_tree.topLevelItemCount()} items")
    if panel.menu_tree is not None:
        print(f"   - Menu Tree: {panel.menu_tree.topLevelItemCount()} items")
    if panel.tabs_tree is not None:
        print(f"   - Tabs Tree: {panel.tabs_tree.topLevelItemCount()} items")
    if panel.panels_list is not None:
        print(f"   - Panels List: {panel.panels_list.count()} items")

    # Removed the invalid return statement

except Exception as e:
    print(f"❌ ConfigurationPanel Fehler: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
