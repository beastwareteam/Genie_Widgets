# JSON Theme-Profile - Anleitung

## Was sind JSON-Profile?

JSON-Profile sind **dynamische Themes**, die QSS zur Laufzeit generieren. Sie bieten:

- ✅ **ARGB Transparenz** - Echte Alpha-Kanal Unterstützung (#AARRGGBB)
- ✅ **Globale Transformationen** - Hue/Saturation/Brightness für alle Farben
- ✅ **Einfache Bearbeitung** - JSON statt komplexem QSS
- ✅ **Automatische QSS-Generierung** - Konsistente Struktur garantiert

## Speicherort

**Alle Profile:** `config/profiles/*.json`

Jede JSON-Datei = 1 Theme im Menü

## JSON-Struktur

```json
{
  "name": "Mein Custom Theme",
  "colors": {
    // Hauptfenster
    "window_bg": "#00202124",           // Transparent: Alpha=00
    
    // Tabs
    "tab_active_bg": "#ccffffff",       // 80% Opak: Alpha=cc
    "tab_active_border": "#ff0288d1",   // Solid: Alpha=ff
    "tab_active_text": "#ff0288d1",
    "tab_inactive_bg": "#cc2d2e31",
    "tab_inactive_text": "#ffbdc1c6",
    "tab_padding": 6,
    "tab_border_radius": 4,
    
    // Title Bar
    "titlebar_bg": "#cc2d2e31",
    "titlebar_text": "#ffe8eaed",
    "titlebar_btn_hover": "#408ab4f8",
    
    // Buttons
    "btn_bg": "#40ffffff",
    "btn_icon": "#ffe8eaed",
    
    // Borders & Splitter
    "floating_border": "#ff3c4043",
    "splitter_handle": "#ff3c4043",
    "splitter_width": 2,
    
    // Auto-Hide Panels
    "autohide_sidebar_bg": "#cc202124",
    "autohide_tab_bg": "#cc2d2e31",
    "autohide_container_bg": "#cc202124",
    "autohide_container_border": "#ff8ab4f8",
    
    // Overlay (Drag & Drop)
    "overlay_base_color": "#808ab4f8",
    "overlay_cross_color": "#ff8ab4f8",
    "overlay_border_color": "#ff8ab4f8",
    "overlay_border_width": 2
  },
  "global": {
    "hue": 0,           // -180 bis +180 (Farbton verschieben)
    "saturation": 1.0,  // 0.0 bis 2.0 (Sättigung anpassen)
    "brightness": 1.0   // 0.0 bis 2.0 (Helligkeit anpassen)
  }
}
```

## ARGB Farbformat

**Format:** `#AARRGGBB` (Hex)

- **AA** = Alpha (Transparenz): `00` = transparent, `FF` = opak
- **RR** = Rot: `00` - `FF`
- **GG** = Grün: `00` - `FF`
- **BB** = Blau: `00` - `FF`

### Beispiele:
```
#00000000  = Vollständig transparent (unsichtbar)
#80000000  = 50% Transparenz, Schwarz
#CC0288D1  = 80% Opak, Blue (#0288D1)
#FFFFFFFF  = 100% Opak, Weiß
#00ECEFF1  = Transparent mit Farbe (nur für Compositing)
```

### Alpha-Werte (häufig verwendet):
```
#00 = 0% Opak (100% transparent)
#40 = 25% Opak
#80 = 50% Opak
#CC = 80% Opak
#FF = 100% Opak (solid)
```

## Globale Transformationen

Werden auf **alle Farben** im Theme angewendet.

### Hue (Farbton)
```json
"hue": 30    // Verschiebt alle Farben um 30° im Farbkreis
```
- `-180` bis `+180`
- **0** = keine Änderung
- **30** = Orange-Shift
- **180** = Komplementärfarben

### Saturation (Sättigung)
```json
"saturation": 1.5  // 50% mehr Sättigung (kräftigere Farben)
```
- `0.0` = Graustufen (keine Farbe)
- `1.0` = Original
- `2.0` = Maximale Sättigung

### Brightness (Helligkeit)
```json
"brightness": 0.8  // 20% dunkler
```
- `0.0` = Schwarz
- `1.0` = Original
- `2.0` = 2x heller

## Workflow: Profile anpassen

### 1. Bestehendes Profil kopieren
```bash
# Beispiel: Midnight Blue als Basis
cp config/profiles/midnight_blue.json config/profiles/my_custom_blue.json
```

### 2. JSON bearbeiten
```json
{
  "name": "My Custom Blue",  // ✏️ Namen ändern!
  "colors": {
    "tab_active_border": "#ffFF00FF",  // ✏️ Magenta statt Cyan
    "tab_active_text": "#ffFF00FF"
  },
  "global": {
    "hue": 15,         // ✏️ Leichter Orange-Shift
    "saturation": 1.2, // ✏️ Kräftigere Farben
    "brightness": 0.9  // ✏️ Etwas dunkler
  }
}
```

### 3. Anwendung neu starten
- Profile werden beim Start automatisch geladen
- Kein Rebuild nötig!

### 4. Im Theme-Menü auswählen
- Erscheint als "My Custom Blue"

## Häufige Anpassungen

### Transparenz ändern
```json
// Mehr Transparenz (weniger opak)
"window_bg": "#00202124",      // 100% transparent
"tab_active_bg": "#80ffffff",  // 50% transparent (war: #cc)

// Weniger Transparenz (mehr opak)
"window_bg": "#80202124",      // 50% transparent
"tab_active_bg": "#FFffffff",  // Solid (war: #cc)
```

### Akzentfarbe ändern
```json
// Alle Border/Active-Farben auf rot setzen
"tab_active_border": "#ffFF0000",        // Rot
"tab_active_text": "#ffFF0000",
"autohide_container_border": "#ffFF0000",
"overlay_cross_color": "#ffFF0000",
"overlay_border_color": "#ffFF0000"
```

### Dunkler / Heller machen
```json
// Methode 1: Global Brightness
"global": {
  "brightness": 0.7  // 30% dunkler
}

// Methode 2: Farben direkt ändern
"window_bg": "#00101010",      // Dunkler (war: #202124)
"tab_active_bg": "#cc101010"   // Dunkler
```

### Colorscheme Shift
```json
// Alles in Richtung Grün verschieben
"global": {
  "hue": -60  // Cyan → Grün, Blue → Cyan
}

// Alles in Richtung Rot/Orange
"global": {
  "hue": 30   // Blue → Magenta, Cyan → Blue
}
```

## Beliebte Farbpaletten

### GitHub Dark
```json
{
  "name": "GitHub Dark Pro",
  "colors": {
    "window_bg": "#000d1117",
    "tab_active_bg": "#cc1f2428",
    "tab_active_border": "#ff58a6ff",
    "tab_active_text": "#ffc9d1d9",
    "titlebar_bg": "#cc0d1117",
    "titlebar_text": "#ffc9d1d9"
  }
}
```

### VS Code Dark+
```json
{
  "name": "VS Code Dark+",
  "colors": {
    "window_bg": "#001e1e1e",
    "tab_active_bg": "#cc2d2d30",
    "tab_active_border": "#ff007acc",
    "tab_active_text": "#ffffffff",
    "titlebar_bg": "#cc252526",
    "titlebar_text": "#ffcccccc"
  }
}
```

### Dracula
```json
{
  "name": "Dracula",
  "colors": {
    "window_bg": "#00282a36",
    "tab_active_bg": "#cc44475a",
    "tab_active_border": "#ffbd93f9",
    "tab_active_text": "#fff8f8f2",
    "titlebar_bg": "#cc44475a",
    "titlebar_text": "#fff8f8f2"
  }
}
```

### Nord
```json
{
  "name": "Nord",
  "colors": {
    "window_bg": "#002e3440",
    "tab_active_bg": "#cc3b4252",
    "tab_active_border": "#ff88c0d0",
    "tab_active_text": "#ffeceff4",
    "titlebar_bg": "#cc2e3440",
    "titlebar_text": "#ffeceff4"
  }
}
```

### Solarized Dark
```json
{
  "name": "Solarized Dark",
  "colors": {
    "window_bg": "#00002b36",
    "tab_active_bg": "#cc073642",
    "tab_active_border": "#ff268bd2",
    "tab_active_text": "#fffdf6e3",
    "titlebar_bg": "#cc073642",
    "titlebar_text": "#ff839496"
  }
}
```

## Programmatische Nutzung

### Profile laden
```python
from pathlib import Path
from widgetsystem.core import ThemeProfile

# Methode 1: Direkt laden
profile = ThemeProfile.load_from_file(Path("config/profiles/midnight_blue.json"))

# Methode 2: Über Factory
from widgetsystem.factories.theme_factory import ThemeFactory

factory = ThemeFactory(Path("config"))
profile = factory.load_profile("midnight_blue")
```

### Profile anpassen & speichern
```python
# Laden
profile = ThemeProfile.load_from_file(Path("config/profiles/dark.json"))

# Anpassen
profile.name = "Dark Modified"
profile.colors.tab_active_border = "#ffFF0000"  # Rot
profile.global_hue = 30         # Orange-Shift
profile.global_brightness = 0.8 # Dunkler

# Speichern
profile.save_to_file(Path("config/profiles/dark_modified.json"))
```

### QSS generieren
```python
# QSS aus Profile generieren
qss = profile.generate_qss()

# In Anwendung anwenden
from PySide6.QtWidgets import QApplication
app = QApplication.instance()
app.setStyleSheet(qss)
```

## Troubleshooting

### Theme erscheint nicht im Menü
- ✅ Datei in `config/profiles/` ablegen
- ✅ Dateiendung `.json` prüfen
- ✅ JSON-Syntax prüfen (validieren mit jsonlint.com)
- ✅ Anwendung neu starten

### Theme sieht falsch aus
- ✅ ARGB-Format prüfen: `#AARRGGBB` (8 Zeichen!)
- ✅ Alpha-Wert prüfen: `#00` = transparent, `#FF` = opak
- ✅ JSON-Struktur mit Beispiel vergleichen

### Transparenz funktioniert nicht
- ⚠️ Windows: Desktop Compositing aktivieren (Aero/DWM)
- ⚠️ Linux: Compositor erforderlich (Compiz, KWin, Picom)
- ⚠️ Alpha-Wert in Hex prüfen: `#00` - `#FF`

### Farben zu dunkel/hell
- 🔧 `global.brightness` anpassen (0.5 - 1.5 Bereich)
- 🔧 Farben direkt bearbeiten
- 🔧 Screenshots bei verschiedenen `brightness`-Werten machen

## Best Practices

1. **Immer von bestehendem Profil starten** - Kopieren statt neu erstellen
2. **Namen eindeutig wählen** - Duplikate mit QSS-Themes vermeiden
3. **ARGB konsistent verwenden** - Gleiche Alpha-Werte für zusammengehörige Elemente
4. **Global Transforms sparsam** - Zu hohe Werte können unleserlich werden
5. **Testen auf allen Plattformen** - Transparenz verhält sich unterschiedlich
6. **JSON validieren** - Syntax-Fehler führen zu Ladefehlern
7. **Git versionieren** - Profile sind Konfiguration, sollten im Repository sein

## Weiterführende Links

- [Theme System Guide](THEME_SYSTEM_GUIDE.md) - Vollständige API-Referenz
- [ARGB Color Picker](https://www.color-hex.com/) - Online Farbwähler
- [JSON Validator](https://jsonlint.com/) - JSON Syntax prüfen
- [Qt Stylesheet Reference](https://doc.qt.io/qt-6/stylesheet-reference.html) - QSS Dokumentation

---

**Tipp:** Experimentiere mit kleinen Änderungen! JSON-Profile sind nicht-destruktiv - einfach kopieren, ändern, testen. Original bleibt erhalten.
