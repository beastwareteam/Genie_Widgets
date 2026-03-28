# Actionbar-Erweiterung – Vollständiger Architekturplan

## 1. Zusammenfassung

Dieses Dokument beschreibt die gründliche Architektur für eine verschachtelte,
konfigurierbare Actionbar mit Ordner-Strukturen, Slide-out-Panels, Miniatur-
ansichten und Automationsfähigkeit. Der Plan baut auf der **bestehenden**
Infrastruktur auf und schließt gezielt die dokumentierten Lücken in Validierung,
Backup und Fehlerbehandlung.

### Zielbild

- Visuelle Ordner mit Slide-out für Action-Buttons (wie Android-Ordner, Discord-Servergruppen)
- Komprimierte Darstellung mit Miniaturansichten
- Farbliche Markierung und Konfiguration pro Gruppe
- Automatisiertes Anlegen von Actions und Ordnern
- Starten ganzer Programme, Module und Automatisierungen

### Grundprinzip

```
config/toolbar.json          (klassische Toolbar – bleibt UNVERÄNDERT)
config/actions.json           (statische Action-Definitionen – bleibt UNVERÄNDERT)
config/custom_actions.json    (Custom Actions – wird ERWEITERT, nicht ersetzt)
config/actionbar.json         (NEU: Baum-Struktur der verschachtelten Actionbar)
config/actionbar_state.json   (NEU: UI-Zustand – letzte Öffnung, Pinning, Badges)
schemas/actionbar.schema.json (NEU: Schema für Baum-Struktur)
```

---

## 2. Bestandsaufnahme bestehender Infrastruktur

### 2.1 Was existiert und funktioniert

| Komponente | Datei | Status |
|---|---|---|
| `ActionFactory` | `src/widgetsystem/factories/action_factory.py` | ✅ 15 Actions in 5 Kategorien |
| `ActionRegistry` | `src/widgetsystem/core/action_registry.py` | ✅ Singleton, QAction-Cache, Handler-Binding |
| `ToolbarFactory` | `src/widgetsystem/factories/toolbar_factory.py` | ✅ JSON-gesteuerte QToolBar-Erzeugung |
| `ConfigValidator` | `src/widgetsystem/core/config_validator.py` | ✅ ID/Name-Sanitierung, Struktur-Validation, Backup/Failsafe |
| `BackupManager` | `src/widgetsystem/core/config_io.py` | ✅ Verzeichnis-Level-Backup (max 10) |
| Custom Actions | `config/custom_actions.json` | ⚠️ Schema vorhanden, Array leer |
| JSON-Schemas | `schemas/*.schema.json` | ⚠️ 11 Schemas, aber nur 2 Factories nutzen sie zur Laufzeit |

### 2.2 Dokumentierte Schwächen (werden im Plan adressiert)

| Problem | Beschreibung | Lösung im Plan |
|---|---|---|
| **Inkonsistente Fehlende-Datei-Behandlung** | 7 Factories werfen `FileNotFoundError`, 4 degradieren graceful | Neue Factories IMMER graceful (§4.3) |
| **Schemas nicht runtime-geprüft** | `.schema.json` existieren, werden nie geladen | Neue Factories nutzen `ConfigValidator` (§4.2) |
| **Backup nur für 2 Factories** | Nur Panel/Tabs nutzen `load_with_failsafe` | Alle neuen Stores nutzen `save_with_backup` + `load_with_failsafe` (§4.4) |
| **Logging inkonsistent** | 4 von 14 Factories nutzen `logging` | Alle neuen Module nutzen `logging` (§4.5) |
| **ConfigValidator untergenutzt** | `sanitize_config`, `validate_structure` kaum verwendet | Volle Integration in allen neuen Stores (§4.2) |

---

## 3. Datenmodell

### 3.1 ActionbarNode (Kern-Datenstruktur)

Jeder Knoten im Actionbar-Baum ist ein `ActionbarNode`:

