# JSON Theme-Profile - Vollständige Farbfelder-Referenz

## Alle verfügbaren Farbfelder (Version 2.0)

### ✅ **ALTE Felder** (in deiner aktuellen dark_transparent.json):
Bereits vorhanden, werden weiterhin unterstützt:
- `window_bg`, `splitter_handle`, `splitter_width`
- `tab_active_bg`, `tab_active_border`, `tab_active_text`
- `tab_inactive_bg`, `tab_inactive_text`
- `tab_padding`, `tab_border_radius`
- `titlebar_bg`, `titlebar_text`, `titlebar_btn_hover`
- `btn_bg`, `btn_icon`
- `floating_border`
- `autohide_sidebar_bg`, `autohide_tab_bg`, `autohide_container_bg`, `autohide_container_border`
- `overlay_base_color`, `overlay_cross_color`, `overlay_border_color`, `overlay_border_width`

### 🆕 **NEUE Felder** (jetzt verfügbar):

#### **Tabs**
```json
"tab_hover_bg": "#40ffffff"  // Tab-Hover-Effekt (war vorher hardcoded)
```

#### **Titlebar Buttons**
```json
"titlebar_btn_pressed": "#60ffffff"  // ButtonPressed State (war vorher hardcoded)
```

#### **Toolbar** (NEU!)
```json
"toolbar_bg": "#cc2d2e31",               // Toolbar Hintergrund
"toolbar_separator": "#ff4c4c4c",        // Toolbar Separator Farbe
"toolbar_button_bg": "#00000000",        // Toolbar Button Hintergrund (transparent)
"toolbar_button_hover": "#40ffffff",     // Toolbar Button Hover
"toolbar_button_pressed": "#60ffffff"    // Toolbar Button Pressed
```

#### **Push Buttons** (NEU!)
```json
"pushbutton_bg": "#ff3c4043",            // Button Hintergrund
"pushbutton_text": "#ffe8eaed",          // Button Text
"pushbutton_border": "#ff5c5c5c",        // Button Border
"pushbutton_hover_bg": "#ff4c5054",      // Button Hover Hintergrund
"pushbutton_pressed_bg": "#ff5c6064"     // Button Pressed Hintergrund
```

#### **Input Widgets** (NEU! - QLineEdit, QTextEdit, QPlainTextEdit)
```json
"input_bg": "#ff2d2e31",                 // Input Hintergrund
"input_text": "#ffe8eaed",               // Input Text
"input_border": "#ff3c4043",             // Input Border
"input_focus_border": "#ff8ab4f8",       // Input Focus Border
"input_selection_bg": "#ff1565c0",       // Text Selection Hintergrund
"input_selection_text": "#ffffffff"      // Text Selection Farbe
```

#### **ComboBox/Dropdown** (NEU!)
```json
"combobox_bg": "#ff2d2e31",              // ComboBox Hintergrund
"combobox_text": "#ffe8eaed",            // ComboBox Text
"combobox_border": "#ff3c4043",          // ComboBox Border
"combobox_dropdown_bg": "#ff3c4043"      // Dropdown Arrow Hintergrund
```

#### **ScrollBar** (NEU!)
```json
"scrollbar_bg": "#ff1a1a1a",             // ScrollBar Hintergrund
"scrollbar_handle": "#ff4c4c4c",         // ScrollBar Handle (Slider)
"scrollbar_handle_hover": "#ff8ab4f8"    // ScrollBar Handle Hover
```

#### **Menu** (NEU! - erweitert)
```json
"menu_bg": "#ff2d2e31",                  // Menü Hintergrund
"menu_text": "#ffe8eaed",                // Menü Text
"menu_border": "#ff3c4043",              // Menü Border
"menu_item_selected_bg": "#cc3c4043",    // Selected Item Hintergrund
"menu_item_selected_text": "#ff8ab4f8"   // Selected Item Text
```

## 🎯 Verwendung

### **Option 1: Erweiterte JSON verwenden**
Kopiere die neue Vorlage:
```bash
cp config/profiles/dark_transparent_FULL.json config/profiles/my_custom_theme.json
```

Bearbeite alle Felder nach Wunsch, speichern, App neu starten oder ↻ klicken.

### **Option 2: Bestehende JSON erweitern**
Füge fehlende Felder zu deiner aktuellen JSON hinzu:

