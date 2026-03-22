# Erweiterte Features & Konfigurationssystem

## 📋 Übersicht

Das System wurde mit umfangreichen, vollständig konfigurierbaren Features erweitert, die es Benutzern ermöglichen, die gesamte UI-Struktur zur Laufzeit anzupassen, ohne Code zu ändern.

## 🏗️ Neue Komponenten

### 1. **ListFactory** (`list_factory.py`)
Verwaltet verschachtelte Listen mit vollständiger i18n-Unterstützung.

#### Features:
- Verschachtelte Listen-Strukturen (unlimited nesting)
- Mehrere List-Typen: `vertical`, `horizontal`, `tree`, `table`
- Vollständig konfigurierbar:
  - `sortable`: Sortierbare Listen
  - `filterable`: Filterbar nach Kriterien
  - `searchable`: Such funktionalität
  - `multi_select`: Multi-Select-Modus
- Runtime-Modifikation: `add_item_to_group()`, `remove_item_from_group()`
- Item-Properties: `editable`, `deletable`, `icon`, `data`

#### Verwendung:
```python
factory = ListFactory(Path("config"))
list_groups = factory.load_list_groups()

# Runtime-Modifikation
new_item = ListItem(
    id="new_item",
    label_key="list.new.item",
    content_type="text",
    content="New Content"
)
factory.add_item_to_group("main_list", new_item)
```

#### Konfiguration (`config/lists.json`):
- `list_groups[]`: Array von Listen-Gruppen
- Jede Gruppe hat `items[]` mit optionalen `children`
- Item-Typen: `text`, `button`, `widget`, `custom`, `nested`

---

### 2. **UIConfigFactory** (`ui_config_factory.py`)
Zentrale Verwaltung aller UI-Konfigurationsseiten und Widgets.

#### Features:
- Strukturierte Konfigurationsseiten nach Kategorien:
  - `menus`: Menükonfiguration
  - `lists`: Listen-Verwaltung
  - `tabs`: Registerkarten-Editor
  - `panels`: Panel-Konfiguration
  - `theme`: Design-Auswahl
  - `advanced`: Responsive Design & DnD
- Property-basierte Widget-Definition
- Eigenschaften-Typen: `text`, `number`, `boolean`, `color`, `select`, `multiline`

#### Verwendung:
```python
ui_config = UIConfigFactory(Path("config"))
pages = ui_config.load_ui_config_pages()
categories = ui_config.get_all_categories()

# Kategoriefilterung
menus_pages = ui_config.get_pages_by_category("menus")
```

#### Konfiguration (`config/ui_config.json`):
```json
{
  "config_pages": [
    {
      "id": "menus_config",
      "title_key": "config.menus.title",
      "category": "menus",
      "order": 1,
      "widgets": [...]
    }
  ]
}
```

---

### 3. **ConfigurationPanel** (`config_panel.py`)
Interaktive GUI für die Konfiguration aller Strukturen.

#### Features:
- **Tab-basierte Oberfläche** für verschiedene Konfigurationskategorien
- **Menü-Editor**: Hierarchischer Editor für verschachtelte Menüs
- **Listen-Editor**: Tree-basierter Editor für Listen mit Runtime-Änderung
- **Tab-Editor**: Verwaltung von Registerkarten-Gruppen
- **Panel-Editor**: Erstellung und Konfiguration von Panels
- **Theme-Selector**: Design-Auswahl mit Live-Anwendung
- **Advanced Settings**: Responsive Design & Drag & Drop-Konfiguration

#### Signale:
- `config_changed(category)`: Emitted wenn Konfiguration ändert
- `item_added(category, id)`: Emitted wenn Element hinzugefügt
- `item_deleted(category, id)`: Emitted wenn Element gelöscht

#### Komponenten-Architektur:
```python
# Tree Widgets für hierarchische Strukturen
- menu_tree: Menü-Hierarchie
- list_tree: Listen-Hierarchie
- tabs_tree: Registerkarten-Gruppen

# Property-Editoren
- QFormLayout für Eigenschaften
- QLineEdit, QComboBox, QCheckBox für Input
- Signal-basierte Event-Verarbeitung
```

---

## 🔄 Integration in main.py

### Neue Imports:
```python
from list_factory import ListFactory
from ui_config_factory import UIConfigFactory
from config_panel import ConfigurationPanel
```

### Factory-Initialisierung:
```python
self.list_factory = ListFactory(Path("config"))
self.ui_config_factory = UIConfigFactory(Path("config"))
```

### Konfigurationspanel-Zugriff:
1. **Toolbar-Button**: "Config" (rechts in der Toolbar)
2. **Tastaturkürzel**: `Ctrl+Shift+C`
3. **Menü**: Tools → Configuration

### Signalverbindungen:
```python
config_widget_content = ConfigurationPanel(...)
config_widget_content.config_changed.connect(
    lambda category: self._on_config_changed(category)
)
```

### Event-Handler:
```python
def _on_config_changed(self, category: str) -> None:
    """Handle configuration changes - reload factory"""
    if category == "menus":
        self.menu_factory = MenuFactory(Path("config"))
```

---

## 📝 i18n-Unterstützung

Alle Konfigurationsseiten, Labels, und Buttons sind vollständig lokalisiert:

### Deutsche Übersetzungen (`config/i18n.de.json`):
- `config.menus.title`: "Menückonfiguration"
- `config.menus.description`: "Erstellen und bearbeiten Sie Menükstrukturen"
- `config.list_editor.label`: "Listen-Editor"
- `config.panel_editor.label`: "Panel-Editor"
- Und ~70 weitere Einträge