```python
@dataclass
class ActionbarNode:
    """Einzelner Knoten im Actionbar-Baum."""

    # Identifikation
    id: str                               # Eindeutig, validiert gegen ConfigValidator.validate_id
    type: str                             # "action" | "folder" | "separator" | "automation"
    
    # Darstellung
    label: str = ""                       # Validiert gegen ConfigValidator.validate_name
    icon: str = ""                        # Icon-Name oder Unicode-Fallback
    color: str = ""                       # CSS-Farbe für Akzent/Rand (#rrggbb oder "")
    badge: str = ""                       # Optionaler Badge-Text ("3", "!", "NEW")
    visible: bool = True
    enabled: bool = True
    
    # Quelle (was wird ausgelöst)
    source_kind: str = ""                 # "registry" | "custom" | "automation" | "module" | "external"
    source_id: str = ""                   # z.B. "action_save_layout" oder "custom.export_pdf"
    
    # Verschachtelung (nur für type="folder")
    children: list[ActionbarNode] = field(default_factory=list)
    collapsed_style: str = "icon"         # "icon" | "stacked" | "mini_grid" | "badge_count"
    slideout_direction: str = "down"      # "down" | "right" | "popup"
    layout_mode: str = "grid"             # "grid" | "list" | "stack" | "carousel"
    preview_count: int = 4                # Anzahl Miniatur-Vorschauen (0 = keine)
    max_depth: int = 2                    # Maximale Verschachtelungstiefe ab hier
    
    # Thumbnail/Preview
    thumbnail_mode: str = "icon"          # "icon" | "snapshot" | "color_swatch" | "none"
    thumbnail_data: str = ""              # Optionale Thumbnail-Referenz
    
    # Sortierung/Filterung
    sort_order: int = 0
    tags: list[str] = field(default_factory=list)
    category: str = ""                    # Zur automatischen Gruppierung
```

### 3.2 ActionbarNode Validierung (\_\_post\_init\_\_)

```python
def __post_init__(self) -> None:
    """Wertebereiche prüfen."""
    valid_types = {"action", "folder", "separator", "automation"}
    if self.type not in valid_types:
        raise ValueError(f"type '{self.type}' nicht in {valid_types}")
    
    valid_source_kinds = {"", "registry", "custom", "automation", "module", "external"}
    if self.source_kind not in valid_source_kinds:
        raise ValueError(f"source_kind '{self.source_kind}' ungültig")
    
    valid_collapsed = {"icon", "stacked", "mini_grid", "badge_count"}
    if self.collapsed_style not in valid_collapsed:
        self.collapsed_style = "icon"  # Fallback statt Crash
    
    valid_directions = {"down", "right", "popup"}
    if self.slideout_direction not in valid_directions:
        self.slideout_direction = "down"
    
    valid_layouts = {"grid", "list", "stack", "carousel"}
    if self.layout_mode not in valid_layouts:
        self.layout_mode = "grid"
    
    if self.preview_count < 0:
        self.preview_count = 0
    if self.preview_count > 9:
        self.preview_count = 9
    
    if self.max_depth < 1:
        self.max_depth = 1
    if self.max_depth > 3:
        self.max_depth = 3  # Harte Obergrenze für UX
```

### 3.3 Verschachtelungsgrenzen

| Phase | Max. Tiefe | Begründung |
|---|---|---|
| MVP (Phase 1-2) | 2 | Root → Folder → Actions |
| Phase 3-4 | 3 | Root → Folder → Sub-Folder → Actions |
| Unbegrenzt | **Nie** | UX-Katastrophe, Performance-Risiko |

Die Grenze wird **doppelt** durchgesetzt:
1. `ActionbarNode.max_depth` (pro Knoten)
2. `ConfigValidator.MAX_NESTING_DEPTH` (global, Wert 5 deckt auch Wrapper-Ebenen ab)

---

## 4. Validierung, Fallback, Backup (Kernkapitel)

### 4.1 Dreistufiges Validierungsmodell

Jeder neue Store durchläuft drei Stufen:

```
 Stufe 1: Schema-Validation        → Struktur passt?
 Stufe 2: Semantic-Validation       → Werte sinnvoll?
 Stufe 3: Cross-Reference-Validation → Referenzen gültig?
```

#### Stufe 1 – Schema-Validation

```python
# Verwendet ConfigValidator.validate_structure()
# Schema definiert in schemas/actionbar.schema.json
# Prüft: Pflichtfelder, Typen, erlaubte Werte, keine unbekannten Felder
```

#### Stufe 2 – Semantic-Validation

```python
# Wird in __post_init__ der Dataclasses durchgesetzt
# Prüft:
#   - type in {"action", "folder", "separator", "automation"}
#   - source_kind in {"registry", "custom", "automation", "module", "external"}
#   - color ist gültiges CSS-Farbformat oder leer
#   - preview_count in [0, 9]
#   - max_depth in [1, 3]
#   - Keine Zirkelreferenzen in children
```

#### Stufe 3 – Cross-Reference-Validation

```python
# Wird beim Laden und vor dem Speichern geprüft
# Prüft:
#   - source_id existiert in ActionRegistry ODER custom_actions.json
#   - folder.children enthalten keine doppelten IDs
#   - Gesamtbaum hat keine doppelten IDs
#   - Tiefe überschreitet nicht max_depth des Elternknotens
```

### 4.2 ConfigValidator-Integration (Pflicht)

Alle neuen Stores **müssen** `ConfigValidator` nutzen:

```python
class ActionbarStore:
    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir
        self.config_file = config_dir / "actionbar.json"
        self._validator = ConfigValidator(config_dir)
        self._cache: list[ActionbarNode] | None = None
```

Operationen:

