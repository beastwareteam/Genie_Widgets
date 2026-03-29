# Toolbar Structure - Unified Styling System

## Übersicht

Alle Themes verwenden eine **identische strukturelle Basis** für die Toolbar. Nur **Farben** unterscheiden sich zwischen Themes.

## Strukturelle Konstanten (Theme-übergreifend)

Diese Eigenschaften sind **identisch** in allen Themes und dürfen **nicht** verändert werden:

### QToolBar
- `spacing: 4px` - Abstand zwischen Toolbar-Elementen
- `border: 1px solid ...` - Border-Breite (Farbe variiert)

### QToolBar::separator
- `width: 2px` - Separator-Breite
- `margin: 0px 4px` - Separator-Abstand links/rechts

### QToolButton
- `padding: 4px 8px` - Innenabstand der Buttons
- `border-radius: 2px` - Ecken-Rundung
- `border: 1px solid ...` - Border-Breite (Farbe variiert)

## Theme-spezifische Eigenschaften (nur Farben)

Nur diese Eigenschaften variieren zwischen Themes:

### Dark Theme
```css
QToolBar {
    background-color: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #3C3C3C;
}

QToolBar::separator {
    background-color: #4C4C4C;
}

QToolButton {
    background-color: transparent;
    color: #E0E0E0;
    border: 1px solid transparent;
}

QToolButton:hover {
    background-color: #323232;
    border: 1px solid #4C4C4C;
}

QToolButton:pressed,
QToolButton:checked {
    background-color: #4C4C4C;
    border: 1px solid #5C5C5C;
}
```

### Light Theme
```css
QToolBar {
    background-color: #F5F5F5;
    color: #212121;
    border: 1px solid #E0E0E0;
}

QToolBar::separator {
    background-color: #D0D0D0;
}

QToolButton {
    background-color: transparent;
    color: #212121;
    border: 1px solid transparent;
}

QToolButton:hover {
    background-color: #E8E8E8;
    border: 1px solid #D0D0D0;
}

QToolButton:pressed,
QToolButton:checked {
    background-color: #D0D0D0;
    border: 1px solid #B0B0B0;
}
```

### Transparent Theme
```css
QToolBar {
    background-color: rgba(0, 0, 0, 0);
    color: #E0E0E0;
    border: 1px solid rgba(64, 64, 64, 0.5);
}

QToolBar::separator {
    background-color: rgba(76, 76, 76, 0.5);
}

QToolButton {
    background-color: rgba(0, 0, 0, 0);
    color: #E0E0E0;
    border: 1px solid transparent;
}

QToolButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(76, 76, 76, 0.5);
}

QToolButton:pressed,
QToolButton:checked {
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(92, 92, 92, 0.5);
}
```

## Änderungen vom 29.03.2026

### Problem
- Toolbar hatte unterschiedliche strukturelle Eigenschaften zwischen Themes
- `transparent.qss` fehlte `QToolBar::separator` Definition
- Inkonsistente Borders bei Buttons

### Lösung
- ✅ **Einheitliche Struktur**: Alle Themes haben identische spacing, padding, margin, border-radius
- ✅ **Separator hinzugefügt**: `transparent.qss` hat jetzt QToolBar::separator
- ✅ **Konsistente Borders**: Alle Buttons haben `border: 1px solid transparent` als Basis
- ✅ **Dokumentiert**: Diese Datei erklärt das System

## Regeln für neue Themes

Wenn Sie ein neues Theme erstellen:

1. **KOPIEREN** Sie die komplette Toolbar-Sektion von `dark.qss`
2. **ÄNDERN** Sie NUR die folgenden Eigenschaften:
   - `background-color`
   - `color`
   - `border` Farben (nicht die Breite!)
3. **NICHT ÄNDERN**:
   - `spacing`
   - `padding`
   - `margin`
   - `border-radius`
   - `width` (bei separator)

## Validierung

Um sicherzustellen, dass Ihre Theme-Datei korrekt ist:

```bash
# Prüfen Sie, ob alle strukturellen Eigenschaften vorhanden sind
grep -E "(spacing|padding|margin|border-radius|width:)" themes/your_theme.qss
```

Erwartete Ausgabe:
```
QToolBar { ... spacing: 4px; ... }
QToolBar::separator { ... width: 2px; margin: 0px 4px; ... }
QToolButton { ... padding: 4px 8px; border-radius: 2px; ... }
```

## Beispiel: Neues Theme erstellen

```css
/* Toolbar Styling - Unified Structure (only colors differ between themes) */
QToolBar {
    background-color: YOUR_COLOR;    /* ÄNDERN */
    color: YOUR_COLOR;               /* ÄNDERN */
    border: 1px solid YOUR_COLOR;    /* ÄNDERN (nur Farbe) */
    spacing: 4px;                    /* NICHT ÄNDERN */
}

QToolBar::separator {
    background-color: YOUR_COLOR;    /* ÄNDERN */
    width: 2px;                      /* NICHT ÄNDERN */
    margin: 0px 4px;                 /* NICHT ÄNDERN */
}

QToolButton {
    background-color: YOUR_COLOR;    /* ÄNDERN */
    color: YOUR_COLOR;               /* ÄNDERN */
    border: 1px solid transparent;   /* NICHT ÄNDERN */
    padding: 4px 8px;                /* NICHT ÄNDERN */
    border-radius: 2px;              /* NICHT ÄNDERN */
}

QToolButton:hover {
    background-color: YOUR_COLOR;    /* ÄNDERN */
    border: 1px solid YOUR_COLOR;    /* ÄNDERN (nur Farbe) */
}

QToolButton:pressed,
QToolButton:checked {
    background-color: YOUR_COLOR;    /* ÄNDERN */
    border: 1px solid YOUR_COLOR;    /* ÄNDERN (nur Farbe) */
}
```

## Referenz

- **Basis-Theme**: `themes/dark.qss` (Standard-Referenz)
- **Theme-Dateien**: 
  - `themes/dark.qss`
  - `themes/light.qss`
  - `themes/transparent.qss`
- **Theme-System**: `src/widgetsystem/core/theme_manager.py`
- **Theme-Factory**: `src/widgetsystem/factories/theme_factory.py`
