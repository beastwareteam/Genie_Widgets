# 🎨 Vollständige Theme-Farb-Konfiguration

## 📋 Übersicht

Dieses Dokument definiert eine **umfassende Farbpalette** für das WidgetSystem mit Struktur für:
- **Dark Theme**: Dunkler Hintergrund mit hellen Texten
- **Transparent Theme**: Transparente Hintergründe mit 50% Rand-Opazität und sichtbarem Content

---

## 🎯 Zielstruktur: `config/colors.json`

```json
{
  "palettes": {
    "dark": { ... },
    "transparent": { ... }
  },
  "categories": {
    "backgrounds": [ ... ],
    "borders": [ ... ],
    "texts": [ ... ],
    "ui_elements": [ ... ]
  }
}
```

---

## 🎨 DARK THEME - Komplette Farbpalette

### 1. BACKGROUND COLORS (Hintergründe)

| Komponente | Farbe | Hex-Code | Beschreibung |
|-----------|-------|----------|-------------|
| **Fenster/Hauptfenster** | Dunkelgrau | `#1E1E1E` | Hauptfenster-Hintergrund |
| **Panels** | Dunkelgrau Hell | `#252525` | Dock-Panel-Hintergrund |
| **Tab Bar** | Tiefblack | `#1A1A1A` | Tab-Leisten-Hintergrund |
| **Dock Area** | Grau | `#2D2D2D` | Dock-Area-Hintergrund |
| **Menü** | Grau + | `#2F2F2F` | Menu-Hintergrund |
| **Status Bar** | Tiefblack | `#1A1A1A` | Statusleisten-Hintergrund |
| **Tooltip** | Dunkelgrau + | `#3F3F3F` | Tooltip-Hintergrund |
| **Scrollbar** | Grau Mittel | `#333333` | Scrollbar-Hintergrund |
| **Button** | Grau Hell | `#363636` | Button-Hintergrund (Normal) |
| **Input** | Grau Dunkel | `#2A2A2A` | Input-Feld-Hintergrund |
| **Selection** | Blau | `#1976D2` | Auswahlbereich |
| **Hover State** | Grau Hell+ | `#373737` | Hover-Effekt-Hintergrund |

### 2. BORDER COLORS (Ränder/Grenzen)

| Komponente | Farbe | Hex-Code | Beschreibung |
|-----------|-------|----------|-------------|
| **Standard Border** | Grau Dunkel | `#404040` | Standard-Randfärbe |
| **Focus Border** | Blau | `#0D47A1` | Focus/Aktiver-Rand |
| **Hover Border** | Grau Hell | `#505050` | Hover-Rand |
| **Error Border** | Rot | `#D32F2F` | Fehler-Rand |
| **Warning Border** | Orange | `#F57C00` | Warnung-Rand |
| **Success Border** | Grün | `#388E3C` | Erfolg-Rand |
| **Disabled Border** | Dunkelgrau | `#383838` | Deaktiviert-Rand |

### 3. TEXT COLORS (Texte)

| Komponente | Farbe | Hex-Code | Beschreibung |
|-----------|-------|----------|-------------|
| **Primary Text** | Hell Grau | `#E0E0E0` | Haupt-Textfarbe |
| **Secondary Text** | Grau Mittel | `#9E9E9E` | Sekundär-Text (z.B. Beschreibungen) |
| **Disabled Text** | Grau Dunkel | `#616161` | Deaktiviert-Text |
| **Accent Text** | Hellblau | `#64B5F6` | Hervorgehobener/Link-Text |
| **Error Text** | Rot | `#EF5350` | Fehler-Text |
| **Warning Text** | Orange | `#FFB74D` | Warnung-Text |
| **Success Text** | Grün | `#66BB6A` | Erfolg-Text |
| **Tab: Active Text** | Weiß | `#FFFFFF` | Aktive Tab-Textfarbe |
| **Tab: Inactive Text** | Grau Hell | `#BDBDBD` | Inaktive Tab-Textfarbe |
| **Menu Text** | Hell Grau | `#E0E0E0` | Menu-Textfarbe |
| **Button Text** | Hell Grau | `#E0E0E0` | Button-Textfarbe |

### 4. UI ELEMENT COLORS (Spezielle Elemente)