| Operation | ConfigValidator-Methode | Wann |
|---|---|---|
| Laden | `load_with_failsafe(path)` | Immer beim Laden |
| Speichern | `save_with_backup(path, data, validate=True, schema=SCHEMA)` | Immer beim Speichern |
| ID erzeugen | `validate_id(value)` | Bei jedem neuen Knoten |
| Name setzen | `validate_name(value)` | Bei jedem Label-/Name-Feld |
| Sanitieren | `sanitize_config(data, "actionbar")` | Nach Import/Migration |

### 4.3 Fehlende-Datei-Behandlung (Graceful Degradation)

Decision: **Alle neuen Stores degradieren graceful** (kein `FileNotFoundError`).

```python
def load_nodes(self) -> list[ActionbarNode]:
    """Lade Actionbar-Baum aus JSON."""
    if not self.config_file.exists():
        logger.info("Actionbar config nicht gefunden: %s – leere Actionbar", self.config_file)
        return []  # Leere Actionbar, kein Crash
    
    try:
        data = self._validator.load_with_failsafe(self.config_file)
    except ConfigValidationError:
        logger.warning("Actionbar config und Backup korrupt – leere Actionbar")
        return []  # Graceful Degradation
    
    # Schema-Validation
    errors = self._validator.validate_structure(data, ACTIONBAR_SCHEMA)
    if errors:
        logger.warning("Actionbar Validierungsfehler: %s", errors[:5])
        # Versuche trotzdem zu parsen (best-effort)
    
    return self._parse_nodes(data.get("nodes", []))
```

### 4.4 Backup-Strategie

```
config/
├── actionbar.json              ← Hauptdatei
├── actionbar_state.json        ← UI-Zustand (kein Backup nötig, regenerierbar)
├── .backup/
│   ├── actionbar_20260327_143022.json
│   ├── actionbar_20260326_091500.json
│   └── ... (max 5 per ConfigValidator._cleanup_old_backups)
```

Regeln:
- **Vor jedem Speichern** → `ConfigValidator.create_backup()`
- **Bei Lade-Fehler** → `ConfigValidator.load_with_failsafe()` (automatisches Backup-Restore)
- **Verzeichnis-Backup** → `BackupManager.create_backup("actionbar_migration")` nur bei Migrationen
- **State-Datei braucht kein Backup** (regenerierbar aus UI-Zustand)
- **Max 5 Datei-Backups** (bestehende Einstellung)

### 4.5 Logging-Standard (Pflicht)

```python
import logging
logger = logging.getLogger(__name__)

# Muster:
logger.info("Loaded %d actionbar nodes from %s", count, self.config_file)
logger.warning("Skipping invalid actionbar node: %s", error)
logger.error("Failed to save actionbar config: %s", error)
logger.debug("Validating node '%s': source_kind=%s, source_id=%s", node.id, node.source_kind, node.source_id)
```

Keine `print()`-Aufrufe in neuen Modulen.

---

## 5. JSON-Schema-Entwurf

