# Master-Roadmap & Regression-Checkliste (Source of Truth)

Stand: 2026-03-23  
Ziel: Eine zentrale, agentenlesbare Referenz für Ist-Zustand, geplante Arbeit und verpflichtende Regressionstests.

---

## 1) Zweck und Geltungsbereich

Dieses Dokument ist die zentrale Steuerdatei für:
- vollständige Projekt-Bestandaufnahme,
- priorisierte Roadmap (Phasen/Prioritäten),
- verbindliche Regression-Checkliste nach Änderungen.

Es gilt für alle Bereiche des Projekts:
- Codebasis: [src/widgetsystem](src/widgetsystem)
- Tests: [tests](tests)
- Konfiguration: [config](config)
- Schemas: [schemas](schemas)
- Themes/Stylesheets: [themes](themes)
- Laufzeit-Daten: [data](data)
- Dokumentation: [docs](docs)
- Qualitäts-Skripte: [scripts](scripts)
- Demo-Anwendungen: [examples](examples)
- Archiv (explizit ausgeschlossen): [archive](archive) — enthält veraltete/archivierte Dateien, nicht im aktiven Geltungsbereich
- Historische Struktur-Referenz: [PROJECT_STRUCTURE_VERIFICATION.md](PROJECT_STRUCTURE_VERIFICATION.md)

### 1.1 Schnellnavigation (1-Seiten-Ansicht)

