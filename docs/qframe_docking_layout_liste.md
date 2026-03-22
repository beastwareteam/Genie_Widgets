# QFRAME — DOCKING LAYOUT LISTE
> Factory-basiert · Kein Hardcode · Kompatibel mit MVP-Mechanik
> Aufbauend auf: FloatingManager + DockSplitter + Persistenz

---

## 0. KERNFRAGE: WAS IST EINE "DOCKING LAYOUT LISTE"?

```
Eine Docking Layout Liste ist eine zur Laufzeit verwaltete,
serialisierbare Beschreibung aller gedockten Zustände.

Sie beantwortet jederzeit:
  • Welche Widgets existieren?
  • Welche sind frei (floating)?
  • Welche sind gedockt (in welcher Gruppe, welcher Position)?
  • Wie ist jede Gruppe aufgeteilt (Splitter-Verhältnis)?
  • Wie heißen gespeicherte Layout-Vorlagen?

Sie ist KEIN visuelles Widget.
Sie ist KEIN hardcodiertes Array.
Sie ist eine lebende Datenstruktur die vom DockManager
verwaltet und vom LayoutRegistry gespeichert wird.
```

---

## 1. SCHICHTEN DER DOCKING LAYOUT LISTE

```
┌─────────────────────────────────────────────────────┐
│  SCHICHT 3 — LAYOUT REGISTRY                        │
│  Benannte Snapshots: "default", "debug", "focus"    │
│  Laden / Speichern / Als Standard setzen             │
├─────────────────────────────────────────────────────┤
│  SCHICHT 2 — LAYOUT SNAPSHOT                        │
│  Vollständiger Zustand zu einem Zeitpunkt           │
│  Serialisierbar → JSON                               │
├─────────────────────────────────────────────────────┤
│  SCHICHT 1 — DOCK STATE (lebendig)                  │
│  FloatingManager.get_state() → aktueller Zustand    │
│  Wird bei jedem Dock/Undock/Move aktualisiert        │
└─────────────────────────────────────────────────────┘
```

---

## 2. DATENMODELL — VOLLSTÄNDIG, KEIN HARDCODE

### 2.1 WidgetEntry (ein einzelnes Widget)

```
WidgetEntry (dataclass):
  widget_id     : str           "widget_1"
  label         : str           benutzerdefinierbarer Name
  state         : str           "free" | "docked" | "minimized" | "hidden"
  x             : int           Canvas-Position (nur wenn free)
  y             : int
  width         : int
  height        : int
  group_id      : str | None    falls docked: welche Gruppe
  group_index   : int | None    Position innerhalb der Gruppe
  content_type  : str | None    was ist drin (für Factory-Befüllung)
  content_state : dict          Zustand des Inhalts (für Persistenz)
  pinned        : bool          kann nicht geschlossen werden
  locked        : bool          kann nicht verschoben werden
```

### 2.2 GroupEntry (eine Dock-Gruppe)

```
GroupEntry (dataclass):
  group_id      : str           "group_1"
  orientation   : str           "H" | "V"
  x             : int           Canvas-Position
  y             : int
  width         : int
  height        : int
  sizes         : list[int]     Splitter-Verhältnisse
  members       : list[str]     geordnete widget_ids
  parent_group  : str | None    für verschachtelte Gruppen
  parent_index  : int | None
```

### 2.3 LayoutSnapshot (vollständiger Zustand)

```
LayoutSnapshot (dataclass):
  snapshot_id   : str           "snap_20240224_143012" (auto)
  name          : str           "Standard" / "Debug" / "Fokus"
  created_at    : str           ISO-Timestamp
  description   : str           optional
  widgets       : dict[str, WidgetEntry]
  groups        : dict[str, GroupEntry]
  counter       : int           aktueller widget_id-Zähler
  canvas_size   : tuple[int,int] (w, h) zum Zeitpunkt der Aufnahme
  window_state  : dict          Fenster-Position + Größe

  Methoden:
    to_dict() → dict       für JSON-Serialisierung
    from_dict(d) → cls     Klassenmethode für Deserialisierung
    diff(other) → list     Liste von Unterschieden zu anderem Snapshot
```

---

## 3. LAYOUT REGISTRY — ZENTRALE VERWALTUNG