### 5.1 schemas/actionbar.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Actionbar Configuration",
  "type": "object",
  "required": ["version", "nodes"],
  "properties": {
    "version": {
      "type": "integer",
      "minimum": 1,
      "description": "Schema-Version für Migrationssupport"
    },
    "nodes": {
      "type": "array",
      "items": { "$ref": "#/definitions/node" }
    }
  },
  "additionalProperties": false,
  "definitions": {
    "node": {
      "type": "object",
      "required": ["id", "type"],
      "properties": {
        "id":                { "type": "string", "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$", "maxLength": 64 },
        "type":              { "type": "string", "enum": ["action", "folder", "separator", "automation"] },
        "label":             { "type": "string", "maxLength": 128 },
        "icon":              { "type": "string" },
        "color":             { "type": "string", "pattern": "^(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8}|)$" },
        "badge":             { "type": "string", "maxLength": 8 },
        "visible":           { "type": "boolean", "default": true },
        "enabled":           { "type": "boolean", "default": true },
        "source_kind":       { "type": "string", "enum": ["", "registry", "custom", "automation", "module", "external"] },
        "source_id":         { "type": "string" },
        "children":          { "type": "array", "items": { "$ref": "#/definitions/node" } },
        "collapsed_style":   { "type": "string", "enum": ["icon", "stacked", "mini_grid", "badge_count"] },
        "slideout_direction": { "type": "string", "enum": ["down", "right", "popup"] },
        "layout_mode":       { "type": "string", "enum": ["grid", "list", "stack", "carousel"] },
        "preview_count":     { "type": "integer", "minimum": 0, "maximum": 9 },
        "max_depth":         { "type": "integer", "minimum": 1, "maximum": 3 },
        "thumbnail_mode":    { "type": "string", "enum": ["icon", "snapshot", "color_swatch", "none"] },
        "thumbnail_data":    { "type": "string" },
        "sort_order":        { "type": "integer" },
        "tags":              { "type": "array", "items": { "type": "string" } },
        "category":          { "type": "string" }
      },
      "additionalProperties": false
    }
  }
}
```

### 5.2 config/actionbar.json (Beispiel)

```json
{
  "version": 1,
  "nodes": [
    {
      "id": "action_new_dock",
      "type": "action",
      "source_kind": "registry",
      "source_id": "action_new_dock",
      "sort_order": 0
    },
    {
      "id": "sep_after_dock",
      "type": "separator",
      "sort_order": 1
    },
    {
      "id": "folder_dock_tools",
      "type": "folder",
      "label": "Dock",
      "icon": "window-restore",
      "color": "#3a7ca5",
      "collapsed_style": "mini_grid",
      "slideout_direction": "down",
      "layout_mode": "grid",
      "preview_count": 4,
      "sort_order": 2,
      "children": [
        {
          "id": "child_float_all",
          "type": "action",
          "source_kind": "registry",
          "source_id": "action_float_all",
          "sort_order": 0
        },
        {
          "id": "child_dock_all",
          "type": "action",
          "source_kind": "registry",
          "source_id": "action_dock_all",
          "sort_order": 1
        },
        {
          "id": "child_close_all",
          "type": "action",
          "source_kind": "registry",
          "source_id": "action_close_all",
          "sort_order": 2
        }
      ]
    },
    {
      "id": "folder_tools",
      "type": "folder",
      "label": "Tools",
      "icon": "cog",
      "color": "#6b4c9a",
      "collapsed_style": "stacked",
      "slideout_direction": "down",
      "layout_mode": "list",
      "preview_count": 3,
      "sort_order": 3,
      "children": [
        {
          "id": "child_theme_editor",
          "type": "action",
          "source_kind": "registry",
          "source_id": "action_show_theme_editor",
          "sort_order": 0
        },
        {
          "id": "child_plugin_manager",
          "type": "action",
          "source_kind": "registry",
          "source_id": "action_show_plugin_manager",
          "sort_order": 1
        },
        {
          "id": "child_configuration",
          "type": "action",
          "source_kind": "registry",
          "source_id": "action_show_configuration",
          "sort_order": 2
        }
      ]
    },
    {
      "id": "action_refresh_root",
      "type": "action",
      "source_kind": "registry",
      "source_id": "action_refresh",
      "sort_order": 4
    }
  ]
}
```

### 5.3 config/actionbar_state.json (UI-Zustand)

```json
{
  "last_opened_folder": "folder_dock_tools",
  "pinned_nodes": ["action_refresh_root"],
  "recently_used": ["action_show_theme_editor", "action_new_dock"],
  "folder_states": {
    "folder_dock_tools": { "was_open": false },
    "folder_tools": { "was_open": true }
  },
  "badges": {
    "folder_tools": "3"
  }
}
```

Decision: `actionbar_state.json` ist **regenerierbar** (kein Backup nötig).
Wenn korrupt oder fehlend → Default-State (alles geschlossen, keine Pins).

---

## 6. Klassenliste und Abhängigkeiten

### 6.1 Neue Module

```
src/widgetsystem/
├── factories/
│   └── actionbar_factory.py           # ActionbarStore + ActionbarNode
├── ui/
│   ├── actionbar_view.py              # ActionbarView (Hauptwidget)
│   ├── actionbar_folder_chip.py       # FolderChip (komprimierte Ordner-Darstellung)
│   ├── actionbar_slideout.py          # SlideoutPanel (aufgeklappter Ordner)
│   ├── actionbar_button_card.py       # ActionButtonCard (einzelner Action-Button)
│   └── actionbar_editor_dialog.py     # EditorDialog (Ordner/Actions konfigurieren)
├── core/
│   └── automation_launcher.py         # AutomationLauncher (einheitliche Startlogik)
schemas/
│   └── actionbar.schema.json          # JSON-Schema
config/
│   ├── actionbar.json                 # Baum-Struktur
│   └── actionbar_state.json           # UI-Zustand
tests/
│   ├── test_actionbar_factory.py      # Store/Model-Tests
│   ├── test_actionbar_validation.py   # Validierung/Backup-Tests
│   └── test_automation_launcher.py    # Launcher-Tests
```

### 6.2 Abhängigkeitsgraph

```
ActionbarStore (factories/actionbar_factory.py)
    ├── uses → ConfigValidator           (load_with_failsafe, save_with_backup, validate_id, validate_name)
    ├── uses → ActionbarNode             (Datenmodell)
    ├── reads → config/actionbar.json
    └── reads → schemas/actionbar.schema.json

AutomationLauncher (core/automation_launcher.py)
    ├── uses → ActionRegistry            (get_action, trigger)
    ├── uses → CustomActionStore*        (bestehend, für source_kind="custom")
    └── validates → Whitelist            (für source_kind="external")

