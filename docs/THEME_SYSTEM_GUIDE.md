# Theme System Implementation Guide

## Übersicht

Das WidgetSystem verfügt nun über ein vollständiges Theme-Management-System mit ARGB-Transparenz-Unterstützung, das vom Qt Advanced Docking System inspiriert ist.

## Neue Features ✨

### 1. **ThemeManager** - Zentrales Theme-Registry System
- Singleton-Pattern für globalen Zugriff
- Signal-basierte Theme-Änderungen
- Support für Custom Properties & Icons pro Theme

### 2. **ThemeProfile** - ARGB-Farbunterstützung
- ARGB Hex Format (#AARRGGBB) mit Alpha-Kanal
- 7 Kategorisierte Farbbereiche (Core, Tabs, Titlebars, Decorations, AutoHide, Overlays)
- Globale Farb-Transformationen (Hue, Saturation, Brightness)
- Automatische QSS-Generierung aus Profil
- JSON Import/Export

### 3. **Erweiterte ThemeFactory**
- Unterstützt Legacy QSS-Themes UND neue Profile
- Automatische Default-Profile-Erstellung
- Profile-Verwaltung (Load/Save/List)

## Verwendung

### Theme-Profile erstellen

```python
from widgetsystem.core import ThemeProfile

# Neues Profil erstellen
profile = ThemeProfile(name="My Custom Theme")

# Farben anpassen (ARGB Format: #AARRGGBB)
profile.colors.window_bg = "#00202124"  # Vollständig transparent
profile.colors.tab_active_bg = "#cc3c4043"  # 80% Opazität
profile.colors.tab_active_border = "#ff8ab4f8"  # Solid Blue

# Globale Transformationen
profile.global_hue = 30  # Farbton verschieben
profile.global_saturation = 1.2  # Sättigung erhöhen
profile.global_brightness = 0.9  # Helligkeit reduzieren

# QSS generieren
qss = profile.generate_qss()

# Als JSON speichern
profile.save_to_file(Path("config/profiles/my_theme.json"))
```

### Theme-Profile laden

```python
from pathlib import Path
from widgetsystem.core import ThemeProfile

# Aus Datei laden
profile = ThemeProfile.load_from_file(Path("config/profiles/dark_transparent.json"))

# Über Factory laden
from widgetsystem.factories.theme_factory import ThemeFactory

factory = ThemeFactory(Path("config"))
profile = factory.load_profile("dark_transparent")
```

### ThemeManager verwenden

```python
from widgetsystem.core import Theme, ThemeManager

# Singleton-Instanz abrufen
theme_manager = ThemeManager.instance()

# Theme registrieren
theme = Theme("my_theme", "My Custom Theme")
theme.set_stylesheet(qss_content)
theme.set_property("author", "John Doe")
theme_manager.register_theme(theme)

# Theme wechseln
theme_manager.set_current_theme("my_theme")

# Auf Theme-Änderungen reagieren
theme_manager.themeChanged.connect(on_theme_changed)

def on_theme_changed(theme: Theme):
    app = QApplication.instance()
    app.setStyleSheet(theme.stylesheet)
```

### In MainWindow integriert

Die MainWindow-Klasse verwendet jetzt automatisch ThemeManager:

```python
# Themes werden automatisch beim Start registriert
# - Legacy QSS-Themes aus config/themes.json
# - Profile-Themes aus config/profiles/*.json

# Theme über Toolbar-Menü wechseln
# - Menü "Themes" zeigt alle verfügbaren Themes
# - Click auf Theme-Name wechselt Theme live

# Programmatisch Theme wechseln
self.theme_manager.set_current_theme("profile_dark_transparent")
```

## ARGB-Farbformat

### Format-Syntax
```
#AARRGGBB
 │││││││└─ Blue (00-FF)
 ││││││└── Green (00-FF)
 │││││└─── Red (00-FF)
 ││││└──── Alpha (00=transparent, FF=opaque)
 └───────── Hash-Prefix
```

### Beispiele
```python
"#00000000"  # Vollständig transparent
"#40ffffff"  # 25% Opazität Weiß
"#80ff0000"  # 50% Opazität Rot
"#cc3c4043"  # 80% Opazität Grau
"#ffffffff"  # 100% Opazität Weiß (solid)
```

### Konvertierung zu QSS
ThemeProfile konvertiert automatisch ARGB → rgba():
```python
profile.as_qss_color("#cc3c4043")
# Output: "rgba(60, 64, 67, 204)"
```

## Vordefinierte Profile

### 1. **dark_transparent** (Default)
- Dunkles Theme mit transparentem Hintergrund
- 80% Opazität für Panels
- Blaue Akzentfarben

### 2. **light_transparent**
- Helles Theme mit transparentem Hintergrund
- 80% Opazität für Panels
- Blaue Akzentfarben

### 3. **solid_dark**
- Dunkles Theme ohne Transparenz
- 100% Opazität überall
- Für maximale Lesbarkeit

### 4. **midnight_blue** (Custom)
- Dunkelblaues Theme
- Hoher Kontrast
- Cyan-Akzente

### 5. **ocean_breeze** (Custom)
- Helles Blau-Theme
- Sanfte Farben
- Perfekt für längere Arbeitssitzungen

## Farb-Kategorien

ThemeProfile organisiert Farben in 7 Kategorien:

### 1. Core & Main Window
```python
window_bg          # Hauptfenster-Hintergrund
splitter_handle    # Splitter-Farbe
splitter_width     # Splitter-Breite (px)
```

### 2. Tabs & Navigation
```python
tab_active_bg      # Aktiver Tab Hintergrund
tab_active_border  # Aktiver Tab Border
tab_active_text    # Aktiver Tab Text
tab_inactive_bg    # Inaktiver Tab Hintergrund
tab_inactive_text  # Inaktiver Tab Text
tab_padding        # Tab-Padding (px)
tab_border_radius  # Tab-Ecken-Radius (px)
```

### 3. Titlebars & Buttons
```python
titlebar_bg        # Titlebar-Hintergrund
titlebar_text      # Titlebar-Text
titlebar_btn_hover # Button-Hover-Overlay
```

### 4. Window Management / Decorations
```python
btn_bg             # Button-Hintergrund
btn_icon           # Button-Icon-Farbe
floating_border    # Floating-Window-Border
```

### 5. Auto-Hide (Sidebars)
```python
autohide_sidebar_bg        # Sidebar-Hintergrund
autohide_tab_bg            # Tab-Hintergrund
autohide_container_bg      # Container-Hintergrund
autohide_container_border  # Container-Border
```

### 6. Overlays (Drag & Drop)
```python
overlay_base_color    # Drop-Zone-Farbe
overlay_cross_color   # Dock-Cross-Farbe
overlay_border_color  # Overlay-Border
overlay_border_width  # Border-Breite (px)
```

## Globale Farb-Transformationen

Profile unterstützen globale HSV-Transformationen:

```python
profile.global_hue = 180        # Hue-Shift: 0-360°
profile.global_saturation = 1.5 # Saturation: 0.0-2.0
profile.global_brightness = 0.8 # Brightness: 0.0-2.0
```

Diese werden beim QSS-Export automatisch auf alle Farben angewendet.

**Beispiel:**
```python
# Original: Blue (#ff0000ff)
profile.colors.tab_active_border = "#ff0000ff"
profile.global_hue = 180  # Shift to Cyan

# Resultat im QSS: Cyan (#ff00ffff)
```

## Migration von Legacy-Themes

### Option 1: Weiterhin QSS verwenden
Legacy QSS-Themes in `themes/*.qss` funktionieren weiterhin über `themes.json`:

```json
{
  "id": "my_theme",
  "name": "My Theme",
  "file": "themes/my_theme.qss"
}
```

### Option 2: Zu Profilen migrieren

1. Erstelle neues Profil:
```python
from widgetsystem.core import ThemeProfile

profile = ThemeProfile(name="My Theme Converted")
# Farben aus QSS übertragen...
profile.save_to_file(Path("config/profiles/my_theme.json"))
```

2. Profil wird automatisch beim nächsten Start registriert

## Dateisystem-Struktur

```
WidgetSystem/
├── config/
│   ├── themes.json           # Legacy Theme-Definitionen
│   └── profiles/             # Theme-Profile (ARGB)
│       ├── dark_transparent.json
│       ├── light_transparent.json
│       ├── solid_dark.json
│       ├── midnight_blue.json
│       └── ocean_breeze.json
├── themes/
│   ├── dark.qss             # Legacy QSS
│   ├── light.qss
│   └── transparent.qss
└── src/widgetsystem/
    ├── core/
    │   ├── theme_manager.py  # ThemeManager & Theme
    │   └── theme_profile.py  # ThemeProfile & ThemeColors
    └── factories/
        └── theme_factory.py  # Erweitert mit Profile-Support
```

## API-Referenz

### Theme Klasse
```python
class Theme:
    theme_id: str
    name: str
    stylesheet: str
    palette: QPalette | None
    has_custom_palette: bool
    icons: dict[str, QIcon]
    properties: dict[str, Any]
    
    def set_stylesheet(stylesheet: str) -> None
    def set_palette(palette: QPalette) -> None
    def set_icon(icon_id: str, icon: QIcon) -> None
    def get_icon(icon_id: str) -> QIcon
    def set_property(name: str, value: Any) -> None
    def get_property(name: str, default: Any = None) -> Any
```

### ThemeManager Klasse
```python
class ThemeManager(QObject):
    themeChanged: Signal  # Emittiert Theme-Objekt
    
    @classmethod
    def instance() -> ThemeManager
    
    def register_theme(theme: Theme) -> None
    def current_theme() -> Theme | None
    def get_theme(theme_id: str) -> Theme | None
    def set_current_theme(theme_id: str) -> bool
    def theme_names() -> list[str]
    def clear() -> None
```

### ThemeProfile Klasse
```python
class ThemeProfile:
    name: str
    colors: ThemeColors
    global_hue: int              # 0-360
    global_saturation: float     # 0.0-2.0
    global_brightness: float     # 0.0-2.0
    
    def as_qss_color(color_hex: str) -> str
    def apply_global_transforms(color_hex: str) -> str
    def generate_qss() -> str
    def to_json() -> str
    def save_to_file(file_path: Path) -> None
    
    @classmethod
    def from_json(json_str: str) -> ThemeProfile
    
    @classmethod
    def load_from_file(file_path: Path) -> ThemeProfile
```

### ThemeFactory Erweiterungen
```python
class ThemeFactory:
    # Legacy API (unverändert)
    def list_themes() -> list[ThemeDefinition]
    def get_default_theme() -> ThemeDefinition | None
    def get_default_stylesheet() -> str
    def get_tab_colors() -> tuple[str, str]
    
    # Neue Profile API
    def load_profile(profile_id: str) -> ThemeProfile | None
    def save_profile(profile: ThemeProfile, profile_id: str) -> bool
    def list_profiles() -> list[str]
    def create_default_profiles() -> None
```

## Best Practices

### 1. Theme-Entwicklung
- Beginne mit einem Default-Profil als Vorlage
- Teste Transparenz auf verschiedenen Hintergründen
- Verwende konsistente Alpha-Werte pro Kategorie
- Dokumentiere Custom Properties

### 2. Farb-Auswahl
- **Core:** Komplett transparent (#00xxxxxx) für echte Transparenz
- **Tabs:** 80% Opazität (#ccxxxxxx) für gute Lesbarkeit
- **Buttons:** 25-40% Opazität (#40xxxxxx) für subtile Effekte
- **Overlays:** 50% Opazität (#80xxxxxx) für Sichtbarkeit

### 3. Barrierefreiheit
- Minimaler Kontrast: 4.5:1 für Text
- Teste mit Solid-Theme für maximale Lesbarkeit
- Verwende kontrastreiche Akzentfarben

### 4. Performance
- Profile werden einmalig beim Start geladen
- QSS-Generierung erfolgt nur bei Theme-Wechsel
- Verwende ThemeManager.instance() für globalen Zugriff

## Troubleshooting

### Theme wird nicht angezeigt
```python
# Prüfe Theme-Registry
theme_manager = ThemeManager.instance()
print(theme_manager.theme_names())

# Prüfe Profil-Verzeichnis
factory = ThemeFactory(Path("config"))
print(factory.list_profiles())
```

### Farben werden nicht angewendet
```python
# Teste QSS-Generierung
profile = factory.load_profile("my_theme")
if profile:
    qss = profile.generate_qss()
    print(qss[:200])  # Erste 200 Zeichen
```

### Transparenz funktioniert nicht
```python
# Stelle sicher, dass WA_TranslucentBackground gesetzt ist
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

# Setze transparente Palette
palette = self.palette()
palette.setColor(self.backgroundRole(), QColor(0, 0, 0, 0))
self.setPalette(palette)
```

## Beispiele

### Vollständiges Theme erstellen
```python
from pathlib import Path
from widgetsystem.core import ThemeProfile, ThemeManager, Theme
from widgetsystem.factories.theme_factory import ThemeFactory

# 1. Profil erstellen
profile = ThemeProfile(name="Sunset Theme")
profile.colors.window_bg = "#00fef3e7"
profile.colors.tab_active_bg = "#ccff6f00"
profile.colors.tab_active_text = "#ffffffff"
profile.colors.tab_inactive_bg = "#ccffa726"
profile.global_hue = 30  # Orange-Shift

# 2. Speichern
factory = ThemeFactory(Path("config"))
factory.save_profile(profile, "sunset")

# 3. Registrieren & Anwenden
theme_manager = ThemeManager.instance()
theme = Theme("profile_sunset", "Sunset Theme")
theme.set_stylesheet(profile.generate_qss())
theme_manager.register_theme(theme)
theme_manager.set_current_theme("profile_sunset")
```

### Theme in Laufzeit anpassen
```python
# Aktuelles Theme abrufen
current_theme = theme_manager.current_theme()
if current_theme and current_theme.get_property("is_profile"):
    profile_id = current_theme.get_property("profile_id")
    
    # Profil laden und anpassen
    profile = factory.load_profile(profile_id)
    if profile:
        profile.global_brightness = 1.2
        
        # Neu registrieren
        theme.set_stylesheet(profile.generate_qss())
        theme_manager.set_current_theme(current_theme.theme_id)
```

## Support & Weiterentwicklung

### Geplante Features (Phase 2)
- [ ] Live Theme Editor Widget
- [ ] ARGB Color Picker mit Alpha-Slider
- [ ] Theme-Vorschau im Menü
- [ ] Widget Feature Editor (Closable/Movable/etc.)
- [ ] Frameless Window Option

### Bekannte Limitierungen
- Globale Transformationen wirken auf alle Farben gleichmäßig
- Kein per-Widget Theme-Override
- Palette-Support nur auf Application-Ebene

### Beiträge
Siehe `docs/THEME_TRANSPARENCY_COMPARISON.md` für vollständige Feature-Liste und Implementierungsplan.

---

**Version:** 1.0.0  
**Datum:** März 2026  
**Status:** Production Ready ✅
