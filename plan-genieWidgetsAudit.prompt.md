# Plan: Genie_Widgets Audit — Agent Execution Todo List

Basierend auf `PROJECT_AUDIT_REPORT.md` (Stand 2026-03-23) bleiben 8 Action-Items offen:
**A-001, A-003, A-004, A-005, A-006, A-007, A-008, A-009, A-010**

Bereits erledigt (nicht wiederholen): A-002, A-011, A-012, A-013, A-014, A-015

---

## Phase 1 — Kritischer Code-Fix: Layout-XML (A-001)

*Alle anderen Phasen blockieren auf diesen Fix — deshalb zuerst.*

1. Lies beide XML-Dateien: `layout.xml` (Root, 1375 Zeichen) und `data/layout.xml` (999 Zeichen). Vergleiche den Inhalt, identifiziere welche Docking-Konfiguration aktueller/vollständiger ist.
2. Merge: Übertrage fehlende Konfiguration nach `data/layout.xml` — das ist die kanonische Zieldatei (matcht `main.py` + `layout_controller.py`).
3. `config/layouts.json` anpassen: `"file": "layout.xml"` → `"file": "data/layout.xml"` (2× — erster und zweiter Eintrag im `layouts`-Array)
4. `src/widgetsystem/core/main_visual.py` Zeile 53 anpassen: `Path("layout.xml")` → `Path.cwd() / "data" / "layout.xml"`
5. Root `layout.xml` nach `archive/` verschieben oder löschen (nach Merge)
6. Verifikation: `grep -r "layout.xml" config/ src/` → kein Treffer ohne `data/`-Prefix

**Betroffene Dateien:**
- `config/layouts.json`
- `src/widgetsystem/core/main_visual.py`
- `layout.xml` (Root — entfernen)
- `data/layout.xml` (Ziel des Merge)

---

## Phase 2 — Dateirollen klären (A-003, A-007)

*Schritte 7 und 8 sind unabhängig voneinander — parallel ausführbar.*

7. **(A-003)** Vergleiche Inhalt von `data/layouts.json` vs. `config/layouts.json` und `data/themes.json` vs. `config/themes.json`. Falls `data/*.json` veraltete Runtime-Kopien sind: nach `archive/` verschieben. Ergänze in `MASTER_ROADMAP_CHECKLIST.md` Sektion 5.1 unter `data/` einen Kommentar: *"`data/layouts.json` und `data/themes.json` sind veraltete Runtime-Kopien, archiviert 2026-03-23."*
8. **(A-007)** Lies `src/widgetsystem/core/config_io.py` — prüfe ob `.backup`-Erzeugung intentional ist. Ergänze in `MASTER_ROADMAP_CHECKLIST.md` Sektion 5.1 unter `config/`: *"`.backup`-Dateien (`config/lists.json.backup`, `config/themes.json.backup`) werden von `config_io.py` automatisch erzeugt und gehören nicht zur aktiven Konfiguration."*

**Betroffene Dateien:**
- `data/layouts.json`, `data/themes.json`
- `config/layouts.json`, `config/themes.json`
- `src/widgetsystem/core/config_io.py` (nur lesen)
- `MASTER_ROADMAP_CHECKLIST.md`

---

## Phase 3 — Source-Code-Dokumentation (A-004, A-005)

*Schritte 9 und 10 sind unabhängig voneinander — parallel ausführbar.*

9. **(A-004)** Lies `src/widgetsystem/enums.py` und inventarisiere alle Enum-Klassen. Füge in `MASTER_ROADMAP_CHECKLIST.md` Feature-Matrix einen neuen Eintrag ein: `F-CORE-010 | EnumTypes | P1 | ✅ Implemented | 🟡 Partially Tested`. Erstelle `tests/test_enums.py` mit mindestens 3 `def test_*`-Funktionen (z.B. Enum-Werte prüfen, Enum-Vergleiche, Enum-Membership).
10. **(A-005)** Prüfe ob `src/widgetsystem/debug/debug_extended.py`, `debug_redocking.py`, `debug_tab_selector.py` von Produktivcode importiert werden (`grep -r "from widgetsystem.debug" src/widgetsystem/core src/widgetsystem/controllers src/widgetsystem/factories src/widgetsystem/ui`). Falls kein Import: nach `tests/debug/` verschieben und alle Importe updaten. Falls doch importiert: neue Sektion `F-DEBUG-001..003` in `MASTER_ROADMAP_CHECKLIST.md` ergänzen.

