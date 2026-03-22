# Agent Configuration Discovery Flow

Dieses Diagramm zeigt, wie verschiedene AI-Agents die Projektkonfiguration finden.

## 🔍 Discovery-Methoden

```
┌─────────────────────────────────────────────────────────────────┐
│                       AI Agent startet                          │
│                  (GitHub Copilot, Claude, etc.)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   Mehrere Einstiegspunkte   │
        └────────────┬────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────────┐
│README.md│   │AGENTS.md │   │AGENT_CONFIG  │
│         │   │          │   │    .md       │
└────┬────┘   └────┬─────┘   └──────┬───────┘
     │             │                 │
     └─────────────┼─────────────────┘
                   │
                   ▼
     ┌─────────────────────────────┐
     │  .github/                   │
     │  copilot-instructions.md    │
     │  (Hauptkonfiguration)       │
     └────────────┬────────────────┘
                  │
                  ▼
     ┌─────────────────────────────┐
     │  .github/instructions/      │
     │  ├── factories.*            │
     │  ├── ui-components.*        │
     │  ├── testing.*              │
     │  └── json-config.*          │
     └────────────┬────────────────┘
                  │
                  ▼
     ┌─────────────────────────────┐
     │  Context angewendet auf:    │
     │  - Datei-Pattern (applyTo)  │
     │  - Workspace-weit           │
     │  - Spezifische Aufgaben     │
     └─────────────────────────────┘
```

## 🎯 Automatische Erkennung

### GitHub Copilot
```
Workspace geöffnet
  ↓
Lädt automatisch: .github/copilot-instructions.md
  ↓
Wendet Instructions an basierend auf: applyTo-Pattern
  ↓
Kontext für alle Vorschläge verfügbar
```

### Andere AI-Agents (Claude, ChatGPT, etc.)
```
Workspace geöffnet
  ↓
Sucht nach: AGENTS.md, AGENT_CONFIG.md, README.md
  ↓
Liest Markdown-Dateien
  ↓
Findet Verweis auf .github/copilot-instructions.md
  ↓
Liest vollständige Guidelines
  ↓
Kontext verfügbar
```

## 📋 Datei-Hierarchie

```
WidgetSystem/
│
├── 📄 README.md ─────────────┐
│   "🤖 For AI Agents"        │
│                              │
├── 📄 AGENT_CONFIG.md ────┐  │
│   "⚠️ IMPORTANT: READ"    │  │
│                            │  │
├── 📄 AGENTS.md ──────────┐│  │
│   "Für AI-Agents"        ││  │
│                           ││  │
├── 📄 QUICK_REFERENCE.md  │││  │
│   "Schnellreferenz"      │││  │
│                           │││  │
└── .github/               │││  │
    │                      │││  │
    ├── 📄 copilot-instructions.md ◄──┴┴──┴─── Alle verweisen hierher
    │   "Vollständige Guidelines"
    │
    ├── 📄 README.md
    │   "Erklärt das Konfigurationssystem"
    │
    └── instructions/
        ├── 📄 factories.instructions.md
        │   applyTo: "**/factories/**/*.py"
        │
        ├── 📄 ui-components.instructions.md
        │   applyTo: "**/ui/**/*.py"
        │
        ├── 📄 testing.instructions.md
        │   applyTo: "**/tests/**/*.py"
        │
        └── 📄 json-config.instructions.md
            applyTo: "**/config/**/*.json"
```

## 🔄 Kontext-Injection-Flow

```
Agent arbeitet an Datei: src/widgetsystem/factories/layout_factory.py
           │
           ├─► Workspace Instructions: ✅ Immer aktiv
           │   (.github/copilot-instructions.md)
           │
           ├─► Pattern Match: ✅ Trifft zu
           │   (factories.instructions.md → "**/factories/**/*.py")
           │
           ├─► Repository Memory: ✅ Verfügbar
           │   (/memories/repo/widgetsystem-structure.md)
           │
           └─► Kombinierter Kontext an Agent
               │
               ▼
           Agent-Vorschlag mit vollständigem Kontext
```

## 🛡️ Fail-Safe-Mechanismen

1. **Mehrere Einstiegspunkte**
   - README.md (immer sichtbar)
   - AGENTS.md (Open Standard)
   - AGENT_CONFIG.md (expliziter Name)

2. **Cross-Referencing**
   - Jede Datei verweist auf die anderen
   - Keine Sackgassen

3. **Validation**
   - `tests/verify_agent_config.py`
   - Prüft Vollständigkeit und Validität

4. **Repository Memory**
   - Persistente Notizen
   - Überleben Session-Ende

5. **Redundanz**
   - Gleiche Info in verschiedenen Formaten
   - Verschiedene Entdeckungsmethoden

## 📊 Kompatibilitäts-Matrix

| AI System          | Discovery Method       | Status |
|--------------------|------------------------|--------|
| GitHub Copilot     | Auto (.github/)        | ✅     |
| VS Code Chat       | Workspace Context      | ✅     |
| Claude Code        | AGENTS.md, Markdown    | ✅     |
| ChatGPT            | File References        | ✅     |
| Custom Agents      | README → Instructions  | ✅     |
| Future Systems     | Multiple Entry Points  | ✅     |

## 🎓 Best Practices

1. **Für neue Agents**
   - Immer zuerst README.md lesen
   - Dann AGENT_CONFIG.md folgen
   - Vollständige Guidelines in .github/ studieren

2. **Bei Änderungen**
   - Relevante Datei in .github/ anpassen
   - `verify_agent_config.py` ausführen
   - In Git committen

3. **Bei Problemen**
   - Verifikations-Skript ausführen
   - YAML-Frontmatter prüfen
   - applyTo-Pattern validieren
   - Explizit auf Datei verweisen

## ✅ Erfolgskriterien

- ✅ Agent findet Guidelines innerhalb von 3 Klicks
- ✅ Mehrere Discovery-Pfade vorhanden
- ✅ Kein "Lost Agent" Szenario möglich
- ✅ Automatische Anwendung bei GitHub Copilot
- ✅ Manuelle Discovery bei anderen Agents
- ✅ Validation automatisiert
- ✅ Cross-Editor kompatibel
