# Corner Splitter Handles - Multi-Axis Simultaneous Movement

## Wichtig: Manuelle Benutzereinstellung

**Corner Handles sind NICHT automatisch aktiviert!** Sie sind eine optionale Funktion, die der Benutzer **manuell über das Menü** aktiviert:

```
Menü: Splitter → Corner Handles ☑️
```

Nur wenn diese Option aktiviert ist, erscheinen die Corner Griffe an den Splitter-Schnittpunkten.

## Überblick

Corner Splitter Handles sind unsichtbare Widget-Bereiche, die an den Schnittpunkten von horizontalen und vertikalen Splittern platziert werden. Sie ermöglichen es Benutzern, **beide Splitter gleichzeitig** zu bewegen.

## Aktivierung

### Im Menü
```
Menu Bar → Splitter → Corner Handles [togglebar]
```

Die Option zeigt:
- ☐ Deaktiviert (keine Corner Handles sichtbar)
- ☑️ Aktiviert (Corner Handles an Schnittpunkten sichtbar)

### Status-Log
Bei Aktivierung/Deaktivierung wird eine Nachricht im Log angezeigt:
- **Aktiviert**: "✓ Corner Handles enabled - click & drag corners to move 2 splitters simultaneously"
- **Deaktiviert**: "✗ Corner Handles disabled"

## Funktionsweise

### Automatische Erkennung (nach Aktivierung)
```python
# Nach dem Klick auf "Corner Handles" im Menü:
factory.install_corner_handles(parent_widget)
```

Die Factory durchsucht alle Splitter und:
1. Kategorisiert sie in **horizontal** und **vertikal** Splitter
2. Findet alle Schnittpunkte durch Geometrie-Überprüfung
3. Platziert CornerSplitterHandle Widgets an diesen Positionen

### Interaktion

| Zustand | Cursor | Verhalten |
|---------|--------|-----------|
| **Normal** | OpenHand (✋) | Wartet auf Klick |
| **Hover** | SizeAll (✦) | Bereit zum Draggen |
| **Dragging** | SizeAll mit Cursor wechsel | Beide Splitter bewegen sich gleichzeitig |

### Bewegungslogik

```
User zieht Corner-Handle:
├─ X-Bewegung → Horizontal Splitter wird verschoben
├─ Y-Bewegung → Vertikal Splitter wird verschoben
└─ XY-Bewegung → Beide Splitter bewegen sich synchron
```

## Implementierung

### CornerSplitterHandle (Widget)

```python
class CornerSplitterHandle(QWidget):
    """Invisible handle at splitter intersections for multi-axis movement."""
    
    def set_splitters(h_splitter, h_idx, v_splitter, v_idx):
        """Register horizontal and vertical splitters."""
    
    def _move_splitter_handle(splitter, handle_index, delta):
        """Adjust panel sizes based on mouse movement."""
        # Minimumgröße: 18px
        # DeltaAusgleich bei Overflow
```

### Visual Feedback

```python
def paintEvent(self):
    # Normal: Semi-transparent blue rectangle (alpha=25)
    # Dragging: Blaues Quadrat mit Crosshair-Linien
```

### Size Enforcement

```
Wenn Benutzer zu weit zieht:
├─ Panel A: min. 18px 
├─ Panel B: min. 18px
└─ Überschüssige Pixel werden auf Nachbar verteilt
```

## Integration in Main App

```python
# 1: Factories initialisieren (normal)
self.splitter_factory = SplitterFactory()
self.splitter_event_handler = SplitterEventHandler(self)

# 2: Flag für Manual Control
self._corner_handles_enabled: bool = False

# 3: Splitter-Menü hinzufügen
self._create_splitter_menu()

# 4: Toggle-Methode implementieren
def _toggle_corner_handles(self) -> None:
    self._corner_handles_enabled = not self._corner_handles_enabled
    if self._corner_handles_enabled:
        self.splitter_factory.install_corner_handles(self.dock_manager)
    else:
        self.splitter_factory.clear_corner_handles()
```

## Konfiguration

```python
# SplitterStyle - Corner Handle Appearance
@dataclass
class SplitterStyle:
    corner_handle_size: int = 12              # Größe in Pixeln
    corner_handle_bg_rgba: str = "rgba(...)"  # Hintergrundfarbe
    corner_handle_hover_rgba: str = "rgba(...)" # Hover-Farbe
```

## Vorteile

✅ **Effizientes Layout-Management**: 1 Griff für 2 Splitter  
✅ **Intuitiv**: Pfeilkreuz-Cursor zeigt Funktion  
✅ **Raumsparend**: Nutzt nur bestehende Schnittpunkte  
✅ **Glatt**: Pixel-genaue Synchronisierung  
✅ **Robust**: Minimum-Size-Enforcement verhindert Overflow  
✅ **Optional**: Benutzer aktiviert nur wenn gewünscht

## Visuelle Konvention

```
Layout mit 2x2 Panels mit aktivierten Corner Handles:

┌────────────────────┐
│  Panel A  │ Panel B│  ← Vertikal Split
├──────────■────────┤  ← Orange/Blauer 12×12 Corner Handle
│ Panel C  │ Panel D│  
└────────────────────┘
     ↑
Horizontal Split
```

Der orange/blaue 12×12 Punkt ist der Corner Handle (nur sichtbar wenn aktiviert).

## Lifecycle

```
Programmstart:
└─ Corner Handles DEAKTIVIERT (kein sichtbarer Handle)
   
Benutzer: Splitter → Corner Handles anklicken:
└─ Corner Handles werden AKTIVIERT
   └─ Factory sucht Schnittpunkte
   └─ Widgets are created & positioned
   └─ Benutzer kann jetzt draggen

Benutzer: Splitter → Corner Handles anklicken (wieder):
└─ Corner Handles werden DEAKTIVIERT
   └─ Alle Handles versteckt & gelöscht
```

---

**Version**: 2.0 (Manual Control)  
**Factory**: `SplitterFactory` in `src/widgetsystem/factories/splitter_factory.py`  
**Widget**: `CornerSplitterHandle`  
**Method**: `SplitterFactory.install_corner_handles()` & `SplitterFactory.clear_corner_handles()`

