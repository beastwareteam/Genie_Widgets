# Theme- und Transparenz-Features Vergleich
## Qt Advanced Docking System vs. WidgetSystem

**Erstellt:** März 2026  
**Analysiert:** Qt ADS Demo & WidgetSystem 

---

## 📊 Executive Summary

### Qt ADS (Referenz-Implementation)
- ✅ **Umfassendes Theme-Management-System** mit CThemeManager & CTheme
- ✅ **Live Theme Editor** mit Echtzeit-Vorschau
- ✅ **ARGB-Farbunterstützung** (Alpha-Kanal) für echte Transparenz
- ✅ **Theme-Profile** mit Import/Export (JSON)
- ✅ **Globale Farb-Transformationen** (Hue, Saturation, Brightness)
- ✅ **Widget-Feature-Editor** (Closable, Movable, Floatable, Pinnable)
- ✅ **Kategorisiertes Styling** (Core, Tabs, Titlebars, AutoHide, Overlays, Window Management)
- ✅ **Frameless Window** mit Drag-Support
- ✅ **Transparente Fenster** (WA_TranslucentBackground)

### WidgetSystem (Aktuell)
- ✅ Theme-Verwaltung über ThemeFactory
- ✅ Basis-Transparenz in transparent.qss (rgba)
- ✅ Tab-Farben-Konfiguration
- ✅ Theme-Wechsel zur Laufzeit
- ❌ **Kein Live Theme Editor**
- ❌ **Kein ARGB-Support** (nur rgba in QSS)
- ❌ **Keine globalen Farb-Transformationen**
- ❌ **Keine Theme-Profile** (Import/Export)
- ❌ **Keine Widget-Feature-Bearbeitung zur Laufzeit**
- ❌ **Keine kategorisierte Theme-Struktur**

---

## 🎨 Feature-Vergleich Detailliert

### 1. Theme-Management-Architektur

#### Qt ADS (Referenz)
```python
class CTheme:
    - name: str
    - stylesheet: str
    - palette: QPalette
    - has_custom_palette: bool
    - icons: dict[str, QIcon]
    - properties: dict[str, Any]

class CThemeManager:
    - themes: dict[str, CTheme]
    - current_theme_name: str
    - themeChanged: Signal(object)
    - registerTheme(theme)
    - setCurrentTheme(name)
```

**Features:**
- Zentrale Theme-Registry
- Signal-basiertes Event-System
- Icon-Mapping pro Theme
- Custom Properties pro Theme
- Custom QPalette pro Theme

#### WidgetSystem (Aktuell)
```python
@dataclass(frozen=True)
class ThemeDefinition:
    theme_id: str
    name: str
    file_path: Path
    tab_active_color: str
    tab_inactive_color: str

class ThemeFactory:
    - list_themes() -> list[ThemeDefinition]
    - get_default_stylesheet() -> str
    - get_tab_colors() -> tuple[str, str]
```

**Features:**
- JSON-basierte Theme-Definition
- Factory-Pattern für Theme-Erstellung
- Tab-Farben-Support
- Statische Theme-Ladung

**❌ Fehlende Features:**
- Keine zentrale Theme-Registry
- Kein Event-System (Signal/Slot)
- Keine Icon-Mappings
- Keine Custom Properties
- Keine Custom Palettes

---

### 2. Transparenz & ARGB-Support

#### Qt ADS (Referenz)

**ARGB Hex Format:**
```python
# ARGB = Alpha + RGB (8 hex digits)
"#00202124"  # 0% Opacity (fully transparent)
"#cc3c4043"  # 80% Opacity (20% transparent)
"#ff8ab4f8"  # 100% Opacity (fully opaque)
```

**Theme Profile Kategorien:**
```python
colors = {
    "core": {
        "window_bg": "#00202124",      # Fully transparent
        "splitter_handle": "#ff3c4043",
        "splitter_width": 2
    },
    "tabs": {
        "active_bg": "#cc3c4043",      # 80% opacity
        "active_border": "#ff8ab4f8",
        "inactive_bg": "#cc2d2e31",    # 80% opacity
    },
    "titlebars": {
        "bg": "#cc2d2e31",
        "text": "#ffe8eaed"
    },
    "decorations": {
        "btn_bg": "#40ffffff",         # 25% opacity
        "btn_icon": "#ffe8eaed",
        "floating_border": "#ff3c4043"
    },
    "autohide": {
        "sidebar_bg": "#cc202124",
        "tab_bg": "#cc2d2e31",
        "container_bg": "#cc202124",
        "container_border": "#ff8ab4f8"
    },
    "overlays": {
        "base_color": "#808ab4f8",     # 50% opacity
        "cross_color": "#ff8ab4f8",
        "border_color": "#ff8ab4f8",
        "border_width": 2
    }
}
```