```
Klasse: LayoutRegistry

  Zweck:
    Verwaltet alle benannten Layout-Snapshots.
    Kennt den "aktiven" Snapshot.
    Liest/Schreibt eine einzige JSON-Datei.
    Kein UI. Kein Qt. Nur Daten + Logik.

  Attribute:
    _snapshots   : dict[str, LayoutSnapshot]   name → snapshot
    _active_name : str | None
    _file_path   : str

  Methoden:

    capture(manager, name, description="") → LayoutSnapshot
      • Ruft manager.get_full_state() auf
      • Erstellt LayoutSnapshot aus dem State
      • Speichert in _snapshots[name]
      • Gibt Snapshot zurück
      • Kein Überschreiben ohne confirm=True

    apply(name, manager) → bool
      • Lädt _snapshots[name]
      • Ruft manager.restore_state(snapshot) auf
      • Setzt _active_name = name
      • Gibt True zurück falls erfolgreich

    delete(name) → bool
      • Entfernt aus _snapshots
      • Falls _active_name == name: _active_name = None

    rename(old, new) → bool

    list_snapshots() → list[SnapshotMeta]
      SnapshotMeta: name, created_at, description, widget_count, group_count

    save_to_file() → None
      • Serialisiert alle Snapshots als JSON
      • Atomar schreiben (temp-Datei → rename)

    load_from_file() → None
      • Liest JSON
      • Deserialisiert in LayoutSnapshot-Objekte

    get_autosave() → LayoutSnapshot | None
      • Gibt den "__autosave__" Snapshot zurück

    autosave(manager) → None
      • capture(manager, "__autosave__") ohne Nachfrage
      • Wird bei jedem Dock/Undock/Close aufgerufen
```

---

## 4. INTEGRATION IN FLOATINGMANAGER

```
FloatingManager bekommt eine LayoutRegistry Referenz.

Neue Attribute:
  self.layout_registry : LayoutRegistry

Neue Methoden:

  get_full_state() → dict
    Gibt vollständigen Zustand zurück:
    {
      "counter":  self._counter,
      "widgets":  { wid: fw.get_state() for wid, fw in self._widgets.items() },
      "groups":   { gid: grp.get_state() for gid, grp in self._groups.items() }
    }

  restore_state(snapshot: LayoutSnapshot | dict) → None
    Existierende Implementierung — funktioniert unverändert.
    Nimmt jetzt auch LayoutSnapshot entgegen (via snapshot.to_dict())

Autosave-Hooks (nach jeder Layout-Änderung):
  Nach _dock():         self.layout_registry.autosave(self)
  Nach remove_widget(): self.layout_registry.autosave(self)
  Nach end_drag():      self.layout_registry.autosave(self)
    ← nur wenn kein Drop (freie Position)
```

---

## 5. LAYOUT LISTE — DAS VISUELLE WIDGET

```
LayoutListWidget(QWidget)

Zweck:
  Zeigt alle gespeicherten Snapshots als scrollbare Liste.
  Jeder Eintrag: Name + Timestamp + Widget-Anzahl + Aktions-Buttons.
  Wird als FloatingWidget-Inhalt eingesetzt (fill()).
  Kein Hardcode — alle Einträge kommen aus LayoutRegistry.list_snapshots().

Aufbau:
  QVBoxLayout
  ├── Header (QHBoxLayout)
  │     ├── QLabel "Layouts"  (Titel)
  │     └── SaveButton "💾 Speichern"  → öffnet SaveDialog
  ├── ScrollArea
  │     └── ListContainer (QVBoxLayout)
  │           └── LayoutListItem × N   (pro Snapshot einer)
  └── Footer (QHBoxLayout)
        └── ImportButton "📂 Importieren"

LayoutListItem(QWidget):
  Enthält:
    active_indicator   QFrame  (2px blau, sichtbar wenn aktiv)
    name_label         QLabel  (Snapshot-Name)
    meta_label         QLabel  (Datum · N Widgets · M Gruppen, klein grau)
    apply_btn          QPushButton "Laden"
    delete_btn         QPushButton "✕"
    options_btn        QPushButton "⋯"  → Rename / Duplicate / Export

  Signale:
    apply_requested(name: str)
    delete_requested(name: str)
    rename_requested(name: str, new_name: str)

LayoutListWidget Methoden:
  refresh() → None
    • list_container leeren
    • LayoutRegistry.list_snapshots() abfragen
    • Für jeden Snapshot: LayoutListItem erstellen + einfügen

  _on_apply(name) → None
    • LayoutRegistry.apply(name, manager)
    • refresh()

  _on_delete(name) → None
    • Bestätigungs-Dialog (QMessageBox)
    • LayoutRegistry.delete(name)
    • refresh()

  _on_save() → None
    • SaveDialog öffnen (Abschnitt 6)
    • Nach OK: LayoutRegistry.capture(manager, entered_name)
    • refresh()
```