Direktzugriffe auf die fehlerorientierten Detailregister:
- [Core-Detailregister (7.2.1)](#721-core-detailregister-lesbar-sortiert-fehlerklar)
- [Controller-Detailregister (7.3.1)](#731-controller-detailregister-lesbar-sortiert-fehlerklar)
- [Factory-Detailregister (7.4.1)](#741-factory-detailregister-lesbar-sortiert-fehlerklar)
- [UI-Detailregister (7.5.1)](#751-ui-detailregister-lesbar-sortiert-fehlerklar)
- [Config/Schema-Detailregister (7.6.1)](#761-configschema-detailregister-lesbar-sortiert-fehlerklar)
- [Pflicht-Regression je Kernfeature (8.6)](#86-pflicht-regression-je-kernfeature-mindestumfang)

Was tun bei Fehlerverdacht? (5 Schritte)
1. Betroffenen Layer wählen (Core/Controller/Factory/UI/Config).
2. Feature-ID in der Schnellübersicht des Layers bestimmen.
3. Fehlercode (`E-...`) im Layer-Register nachschlagen.
4. Zugehörigen Test ausführen (zuerst spezifisch, dann breiter).
5. Matrixstatus (`Verify`, `Risiko`) und Dokumentationsstand aktualisieren.

---

## 2) Normative Referenzen (festgeschrieben)

Bei Konflikten gilt folgende Reihenfolge:
1. Projektregeln in [AGENT_CONFIG.md](AGENT_CONFIG.md)
2. Agentenregeln in [AGENTS.md](AGENTS.md)
3. Copilot-Regeln in [.github/copilot-instructions.md](.github/copilot-instructions.md)
4. Bereichsspezifische Regeln in [.github/instructions](.github/instructions)

Bereichsspezifisch:
- Factories: [.github/instructions/factories.instructions.md](.github/instructions/factories.instructions.md)
- UI/Core: [.github/instructions/ui-components.instructions.md](.github/instructions/ui-components.instructions.md)
- Tests: [.github/instructions/testing.instructions.md](.github/instructions/testing.instructions.md)
- JSON/Schemas: [.github/instructions/json-config.instructions.md](.github/instructions/json-config.instructions.md)

---

## 3) Statusmodell (verbindlich)

Jedes Feature erhält drei Statusachsen:

- Implementierungsstatus:
  - Planned
  - In Progress
  - Implemented

- Verifikationsstatus:
  - Untested
  - Partially Tested
  - Verified

- Governance-Status:
  - Not Reviewed
  - Compliant
  - Exception Approved

Abschlusskriterium eines Features:
- Implemented + Verified + Compliant

---

## 4) Prioritätsmodell (Roadmap)

- P0 Kritisch: Betrieb/Regression/Build-Stabilität
- P1 Hoch: Kernfunktionalität und Nutzerfluss
- P2 Mittel: Komfort/Erweiterungen
- P3 Optional: Nice-to-have, experimentell

---

## 5) Hierarchische Bestandsaufnahme (Ist)

### 5.1 Architektur-Layer

- Governance/Qualität
  - Regeln: [AGENT_CONFIG.md](AGENT_CONFIG.md), [AGENTS.md](AGENTS.md)
  - Qualitätslauf: [scripts/check_quality.py](scripts/check_quality.py)

- Core
  - Module in [src/widgetsystem/core](src/widgetsystem/core)
  - Architektur: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

- Controller
  - Module in [src/widgetsystem/controllers](src/widgetsystem/controllers)
  - Architektur: [docs/CONTROLLER_ARCHITECTURE.md](docs/CONTROLLER_ARCHITECTURE.md)

- Factory-System
  - Module in [src/widgetsystem/factories](src/widgetsystem/factories)
  - Architektur: [docs/FACTORY_SYSTEM.md](docs/FACTORY_SYSTEM.md)

- UI
  - Module in [src/widgetsystem/ui](src/widgetsystem/ui)

- Konfiguration
  - JSON in [config](config)
  - Schemas in [schemas](schemas)
  - `.backup`-Dateien ([config/lists.json.backup](config/lists.json.backup), [config/themes.json.backup](config/themes.json.backup)) werden im Backup-Kontext von [src/widgetsystem/core/config_io.py](src/widgetsystem/core/config_io.py) automatisch erzeugt und gehören nicht zur aktiven Konfiguration.

- Daten
  - Laufzeit-/Layoutdaten in [data](data)
  - `data/layouts.json` und `data/themes.json` sind veraltete Runtime-Kopien, archiviert 2026-03-23.

- Tests
  - Testmodule in [tests](tests)

### 5.2 Implementierte Hauptdomänen (gemäß Codebasis)

- Factory-Domäne:
  - Layout, Theme, Panel, Menu, Tabs, DnD, Responsive, I18n, List, UIConfig

- Controller-Domäne:
  - Dock, Layout, Theme, DnD, Responsive, Shortcut, TabSubsystem

- Core-Domäne:
  - Plugin-System, Undo/Redo, Config I/O, Template-System, Theme-Management, Gradient-System

- UI-Domäne:
  - Visual Layer/App, Konfigurationspanel, Titlebar-Subsystem, Theme-Editor, ARGB-Farbwahl,
    Widget-Feature-Editor

### 5.3 Konkrete Bestandsaufnahme: Funktionen & Features (fachlich)

Ziel dieser Sektion:
- klare Antwort auf „Welche Funktionen haben wir genau?“
- unabhängig von Dateipfaden direkt nutzbar für Planung, Regression und Abnahme

#### 5.3.1 Governance & Qualität (fachliche Funktionen)

| ID | Funktion (fachlich) |
|---|---|
| F-GOV-001 | Verbindliche Agenten-/Projektregel-Hierarchie zur einheitlichen Arbeitsausführung |
| F-GOV-002 | Bereichsspezifisches Instruction-Routing (Factories, UI/Core, Tests, JSON/Schemas) |
| F-QA-001 | Qualitäts-Gate-Orchestrierung für Linting, Typprüfung, Sicherheit und Tests |
| F-QA-002 | Automatisierte Verifikation der Agenten-/Instruktionskonfiguration |

#### 5.3.2 Core (fachliche Funktionen)

| ID | Funktion (fachlich) |
|---|---|
| F-CORE-001 | Startet und verwaltet den Hauptanwendungs-Lifecycle inklusive zentraler Initialisierung |
| F-CORE-002 | Betreibt die visuelle Hauptfenster-Variante für das GUI-System |
| F-CORE-003 | Registriert und verwaltet Plugins über ein zentrales Registry-Modell |
| F-CORE-004 | Bietet Undo/Redo über einen Command-Stack für rücknehmbare Aktionen |
| F-CORE-005 | Importiert/exportiert Konfigurationen inkl. Sicherungs- und Wiederherstellungslogik |
| F-CORE-006 | Stellt ein Template-System zur Wiederverwendung vordefinierter Konfigurationsmuster bereit |
| F-CORE-007 | Zentraler ThemeManager (Singleton) für Theme-Status und Signalverteilung |
| F-CORE-008 | Definiert Theme-Profile mit ARGB-Farbdaten und Profilserialisierung |
| F-CORE-009 | Verarbeitet Gradient-Definitionen für visuelle Farbverläufe |
| F-CORE-010 | Definiert typsichere EnumTypes für Bereiche, Aktionen, Regeln und Theme-Modi |

#### 5.3.3 Controller (fachliche Funktionen)

| ID | Funktion (fachlich) |
|---|---|
| F-CTRL-001 | Steuert Dock-Lifecycle (Erzeugen, Andocken, Schließen, Zustandswechsel) |
| F-CTRL-002 | Verwalten von Layout speichern/laden/zurücksetzen für reproduzierbare UI-Zustände |
| F-CTRL-003 | Anwenden und Neuladen von Themes auf laufende UI-Komponenten |
| F-CTRL-004 | Durchsetzen von Drag-and-Drop-Regeln für erlaubte Zielbereiche |
| F-CTRL-005 | Auswertung von Breakpoints für responsive Anpassungen im UI |
| F-CTRL-006 | Zuordnung und Ausführung von Aktionen über Shortcut-Steuerung |
| F-CTRL-007 | Integration des Tab-Subsystems (Zustand, Ereignisse, Sichtbarkeit) |

#### 5.3.4 Factory-System (fachliche Funktionen)

| ID | Funktion (fachlich) |
|---|---|
| F-FAC-001 | Lädt Layoutdefinitionen und löst Layout-Dateipfade auf |
| F-FAC-002 | Lädt Theme-Definitionen, Default-Theme, Stylesheets und Theme-Profile |
| F-FAC-003 | Lädt und validiert Paneldefinitionen inklusive DnD-/Responsive-Feldern |
| F-FAC-004 | Lädt rekursive Menüstrukturen mit Aktionen, Sichtbarkeit und Shortcuts |
| F-FAC-005 | Lädt Tab-Gruppen inkl. verschachtelter Tabs, Dock-Areas und Orientierung |
| F-FAC-006 | Lädt Drop-Zonen und DnD-Regelwerke inkl. Zielbereichsfreigaben |
| F-FAC-007 | Lädt Breakpoints und responsive Regeln für UI-Anpassungen |
| F-FAC-008 | Lädt Übersetzungen, unterstützt Locale-Wechsel und Key-Auflösung (flat/nested) |
| F-FAC-009 | Lädt/manipuliert Listenbäume (Gruppen/Items/Children) inkl. Persistenz |
| F-FAC-010 | Lädt dynamische UI-Konfigurationsseiten, Widgets und Property-Definitionen |

#### 5.3.5 UI (fachliche Funktionen)

| ID | Funktion (fachlich) |
|---|---|
| F-UI-001 | VisualApp-Wrapper für Anwendungseinbettung und visuelle Initialisierung |
| F-UI-002 | VisualLayer als zentrale Hauptoberfläche mit Panel-/Dockzusammenspiel |
| F-UI-003 | ConfigurationPanel als Laufzeit-Editor für konfigurierbare UI-Elemente |
| F-UI-004 | InlayTitleBar mit dynamischem Interaktionsverhalten (kompakt/erweitert) |
| F-UI-005 | FloatingTitlebar-Steuerung für Floating-/Dock-Übergänge |
| F-UI-006 | FloatingStateTracker zur Persistenz von Floating-Zuständen |
| F-UI-007 | TabColorController für tabbezogene Farbzustandslogik |
| F-UI-008 | TabSelectorMonitor zur Überwachung relevanter Tabzustände |
| F-UI-009 | TabSelectorEventHandler zur Eventverarbeitung im Tab-Selector-Fluss |
| F-UI-010 | TabSelectorVisibilityController für Sichtbarkeitsregeln des Tab-Selectors |
| F-UI-011 | ThemeEditor zur Live-Bearbeitung von Theme-Eigenschaften |
| F-UI-012 | ARGBColorPicker für Farbauswahl inklusive Alpha-Kanal |
| F-UI-013 | WidgetFeaturesEditor zur Bearbeitung von Widget-Feature-Eigenschaften |
| F-UI-014 | PluginManagerDialog zur UI-seitigen Verwaltung von Plugins |

#### 5.3.6 Config & Schema (fachliche Funktionen)

| ID | Funktion (fachlich) |
|---|---|
| F-CONF-001 | Layout-Konfigurationsmodell (Layoutliste + Standardlayout) |
| F-CONF-002 | Theme-Konfigurationsmodell (Theme-Liste + Defaults + Stylepfade) |
| F-CONF-003 | Panel-Konfigurationsmodell (Areas, Flags, responsive Metadaten) |
| F-CONF-004 | Menü-Konfigurationsmodell (hierarchische Menü-/Aktionsstruktur) |
| F-CONF-005 | Tab-Konfigurationsmodell (Gruppen, Tabs, Orientierung, Docking) |
| F-CONF-006 | DnD-Konfigurationsmodell (Drop-Zonen, Regeln, erlaubte Targets) |
| F-CONF-007 | Responsive-Konfigurationsmodell (Breakpoints, panelbezogene Aktionen) |
| F-CONF-008 | I18n-Konfigurationsmodell (Sprachdateien, Schlüsselräume, Texte) |
| F-CONF-009 | Listen-Konfigurationsmodell (Gruppen, Items, Nested-Strukturen) |
| F-CONF-010 | UIConfig-Konfigurationsmodell (Seiten, Widgets, Property-Typen) |

Interpretation für Regression:
- Diese Sektion beschreibt den fachlichen Bestand (Was ist implementiert).
- Die Detailregister 7.2.1 bis 7.6.1 beschreiben Fehlerbilder und Prüfpfade (Wie wird abgesichert).

---

## 6) Geplante/optionale Themen (Roadmap-Backlog)

Quelle für geplante bzw. optionale Punkte:
- [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)
- [docs/THEME_SYSTEM_GUIDE.md](docs/THEME_SYSTEM_GUIDE.md)
- [docs/THEME_IMPLEMENTATION_COMPLETE.md](docs/THEME_IMPLEMENTATION_COMPLETE.md)
- [docs/PHASE_2_FLOAT_BUTTON.md](docs/PHASE_2_FLOAT_BUTTON.md)

Hinweis:
- Dokumente können zeitlich abweichen.
- Bei Konflikt zählt Ist-Zustand im Code + Testnachweis.

### 6.1 Drift-Kandidaten (Plan vs. Ist)

Ziel: Offene Widersprüche zwischen Plan-/Phasen-Dokumenten und aktuellem Code-/Teststand sichtbar machen.

| Drift-ID | Bereich | Plan-/Doku-Hinweis | Ist-Hinweis | Bewertungsstand | Nächste Aktion |
|---|---|---|---|---|---|
| D-001 | Theme | [docs/THEME_SYSTEM_GUIDE.md](docs/THEME_SYSTEM_GUIDE.md) enthält „Geplante Features (Phase 2)“ | Features wie ARGB-Editor/Theme-Editing sind im Code und in Tests vorhanden (siehe F-UI-011, F-UI-012) | Offen | Guide in „bereits umgesetzt“ vs. „weiter geplant“ aufteilen |
| D-002 | Theme | [docs/THEME_IMPLEMENTATION_COMPLETE.md](docs/THEME_IMPLEMENTATION_COMPLETE.md) enthält „Phase 2 (Optional): Live Theme Editor“ | Theme-Editor und Color-Picker existieren bereits (F-UI-011, F-UI-012) | Offen | Optional-Liste bereinigen oder als historisch markieren |
| D-003 | Erweiterte Features | [docs/IMPLEMENTATION_COMPLETE.md](docs/IMPLEMENTATION_COMPLETE.md) enthält optionale Phasen, obwohl Status „vollständig implementiert“ genannt wird | Mehrere optionale Punkte sind als umgesetzt modelliert (F-CORE-004..006, F-FAC-009..010, F-UI-003) | Offen | Abschnitt „optional“ präzisieren und mit Matrix-IDs verknüpfen |
| D-004 | Analyse | [docs/ANALYSE_SUMMARY.md](docs/ANALYSE_SUMMARY.md) nennt „Unit-Tests optional“ | Im Repo existiert breiter Testbestand in [tests](tests) | Offen | Analyse-Dokument zeitlich einordnen (historischer Snapshot) |
| D-005 | Phase-Fortsetzung | [docs/PHASE_2_FLOAT_BUTTON.md](docs/PHASE_2_FLOAT_BUTTON.md) nennt „Nächste Phase: Z-Order Management“ | Keine explizite Feature-ID dazu in Matrix | Offen | Neue Planned-ID (P2/P3) in Matrix ergänzen |

Drift-Policy:
- Jede Drift-Korrektur muss eine Matrix-ID referenzieren.
- Plan-Dokumente mit überholtem Stand als „Historisch“ markieren statt löschen.
- Nach Korrektur: Bewertungsstand auf „Bereinigt“ setzen und Datum ergänzen.
### 6.2 Neue Drift-Kandidaten (Audit 2026-03-23)

Aus dem vollständigen Projekt-Audit ergänzte Drift-Kandidaten:

| Drift-ID | Bereich | Problem | Ist-Zustand | Bewertungsstand | Nächste Aktion |
|---|---|---|---|---|---|
| D-006 | Geltungsbereich | `themes/` nicht in Roadmap Sektion 5.1 erfasst | 3 QSS-Dateien vorhanden, funktional aktiv | Offen | Sektion 5.1 ergänzen |
| D-007 | Geltungsbereich | `data/` nicht in Roadmap Sektion 5.1 erfasst | Enthält `layout.xml`, `layout_alt.xml`, `layouts.json`, `themes.json` — teils aktiv genutzt | Offen | Sektion 5.1 ergänzen, Inhalt klären (A-003) |
| D-008 | Geltungsbereich | `examples/` nicht in Roadmap Sektion 5.1 erfasst | 3 Demo-Dateien; `phase_5_demo.py` undokumentiert | Offen | Sektion 5.1 ergänzen, `phase_5_demo.py` dokumentieren |
| D-009 | Dokumentation | [PROJECT_STRUCTURE_VERIFICATION.md](PROJECT_STRUCTURE_VERIFICATION.md) nicht in Roadmap verlinkt | Historisches Dokument (07.03.2026), erklärt Herkunft von Debug-Modulen und Test-Skripten | Offen | In Sektion 2 oder 5 als historischen Ankerpunkt aufnehmen |
| D-010 | README | `README.md` behauptet „27 UI Components" — tatsächlich 14 Module | 14 Python-Dateien in `src/widgetsystem/ui/` bestätigt per Dateisystem-Scan | Offen | README.md + docs/README.md + docs/UI_COMPONENTS.md auf 14 korrigieren |
| D-011 | Daten | Root-`layout.xml` (1375 Bytes) koexistiert mit `data/layout.xml` (999 Bytes) | Beide aktiv genutzt von verschiedenen Code-Stellen — echter Konfigurationssplit | Offen | Mit A-001 zusammenführen: eine kanonische Layout-Quelle festlegen |
| D-012 | Matrix-Vollständigkeit | Claim: Matrix hat 14 UI-Einträge, README nennt 27 | Befund: Matrix ist vollständig — README-Zahl ist falsch (D-010) | Bereinigt | Kein Matrixhandlungsbedarf — wird durch D-010-Korrektur aufgelöst |
| D-013 | README | `README.md` behauptet „49 test modules" — tatsächlich 54 Dateien | 54 .py-Dateien in `tests/` bestätigt per Scan | Offen | README.md auf 54 korrigieren |
| D-014 | Geltungsbereich | `archive/` nicht in Roadmap Sektion 5.1 erfasst | Enthält 5 Profil-JSONs identisch mit aktiven Profilen + 1 identisches QSS | Offen | Als explizit ausgeschlossenen/archivierten Bereich in Checklist vermerken |
---

## 7) Master-Feature-Matrix (Pflichtschema)

Für jedes Feature eine Zeile mit folgenden Feldern pflegen:

- Feature-ID
- Name
- Layer (Core/Controller/Factory/UI/Config/Test)
- Priorität (P0/P1/P2/P3)
- Implementierungsstatus
- Verifikationsstatus
- Governance-Status
- Code-Referenz
- Test-Referenz
- Manuelle Prüfschritte
- Risiko bei Regression
- Owner
- Letzte Prüfung (Datum)

Initiale Befüllung (v1, 54 Einträge, kompakt):

Hinweis zur Lesbarkeit:
- Alle Einträge in dieser Matrix sind aktuell `Implemented` + `Compliant`.
- Unterschiede liegen primär in `Verify`, `Risiko` und Referenzen.
- Detail-Referenzen mit mehreren Tests stehen in Abschnitt 8.6.

Visuelle Kodierung:
- `Verify`: 🟢 `Verified` · 🟡 `Partially Tested` · 🔴 `Untested`
- `Risiko`: 🔴 `Hoch` · 🟠 `Mittel` · 🟡 `Niedrig`

### 7.0 Status-Dashboard (Schnellleseansicht)

| Blick | Inhalt |
|---|---|
| ✅ Vollständig verifiziert (Auszug) | F-GOV-001, F-GOV-002, F-QA-002, F-CORE-001..003, F-CORE-007..009, F-CTRL-007, F-FAC-001..010, F-UI-001..002, F-UI-004..006, F-UI-008..013, F-CONF-001..010 |
| ⚠️ Teilverifiziert | F-CORE-010 |
| 🔴 Hochrisko-Features | F-GOV-001, F-QA-001, F-CORE-001, F-CORE-004, F-CORE-005, F-CORE-007, F-CTRL-001, F-CTRL-002, F-CTRL-007, F-FAC-002, F-FAC-003, F-FAC-009, F-UI-003, F-UI-005, F-UI-006, F-UI-008, F-UI-009, F-UI-010, F-CONF-001, F-CONF-002 |

Interpretation:
- Für Release-Kandidaten zuerst `⚠️ Teilverifiziert` schließen.
- Bei Änderungen an `🔴 Hochrisko-Features` immer Abschnitt 8.6 vollständig anwenden.

### 7.1 Governance & Qualität

| ID | Feature | Prio | Verify | Risiko | Code | Test |
|---|---|---|---|---|---|---|
| F-GOV-001 | Agenten-Basisregeln & Reihenfolge | P0 | 🟢 Verified | 🔴 Hoch | [AGENT_CONFIG.md](AGENT_CONFIG.md) | [tests/verify_agent_config.py](tests/verify_agent_config.py) |
| F-GOV-002 | Instruction-Routing-Regeln | P0 | 🟢 Verified | 🟠 Mittel | [.github/instructions](.github/instructions) | [tests/verify_agent_config.py](tests/verify_agent_config.py) |
| F-QA-001 | Qualitäts-Gate Pipeline | P0 | 🟢 Verified | 🔴 Hoch | [scripts/check_quality.py](scripts/check_quality.py) | [tests/test_full_system.py](tests/test_full_system.py) |
| F-QA-002 | Agent-Konfigurations-Verifikation | P0 | 🟢 Verified | 🟠 Mittel | [tests/verify_agent_config.py](tests/verify_agent_config.py) | [tests/verify_agent_config.py](tests/verify_agent_config.py) |

### 7.2 Core

- Neuer Matrix-Eintrag: `F-CORE-010 | EnumTypes | P1 | ✅ Implemented | 🟡 Partially Tested`

| ID | Feature | Prio | Verify | Risiko | Code | Test |
|---|---|---|---|---|---|---|
| F-CORE-001 | MainWindow App-Lifecycle | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/core/main.py](src/widgetsystem/core/main.py) | [tests/test_main_window.py](tests/test_main_window.py) |
| F-CORE-002 | Visual Main Window | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/core/main_visual.py](src/widgetsystem/core/main_visual.py) | [tests/test_main_visual.py](tests/test_main_visual.py) |
| F-CORE-003 | Plugin-System & Registry | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/core/plugin_system.py](src/widgetsystem/core/plugin_system.py) | [tests/test_plugin_system.py](tests/test_plugin_system.py) |
| F-CORE-004 | Undo/Redo Command-Stack | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/core/undo_redo.py](src/widgetsystem/core/undo_redo.py) | [tests/test_features.py](tests/test_features.py) |
| F-CORE-005 | Config Import/Export & Backup | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/core/config_io.py](src/widgetsystem/core/config_io.py) | [tests/test_full_system.py](tests/test_full_system.py) |
| F-CORE-006 | Template-System | P2 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/core/template_system.py](src/widgetsystem/core/template_system.py) | [tests/test_features.py](tests/test_features.py) |
| F-CORE-007 | ThemeManager Singleton & Signals | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/core/theme_manager.py](src/widgetsystem/core/theme_manager.py) | [tests/test_theme_manager.py](tests/test_theme_manager.py) |
| F-CORE-008 | ThemeProfile ARGB-Profilmodell | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/core/theme_profile.py](src/widgetsystem/core/theme_profile.py) | [tests/test_theme_profile.py](tests/test_theme_profile.py) |
| F-CORE-009 | Gradient-System | P2 | 🟢 Verified | 🟡 Niedrig | [src/widgetsystem/core/gradient_system.py](src/widgetsystem/core/gradient_system.py) | [tests/test_gradient_system.py](tests/test_gradient_system.py) |
| F-CORE-010 | EnumTypes | P1 | 🟡 Partially Tested | 🟠 Mittel | [src/widgetsystem/enums.py](src/widgetsystem/enums.py) | [tests/test_enums.py](tests/test_enums.py) |