**QSS Konvertierung:**
```python
def as_qss_color(color_hex: str) -> str:
    """Converts ARGB hex to rgba(r, g, b, a) for QSS compatibility."""
    color = QColor(color_hex)
    r, g, b, a = color.getRgb()
    return f"rgba({r}, {g}, {b}, {a})"
```

**Window-Level Transparenz:**
```python
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

palette = self.palette()
palette.setColor(self.backgroundRole(), QColor(0, 0, 0, 0))
self.setPalette(palette)
```

#### WidgetSystem (Aktuell)

**rgba() in QSS:**
```css
* {
    background-color: rgba(0, 0, 0, 0);
}

ads--CDockWidget {
    background-color: rgba(0, 0, 0, 0);
    border: 1px solid rgba(64, 64, 64, 0.5);
}

ads--CTitleBarButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
}

QTabBar::tab:selected {
    border-bottom: 2px solid rgba(100, 181, 246, 0.5);
}
```

**Window-Level Transparenz:**
```python
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

palette = self.palette()
from PySide6.QtGui import QColor
palette.setColor(self.backgroundRole(), QColor(0, 0, 0, 0))
self.setPalette(palette)
```

**✅ Vorhanden:**
- rgba() in QSS
- WA_TranslucentBackground
- Transparente Palette

**❌ Fehlend:**
- Kein ARGB-Hex-Format in Konfiguration
- Keine automatische ARGB → rgba() Konvertierung
- Keine kategorisierte Transparenz-Definition
- Keine Frameless Window Option

---

### 3. Live Theme Editor

#### Qt ADS (Referenz)

**CThemeEditor Features:**
```python
class CThemeEditor(QWidget):
    themeApplied = Signal()
    
    # Tabs:
    - "Elements" (Kategorien-basiert)
    - "Global FX" (Hue, Saturation, Brightness)
    - "Widget Properties" (Feature-Toggles)
    - "Profiles" (Import/Export)
```

**Element-Kategorie-Editor:**
```python
def add_category_group(title, category, fields):
    # Erstellt Farb-Picker (ARGB) und Spinboxen
    - "Core & Main Window"
    - "Window Management"
    - "Tabs & Navigation"
    - "Titlebars & Buttons"
    - "Auto-Hide (Sidebars)"
    - "Overlays (Drag & Drop)"
```

**ARGB-Farb-Picker:**
```python
class CARGBPicker(QPushButton):
    colorChanged = Signal(str)
    
    def pick(self):
        color = QColorDialog.getColor(
            QColor(self.argb), 
            self, 
            "Select ARGB Color", 
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.argb = color.name(QColor.NameFormat.HexArgb)
```

**Global FX Sliders:**
```python
- Hue Shift: 0-360°
- Saturation: 0-200%
- Brightness: 0-200%

def apply_global_transforms(color_hex: str) -> str:
    color = QColor(color_hex)
    h, s, v, a = color.getHsvF()
    
    h = (h + global_hue / 360.0) % 1.0
    s = max(0.0, min(1.0, s * global_saturation))
    v = max(0.0, min(1.0, v * global_brightness))
    
    return QColor.fromHsvF(h, s, v, a).name(QColor.NameFormat.HexArgb)
```

**Widget Feature Editor:**
```python
- Closable: QCheckBox
- Movable: QCheckBox
- Floatable: QCheckBox
- Pinnable: QCheckBox

def apply_widget_features():
    features = QtAds.CDockWidget.NoDockWidgetFeatures
    if closable.isChecked(): 
        features |= QtAds.CDockWidget.DockWidgetClosable
    # ...
    current_dock_widget.setFeatures(features)
```

**Theme Profile Import/Export:**
```python
def export_theme():
    path, _ = QFileDialog.getSaveFileName(...)
    with open(path, 'w') as f:
        f.write(profile.to_json())

def import_theme():
    path, _ = QFileDialog.getOpenFileName(...)
    with open(path, 'r') as f:
        profile = CThemeProfile.from_json(f.read())
    apply_theme()
```

#### WidgetSystem (Aktuell)

**❌ Kein Live Theme Editor vorhanden**

**ConfigurationPanel (Vorhanden):**
- JSON-Editierung für Konfigurationsdateien
- Kein visueller Theme-Editor
- Keine ARGB-Farb-Picker
- Keine Live-Vorschau

---

### 4. Theme-Kategorien & Struktur

#### Qt ADS (Referenz)

**7 Kategorien:**
1. **Core & Main Window** (Hintergründe, Splitter)
2. **Window Management** (Buttons, Icons, Floating)
3. **Tabs & Navigation** (Active/Inactive, Borders, Padding)
4. **Titlebars & Buttons** (Background, Text, Hover)
5. **Auto-Hide (Sidebars)** (Sidebar, Tabs, Container)
6. **Overlays (Drag & Drop)** (Drop-Zones, Borders)
7. **Global Properties** (Hue, Saturation, Brightness)