---

## 6. SAVE DIALOG — OHNE HARDCODE

```
LayoutSaveDialog(QDialog)

Zweck:
  Kleines Popup: Name + Beschreibung eingeben.
  Kein fester Inhalt — alles eingabebasiert.

Layout:
  QVBoxLayout
  ├── QLabel "Layout speichern"
  ├── QLineEdit  placeholder="Layout Name"     (self.name_input)
  ├── QLineEdit  placeholder="Beschreibung (optional)" (self.desc_input)
  └── QHBoxLayout
        ├── QPushButton "Abbrechen"
        └── QPushButton "Speichern"

Validierung:
  • Name darf nicht leer sein
  • Name darf nicht "__autosave__" sein (reserviert)
  • Falls Name bereits existiert: "Überschreiben?" Bestätigung

Ergebnis:
  dialog.exec() → int  (QDialog.Accepted / Rejected)
  dialog.get_name() → str
  dialog.get_description() → str
```

---

## 7. VORDEFINIERTE LAYOUT-VORLAGEN (FACTORY-BASIERT)

```
Vordefinierte Layouts werden NICHT hardcodiert eingebaut.
Sie werden als JSON-Dateien in einem templates/ Verzeichnis ausgeliefert.
LayoutRegistry lädt sie beim ersten Start einmalig ein.

templates/
  default.json         Leerer Canvas
  two_column.json      Zwei Widgets nebeneinander
  three_column.json    Drei Widgets nebeneinander
  top_bottom.json      Zwei Widgets übereinander
  quad.json            2×2 Raster
  focus_left.json      Großes Widget links + kleines rechts
  focus_right.json     Kleines links + großes rechts
  sidebar_left.json    Schmale Spalte links + breiter Bereich rechts
  sidebar_right.json   Breiter Bereich links + schmale Spalte rechts
  triple_v.json        Drei Zeilen übereinander

Format (Beispiel two_column.json):
{
  "name": "Zwei Spalten",
  "description": "Zwei gleichbreite Widgets nebeneinander",
  "is_template": true,
  "widgets": {
    "widget_1": { "widget_id": "widget_1", "state": "docked",
                  "group_id": "group_1", "group_index": 0,
                  "width": 300, "height": 400 },
    "widget_2": { "widget_id": "widget_2", "state": "docked",
                  "group_id": "group_1", "group_index": 1,
                  "width": 300, "height": 400 }
  },
  "groups": {
    "group_1": { "group_id": "group_1", "orientation": "H",
                 "x": 60, "y": 60, "width": 620, "height": 400,
                 "sizes": [310, 310],
                 "members": ["widget_1", "widget_2"] }
  },
  "counter": 2
}

LayoutRegistry.load_templates(templates_dir: str) → None
  • Liest alle .json Dateien im Verzeichnis
  • Lädt nur falls is_template == true
  • Fügt in _snapshots ein mit Prefix "template." + name
  • Templates können nicht überschrieben werden (read-only)
  • Templates erscheinen in LayoutListWidget unter eigenem Header
```

---

## 8. VOLLSTÄNDIGE DATENSTRUKTUR (JSON-Beispiel)

```json
{
  "active": "Mein Layout",
  "snapshots": {
    "__autosave__": {
      "snapshot_id": "snap_autosave",
      "name": "__autosave__",
      "created_at": "2024-02-24T14:30:12",
      "description": "Automatisch gespeichert",
      "counter": 3,
      "canvas_size": [1180, 740],
      "window_state": { "x": 50, "y": 50, "width": 1280, "height": 800 },
      "widgets": {
        "widget_1": {
          "widget_id": "widget_1", "label": "Widget 1",
          "state": "docked", "x": 0, "y": 0,
          "width": 300, "height": 400,
          "group_id": "group_1", "group_index": 0,
          "content_type": null, "content_state": {},
          "pinned": false, "locked": false
        },
        "widget_2": {
          "widget_id": "widget_2", "label": "Widget 2",
          "state": "docked", "x": 0, "y": 0,
          "width": 300, "height": 400,
          "group_id": "group_1", "group_index": 1,
          "content_type": null, "content_state": {},
          "pinned": false, "locked": false
        },
        "widget_3": {
          "widget_id": "widget_3", "label": "Widget 3",
          "state": "free", "x": 700, "y": 200,
          "width": 300, "height": 200,
          "group_id": null, "group_index": null,
          "content_type": null, "content_state": {},
          "pinned": false, "locked": false
        }
      },
      "groups": {
        "group_1": {
          "group_id": "group_1", "orientation": "H",
          "x": 60, "y": 60, "width": 620, "height": 400,
          "sizes": [310, 310],
          "members": ["widget_1", "widget_2"],
          "parent_group": null, "parent_index": null
        }
      }
    },
    "Mein Layout": {
      "snapshot_id": "snap_20240224_141500",
      "name": "Mein Layout",
      "created_at": "2024-02-24T14:15:00",
      "description": "Mein bevorzugtes Arbeits-Layout"
      // ... gleiche Struktur wie __autosave__
    }
  }
}
```