#### 7.2.1 Core-Detailregister (lesbar, sortiert, fehlerklar)

##### 7.2.1.1 Schnellübersicht

| ID | Core-Feature | Primärer Fokus | Fehlerklasse bei Defekt |
|---|---|---|---|
| F-CORE-001 | MainWindow App-Lifecycle | Startup/Shutdown/Lebenszyklus | Orchestrierungsfehler |
| F-CORE-002 | Visual Main Window | Visuelle Hauptinitialisierung | Integrationsfehler |
| F-CORE-003 | Plugin-System & Registry | Registrierung/Ladevorgang | Plugin-/Registry-Fehler |
| F-CORE-004 | Undo/Redo Command-Stack | Stack-Konsistenz | Zustands-/History-Fehler |
| F-CORE-005 | Config Import/Export & Backup | Persistenz & Wiederherstellung | I/O-/Backup-Fehler |
| F-CORE-006 | Template-System | Vorlagenanwendung | Daten-/Template-Fehler |
| F-CORE-007 | ThemeManager Singleton & Signals | Theme-Status + Signalfluss | Theme-Orchestrierungsfehler |
| F-CORE-008 | ThemeProfile ARGB-Profilmodell | Profilserialisierung | Profil-/Datenfehler |
| F-CORE-009 | Gradient-System | Gradient-Berechnung/Mapping | Rendering-/Datenfehler |
| F-CORE-010 | EnumTypes | Typsichere Enum-Werte statt Magic Strings | Typ-/Mapping-Fehler |

##### 7.2.1.2 Fehlerdefinition (Core)

| Schweregrad | Wann ist es ein Core-Fehler? | Sofortmaßnahme |
|---|---|---|
| 🔴 Blocker | Startpfad bricht, Persistenz beschädigt, zentrale Objekte nicht verfügbar | Lauf sofort stoppen, betroffene Core-Tests starten |
| 🟠 Relevant | Teilfunktion arbeitet inkonsistent (z. B. History, Plugin, Theme-State) | betroffene Feature-ID auf 🟡 setzen, Ursache isolieren |
| 🟡 Hinweis | Optionaler Komfortpfad ohne Kernschaden betroffen | dokumentieren, nachgelagert beheben |

##### 7.2.1.3 Pro-Core-Feature mit Fehlercodes

| Feature-ID | Code | Regression |
|---|---|---|
| F-CORE-001 | [src/widgetsystem/core/main.py](src/widgetsystem/core/main.py) | [tests/test_main_window.py](tests/test_main_window.py) |
| F-CORE-002 | [src/widgetsystem/core/main_visual.py](src/widgetsystem/core/main_visual.py) | [tests/test_main_visual.py](tests/test_main_visual.py) |
| F-CORE-003 | [src/widgetsystem/core/plugin_system.py](src/widgetsystem/core/plugin_system.py) | [tests/test_plugin_system.py](tests/test_plugin_system.py) |
| F-CORE-004 | [src/widgetsystem/core/undo_redo.py](src/widgetsystem/core/undo_redo.py) | [tests/test_features.py](tests/test_features.py) |
| F-CORE-005 | [src/widgetsystem/core/config_io.py](src/widgetsystem/core/config_io.py) | [tests/test_full_system.py](tests/test_full_system.py) |
| F-CORE-006 | [src/widgetsystem/core/template_system.py](src/widgetsystem/core/template_system.py) | [tests/test_features.py](tests/test_features.py) |
| F-CORE-007 | [src/widgetsystem/core/theme_manager.py](src/widgetsystem/core/theme_manager.py) | [tests/test_theme_manager.py](tests/test_theme_manager.py) |
| F-CORE-008 | [src/widgetsystem/core/theme_profile.py](src/widgetsystem/core/theme_profile.py) | [tests/test_theme_profile.py](tests/test_theme_profile.py) |
| F-CORE-009 | [src/widgetsystem/core/gradient_system.py](src/widgetsystem/core/gradient_system.py) | [tests/test_gradient_system.py](tests/test_gradient_system.py) |
| F-CORE-010 | [src/widgetsystem/enums.py](src/widgetsystem/enums.py) | [tests/test_enums.py](tests/test_enums.py) |