**QSS-Generierung:**
```python
def apply_theme():
    # Kategorisiertes QSS mit ARGB → rgba() Konvertierung
    qss = f"""
    /* 1. Core & Windows */
    QMainWindow {{ background: {c("core", "window_bg")}; }}
    ads--CDockSplitter::handle {{ background: {c("core", "splitter_handle")}; }}
    
    /* 2. Window Management */
    ads--CTitleBarButton {{ background: {c("decorations", "btn_bg")}; }}
    
    /* 3. Tabs */
    ads--CDockWidgetTab {{ background: {c("tabs", "inactive_bg")}; }}
    ads--CDockWidgetTab[activeTab="true"] {{ 
        background: {c("tabs", "active_bg")}; 
        border-bottom: 2px solid {c("tabs", "active_border")};
    }}
    
    /* 4. Titlebars */
    ads--CDockAreaTitleBar {{ background: {c("titlebars", "bg")}; }}
    
    /* 5. AutoHide */
    ads--CAutoHideSideBar {{ background: {c("autohide", "sidebar_bg")}; }}
    
    /* 6. Overlays */
    ads--CDockOverlay {{ 
        background-color: {c("overlays", "base_color")}; 
        border: {p['overlays']['border_width']}px solid {c("overlays", "border_color")};
    }}
    """
```

#### WidgetSystem (Aktuell)

**Struktur:**
```json
{
  "default_theme_id": "transparent",
  "themes": [
    {
      "id": "dark",
      "name": "Dark",
      "file": "themes/dark.qss",
      "tab_colors": {
        "active": "#E0E0E0",
        "inactive": "#cfcfcf"
      }
    }
  ]
}
```

**❌ Keine kategorisierte Struktur**
- Nur monolithische QSS-Dateien
- Keine granulare Konfiguration
- Keine Live-QSS-Generierung

---

## 🚀 Empfohlene Features für WidgetSystem

### Priority 1: Kritisch (Sofort implementieren)

#### 1.1 Theme Manager System
```python
# src/widgetsystem/core/theme_manager.py

class Theme:
    """Theme definition with palette, stylesheet, icons."""
    def __init__(self, theme_id: str, name: str) -> None:
        self.theme_id = theme_id
        self.name = name
        self.stylesheet: str = ""
        self.palette: QPalette | None = None
        self.icons: dict[str, QIcon] = {}
        self.properties: dict[str, Any] = {}

class ThemeManager(QObject):
    """Singleton theme manager with signal-based updates."""
    themeChanged = Signal(object)
    
    _instance: ThemeManager | None = None
    
    def __init__(self) -> None:
        super().__init__()
        self.themes: dict[str, Theme] = {}
        self.current_theme_id: str = ""
    
    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance
    
    def register_theme(self, theme: Theme) -> None:
        self.themes[theme.theme_id] = theme
    
    def set_current_theme(self, theme_id: str) -> bool:
        if theme_id not in self.themes:
            return False
        self.current_theme_id = theme_id
        self.themeChanged.emit(self.themes[theme_id])
        return True
    
    def current_theme(self) -> Theme | None:
        return self.themes.get(self.current_theme_id)
```

**Integration:**
```python
# In MainWindow.__init__():
theme_manager = ThemeManager.instance()
theme_manager.themeChanged.connect(self._on_theme_changed)

def _on_theme_changed(self, theme: Theme) -> None:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        app.setStyleSheet(theme.stylesheet)
        if theme.palette:
            app.setPalette(theme.palette)
```