```json
{
  "name": "Dark Transparent",
  "colors": {
    // ... deine bestehenden Farben ...
    
    // ✨ Neue Felder hinzufügen:
    "tab_hover_bg": "#40ffffff",
    "titlebar_btn_pressed": "#60ffffff",
    "toolbar_bg": "#cc2d2e31",
    "toolbar_separator": "#ff4c4c4c",
    "toolbar_button_bg": "#00000000",
    "toolbar_button_hover": "#40ffffff",
    "toolbar_button_pressed": "#60ffffff",
    "pushbutton_bg": "#ff3c4043",
    "pushbutton_text": "#ffe8eaed",
    "pushbutton_border": "#ff5c5c5c",
    "pushbutton_hover_bg": "#ff4c5054",
    "pushbutton_pressed_bg": "#ff5c6064",
    "input_bg": "#ff2d2e31",
    "input_text": "#ffe8eaed",
    "input_border": "#ff3c4043",
    "input_focus_border": "#ff8ab4f8",
    "input_selection_bg": "#ff1565c0",
    "input_selection_text": "#ffffffff",
    "combobox_bg": "#ff2d2e31",
    "combobox_text": "#ffe8eaed",
    "combobox_border": "#ff3c4043",
    "combobox_dropdown_bg": "#ff3c4043",
    "scrollbar_bg": "#ff1a1a1a",
    "scrollbar_handle": "#ff4c4c4c",
    "scrollbar_handle_hover": "#ff8ab4f8",
    "menu_bg": "#ff2d2e31",
    "menu_text": "#ffe8eaed",
    "menu_border": "#ff3c4043",
    "menu_item_selected_bg": "#cc3c4043",
    "menu_item_selected_text": "#ff8ab4f8"
  }
}
```

### **Option 3: Nur benötigte Felder hinzufügen**
Das System verwendet **Default-Werte** für fehlende Felder. Du kannst selektiv nur die Felder hinzufügen, die du ändern möchtest.

## ⚠️ Abwärtskompatibilität

**WICHTIG:** Alte JSON-Profile funktionieren weiterhin! Fehlende Felder verwenden Default-Werte aus der ThemeColors-Klasse.

Deine aktuelle `dark_transparent.json` bleibt funktional - du siehst jetzt nur mehr steuerbare UI-Elemente!

## 📋 Komponenten-Mapping

| UI-Komponente | Farbfelder |
|---------------|------------|
| **Dock-Fenster** | `window_bg`, `splitter_handle`, `floating_border` |
| **Tabs** | `tab_active_*`, `tab_inactive_*`, `tab_hover_bg` |
| **Titlebar** | `titlebar_bg`, `titlebar_text`, `titlebar_btn_*` |
| **Toolbar** | `toolbar_*` (5 Felder) |
| **Buttons** | `pushbutton_*` (5 Felder) |
| **Input** | `input_*` (6 Felder) |
| **ComboBox** | `combobox_*` (4 Felder) |
| **ScrollBar** | `scrollbar_*` (3 Felder) |
| **Menu** | `menu_*` (5 Felder) |
| **Auto-Hide** | `autohide_*` (4 Felder) |
| **Overlay** | `overlay_*` (4 Felder) |

## 🔧 Testing

1. **Kopiere Vorlage:**
   ```bash
   cp config/profiles/dark_transparent_FULL.json config/profiles/test_theme.json
   ```

2. **Ändere einzelne Felder:**
   ```json
   "pushbutton_bg": "#ffFF0000"  // ← Rote Buttons!
   ```

3. **Speichern + Refresh (↻)**

4. **Wähle "Dark Transparent (FULL)" im Theme-Menü**

Jetzt sollten alle UI-Elemente steuerbar sein!

## 🎨 Beispiel: Komplett Grünes Theme

```json
{
  "name": "Matrix Green",
  "colors": {
    "window_bg": "#00000000",
    "tab_active_border": "#ff00ff00",
    "tab_active_text": "#ff00ff00",
    "titlebar_text": "#ff00ff00",
    "toolbar_button_hover": "#4000ff00",
    "pushbutton_bg": "#ff003300",
    "pushbutton_text": "#ff00ff00",
    "input_text": "#ff00ff00",
    "input_focus_border": "#ff00ff00",
    "scrollbar_handle_hover": "#ff00ff00",
    "menu_item_selected_text": "#ff00ff00"
  },
  "global": {
    "hue": 120,          // Alles nach Grün verschieben
    "saturation": 1.5,   // Kräftigere Farben
    "brightness": 1.0
  }
}
```

---

**Nächste Schritte:**
1. Teste die erweiterte Vorlage: `dark_transparent_FULL.json`
2. Passe einzelne Felder an
3. Finde heraus, welche UI-Elemente du noch vermisst hast
4. Feedback geben, falls weitere Felder benötigt werden!
