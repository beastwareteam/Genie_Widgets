# WidgetSystem

Ein modulares, konfigurationsgesteuertes GUI-Anwendungs-Framework mit PySide6 und Advanced Docking System.

## 🤖 Für AI-Agents

**Dieses Projekt hat umfassende Richtlinien. Bitte lesen Sie diese Dateien VOR der Arbeit:**

### Pflichtlektüre
1. **`AGENT_CONFIG.md`** - Übersicht und Einstiegspunkt für alle AI-Agents
2. **`.github/copilot-instructions.md`** - Vollständige Projektrichtlinien
3. **`QUICK_REFERENCE.md`** - Kompakte Referenz (Deutsch)

### Kontext-spezifische Richtlinien
- `.github/instructions/factories.instructions.md` - Factory-Klassen
- `.github/instructions/ui-components.instructions.md` - UI-Komponenten
- `.github/instructions/testing.instructions.md` - Tests
- `.github/instructions/json-config.instructions.md` - JSON-Konfiguration

## 🎯 Kritische Regeln

### Projektstruktur (PEP 420 src-layout)
- ✅ **Alle** Quelldateien in `src/widgetsystem/`
- ❌ **Niemals** Python-Dateien im Root-Verzeichnis erstellen

### Import-Konvention
```python
# ✅ RICHTIG - Absolute Imports
from widgetsystem.factories.layout_factory import LayoutFactory
from widgetsystem.ui import ConfigurationPanel

# ❌ FALSCH - Relative Imports
from ..factories.layout_factory import LayoutFactory
from layout_factory import LayoutFactory
```

### Factory-Pattern
- Alle UI-Komponenten durch Factories erstellen
- Factories laden aus JSON-Konfiguration (`config/` Verzeichnis)
- Konfigurationspfade relativ zum Workspace-Root

### Type Hints
- **Pflicht** für alle Funktionen und Methoden
- `Path`-Objekte für Dateipfade verwenden
- Python 3.10+ Syntax

### Code-Qualität
- Google-Style Docstrings für alle öffentlichen APIs
- MyPy für Type-Checking
- Ruff für Linting
- Black für Formatierung

## 📁 Verzeichnisstruktur

```
WidgetSystem/
├── .github/
│   ├── copilot-instructions.md      # Hauptkonfiguration
│   └── instructions/                # Datei-spezifische Regeln
├── src/widgetsystem/                # Hauptpaket
│   ├── core/                        # Kernanwendungslogik
│   │   ├── main.py
│   │   └── main_visual.py
│   ├── factories/                   # Factory-Klassen
│   │   ├── layout_factory.py
│   │   ├── theme_factory.py
│   │   ├── menu_factory.py
│   │   └── ... (10 Factories)
│   ├── ui/                          # UI-Komponenten
│   │   ├── visual_layer.py
│   │   ├── visual_app.py
│   │   └── config_panel.py
│   ├── __init__.py
│   ├── py.typed                     # PEP 561 Marker
│   └── PySide6QtAds.pyi            # Type Stubs
├── tests/                           # Test-Suite
│   ├── verify_setup.py
│   ├── test_full_system.py
│   └── test_visual_layer.py
├── examples/                        # Demo-Anwendungen
│   ├── complete_demo.py
│   └── demo.py
├── config/                          # JSON-Konfigurationen
│   ├── layouts.json
│   ├── themes.json
│   ├── menus.json
│   └── ... (10 Config-Dateien)
├── schemas/                         # JSON-Schemas
├── themes/                          # QSS-Stylesheets
│   ├── dark.qss
│   └── light.qss
├── data/                            # Datendateien
│   ├── layout.xml
│   └── layout_alt.xml
└── pyproject.toml                   # Projektkonfiguration
```

## 🛠️ Entwicklungsumgebung

### Installation
```bash
# Virtual Environment erstellen
python -m venv .venv

# Aktivieren (Windows)
.venv\Scripts\activate

# Paket installieren (Entwicklungsmodus)
pip install -e ".[dev]"
```

### Tests ausführen
```bash
# Alle Tests
pytest tests/

# Setup verifizieren
python tests/verify_setup.py

# Vollständiger Systemtest
python tests/test_full_system.py

# Visual Layer Test
python tests/test_visual_layer.py
```