ActionbarView (ui/actionbar_view.py)
    ├── uses → ActionbarStore            (Daten laden)
    ├── uses → AutomationLauncher        (Actions ausführen)
    ├── creates → FolderChip             (pro Folder)
    ├── creates → ActionButtonCard       (pro Action)
    └── creates → SlideoutPanel          (pro geöffneten Folder)

ActionbarEditorDialog (ui/actionbar_editor_dialog.py)
    ├── uses → ActionbarStore            (Lesen/Schreiben)
    ├── uses → ActionRegistry            (verfügbare Actions auflisten)
    └── uses → ConfigValidator           (ID/Name-Sanitierung)
```

### 6.3 Integration in MainWindow

```python
# In src/widgetsystem/core/main.py
# Die neue Actionbar wird ALS Widget in die bestehende QToolBar eingebettet:

def _create_toolbar(self) -> None:
    """Create toolbar from ToolbarFactory configuration."""
    # ... bestehender Code bleibt ...
    
    # Feature-Flag prüfen
    if self._use_actionbar:
        actionbar_widget = ActionbarView(
            store=self._actionbar_store,
            launcher=self._automation_launcher,
            parent=self,
        )
        self._toolbar.addWidget(actionbar_widget)
```

Decision: **Klassische Toolbar bleibt erhalten.** Feature-Flag `use_actionbar` schaltet um.

---

## 7. Fehlerbehandlungsmatrix

### 7.1 Lade-Fehler

| Szenario | Behandlung | User sieht |
|---|---|---|
| `actionbar.json` fehlt | `return []` + `logger.info` | Leere Actionbar, klassische Toolbar funktioniert |
| `actionbar.json` korrupt | `load_with_failsafe` → Backup laden | Letzte gute Konfiguration |
| Backup auch korrupt | `return []` + `logger.error` | Leere Actionbar |
| Einzelner Knoten ungültig | `logger.warning` + `continue` | Knoten wird übersprungen |
| `source_id` referenziert nicht-existente Action | Node wird angezeigt, aber `enabled=False` | Ausgegraut mit Tooltip |
| `actionbar_state.json` fehlt/korrupt | Default-State | Alles geschlossen, keine Pins |

### 7.2 Speicher-Fehler

| Szenario | Behandlung | User sieht |
|---|---|---|
| Schema-Validation scheitert | `ConfigValidationError` → Dialog | Fehlermeldung mit Details |
| Backup-Erstellung schlägt fehl | `logger.error`, Speichern wird trotzdem versucht | Warnung im Log |
| Schreibfehler (Berechtigung) | `return False` + `logger.error` | Fehlermeldung im Dialog |
| Doppelte IDs nach Bearbeitung | Validation blockiert Speichern | "Doppelte ID: ..." Meldung |

### 7.3 Laufzeit-Fehler

| Szenario | Behandlung | User sieht |
|---|---|---|
| Action-Trigger wirft Exception | `try/except` im Launcher + `logger.error` | Toast/Status-Meldung |
| Externes Programm nicht gefunden | Whitelist + `FileNotFoundError` fangen | "Programm nicht gefunden" |
| Automation-Chain bricht ab | Jeder Schritt einzeln abgesichert | Teilstatus + Fehlermeldung |
| UI-Widget-Crash im Slideout | `try/except` um Paint/Layout + `logger.error` | Panel schließt sich, Toolbar bleibt |

---

## 8. Sicherheitskonzept

### 8.1 Externe Programmausführung (source_kind="external")

```python
class AutomationLauncher:
    # Whitelist wird aus Config geladen, nicht hardcoded
    WHITELIST_FILE = "config/external_whitelist.json"
    
    def launch_external(self, program_path: str, args: list[str]) -> None:
        """Startet externes Programm NUR wenn auf Whitelist."""
        if not self._is_whitelisted(program_path):
            raise PermissionError(f"Programm nicht erlaubt: {program_path}")
        
        # NIEMALS shell=True
        # NIEMALS ungeprüfte Pfade
        # IMMER absolute Pfade nach Normalisierung
        resolved = Path(program_path).resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Programm nicht gefunden: {resolved}")
        
        # Subprocess async starten, UI nicht blockieren
        # ...
```

### 8.2 Input-Sanitierung

Alle Benutzereingaben durchlaufen `ConfigValidator`:
- IDs → `validate_id()` (Regex `^[a-zA-Z][a-zA-Z0-9_]*$`, max 64)
- Namen/Labels → `validate_name()` (entfernt `<>:"/\|?*`, max 128)
- Farben → Regex `^(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8}|)$`
- Keine Injection-Vektoren in JSON-Werten möglich (kein `eval`, kein Template-Rendering)

### 8.3 Zirkelreferenz-Schutz

