# Projekt-Audit-Bericht

**Datum:** 2026-03-23  
**Basis:** MASTER_ROADMAP_CHECKLIST.md  
**Scope:** Vollständige Bestandsprüfung — Dateien, Tests, Konsistenz, Code-Qualität

---

## Legende

| Symbol | Bedeutung |
|---|---|
| ✅ | OK — vollständig, korrekt |
| 🔴 | Kritisch — sofortiger Handlungsbedarf |
| 🟠 | Warnung — zeitnah klären |
| 🟡 | Hinweis — nachgelagert prüfen |
| ☑️ | Checklist-Item abgehakt |

---

## 1) Source-Code-Bestand — ✅ Vollständig

Alle im Checklist referenzierten Quell-Dateien sind vorhanden:

### `src/widgetsystem/core/` — ✅ 9/9
| ✅ | Datei |
|---|---|
| ☑️ | `config_io.py` |
| ☑️ | `gradient_system.py` |
| ☑️ | `main.py` |
| ☑️ | `main_visual.py` |
| ☑️ | `plugin_system.py` |
| ☑️ | `template_system.py` |
| ☑️ | `theme_manager.py` |
| ☑️ | `theme_profile.py` |
| ☑️ | `undo_redo.py` |

### `src/widgetsystem/factories/` — ✅ 10/10
| ✅ | Datei |
|---|---|
| ☑️ | `dnd_factory.py` |
| ☑️ | `i18n_factory.py` |
| ☑️ | `layout_factory.py` |
| ☑️ | `list_factory.py` |
| ☑️ | `menu_factory.py` |
| ☑️ | `panel_factory.py` |
| ☑️ | `responsive_factory.py` |
| ☑️ | `tabs_factory.py` |
| ☑️ | `theme_factory.py` |
| ☑️ | `ui_config_factory.py` |

### `src/widgetsystem/controllers/` — ✅ 7/7
| ✅ | Datei |
|---|---|
| ☑️ | `dnd_controller.py` |
| ☑️ | `dock_controller.py` |
| ☑️ | `layout_controller.py` |
| ☑️ | `responsive_controller.py` |
| ☑️ | `shortcut_controller.py` |
| ☑️ | `tab_subsystem.py` |
| ☑️ | `theme_controller.py` |

### `src/widgetsystem/ui/` — ✅ 14/14
| ✅ | Datei |
|---|---|
| ☑️ | `argb_color_picker.py` |
| ☑️ | `config_panel.py` |
| ☑️ | `floating_state_tracker.py` |
| ☑️ | `floating_titlebar.py` |
| ☑️ | `inlay_titlebar.py` |
| ☑️ | `plugin_manager_dialog.py` |
| ☑️ | `tab_color_controller.py` |
| ☑️ | `tab_selector_event_handler.py` |
| ☑️ | `tab_selector_monitor.py` |
| ☑️ | `tab_selector_visibility_controller.py` |
| ☑️ | `theme_editor.py` |
| ☑️ | `visual_app.py` |
| ☑️ | `visual_layer.py` |
| ☑️ | `widget_features_editor.py` |

### `config/` — ✅ 10/10 JSON-Konfigurationen
| ✅ | Datei |
|---|---|
| ☑️ | `dnd.json` |
| ☑️ | `i18n.de.json` |
| ☑️ | `i18n.en.json` |
| ☑️ | `layouts.json` |
| ☑️ | `lists.json` |
| ☑️ | `menus.json` |
| ☑️ | `panels.json` |
| ☑️ | `responsive.json` |
| ☑️ | `tabs.json` |
| ☑️ | `themes.json` |
| ☑️ | `ui_config.json` |

### `schemas/` — ✅ 10/10 Schema-Dateien
Alle Schemas vorhanden: `dnd`, `i18n`, `layouts`, `lists`, `menus`, `panels`, `responsive`, `tabs`, `themes`, `ui_config`.

### `config/profiles/` — ✅ 8 Profil-Dateien
`dark.json`, `dark_transparent.json`, `light.json`, `light_transparent.json`,
`midnight_blue.json`, `ocean_breeze.json`, `solid_dark.json`, `transparent.json`

---

## 2) Kritische Probleme 🔴

