# 🏗️ Theme-Konfiguration - Implementierungsplan

## 📊 Visualisierter Aufbau

```
THEME CONFIGURATION SYSTEM
│
├─ themes.json (Theme-Definitionen)
│  ├─ dark-theme
│  │  ├─ Datei: themes/dark.qss
│  │  ├─ Color-Palette: "dark"
│  │  └─ Tab-Farben: active/#FFF, inactive/#BDBDBD
│  │
│  └─ transparent-theme
│     ├─ Datei: themes/transparent.qss
│     ├─ Color-Palette: "transparent"
│     └─ Tab-Farben: active/#FFF, inactive/#BDBDBD
│
├─ colors.json (Zentrale Farbpaletten)
│  ├─ dark-palette
│  │  ├─ backgrounds: 12 Farben
│  │  ├─ borders: 7 Farben
│  │  ├─ texts: 11 Farben
│  │  └─ ui_elements: 10 Farben
│  │
│  └─ transparent-palette
│     ├─ backgrounds: 10x rgba(0,0,0,0)
│     ├─ borders: 7x rgba(..., 0.5)
│     ├─ texts: 11 Farben (100% sichtbar)
│     └─ ui_elements: nicht benötigt (transparent)
│
├─ themes/dark.qss (QSS-Stylesheet)
│  └─ Generiert aus dark-palette von colors.json
│
└─ themes/transparent.qss (QSS-Stylesheet)
   └─ Generiert aus transparent-palette von colors.json
```

---

## 🔄 Datenflususs

```
MainWindow.__init__()
    │
    ├─ Theme laden: ThemeFactory.get_default_theme()
    │  └─ Rückgabe: ThemeDefinition (mit color_palette_id)
    │
    ├─ Farben laden: ThemeFactory.get_color_palette(palette_id)
    │  └─ Rückgabe: dict[str, dict[str, str]]
    │
    ├─ Tab-Farben: ThemeFactory.get_tab_colors()
    │  └─ TabColorController initialisieren
    │
    ├─ QSS anwenden: Read from theme.file_path
    │  └─ app.setStyleSheet(qss_content)
    │
    └─ Anwendung lädt alle Farben aus definierter Palette
```

---

## 📦 Farbkategorien pro Palette

### Dark-Palette: 40 Farben insgesamt

**Backgrounds (12):**
```
window, panel, tab_bar, dock_area, menu, status_bar,
tooltip, scrollbar, button, input, selection, hover
```

**Borders (7):**
```
default, focus, hover, error, warning, success, disabled
```

**Texts (11):**
```
primary, secondary, disabled, accent, error, warning, success,
tab_active, tab_inactive, menu, button
```

**UI Elements (10):**
```
button_normal, button_hover, button_pressed, input_focus,
scrollbar_thumb, scrollbar_hover, progressbar, checkbox,
radio_button, slider
```

### Transparent-Palette: ~20 Farben + Variationen

**Backgrounds (10):**
```
Alle mit: rgba(0, 0, 0, 0)  -> 100% transparent
```

**Borders (7):**
```
Alle mit: rgba(..., 0.5)  -> 50% Opazität, Rest transparent
```

**Texts (11):**
```
Identisch mit Dark-Palette -> 100% sichtbar
```

---

## 🛠️ Implementierungs-Routen

### Route 1: Ab sofort nutzbares System
```python
# In MainWindow
colors_file = Path("config/colors.json")
with open(colors_file) as f:
    palettes = json.load(f)["palettes"]
    dark_colors = palettes["dark"]
    
# Verwenden:
body_bg = dark_colors["backgrounds"]["panel"]
tab_text = dark_colors["texts"]["tab_active"]
```

### Route 2: Via Factory (Empfohlen)
```python
# In MainWindow
palette = self.theme_factory.get_color_palette()
body_bg = palette["backgrounds"]["panel"]

# oder spezifisch:
tab_text = self.theme_factory.get_color("dark", "texts", "tab_active")
```