```python
def _validate_no_cycles(self, nodes: list[ActionbarNode]) -> list[str]:
    """Erkennt Zirkelreferenzen im Baum."""
    seen: set[str] = set()
    errors: list[str] = []
    
    def walk(node: ActionbarNode, path: list[str]) -> None:
        if node.id in seen:
            errors.append(f"Zirkelreferenz: {' → '.join(path)} → {node.id}")
            return
        seen.add(node.id)
        for child in node.children:
            walk(child, [*path, node.id])
    
    for node in nodes:
        walk(node, [])
    
    return errors
```

---

## 9. UI-Zustandsdiagramm

```
          ┌──────────────┐
          │  COLLAPSED    │◀─────────────── Klick außerhalb
          │  (nur Root-   │                 oder ESC
          │   Items)      │
          └──────┬───────┘
                 │ Klick auf FolderChip
                 ▼
          ┌──────────────┐
          │  SLIDEOUT     │──── Klick auf Action ──→ [Action ausführen]
          │  OPEN         │                          → zurück zu COLLAPSED
          │  (Panel mit   │
          │   Grid/Liste) │──── Suche tippen ──→ Gefilterte Liste
          │               │
          │               │──── Klick auf Sub-Folder ──→ SLIDEOUT (verschachtelt)
          └──────┬───────┘
                 │ Rechtsklick auf Node
                 ▼
          ┌──────────────┐
          │  CONTEXT MENU │──── "Bearbeiten" ──→ EditorDialog
          │               │──── "Entfernen" ──→ Confirm → entfernen
          │               │──── "Verschieben" ──→ DnD-Modus
          └──────────────┘
```

### Pin-Mechanismus

Gepinnte Actions werden **zusätzlich** als Root-Items angezeigt (Shortcut),
bleiben aber auch im Ordner. Pin-Status lebt in `actionbar_state.json`.

---

## 10. Migrationsstrategie

### 10.1 Erstbefüllung

Beim ersten Start ohne `actionbar.json`:

```python
def _generate_default_actionbar(self) -> list[ActionbarNode]:
    """Erzeugt Default-Actionbar aus bestehender toolbar.json."""
    toolbar_items = self.toolbar_factory.load_toolbars()
    nodes: list[ActionbarNode] = []
    
    for item in toolbar_items[0].items:
        if item.type == "separator":
            nodes.append(ActionbarNode(id=f"sep_{len(nodes)}", type="separator"))
        elif item.type == "action":
            nodes.append(ActionbarNode(
                id=item.action_id,
                type="action",
                source_kind="registry",
                source_id=item.action_id,
            ))
        # Menüs werden zu Ordnern
        elif item.type == "menu":
            nodes.append(ActionbarNode(
                id=item.menu_id,
                type="folder",
                label=item.label_key,
                icon=item.icon,
                slideout_direction="down",
            ))
    
    return nodes
```

### 10.2 Feature-Flag

```python
# In ui_config.json oder eigener Config:
{
    "actionbar": {
        "enabled": false,       # Deaktiviert in Phase 1
        "mode": "classic"       # "classic" | "actionbar" | "hybrid"
    }
}
```

- `classic`: Nur bestehende Toolbar aus `toolbar.json`
- `actionbar`: Neue verschachtelte Actionbar aus `actionbar.json`
- `hybrid`: Beides sichtbar (Entwicklungsmodus)

### 10.3 Versionsfeld

`actionbar.json` enthält `"version": 1`. Bei Schemaänderungen:
- Version erhöhen
- Migrationsfunktion `_migrate_v1_to_v2()` schreiben
- Alte Datei automatisch upgraden, Backup vorher

---

## 11. Phasenplan mit Quality Gates

### Phase 1 – Fundament (M1)

**Scope:** Datenmodell + Store + Schema + Tests

| Aufgabe | Datei | Quality Gate |
|---|---|---|
| `ActionbarNode` Dataclass | `factories/actionbar_factory.py` | mypy strict, `__post_init__`-Tests |
| `ActionbarStore` (load/save) | `factories/actionbar_factory.py` | `load_with_failsafe`, `save_with_backup` |
| `actionbar.schema.json` | `schemas/` | Gegen Beispiel-Config validiert |
| Default-Befüllung aus `toolbar.json` | `factories/actionbar_factory.py` | Round-trip-Test |
| Unit-Tests | `tests/test_actionbar_factory.py` | Coverage ≥ 80% |
| Backup-Tests | `tests/test_actionbar_validation.py` | Corrupt-Fallback, Backup-Restore |

Gate: `ruff check`, `mypy`, `pytest`, Import ohne Traceback

### Phase 2 – UI-Basis (M2)

**Scope:** Sichtbare Actionbar mit Ordnern