### 2.1 🔴 Inkonsistente Layout-XML-Pfade (3 verschiedene Pfade!)

| Bereich | Verwendeter Pfad |
|---|---|
| `config/layouts.json` | `"file": "layout.xml"` (Root-Verzeichnis) |
| `src/widgetsystem/core/main.py` | `Path.cwd() / "data" / "layout.xml"` |
| `src/widgetsystem/controllers/layout_controller.py` | `Path.cwd() / "data" / "layout.xml"` |
| `src/widgetsystem/core/main_visual.py` | `Path("layout.xml")` (Root-relativ) |

**Befund:** Drei verschiedene Pfadkonventionen für dieselbe Layout-XML-Datei.  
- Root `layout.xml` und `data/layout.xml` existieren beide, haben aber UNTERSCHIEDLICHEN Inhalt (1375 vs. 999 Zeichen).
- `config/layouts.json` und `main_visual.py` nutzen `layout.xml` (Root).
- `layout_controller.py` und `core/main.py` nutzen `data/layout.xml`.

**Aktion:** Einheitlichen Pfad festlegen (Empfehlung: `data/layout.xml`), `config/layouts.json` anpassen, Root-`layout.xml` entfernen oder in `data/` verschieben.

---

### 2.2 🔴 Fehlende Datei — `examples/demo.py`

In `AGENTS.md` referenziert:
```
python examples/demo.py  # Basis-Demo
```
Die Datei existiert **nicht**. Vorhandene Examples:
- `examples/complete_demo.py`
- `examples/demo_inlay_titlebar.py`
- `examples/phase_5_demo.py`

**Aktion:** Entweder `examples/demo.py` erstellen (als Alias/Wrapper für `complete_demo.py`) oder `AGENTS.md` korrigieren.

---

## 3) Warnungen 🟠

### 3.1 🟠 Doppelte JSON-Dateien in `data/` vs. `config/`

| Datei 1 | Datei 2 | Inhalt identisch? |
|---|---|---|
| `config/layouts.json` | `data/layouts.json` | ❌ Nein (unterschiedlich) |
| `config/themes.json` | `data/themes.json` | ❌ Nein (unterschiedlich) |

**Befund:** Es existieren zwei voneinander abweichende Versionen. Unklar, welche die aktive Quelle ist.  
**Aktion:** Rollen klären. Sind `data/*.json` Backups, Alt-Stände oder Vorlagen? Wenn veraltet → in `archive/` verschieben oder löschen. Klärung in Kommentar / Checklist dokumentieren.

---

### 3.2 🟠 Undokumentiertes Source-Modul: `src/widgetsystem/enums.py`

Datei vorhanden, aber:
- Keine Matrix-ID in der Checklist
- Kein dedizierter Test
- Kein Eintrag in `__all__`-Dokumentation

**Aktion:** Entweder Feature-ID `F-CORE-010` anlegen oder Datei einem bestehenden Feature zuordnen + Test ergänzen.

---

### 3.3 🟠 Undokumentiertes Modul: `src/widgetsystem/debug/`

Drei Dateien ohne Checklist-Eintrag:
- `debug_extended.py`
- `debug_redocking.py`
- `debug_tab_selector.py`

**Befund:** Debug-Module im Produktiv-Paket (`src/widgetsystem/`). Kein Test, kein Matrix-Eintrag.  
**Aktion:** Entscheiden — produktiv notwendig → dokumentieren; nur Debugtools → in `tests/` oder eigenes `debug/`-Verzeichnis außerhalb von `src/` verschieben.

---

### 3.4 🟠 Test-Dateien ohne pytest-Struktur — in Checklist referenziert

Diese Dateien sind im Checklist als Regressions-Tests geführt, haben aber **keine** `def test_`-Funktionen oder `class Test`:

