# GitHub Repository Einstellungen

## Branch Protection Rules einrichten

Gehe zu: **Repository → Settings → Branches → Add branch protection rule**

---

### 1. Schutz für `main` Branch

**Branch name pattern:** `main`

#### Aktivieren:
- [x] **Require a pull request before merging**
  - [x] Require approvals: `1`
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require approval of the most recent reviewable push

- [x] **Require status checks to pass before merging** (optional, wenn CI vorhanden)
  - [x] Require branches to be up to date before merging

- [x] **Require conversation resolution before merging**

- [x] **Do not allow bypassing the above settings**

- [x] **Restrict who can push to matching branches**
  - Niemand hinzufügen (nur via PR)

- [ ] Allow force pushes → **DEAKTIVIERT lassen!**
- [ ] Allow deletions → **DEAKTIVIERT lassen!**

---

### 2. Schutz für `develop` Branch

**Branch name pattern:** `develop`

#### Aktivieren:
- [x] **Require a pull request before merging**
  - [x] Require approvals: `1`
  - [ ] Dismiss stale approvals (optional bei develop)

- [x] **Require conversation resolution before merging**

- [ ] Allow force pushes → **DEAKTIVIERT lassen!**
- [ ] Allow deletions → **DEAKTIVIERT lassen!**

---

## Repository Settings

### General → Pull Requests

- [x] **Allow squash merging** ← Empfohlen für saubere History
  - Default: "Default to pull request title and description"
- [ ] Allow merge commits (optional deaktivieren)
- [ ] Allow rebase merging (optional deaktivieren)

- [x] **Automatically delete head branches**
  - Löscht Feature-Branches nach Merge automatisch

---

## Collaborators einrichten

**Settings → Collaborators and teams**

1. Beide Teammitglieder als **Collaborators** hinzufügen
2. Rolle: `Write` oder `Maintain`

---

## Branch-Struktur nach Setup

```
Repository
├── main (protected)
│   └── Nur via PR von develop oder hotfix/*
│
├── develop (protected)
│   └── Nur via PR von feature/* oder bugfix/*
│
└── feature/*, bugfix/*, hotfix/* (ungeschützt)
    └── Jeder kann hier arbeiten
```

---

## Schnellzugriff Links

Nach dem Einrichten könnt ihr diese URLs nutzen:

- **Neuer PR:** `https://github.com/beastwareteam/Genie_Widgets/compare/develop...feature/BRANCH`
- **Branch Protection:** `https://github.com/beastwareteam/Genie_Widgets/settings/branches`
- **Collaborators:** `https://github.com/beastwareteam/Genie_Widgets/settings/access`

---

## CLI-Befehle für GitHub CLI (optional)

Falls ihr `gh` CLI installiert habt:

```bash
# PR erstellen
gh pr create --base develop --title "Feature: Beschreibung" --body "Details..."

# PR reviewen
gh pr review --approve

# PR mergen
gh pr merge --squash --delete-branch
```

---

## Checkliste nach Setup

- [ ] `develop` Branch existiert
- [ ] Branch Protection für `main` aktiviert
- [ ] Branch Protection für `develop` aktiviert
- [ ] Beide Teammitglieder als Collaborators
- [ ] Auto-delete für merged branches aktiviert
- [ ] Squash merge als Default
- [ ] Erster Test-PR erfolgreich