### Code-Qualität prüfen
```bash
# Alle Qualitätschecks ausführen (empfohlen vor Commit)
python scripts/check_quality.py

# Auto-Fix für häufige Probleme
python scripts/autofix.py

# Pre-Commit Hooks installieren
pre-commit install
pre-commit run --all-files

# Einzelne Tools:
ruff check src/                      # Linting (600+ Rules)
ruff format src/                     # Formatierung
mypy src/                            # Type Checking (strict mode)
pylint src/widgetsystem/             # Zusätzliches Linting (min 9.0/10)
bandit -r src/ -c pyproject.toml     # Security Scanning
pytest tests/ --cov=src/widgetsystem # Tests mit Coverage (min 80%)
```

### Beispiele ausführen
```bash
# Vollständige Demo
python examples/complete_demo.py

# Basis-Demo
python examples/demo.py
```

## 🏗️ Architektur-Prinzipien

### Factory-Pattern
Alle UI-Komponenten werden durch Factory-Klassen erstellt:
- **LayoutFactory** - Fenster-Layouts
- **ThemeFactory** - Themes und Stylesheets
- **MenuFactory** - Menüs und Menü-Items
- **PanelFactory** - Dock-Panels
- **ListFactory** - Listen und Gruppen
- **TabsFactory** - Tab-Gruppen
- **DnDFactory** - Drag & Drop Konfiguration
- **I18nFactory** - Internationalisierung
- **ResponsiveFactory** - Responsive Layouts
- **UIConfigFactory** - UI-Konfiguration

### Konfigurationsgesteuert
- Alle UI-Definitionen in JSON-Dateien (`config/`)
- JSON-Schema-Validierung (`schemas/`)
- Relative Pfade vom Workspace-Root

### Separation of Concerns
- **`core/`** - Anwendungs-Shell und Hauptfenster
- **`factories/`** - Komponenten-Erstellung
- **`ui/`** - Visuelle Komponenten und Panels

## 🔧 Konfiguration

### JSON-Konfigurationsdateien
- `layouts.json` - Fenster-Layouts
- `themes.json` - Theme-Definitionen
- `menus.json` - Menü-Konfigurationen
- `panels.json` - Panel-Definitionen
- `tabs.json` - Tab-Konfigurationen
- `lists.json` - Listen-Definitionen
- `dnd.json` - Drag & Drop Konfiguration
- `responsive.json` - Responsive Layout-Regeln
- `ui_config.json` - UI-Element-Konfiguration
- `i18n.de.json` / `i18n.en.json` - Übersetzungen

### Pfad-Konvention in JSON
```json
{
  "file": "data/layout.xml",          // ✅ Relativ zum Workspace-Root
  "stylesheet": "themes/dark.qss"     // ✅ Relativ zum Workspace-Root
}
```

## 🧪 Testing-Strategie

- **Unit Tests** - Einzelne Komponenten und Factories
- **Integration Tests** - Zusammenspiel mehrerer Komponenten
- **UI Tests** - Widget-Funktionalität mit QApplication
- **Verification Tests** - Setup und Konfiguration

## 📦 Dependencies

### Erforderlich
- Python 3.10+
- PySide6 >= 6.5.0
- PySide6-QtAds >= 4.0.0

### Entwicklung
- mypy >= 1.8.0 - Type Checking
- ruff >= 0.2.0 - Linting
- black >= 24.0.0 - Code Formatierung
- isort >= 5.13.0 - Import-Sortierung
- pytest >= 7.4.0 - Testing

## 📄 Lizenz

MIT

## 🤝 Beitragen

Beiträge sind willkommen! Bitte beachten Sie:
1. Lesen Sie **alle** Richtlinien in `.github/`
2. Folgen Sie dem Factory-Pattern
3. Verwenden Sie Type Hints
4. Schreiben Sie Tests
5. Aktualisieren Sie Dokumentation

## 📚 Weiterführende Dokumentation

- **AGENT_CONFIG.md** - Agent-Konfiguration Übersicht
- **QUICK_REFERENCE.md** - Schnellreferenz
- **.github/README.md** - Copilot-Konfiguration Details
- **docs/** - Zusätzliche Dokumentation

---

**Wichtig für AI-Agents**: Dieses Projekt folgt strengen Konventionen für Codequalität und Konsistenz. Lesen Sie ALLE Konfigurationsdateien, bevor Sie Änderungen vornehmen. Die Richtlinien sind nicht optional—sie repräsentieren Team-Vereinbarungen und Best Practices.