| Datei | Checklist-Verwendung | Typ |
|---|---|---|
| `tests/test_features.py` | F-CORE-004, F-CORE-006, F-FAC-006, F-FAC-009 | Script (kein pytest) |
| `tests/test_full_system.py` | F-CORE-005, F-QA-001 | Script (kein pytest) |
| `tests/test_signals.py` | F-CTRL-006 | Script (kein pytest) |
| `tests/test_area_methods.py` | TP-TAB | Script (kein pytest) |
| `tests/test_button_visibility.py` | TP-FLOAT | Script (kein pytest) |
| `tests/test_count_behavior.py` | TP-TAB | Script (kein pytest) |
| `tests/test_detection_methods.py` | TP-TAB | Script (kein pytest) |
| `tests/test_phase_2_float_button.py` | TP-FLOAT | Script (kein pytest) |
| `tests/test_tabbar.py` | F-UI-007 | Script (kein pytest) |
| `tests/test_theme_system.py` | TP-THEME | Script (kein pytest) |

**Befund:** `pytest tests/` führt diese Dateien aus, findet aber keine Tests → sie erzeugen 0 Test-Ergebnisse. Damit ist die Regression-Abdeckung in der Checklist faktisch schlechter als angegeben.  
**Aktion:** Entweder in richtige pytest-Tests umwandeln (`def test_*`) oder als „manuelle Skripte" umkategorisieren und aus der Checklist-Regression herausnehmen.

---

## 4) Hinweise 🟡

### 4.1 🟡 Backup-Dateien im `config/`-Verzeichnis

| Datei | Status |
|---|---|
| `config/lists.json.backup` | Nicht in Checklist dokumentiert |
| `config/themes.json.backup` | Nicht in Checklist dokumentiert |

**Aktion:** Housekeeping-Regel für Backups in Checklist aufnehmen. Alternativ in `archive/` verschieben.

---

### 4.2 🟡 Test-Dateien nicht im Checklist (kein Matrix-Eintrag)

Diese Dateien existieren in `tests/`, sind aber in keiner Checklist-Regression registriert:

| Datei | Art |
|---|---|
| `tests/analyze_project.py` | Analyse-Skript (kein pytest) |
| `tests/screenshot_titlebar.py` | Manuelles Test-Skript |
| `tests/test_corrected.py` | Unklarer Zweck, kein pytest |
| `tests/test_simple.py` | Unklarer Zweck, kein pytest |
| `tests/test_tab.py` | Unklarer Zweck, kein pytest |
| `tests/test_titlebar_visibility.py` | Manuelles Skript |
| `tests/test_which_signal.py` | Debug-Skript |
| `tests/test_widget_signals.py` | Kein pytest |
| `tests/verify_titlebar_styles.py` | Verifikationsskript |

**Aktion:** Zuordnen, umbenennen (von `test_` auf `debug_` oder `check_`) oder in Checklist aufnehmen. Files mit `test_`-Prefix aber ohne pytest-Inhalt sind verwirrend.

---

### 4.3 🟡 `type: ignore` und `noqa`-Kommentare im Source

11 Suppression-Kommentare gefunden (akzeptabel, aber dokumentieren):

| Datei | Kommentar |
|---|---|
| `src/widgetsystem/core/theme_profile.py` | `# type: ignore[assignment]` (2×) — Qt gibt kein exaktes Tupel zurück |
| `src/widgetsystem/ui/floating_titlebar.py` | `# type: ignore[unreachable]` — defensive Nullprüfung |
| `src/widgetsystem/ui/inlay_titlebar.py` | `# noqa: ANN401` (7×) — Qt-Event-Handler erfordern `Any` |

**Bewertung:** Alle begründet durch Qt-API-Eigenheiten. Kein Handlungsbedarf, aber in Code-Review-Notizen aufnehmen.

---

### 4.4 🟡 Teilverifizierte Features (noch auf 🟡 Partially Tested)

Diese Features sind implementiert, aber nicht vollständig durch Tests abgesichert:

| Feature-ID | Name |
|---|---|
| F-QA-001 | Qualitäts-Gate Pipeline |
| F-CORE-004 | Undo/Redo Command-Stack |
| F-CORE-005 | Config Import/Export & Backup |
| F-CORE-006 | Template-System |
| F-CTRL-001 | DockController Lifecycle |
| F-CTRL-002 | LayoutController Save/Load/Reset |
| F-CTRL-003 | ThemeController Apply/Reload |
| F-CTRL-004 | DnDController Regeln |
| F-CTRL-005 | ResponsiveController Breakpoints |
| F-CTRL-006 | ShortcutController Aktionen/Shortcuts |
| F-UI-003 | ConfigurationPanel Runtime-Editor |
| F-UI-007 | TabColorController |
| F-UI-014 | PluginManagerDialog |