#### 1.2 ARGB Theme Profile System
```python
# src/widgetsystem/core/theme_profile.py

@dataclass
class ThemeColors:
    """Categorized theme colors with ARGB support."""
    # Core
    window_bg: str = "#00202124"
    splitter_handle: str = "#ff3c4043"
    splitter_width: int = 2
    
    # Tabs
    tab_active_bg: str = "#cc3c4043"
    tab_active_border: str = "#ff8ab4f8"
    tab_active_text: str = "#ff8ab4f8"
    tab_inactive_bg: str = "#cc2d2e31"
    tab_inactive_text: str = "#ffbdc1c6"
    tab_padding: int = 4
    tab_border_radius: int = 0
    
    # Titlebars
    titlebar_bg: str = "#cc2d2e31"
    titlebar_text: str = "#ffe8eaed"
    titlebar_btn_hover: str = "#408ab4f8"
    
    # Decorations
    btn_bg: str = "#40ffffff"
    btn_icon: str = "#ffe8eaed"
    floating_border: str = "#ff3c4043"
    
    # AutoHide
    autohide_sidebar_bg: str = "#cc202124"
    autohide_tab_bg: str = "#cc2d2e31"
    autohide_container_bg: str = "#cc202124"
    autohide_container_border: str = "#ff8ab4f8"
    
    # Overlays
    overlay_base_color: str = "#808ab4f8"
    overlay_cross_color: str = "#ff8ab4f8"
    overlay_border_color: str = "#ff8ab4f8"
    overlay_border_width: int = 2

class ThemeProfile:
    """Theme profile with ARGB colors and global transformations."""
    def __init__(self, name: str = "Custom Profile") -> None:
        self.name = name
        self.colors = ThemeColors()
        self.global_hue: int = 0  # 0-360
        self.global_saturation: float = 1.0  # 0.0-2.0
        self.global_brightness: float = 1.0  # 0.0-2.0
    
    def as_qss_color(self, color_hex: str) -> str:
        """Convert ARGB hex to rgba(r, g, b, a) for QSS."""
        transformed = self.apply_global_transforms(color_hex)
        color = QColor(transformed)
        r, g, b, a = color.getRgb()
        return f"rgba({r}, {g}, {b}, {a})"
    
    def apply_global_transforms(self, color_hex: str) -> str:
        """Apply hue, saturation, brightness shifts."""
        color = QColor(color_hex)
        h, s, v, a = color.getHsvF()
        
        h = (h + self.global_hue / 360.0) % 1.0
        s = max(0.0, min(1.0, s * self.global_saturation))
        v = max(0.0, min(1.0, v * self.global_brightness))
        
        new_color = QColor.fromHsvF(h, s, v, a)
        return new_color.name(QColor.NameFormat.HexArgb)
    
    def generate_qss(self) -> str:
        """Generate QSS from profile colors."""
        c = self.colors
        return f"""
        /* Core */
        QMainWindow {{ background: {self.as_qss_color(c.window_bg)}; }}
        ads--CDockSplitter::handle {{ 
            background: {self.as_qss_color(c.splitter_handle)}; 
            width: {c.splitter_width}px;
        }}
        
        /* Tabs */
        ads--CDockWidgetTab {{ 
            background: {self.as_qss_color(c.tab_inactive_bg)}; 
            color: {self.as_qss_color(c.tab_inactive_text)};
            padding: {c.tab_padding}px;
            border-radius: {c.tab_border_radius}px;
        }}
        ads--CDockWidgetTab[activeTab="true"] {{ 
            background: {self.as_qss_color(c.tab_active_bg)}; 
            color: {self.as_qss_color(c.tab_active_text)};
            border-bottom: 2px solid {self.as_qss_color(c.tab_active_border)};
        }}
        
        /* Titlebars */
        ads--CDockAreaTitleBar {{ 
            background: {self.as_qss_color(c.titlebar_bg)}; 
        }}
        
        /* Buttons */
        ads--CTitleBarButton {{ 
            background: {self.as_qss_color(c.btn_bg)}; 
        }}
        ads--CTitleBarButton:hover {{ 
            background: {self.as_qss_color(c.titlebar_btn_hover)}; 
        }}
        
        /* AutoHide */
        ads--CAutoHideSideBar {{ 
            background: {self.as_qss_color(c.autohide_sidebar_bg)}; 
        }}
        
        /* Overlays */
        ads--CDockOverlay {{ 
            background-color: {self.as_qss_color(c.overlay_base_color)}; 
            border: {c.overlay_border_width}px solid {self.as_qss_color(c.overlay_border_color)};
        }}
        """
    
    def to_json(self) -> str:
        """Export profile to JSON."""
        data = {
            "name": self.name,
            "colors": asdict(self.colors),
            "global": {
                "hue": self.global_hue,
                "saturation": self.global_saturation,
                "brightness": self.global_brightness
            }
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ThemeProfile":
        """Import profile from JSON."""
        data = json.loads(json_str)
        profile = cls(data.get("name", "Imported"))
        profile.colors = ThemeColors(**data.get("colors", {}))
        glob = data.get("global", {})
        profile.global_hue = glob.get("hue", 0)
        profile.global_saturation = glob.get("saturation", 1.0)
        profile.global_brightness = glob.get("brightness", 1.0)
        return profile
```

**JSON Schema:**
```json
{
  "name": "Dark Transparent Pro",
  "colors": {
    "window_bg": "#00202124",
    "splitter_handle": "#ff3c4043",
    "tab_active_bg": "#cc3c4043",
    "tab_active_border": "#ff8ab4f8",
    ...
  },
  "global": {
    "hue": 0,
    "saturation": 1.0,
    "brightness": 1.0
  }
}
```

#### 1.3 Theme Factory Integration
```python
# Update ThemeFactory to support ThemeProfile

class ThemeFactory:
    def load_profile(self, profile_id: str) -> ThemeProfile | None:
        """Load theme profile from JSON."""
        profile_file = self.config_path / "profiles" / f"{profile_id}.json"
        if not profile_file.exists():
            return None
        
        with open(profile_file, "r", encoding="utf-8") as f:
            return ThemeProfile.from_json(f.read())
    
    def save_profile(self, profile: ThemeProfile, profile_id: str) -> bool:
        """Save theme profile to JSON."""
        profiles_dir = self.config_path / "profiles"
        profiles_dir.mkdir(exist_ok=True)
        
        profile_file = profiles_dir / f"{profile_id}.json"
        with open(profile_file, "w", encoding="utf-8") as f:
            f.write(profile.to_json())
        return True
```