| Komponente | Farbe | Hex-Code | Beschreibung |
|-----------|-------|----------|-------------|
| **Button Normal** | Grau | `#363636` | Button-Hintergrund |
| **Button Hover** | Grau Hell | `#404040` | Button-Hover |
| **Button Pressed** | Blau | `#1976D2` | Button-Pressed |
| **Input Focus** | Blau Hell | `#2196F3` | Input-Focus-Border |
| **Scrollbar Thumb** | Grau Hell | `#555555` | Scrollbar-Schieber |
| **Scrollbar Hover** | Grau Hellest | `#666666` | Scrollbar-Schieber-Hover |
| **Progressbar** | Blau | `#2196F3` | Fortschrittsbalken |
| **Checkbox Check** | Blau | `#2196F3` | Checkbox-Häkchen |
| **Radio Button** | Blau | `#2196F3` | Radio-Button |
| **Slider** | Blau | `#2196F3` | Schieberegler |

---

## 🎨 TRANSPARENT THEME - Komplette Farbpalette

### 1. BACKGROUND COLORS (Transparent - mit RGBA)

| Komponente | Farbe | RGBA-Code | Beschreibung |
|-----------|-------|----------|-------------|
| **Fenster** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Panels** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Tab Bar** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Dock Area** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Menü** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Status Bar** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Tooltip** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Scrollbar** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Button** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |
| **Input** | Transparent | `rgba(0, 0, 0, 0)` | Komplett transparent |

### 2. BORDER COLORS (50% Opazität)

| Komponente | Farbe | RGBA-Code | Beschreibung |
|-----------|-------|----------|-------------|
| **Standard Border** | Grau 50% | `rgba(64, 64, 64, 0.5)` | 50% sichtbar |
| **Focus Border** | Blau 50% | `rgba(13, 71, 161, 0.5)` | 50% sichtbar |
| **Hover Border** | Grau Hell 50% | `rgba(80, 80, 80, 0.5)` | 50% sichtbar |
| **Error Border** | Rot 50% | `rgba(211, 47, 47, 0.5)` | 50% sichtbar |
| **Warning Border** | Orange 50% | `rgba(245, 124, 0, 0.5)` | 50% sichtbar |
| **Success Border** | Grün 50% | `rgba(56, 142, 60, 0.5)` | 50% sichtbar |
| **Disabled Border** | Dunkelgrau 50% | `rgba(56, 56, 56, 0.5)` | 50% sichtbar |

### 3. TEXT COLORS (100% - Vollständig sichtbar)

| Komponente | Farbe | Hex-Code | Beschreibung |
|-----------|-------|----------|-------------|
| **Primary Text** | Hell Grau | `#E0E0E0` | Haupt-Textfarbe |
| **Secondary Text** | Grau Mittel | `#9E9E9E` | Sekundär-Text |
| **Disabled Text** | Grau Dunkel | `#616161` | Deaktiviert-Text |
| **Accent Text** | Hellblau | `#64B5F6` | Hervorgehobener/Link-Text |
| **Error Text** | Rot | `#EF5350` | Fehler-Text |
| **Warning Text** | Orange | `#FFB74D` | Warnung-Text |
| **Success Text** | Grün | `#66BB6A` | Erfolg-Text |
| **Tab: Active Text** | Weiß | `#FFFFFF` | Aktive Tab-Textfarbe |
| **Tab: Inactive Text** | Grau Hell | `#BDBDBD` | Inaktive Tab-Textfarbe |

---

## 📁 Neue Config-Struktur

### `config/colors.json` (Neue Datei)