**Betroffene Dateien:**
- `src/widgetsystem/enums.py` (lesen)
- `src/widgetsystem/debug/` (evaluieren)
- `MASTER_ROADMAP_CHECKLIST.md`
- `tests/test_enums.py` (neu erstellen)

---

## Phase 4 — Teststruktur bereinigen (A-006, A-008)

*A-006 vor A-008, da A-006 Coverage-kritisch ist. Schritte 11–20 sind parallel ausführbar.*

### A-006 — 10 checklist-referenzierte Testdateien ohne pytest-Struktur

Strategie: Bestehende Logik in `def test_*`-Funktionen wrappen (nicht umbenennen — erhält Checklist-Coverage ohne Matrix-Änderung). `QApplication`-Instanz ggf. als pytest-Fixture einrichten (vgl. `.github/instructions/testing.instructions.md`).

11. `tests/test_features.py` → bestehende Logik in `def test_*`-Funktionen wrappen
    - Checklist-Features: F-CORE-004, F-CORE-006, F-FAC-006, F-FAC-009
12. `tests/test_full_system.py` → gleiche Strategie
    - Checklist-Features: F-CORE-005, F-QA-001
13. `tests/test_signals.py` → wrappen
    - Checklist-Feature: F-CTRL-006
14. `tests/test_area_methods.py` → wrappen
    - Checklist-Feature: TP-TAB
15. `tests/test_button_visibility.py` → wrappen
    - Checklist-Feature: TP-FLOAT
16. `tests/test_count_behavior.py` → wrappen
    - Checklist-Feature: TP-TAB
17. `tests/test_detection_methods.py` → wrappen
    - Checklist-Feature: TP-TAB
18. `tests/test_phase_2_float_button.py` → wrappen
    - Checklist-Feature: TP-FLOAT
19. `tests/test_tabbar.py` → wrappen
    - Checklist-Feature: F-UI-007
20. `tests/test_theme_system.py` → wrappen
    - Checklist-Feature: TP-THEME

### A-008 — 9 Testdateien ohne Checklist-Eintrag

Strategie: `check_`-Prefix für alle `test_*`-Dateien ohne pytest-Inhalt (verhindert Verwechslung mit pytest-Discovery). Reine Analyse-/Debug-Skripte nach `scripts/` verschieben.

21. `tests/analyze_project.py` → nach `scripts/analyze_project.py` verschieben
22. `tests/screenshot_titlebar.py` → umbenennen zu `tests/check_screenshot_titlebar.py`
23. `tests/test_corrected.py` → lesen, Inhalt prüfen; dann löschen oder umbenennen zu `tests/check_corrected.py`
24. `tests/test_simple.py` → lesen, Inhalt prüfen; dann löschen oder umbenennen zu `tests/check_simple.py`
25. `tests/test_tab.py` → lesen, Inhalt prüfen; dann löschen oder umbenennen zu `tests/check_tab.py`
26. `tests/test_titlebar_visibility.py` → umbenennen zu `tests/check_titlebar_visibility.py`
27. `tests/test_which_signal.py` → umbenennen zu `tests/check_which_signal.py`
28. `tests/test_widget_signals.py` → lesen; wenn sinnvoll wrappen (→ A-006-Strategie), sonst umbenennen zu `tests/check_widget_signals.py`
29. `tests/verify_titlebar_styles.py` → belassen (`verify_`-Prefix ist unproblematisch, kein pytest-Konflikt)

---

## Phase 5 — Test-Coverage erhöhen (A-009)

*Depends on Phase 4 (A-006-Fixes decken automatisch F-CORE-004/005/006, F-CTRL-006, F-UI-007 ab).*

Für jedes der verbleibenden 8 "Partially Tested"-Features mindestens einen neuen echten pytest-Test schreiben:

30. **F-CTRL-001 (DockController Lifecycle):** neue `def test_dock_controller_lifecycle()` in `tests/test_main_window_extended.py`
31. **F-CTRL-002 (LayoutController Save/Load/Reset):** neue Tests in `tests/test_main_window.py`
32. **F-CTRL-003 (ThemeController Apply/Reload):** neue Tests in `tests/test_theme_manager.py`
33. **F-CTRL-004 (DnDController Regeln):** neue Tests in `tests/test_dnd_factory.py`
34. **F-CTRL-005 (ResponsiveController Breakpoints):** neues `tests/test_responsive_controller.py` erstellen
35. **F-UI-003 (ConfigurationPanel Runtime-Editor):** neues `tests/test_config_panel.py` erstellen
36. **F-UI-014 (PluginManagerDialog):** neues `tests/test_plugin_manager_dialog.py` erstellen
37. **Nach erfolgreichem `pytest`:** alle 13 Features in `MASTER_ROADMAP_CHECKLIST.md` von `🟡 Partially Tested` → `🟢 Verified` setzen