| Fehlercode | Trigger | Sollverhalten | Abweichung = Fehler |
|---|---|---|---|
| E-CORE-001-A | App-Start | MainWindow initialisiert stabil | Startabbruch/Exception |
| E-CORE-002-A | Visual-Init | visuelle Oberfläche lädt vollständig | unvollständiger Aufbau |
| E-CORE-003-A | Plugin-Registrierung | bekannte Plugins verfügbar | fehlende Registry-Einträge |
| E-CORE-004-A | Undo/Redo-Sequenz | deterministische Rücknahme/Wiederholung | falsche Reihenfolge/Zustand |
| E-CORE-005-A | Import/Export | konsistente Dateioperationen + Backup | Datenverlust/inkonsistente Dateien |
| E-CORE-006-A | Template-Anwendung | vollständige Erzeugung gemäß Template | fehlende/inkonsistente Artefakte |
| E-CORE-007-A | Theme-Signalfluss | Themewechsel propagiert korrekt | stale UI/fehlende Signale |
| E-CORE-008-A | Profil lesen/schreiben | ARGB-Profile konsistent serialisiert | Profilverlust/inkonsistente Werte |
| E-CORE-009-A | Gradient-Berechnung | stabile Farbübergänge | falsches Rendering/Mapping |
| E-CORE-010-A | Enum-Nutzung/Serialisierung | gültige, typsichere Enum-Werte | ungültige Werte/Mappings |

##### 7.2.1.4 Vorgehen bei Core-Fehlerverdacht

1. Core-ID in 7.2.1.1 bestimmen.
2. Fehlercode in 7.2.1.3 zuordnen.
3. Zugehörigen Test ausführen.
4. Matrixstatus (`Verify`, `Risiko`) anpassen.

### 7.3 Controller

| ID | Feature | Prio | Verify | Risiko | Code | Test |
|---|---|---|---|---|---|---|
| F-CTRL-001 | DockController Lifecycle | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/controllers/dock_controller.py](src/widgetsystem/controllers/dock_controller.py) | [tests/test_main_window_extended.py](tests/test_main_window_extended.py) |
| F-CTRL-002 | LayoutController Save/Load/Reset | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/controllers/layout_controller.py](src/widgetsystem/controllers/layout_controller.py) | [tests/test_main_window.py](tests/test_main_window.py) |
| F-CTRL-003 | ThemeController Apply/Reload | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/controllers/theme_controller.py](src/widgetsystem/controllers/theme_controller.py) | [tests/test_theme_manager.py](tests/test_theme_manager.py) |
| F-CTRL-004 | DnDController Regeln | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/controllers/dnd_controller.py](src/widgetsystem/controllers/dnd_controller.py) | [tests/test_dnd_factory.py](tests/test_dnd_factory.py) |
| F-CTRL-005 | ResponsiveController Breakpoints | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/controllers/responsive_controller.py](src/widgetsystem/controllers/responsive_controller.py) | [tests/test_responsive_controller.py](tests/test_responsive_controller.py) |
| F-CTRL-006 | ShortcutController Aktionen/Shortcuts | P2 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/controllers/shortcut_controller.py](src/widgetsystem/controllers/shortcut_controller.py) | [tests/test_signals.py](tests/test_signals.py) |
| F-CTRL-007 | TabSubsystem Integration | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/controllers/tab_subsystem.py](src/widgetsystem/controllers/tab_subsystem.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |

#### 7.3.1 Controller-Detailregister (lesbar, sortiert, fehlerklar)

##### 7.3.1.1 Schnellübersicht

| ID | Controller-Feature | Primärer Fokus | Fehlerklasse bei Defekt |
|---|---|---|---|
| F-CTRL-001 | DockController Lifecycle | Dock-Lifecycle und Statusübergänge | Dock-Orchestrierungsfehler |
| F-CTRL-002 | LayoutController Save/Load/Reset | Layoutpersistenz | Save/Load-Fehler |
| F-CTRL-003 | ThemeController Apply/Reload | Theme-Anwendung auf Laufzeitobjekte | Theme-Anwendungsfehler |
| F-CTRL-004 | DnDController Regeln | DnD-Regelprüfung | Regelverletzungsfehler |
| F-CTRL-005 | ResponsiveController Breakpoints | Breakpoint-Auswertung | Responsivitätsfehler |
| F-CTRL-006 | ShortcutController Aktionen/Shortcuts | Shortcut-Mapping | Event-/Shortcut-Fehler |
| F-CTRL-007 | TabSubsystem Integration | Tab-Subsystem-Orchestrierung | Integrations-/Sichtbarkeitsfehler |

##### 7.3.1.2 Fehlerdefinition (Controller)

| Schweregrad | Wann ist es ein Controller-Fehler? | Sofortmaßnahme |
|---|---|---|
| 🔴 Blocker | Kernaktionen (Dock/Layout/Tab) brechen oder erzeugen falschen UI-Zustand | Änderung stoppen, Controller-Regression ausführen |
| 🟠 Relevant | Steuerlogik arbeitet nur teilweise (z. B. einzelne Regeln/Shortcuts fehlen) | betroffene Feature-ID auf 🟡 setzen |
| 🟡 Hinweis | Randfall betroffen ohne Kernflussbruch | dokumentieren und priorisieren |

##### 7.3.1.3 Pro-Controller-Feature mit Fehlercodes

| Feature-ID | Code | Regression |
|---|---|---|
| F-CTRL-001 | [src/widgetsystem/controllers/dock_controller.py](src/widgetsystem/controllers/dock_controller.py) | [tests/test_main_window_extended.py](tests/test_main_window_extended.py) |
| F-CTRL-002 | [src/widgetsystem/controllers/layout_controller.py](src/widgetsystem/controllers/layout_controller.py) | [tests/test_main_window.py](tests/test_main_window.py) |
| F-CTRL-003 | [src/widgetsystem/controllers/theme_controller.py](src/widgetsystem/controllers/theme_controller.py) | [tests/test_theme_manager.py](tests/test_theme_manager.py) |
| F-CTRL-004 | [src/widgetsystem/controllers/dnd_controller.py](src/widgetsystem/controllers/dnd_controller.py) | [tests/test_dnd_factory.py](tests/test_dnd_factory.py) |
| F-CTRL-005 | [src/widgetsystem/controllers/responsive_controller.py](src/widgetsystem/controllers/responsive_controller.py) | [tests/test_responsive_factory.py](tests/test_responsive_factory.py) |
| F-CTRL-006 | [src/widgetsystem/controllers/shortcut_controller.py](src/widgetsystem/controllers/shortcut_controller.py) | [tests/test_signals.py](tests/test_signals.py) |
| F-CTRL-007 | [src/widgetsystem/controllers/tab_subsystem.py](src/widgetsystem/controllers/tab_subsystem.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |

| Fehlercode | Trigger | Sollverhalten | Abweichung = Fehler |
|---|---|---|---|
| E-CTRL-001-A | Dock-Open/Close | konsistente Dock-Zustände | Zombie-/unsichtbare Docks |
| E-CTRL-002-A | Layout Save/Load/Reset | reproduzierbarer Layoutzustand | Layoutverlust oder falscher Restore |
| E-CTRL-003-A | Theme apply/reload | einheitliche Theme-Anwendung | nur Teilbereiche aktualisiert |
| E-CTRL-004-A | DnD-Regelprüfung | nur erlaubte Moves | unzulässiger Move möglich |
| E-CTRL-005-A | Breakpoint-Wechsel | erwartete UI-Anpassung | keine/falsche Anpassung |
| E-CTRL-006-A | Shortcut-Ausführung | Aktion wird exakt ausgelöst | keine oder falsche Aktion |
| E-CTRL-007-A | Tab-Subsystem-Flow | korrekte Sichtbarkeit/Umschaltung | inkonsistente Tab-Anzeige |

##### 7.3.1.4 Vorgehen bei Controller-Fehlerverdacht

1. Controller-ID in 7.3.1.1 bestimmen.
2. Fehlercode in 7.3.1.3 abgleichen.
3. Zugehörigen Test ausführen.
4. Matrixstatus (`Verify`, `Risiko`) anpassen.

### 7.4 Factory

| ID | Feature | Prio | Verify | Risiko | Code | Test |
|---|---|---|---|---|---|---|
| F-FAC-001 | LayoutFactory | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/factories/layout_factory.py](src/widgetsystem/factories/layout_factory.py) | [tests/test_layout_factory.py](tests/test_layout_factory.py) |
| F-FAC-002 | ThemeFactory | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/factories/theme_factory.py](src/widgetsystem/factories/theme_factory.py) | [tests/test_theme_factory_extended.py](tests/test_theme_factory_extended.py) |
| F-FAC-003 | PanelFactory | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/factories/panel_factory.py](src/widgetsystem/factories/panel_factory.py) | [tests/test_panel_factory.py](tests/test_panel_factory.py) |
| F-FAC-004 | MenuFactory | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/factories/menu_factory.py](src/widgetsystem/factories/menu_factory.py) | [tests/test_menu_factory.py](tests/test_menu_factory.py) |
| F-FAC-005 | TabsFactory | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/factories/tabs_factory.py](src/widgetsystem/factories/tabs_factory.py) | [tests/test_tabs_factory.py](tests/test_tabs_factory.py) |
| F-FAC-006 | DnDFactory | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/factories/dnd_factory.py](src/widgetsystem/factories/dnd_factory.py) | [tests/test_dnd_factory.py](tests/test_dnd_factory.py) |
| F-FAC-007 | ResponsiveFactory | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/factories/responsive_factory.py](src/widgetsystem/factories/responsive_factory.py) | [tests/test_responsive_factory.py](tests/test_responsive_factory.py) |
| F-FAC-008 | I18nFactory | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/factories/i18n_factory.py](src/widgetsystem/factories/i18n_factory.py) | [tests/test_i18n_factory.py](tests/test_i18n_factory.py) |
| F-FAC-009 | ListFactory | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/factories/list_factory.py](src/widgetsystem/factories/list_factory.py) | [tests/test_list_factory.py](tests/test_list_factory.py) |
| F-FAC-010 | UIConfigFactory | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/factories/ui_config_factory.py](src/widgetsystem/factories/ui_config_factory.py) | [tests/test_ui_config_factory_extended.py](tests/test_ui_config_factory_extended.py) |

