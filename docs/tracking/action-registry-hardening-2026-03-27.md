# Action Registry Hardening Log (2026-03-27)

## Ziel
- Produktionsreife von Action-Registry-Funktion herstellen.
- Latenz bei Splitter-/Corner-Handle-Bewegung reduzieren.
- Vollständige Nachverfolgbarkeit und Rollback-Backup herstellen.
- Demo-/Runtime-Artefakte aus Git-Rauschen herausfiltern.

## Backup & Tracking
- Vollbackup erstellt:
  - `archive/backups/2026-03-27/demo_action_registry.py.bak`
- Git-Status-Snapshot erstellt:
  - `docs/tracking/git-status-2026-03-27.txt`

## Architektur-Anpassung
- Produktive Implementierung nach `src/` gespiegelt:
  - `src/widgetsystem/core/action_registry_window.py`
- Launcher in `examples/` auf Thin-Entry umgestellt:
  - `examples/demo_action_registry.py`
- Damit bleibt der Startweg erhalten, die Fachlogik liegt aber paketkonform in `src/widgetsystem/core/`.

## Performance-/Latenz-Optimierung

### 1) Polling entfernt, Debounce eingeführt
Datei: `src/widgetsystem/core/action_registry_window.py`
- Statt periodischem 250ms-Dauertimer wird jetzt ein SingleShot-Debounce verwendet.
- Neue Methoden:
  - `_schedule_splitter_refresh()`
  - `_ensure_splitter_connections()`
  - `_on_splitter_moved_runtime()`
- Effekt:
  - deutlich weniger Dauerlast,
  - präzisere Reaktion auf tatsächliche Layoutänderungen.

### 2) Doppelte Signal-Verbindungen verhindert
Datei: `src/widgetsystem/core/action_registry_window.py`
- `splitterMoved` wird mit Property-Guard nur einmal verbunden:
  - `ws_splitter_moved_connected`.
- Effekt:
  - keine Signal-Vervielfachung,
  - geringerer Event-Overhead.

### 3) Corner-Handle-Sync günstiger
Datei: `src/widgetsystem/factories/splitter_factory.py`
- Peer-Sync nicht mehr auf jedem `mouseMoveEvent`.
- Neue Factory-Methode:
  - `sync_corner_handles()`
- Sync erfolgt jetzt gezielt über Runtime-Callback und bei strukturellen Updates.
- Effekt:
  - spürbar geringere Drag-Latenz bei vielen Handles.

## Git-Noise / Schrottfilter
Datei: `.gitignore`
- Hinzugefügt (Artefakte):
  - `config/.backup/`
  - `config/custom_actions.json`
  - `pytest_output.txt`
  - `test_batch.txt`
  - `all_phase1_tests.txt`
  - `phase1_complete_summary.txt`
  - `phase1_test_summary.txt`
  - `phase1_tests_all.txt`
  - `chevron_tests.txt`
  - `screenshot_tabs.png`
  - `test_x_icon.png`

## Verifikation
- Syntax geprüft:
  - `python -m py_compile examples/demo_action_registry.py src/widgetsystem/factories/splitter_factory.py`
- Runtime-Smoke-Test ausgeführt:
  - `python examples/demo_action_registry.py`

## Nächste Schritte (empfohlen)
1. Git gezielt stage:
   - `examples/demo_action_registry.py`
   - `src/widgetsystem/core/action_registry_window.py`
   - `src/widgetsystem/factories/splitter_factory.py`
   - `.gitignore`
   - `docs/tracking/*`
   - `archive/backups/2026-03-27/demo_action_registry.py.bak`
2. Danach optional:
   - vorhandene untracked Test-/Demo-Skripte in separatem Cleanup-Commit aufräumen.
