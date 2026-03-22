# WidgetSystem - Quick Reference

Schnellreferenz für die wichtigsten Projektkonventionen.

## 📁 Projektstruktur

```
src/widgetsystem/          ← Alle Quelldateien hier
├── core/                  ← Hauptfenster & Anwendungslogik
├── factories/             ← Factory-Klassen für UI-Komponenten
└── ui/                    ← UI-Komponenten & visuelle Ebene

tests/                     ← Alle Tests
examples/                  ← Demo-Anwendungen
config/                    ← JSON-Konfigurationen
```

**Wichtig**: Nie Python-Module im Root-Verzeichnis erstellen!

## 📝 Imports

**Immer absolute Imports verwenden:**

```python
# ✅ RICHTIG
from widgetsystem.factories.layout_factory import LayoutFactory
from widgetsystem.ui import ConfigurationPanel

# ❌ FALSCH
from ..factories.layout_factory import LayoutFactory
from layout_factory import LayoutFactory
```

**Import-Reihenfolge:**
1. Standard-Bibliothek
2. Third-Party (PySide6, PySide6QtAds)
3. First-Party (widgetsystem.*)

## 🏭 Factory-Pattern

Jede Factory muss haben:

```python
class ComponentFactory:
    def __init__(self, config_path: Path) -> None:
        """Initialize mit config-Verzeichnis."""
        
    def load_components(self) -> list[Component]:
        """Lade alle Komponenten aus JSON."""
        
    def _create_component(self, data: dict[str, Any]) -> Component:
        """Erstelle einzelne Komponente (privat)."""
```

## 🎨 UI-Komponenten

Jede UI-Komponente muss:

```python
class ComponentWidget(QWidget):
    # Signals auf Klassenebene definieren
    data_changed = Signal(object)
    
    def __init__(self, config_path: Path, parent: QWidget | None = None):
        super().__init__(parent)
        self.factory = ComponentFactory(config_path)
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self) -> None:
        """Setup UI mit Layouts."""
        
    def refresh(self) -> None:
        """Daten neu laden und anzeigen."""
```

## ⚙️ JSON-Konfiguration

**Immer relative Pfade vom Workspace-Root:**

```json
{
  "file": "data/layout.xml",      // ✅ RICHTIG
  "stylesheet": "themes/dark.qss"
}
```

**Struktur:**
```json
{
  "items": [
    {
      "id": "unique_id",          // Erforderlich
      "name": "Display Name",     // Erforderlich
      "description": "Optional"
    }
  ]
}
```

## 🧪 Tests

**Test-Namen:**
- Dateien: `test_<modul>.py`
- Funktionen: `test_<was>_<bedingung>()`

**UI-Tests benötigen QApplication:**
```python
def test_widget():
    app = QApplication.instance() or QApplication(sys.argv)
    widget = ComponentWidget(Path("config"))
    assert widget is not None
```

## 📏 Code-Style

- **Type Hints**: Pflicht für alle Funktionen/Methoden
- **Docstrings**: Google-Format, pflicht für public APIs
- **Benennung**:
  - Klassen: `PascalCase`
  - Funktionen: `snake_case`
  - Konstanten: `UPPER_SNAKE_CASE`
  - Private: `_prefix`

## 🚀 Befehle

```bash
# Installation
pip install -e ".[dev]"

# Tests
pytest tests/
python tests/verify_setup.py

# Code-Qualität
mypy src/
ruff check src/
black src/
isort src/

# Beispiele
python examples/complete_demo.py
python examples/demo.py
```

## ❌ Häufige Fehler vermeiden

1. Python-Dateien im Root erstellen
2. Relative Imports verwenden
3. Type Hints vergessen
4. Hardcodierte Pfade statt `Path`-Objekte
5. Widgets direkt erstellen statt Factories
6. Docstrings weglassen
7. Nach Refactoring Imports nicht aktualisieren
8. Zirkuläre Imports

## 📚 Weitere Infos

- Vollständige Guidelines: `.github/copilot-instructions.md`
- Factory-Regeln: `.github/instructions/factories.instructions.md`
- UI-Regeln: `.github/instructions/ui-components.instructions.md`
- Test-Regeln: `.github/instructions/testing.instructions.md`
- JSON-Regeln: `.github/instructions/json-config.instructions.md`

## 🆘 Bei Unsicherheit

1. Bestehende Implementierungen als Vorlage nutzen
2. Tests als Beispiele ansehen
3. Mit `mypy` und `ruff` validieren
4. Vollständige Test-Suite ausführen