#### 7.4.1 Factory-Detailregister (lesbar, sortiert, fehlerklar)

Ziel dieser Ansicht:
- schnelle Orientierung (welche Factory ist betroffen?),
- klare Fehlerdefinition im Bedarfsfall,
- einheitliches Vorgehen für Analyse und Regression.

##### 7.4.1.1 Schnellübersicht (Scan in < 1 Minute)

| ID | Factory | Primäre Config | Kritischer Fokus | Fehlerklasse bei Defekt |
|---|---|---|---|---|
| F-FAC-001 | LayoutFactory | [config/layouts.json](config/layouts.json) | Pfadauflösung & Default-Layout | Konfig-/I/O-Fehler |
| F-FAC-002 | ThemeFactory | [config/themes.json](config/themes.json) | Theme-Auswahl, Stylesheet, Profile | Theme- und Persistenzfehler |
| F-FAC-003 | PanelFactory | [config/panels.json](config/panels.json) | Panel-Validierung & Speicherung | Struktur-/Validierungsfehler |
| F-FAC-004 | MenuFactory | [config/menus.json](config/menus.json) | Rekursive Menüstruktur | Struktur-/Rekursionsfehler |
| F-FAC-005 | TabsFactory | [config/tabs.json](config/tabs.json) | Tab-Gruppen, Dock-Area, Orientierung | Validierungs-/Serialisierungsfehler |
| F-FAC-006 | DnDFactory | [config/dnd.json](config/dnd.json) | Drop-Zonen & Rules-Mapping | Regel-/Mapping-Fehler |
| F-FAC-007 | ResponsiveFactory | [config/responsive.json](config/responsive.json) | Breakpoints & Actions | Grenzwert-/Regelfehler |
| F-FAC-008 | I18nFactory | [config/i18n.de.json](config/i18n.de.json), [config/i18n.en.json](config/i18n.en.json) | Locale-Wechsel & Key-Auflösung | Übersetzungs-/Locale-Fehler |
| F-FAC-009 | ListFactory | [config/lists.json](config/lists.json) | Nested-Items & Persistenz | Baum-/Persistenzfehler |
| F-FAC-010 | UIConfigFactory | [config/ui_config.json](config/ui_config.json) | Seiten/Widgets/Properties | Typ-/Strukturfehler |

##### 7.4.1.2 Fehlerdefinition (verbindlich)

| Schweregrad | Wann ist es ein Fehler? | Sofortmaßnahme |
|---|---|---|
| 🔴 Blocker | Unbehandelte Exception, ungültiger Write-Back, leere Kernstruktur trotz valider Config | Änderung stoppen, Konfig + betroffene Tests sofort prüfen |
| 🟠 Relevant | Datensatz wird verworfen, Fallback greift unerwartet, Teilfunktion fehlt | Ursache eingrenzen, Matrix-Verify auf 🟡 setzen |
| 🟡 Hinweis | Optionaler Teil fehlt ohne Funktionsverlust | dokumentieren, keine Blockade |

Fehlerkennung im Bedarfsfall:
1. Betroffene Factory über Config-Datei zuordnen.
2. Fehlercode aus Tabelle 7.4.1.3 nehmen.
3. Zieltest aus „Regression“ ausführen.
4. Status in Matrix (Verify/Risiko) nachziehen.

##### 7.4.1.3 Pro-Factory-Steckbrief inkl. Fehlerindikatoren