### Priority 2: Wichtig (Nächste Phase)

#### 2.1 Live Theme Editor Widget
```python
# src/widgetsystem/ui/theme_editor.py

class ARGBColorPicker(QPushButton):
    """Color picker with alpha channel support."""
    colorChanged = Signal(str)
    
    def __init__(self, initial_argb: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.argb = initial_argb
        self.setFixedWidth(60)
        self.update_style()
        self.clicked.connect(self._pick_color)
    
    def update_style(self) -> None:
        color = QColor(self.argb)
        self.setStyleSheet(
            f"background-color: {color.name()}; "
            f"border: 1px solid white; height: 20px;"
        )
    
    def _pick_color(self) -> None:
        color = QColorDialog.getColor(
            QColor(self.argb),
            self,
            "Select ARGB Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.argb = color.name(QColor.NameFormat.HexArgb)
            self.update_style()
            self.colorChanged.emit(self.argb)

class ThemeEditorWidget(QWidget):
    """Live theme editor with real-time preview."""
    themeApplied = Signal()
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.profile = ThemeProfile()
        self.init_ui()
    
    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Tab 1: Color Categories
        tabs.addTab(self._create_colors_tab(), "Colors")
        
        # Tab 2: Global Effects
        tabs.addTab(self._create_global_fx_tab(), "Global FX")
        
        # Tab 3: Widget Features
        tabs.addTab(self._create_features_tab(), "Widget Features")
        
        # Tab 4: Import/Export
        tabs.addTab(self._create_io_tab(), "Import/Export")
        
        # Apply Button
        apply_btn = QPushButton("APPLY THEME LIVE")
        apply_btn.setStyleSheet(
            "background-color: #4caf50; color: white; "
            "height: 30px; font-weight: bold;"
        )
        apply_btn.clicked.connect(self._apply_theme)
        layout.addWidget(apply_btn)
    
    def _create_colors_tab(self) -> QWidget:
        widget = QScrollArea()
        widget.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Core Category
        layout.addWidget(self._create_category_group(
            "Core & Main Window",
            [
                ("window_bg", "Application Background"),
                ("splitter_handle", "Splitter Handle"),
                ("splitter_width", "Splitter Width", "int")
            ]
        ))
        
        # Tabs Category
        layout.addWidget(self._create_category_group(
            "Tabs & Navigation",
            [
                ("tab_active_bg", "Active Tab Background"),
                ("tab_active_border", "Active Tab Border"),
                ("tab_active_text", "Active Tab Text"),
                ("tab_inactive_bg", "Inactive Tab Background"),
                ("tab_inactive_text", "Inactive Tab Text"),
            ]
        ))
        
        # ... (weitere Kategorien)
        
        widget.setWidget(content)
        return widget
    
    def _create_category_group(
        self, title: str, fields: list[tuple[str, str, str]]
    ) -> QGroupBox:
        group = QGroupBox(title)
        form = QFormLayout(group)
        
        for field in fields:
            attr_name = field[0]
            label = field[1]
            field_type = field[2] if len(field) > 2 else "color"
            
            if field_type == "color":
                initial_color = getattr(self.profile.colors, attr_name)
                picker = ARGBColorPicker(initial_color)
                picker.colorChanged.connect(
                    lambda val, attr=attr_name: self._update_color(attr, val)
                )
                form.addRow(label, picker)
            elif field_type == "int":
                spinbox = QSpinBox()
                spinbox.setRange(0, 50)
                spinbox.setValue(getattr(self.profile.colors, attr_name))
                spinbox.valueChanged.connect(
                    lambda val, attr=attr_name: self._update_int(attr, val)
                )
                form.addRow(label, spinbox)
        
        return group
    
    def _create_global_fx_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        
        # Hue Slider
        hue_slider = QSlider(Qt.Orientation.Horizontal)
        hue_slider.setRange(0, 360)
        hue_slider.setValue(0)
        hue_slider.valueChanged.connect(self._update_hue)
        form.addRow("Hue Shift (0-360°)", hue_slider)
        
        # Saturation Slider
        sat_slider = QSlider(Qt.Orientation.Horizontal)
        sat_slider.setRange(0, 200)
        sat_slider.setValue(100)
        sat_slider.valueChanged.connect(self._update_saturation)
        form.addRow("Saturation (0-200%)", sat_slider)
        
        # Brightness Slider
        brt_slider = QSlider(Qt.Orientation.Horizontal)
        brt_slider.setRange(0, 200)
        brt_slider.setValue(100)
        brt_slider.valueChanged.connect(self._update_brightness)
        form.addRow("Brightness (0-200%)", brt_slider)
        
        return widget
    
    def _create_features_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        
        info = QLabel("Focus a dock widget to edit its features")
        form.addRow(info)
        
        # Feature Checkboxes (später implementieren)
        
        return widget
    
    def _create_io_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        export_btn = QPushButton("Export Theme Profile (.json)")
        export_btn.clicked.connect(self._export_theme)
        layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import Theme Profile (.json)")
        import_btn.clicked.connect(self._import_theme)
        layout.addWidget(import_btn)
        
        layout.addStretch()
        return widget
    
    def _update_color(self, attr_name: str, argb: str) -> None:
        setattr(self.profile.colors, attr_name, argb)
        self._apply_theme()
    
    def _update_int(self, attr_name: str, value: int) -> None:
        setattr(self.profile.colors, attr_name, value)
        self._apply_theme()
    
    def _update_hue(self, value: int) -> None:
        self.profile.global_hue = value
        self._apply_theme()
    
    def _update_saturation(self, value: int) -> None:
        self.profile.global_saturation = value / 100.0
        self._apply_theme()
    
    def _update_brightness(self, value: int) -> None:
        self.profile.global_brightness = value / 100.0
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        qss = self.profile.generate_qss()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(qss)
        self.themeApplied.emit()
    
    def _export_theme(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Theme Profile", "", "JSON Files (*.json)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.profile.to_json())
            QMessageBox.information(
                self, "Success", f"Theme exported to {Path(path).name}"
            )
    
    def _import_theme(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme Profile", "", "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.profile = ThemeProfile.from_json(f.read())
                self._apply_theme()
                QMessageBox.information(
                    self, "Success", "Theme imported and applied"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to import theme: {e}"
                )
```

