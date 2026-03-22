# Inlay TitleBar - Collapsible Window Control

## Übersicht

Die **Inlay TitleBar** ist eine moderne UI-Komponente, die eine schlanke Drag & Drop-Leiste am oberen Fensterrand bereitstellt, die sich bei Mouse-over zu einer vollständigen Titelleiste mit Fenster-Steuerungen ausfaltet.

## Features

### ✨ Kernfunktionen

- **3px Slim Handle** - Minimale Höhe im eingeklappten Zustand
- **35px Expanded Height** - Vollständige Titelleiste beim Hovern
- **Smooth Animations** - Flüssige Ein-/Ausklapp-Animationen (200ms)
- **Window Controls** - Minimieren, Maximieren, Schließen
- **Drag-to-Move** - Fenster verschieben durch Ziehen der Titelleiste
- **Auto-Collapse** - Automatisches Einklappen nach Mouse-out (300ms Delay)
- **Full Width** - Erstreckt sich über die gesamte Fensterbreite

### 🎨 Visuelle Eigenschaften

**Collapsed State (Standard):**
```
┌─────────────────────────────────────────┐  ← 3px hoch
│         [Schmales Handle]                │  ← Gesamte Breite
└─────────────────────────────────────────┘
```

**Expanded State (Mouse Hover):**
```
┌─────────────────────────────────────────┐
│ WidgetSystem        [─] [□] [×]        │  ← 35px hoch
└─────────────────────────────────────────┘
```

### ⏱️ Timing-Konfiguration

| Eigenschaft | Wert | Beschreibung |
|------------|------|--------------|
| `COLLAPSED_HEIGHT` | 3px | Höhe im eingeklappten Zustand |
| `EXPANDED_HEIGHT` | 35px | Höhe im ausgeklappten Zustand |
| `ANIMATION_DURATION` | 200ms | Dauer der Ein-/Ausklapp-Animation |
| `HOVER_DELAY` | 100ms | Verzögerung vor dem Ausklappen |
| `COLLAPSE_DELAY` | 300ms | Verzögerung vor dem Einklappen |

## Integration

### Schnellstart

```python
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt
from widgetsystem.ui import InlayTitleBarController

# Hauptfenster mit Frameless Window Flag
window = QMainWindow()
window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

# Inlay TitleBar Controller erstellen und installieren
controller = InlayTitleBarController(window)
controller.install()
controller.set_title("Meine Anwendung")

window.show()
```

### In main.py Integration

```python
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        # Frameless Window für transparentes Fenster
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        
        # ... weitere Initialisierung ...
        
        # Inlay TitleBar installieren
        self._create_inlay_title_bar()
    
    def _create_inlay_title_bar(self) -> None:
        """Erstelle moderne Inlay-Titelleiste."""
        from widgetsystem.ui import InlayTitleBarController
        
        self._inlay_controller = InlayTitleBarController(self)
        self._inlay_controller.install()
        self._inlay_controller.set_title("WidgetSystem - Advanced Docking")
```

## API-Referenz

### InlayTitleBar

Die Hauptkomponente - ein QWidget mit Ein-/Ausklapp-Funktionalität.

#### Konstruktor

```python
InlayTitleBar(parent_window: QWidget)
```

**Parameter:**
- `parent_window`: Das Hauptfenster, das gesteuert werden soll

#### Methoden

##### `set_title(title: str) -> None`
Setzt den Fenstertitel.

```python
titlebar.set_title("Meine Anwendung v2.0")
```

##### `_expand() -> None` (Internal)
Expandiert die Titelleiste zu voller Höhe. Wird automatisch bei Mouse-over aufgerufen.

##### `_collapse() -> None` (Internal)
Kollabiert die Titelleiste auf minimale Höhe. Wird automatisch bei Mouse-out aufgerufen.

#### Events

Die Komponente reagiert auf folgende Events:

- **`enterEvent`** - Mouse-over → Startet Expand-Timer
- **`leaveEvent`** - Mouse-out → Startet Collapse-Timer
- **`mousePressEvent`** - Linksklick → Startet Drag
- **`mouseMoveEvent`** - Mausbewegung während Drag → Bewegt Fenster
- **`mouseReleaseEvent`** - Loslassen → Beendet Drag
- **`mouseDoubleClickEvent`** - Doppelklick → Toggle Maximize
- **`resizeEvent`** - Fenster-Resize → Aktualisiert Breite

### InlayTitleBarController

Controller zur Verwaltung der Inlay TitleBar.

#### Konstruktor

```python
InlayTitleBarController(main_window: QWidget)
```

**Parameter:**
- `main_window`: Das Hauptfenster, dem die Titelleiste hinzugefügt werden soll

#### Methoden

##### `install() -> None`
Installiert die Inlay TitleBar im Hauptfenster.

```python
controller.install()
```

##### `uninstall() -> None`
Entfernt die Inlay TitleBar aus dem Hauptfenster.

```python
controller.uninstall()
```

##### `set_title(title: str) -> None`
Aktualisiert den Fenstertitel.

```python
controller.set_title("Neue Anwendung")
```

## Styling

### Standard-Stylesheet

Die Komponente verwendet ein eingebautes Stylesheet mit Gradient-Hintergrund:

```python
InlayTitleBar {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(60, 60, 60, 200),
        stop:1 rgba(40, 40, 40, 230)
    );
    border: none;
    border-bottom: 1px solid rgba(80, 80, 80, 180);
}
```

### Anpassung

Um das Styling anzupassen, überschreiben Sie die `_apply_stylesheet()` Methode:

