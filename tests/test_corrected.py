"""Test Script - Testet korrigierte Tab Selector Visibility.

Startet App mit korrigierter Implementierung und zeigt ob tabsMenuButton
korrekt gefunden und gesteuert wird.
"""

import sys
from pathlib import Path

import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

# Import der korrigierten Module
sys.path.insert(0, str(Path(__file__).parent / "src"))

from widgetsystem.ui.tab_selector_monitor import TabSelectorMonitor
from widgetsystem.ui.tab_selector_event_handler import TabSelectorEventHandler
from widgetsystem.ui.tab_selector_visibility_controller import TabSelectorVisibilityController


class DemoWindow(QMainWindow):
    """Demo Window mit Tab Selector Control (not a pytest test class)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEST - Tab Selector Visibility (Corrected)")
        self.setMinimumSize(1000, 600)
        
        # QtAds Setup
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DockAreaHasTabsMenuButton, True  # Wichtig!
        )
        
        self.dock_manager = QtAds.CDockManager(self)
        
        # Phase 1: Tab Selector Visibility Control (Korrigiert)
        self._tab_monitor = TabSelectorMonitor()
        self._tab_event_handler = TabSelectorEventHandler(self.dock_manager, self._tab_monitor)
        self._tab_visibility = TabSelectorVisibilityController(self._tab_monitor)
        
        # Erstelle 1 Panel (sollte Pfeil AUSBLENDEN)
        self.dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1 (Allein)", self)
        self.dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, self.dock1)
        
        # Nach 2 Sekunden: Prüfe ob Pfeil ausgeblendet ist
        QTimer.singleShot(2000, self.check_single_tab)
        
        # Nach 4 Sekunden: Füge 2. Panel hinzu (sollte Pfeil EINBLENDEN)
        QTimer.singleShot(4000, self.add_second_panel)
        
        # Nach 6 Sekunden: Prüfe ob Pfeil sichtbar ist
        QTimer.singleShot(6000, self.check_multiple_tabs)
        
        # Nach 8 Sekunden: Schließe 2. Panel (sollte Pfeil AUSBLENDEN)
        QTimer.singleShot(8000, self.close_second_panel)
        
        # Nach 10 Sekunden: Final Check
        QTimer.singleShot(10000, self.final_check)
        
        # Nach 12 Sekunden: Schließen
        QTimer.singleShot(12000, app.quit)
    
    def check_single_tab(self):
        """Check: Pfeil sollte ausgeblendet sein bei 1 Tab."""
        print(f"\n{'='*60}")
        print(f"✅ CHECK 1: Single Tab - Button should be HIDDEN")
        print(f"{'='*60}")
        
        areas = self.dock_manager.openedDockAreas()
        for i, area in enumerate(areas):
            title_bar = area.titleBar()
            if title_bar:
                button = title_bar.findChild(QWidget, "tabsMenuButton")
                if button:
                    is_visible = button.isVisible()
                    tab_count = area.dockWidgetsCount() if hasattr(area, 'dockWidgetsCount') else 0
                    
                    print(f"  Area {i}:")
                    print(f"    Tab Count: {tab_count}")
                    print(f"    tabsMenuButton Visible: {is_visible}")
                    print(f"    Expected: False (1 tab)")
                    
                    if is_visible and tab_count == 1:
                        print(f"    ❌ FAIL: Button is visible but should be hidden!")
                    elif not is_visible and tab_count == 1:
                        print(f"    ✅ PASS: Button is correctly hidden!")
                    else:
                        print(f"    ⚠️  UNEXPECTED STATE")
    
    def add_second_panel(self):
        """Füge 2. Panel hinzu."""
        print(f"\n{'='*60}")
        print(f"➕ ADDING SECOND PANEL as Tab")
        print(f"{'='*60}")
        
        self.dock2 = QtAds.CDockWidget(self.dock_manager, "Panel 2 (Tab)", self)
        self.dock2.setWidget(QWidget())
        
        # Füge als Tab im selben Bereich hinzu
        area = self.dock1.dockAreaWidget()
        if area:
            self.dock_manager.addDockWidgetTabToArea(self.dock2, area)
            print(f"  ✅ Panel 2 added as tab to same area")
        else:
            print(f"  ❌ Could not find area for Panel 1")
    
    def check_multiple_tabs(self):
        """Check: Pfeil sollte sichtbar sein bei 2+ Tabs."""
        print(f"\n{'='*60}")
        print(f"✅ CHECK 2: Multiple Tabs - Button should be VISIBLE")
        print(f"{'='*60}")
        
        areas = self.dock_manager.openedDockAreas()
        for i, area in enumerate(areas):
            title_bar = area.titleBar()
            if title_bar:
                button = title_bar.findChild(QWidget, "tabsMenuButton")
                if button:
                    is_visible = button.isVisible()
                    tab_count = area.dockWidgetsCount() if hasattr(area, 'dockWidgetsCount') else 0
                    
                    print(f"  Area {i}:")
                    print(f"    Tab Count: {tab_count}")
                    print(f"    tabsMenuButton Visible: {is_visible}")
                    print(f"    Expected: True (2+ tabs)")
                    
                    if is_visible and tab_count > 1:
                        print(f"    ✅ PASS: Button is correctly visible!")
                    elif not is_visible and tab_count > 1:
                        print(f"    ❌ FAIL: Button is hidden but should be visible!")
                    else:
                        print(f"    ⚠️  UNEXPECTED STATE")
    
    def close_second_panel(self):
        """Schließe 2. Panel."""
        print(f"\n{'='*60}")
        print(f"➖ CLOSING SECOND PANEL")
        print(f"{'='*60}")
        
        if hasattr(self, 'dock2'):
            self.dock2.close()
            print(f"  ✅ Panel 2 closed")
    
    def final_check(self):
        """Final Check: Pfeil sollte wieder ausgeblendet sein."""
        print(f"\n{'='*60}")
        print(f"✅ CHECK 3: After Close - Button should be HIDDEN again")
        print(f"{'='*60}")
        
        areas = self.dock_manager.openedDockAreas()
        for i, area in enumerate(areas):
            title_bar = area.titleBar()
            if title_bar:
                button = title_bar.findChild(QWidget, "tabsMenuButton")
                if button:
                    is_visible = button.isVisible()
                    tab_count = area.dockWidgetsCount() if hasattr(area, 'dockWidgetsCount') else 0
                    
                    print(f"  Area {i}:")
                    print(f"    Tab Count: {tab_count}")
                    print(f"    tabsMenuButton Visible: {is_visible}")
                    print(f"    Expected: False (1 tab)")
                    
                    if is_visible and tab_count == 1:
                        print(f"    ❌ FAIL: Button is visible but should be hidden!")
                    elif not is_visible and tab_count == 1:
                        print(f"    ✅ PASS: Button is correctly hidden!")
                    else:
                        print(f"    ⚠️  UNEXPECTED STATE")
        
        print(f"\n{'='*60}")
        print(f"🎬 TEST COMPLETE - App will close in 2 seconds")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())