**Integration in MainWindow:**
```python
def _show_theme_editor(self) -> None:
    """Show live theme editor panel."""
    editor_widget = ThemeEditorWidget()
    
    # Create dock for editor
    editor_dock = QtAds.CDockWidget(
        self.dock_manager,
        "Live Theme Editor",
        self
    )
    editor_dock.setWidget(editor_widget)
    editor_dock.setIcon(QIcon(":/icons/palette.svg"))
    
    self.dock_manager.addDockWidget(
        QtAds.RightDockWidgetArea, 
        editor_dock
    )
    self.docks.append(editor_dock)
    
    # Connect signals
    editor_widget.themeApplied.connect(
        lambda: print("✓ Theme applied")
    )
```

#### 2.2 Frameless Window Option
```python
# Update MainWindow to support frameless mode

class MainWindow(QMainWindow):
    def __init__(self, frameless: bool = False) -> None:
        super().__init__()
        
        if frameless:
            self._setup_frameless_window()
        
        # ... rest of initialization
    
    def _setup_frameless_window(self) -> None:
        """Configure frameless window with custom controls."""
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        
        # Transparent palette
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0, 0))
        self.setPalette(palette)
        
        # Add window controls to menuBar corner
        self._add_window_controls()
        
        # Dragging support
        self._drag_pos: QPoint | None = None
    
    def _add_window_controls(self) -> None:
        """Add minimize/maximize/close buttons."""
        controls = QWidget()
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 10, 15, 0)
        layout.setSpacing(8)
        
        def create_btn(
            symbol: str, 
            slot: Any, 
            color: str, 
            hover_color: str
        ) -> QPushButton:
            btn = QPushButton(symbol)
            btn.setFixedSize(14, 14)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    background: {color}; 
                    border-radius: 7px; 
                    border: none;
                }}
                QPushButton:hover {{ background: {hover_color}; }}
            """)
            btn.clicked.connect(slot)
            return btn
        
        layout.addWidget(create_btn(
            "", self.showMinimized, "#febc2e", "#d6a228"
        ))
        layout.addWidget(create_btn(
            "", self._toggle_maximize, "#28c840", "#1e9d32"
        ))
        layout.addWidget(create_btn(
            "", self.close, "#ff5f57", "#d34b45"
        ))
        
        if hasattr(self, "menuBar"):
            self.menuBar().setCornerWidget(
                controls, Qt.Corner.TopRightCorner
            )
    
    def _toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def mousePressEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - 
                self.frameGeometry().topLeft()
            )
            event.accept()
    
    def mouseMoveEvent(self, event: Any) -> None:
        if self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: Any) -> None:
        self._drag_pos = None
```

### Priority 3: Nice-to-Have (Langfristig)