```python
class CustomInlayTitleBar(InlayTitleBar):
    def _apply_stylesheet(self) -> None:
        self.setStyleSheet("""
            InlayTitleBar {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 100, 150, 200),
                    stop:1 rgba(30, 70, 120, 230)
                );
            }
            /* ... weitere Styles ... */
        """)
```

## Beispiele

### Beispiel 1: Basis-Integration

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
from widgetsystem.ui import InlayTitleBarController

app = QApplication([])

window = QMainWindow()
window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
window.setGeometry(100, 100, 800, 600)

controller = InlayTitleBarController(window)
controller.install()
controller.set_title("Meine App")

window.show()
app.exec()
```

### Beispiel 2: Mit Theme-Integration

```python
from widgetsystem.core import ThemeManager
from widgetsystem.ui import InlayTitleBarController

class ThemedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        
        # Inlay TitleBar
        self.titlebar_controller = InlayTitleBarController(self)
        self.titlebar_controller.install()
        
        # Theme Manager
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.themeChanged.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, theme_name: str):
        """Reaktion auf Theme-Änderung."""
        # Titlebar-Farben aktualisieren
        if self.titlebar_controller.titlebar:
            # Stylesheet anpassen
            pass
```

### Beispiel 3: Dynamische Titel-Updates

```python
from PySide6.QtCore import QTimer

class DynamicTitleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.titlebar_controller = InlayTitleBarController(self)
        self.titlebar_controller.install()
        
        # Timer für dynamische Titel
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_title)
        self.timer.start(1000)  # Jede Sekunde
        
        self.counter = 0
    
    def _update_title(self):
        """Aktualisiere Titel jede Sekunde."""
        self.counter += 1
        self.titlebar_controller.set_title(f"App - {self.counter} Sekunden")
```

## Technische Details

### Architektur

```
InlayTitleBarController
    │
    ├── install()           → Erstellt InlayTitleBar
    ├── uninstall()         → Entfernt InlayTitleBar
    └── set_title()         → Delegiert an InlayTitleBar
            │
            InlayTitleBar (QWidget)
                │
                ├── _controls_widget (QWidget)
                │   ├── _title_label (QLabel)
                │   ├── _minimize_btn (QPushButton)
                │   ├── _maximize_btn (QPushButton)
                │   └── _close_btn (QPushButton)
                │
                ├── _height_animation (QPropertyAnimation)
                ├── _opacity_animation (QPropertyAnimation)
                ├── _hover_timer (QTimer)
                └── _collapse_timer (QTimer)
```

### Animation-System

Die Komponente verwendet zwei synchronisierte Animationen:

1. **Height Animation** - Animiert die Höhe von 3px → 35px
2. **Opacity Animation** - Blendet Controls ein/aus (0.0 → 1.0)

Beide verwenden `QEasingCurve.Type.InOutCubic` für smooth Bewegung.

### Event-Flow

```
Mouse Enter
    ↓
Stop Collapse Timer
    ↓
Start Hover Timer (100ms)
    ↓
Expand Animation (200ms)
    ↓
Show Controls (Fade In)
    ↓
[EXPANDED STATE]
    ↓
Mouse Leave
    ↓
Stop Hover Timer
    ↓
Start Collapse Timer (300ms)
    ↓
Fade Out Controls
    ↓
Collapse Animation (200ms)
    ↓
Hide Controls
    ↓
[COLLAPSED STATE]
```

## Performance

### Memory Footprint
- **InlayTitleBar**: ~5KB pro Instanz
- **Animations**: ~2KB pro Animation
- **Gesamt**: ~10KB pro Fenster

### CPU Usage
- **Idle**: 0% (keine aktiven Timer)
- **Animation**: <1% (200ms burst)
- **Hover Detection**: Minimal (event-driven)

## Kompatibilität

### Getestet mit
- ✅ PySide6 >= 6.5.0
- ✅ Python 3.10+
- ✅ Windows 10/11
- ✅ Qt Advanced Docking System

### Bekannte Einschränkungen
- Frameless Window erforderlich
- Keine native Window-Shadows (kann mit QGraphicsDropShadowEffect ergänzt werden)

## Troubleshooting

### Problem: TitleBar erscheint nicht
**Lösung:** Stellen Sie sicher, dass `Qt.WindowType.FramelessWindowHint` gesetzt ist.

```python
window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
```

### Problem: Animation ruckelt
**Lösung:** Reduzieren Sie `ANIMATION_DURATION` oder ändern Sie EasingCurve.

```python
InlayTitleBar.ANIMATION_DURATION = 150  # Schneller
```

### Problem: TitleBar falscher Breite
**Lösung:** Rufen Sie `_update_geometry()` nach Window-Resize auf.

```python
def resizeEvent(self, event):
    super().resizeEvent(event)
    if hasattr(self, '_inlay_controller') and self._inlay_controller.titlebar:
        self._inlay_controller.titlebar._update_geometry()
```

## Zukünftige Erweiterungen

### Geplante Features
- [ ] Konfigurierbare Höhen über Settings
- [ ] Theme-Integration (automatische Farbanpassung)
- [ ] Zusätzliche Buttons (z.B. Settings, Help)
- [ ] Custom Icons für Buttons
- [ ] Animierte Icon-Transitions
- [ ] Touch-optimierte Variante (größere Touch-Targets)
- [ ] Accessibility-Features (Screen-Reader-Support)

## Siehe auch

- [FloatingTitleBar](floating_titlebar.md) - Original floating window titlebar
- [Theme System](THEME_SYSTEM_GUIDE.md) - Theme-Integration
- [Window Management](WINDOW_MANAGEMENT.md) - Fenster-Steuerung

## Lizenz

MIT License - Teil des WidgetSystem Projekts