| Aufgabe | Datei | Quality Gate |
|---|---|---|
| `ActionbarView` Widget | `ui/actionbar_view.py` | Zeigt Root-Items, reagiert auf Klick |
| `FolderChip` Widget | `ui/actionbar_folder_chip.py` | Icon + Farbrand + Badge |
| `ActionButtonCard` Widget | `ui/actionbar_button_card.py` | Icon + Label + Trigger |
| `SlideoutPanel` | `ui/actionbar_slideout.py` | Öffnet/schließt, Grid-Layout |
| Integration in MainWindow | `core/main.py` | Feature-Flag, kein Bruch der klassischen Toolbar |
| `AutomationLauncher` | `core/automation_launcher.py` | Registry/Custom-Dispatch |

Gate: Start Main + Demo ohne Traceback, Feature-Flag funktioniert

### Phase 3 – Editor und DnD (M3)

**Scope:** Benutzerkonfiguration

| Aufgabe | Datei | Quality Gate |
|---|---|---|
| `ActionbarEditorDialog` | `ui/actionbar_editor_dialog.py` | CRUD für Folders + Actions |
| DnD innerhalb Actionbar | `ui/actionbar_view.py` | Reorder, Folder-Drop |
| Farb-/Icon-Auswahl | `ui/actionbar_editor_dialog.py` | Picker-Widget |
| Automatisches Gruppieren | `factories/actionbar_factory.py` | Nach Kategorie/Tags |

Gate: Editor-Save → Schema-gültige `actionbar.json`, DnD-Persistenz-Test

### Phase 4 – Automation und Module (M4)

**Scope:** Programme und Workflows starten

| Aufgabe | Datei | Quality Gate |
|---|---|---|
| `source_kind="external"` Support | `core/automation_launcher.py` | Whitelist, kein `shell=True` |
| `source_kind="module"` Support | `core/automation_launcher.py` | Modul-Loader, Fehlerbehandlung |
| `source_kind="automation"` Rezepte | `core/automation_launcher.py` | Schrittweise Ausführung |
| Batch-Erstellung aus Registry | `factories/actionbar_factory.py` | Erzeugt Folder pro Kategorie |

Gate: Security-Review (Bandit), kein externer Start ohne Whitelist

### Phase 5 – Polish und Thumbnails (M5)

**Scope:** Visuelle Verfeinerung

| Aufgabe | Datei | Quality Gate |
|---|---|---|
| Miniaturansichten (statisch) | `ui/actionbar_button_card.py` | Icon + Farbmarker + Badge |
| Animiertes Slide-out | `ui/actionbar_slideout.py` | Smooth open/close |
| Snapshot-Provider (optional) | `ui/actionbar_thumbnail_provider.py` | Pro Modultyp |
| Performance-Test | Tests | ≤ 50ms für 200 Nodes |

Gate: Kein UI-Lag bei >150 Actions, Pylint ≥ 9.0

---

## 12. Testplan

### 12.1 Unit-Tests (`test_actionbar_factory.py`)

```python
# Validierung
def test_node_type_invalid_raises_value_error() -> None: ...
def test_node_id_empty_raises_value_error() -> None: ...
def test_node_id_sanitized_by_validator() -> None: ...
def test_node_max_depth_clamped() -> None: ...
def test_node_preview_count_clamped() -> None: ...
def test_node_color_invalid_fallback() -> None: ...

# Persistenz
def test_load_empty_file_returns_empty_list() -> None: ...
def test_load_missing_file_returns_empty_list() -> None: ...
def test_load_corrupt_file_falls_back_to_backup() -> None: ...
def test_save_creates_backup_first() -> None: ...
def test_save_validates_schema_before_write() -> None: ...
def test_round_trip_preserves_all_fields() -> None: ...
def test_round_trip_preserves_nested_children() -> None: ...

# Baum-Integrität
def test_no_duplicate_ids_in_tree() -> None: ...
def test_max_nesting_depth_enforced() -> None: ...
def test_no_circular_references() -> None: ...

# Cross-Referenz
def test_source_id_registry_action_exists() -> None: ...
def test_source_id_custom_action_exists() -> None: ...
def test_missing_source_id_sets_disabled() -> None: ...

# Migration
def test_default_from_toolbar_json() -> None: ...
def test_version_migration_v1_to_v2() -> None: ...
```

### 12.2 Validierungs-Tests (`test_actionbar_validation.py`)

```python
# Schema
def test_schema_rejects_missing_version() -> None: ...
def test_schema_rejects_unknown_type() -> None: ...
def test_schema_rejects_invalid_color_format() -> None: ...
def test_schema_accepts_empty_nodes() -> None: ...

# Backup
def test_backup_created_on_save() -> None: ...
def test_backup_cleanup_keeps_max_5() -> None: ...
def test_failsafe_restores_from_backup() -> None: ...
def test_failsafe_both_corrupt_returns_empty() -> None: ...

# Sanitierung
def test_sanitize_strips_dangerous_chars_from_labels() -> None: ...
def test_sanitize_prefixes_numeric_ids() -> None: ...
def test_sanitize_replaces_reserved_names() -> None: ...
```