#### 3.1 Theme Presets Manager
```python
# src/widgetsystem/core/theme_presets.py

class ThemePresetsManager:
    """Manages built-in and custom theme presets."""
    
    BUILTIN_PRESETS = {
        "dark_transparent": ThemeProfile(name="Dark Transparent"),
        "light_transparent": ThemeProfile(name="Light Transparent"),
        "dark_pro": ThemeProfile(name="Dark Pro"),
        "midnight": ThemeProfile(name="Midnight"),
        "ocean_blue": ThemeProfile(name="Ocean Blue"),
    }
    
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.presets_dir = config_path / "profiles"
        self.presets_dir.mkdir(exist_ok=True)
    
    def list_presets(self) -> list[str]:
        """List all available presets (built-in + custom)."""
        builtin = list(self.BUILTIN_PRESETS.keys())
        custom = [
            f.stem for f in self.presets_dir.glob("*.json")
        ]
        return builtin + custom
    
    def load_preset(self, preset_id: str) -> ThemeProfile | None:
        """Load a preset by ID."""
        if preset_id in self.BUILTIN_PRESETS:
            return self.BUILTIN_PRESETS[preset_id]
        
        preset_file = self.presets_dir / f"{preset_id}.json"
        if preset_file.exists():
            with open(preset_file, "r", encoding="utf-8") as f:
                return ThemeProfile.from_json(f.read())
        
        return None
    
    def save_preset(
        self, profile: ThemeProfile, preset_id: str
    ) -> bool:
        """Save a custom preset."""
        preset_file = self.presets_dir / f"{preset_id}.json"
        with open(preset_file, "w", encoding="utf-8") as f:
            f.write(profile.to_json())
        return True
```

#### 3.2 Widget Feature Editor Integration
```python
# Add to ThemeEditorWidget

def _create_features_tab(self) -> QWidget:
    widget = QWidget()
    form = QFormLayout(widget)
    
    self.widget_info = QLabel("Focus a dock widget to edit features")
    form.addRow(self.widget_info)
    
    self.feat_closable = QCheckBox("Closable")
    self.feat_movable = QCheckBox("Movable")
    self.feat_floatable = QCheckBox("Floatable")
    self.feat_pinnable = QCheckBox("Pinnable")
    
    for checkbox in [
        self.feat_closable, 
        self.feat_movable, 
        self.feat_floatable, 
        self.feat_pinnable
    ]:
        form.addRow(checkbox)
        checkbox.toggled.connect(self._apply_widget_features)
    
    return widget

def set_active_dock_widget(self, dock_widget: Any) -> None:
    """Update feature checkboxes for active widget."""
    self.current_dock_widget = dock_widget
    if dock_widget:
        self.widget_info.setText(
            f"Active: {dock_widget.windowTitle()}"
        )
        features = dock_widget.features()
        self.feat_closable.setChecked(
            bool(features & QtAds.CDockWidget.DockWidgetClosable)
        )
        self.feat_movable.setChecked(
            bool(features & QtAds.CDockWidget.DockWidgetMovable)
        )
        self.feat_floatable.setChecked(
            bool(features & QtAds.CDockWidget.DockWidgetFloatable)
        )
        self.feat_pinnable.setChecked(
            bool(features & QtAds.CDockWidget.DockWidgetPinnable)
        )

def _apply_widget_features(self) -> None:
    """Apply feature changes to active widget."""
    if not self.current_dock_widget:
        return
    
    features = QtAds.CDockWidget.NoDockWidgetFeatures
    if self.feat_closable.isChecked():
        features |= QtAds.CDockWidget.DockWidgetClosable
    if self.feat_movable.isChecked():
        features |= QtAds.CDockWidget.DockWidgetMovable
    if self.feat_floatable.isChecked():
        features |= QtAds.CDockWidget.DockWidgetFloatable
    if self.feat_pinnable.isChecked():
        features |= QtAds.CDockWidget.DockWidgetPinnable
    
    self.current_dock_widget.setFeatures(features)
```

**MainWindow Integration:**
```python
# Track focus changes for widget feature editor
def __init__(self) -> None:
    # ... existing code
    
    # Connect focus tracking
    app = QApplication.instance()
    if app:
        app.focusChanged.connect(self._on_focus_changed)

def _on_focus_changed(self, old: QWidget, new: QWidget) -> None:
    """Update theme editor when focus changes."""
    if new:
        widget = new
        while widget:
            if isinstance(widget, QtAds.CDockWidget):
                if hasattr(self, "theme_editor"):
                    self.theme_editor.set_active_dock_widget(widget)
                break
            widget = widget.parentWidget()
```

---

## 📋 Implementation Checklist

### Phase 1: Foundation (2-3 Wochen)
- [ ] ThemeManager Klasse erstellen
- [ ] Theme Klasse mit Palette/Icons/Properties
- [ ] Signal-basiertes Event-System
- [ ] ThemeProfile Klasse mit ThemeColors dataclass
- [ ] ARGB → rgba() Konvertierung
- [ ] Global Transformationen (Hue, Saturation, Brightness)
- [ ] QSS-Generierung aus ThemeProfile
- [ ] JSON Import/Export für ThemeProfile
- [ ] ThemeFactory Integration
- [ ] Unit Tests für Theme-System