###### F-FAC-001 · LayoutFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🟠 Mittel |
| Code | [src/widgetsystem/factories/layout_factory.py](src/widgetsystem/factories/layout_factory.py) |
| Config/Schema | [config/layouts.json](config/layouts.json) · [schemas/layouts.schema.json](schemas/layouts.schema.json) |
| Kern-API | `list_layouts()`, `get_default_layout_id()` |
| Regression | [tests/test_layout_factory.py](tests/test_layout_factory.py), [tests/test_layout_factory_extended.py](tests/test_layout_factory_extended.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-001-A | `layouts.json` fehlt | `FileNotFoundError` in `list_layouts()` | keine Exception oder falscher Typ |
| E-FAC-001-B | JSON defekt | Warnung + leere Liste | Crash oder inkonsistente Rückgabe |
| E-FAC-001-C | Eintrag ohne `id/name/file` | Eintrag wird übersprungen | Eintrag wird trotzdem übernommen |

###### F-FAC-002 · ThemeFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🔴 Hoch |
| Code | [src/widgetsystem/factories/theme_factory.py](src/widgetsystem/factories/theme_factory.py) |
| Config/Schema | [config/themes.json](config/themes.json) · [schemas/themes.schema.json](schemas/themes.schema.json) · [config/profiles](config/profiles) |
| Kern-API | `load_themes()`, `list_themes()`, `get_default_theme()`, `get_default_stylesheet()`, `load_profile()`, `save_profile()` |
| Regression | [tests/test_theme_factory_extended.py](tests/test_theme_factory_extended.py), [tests/test_theme_manager.py](tests/test_theme_manager.py), [tests/test_theme_system.py](tests/test_theme_system.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-002-A | `themes.json` fehlt/defekt | sichere Fallbacks (leere Daten) | unkontrollierte Exception |
| E-FAC-002-B | Theme ohne Dateifeld | Theme wird verworfen | Theme wird fehlerhaft geladen |
| E-FAC-002-C | Profil speichern | `True` und Datei vorhanden | `False` oder fehlende Datei |

###### F-FAC-003 · PanelFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🔴 Hoch |
| Code | [src/widgetsystem/factories/panel_factory.py](src/widgetsystem/factories/panel_factory.py) |
| Config/Schema | [config/panels.json](config/panels.json) · [schemas/panels.schema.json](schemas/panels.schema.json) |
| Kern-API | `load_panels()`, `get_panel()`, `get_panels_by_area()`, `add_panel()`, `save_to_file()` |
| Regression | [tests/test_panel_factory.py](tests/test_panel_factory.py), [tests/test_panel_factory_extended.py](tests/test_panel_factory_extended.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-003-A | ungültige `area` | `ValueError` | stillschweigende Übernahme |
| E-FAC-003-B | fehlerhafte JSON-Struktur | `ValueError` | undefinierter Zustand |
| E-FAC-003-C | `save_to_file()` nach Änderung | `True` und persistierte Daten | `False` oder fehlende Änderungen |

###### F-FAC-004 · MenuFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🟠 Mittel |
| Code | [src/widgetsystem/factories/menu_factory.py](src/widgetsystem/factories/menu_factory.py) |
| Config/Schema | [config/menus.json](config/menus.json) · [schemas/menus.schema.json](schemas/menus.schema.json) |
| Kern-API | `load_menus()`, `get_menu_item()`, `find_actions()`, `list_shortcuts()`, `save_to_file()` |
| Regression | [tests/test_menu_factory.py](tests/test_menu_factory.py), [tests/test_menu_factory_extended.py](tests/test_menu_factory_extended.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-004-A | ungültiger `type` | `ValueError` | fehlerhafter Typ bleibt aktiv |
| E-FAC-004-B | rekursive `children` | vollständiger Baum | fehlende Untereinträge |
| E-FAC-004-C | Shortcut-Auswertung | konsistentes Mapping | fehlende/falsche Zuordnungen |

###### F-FAC-005 · TabsFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🟠 Mittel |
| Code | [src/widgetsystem/factories/tabs_factory.py](src/widgetsystem/factories/tabs_factory.py) |
| Config/Schema | [config/tabs.json](config/tabs.json) · [schemas/tabs.schema.json](schemas/tabs.schema.json) |
| Kern-API | `load_tab_groups()`, `get_tab_groups_by_area()`, `find_tab_by_id()`, `get_flat_tab_list()`, `save_to_file()` |
| Regression | [tests/test_tabs_factory.py](tests/test_tabs_factory.py), [tests/test_tabs_factory_extended.py](tests/test_tabs_factory_extended.py), [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-005-A | ungültige `dock_area` | `ValueError` | ungültige Area wird akzeptiert |
| E-FAC-005-B | ungültige `orientation` | `ValueError` | unklare Layoutrichtung |
| E-FAC-005-C | Flatten eines Nested-Baums | alle Tabs enthalten | Tabs fehlen im Flat-Resultat |

###### F-FAC-006 · DnDFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🟠 Mittel |
| Code | [src/widgetsystem/factories/dnd_factory.py](src/widgetsystem/factories/dnd_factory.py) |
| Config/Schema | [config/dnd.json](config/dnd.json) · [schemas/dnd.schema.json](schemas/dnd.schema.json) |
| Kern-API | `load_drop_zones()`, `load_dnd_rules()`, `get_dnd_rule()`, `get_panel_rules()` |
| Regression | [tests/test_dnd_factory.py](tests/test_dnd_factory.py), [tests/test_features.py](tests/test_features.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-006-A | negative `nav_zone_width` | `ValueError` | ungültiger Wert aktiv |
| E-FAC-006-B | `rules`/`dnd_rules` Kompatibilität | Regeln werden geladen | leere Regeln trotz valider Datei |
| E-FAC-006-C | Panel-Regeln abrufen | konsistente Rule-Menge | fehlende oder fremde Regeln |

###### F-FAC-007 · ResponsiveFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🟠 Mittel |
| Code | [src/widgetsystem/factories/responsive_factory.py](src/widgetsystem/factories/responsive_factory.py) |
| Config/Schema | [config/responsive.json](config/responsive.json) · [schemas/responsive.schema.json](schemas/responsive.schema.json) |
| Kern-API | `load_breakpoints()`, `load_responsive_rules()`, `get_breakpoint()`, `get_panel_rules()` |
| Regression | [tests/test_responsive_factory.py](tests/test_responsive_factory.py), [tests/test_responsive_factory_extended.py](tests/test_responsive_factory_extended.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-007-A | `min_width > max_width` | `ValueError` | ungültiger Breakpoint aktiv |
| E-FAC-007-B | ungültige Action | `ValueError` | Aktion außerhalb `hide/show/collapse` |
| E-FAC-007-C | Regelabfrage Panel | nur passende Regeln | unvollständige oder falsche Treffermenge |

###### F-FAC-008 · I18nFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🟠 Mittel |
| Code | [src/widgetsystem/factories/i18n_factory.py](src/widgetsystem/factories/i18n_factory.py) |
| Config/Schema | [config/i18n.de.json](config/i18n.de.json), [config/i18n.en.json](config/i18n.en.json) · [schemas/i18n.schema.json](schemas/i18n.schema.json) |
| Kern-API | `set_locale()`, `translate()`, `t()`, `has_key()`, `get_all_keys()` |
| Regression | [tests/test_i18n_factory.py](tests/test_i18n_factory.py), [tests/test_i18n_factory_extended.py](tests/test_i18n_factory_extended.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-008-A | nicht unterstützte Locale | `ValueError` | Locale wird trotzdem gesetzt |
| E-FAC-008-B | fehlender Key | Key oder `default` wird zurückgegeben | unerwarteter Leerwert |
| E-FAC-008-C | Interpolation | Platzhalter ersetzt | Platzhalter bleibt ungefüllt |

###### F-FAC-009 · ListFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🔴 Hoch |
| Code | [src/widgetsystem/factories/list_factory.py](src/widgetsystem/factories/list_factory.py) |
| Config/Schema | [config/lists.json](config/lists.json) · [schemas/lists.schema.json](schemas/lists.schema.json) |
| Kern-API | `load_list_groups()`, `get_list_group_by_id()`, `add_item_to_group()`, `remove_item_from_group()`, `save_to_file()` |
| Regression | [tests/test_list_factory.py](tests/test_list_factory.py), [tests/test_list_factory_extended.py](tests/test_list_factory_extended.py), [tests/test_features.py](tests/test_features.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-009-A | ungültiger `list_type`/`content_type` | `ValueError` | ungültiger Typ aktiv |
| E-FAC-009-B | Nested-Insert/Remove | Baum bleibt konsistent | Children-Verlust oder Duplikate |
| E-FAC-009-C | Persistenz nach Mutation | `save_to_file()` erfolgreich | Änderungen nicht dauerhaft |

###### F-FAC-010 · UIConfigFactory
| Feld | Inhalt |
|---|---|
| Status | P1 · 🟢 Verified · 🟠 Mittel |
| Code | [src/widgetsystem/factories/ui_config_factory.py](src/widgetsystem/factories/ui_config_factory.py) |
| Config/Schema | [config/ui_config.json](config/ui_config.json) · [schemas/ui_config.schema.json](schemas/ui_config.schema.json) |
| Kern-API | `load_ui_config_pages()`, `get_page_by_id()`, `get_pages_by_category()`, `get_all_categories()` |
| Regression | [tests/test_ui_config_factory_extended.py](tests/test_ui_config_factory_extended.py), [tests/test_widget_features_editor.py](tests/test_widget_features_editor.py) |

| Fehlercode | Trigger | Erwartetes Verhalten | Wenn abweichend, dann Fehler |
|---|---|---|---|
| E-FAC-010-A | ungültiger Widget-Typ | `ValueError` | Widget mit ungültigem Typ geladen |
| E-FAC-010-B | ungültiger Property-Typ | `ValueError` | Property inkonsistent im UI |
| E-FAC-010-C | Kategorie-/Order-Filter | deterministisch sortierte Seiten | unstabile Reihenfolge |

#### 7.4.2 Sortierung und Vorgehen bei Bedarf

Verbindliche Sortierung für Reviews und Regression:
1. Basisladepfad: F-FAC-001, F-FAC-002
2. Struktur/Container: F-FAC-003, F-FAC-004, F-FAC-005
3. Verhalten: F-FAC-006, F-FAC-007
4. Lokalisierung: F-FAC-008
5. Inhalt/Editor: F-FAC-009, F-FAC-010

Bedarfsfall-Ablauf (wenn ein Fehler vermutet wird):
1. Factory-ID in 7.4.1.1 bestimmen.
2. Passenden Fehlercode in 7.4.1.3 abgleichen.
3. Zugehörige Tests sofort ausführen.
4. Bei bestätigtem Fehler: Matrix-Verify auf 🟡/🔴 setzen und Risiko aktualisieren.

### 7.5 UI

| ID | Feature | Prio | Verify | Risiko | Code | Test |
|---|---|---|---|---|---|---|
| F-UI-001 | VisualApp Wrapper | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/ui/visual_app.py](src/widgetsystem/ui/visual_app.py) | [tests/test_visual_app_extended.py](tests/test_visual_app_extended.py) |
| F-UI-002 | VisualLayer Hauptoberfläche | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/ui/visual_layer.py](src/widgetsystem/ui/visual_layer.py) | [tests/test_visual_layer.py](tests/test_visual_layer.py) |
| F-UI-003 | ConfigurationPanel Runtime-Editor | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/ui/config_panel.py](src/widgetsystem/ui/config_panel.py) | [tests/test_config_panel.py](tests/test_config_panel.py) |
| F-UI-004 | InlayTitleBar (3px→35px) | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/ui/inlay_titlebar.py](src/widgetsystem/ui/inlay_titlebar.py) | [tests/test_inlay_titlebar.py](tests/test_inlay_titlebar.py) |
| F-UI-005 | FloatingTitlebar Verhalten | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/ui/floating_titlebar.py](src/widgetsystem/ui/floating_titlebar.py) | [tests/test_floating_titlebar_extended.py](tests/test_floating_titlebar_extended.py) |
| F-UI-006 | FloatingStateTracker Persistenz | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/ui/floating_state_tracker.py](src/widgetsystem/ui/floating_state_tracker.py) | [tests/test_phase_2_floating_state_tracker.py](tests/test_phase_2_floating_state_tracker.py) |
| F-UI-007 | TabColorController | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/ui/tab_color_controller.py](src/widgetsystem/ui/tab_color_controller.py) | [tests/test_tabbar.py](tests/test_tabbar.py) |
| F-UI-008 | TabSelectorMonitor | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/ui/tab_selector_monitor.py](src/widgetsystem/ui/tab_selector_monitor.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |
| F-UI-009 | TabSelectorEventHandler | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/ui/tab_selector_event_handler.py](src/widgetsystem/ui/tab_selector_event_handler.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |
| F-UI-010 | TabSelectorVisibilityController | P1 | 🟢 Verified | 🔴 Hoch | [src/widgetsystem/ui/tab_selector_visibility_controller.py](src/widgetsystem/ui/tab_selector_visibility_controller.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |
| F-UI-011 | ThemeEditor Live-Editing | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/ui/theme_editor.py](src/widgetsystem/ui/theme_editor.py) | [tests/test_theme_editor.py](tests/test_theme_editor.py) |
| F-UI-012 | ARGBColorPicker | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/ui/argb_color_picker.py](src/widgetsystem/ui/argb_color_picker.py) | [tests/test_argb_color_picker.py](tests/test_argb_color_picker.py) |
| F-UI-013 | WidgetFeaturesEditor | P1 | 🟢 Verified | 🟠 Mittel | [src/widgetsystem/ui/widget_features_editor.py](src/widgetsystem/ui/widget_features_editor.py) | [tests/test_widget_features_editor.py](tests/test_widget_features_editor.py) |
| F-UI-014 | PluginManagerDialog | P2 | 🟢 Verified | 🟡 Niedrig | [src/widgetsystem/ui/plugin_manager_dialog.py](src/widgetsystem/ui/plugin_manager_dialog.py) | [tests/test_plugin_manager_dialog.py](tests/test_plugin_manager_dialog.py) |
| F-UI-015 | Z-Order Management | P3 | 🗓 Planned | ⬜ Untested | [docs/PHASE_2_FLOAT_BUTTON.md](docs/PHASE_2_FLOAT_BUTTON.md) | - |

#### 7.5.1 UI-Detailregister (lesbar, sortiert, fehlerklar)

##### 7.5.1.1 Schnellübersicht

| ID | UI-Feature | Primärer Fokus | Fehlerklasse bei Defekt |
|---|---|---|---|
| F-UI-001 | VisualApp Wrapper | App-Wrapper-Initialisierung | Start-/Integrationsfehler |
| F-UI-002 | VisualLayer Hauptoberfläche | Hauptlayout und Panelzusammenspiel | Layout-/Darstellungsfehler |
| F-UI-003 | ConfigurationPanel Runtime-Editor | Laufzeitkonfiguration im UI | Editor-/State-Fehler |
| F-UI-004 | InlayTitleBar | Interaktion und Sichtbarkeit | Titlebar-Verhaltensfehler |
| F-UI-005 | FloatingTitlebar Verhalten | Floating-Titelzustände | Floating-Orchestrierungsfehler |
| F-UI-006 | FloatingStateTracker Persistenz | Zustandsspeicherung | Persistenzfehler |
| F-UI-007 | TabColorController | Farbzustand Tabs | Darstellungs-/State-Fehler |
| F-UI-008 | TabSelectorMonitor | Monitoring Tabanzahl/-zustand | Erkennungsfehler |
| F-UI-009 | TabSelectorEventHandler | Eventverarbeitung | Eventflussfehler |
| F-UI-010 | TabSelectorVisibilityController | Sichtbarkeitsregeln | Sichtbarkeitsfehler |
| F-UI-011 | ThemeEditor Live-Editing | Theme-Livebearbeitung | Editor-/Apply-Fehler |
| F-UI-012 | ARGBColorPicker | Farbselektion inkl. Alpha | Farbberechnungsfehler |
| F-UI-013 | WidgetFeaturesEditor | Widget-Feature-Editor | Editor-/Binding-Fehler |
| F-UI-014 | PluginManagerDialog | Pluginverwaltung im Dialog | Dialog-/Integrationsfehler |

##### 7.5.1.2 Fehlerdefinition (UI)

| Schweregrad | Wann ist es ein UI-Fehler? | Sofortmaßnahme |
|---|---|---|
| 🔴 Blocker | Kern-UI nicht bedienbar, zentrale Views fehlen/brechen | Änderung stoppen, UI-Kernpfad testen |
| 🟠 Relevant | Teilansichten/Interaktionen fehlerhaft, Hauptfluss noch möglich | betroffene UI-ID auf 🟡 setzen |
| 🟡 Hinweis | optischer oder randständiger Defekt ohne Kernflussbruch | dokumentieren und bündeln |

##### 7.5.1.3 Pro-UI-Feature mit Fehlercodes

| Feature-ID | Code | Regression |
|---|---|---|
| F-UI-001 | [src/widgetsystem/ui/visual_app.py](src/widgetsystem/ui/visual_app.py) | [tests/test_visual_app_extended.py](tests/test_visual_app_extended.py) |
| F-UI-002 | [src/widgetsystem/ui/visual_layer.py](src/widgetsystem/ui/visual_layer.py) | [tests/test_visual_layer.py](tests/test_visual_layer.py) |
| F-UI-003 | [src/widgetsystem/ui/config_panel.py](src/widgetsystem/ui/config_panel.py) | [tests/test_main_window_extended.py](tests/test_main_window_extended.py) |
| F-UI-004 | [src/widgetsystem/ui/inlay_titlebar.py](src/widgetsystem/ui/inlay_titlebar.py) | [tests/test_inlay_titlebar.py](tests/test_inlay_titlebar.py) |
| F-UI-005 | [src/widgetsystem/ui/floating_titlebar.py](src/widgetsystem/ui/floating_titlebar.py) | [tests/test_floating_titlebar_extended.py](tests/test_floating_titlebar_extended.py) |
| F-UI-006 | [src/widgetsystem/ui/floating_state_tracker.py](src/widgetsystem/ui/floating_state_tracker.py) | [tests/test_phase_2_floating_state_tracker.py](tests/test_phase_2_floating_state_tracker.py) |
| F-UI-007 | [src/widgetsystem/ui/tab_color_controller.py](src/widgetsystem/ui/tab_color_controller.py) | [tests/test_tabbar.py](tests/test_tabbar.py) |
| F-UI-008 | [src/widgetsystem/ui/tab_selector_monitor.py](src/widgetsystem/ui/tab_selector_monitor.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |
| F-UI-009 | [src/widgetsystem/ui/tab_selector_event_handler.py](src/widgetsystem/ui/tab_selector_event_handler.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |
| F-UI-010 | [src/widgetsystem/ui/tab_selector_visibility_controller.py](src/widgetsystem/ui/tab_selector_visibility_controller.py) | [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py) |
| F-UI-011 | [src/widgetsystem/ui/theme_editor.py](src/widgetsystem/ui/theme_editor.py) | [tests/test_theme_editor.py](tests/test_theme_editor.py) |
| F-UI-012 | [src/widgetsystem/ui/argb_color_picker.py](src/widgetsystem/ui/argb_color_picker.py) | [tests/test_argb_color_picker.py](tests/test_argb_color_picker.py) |
| F-UI-013 | [src/widgetsystem/ui/widget_features_editor.py](src/widgetsystem/ui/widget_features_editor.py) | [tests/test_widget_features_editor.py](tests/test_widget_features_editor.py) |
| F-UI-014 | [src/widgetsystem/ui/plugin_manager_dialog.py](src/widgetsystem/ui/plugin_manager_dialog.py) | [tests/test_plugin_system.py](tests/test_plugin_system.py) |

| Fehlercode | Trigger | Sollverhalten | Abweichung = Fehler |
|---|---|---|---|
| E-UI-001-A | App-Wrapper startet | visuelle App wird stabil aufgebaut | Initialisierungsabbruch |
| E-UI-002-A | VisualLayer-Init | Hauptoberfläche vollständig | fehlende Kernbereiche |
| E-UI-003-A | Konfigurationsänderung im Panel | konsistenter Runtime-Update | UI-Zustand driftet |
| E-UI-004-A | Inlay-Hover/Expand | erwartete Größen-/Sichtbarkeitswechsel | keine/falsche Reaktion |
| E-UI-005-A | Float/Dock-Wechsel | konsistenter Titelbar-Status | inkonsistenter Zustand |
| E-UI-006-A | Zustand speichern/laden | Floating-Status bleibt erhalten | Statusverlust |
| E-UI-007-A | Tab-Farbwechsel | Farbzustand korrekt angewendet | falsche Farben |
| E-UI-008-A | Tab-Monitoring | korrekte Erkennung von Tabzuständen | Fehltrigger |
| E-UI-009-A | Tab-Events | deterministische Eventbehandlung | Ereignisse fehlen/duplizieren |
| E-UI-010-A | Sichtbarkeitsumschaltung | Regeln greifen korrekt | TabSelector falsch sichtbar |
| E-UI-011-A | Live-Theme-Edit | Änderungen wirken direkt | keine/teilweise Übernahme |
| E-UI-012-A | ARGB-Eingabe | erwartete Farbwerte | fehlerhafte Konvertierung |
| E-UI-013-A | Feature-Edit | konsistente Widget-Feature-Updates | fehlerhafte Bindings |
| E-UI-014-A | Plugin-Dialog-Aktion | erwartete Plugin-Operation | Dialogaktion ohne Wirkung |

##### 7.5.1.4 Vorgehen bei UI-Fehlerverdacht

1. UI-ID in 7.5.1.1 bestimmen.
2. Fehlercode in 7.5.1.3 abgleichen.
3. Zugehörigen Test ausführen.
4. Matrixstatus (`Verify`, `Risiko`) anpassen.

### 7.6 Config & Schema

| ID | Feature | Prio | Verify | Risiko | Code | Test |
|---|---|---|---|---|---|---|
| F-CONF-001 | Layout-Konfigurationsmodell | P1 | 🟢 Verified | 🔴 Hoch | [config/layouts.json](config/layouts.json) | [tests/test_layout_factory.py](tests/test_layout_factory.py) |
| F-CONF-002 | Theme-Konfigurationsmodell | P1 | 🟢 Verified | 🔴 Hoch | [config/themes.json](config/themes.json) | [tests/test_theme_factory_extended.py](tests/test_theme_factory_extended.py) |
| F-CONF-003 | Panel-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/panels.json](config/panels.json) | [tests/test_panel_factory.py](tests/test_panel_factory.py) |
| F-CONF-004 | Menu-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/menus.json](config/menus.json) | [tests/test_menu_factory.py](tests/test_menu_factory.py) |
| F-CONF-005 | Tabs-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/tabs.json](config/tabs.json) | [tests/test_tabs_factory.py](tests/test_tabs_factory.py) |
| F-CONF-006 | DnD-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/dnd.json](config/dnd.json) | [tests/test_dnd_factory.py](tests/test_dnd_factory.py) |
| F-CONF-007 | Responsive-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/responsive.json](config/responsive.json) | [tests/test_responsive_factory.py](tests/test_responsive_factory.py) |
| F-CONF-008 | I18n-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/i18n.de.json](config/i18n.de.json) | [tests/test_i18n_factory.py](tests/test_i18n_factory.py) |
| F-CONF-009 | Listen-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/lists.json](config/lists.json) | [tests/test_list_factory.py](tests/test_list_factory.py) |
| F-CONF-010 | UIConfig-Konfigurationsmodell | P1 | 🟢 Verified | 🟠 Mittel | [config/ui_config.json](config/ui_config.json) | [tests/test_ui_config_factory_extended.py](tests/test_ui_config_factory_extended.py) |