```json
{
  "version": "1.0",
  "palettes": {
    "dark": {
      "backgrounds": {
        "window": "#1E1E1E",
        "panel": "#252525",
        "tab_bar": "#1A1A1A",
        "dock_area": "#2D2D2D",
        "menu": "#2F2F2F",
        "status_bar": "#1A1A1A",
        "tooltip": "#3F3F3F",
        "scrollbar": "#333333",
        "button": "#363636",
        "input": "#2A2A2A",
        "selection": "#1976D2",
        "hover": "#373737"
      },
      "borders": {
        "default": "#404040",
        "focus": "#0D47A1",
        "hover": "#505050",
        "error": "#D32F2F",
        "warning": "#F57C00",
        "success": "#388E3C",
        "disabled": "#383838"
      },
      "texts": {
        "primary": "#E0E0E0",
        "secondary": "#9E9E9E",
        "disabled": "#616161",
        "accent": "#64B5F6",
        "error": "#EF5350",
        "warning": "#FFB74D",
        "success": "#66BB6A",
        "tab_active": "#FFFFFF",
        "tab_inactive": "#BDBDBD",
        "menu": "#E0E0E0",
        "button": "#E0E0E0"
      },
      "ui_elements": {
        "button_normal": "#363636",
        "button_hover": "#404040",
        "button_pressed": "#1976D2",
        "input_focus": "#2196F3",
        "scrollbar_thumb": "#555555",
        "scrollbar_hover": "#666666",
        "progressbar": "#2196F3",
        "checkbox": "#2196F3",
        "radio_button": "#2196F3",
        "slider": "#2196F3"
      }
    },
    "transparent": {
      "backgrounds": {
        "window": "rgba(0, 0, 0, 0)",
        "panel": "rgba(0, 0, 0, 0)",
        "tab_bar": "rgba(0, 0, 0, 0)",
        "dock_area": "rgba(0, 0, 0, 0)",
        "menu": "rgba(0, 0, 0, 0)",
        "status_bar": "rgba(0, 0, 0, 0)",
        "tooltip": "rgba(0, 0, 0, 0)",
        "scrollbar": "rgba(0, 0, 0, 0)",
        "button": "rgba(0, 0, 0, 0)",
        "input": "rgba(0, 0, 0, 0)"
      },
      "borders": {
        "default": "rgba(64, 64, 64, 0.5)",
        "focus": "rgba(13, 71, 161, 0.5)",
        "hover": "rgba(80, 80, 80, 0.5)",
        "error": "rgba(211, 47, 47, 0.5)",
        "warning": "rgba(245, 124, 0, 0.5)",
        "success": "rgba(56, 142, 60, 0.5)",
        "disabled": "rgba(56, 56, 56, 0.5)"
      },
      "texts": {
        "primary": "#E0E0E0",
        "secondary": "#9E9E9E",
        "disabled": "#616161",
        "accent": "#64B5F6",
        "error": "#EF5350",
        "warning": "#FFB74D",
        "success": "#66BB6A",
        "tab_active": "#FFFFFF",
        "tab_inactive": "#BDBDBD",
        "menu": "#E0E0E0",
        "button": "#E0E0E0"
      }
    }
  }
}
```

### `config/themes.json` (Erweitert)

```json
{
  "default_theme_id": "dark",
  "themes": [
    {
      "id": "dark",
      "name": "Dark",
      "file": "themes/dark.qss",
      "color_palette_id": "dark",
      "tab_colors": {
        "active": "#FFFFFF",
        "inactive": "#BDBDBD"
      }
    },
    {
      "id": "transparent",
      "name": "Transparent",
      "file": "themes/transparent.qss",
      "color_palette_id": "transparent",
      "tab_colors": {
        "active": "#FFFFFF",
        "inactive": "#BDBDBD"
      }
    }
  ]
}
```

---

## 🔗 Integration in ThemeFactory

```python
# Neue Methoden in ThemeFactory

def get_color_palette(self, palette_id: str | None = None) -> dict[str, Any]:
    """Load color palette for a theme."""
    if palette_id is None:
        theme = self.get_default_theme()
        palette_id = theme.color_palette_id if hasattr(theme, 'color_palette_id') else theme.theme_id
    
    colors_file = self.config_path / "colors.json"
    if not colors_file.exists():
        return {}
    
    with open(colors_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("palettes", {}).get(palette_id, {})

def get_color(self, palette_id: str, category: str, name: str) -> str:
    """Get a specific color from a palette."""
    palette = self.get_color_palette(palette_id)
    return palette.get(category, {}).get(name, "#E0E0E0")
```

---

## 📝 Implementierungs-Checkliste

- [ ] `colors.json` erstellen
- [ ] `themes.json` mit `color_palette_id` erweitern
- [ ] `ThemeDefinition` um Palette-ID erweitern
- [ ] `ThemeFactory` um Color-Palette-Methoden erweitern
- [ ] `themes/dark.qss` basierend auf Palette generieren
- [ ] `themes/transparent.qss` basierend auf Palette generieren
- [ ] `MainWindow` anpassen um Farben zu nutzen
- [ ] QSS-Schema-Validierung durchführen

---

## 🎯 Nächste Schritte

1. **Validiere diese Farb-Palette** - Sind die Farben so gewünscht?
2. **Wir erstellen `colors.json`** mit dieser Struktur
3. **Wir erweitern `ThemeFactory`** um Farb-Palette-Zugriff
4. **Wir generieren die QSS-Dateien** aus den Farben
5. **Integration in MainWindow** für dynamische Farb-Verwaltung
