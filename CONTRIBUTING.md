# Contributing Guide - Genie Widgets

## Git Flow Workflow (2-Mann-Team)

### Branch-Struktur

```
main (Production)     ← Nur stabile Releases, geschützt
  │
develop (Integration) ← Alle Features werden hier integriert
  │
  ├── feature/user-a/beschreibung
  └── feature/user-b/beschreibung
```

### Branch-Regeln

| Branch | Zweck | Wer darf pushen | Merge via |
|--------|-------|-----------------|-----------|
| `main` | Production-Release | Niemand direkt | PR von `develop` (mit Review) |
| `develop` | Integration | Niemand direkt | PR von Feature-Branches |
| `feature/*` | Neue Features | Ersteller | - |
| `bugfix/*` | Bug-Fixes | Ersteller | - |
| `hotfix/*` | Kritische Fixes | Ersteller | PR direkt zu `main` + `develop` |

---

## Workflow für neue Features

### 1. Feature-Branch erstellen
```bash
# Immer von develop ausgehen!
git checkout develop
git pull origin develop
git checkout -b feature/dein-name/feature-beschreibung
```

### 2. Arbeiten und committen
```bash
# Regelmäßig committen mit aussagekräftigen Messages
git add .
git commit -m "feat(modul): Beschreibung der Änderung"

# Regelmäßig develop reinholen (mindestens 1x täglich)
git fetch origin
git merge origin/develop
```

### 3. Feature fertig → Pull Request
```bash
# Letzter Stand von develop
git fetch origin
git merge origin/develop

# Konflikte lösen falls nötig, dann pushen
git push -u origin feature/dein-name/feature-beschreibung
```

Dann auf GitHub: **Pull Request erstellen** → Base: `develop`

### 4. Code Review
- Der andere Teammitglied reviewt
- Mindestens 1 Approval erforderlich
- Nach Approval: **Squash and Merge**

---

## Workflow für Releases

### Release vorbereiten
```bash
# Release-Branch von develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0
```

### Release finalisieren
1. Version bumpen, Changelog aktualisieren
2. PR zu `main` erstellen
3. Nach Merge: Tag erstellen
4. `main` zurück in `develop` mergen

```bash
git checkout main
git pull
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Zurück zu develop mergen
git checkout develop
git merge main
git push origin develop
```

---

## Hotfix-Workflow (kritische Bugs in Production)

```bash
# Direkt von main
git checkout main
git pull
git checkout -b hotfix/kritischer-bug

# Fix implementieren, dann PR zu BEIDEN:
# 1. PR zu main (schneller Fix)
# 2. PR zu develop (damit Fix nicht verloren geht)
```

---

## Commit Message Convention

Format: `type(scope): beschreibung`

### Types
- `feat` - Neues Feature
- `fix` - Bug Fix
- `docs` - Dokumentation
- `style` - Formatting, keine Code-Änderung
- `refactor` - Code-Umstrukturierung
- `test` - Tests hinzufügen/ändern
- `chore` - Maintenance, Dependencies

### Beispiele
```
feat(tabs): Add drag-and-drop support for tab reordering
fix(theme): Resolve dark mode contrast issues
docs(readme): Update installation instructions
refactor(controller): Extract tab logic into separate module
```

---

## Tägliche Routine (Best Practice)

### Morgens
```bash
git checkout develop
git pull origin develop
git checkout feature/dein-aktueller-branch
git merge origin/develop
```

### Vor Feierabend
```bash
git add .
git commit -m "wip: Beschreibung des Stands"
git push
```

### Vor jedem PR
```bash
git fetch origin
git merge origin/develop
# Tests laufen lassen
python -m pytest
```

---

## Konflikt-Vermeidung

1. **Kleine, fokussierte PRs** - Max 1-2 Tage Arbeit pro PR
2. **Häufig develop mergen** - Mindestens 1x täglich
3. **Kommunikation** - Vor größeren Refactorings abstimmen
4. **Dateien aufteilen** - Nicht beide am selben File arbeiten

---

## Quick Reference

```bash
# Neues Feature starten
git checkout develop && git pull && git checkout -b feature/name/beschreibung

# Develop aktualisieren
git fetch origin && git merge origin/develop

# Feature abschließen
git push -u origin HEAD
# → PR auf GitHub erstellen

# Nach PR-Merge: Aufräumen
git checkout develop && git pull && git branch -d feature/name/beschreibung
```