### 12.3 Integration-Tests

```python
# UI
def test_actionbar_view_loads_and_displays_nodes() -> None: ...
def test_folder_chip_click_opens_slideout() -> None: ...
def test_slideout_close_on_outside_click() -> None: ...
def test_action_trigger_calls_registry() -> None: ...

# DnD
def test_drag_action_to_folder() -> None: ...
def test_drag_action_out_of_folder() -> None: ...
def test_reorder_within_folder() -> None: ...
def test_dnd_persists_after_drop() -> None: ...

# Regression
def test_classic_toolbar_still_works() -> None: ...
def test_feature_flag_switches_mode() -> None: ...
def test_action_registry_unchanged() -> None: ...
```

---

## 13. Entscheidungslog

| # | Entscheidung | Begründung | Alternative |
|---|---|---|---|
| E1 | Separate `actionbar.json`, nicht in `toolbar.json` | Keine Breaking Changes, klassische Toolbar bleibt | Toolbar erweitern → risikoreicher |
| E2 | Max 3 Ebenen Verschachtelung | UX-Forschung zeigt: >3 Ebenen verwirrt | Unbegrenzt → schlecht für Touch/UX |
| E3 | `ConfigValidator` Pflicht für alle Stores | Bestehende Infrastruktur nutzen, Konsistenz | Eigene Validation → Duplizierung |
| E4 | Feature-Flag für Umschaltung | Risikoarme Einführung, Rollback möglich | Harter Switch → gefährlich |
| E5 | `actionbar_state.json` ohne Backup | Regenerierbar, kein Datenverlust | Mit Backup → unnötiger Overhead |
| E6 | Graceful Degradation bei fehlender Config | Konsistent mit Action/Toolbar/Theme-Factory | FileNotFoundError → User-Crash |
| E7 | Whitelist für externe Programme | OWASP: keine ungeprüfte Ausführung | Blacklist → unsicher |
| E8 | Kein `shell=True` bei subprocess | Command-Injection verhindern | Shell-Nutzung → Sicherheitslücke |
| E9 | Version-Feld in Config | Migrationssupport bei Schema-Änderungen | Ohne Version → Breaking Changes |
| E10 | Logging statt print() | Konsistenz mit modernen Factories | print() → nicht filterbar |

---

## 14. Offene Fragen (vor Implementierung zu klären)

| # | Frage | Empfehlung |
|---|---|---|
| F1 | Soll die Actionbar auch vertikal (als Sidebar) darstellbar sein? | Phase 2+ als Option |
| F2 | Sollen Folder-Inhalte per Drag auch zwischen Fenstern verschiebbar sein? | Nein in Phase 1, optional später |
| F3 | Wie werden Automations-Rezepte definiert? Eigenes Schema oder Teil von actionbar? | Eigenes Schema `config/automations.json` |
| F4 | Soll es einen "Papierkorb"-Ordner für gelöschte Actions geben? | Ja, als Soft-Delete mit Undo |
| F5 | Soll die Actionbar im Kontext der Dock-Areas leben (pro Area eine Actionbar)? | Nein, eine zentrale Actionbar |
| F6 | Maximale Anzahl Root-Items bevor horizontales Scrollen einsetzt? | ~15 Items, dann Overflow-Menü |
| F7 | Soll die Actionbar Keyboard-Navigation unterstützen (Pfeiltasten)? | Ja, ab Phase 3 |

---

## Anhang A: Bestehende Validierungsregeln-Referenz

Zusammengestellt aus der Codebase-Analyse:

| Modul | Pattern | Angewendet auf |
|---|---|---|
| `ConfigValidator.validate_id()` | `^[a-zA-Z][a-zA-Z0-9_]*$`, max 64 | ActionbarNode.id |
| `ConfigValidator.validate_name()` | Entfernt `<>:"/\|?*`, max 128 | ActionbarNode.label |
| `ConfigValidator.validate_structure()` | Required/Optional/Unknown fields, Tiefe ≤ 5 | Gesamte actionbar.json |
| `ConfigValidator.sanitize_config()` | Rekursiv über id/name/label | Import/Migration |
| `ConfigValidator.load_with_failsafe()` | JSON-Parse → Backup → Error | Laden |
| `ConfigValidator.save_with_backup()` | Backup → Schema-Check → Write | Speichern |
| `ActionbarNode.__post_init__()` | Enum-Prüfung, Clamping, Fallbacks | Jeder geparste Knoten |
| Cross-Reference | source_id existiert in Registry/Custom | Nach dem Laden |
| Zirkel-Check | `seen`-Set über Baum-Walk | Nach dem Laden |
| Duplikat-Check | Alle IDs im Baum eindeutig | Nach dem Laden und vor Speichern |