#### 7.6.1 Config/Schema-Detailregister (lesbar, sortiert, fehlerklar)

##### 7.6.1.1 Schnellübersicht

| ID | Konfigurationsbereich | Primäre Dateien | Fehlerklasse bei Defekt |
|---|---|---|---|
| F-CONF-001 | Layout | [config/layouts.json](config/layouts.json), [schemas/layouts.schema.json](schemas/layouts.schema.json) | Pfad-/Strukturfehler |
| F-CONF-002 | Theme | [config/themes.json](config/themes.json), [schemas/themes.schema.json](schemas/themes.schema.json) | Theme-/Dateifehler |
| F-CONF-003 | Panel | [config/panels.json](config/panels.json), [schemas/panels.schema.json](schemas/panels.schema.json) | Struktur-/Validierungsfehler |
| F-CONF-004 | Menu | [config/menus.json](config/menus.json), [schemas/menus.schema.json](schemas/menus.schema.json) | Struktur-/Hierarchiefehler |
| F-CONF-005 | Tabs | [config/tabs.json](config/tabs.json), [schemas/tabs.schema.json](schemas/tabs.schema.json) | Gruppen-/Orientierungsfehler |
| F-CONF-006 | DnD | [config/dnd.json](config/dnd.json), [schemas/dnd.schema.json](schemas/dnd.schema.json) | Regel-/Mapping-Fehler |
| F-CONF-007 | Responsive | [config/responsive.json](config/responsive.json), [schemas/responsive.schema.json](schemas/responsive.schema.json) | Breakpoint-/Regelfehler |
| F-CONF-008 | I18n | [config/i18n.de.json](config/i18n.de.json), [config/i18n.en.json](config/i18n.en.json), [schemas/i18n.schema.json](schemas/i18n.schema.json) | Locale-/Key-Fehler |
| F-CONF-009 | Lists | [config/lists.json](config/lists.json), [schemas/lists.schema.json](schemas/lists.schema.json) | Baum-/Inhaltsfehler |
| F-CONF-010 | UIConfig | [config/ui_config.json](config/ui_config.json), [schemas/ui_config.schema.json](schemas/ui_config.schema.json) | Widget-/Property-Fehler |

##### 7.6.1.2 Fehlerdefinition (Config/Schema)

| Schweregrad | Wann ist es ein Config-Fehler? | Sofortmaßnahme |
|---|---|---|
| 🔴 Blocker | JSON nicht ladbar, Schema-Kernstruktur verletzt, zentrale Datei fehlt | Änderung stoppen, betroffene Datei + zugehörige Tests prüfen |
| 🟠 Relevant | valide JSON, aber semantisch falsche Werte (IDs, Areas, Typen) | betroffene CONF-ID auf 🟡 setzen |
| 🟡 Hinweis | optionaler Eintrag fehlt ohne unmittelbaren Kernbruch | dokumentieren und nachziehen |