**Betroffene Dateien:**
- `tests/test_main_window_extended.py`, `tests/test_main_window.py`, `tests/test_theme_manager.py`, `tests/test_dnd_factory.py`
- Neu: `tests/test_responsive_controller.py`, `tests/test_config_panel.py`, `tests/test_plugin_manager_dialog.py`
- `MASTER_ROADMAP_CHECKLIST.md`

---

## Phase 6 — Dokumentations-Drift (A-010)

*Vollständig unabhängig von allen anderen Phasen. Alle 5 Schritte parallel ausführbar.*

38. **D-001** → `docs/THEME_SYSTEM_GUIDE.md`: Header-Block am Anfang des Dokuments einfügen:
    ```
    > **Status 2026-03-23:** Phase-2-Features sind vollständig implementiert —
    > F-UI-011 ThemeEditor, F-UI-012 ARGBColorPicker. Die nachfolgenden Abschnitte
    > beschreiben den historischen Planungsstand.
    ```
39. **D-002** → `docs/THEME_IMPLEMENTATION_COMPLETE.md`: "Phase 2 (Optional): Live Theme Editor" ersetzen durch:
    `"✅ Implementiert — F-UI-011 ThemeEditor + F-UI-012 ARGBColorPicker (seit 2026-03-07)"`
40. **D-003** → `docs/IMPLEMENTATION_COMPLETE.md`: Jede "optional phase"-Zeile mit der korrekten Feature-ID annotieren; Hinweis-Header hinzufügen: *"Historischer Stand — alle nachfolgend genannten Phasen sind umgesetzt. Aktuelle IDs: F-CORE-004..006, F-FAC-009..010, F-UI-003."*
41. **D-004** → `docs/ANALYSE_SUMMARY.md`: Blockquote am Anfang einfügen:
    ```
    > ⚠️ **Historischer Stand (vor 2026-03-07).** Unit-Tests sind vorhanden in `tests/`.
    > Die nachfolgende Analyse ist veraltet und dient nur als Referenz.
    ```
42. **D-005** → `MASTER_ROADMAP_CHECKLIST.md`: Neue Matrix-Zeile unter F-UI-014 einfügen:
    `F-UI-015 | Z-Order Management | P3 | 🗓 Planned | ⬜ Untested` mit Verweis auf `docs/PHASE_2_FLOAT_BUTTON.md`

---

## Verifikation (nach allen Phasen)

```bash
# 1. Layout-XML: nur noch data/layout.xml darf auftauchen
grep -r "layout.xml" config/ src/
# Erwartung: kein Treffer ohne data/-Prefix

# 2. pytest: 0 Fehler, mehr Tests als vorher
pytest tests/ -q

# 3. Keine test_*-Dateien mit 0 Tests
pytest --collect-only -q 2>&1 | grep "<Module"

# 4. Keine Partially-Tested-Einträge mehr
grep "Partially Tested" MASTER_ROADMAP_CHECKLIST.md

# 5. Import-Test
python -c "from widgetsystem.core.main_visual import MainVisualWindow; print('OK')"
```

---

## Entscheidungen (für den ausführenden Agent)

| Thema | Entscheidung |
|---|---|
| Kanonischer Layout-Pfad | `data/layout.xml` — matcht `main.py` + `layout_controller.py` |
| A-006-Strategie | Wrapping bevorzugen (nicht umbenennen), erhält Checklist-Abdeckung |
| A-008-Strategie | `check_`-Prefix für `test_*`-Dateien ohne pytest-Inhalt |
| data/*.json | Als veraltete Kopien nach `archive/` verschieben (nach Inhaltsprüfung in A-003) |
| debug/ Module | In `src/widgetsystem/debug/` belassen sofern importiert; sonst nach `tests/debug/` |

## Scope

**Enthalten**: A-001, A-003, A-004, A-005, A-006, A-007, A-008, A-009, A-010
**Ausgeschlossen**: A-002, A-011..A-015 (bereits erledigt)
