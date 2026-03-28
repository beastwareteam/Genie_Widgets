# Corner Splitter Handles - Integration mit manuellem Control

## Wichtig: Manuelle Benutzereinstellung!

Corner Handles sind **NICHT automatisch aktiviert**. Sie müssen vom Benutzer über das Menü aktiviert werden:

```
Menü → Splitter → Corner Handles [☑️ Option]
```

---

## Schnelle Integration

### Schritt 1: SplitterFactory & Handler initialisieren

```python
from widgetsystem.factories.splitter_factory import SplitterFactory, SplitterEventHandler
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction

# In MainWindow.__init__():
self.splitter_factory = SplitterFactory()
self.splitter_event_handler = SplitterEventHandler(self)
self.splitter_factory.configure_handler(self.splitter_event_handler)
self.splitter_event_handler.set_factory(self.splitter_factory)
self.splitter_event_handler.set_restore_callback(self._on_splitter_restored)

# NEW: Manual control flag
self._corner_handles_enabled: bool = False
```

### Schritt 2: Splitter-Menü mit Checkbox erstellen

```python
def _create_splitter_menu(self) -> None:
    """Create Splitter menu with Corner Handles option."""
    menubar = self.menuBar()
    splitter_menu = menubar.addMenu("&Splitter")
    
    # Checkable action
    corner_handles_action = QAction("&Corner Handles", self)
    corner_handles_action.setCheckable(True)
    corner_handles_action.setChecked(self._corner_handles_enabled)
    
    # Connect to toggle method
    corner_handles_action.triggered.connect(self._toggle_corner_handles)
    splitter_menu.addAction(corner_handles_action)
```

### Schritt 3: Toggle-Methode implementieren

```python
def _toggle_corner_handles(self) -> None:
    """Toggle corner handles for multi-axis splitter movement."""
    self._corner_handles_enabled = not self._corner_handles_enabled
    
    if self._corner_handles_enabled:
        # AKTIVIEREN
        self.splitter_factory.install_corner_handles(self.dock_manager)
        self._log("✓ Corner Handles enabled - click & drag corners to move 2 splitters simultaneously")
    else:
        # DEAKTIVIEREN
        self.splitter_factory.clear_corner_handles()
        self._log("✗ Corner Handles disabled")
```

### Schritt 4: Splitter-Menü in Menu Bar integrieren

```python
def _create_menu_bar(self) -> None:
    """Setup application menu bar."""
    # ... other menus ...
    self._create_splitter_menu()  # NEW: Add splitter menu
    # ... other menus ...
```

### Schritt 3: Timer für periodische Aktualisierung (optional)

```python
# Für Splitter Refresh nach ADS Layout-Änderungen:
self._splitter_timer = QTimer(self)
self._splitter_timer.timeout.connect(self._set_modern_splitter_behavior)
self._splitter_timer.start(250)

def _set_modern_splitter_behavior(self) -> None:
    """Splitter refresh mit Corner Handles."""
    splitters = self.dock_manager.findChildren(QSplitter)
    for splitter in splitters:
        self.splitter_factory.apply_modern_behavior(splitter, handle_width=6)
        self.splitter_event_handler.track_splitter(splitter)
    self.splitter_factory.install_corner_handles(self.dock_manager)
```

## Beispiel-Code (vollständig)

```python
# In MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Factory Setup
        self.splitter_factory = SplitterFactory()
        self.splitter_event_handler = SplitterEventHandler(self)
        self.splitter_factory.configure_handler(self.splitter_event_handler)
        self.splitter_event_handler.set_factory(self.splitter_factory)
        self.splitter_event_handler.set_restore_callback(self._on_splitter_restored)
        
        # Splitter-Stylesheet anwenden
        stylesheet = _build_stylesheet_with_splitter_styling(self.splitter_factory)
        self.setStyleSheet(stylesheet)
        
        # CDockManager Setup
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True
        )
        self.dock_manager = QtAds.CDockManager(self)
        
        # Docks hinzufügen
        actions_dock = self._create_actions_dock()
        self.dock_manager.addDockWidget(QtAds.CenterDockWidgetArea, actions_dock)
        
        # Splitter Setup + Corner Handles
        self._apply_splitter_behavior()
        
        # Timer für Refresh
        self._splitter_timer = QTimer(self)
        self._splitter_timer.timeout.connect(self._apply_splitter_behavior)
        self._splitter_timer.start(250)
    
    def _apply_splitter_behavior(self) -> None:
        """Apply modern splitter behavior with corner handles."""
        if self.dock_manager is None:
            return
        
        splitters = self.dock_manager.findChildren(QSplitter)
        for splitter in splitters:
            self.splitter_factory.apply_modern_behavior(
                splitter,
                handle_width=6,
                min_remainder=18,
            )
            self.splitter_event_handler.track_splitter(splitter)
        
        # WICHTIG: Corner Handles installieren
        self.splitter_factory.install_corner_handles(self.dock_manager)
    
    def _on_splitter_restored(self, splitter: QSplitter, mode: str) -> None:
        """Callback after double-click restore."""
        print(f"Splitter restored: {mode}")
```

## Testing

```python
# Test: Corner Handles erstellen
def test_corner_handles():
    app = QApplication([])
    
    # Create container with 2 perpendicular splitters
    container = QWidget()
    layout = QVBoxLayout(container)
    
    h_splitter = QSplitter(Qt.Orientation.Horizontal)
    h_splitter.addWidget(QLabel("Left"))
    h_splitter.addWidget(QLabel("Right"))
    
    v_splitter = QSplitter(Qt.Orientation.Vertical)
    v_splitter.addWidget(h_splitter)
    v_splitter.addWidget(QLabel("Bottom"))
    
    layout.addWidget(v_splitter)
    
    # Install corner handles
    factory = SplitterFactory()
    factory.install_corner_handles(container)
    
    # Check: Container sollte CornerSplitterHandle enthalten
    corner_handles = container.findChildren(CornerSplitterHandle)
    assert len(corner_handles) > 0, "No corner handles created"
    print(f"✓ {len(corner_handles)} corner handle(s) created successfully")
```

## Styling (Optional)

Um Corner Handles visuell anzupassen:

```python
style = SplitterStyle(
    corner_handle_size=16,           # Größer
    corner_handle_bg_rgba="rgba(0, 200, 100, 0.3)",  # Grün statt Blau
    corner_handle_hover_rgba="rgba(0, 255, 100, 0.7)",
)
factory = SplitterFactory(style=style)
```

## Troubleshooting

### Corner Handles erscheinen nicht
- **Grund**: Keine perpendiculären Splitter oder Methode nicht aufgerufen
- **Lösung**: Überprüfen Sie, dass `install_corner_handles()` nach allen Docks aufgerufen wird

### Splitter-Bewegung flackert
- **Grund**: Timer-Intervall zu häufig
- **Lösung**: Timer-Intervall auf 500ms erhöhen (aktuell: 250ms)

### Corner Handle antwortet nicht auf Drag
- **Grund**: Widget-Position nicht updatet
- **Lösung**: Timer sorgt für regelmäßige Neu-Positionierung

---

**Integration Difficulty**: ⭐⭐ (Easy)  
**Lines of Code**: ~15-20 (ohne Timer)