##### 7.6.1.3 Pro-Konfigurationsbereich mit Fehlercodes

| Fehlercode | Scope | Trigger | Sollverhalten | Abweichung = Fehler |
|---|---|---|---|---|
| E-CONF-001-A | Layout | fehlendes/ungültiges `default_layout_id` | Default sauber auflösbar | kein valides Default-Layout |
| E-CONF-002-A | Theme | Theme ohne Dateireferenz | Theme wird korrekt verworfen | invalides Theme aktiv |
| E-CONF-003-A | Panel | ungültige `area`/Panelfelder | klare Validierung | ungültige Area akzeptiert |
| E-CONF-004-A | Menu | fehlerhafte Child-Struktur | konsistenter Menübaum | Baumbruch/fehlende Knoten |
| E-CONF-005-A | Tabs | ungültige `dock_area`/`orientation` | validierte Gruppen | ungültige Gruppen aktiv |
| E-CONF-006-A | DnD | inkonsistente Rules/Targets | konsistente Regelliste | unzulässige Moves möglich |
| E-CONF-007-A | Responsive | Breakpoint-Grenzen inkonsistent | deterministische Bereichslogik | Lücken/Überlappungen kritisch |
| E-CONF-008-A | I18n | fehlender Pflicht-Key | definierter Fallbackpfad | leerer oder falscher Text |
| E-CONF-009-A | Lists | fehlerhafte Nested-Items | konsistenter Listenbaum | Children-Verlust/Inkonsistenz |
| E-CONF-010-A | UIConfig | ungültige Widget-/Property-Typen | validiertes UI-Modell | fehlerhafte Typen im Runtime-UI |

##### 7.6.1.4 Vorgehen bei Config/Schema-Fehlerverdacht

1. CONF-ID in 7.6.1.1 bestimmen.
2. Fehlercode in 7.6.1.3 abgleichen.
3. Zugehörige Factory-/Subsystem-Tests ausführen.
4. Matrixstatus (`Verify`, `Risiko`) anpassen.

---

## 8) Regression-Checkliste (verbindlich nach jeder Änderung)

### 8.1 Scope-Check
- [ ] Betroffene Feature-IDs in Master-Matrix markiert
- [ ] Betroffene Layer markiert
- [ ] Risiko pro Feature aktualisiert

### 8.2 Konfigurations- und Schema-Konsistenz
- [ ] Geänderte JSON-Dateien in [config](config) geprüft
- [ ] Passende Schemas in [schemas](schemas) geprüft
- [ ] Pfadkonventionen konsistent

### 8.3 Teststufen (von spezifisch nach breit)
- [ ] Direkt betroffene Tests in [tests](tests) ausgeführt
- [ ] Subsystem-Tests des Layers ausgeführt
- [ ] Relevante Integrations-/Systemtests ausgeführt
- [ ] Kritische manuelle UI-Flows geprüft (falls UI betroffen)

### 8.4 Qualitätsgates
- [ ] Qualitätslauf über [scripts/check_quality.py](scripts/check_quality.py)
- [ ] Optional schnelle Zusammenfassung über [scripts/run_tests_summary.py](scripts/run_tests_summary.py)

### 8.5 Dokumentationspflege
- [ ] Feature-Matrix aktualisiert
- [ ] Veraltete „geplant“-Einträge in Doku bereinigt oder als historisch markiert
- [ ] Datum und Prüfer dokumentiert

Freigabekriterium:
- Keine offene P0/P1-Regression.
- Alle betroffenen Features: mindestens Implemented + Verified.

### 8.6 Pflicht-Regression je Kernfeature (Mindestumfang)

Bei Änderungen an den genannten Bereichen sind mindestens folgende Tests/Szenarien verpflichtend:

| Kernbereich | Matrix-IDs | Testpaket | Pflicht-Manuell |
|---|---|---|---|
| 🔴 Main/Window-Orchestrierung | F-CORE-001, F-CORE-002, F-UI-001, F-UI-002 | TP-MAIN | App starten, Panels öffnen/schließen, Basis-Workflow |
| 🔴 Tab-Subsystem | F-CTRL-007, F-UI-008, F-UI-009, F-UI-010 | TP-TAB | 1 Tab vs. 2+ Tabs, Bereichswechsel |
| 🔴 Floating-Subsystem | F-UI-005, F-UI-006 | TP-FLOAT | Float → Dock → Float Zyklus |
| 🔴 Theme-Subsystem | F-CORE-007, F-CORE-008, F-FAC-002, F-UI-011, F-UI-012 | TP-THEME | Theme live wechseln, Farben/Alpha prüfen |
| 🟠 Factory-Backbone | F-FAC-001..010 | TP-FACTORY | Stichprobe je geänderter Factory |
| 🟠 Governance/Qualität | F-GOV-001, F-GOV-002, F-QA-001, F-QA-002 | TP-GOV | Doku-Einstiegspfade prüfen |

Testpakete (lesbar, je Zeile ein Test):

- TP-MAIN
  - [tests/test_main_window.py](tests/test_main_window.py)
  - [tests/test_main_window_extended.py](tests/test_main_window_extended.py)
  - [tests/test_main_visual.py](tests/test_main_visual.py)
  - [tests/test_visual_layer.py](tests/test_visual_layer.py)

- TP-TAB
  - [tests/test_phase_1_tab_selector.py](tests/test_phase_1_tab_selector.py)
  - [tests/test_count_behavior.py](tests/test_count_behavior.py)
  - [tests/test_detection_methods.py](tests/test_detection_methods.py)
  - [tests/test_area_methods.py](tests/test_area_methods.py)

- TP-FLOAT
  - [tests/test_floating_titlebar_extended.py](tests/test_floating_titlebar_extended.py)
  - [tests/test_phase_2_floating_state_tracker.py](tests/test_phase_2_floating_state_tracker.py)
  - [tests/test_phase_2_float_button.py](tests/test_phase_2_float_button.py)
  - [tests/test_button_visibility.py](tests/test_button_visibility.py)

- TP-THEME
  - [tests/test_theme_manager.py](tests/test_theme_manager.py)
  - [tests/test_theme_profile.py](tests/test_theme_profile.py)
  - [tests/test_theme_factory_extended.py](tests/test_theme_factory_extended.py)
  - [tests/test_theme_editor.py](tests/test_theme_editor.py)
  - [tests/test_argb_color_picker.py](tests/test_argb_color_picker.py)
  - [tests/test_theme_system.py](tests/test_theme_system.py)

- TP-FACTORY
  - [tests/test_layout_factory.py](tests/test_layout_factory.py)
  - [tests/test_menu_factory.py](tests/test_menu_factory.py)
  - [tests/test_panel_factory.py](tests/test_panel_factory.py)
  - [tests/test_tabs_factory.py](tests/test_tabs_factory.py)
  - [tests/test_dnd_factory.py](tests/test_dnd_factory.py)
  - [tests/test_responsive_factory.py](tests/test_responsive_factory.py)
  - [tests/test_i18n_factory.py](tests/test_i18n_factory.py)
  - [tests/test_list_factory.py](tests/test_list_factory.py)
  - [tests/test_ui_config_factory_extended.py](tests/test_ui_config_factory_extended.py)

- TP-GOV
  - [tests/verify_agent_config.py](tests/verify_agent_config.py)
  - [tests/test_full_system.py](tests/test_full_system.py)

Empfohlene Ausführungsreihenfolge:
1. Direkt betroffene Testmodule
2. Betroffenes Subsystem gemäß Tabelle
3. [tests/test_full_system.py](tests/test_full_system.py)
4. [scripts/check_quality.py](scripts/check_quality.py)

---

## 9) Phase-Roadmap (arbeitsfähig)

### Phase P0 (Stabilität & Wahrheit der Daten)
- [x] Master-Matrix initial komplett ausfüllen
- [x] Doku-Drift bereinigen (Plan vs. Ist)
- [x] Pflicht-Regression je Kernfeature fest verknüpfen

Ergebnis:
- Eine verlässliche Source of Truth für Agenten und Menschen.

### Phase P1 (Kernfunktion robust halten)
- [ ] Tab/Floating/Theme/Factory-Kernflüsse als Pflichtpfad definieren
- [ ] Kritische manuelle Tests standardisieren
- [ ] Release-Kandidaten nur mit vollständigem P1-Check freigeben

Ergebnis:
- Höhere Änderungssicherheit bei Kernfeatures.

### Phase P2 (Qualitätserweiterung)
- [ ] Matrix um Risiko-Score und Änderungsfrequenz ergänzen
- [ ] Testlücken priorisiert schließen
- [ ] Konfigurationsvalidierung weiter härten

Ergebnis:
- Bessere Vorhersagbarkeit und weniger Folgeregressionen.

### Phase P3 (Optional/Optimierung)
- [ ] Automatisierte Generierung von Matrix-Teilfeldern
- [ ] Dashboards für Trends (Failrate, Flaky, Dauer)
- [ ] Historisierung pro Release

Ergebnis:
- Skalierbares Qualitätsmanagement.

---

## 10) Agenten-Arbeitsanweisung (kurz)

Bei jeder Aufgabe:
1. Betroffene Feature-IDs in diesem Dokument suchen.
2. Statusachsen prüfen.
3. Pflicht-Tests ausführen/zuordnen.
4. Nach Abschluss Matrix und Datum aktualisieren.

Wenn Feature nicht vorhanden:
- Neue Feature-ID anlegen.
- Pflichtfelder vollständig ausfüllen.
- Priorität und Risiko vergeben.
- Testpfad direkt definieren.

---

## 11) Offene Punkte / Konfliktregel

Wenn Doku und Code widersprechen:
- Vorrang hat der nachweisbare Codezustand plus Testbeleg.
- Doku ist anschließend verpflichtend nachzuführen.

---

## 12) Änderungsprotokoll

- 2026-03-23: Initiale Version erstellt.