---

## 9. NEUE DATEIEN FÜR DEN AGENT

```
qframe_mvp/
├── persistence.json              ← jetzt: nur window-state + active layout name
├── layouts.json                  ← NEU: alle LayoutSnapshots
├── templates/
│   ├── default.json
│   ├── two_column.json
│   ├── three_column.json
│   ├── top_bottom.json
│   ├── quad.json
│   ├── focus_left.json
│   ├── focus_right.json
│   ├── sidebar_left.json
│   ├── sidebar_right.json
│   └── triple_v.json
│
└── qframe/
    ├── layout_registry.py        ← NEU: LayoutRegistry + LayoutSnapshot + SnapshotMeta
    ├── layout_list_widget.py     ← NEU: LayoutListWidget + LayoutListItem + LayoutSaveDialog
    ├── floating_manager.py       ← ERWEITERN: get_full_state(), autosave-Hooks
    ├── floating_widget.py        ← ERWEITERN: WidgetEntry-Daten (label, pinned, locked)
    └── persistence.py            ← VEREINFACHEN: nur window-state, layouts in layouts.json
```

---

## 10. INTEGRATION: LAYOUT LISTE ALS FLOATING WIDGET

```
Die LayoutListWidget wird als Inhalt eines FloatingWidget geöffnet.
Kein separates Fenster. Keine hardcodierte Sidebar.

Aufruf:
  Neuer Button in TitleBar: "☰ Layouts"
  Klick → FloatingManager.create_floating_widget(content_type="layout_list")

  In FloatingManager.create_floating_widget():
    fw = FloatingWidget(widget_id, canvas, self)
    if content_type == "layout_list":
        list_widget = LayoutListWidget(self.layout_registry, self)
        fw.fill(list_widget)
        fw.inlay_bar.set_label("Layouts")
    ...

  LayoutListWidget kennt:
    • layout_registry → um Snapshots zu lesen/schreiben
    • manager         → um apply()/capture() aufzurufen

WICHTIG: LayoutListWidget ist nur ein weiteres floating Widget.
  Es kann gedockt, verschoben, geschlossen werden wie jedes andere.
  Kein Sonderfall. Keine hardcodierte Position.
```

---

## 11. QUALITÄTSKRITERIEN

```
LAYOUT LISTE:
  □ "☰ Layouts" Button in TitleBar öffnet FloatingWidget mit Liste
  □ Liste zeigt: "__autosave__" + alle benannten Snapshots + Templates
  □ Jeder Eintrag: Name + Datum + N Widgets + M Gruppen
  □ "Laden" → Layout wird sofort angewendet
  □ "💾 Speichern" → SaveDialog → Name eingeben → in Liste
  □ "✕" an Eintrag → Bestätigung → Eintrag verschwindet
  □ Templates erscheinen unter eigenem Header, kein "✕" Button

AUTOSAVE:
  □ Nach jedem Dock-Vorgang: __autosave__ aktualisiert
  □ Nach closeEvent: __autosave__ aktualisiert
  □ Neustart: __autosave__ wird geladen

PERSISTENZ:
  □ layouts.json enthält alle Snapshots
  □ Snapshot-Inhalt entspricht JSON-Beispiel (Abschnitt 8)
  □ Templates aus templates/*.json laden ohne Fehler
  □ Benannte Snapshots überleben Neustart

FACTORY:
  □ Kein Layout-Name ist irgendwo im Code fest eingetragen
  □ Neue Templates durch Hinzufügen von JSON-Dateien in templates/
  □ LayoutRegistry.list_snapshots() ist die einzige Datenquelle der Liste
  □ LayoutListWidget hat kein "if name == 'debug'" oder ähnliches
```
