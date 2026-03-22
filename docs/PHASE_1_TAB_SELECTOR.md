"""Phase 1 - Tab Selector Visibility

## Übersicht

Phase 1 implementiert das intelligente Ein-/Ausblenden des Tab-Selectors (Reiter-Wechslers)
in Dock-Bereichen basierend auf der Anzahl der geöffneten Panels im Bereich.

## Problem

Wenn nur ein Panel in einem Dock-Bereich offen ist, wird der Tab-Selector (das Dropdown
mit Pfeil) angezeigt, obwohl er nicht notwendig ist. Der Nutzer kann damit nicht
interagieren, da es nur eine Option gibt.

## Lösung

Der Tab-Selector wird nur angezeigt, wenn **2 oder mehr Panels** im selben Dock-Bereich
als Tabs übereinander liegen. In diesem Fall kann der Nutzer mit dem Dropdown zwischen
den Tabs wechseln.

**Logik:**
- 1 Tab offen → Selector **ausgeblendet** (setVisible(False))
- 2+ Tabs offen → Selector **sichtbar** (setVisible(True))
- Tab geschlossen → Zurück zu 1 Tab → Selector **ausgeblendet**

---

## Architektur (Phase 1)

### Komponenten

#### 1. **TabSelectorMonitor** (`tab_selector_monitor.py`)

**Zweck:** Überwacht die Tab-Anzahl in allen Dock-Bereichen

**Verantwortlichkeiten:**
- Registriert Dock-Bereiche
- Verfolgt Tab-Anzahl pro Bereich
- Signalisiert Änderungen
- Bestimmt ob Selector angezeigt werden soll

**Wichtige Methoden:**
```python
def register_dock_area(area_id: str, area_widget: Any) -> None:
    """Bereich für Überwachung registrieren"""

def update_tab_count(area_id: str, new_count: int) -> None:
    """Tab-Anzahl aktualisieren + Signal emittieren"""

def should_show_selector(area_id: str) -> bool:
    """Gibt True zurück wenn > 1 Tab, sonst False"""

def get_tab_count(area_id: str) -> int:
    """Aktuelle Tab-Anzahl abfragen"""
```

**Signal:**
- `tab_count_changed(area_id: str, count: int)` - Emittiert wenn Tab-Anzahl sich ändert


#### 2. **TabSelectorEventHandler** (`tab_selector_event_handler.py`)

**Zweck:** Verbindet CDockManager Signale mit TabSelectorMonitor

**Verantwortlichkeiten:**
- Horcht auf QtAds Events (Panel hinzugefügt/entfernt)
- Aktualisiert Tab-Zähler im Monitor
- Verwaltet Area-Identifikation

**Wichtige Methoden:**
```python
def _on_dock_area_created(area_widget: Any) -> None:
    """Neue Dock-Area erkannt → im Monitor registrieren"""

def _on_dock_widget_added(dock_widget: Any) -> None:
    """Widget hinzugefügt → Tab-Count erhöhen"""

def _on_dock_widget_removed(dock_widget: Any) -> None:
    """Widget entfernt → Tab-Count senken"""
```

**Connected Signals:**
- `dock_manager.dockAreaCreated` → `_on_dock_area_created()`
- `dock_manager.dockWidgetAdded` → `_on_dock_widget_added()`
- `dock_manager.dockWidgetRemoved` → `_on_dock_widget_removed()`


#### 3. **TabSelectorVisibilityController** (`tab_selector_visibility_controller.py`)

**Zweck:** Steuert die Sichtbarkeit des Tab-Selectors in der Title Bar

**Verantwortlichkeiten:**
- Horcht auf Monitor Signale
- Findet Tab-Selector Element in Title Bar
- Setzt Sichtbarkeit basierend auf Tab-Count

**Wichtige Methoden:**
```python
def _on_tab_count_changed(area_id: str, count: int) -> None:
    """Signal empfangen → Selector sichtbar/unsichtbar machen"""

def _get_title_bar(area_widget: Any) -> Any:
    """Findet CDockAreaTitleBar"""

def _find_tab_selector(title_bar: Any) -> Any:
    """Findet QComboBox/Selector in Title Bar"""

def _set_selector_visibility(selector: Any, visible: bool) -> None:
    """Setzt setVisible(True/False) des Selectors"""
```

**Connected Signals:**
- `tab_monitor.tab_count_changed` → `_on_tab_count_changed()`

---

## Integration in bestehenden Code

### In `main.py` & `visual_app.py` - Methode `_setup_docking()`

Nach dieser Codezeile:
```python
self.dock_manager: Any = QtAds.CDockManager(self)
```

Müssen folgende Zeilen hinzugefügt werden:
```python
# Phase 1: Tab Selector Visibility
from widgetsystem.ui import (
    TabSelectorMonitor,
    TabSelectorEventHandler,
    TabSelectorVisibilityController,
)

self._tab_monitor = TabSelectorMonitor()
self._tab_event_handler = TabSelectorEventHandler(self.dock_manager, self._tab_monitor)
self._tab_visibility = TabSelectorVisibilityController(self._tab_monitor)
```

---

## Datenfluss

```
QtAds CDockManager
    ↓ (Signal: Widget added/removed)
TabSelectorEventHandler
    ↓ (update_tab_count())
TabSelectorMonitor
    ↓ (Signal: tab_count_changed)
TabSelectorVisibilityController
    ↓ (setVisible True/False)
CDockAreaTitleBar → Tab Selector Button
```

---

## Testing

### Unit Tests

Siehe `tests/test_phase_1_tab_selector.py`

**Testabdeckung:**
- ✅ TabSelectorMonitor Registrierung/Deregistrierung
- ✅ Tab-Count Updates
- ✅ should_show_selector() Logik
- ✅ Event Handler Signal Verbindungen
- ✅ Visibility Controller Signal Handling

**Ausführung:**
```bash
pytest tests/test_phase_1_tab_selector.py -v
```

### UI Tests (Manuell)

1. **Single Tab Test:**
   - App starten
   - 1 Panel offen (z.B. left_panel)
   - ✅ Tab-Selector sollte **NICHT sichtbar** sein (Pfeil ausgeblendet)

2. **Multiple Tabs Test:**
   - 1 Panel floaten und neu andocken im selben Bereich
   - ✅ Tab-Selector sollte **SICHTBAR** sein (Pfeil sichtbar)
   - ✅ Dropdown zeigt beide Panel-Namen
   - ✅ Mit Dropdown können zwischen Panels gewechselt werden

3. **Tab Close Test:**
   - Eines der Panels mit X schließen
   - ✅ Tab-Selector sollte wieder **AUSGEBLENDET** sein

4. **Multiple Areas Test:**
   - Mehrere Panels in verschiedenen Bereichen floaten
   - ✅ Jeder Bereich sollte unabhängig seinen Selector zeigen/verstecken

---

## Debugging-Tipps

### Selector wird nicht angezeigt wenn mehrere Tabs da sind

1. Prüfe ob Monitor die Tab-Count richtig zählt:
   ```python
   print(self._tab_monitor.get_all_area_counts())
   ```

2. Prüfe ob Visibility Controller den Selector findet:
   ```python
   # Im _find_tab_selector() eine Exception werfen wenn nicht gefunden
   ```

3. Prüfe QtAds Signale werden richtig emittiert:
   ```python
   dock_manager.dockWidgetAdded.connect(lambda w: print(f"Widget added: {w}"))
   ```

### Selector wird fälschlicherweise angezeigt

1. Prüfe should_show_selector() Rückgabewert:
   ```python
   print(monitor.should_show_selector("area_id"))  # Sollte False sein bei 1 Tab
   ```

2. Prüfe dass setVisible() wirklich aufgerufen wird

---

## Bekannte Einschränkungen

1. **Area ID Bestimmung:** Bereiche werden via objectName() identifiziert. Falls QtAds keine Namen setzt, wird ein Auto-ID generiert.

2. **Kompatibilität:** Funktionanweit nur wenn QtAds die erwarteten Signale emittiert. Wurde getestet mit QtAds 4.0+

3. **Performance:** Pro Tab-Change wird ein Signal emittiert. Bei vielen gleichzeitigen Änderungen könnte es zu Verzögerungen kommen (selten).

---

## Nächste Phase

Nachdem Phase 1 getestet ist, können wir zu **Phase 2: Float-Button Persistierung** übergehen.