### Englische Übersetzungen (`config/i18n.en.json`):
- `config.menus.title`: "Menu Configuration"
- `config.menus.description`: "Create and edit menu structures"
- Entsprechung für alle deutschen Einträge

---

## 🎯 Konfigurationsstruktur

### config/lists.json

```json
{
  "list_groups": [
    {
      "id": "main_list",
      "title_key": "list.main.title",
      "list_type": "tree",
      "dock_panel_id": "left",
      "sortable": true,
      "filterable": true,
      "searchable": true,
      "multi_select": false,
      "items": [
        {
          "id": "item_1",
          "label_key": "list.item.1",
          "content_type": "text",
          "content": "Item 1",
          "editable": true,
          "deletable": true,
          "icon": "document",
          "children": [...]
        }
      ]
    }
  ]
}
```

### config/ui_config.json
Definiert alle Konfigurationsseiten mit Widgets und Eigenschafts-Editoren. Strukturiert nach Kategorien mit Order für Sortierung.

---

## 🚀 Runtime-Modifikation

Alle Strukturen können zur Laufzeit modifiziert werden:

### Listen:
```python
# Element hinzufügen
factory.add_item_to_group("main_list", new_item, parent_id=None)

# Element entfernen
factory.remove_item_from_group("main_list", "item_1")
```

### Konfiguration aktualisieren:
```python
def _on_config_changed(self, category: str) -> None:
    if category == "lists":
        self.list_factory = ListFactory(Path("config"))
        # Factory wird neugeladen, neue Konfiguration aktiv
```

---

## 🎨 DnD-Kompatibilität

Alle neuen Strukturen sind DnD-kompatibel:

### ConfigurationPanel:
- `dnd_enabled`: True für alle widget (standardmäßig)
- `movable`: Widgets können in der UI bewegt werden
- `resizable`: Einige Widgets sind größenveränderbar
- `container`: Einige Widgets können andere enthalten

### Listen:
- Items können innerhalb der Liste verschoben werden
- Nested Items können reorganisiert werden

### Panels:
- Konfigurierte Panels haben DnD-Support
- Abhängig von `dnd_enabled` in der Panel-Konfiguration

---

## ✨ Erweiterte Funktionen

### Responsive Design:
- Breakpoint-Definition (xs, sm, md, lg, xl)
- Panel-Sichtbarkeit je nach Breakpoint
- UI-Anpassung bei Fenstergrößenänderung

### Drag & Drop Einstellungen:
- Aktivierung/Deaktivierung
- Opazität beim Ziehen konfigurierbar

### Theme-System:
- Integriert mit Light/Dark Themes
- Theme-Switching in Konfigurationspanel

---

## 📊 Dateistruktur nach Update

```
├── config/
│   ├── lists.json              ✨ NEW - Listen-Konfiguration
│   ├── ui_config.json          ✨ NEW - UI-Konfiguration
│   ├── i18n.de.json            (erweitert)
│   ├── i18n.en.json            (erweitert)
│   ├── panels.json
│   ├── menus.json
│   ├── tabs.json
│   ├── themes.json
│   └── ...
├── list_factory.py             ✨ NEW - Listen-Factory
├── ui_config_factory.py        ✨ NEW - UI-Config-Factory
├── config_panel.py             ✨ NEW - Konfigurationspanel
├── main.py                     (aktualisiert mit neuen Factories)
└── ...
```

---

## 🔍 Validierung & Testing

✅ **ListFactory**: 
- JSON-Konfiguration valide
- Recursive Parsing funktioniert
- Runtime-Modifikation möglich

✅ **UIConfigFactory**:
- 5 Konfigurationsseiten geladen
- Kategoriefilterung funktioniert
- Property-Definitionen valid

✅ **ConfigurationPanel**:
- Alle Tabs verfügbar
- Signale verbunden
- Live-Konfiguration möglich

✅ **i18n**:
- ~70 neue Einträge in Deutsch
- ~70 neue Einträge in Englisch
- Alle Keys konsistent

---

## 🎓 Verwendungsbeispiel

```python
# Konfigurationspanel öffnen (User-Action)
window._show_configuration_panel()

# Benutzer:
# 1. Navigiert zu "Listenkonfiguration"
# 2. Editiert Liste: Name, Typ, Eigenschaften
# 3. Klickt "Hinzufügen"
# 4. Emits: config_changed("lists")

# Dashboard:
# 1. Signal empfangen
# 2. _on_config_changed("lists") aufgerufen
# 3. ListFactory neugeladen aus config/lists.json
# 4. UI aktualisiert mit neuer Konfiguration
```

---

## 🔗 Säulen der Architektur

Das System basiert auf 4 Haupt-Säulen:

1. **Factory Pattern**: Alle Strukturen über Factories der json-Config geladen
2. **Type Safety**: 100% typsicher mit TypedDict, @dataclass, type hints
3. **i18n-First**: Alle UI-Strings über i18n-Keys lokalisierbar
4. **Runtime-Modular**: Alle Komponenten zur Laufzeit modifizierbar

---

## 📈 Erweiterungsoptionen

Die Architektur ermöglicht einfache Erweiterungen:

- ➕ Neue Listen-Item-Typen hinzufügen
- ➕ Neue Widget-Typen in UIConfigFactory
- ➕ Neue Konfigurationskategorien
- ➕ Custom Widget Editoren
- ➕ Persistenz (Konfiguration speichern)
- ➕ Undo/Redo für Konfigurationsänderungen

