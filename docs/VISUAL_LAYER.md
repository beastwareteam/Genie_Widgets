# 🎨 Visuelle Ebene - Architektur & Komponenten

## 📋 Übersicht

Die **Visuelle Ebene** ist eine vollständige Darstellungsschicht, die alle strukturellen Komponenten des Systems visualisiert:

- **Listen** mit hierarchischer Darstellung
- **Menüs** mit Verschachtelung
- **Tabs** in Gruppen organisiert
- **Panels** mit Konfigurationen
- **Responsive Layouts** passend zur Fensteröße

## 🏗️ Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    VisualMainWindow                         │
│  (QtAds Docking System + Toolbar + Menu)                    │
├─────────────────────────────────────────────────────────────┤
│                  Vier DockWidget-Bereiche                   │
├──────────────────────┬──────────────────────────────────────┤
│   LINKS              │   RECHTS                             │
├──────────────────────┼──────────────────────────────────────┤
│ • ListsViewer        │ • TabsViewer                         │
│   (Listen-Hierarchie)│   (Tab-Gruppen)                      │
│                      │                                      │
│ • MenusViewer        │ • PanelsViewer                       │
│   (Menü-Struktur)    │   (Panel-Configs)                    │
└──────────────────────┴──────────────────────────────────────┘
```

## 📦 Komponenten

### 1. ListsViewer
**Datei**: `visual_layer.py`

Zeigt alle Listen mit vollständiger Hierarchie:
- **Struktur**: Gruppen → Elemente → Unterelemente
- **Features**:
  - Expandierbare Baumstruktur
  - Eigenschaften-Panel für selected Items
  - i18n-Unterstützung
  - Konfigurierbare Anzeigetiefe

```python
# Beispiel-Nutzung:
viewer = ListsViewer(
    Path("config"),
    i18n_factory,
    config=ViewerConfig(show_properties=True)
)
viewer.refresh()  # Daten neu laden
```

### 2. MenusViewer
**Datei**: `visual_layer.py`

Visualisiert die komplette Menü-Struktur:
- **Struktur**: Root-Menüs → Untermenüs → Actions
- **Features**:
  - Rekursive Darstellung
  - Menü-Typen anzeigen
  - Eigenschaften-Anzeige
  - Schnellnavigation

```python
viewer = MenusViewer(
    Path("config"),
    i18n_factory,
    config=ViewerConfig(show_properties=True)
)
```

### 3. TabsViewer
**Datei**: `visual_layer.py`

Zeigt Tab-Gruppen und ihre Tabs:
- **Struktur**: Gruppen → Tabs
- **Features**:
  - Übersichtliche Baumansicht
  - Tab-Properties abrufbar
  - Gruppierung nach Container

```python
viewer = TabsViewer(
    Path("config"),
    i18n_factory
)
```

### 4. PanelsViewer
**Datei**: `visual_layer.py`

Listet alle Panel-Konfigurationen:
- **Struktur**: Flache Liste aller Panels
- **Features**:
  - Panel-Details anzeigen
  - Bereichs-Zuweisung sichtbar
  - Eigenschaften-Formular

```python
viewer = PanelsViewer(
    Path("config"),
    i18n_factory
)
```

### 5. VisualDashboard
**Datei**: `visual_layer.py`

Kombiniert alle 4 Viewer in einem Fenster:
- **Layout**: Tab-basiert
  - Tab 1: Listen
  - Tab 2: Menüs
  - Tab 3: Tabs
  - Tab 4: Panels
- **Purpose**: Schnelle Übersicht über gesamte Struktur

```python
dashboard = VisualDashboard(Path("config"), i18n_factory)
dashboard.show()
```

## 🎯 VisualMainWindow

**Datei**: `visual_app.py`

Hauptfenster mit vollständiger Anwendung:

### Toolbar-Aktionen:
- **📊 Dashboard** - Zeigt VisualDashboard
- **⚙️ Konfiguration** - Öffnet ConfigurationPanel zur Bearbeitung
- **🔄 Aktualisieren** - Refresht alle Viewer
- **🎨 Themes** - Theme-Auswahl (Light/Dark)

### Menu-Struktur:
```
Datei
  └─ Beenden

Ansicht
  ├─ Listen anzeigen
  ├─ Menüs anzeigen
  ├─ Tabs anzeigen
  └─ Panels anzeigen

Hilfe
  ├─ Über...
