"""Extended Debug - Findet den Tab Selector Button.

Dieses Script sucht systematisch nach dem "Pfeil nach unten" Button.
"""

import sys
from pathlib import Path

import PySide6QtAds as QtAds
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QToolButton, QComboBox


def find_all_buttons(widget, indent=0) -> None:
    """Rekursiv alle Buttons finden."""
    prefix = "  " * indent
    
    widget_type = type(widget).__name__
    object_name = widget.objectName() if hasattr(widget, 'objectName') else ''
    
    # Interessante Widget-Typen
    if any(x in widget_type for x in ['Button', 'Combo', 'Menu', 'Tool']):
        print(f"{prefix}🔘 {widget_type}")
        print(f"{prefix}   Name: '{object_name}'")
        print(f"{prefix}   Visible: {widget.isVisible()}")
        print(f"{prefix}   Size: {widget.width()}x{widget.height()}")
        print(f"{prefix}   Pos: ({widget.x()}, {widget.y()})")
        
        # Text oder Icon
        if hasattr(widget, 'text'):
            try:
                text = widget.text()
                if text:
                    print(f"{prefix}   Text: '{text}'")
            except:
                pass
        
        if hasattr(widget, 'toolTip'):
            try:
                tooltip = widget.toolTip()
                if tooltip:
                    print(f"{prefix}   ToolTip: '{tooltip}'")
            except:
                pass
        
        if hasattr(widget, 'icon'):
            try:
                icon = widget.icon()
                if not icon.isNull():
                    print(f"{prefix}   Has Icon: Yes")
            except:
                pass
        
        print()
    
    # Rekursiv durch Kinder
    if hasattr(widget, 'children'):
        for child in widget.children():
            if isinstance(child, QWidget):
                find_all_buttons(child, indent + 1)


def search_for_dropdown_arrow(dock_manager) -> None:
    """Sucht nach dem Dropdown-Pfeil Button."""
    print(f"\n{'='*80}")
    print(f"🔎 SEARCHING FOR DROPDOWN ARROW BUTTON")
    print(f"{'='*80}\n")
    
    # Alle dock areas durchsuchen
    if hasattr(dock_manager, 'openedDockAreas'):
        areas = dock_manager.openedDockAreas()
        print(f"✅ Searching through {len(areas)} dock areas...\n")
        
        for i, area in enumerate(areas):
            area_name = f"Area_{i}"
            if hasattr(area, 'objectName') and area.objectName():
                area_name = area.objectName()
            
            print(f"\n{'─'*60}")
            print(f"📍 {area_name}")
            print(f"{'─'*60}")
            
            # Durchsuche Area
            find_all_buttons(area, indent=1)
            
            # Durchsuche Title Bar
            if hasattr(area, 'titleBar'):
                title_bar = area.titleBar()
                if title_bar:
                    print(f"\n  📋 Title Bar Buttons:")
                    find_all_buttons(title_bar, indent=2)
    
    # Durchsuche auch floating containers
    print(f"\n{'='*80}")
    print(f"🎈 FLOATING CONTAINERS")
    print(f"{'='*80}\n")
    
    if hasattr(dock_manager, 'floatingWidgets'):
        try:
            floating = dock_manager.floatingWidgets()
            print(f"✅ Found {len(floating)} floating widgets\n")
            for i, fw in enumerate(floating):
                print(f"\n  📦 Floating Widget {i}:")
                find_all_buttons(fw, indent=2)
        except Exception as e:
            print(f"❌ Error getting floating widgets: {e}")


class ExtendedDebugWindow(QMainWindow):
    """Extended Debug Window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extended Debug - Find Tab Selector")
        self.setMinimumSize(1000, 600)
        
        # QtAds Setup - ALLE möglichen Flags
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DockAreaHasTabsMenuButton, True  # <-- WICHTIG!
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DockAreaHideDisabledButtons, False
        )
        
        self.dock_manager = QtAds.CDockManager(self)
        
        # Erstelle 2 Panels im SELBEN Bereich (für Tabs)
        dock1 = QtAds.CDockWidget(self.dock_manager, "Panel 1", self)
        dock1.setWidget(QWidget())
        self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock1)
        
        dock2 = QtAds.CDockWidget(self.dock_manager, "Panel 2", self)
        dock2.setWidget(QWidget())
        # Füge als TAB hinzu, nicht als Split
        area = dock1.dockAreaWidget()
        if area:
            self.dock_manager.addDockWidgetTab(QtAds.CenterDockWidgetArea, dock2)
        else:
            self.dock_manager.addDockWidget(QtAds.LeftDockWidgetArea, dock2)
        
        # Debug nach Verzögerung
        QTimer.singleShot(1000, self.run_debug)
    
    def run_debug(self):
        """Führt erweiterte Debug-Analyse aus."""
        search_for_dropdown_arrow(self.dock_manager)
        
        print(f"\n\n{'='*80}")
        print(f"✅ EXTENDED DEBUG COMPLETE")
        print(f"{'='*80}\n")
        
        # Zeige noch QtAds Flags
        print(f"\n{'='*80}")
        print(f"⚙️  QTADS CONFIG FLAGS")
        print(f"{'='*80}\n")
        
        flags = [
            'DockAreaHasTabsMenuButton',
            'DockAreaHideDisabledButtons',
            'AllTabsHaveCloseButton',
            'DockAreaCloseButtonClosesTab',
        ]
        
        for flag_name in flags:
            if hasattr(QtAds.CDockManager.eConfigFlag, flag_name):
                flag = getattr(QtAds.CDockManager.eConfigFlag, flag_name)
                is_set = QtAds.CDockManager.configFlag(flag)
                print(f"  {flag_name}: {is_set}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExtendedDebugWindow()
    window.show()
    
    # Länger offen lassen für manuelle Inspektion
    QTimer.singleShot(10000, app.quit)
    
    sys.exit(app.exec())