### Route 3: Automatische QSS-Generierung
```python
# QSS-Generator könnte aus colors.json generieren:
def generate_qss_from_palette(palette_dict) -> str:
    """Generiert komplettes QSS aus Farb-Palette"""
    qss = "QMainWindow { ... }"
    for widget, colors in palette_dict.items():
        for color_name, color_value in colors.items():
            # QSS-Regeln erzeugen
    return qss
```

---

## 📋 Checkliste: Schritt für Schritt

### Phase 1: Foundation
- [ ] `config/colors.json` erstellen mit Dark- und Transparent-Paletten
- [ ] `ThemeDefinition` erweitern um `color_palette_id: str`
- [ ] `config/themes.json` mit `color_palette_id` aktualisieren

### Phase 2: Factory-Erweiterung
- [ ] `ThemeFactory.get_color_palette(palette_id)` implementieren
- [ ] `ThemeFactory.get_color(category, name)` implementieren
- [ ] Type-Hints und Docstrings hinzufügen

### Phase 3: QSS-Integration
- [ ] `themes/dark.qss` basierend auf Palette aktualisieren
- [ ] `themes/transparent.qss` mit RGBA-Farben erstellen
- [ ] Beide QSS-Dateien testen

### Phase 4: MainWindow-Integration
- [ ] Tab-Farben aus Palette laden (existiert bereits)
- [ ] Optional: Weitere UI-Farben aus Palette laden
- [ ] Theme-Wechsel testen

### Phase 5: Dokumentation & Validierung
- [ ] Schema für `colors.json` erstellen
- [ ] Validierung in Factory durchführen
- [ ] Dokumentation aktualisieren

---

## 🎯 Farbidee: Transparent Theme

```
┌─────────────────────────────────────┐
│ Window (transparent)                │
│                                     │
│ ┌───────────────────────────────┐   │
│ │ Panel (transparent)           │   │  ← Border mit 50% Sichtbarkeit
│ │                               │   │     (Grau, 50% opacity)
│ │ Tab: Active (text #FFFFFF)    │───┘
│ │ Tab: Inactive (text #BDBDBD)  │
│ │                               │
│ │ Content (E0E0E0)              │
│ └───────────────────────────────┘
│                                     │
└─────────────────────────────────────┘

Sichtbar:
- Alle Ränder (50% transparent → halbtransparent)
- Alle Texte (100% sichtbar)
- Keine Füllungen (100% transparent → unsichtbar)

Effekt: "Glassmorph" / "Floating" Design
```

---

## 🔐 Validierungs-Anforderungen

### colors.json
```python
def validate_colors_file():
    """Validiere, dass colors.json korrekt ist"""
    # Prüfe: Alle erforderlichen Paletten existieren
    assert "dark" in palettes
    assert "transparent" in palettes
    
    # Prüfe: Kategorien sind konsistent
    categories = ["backgrounds", "borders", "texts", "ui_elements"]
    for category in categories:
        assert category in dark_palette or category == "ui_elements"
    
    # Prüfe: Hex/RGBA-Format
    for color in all_colors:
        assert is_valid_hex(color) or is_valid_rgba(color)
```

---

## 💡 Notizen zur Implementation

1. **Reihenfolge der Ein-Werte**: Kategorien -> Widget-Name -> Farbe
   ```
   colors["dark"]["texts"]["primary"] = "#E0E0E0"
   ```

2. **RGBA-Format für Transparent**:
   ```
   rgba(R, G, B, Opacity)
   rgba(64, 64, 64, 0.5)  // 50% sichtbar
   ```

3. **Fallback-Werte**: Wenn Farbe nicht gefunden → `#E0E0E0` (Standard)

4. **Theme-Wechsel**: Auch `ThemeFactory.switch_theme()` sollte Farben neu laden

---

## 🎨 Zusammenfassung der Struktur

| Komponente | Dateien | Farben | Status |
|-----------|---------|--------|--------|
| **Dark Theme** | colors.json + dark.qss | 40+ | Plan ✓ |
| **Transparent** | colors.json + transparent.qss | 20+ | Plan ✓ |
| **Factory** | theme_factory.py | Methoden | Zu erweitern |
| **Validation** | colors.schema.json | Schema | Zu erstellen |
| **QSS Assets** | themes/*.qss | CSS | Zu generieren |