```

### DockWidgets:
- **Links-Oben**: ListsViewer (Listen-Hierarchie)
- **Links-Unten**: MenusViewer (Menü-Struktur)
- **Rechts-Oben**: TabsViewer (Tab-Gruppen)
- **Rechts-Unten**: PanelsViewer (Panels)

## 🔄 Datenfluss

```
Configuration (config/*.json)
        ↓
    Factories
        ↓
   Viewer Components
        ↓
   VisualMainWindow (QtAds Docking)
        ↓
   User Interface
```

## 💻 Verwendung

### Start der Visual Application:
```bash
python visual_app.py
```

### Ausgabe:
```
============================================================
🚀 WidgetSystem - VISUELLE EBENE (Visual Layer)
============================================================

✅ Anwendung wird gestartet...
✅ Alle Factories werden initialisiert...
✅ Viewer werden erstellt...
✅ Docking-System wird konfiguriert...

============================================================
✨ VISUELLE EBENE IST AKTIV
============================================================

Verfügbare Komponenten:
  📋 Listen-Viewer (Links)
  📝 Menü-Viewer (Links)
  📑 Tabs-Viewer (Rechts)
  📦 Panels-Viewer (Rechts)

Aktionen:
  🎨 Themes im Toolbar wählbar
  ⚙️  Konfigurationspanel erreichbar
  📊 Dashboard für Übersicht verfügbar
```

## 🎨 Features

### 1. ViewerConfig
Konfigurierbar für verschiedene Anzeigeoptionen:

```python
config = ViewerConfig(
    show_properties=True,    # Eigenschaften-Panel anzeigen
    show_icons=True,         # Icons in Trees
    editable=False,          # Bearbeitung erlauben
    max_depth=10             # Maximale Hierarchie-Tiefe
)
```

### 2. Theme-Integration
- Light-Theme für helle Umgebung
- Dark-Theme für Nacht-Modus
- Zwischen Themes wählbar

### 3. i18n-Support
- Alle Labels in Deutsch
- Englisch verfügbar (erweiterbar)
- Konsistente Übersetzungen

### 4. Interaktivität
- Drag & Drop im Docking-System
- Fenster verschiebbar/resizable
- Tree-Items expandierbar
- Properties-Panel live aktualisierbar

## 📝 Beispiel-Integration

```python
from visual_layer import VisualDashboard
from i18n_factory import I18nFactory
from pathlib import Path

# Factories initialisieren
i18n = I18nFactory(Path("config"), locale="de")

# Dashboard öffnen
dashboard = VisualDashboard(Path("config"), i18n)
dashboard.show()

# Oder Hauptfenster starten
from visual_app import VisualMainWindow
window = VisualMainWindow()
window.show()
```

## 🔗 Komponenten-Matrix

| Komponente | Datenquelle | Anzeige-Typ | Interaktiv | Editierbar |
|------------|------------|-------------|-----------|-----------|
| ListsViewer | ListFactory | Tree | Ja | Optional |
| MenusViewer | MenuFactory | Tree | Ja | Optional |
| TabsViewer | TabsFactory | Tree | Ja | Nein |
| PanelsViewer | PanelFactory | List | Ja | Optional |
| Dashboard | Alle | Tabs+Widgets | Ja | Nein |

## 🚀 Nächste Schritte

1. **ConfigurationPanel mit Viewers synchronisieren**
   - Änderungen in Config sofort in Viewern sichtbar
   - Live-Refresh bei Modifikationen

2. **DragDrop zwischen Structuren**
   - Elemente verschiebbar
   - Neue Hierarchien erstellbar

3. **Export-Funktionen**
   - Strukturen als JSON exportieren
   - Snapshots speichern

4. **Advanced Visualizations**
   - Verschiedene View-Modi
   - Graphische Layouts
   - Dependency-Visualisierung

## ✅ Status

- ✅ ListsViewer - Funktional
- ✅ MenusViewer - Funktional
- ✅ TabsViewer - Funktional
- ✅ PanelsViewer - Funktional
- ✅ VisualDashboard - Funktional
- ✅ VisualMainWindow - Funktional
- ✅ Theme-Integration - Funktional
- ✅ i18n-Support - Funktional
- 🟡 Live-Synchronisierung - Geplant
- 🟡 Editing im Viewer - Geplant

---

## 📚 Weitere Dokumentation

- [DEMO.md](DEMO.md) - Feature-Übersicht
- [EXTENDED_FEATURES.md](EXTENDED_FEATURES.md) - Technische Details
- [test_full_system.py](test_full_system.py) - System-Tests
- [config_panel.py](config_panel.py) - KonfigurationsEditor