### Phase 2: UI Editor (2-3 Wochen)
- [ ] ARGBColorPicker Widget mit Alpha-Kanal
- [ ] ThemeEditorWidget Grundstruktur
- [ ] Colors Tab mit Kategorie-Gruppen
- [ ] Global FX Tab mit Slidern
- [ ] Widget Features Tab (Skeleton)
- [ ] Import/Export Tab mit File Dialogs
- [ ] Live-Apply Funktionalität
- [ ] Integration in MainWindow als Dock
- [ ] Toolbar-Button für Theme-Editor

### Phase 3: Advanced Features (1-2 Wochen)
- [ ] Widget Feature Editor (Runtime-Anpassung)
- [ ] Focus-Tracking für aktives Widget
- [ ] ThemePresetsManager mit Built-in Presets
- [ ] Preset-Auswahl in Theme-Editor
- [ ] Frameless Window Option
- [ ] Window Controls (Minimize/Maximize/Close)
- [ ] Drag-Support für Frameless Window
- [ ] Dokumentation und Beispiele

### Phase 4: Polish & Testing (1 Woche)
- [ ] Integration Tests
- [ ] UI Tests
- [ ] Performance-Optimierung
- [ ] Fehlerbehandlung
- [ ] User Documentation
- [ ] API Documentation
- [ ] Demo-Anwendung mit Theme-Editor

---

## 🎯 Migrations-Strategie

### Schritt 1: Backwards Compatibility
```python
# ThemeFactory behält alte API bei:
def get_default_stylesheet(self) -> str:
    """Legacy method - loads from .qss file."""
    # Existing implementation

def list_themes(self) -> list[ThemeDefinition]:
    """Legacy method - loads from themes.json."""
    # Existing implementation

# Neue API parallel einführen:
def load_profile(self, profile_id: str) -> ThemeProfile | None:
    """New method - loads theme profile with ARGB."""
    # New implementation
```

### Schritt 2: Opt-in Migration
```python
# In config/themes.json:
{
  "version": 2,  # Neues Format
  "default_theme_id": "dark_transparent",
  "themes": [
    {
      "id": "dark",
      "name": "Dark",
      "type": "qss",  # Legacy
      "file": "themes/dark.qss"
    },
    {
      "id": "dark_transparent_pro",
      "name": "Dark Transparent Pro",
      "type": "profile",  # New
      "profile": "profiles/dark_transparent_pro.json"
    }
  ]
}
```

### Schritt 3: Gradual Adoption
1. **Woche 1-2:** ThemeManager + ThemeProfile implementieren
2. **Woche 3-4:** Theme-Editor UI erstellen
3. **Woche 5:** Migration Helper schreiben (.qss → .json)
4. **Woche 6:** Dokumentation + Tutorials

---

## 📊 Zusammenfassung

### Neue Features (14 Haupt-Features)

#### Kritisch (6):
1. ✅ **ThemeManager Singleton** mit Event-System
2. ✅ **Theme Klasse** mit Palette/Icons/Properties
3. ✅ **ThemeProfile System** mit ARGB-Support
4. ✅ **Kategorisierte Farbstruktur** (7 Kategorien)
5. ✅ **ARGB → rgba() Konvertierung**
6. ✅ **JSON Import/Export** für Profile

#### Wichtig (5):
7. ✅ **Live Theme Editor Widget**
8. ✅ **ARGBColorPicker** mit Alpha-Kanal
9. ✅ **Global FX Transformationen** (Hue/Sat/Brt)
10. ✅ **Frameless Window Option**
11. ✅ **Window Controls** (Drag/Minimize/Maximize)

#### Nice-to-Have (3):
12. ✅ **Widget Feature Editor** (Runtime)
13. ✅ **Theme Presets Manager**
14. ✅ **Built-in Presets** (5 Themes)

### Vorteile

1. **Flexibilität:** Live-Bearbeitung ohne Neustart
2. **Konsistenz:** Kategorisierte Struktur
3. **Transparenz:** ARGB-Support für echte Transparenz
4. **Wiederverwendbarkeit:** Import/Export von Profilen
5. **User Experience:** Visueller Editor statt JSON-Text
6. **Professionalität:** Feature-Parität mit Qt ADS Demo

---

## 🔗 Referenzen

- **Qt ADS Demo:** `c:\Users\StarLap\Qt-Advanced-Docking-System - Kopie\demo\`
- **WidgetSystem:** `d:\Projekte\python\WidgetSystem\`
- **Theme Files:** `themes_pyside6.py`, `theme_profile_pyside6.py`, `theme_editor_pyside6.py`
- **Main Demo:** `main_pyside6.py`

---

**Ende des Vergleichsberichts**
