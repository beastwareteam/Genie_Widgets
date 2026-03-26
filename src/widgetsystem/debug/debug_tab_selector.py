"""Debug Script - Analysiert CDockAreaTitleBar und Tab Selector Struktur.

Dieses Script startet die App und gibt detaillierte Debug-Informationen aus
über die Title Bar Struktur und alle Widgets darin.
"""

import sys
from pathlib import Path

import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


def analyze_title_bar(title_bar, area_name: str = "unknown") -> None:
    """Analysiert die Title Bar Struktur detailliert."""
    print(f"\n{'='*80}")
    print(f"🔍 ANALYZING TITLE BAR: {area_name}")
    print(f"{'='*80}")

    print(f"\n📦 Title Bar Type: {type(title_bar).__name__}")
    print(f"📦 Title Bar Object: {title_bar}")

    # Alle Attribute auflisten
    print(f"\n📋 Available Attributes:")
    attrs = [a for a in dir(title_bar) if not a.startswith('_')]
    for attr in sorted(attrs)[:20]:  # Erste 20
        print(f"  - {attr}")

    # Suche nach Tab-bezogenen Methoden
    print(f"\n🔎 Tab-related Attributes:")
    tab_attrs = [a for a in dir(title_bar) if 'tab' in a.lower() or 'menu' in a.lower()]
    for attr in sorted(tab_attrs):
        print(f"  - {attr}")

    # Kinder-Widgets
    print(f"\n👶 Child Widgets:")
    children = title_bar.findChildren(QWidget)
    for i, child in enumerate(children[:10]):  # Erste 10
        print(f"  [{i}] {type(child).__name__} - ObjectName: '{child.objectName()}'")
        print(f"      Visible: {child.isVisible()}")
        print(f"      Size: {child.width()}x{child.height()}")

        # Spezielle Checks
        if 'Button' in type(child).__name__ or 'Combo' in type(child).__name__:
            print(f"      ⚠️  POTENTIAL TAB SELECTOR BUTTON!")

    # Versuche spezifische tab selector Methoden
    print(f"\n🎯 Trying to find Tab Selector:")

    if hasattr(title_bar, 'tabsMenuButton'):
        try:
            btn = title_bar.tabsMenuButton()
            print(f"  ✅ tabsMenuButton() found: {btn}")
            print(f"     Type: {type(btn).__name__}")
            print(f"     Visible: {btn.isVisible() if btn else 'N/A'}")
        except Exception as e:
            print(f"  ❌ Error calling tabsMenuButton(): {e}")
    else:
        print(f"  ❌ No tabsMenuButton() method")

    if hasattr(title_bar, 'tabBar'):
        try:
            tab_bar = title_bar.tabBar()
            print(f"  ✅ tabBar() found: {tab_bar}")
        except Exception as e:
            print(f"  ❌ Error calling tabBar(): {e}")
    else:
        print(f"  ❌ No tabBar() method")


def debug_dock_areas(dock_manager) -> None:
    """Debuggt alle Dock Areas im Manager."""
    print(f"\n{'#'*80}")
    print(f"🏢 DOCK MANAGER ANALYSIS")
    print(f"{'#'*80}")

    # Alle dock areas finden
    print(f"\n📍 Finding all Dock Areas...")

    # Methode 1: Über openedDockAreas
    if hasattr(dock_manager, 'openedDockAreas'):
        try:
            areas = dock_manager.openedDockAreas()
            print(f"\n✅ Found {len(areas)} opened dock areas via openedDockAreas()")

            for i, area in enumerate(areas):
                area_name = f"Area_{i}"
                if hasattr(area, 'objectName') and area.objectName():
                    area_name = area.objectName()

                # Tab Count
                tab_count = 0
                if hasattr(area, 'dockWidgetsCount'):
                    tab_count = area.dockWidgetsCount()
                elif hasattr(area, 'tabCount'):
                    tab_count = area.tabCount()

                print(f"\n  📌 {area_name}")
                print(f"     Tabs: {tab_count}")

                # Title Bar analysieren
                if hasattr(area, 'titleBar'):
                    title_bar = area.titleBar()
                    if title_bar:
                        analyze_title_bar(title_bar, area_name)
        except Exception as e:
            print(f"❌ Error with openedDockAreas(): {e}")

    # Methode 2: Über alle dock widgets
    if hasattr(dock_manager, 'dockWidgetsMap'):
        try:
            widgets_map = dock_manager.dockWidgetsMap()
            print(f"\n✅ Found {len(widgets_map)} dock widgets via dockWidgetsMap()")
        except Exception as e:
            print(f"❌ Error with dockWidgetsMap(): {e}")


class DebugMainWindow(QMainWindow):
    """Debug Main Window mit minimalem Setup."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug - Tab Selector Analysis")
        self.setMinimumSize(1000, 600)

        # QtAds Setup
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True
        )

        self.dock_manager = QtAds.CDockManager(self)

        # Erstelle 2 Panels im selben Bereich (für Tab-Test)
        dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1", self)
        dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock1)

        dock2 = QtAds.CDockWidget(self.dock_manager, "Panel 2", self)
        dock2.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock2)

        # Debug nach kurzer Verzögerung
        QTimer.singleShot(1000, self.run_debug)

    def run_debug(self):
        """Führt Debug-Analyse aus."""
        debug_dock_areas(self.dock_manager)

        print(f"\n\n{'='*80}")
        print(f"✅ DEBUG ANALYSIS COMPLETE")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebugMainWindow()
    window.show()

    # Nach 5 Sekunden automatisch schließen
    QTimer.singleShot(5000, app.quit)

    sys.exit(app.exec())