**Aktion:** Test-Lücken priorisiert schließen (→ Phase P2 im Checklist).

---

### 4.5 🟡 Drift-Kandidaten D-001 bis D-005 — alle noch offen

Alle 5 Drift-Kandidaten aus Checklist-Abschnitt 6.1 sind weiterhin mit Status „Offen":

| ID | Thema |
|---|---|
| D-001 | `THEME_SYSTEM_GUIDE.md` enthält „geplante Features" die bereits umgesetzt sind |
| D-002 | `THEME_IMPLEMENTATION_COMPLETE.md` nennt Theme-Editor als optional, obwohl implementiert |
| D-003 | `IMPLEMENTATION_COMPLETE.md` nennt optionale Phasen als umgesetzt |
| D-004 | `ANALYSE_SUMMARY.md` nennt Unit-Tests optional (veraltet) |
| D-005 | `PHASE_2_FLOAT_BUTTON.md` mentioned Z-Order Management ohne Matrix-ID |

**Aktion:** Doku-Dateien bereinigen oder historisch markieren (→ „Stand: YYYY-MM-DD veraltet").

---

### 4.6 🟡 Roadmap-Phasen P1–P3 — alle offen

| Phase | Offene Punkte |
|---|---|
| P1 (Kernfunktion robust) | 3 Punkte offen |
| P2 (Qualitätserweiterung) | 3 Punkte offen |
| P3 (Optional/Optimierung) | 3 Punkte offen |

---

## Nachtrag: Neue Drift-Kandidaten D-006 bis D-014 (verifiziert 2026-03-23)

Die folgenden 9 Punkte wurden nach dem initialen Audit zusätzlich identifiziert und hier vollständig geprüft.

### D-006 🟠 `themes/`-Verzeichnis nicht im Roadmap-Geltungsbereich

| Feld | Inhalt |
|---|---|
| Verzeichnis | `themes/` |
| Inhalt | `dark.qss`, `light.qss`, `transparent.qss` — 3 QSS-Stylesheets |
| Status | Vorhanden, funktional referenziert, aber **kein** Abschnitt in Roadmap/Matrix |
| Befund | `config/themes.json` referenziert die QSS-Pfade; ThemeFactory nutzt sie. Inhaltlich vollständig, nicht dokumentiert. |
| **Aktion** | Sektion 5.1 der Checklist anpassen: `themes/` als Geltungsbereich ergänzen. Kein Code-Handlungsbedarf. |

---

### D-007 🟠 `data/`-Verzeichnis nicht im Roadmap-Geltungsbereich

| Feld | Inhalt |
|---|---|
| Verzeichnis | `data/` |
| Inhalt | `layout.xml`, `layout_alt.xml`, `layouts.json`, `themes.json` |
| Status | **Teilweise** im Code genutzt (`data/layout.xml` von `layout_controller.py` und `core/main.py`) |
| Befund | Verzeichnis fehlt als expliziter Geltungsbereich. `data/layouts.json` und `data/themes.json` haben ungeklärte Rolle (bereits A-003). Root-`layout.xml` ist Konflikt aus A-001. |
| **Aktion** | Sektion 5.1 der Checklist um `data/` erweitern. Inhalt zeitgleich mit A-001/A-003 klären. |

---

### D-008 🟠 `examples/`-Verzeichnis nicht im Roadmap-Geltungsbereich

| Feld | Inhalt |
|---|---|
| Verzeichnis | `examples/` |
| Inhalt | `complete_demo.py`, `demo_inlay_titlebar.py`, `phase_5_demo.py` |
| Status | Vorhanden; `AGENTS.md` referenziert `examples/demo.py` (fehlend — A-002) und `examples/complete_demo.py` (vorhanden) |
| Befund | Kein Matrix-Eintrag, keine Tests für Demo-Lauffähigkeit. `phase_5_demo.py` ist undokumentiert. |
| **Aktion** | `examples/` als Geltungsbereich in Checklist aufnehmen. `phase_5_demo.py` dokumentieren. |

---

### D-009 🟡 `PROJECT_STRUCTURE_VERIFICATION.md` nicht in Roadmap referenziert

| Feld | Inhalt |
|---|---|
| Datei | `PROJECT_STRUCTURE_VERIFICATION.md` |
| Inhalt | Dokumentiert die Reorganisierung vom 07.03.2026 — Verschiebung von Debug-Dateien, Tests und Scripts in korrekte Verzeichnisse |
| Status | Historisches Dokument, aber inhaltlich relevant (erklärt u.a. Herkunft der Debug-Module in `src/widgetsystem/debug/`) |
| Befund | Wäre der Audit-Reporter bekannt gewesen, hätten A-005 (Debug-Module) und A-008 (Tests ohne pytest-Struktur) eine klare Herkunftserklärung erhalten. |
| **Aktion** | In Sektion 2 (Normative Referenzen) der Checklist als historischer Ankerpunkt ergänzen oder zumindest in Section 5 (Bestandsaufnahme) verlinken. |

---

### D-010 🔴 README.md „27 UI Components" ist faktisch falsch

| Feld | Inhalt |
|---|---|
| Claim | README.md Zeile 8, 29, 166, 202: `UI Components (27)` |
| Realität | `src/widgetsystem/ui/` hat **14 Python-Module** (ohne `__init__.py`): `argb_color_picker`, `config_panel`, `floating_state_tracker`, `floating_titlebar`, `inlay_titlebar`, `plugin_manager_dialog`, `tab_color_controller`, `tab_selector_event_handler`, `tab_selector_monitor`, `tab_selector_visibility_controller`, `theme_editor`, `visual_app`, `visual_layer`, `widget_features_editor` |
| Diskrepanz | 27 vs. 14 → Differenz von 13 |
| Ursache | README zählt vermutlich **Klassen** (nicht Dateien). Eine Datei kann mehrere Klassen enthalten. Oder die Zahl ist veraltet und bezog sich auf einen früheren Stand. |
| **Aktion** | README.md korrigieren: `UI Components (14 module files)` oder Clarification hinzufügen. Auch `docs/README.md` und `docs/UI_COMPONENTS.md` betroffen. |

---

### D-011 🟠 Root-`layout.xml` — Zweck nach wie vor unklar

| Feld | Inhalt |
|---|---|
| Datei | `layout.xml` im Projekt-Root |
| Inhalt | 1375 Zeichen — unterschiedlich von `data/layout.xml` (999 Zeichen) |
| Status | Nicht in Roadmap, wird von `config/layouts.json` (`"file": "layout.xml"`) und `core/main_visual.py` (`Path("layout.xml")`) referenziert |
| Befund | Ist der **aktive** Layout-Stand für `main_visual.py`. `data/layout.xml` ist die Version für `layout_controller.py` + `core/main.py`. Es existieren also **zwei aktive, aber voneinander abweichende** Layout-XMLs. Das ist keine Duplikation sondern ein echter Konfigurationssplit. |
| **Aktion** | Entscheidung erzwingen: Welches Layout ist die einzige Quelle? Zusammenführen. (Verstärkt A-001.) |

---

### D-012 🔴 Feature-Matrix erfasst 14 UI-Features (F-UI-001..014), README nennt 27

| Feld | Inhalt |
|---|---|
| Matrix | F-UI-001 bis F-UI-014 (14 Einträge) |
| README | „27 UI Components" |
| Tatsächliche Module | 14 Dateien in `ui/` |
| **Befund** | Die Diskrepanz kommt aus einem falschen README-Wert (D-010), **nicht** aus fehlenden Matrix-Einträgen. Die Matrix ist vollständig für alle vorhandenen UI-Module. Es fehlen **keine F-UI-015..027**, weil es keine 27 Module gibt. |
| **Aktion** | README korrigieren (D-010). Matrix-Vollständigkeit ist ✅ bestätigt. |

---

### D-013 🟠 Test-Modul-Anzahl: README „49", Repo tatsächlich 54

| Feld | Inhalt |
|---|---|
| README-Claim | `tests/ — Test Suite (49 modules)` |
| Tatsächlich | **54 .py-Dateien** in `tests/` |
| Differenz | +5 gegenüber README-Angabe |
| Ursache | README wurde nach dem 07.03.2026-Reorganisierungsschritt nicht aktualisiert |
| **Aktion** | README.md auf 54 korrigieren. Zusätzlich: Die 5 bisher nicht gezählten Dateien identifizieren (wahrscheinlich die in `PROJECT_STRUCTURE_VERIFICATION.md` nachträglich verscho­benen Test-Skripte). |

---

### D-014 🟠 `archive/`-Verzeichnis nicht im Roadmap-Geltungsbereich

| Feld | Inhalt |
|---|---|
| Verzeichnis | `archive/` |
| Inhalt | `profiles-old/` (5 JSON-Profildateien), `themes-old/` (enthält `light.qss`) |
| Status | `archive/profiles-old/*.json` sind **identisch** mit 5 aktiven Dateien in `config/profiles/` (per Hash bestätigt). `archive/themes-old/light.qss` ist identisch mit `themes/light.qss`. |
| Befund | `archive/` enthält echte 1:1-Duplikate aktiver Dateien — reine Archivkopien. Kein Geltungsbereich in Roadmap. |
| **Aktion** | `archive/` in Checklist als explizit ausgeschlossenen/archivierten Bereich vermerken. Kein Code-Handlungsbedarf, aber das Verzeichnis sollte nicht in Produktiv-Builds eingebunden werden. |

---

### Zusammenfassung Nachprüfung D-012 Kernbefund

> **D-012 ist kein echtes Problem.** Die Feature-Matrix ist vollständig.  
> Die „13 fehlenden UI-Komponenten" existieren **nicht** — die README-Zahl 27 ist falsch.  
> Tatsächlich gibt es 14 UI-Module (alle in der Matrix erfasst). Handlungsbedarf liegt beim README, nicht bei der Matrix.

---

## 5) Zusammenfassung — Priorisierte Aktionsliste

| Prio | ID | Problem | Status | Maßnahme |
|---|---|---|---|---|
| 🔴 1 | A-001 | Layout-XML: 3 verschiedene Pfade + 2 aktive Dateien mit unterschiedlichem Inhalt | 🔴 **Offen** | Einheitlicher Pfad `data/layout.xml`; `config/layouts.json` + `main_visual.py` anpassen; Root-`layout.xml` entfernen oder mergen |
| 🔴 2 | A-002 | `examples/demo.py` fehlt (in AGENTS.md referenziert) | ✅ **Erledigt** | `AGENTS.md` auf `examples/demo_inlay_titlebar.py` korrigiert |
| 🔴 3 | A-011 | README.md zeigt „27 UI Components" — tatsächlich 14 Module | ✅ **Erledigt** | README.md + docs/README.md korrigiert (14 UI, 44 Source, 54 Tests) |
| 🔴 4 | A-012 | README.md zeigt „49 test modules" — tatsächlich 54 Dateien | ✅ **Erledigt** | Gemeinsam mit A-011 behoben |
| 🟠 5 | A-003 | `data/layouts.json` und `data/themes.json` — Rolle unklar | 🟠 **Offen** | Klären: Backup oder aktive Quelle? Archivieren oder dokumentieren |
| 🟠 6 | A-004 | `src/widgetsystem/enums.py` ohne Matrix-ID und Test | 🟠 **Offen** | Feature-ID anlegen oder zu bestehendem Feature zuordnen |
| 🟠 7 | A-005 | `src/widgetsystem/debug/` — 3 Debug-Module im Produktivpaket | 🟠 **Offen** | Explizit als Debug-Unterpaket dokumentieren; Checklist-Eintrag anlegen |
| 🟠 8 | A-006 | 10 Checklist-referenzierte Testdateien ohne pytest-Struktur | 🟠 **Offen** | In echte pytest-Tests umwandeln oder als manuelle Skripte kategorisieren |
| 🟠 9 | A-013 | `themes/`, `data/`, `examples/`, `archive/` fehlen im Geltungsbereich | ✅ **Erledigt** | Checklist Sektion 1.1 um alle 4 Verzeichnisse + archive-Ausschluss erweitert |
| 🟠 10 | A-014 | `PROJECT_STRUCTURE_VERIFICATION.md` nirgends in Roadmap verlinkt | ✅ **Erledigt** | Als historischen Ankerpunkt in Checklist Sektion 1.1 aufgenommen |
| 🟡 11 | A-007 | Backup-Dateien `config/*.backup` ohne Housekeeping-Regel | 🟡 **Offen** | In `archive/` verschieben oder Regel in Checklist aufnehmen |
| 🟡 12 | A-008 | 9 Testdateien in `tests/` ohne Checklist-Eintrag | 🟡 **Offen** | Zuordnen, umbenennen (`test_` → `debug_`/`check_`) oder in Checklist aufnehmen |
| 🟡 13 | A-009 | 13 Features noch `Partially Tested` | 🟡 **Offen** | Test-Lücken schließen (Prio: F-CORE-004, F-CORE-005, F-CTRL-001, F-CTRL-002) |
| 🟡 14 | A-010 | 5 Drift-Kandidaten D-001..D-005 noch offen | 🟡 **Offen** | Doku-Dateien bereinigen oder als historisch markieren |
| 🟡 15 | A-015 | `archive/` enthält 1:1-Duplikate aktiver Profile und `light.qss` | ✅ **Erledigt** | Als archiviert/ausgeschlossen in Checklist vermerkt |

---

## 6) Abschluss-Checkliste (Regression-Status)

### 8.1 Scope-Check
- [x] Alle Feature-IDs in Master-Matrix geprüft
- [x] Alle Layer überprüft (Core, Controller, Factory, UI, Config)
- [x] Alle Verzeichnisse inventarisiert (inkl. `themes/`, `data/`, `examples/`, `archive/`)
- [ ] Risiko pro Feature nach A-006 aktualisieren (nach Test-Konvertierung)

### 8.2 Konfigurations-Konsistenz
- [ ] Layout-XML-Pfad-Inkonsistenz beheben (A-001 / D-011)
- [x] Schemas vorhanden und vollständig
- [ ] `data/*.json` Rolle klären (A-003 / D-007)

### 8.3 Teststufen
- [x] Alle referenzierten pytest-Tests physisch vorhanden
- [ ] 10 Script-Tests auf pytest-Format umstellen (A-006)
- [ ] 13 Partially-Tested-Features aufwerten (A-009)

### 8.4 Qualitätsgates
- [ ] `scripts/check_quality.py` vollständig ausführen und Ergebnis dokumentieren

### 8.5 Dokumentation
- [x] 135 lokale Links in Checklist validiert — 0 fehlende Zieldateien
- [x] 6 Inhalts-Duplikate per Hash identifiziert (alle in `archive/` — unkritisch)
- [x] README.md: „27 UI" → **14** korrigiert (A-011) ✅
- [x] README.md: „49 Tests" → **54** korrigiert (A-012) ✅
- [x] README.md: „41 Source" → **44** korrigiert (A-011 Nebenkorrektur) ✅
- [x] `docs/README.md`: Zahlen identisch korrigiert ✅
- [x] `AGENTS.md`: `examples/demo.py` → `examples/demo_inlay_titlebar.py` korrigiert (A-002) ✅
- [x] MASTER_ROADMAP_CHECKLIST Sektion 1.1: `themes/`, `data/`, `examples/`, `archive/` als Geltungsbereich ergänzt (A-013) ✅
- [x] MASTER_ROADMAP_CHECKLIST: `PROJECT_STRUCTURE_VERIFICATION.md` als historischer Ankerpunkt verlinkt (A-014) ✅
- [x] MASTER_ROADMAP_CHECKLIST Sektion 6.2: D-006 bis D-014 tabelliert ✅
- [ ] Drift-Kandidaten D-001 bis D-005 bereinigen (A-010) — noch offen
- [ ] Layout-XML-Pfad-Inkonsistenz beheben (A-001 / D-011) — noch offen
- [x] Audit-Report erstellt und vollständig (dieses Dokument)

---

*Erstellt: 2026-03-23 | Erweitert: 2026-03-23 (D-006..D-014, A-002/A-011..A-014 umgesetzt) | Basis: vollständige Bestandsprüfung gegen MASTER_ROADMAP_CHECKLIST.md*
