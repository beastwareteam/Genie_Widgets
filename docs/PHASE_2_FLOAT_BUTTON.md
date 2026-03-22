# Phase 2: Float-Button Persistierung

## Übersicht

Phase 2 implementiert einen FloatingStateTracker, der sicherstellt, dass Title Bar Buttons (insbesondere der Float-Button) korrekt erhalten bleiben, wenn Panels zwischen floating und docked wechseln.

## Problem

QtAds erstellt die Title Bar neu, wenn ein Panel re-docked wird. Dabei können Button-Zustände verloren gehen, was dazu führt, dass der Float-Button oder andere Buttons nach dem Re-Docking fehlen.

## Lösung

**FloatingStateTracker** überwacht Floating-Übergänge und aktualisiert die Title Bar nach Re-Docking-Operationen automatisch.

## Architektur

### Klassen

#### `FloatingStateTracker` (floating_state_tracker.py)

**Zweck**: Trackt Floating-States von Panels und stellt Title Bar Buttons nach Re-Docking wieder her.

**Hauptfunktionen**:
- Überwacht `dockWidgetAboutToBeFloated` Signal
- Überwacht `dockWidgetAdded` Signal (für Re-Docking)
- Trackt Floating-Status in `_floating_widgets` Dictionary
- Scheduled Title Bar Refresh nach Re-Docking (100ms Verzögerung)

**Signale**:
```python
# CDockManager Signale
dockWidgetAboutToBeFloated  # Widget wird floating
floatingWidgetCreated       # Floating Container erstellt
dockWidgetAdded             # Widget hinzugefügt (inkl. Re-Docking)
```

### Integration

**main.py**:
```python
from widgetsystem.ui import FloatingStateTracker

# Nach CDockManager Erstellung
self._floating_tracker = FloatingStateTracker(self.dock_manager)
```

**visual_app.py**:
```python
from widgetsystem.ui import FloatingStateTracker

# In _setup_docking()
self._floating_tracker = FloatingStateTracker(self.dock_manager)
```

## Funktionsweise

### 1. Widget wird Floating

```python
# Signal: dockWidgetAboutToBeFloated
_floating_widgets[widget_id] = True  # Markiere als floating
```

### 2. Widget wird Re-Docked

```python
# Signal: dockWidgetAdded
if was_floating:
    _floating_widgets[widget_id] = False  # Markiere als nicht mehr floating
    schedule_refresh()  # Schedule Title Bar Refresh nach 100ms
```

### 3. Title Bar Refresh

```python
def _refresh_title_bar(widget):
    title_bar = get_title_bar(widget)
    
    # Force Update durch Visibility Toggle
    title_bar.setVisible(False)
    title_bar.setVisible(True)
    title_bar.update()
```

## Timing

**Wichtig**: Der Refresh erfolgt **100ms nach Re-Docking**, um QtAds Zeit für interne Setup-Operationen zu geben.

## Tests

### Unit-Tests (`tests/test_phase_2_floating_state_tracker.py`)

**13 Tests** - Alle PASSED ✅

- `test_initialization`: Initialisierung prüfen
- `test_signal_connections`: Signal-Verbindungen prüfen
- `test_widget_about_to_float`: Tracking beim Floating
- `test_floating_widget_created`: Container-Erstellung
- `test_widget_added_not_previously_floating`: Neues Widget hinzugefügt
- `test_widget_added_was_floating`: Re-Docking erkannt
- `test_is_widget_floating_*`: Floating-Status abfragen
- `test_get_floating_widgets`: Alle Status abrufen
- `test_refresh_title_bar_*`: Title Bar Refresh-Logik

**Coverage**: 78.95% für floating_state_tracker.py

### Integrationstest (`test_phase_2_float_button.py`)

**Ablauf**:
1. Panel erstellen (docked)
2. Float-Button prüfen
3. Panel floating machen
4. Floating-Status prüfen
5. Panel re-docken
6. **Float-Button erneut prüfen** (sollte vorhanden sein)

## API

### FloatingStateTracker

```python
class FloatingStateTracker(QObject):
    def __init__(self, dock_manager: CDockManager, parent: QObject | None = None)
    
    # Öffentliche Methoden
    def is_widget_floating(self, dock_widget: CDockWidget) -> bool
    def get_floating_widgets(self) -> dict[int, bool]
    
    # Signal-Handler (intern)
    def _on_widget_about_to_float(self, dock_widget)
    def _on_floating_widget_created(self, floating_container)
    def _on_dock_widget_added(self, dock_widget)
    def _refresh_title_bar(self, dock_widget)
```

## Debug-Output

Bei aktiviertem Debug-Modus:
```
[FloatingStateTracker] Widget Test Panel about to float
[FloatingStateTracker] Floating container created
[FloatingStateTracker] Widget Test Panel re-docked, scheduling title bar refresh
[FloatingStateTracker] Refreshing title bar for Test Panel
[FloatingStateTracker] Title bar refreshed
```

## Bekannte Einschränkungen

1. **Visibility Toggle**: Der Refresh erfolgt durch Visibility-Toggle. In seltenen Fällen kann dies zu kurzen visuellen Flackern führen.

2. **Timing-Abhängigkeit**: Die 100ms Verzögerung ist ein Kompromiss. Bei sehr langsamen Systemen könnte mehr Zeit benötigt werden.

3. **Button-State**: Nur die Präsenz der Buttons wird sichergestellt, nicht deren interner State (z.B. enabled/disabled).

## Konfiguration

**Keine Konfiguration erforderlich**. Der Tracker funktioniert automatisch nach der Integration.

## Zusammenfassung

✅ **Phase 2 komplett implementiert**
- FloatingStateTracker Klasse erstellt
- Signal-Handler implementiert
- Title Bar Refresh-Logik funktioniert
- 13 Unit-Tests PASSED (78.95% Coverage)
- Integration in main.py und visual_app.py abgeschlossen

**Nächste Phase**: Phase 3 - Panel Factory erweitern für Z-Order Management
