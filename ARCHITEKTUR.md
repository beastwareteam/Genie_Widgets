# Architektur-Richtlinie: Theme- und QSS-System

## 1. QSS-Validierung
- Alle QSS-Dateien werden vor jedem Commit automatisch auf ungültige CSS-Properties geprüft (siehe scripts/check_qss_validity.py).
- Verbotene Properties (z.B. transition, animation, filter, etc.) sind in der Prüfliste hinterlegt und dürfen nicht verwendet werden.

## 2. Encoding
- Alle Theme-, QSS- und JSON-Dateien müssen UTF-8 kodiert sein.
- Ein Pre-Commit-Hook prüft dies und verhindert Commits mit anderen Zeichensätzen.

## 3. Theme-Design-Workflow
- Farb- und Maßwerte werden zentral in einer JSON-Datei gepflegt (z.B. config/theme_tokens.json).
- QSS wird automatisch aus diesen Tokens generiert (Build-Skript, TODO).
- Keine manuelle Bearbeitung von QSS-Dateien im Produktivbetrieb.

## 4. Architekturprinzipien
- Factory-Pattern für Theme- und UI-Komponenten.
- Keine direkten QSS-Änderungen ohne Validierung.
- Alle neuen Themes müssen die Validierung bestehen und UTF-8 sein.

## 5. Automatisierte Tests
- Es gibt Tests, die prüfen, dass Themes korrekt geladen werden und keine Qt-Fehler auslösen.
- Fehlerhafte Themes blockieren den Build/Test.

## 6. Agenten-Richtlinie
- AI-Agents dürfen keine ungültigen QSS-Properties generieren oder übernehmen.
- Vor jeder Änderung an QSS/Theme-Dateien ist eine Validierung durchzuführen.

---

**Diese Richtlinie ist verbindlich für alle Theme- und QSS-Entwicklungen im WidgetSystem-Projekt.**
