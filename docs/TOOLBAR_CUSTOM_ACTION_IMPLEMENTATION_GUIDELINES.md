# Toolbar Custom Actions - Implementierungsrichtlinien

## Zielbild

Diese Richtlinie beschreibt die Übernahme der Demo-Features in die Main App mit klaren Architekturgrenzen, Quality Gates und Testkriterien.

## Funktionsumfang (Muss)

- Panel-lokale Toolbar-Buttons mit eigener Objekt-ID
- Bindung eines Buttons auf:
  - Registry-Action (`ActionRegistry`)
  - Custom Runtime-Action (eigene `custom.*` ID)
- Ein gemeinsames Bearbeitungsmodal für:
  - Beschriftung
  - Icon-Auswahl
  - Action-Bindung
  - Separator-Anordnung (links/rechts/beide/keine)
  - Toolbar-Icongröße (Pixel)
- Drag-and-Drop-Switching innerhalb der Toolbar (inkl. Separatoren)
- Linker DnD-Griff an der Toolbar bleibt erhalten
- Slide-/Scroll-fähige Auswahllisten im Modal (kompakt + filterbar)

## Architekturvorgaben

### 1) Schichten

- `ActionFactory`: statische JSON-Definitionen (config/actions.json)
- `ActionRegistry`: zentrale QAction-Erzeugung und Handler-Bindung
- `PanelToolbarLayer` (neu, logisch):
  - Proxy-Actions pro Panel-Toolbar-Objekt
  - Objektmetadaten (`object_id`, `source_action_kind`, `source_action_id`)
  - Separator-Owner-Metadaten
- `CustomActionStore` (neu, logisch):
  - Persistente Custom-Action-Definitionen (`config/custom_actions.json`)
  - Laufzeit-Instanzen (`QAction`)

### 2) ID-Konventionen

- Panel-Objekt: `panel_toolbar_object_<int>`
- Custom Action: `custom.<name>` (z. B. `custom.export_pdf`)
- Keine Leerzeichen, nur `[a-zA-Z0-9._-]`

### 3) Datenschema (Custom Actions)

Datei: `config/custom_actions.json`

- `id: str`
- `name: str`
- `label: str`
- `message: str`
- `icon: str`
- `description: str`
- `enabled: bool`

Schema: `schemas/custom_actions.schema.json`

## Integrationsregeln für Main App

1. **Keine Logikduplikate**
   - Handler weiter zentral in `ActionRegistry`
   - Panel-Toolbar nutzt Proxy-Actions und delegiert Trigger

2. **Separator-Verhalten**
   - Separatoren sind eigene `QAction`-Elemente
   - Separator-Metadaten über `separator_owner` + `separator_side`
   - Reorder via DnD darf Separatoren mitbewegen

3. **Toolbar-Griff links**
   - `QToolBar.setMovable(True)` aktiv lassen
   - Linke Griffzone nicht durch Custom-Widget überdecken

4. **DnD-Switching innerhalb Toolbar**
   - Drop auf Action => Positionswechsel (Switch)
   - Drop auf freie Fläche => ans Ende
   - Nach jeder Strukturänderung: UI-Refresh + Slide-Button-State aktualisieren

5. **Modal-UX kompakt halten**
   - Filterfelder für Action/Icon-Liste
   - Listenhöhe begrenzen
   - Page-Slide-Buttons `▲/▼`

## Quality Gates (Pflicht)

Vor Merge in Main App müssen alle Gates grün sein:

1. **Lint/Format**
   - `ruff check src/`
   - `ruff format --check src/`

2. **Typing**
   - `mypy src/`

3. **Tests**
   - `pytest tests/ -q`
   - betroffene Testsuite muss für Toolbar/Action bestehen (siehe Testkatalog)

4. **Runtime Checks**
   - Start Main App ohne Traceback
   - Start Demo ohne Traceback

5. **Config/Schema Konsistenz**
   - `config/custom_actions.json` validiert gegen `schemas/custom_actions.schema.json`

## Testkatalog

### A) Unit-Tests

- Custom Action Registrierung
  - neue `custom.*` ID erzeugt `QAction`
  - Duplicate-ID überschreibt deterministisch oder wird blockiert (Projektentscheidung dokumentieren)
- Persistenz
  - speichern/laden round-trip ohne Datenverlust
- Binding
  - Proxy triggert Registry-Action korrekt
  - Proxy triggert Custom-Action korrekt
- Separator-Logik
  - links/rechts/beide/none korrekt gesetzt
  - Owner-separators werden korrekt entfernt/neu gesetzt

### B) UI-Integrationstests

- Modal
  - ein Dialog ändert Text + Icon + Binding + Separator + Pixelgröße
- Icon-Konsistenz
  - Binding-Liste und Icon-Liste zeigen konsistente Vorschauen
- Kompaktheit
  - Listen bleiben in begrenzter Höhe, Scroll/Page-Slide funktioniert

### C) DnD-Tests

- Drag Action -> Drop auf Zielaction => Switch
- Drag Separator -> Drop auf Zielaction => Switch
- Drag -> freie Fläche => Move ans Ende
- Nach DnD bleiben Trigger und Metadaten intakt

### D) Regression

- Standard-Toolbar aus `toolbar.json` weiterhin funktionsfähig
- Bestehende Menü-/Kontextmenü-Actionbindungen unverändert

## Nicht-funktionale Anforderungen

- Keine blockierenden Dialogketten
- Keine UI-Lags bei >150 Action-Optionen
- Modal bleibt bei Standard-DPI unterhalb der Bildschirmhöhe

## Migrationsplan (Demo -> Main)

1. PanelToolbarLayer als eigenes Modul extrahieren
2. CustomActionStore als eigenes Modul extrahieren
3. Modal als wiederverwendbaren Editor-Dialog auslagern
4. MainWindow-Hooks für Dock/Toolbar registrieren
5. Tests + Quality Gates aktivieren

## Abnahmekriterien

Feature gilt als abgenommen, wenn:

- alle Pflichtfunktionen vorhanden sind
- alle Quality Gates grün sind
- alle DnD- und Persistenzfälle reproduzierbar bestehen
- kein Bruch der bestehenden Standardtoolbar-Pfade auftritt
