# WidgetSystem Theme System

## Overview

The Theme System provides comprehensive theming capabilities including:

- Theme definitions with color palettes
- QSS stylesheet generation
- ARGB color support with alpha channel
- Dynamic gradient rendering
- Live theme editing
- Theme profiles for quick switching

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   ThemeManager                       │
│  - Theme state management                            │
│  - Signal emission on changes                        │
│  - Stylesheet application                            │
├─────────────────────────────────────────────────────┤
│                   ThemeFactory                       │
│  - Theme loading from JSON                           │
│  - QSS stylesheet generation                         │
│  - Theme creation/modification                       │
├─────────────────────────────────────────────────────┤
│                   ThemeProfile                       │
│  - Color palette definitions                         │
│  - ARGB color handling                               │
│  - Profile switching                                 │
├─────────────────────────────────────────────────────┤
│                  GradientSystem                      │
│  - Gradient definitions                              │
│  - QSS gradient generation                           │
│  - Dynamic gradient rendering                        │
└─────────────────────────────────────────────────────┘
```

---

## ThemeManager

Central theme state management with Qt signals.

### Basic Usage

```python
from widgetsystem.core import ThemeManager, Theme

# Create manager
manager = ThemeManager()

# Set active theme
manager.set_theme("dark")

# Get current theme info
current = manager.current_theme
print(f"Current theme: {current.name}")

# Get specific color
bg_color = manager.get_color("background")

# Apply stylesheet to widget
manager.apply_stylesheet(main_window)
```

### Signals

```python
# Connect to theme changes
manager.themeChanged.connect(on_theme_changed)
manager.colorsUpdated.connect(on_colors_updated)
manager.styleApplied.connect(on_style_applied)

def on_theme_changed(theme_name: str) -> None:
    print(f"Theme changed to: {theme_name}")
    # Update UI elements that need manual refresh

def on_colors_updated(colors: dict) -> None:
    # React to color changes
    for key, value in colors.items():
        print(f"  {key}: {value}")
```

### Theme Registration

```python
from widgetsystem.core import Theme

# Define a new theme
custom_theme = Theme(
    name="custom",
    display_name="My Custom Theme",
    colors={
        "background": "#2d2d2d",
        "foreground": "#e0e0e0",
        "accent": "#ff5722"
    },
    stylesheet_path="themes/custom.qss"
)

# Register with manager
manager.register_theme(custom_theme)
```

---

## ThemeFactory

Factory for creating and managing themes from configuration.

### Loading Themes

```python
from widgetsystem.factories import ThemeFactory
from pathlib import Path

factory = ThemeFactory(Path("config"))

# Get theme definition
theme = factory.get_theme("dark")
# Returns: {
#     "name": "Dark Theme",
#     "colors": {...},
#     "stylesheet": "dark.qss"
# }

# Get QSS stylesheet
stylesheet = factory.get_stylesheet("dark")

# List available themes
themes = factory.list_themes()
# Returns: ["dark", "light", "transparent"]
```

### Creating Themes

```python
# Create new theme
factory.create_theme("ocean", {
    "background": "#0d1117",
    "foreground": "#c9d1d9",
    "accent": "#58a6ff",
    "border": "#30363d",
    "selection": "#388bfd"
})

# Derive from existing theme
factory.derive_theme("ocean_dark", "ocean", {
    "accent": "#1f6feb"  # Override only accent
})
```

---

## Theme Colors

### Standard Color Keys

| Key | Description | Example |
|-----|-------------|---------|
| `background` | Main background | `#1e1e1e` |
| `background_alt` | Alternative background | `#252526` |
| `foreground` | Primary text | `#d4d4d4` |
| `foreground_muted` | Secondary text | `#808080` |
| `accent` | Primary accent | `#007acc` |
| `accent_hover` | Accent on hover | `#1c97ea` |
| `border` | Border color | `#3c3c3c` |
| `divider` | Divider lines | `#454545` |
| `selection` | Selection highlight | `#264f78` |
| `error` | Error state | `#f44747` |
| `warning` | Warning state | `#cca700` |
| `success` | Success state | `#4ec9b0` |
| `info` | Info state | `#3794ff` |

### ARGB Color Format

Colors support alpha channel using `#AARRGGBB` format:

```json
{
  "colors": {
    "overlay": "#80000000",
    "panel_bg": "#e01e1e1e",
    "glass_effect": "#40ffffff"
  }
}
```

**Alpha Values:**

| Hex | Decimal | Transparency |
|-----|---------|--------------|
| `FF` | 255 | 0% (Opaque) |
| `E0` | 224 | 12% |
| `C0` | 192 | 25% |
| `A0` | 160 | 37% |
| `80` | 128 | 50% |
| `60` | 96 | 62% |
| `40` | 64 | 75% |
| `20` | 32 | 87% |
| `00` | 0 | 100% (Transparent) |

### Using ARGB Colors

```python
from PySide6.QtGui import QColor

# Parse ARGB color
def parse_argb(color_str: str) -> QColor:
    """Parse #AARRGGBB or #RRGGBB to QColor."""
    if len(color_str) == 9:  # #AARRGGBB
        alpha = int(color_str[1:3], 16)
        r = int(color_str[3:5], 16)
        g = int(color_str[5:7], 16)
        b = int(color_str[7:9], 16)
        return QColor(r, g, b, alpha)
    else:  # #RRGGBB
        return QColor(color_str)

# Create ARGB string
def to_argb(color: QColor) -> str:
    """Convert QColor to #AARRGGBB string."""
    return f"#{color.alpha():02x}{color.red():02x}{color.green():02x}{color.blue():02x}"
```

---

## ThemeProfile

Pre-defined color palettes for quick theme switching.

### Structure

```python
from widgetsystem.core import ThemeProfile, ThemeColors

# Define color palette
colors = ThemeColors(
    background="#1e1e1e",
    background_alt="#252526",
    foreground="#d4d4d4",
    accent="#007acc",
    border="#3c3c3c"
)

# Create profile
profile = ThemeProfile(
    name="dark",
    display_name="Dark Theme",
    colors=colors,
    transparency_enabled=False
)
```

### Profile Configuration

**File**: `config/profiles/dark.json`

```json
{
  "name": "dark",
  "display_name": "Dark Theme",
  "base_theme": "dark",
  "transparency": false,
  "colors": {
    "window_background": "#1e1e1e",
    "panel_background": "#252526",
    "titlebar_background": "#323233",
    "titlebar_foreground": "#cccccc",
    "menu_background": "#2d2d2d",
    "menu_foreground": "#d4d4d4",
    "menu_highlight": "#094771",
    "text_primary": "#d4d4d4",
    "text_secondary": "#808080",
    "text_disabled": "#5a5a5a",
    "accent_primary": "#007acc",
    "accent_secondary": "#1c97ea",
    "accent_tertiary": "#40a9ff",
    "border_primary": "#3c3c3c",
    "border_secondary": "#454545",
    "scrollbar_track": "#1e1e1e",
    "scrollbar_thumb": "#4a4a4a",
    "scrollbar_thumb_hover": "#5a5a5a",
    "tab_active": "#1e1e1e",
    "tab_inactive": "#2d2d2d",
    "tab_hover": "#383838",
    "button_background": "#0e639c",
    "button_foreground": "#ffffff",
    "button_hover": "#1177bb",
    "button_pressed": "#094771",
    "input_background": "#3c3c3c",
    "input_foreground": "#cccccc",
    "input_border": "#3c3c3c",
    "input_focus_border": "#007acc"
  }
}
```

### Transparent Profile

**File**: `config/profiles/transparent.json`

```json
{
  "name": "transparent",
  "display_name": "Transparent",
  "base_theme": "dark",
  "transparency": true,
  "blur_effect": true,
  "blur_radius": 10,
  "colors": {
    "window_background": "#c01e1e1e",
    "panel_background": "#b0252526",
    "titlebar_background": "#a0323233",
    "menu_background": "#d02d2d2d",
    "overlay": "#80000000"
  }
}
```

---

## GradientSystem

Dynamic gradient rendering for backgrounds and effects.

### GradientDefinition

```python
from widgetsystem.core import GradientDefinition, GradientStop, GradientRenderer

# Define gradient
gradient = GradientDefinition(
    type="linear",
    angle=45,
    stops=[
        GradientStop(position=0.0, color="#1e1e1e"),
        GradientStop(position=0.5, color="#2d2d2d"),
        GradientStop(position=1.0, color="#1e1e1e")
    ]
)

# Render to QSS
renderer = GradientRenderer()
qss = renderer.to_qss(gradient)
# Returns: "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e1e1e, stop:0.5 #2d2d2d, stop:1 #1e1e1e)"
```

### Gradient Types

```python
# Linear gradient
linear = GradientDefinition(
    type="linear",
    angle=90,  # Top to bottom
    stops=[...]
)

# Radial gradient
radial = GradientDefinition(
    type="radial",
    center=(0.5, 0.5),
    radius=0.5,
    stops=[...]
)

# Conical gradient
conical = GradientDefinition(
    type="conical",
    center=(0.5, 0.5),
    angle=0,
    stops=[...]
)
```

### Using Gradients in QSS

```css
/* Linear gradient background */
QWidget {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1e1e1e,
        stop:0.5 #2d2d2d,
        stop:1 #1e1e1e
    );
}

/* Radial gradient */
QPushButton {
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.5,
        fx:0.5, fy:0.5,
        stop:0 #007acc,
        stop:1 #005a9c
    );
}
```

---

## QSS Stylesheets

### Structure

**File**: `themes/dark.qss`

```css
/* ============================================
   Dark Theme Stylesheet
   ============================================ */

/* ----- Global ----- */
QWidget {
    background-color: @background;
    color: @foreground;
    font-family: @font_family;
    font-size: @font_size;
}

/* ----- Main Window ----- */
QMainWindow {
    background-color: @background;
}

QMainWindow::separator {
    background-color: @border;
    width: 1px;
    height: 1px;
}

/* ----- Menu Bar ----- */
QMenuBar {
    background-color: @menu_background;
    color: @foreground;
    padding: 2px;
}

QMenuBar::item {
    padding: 4px 8px;
    background: transparent;
}

QMenuBar::item:selected {
    background-color: @selection;
}

/* ----- Menu ----- */
QMenu {
    background-color: @menu_background;
    border: 1px solid @border;
    padding: 4px 0px;
}

QMenu::item {
    padding: 6px 32px 6px 24px;
}

QMenu::item:selected {
    background-color: @selection;
}

QMenu::separator {
    height: 1px;
    background-color: @border;
    margin: 4px 8px;
}

/* ----- Tab Widget ----- */
QTabWidget::pane {
    border: 1px solid @border;
    background-color: @background;
}

QTabBar::tab {
    background-color: @tab_inactive;
    color: @foreground_muted;
    padding: 8px 16px;
    border: none;
}

QTabBar::tab:selected {
    background-color: @tab_active;
    color: @foreground;
}

QTabBar::tab:hover:!selected {
    background-color: @tab_hover;
}

/* ----- Dock Widget ----- */
ads--CDockWidget {
    background-color: @panel_background;
}

ads--CDockWidgetTab {
    background-color: @tab_inactive;
    padding: 4px 8px;
}

ads--CDockWidgetTab[activeTab="true"] {
    background-color: @tab_active;
}

/* ----- Buttons ----- */
QPushButton {
    background-color: @button_background;
    color: @button_foreground;
    border: none;
    padding: 6px 16px;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: @button_hover;
}

QPushButton:pressed {
    background-color: @button_pressed;
}

QPushButton:disabled {
    background-color: @background_alt;
    color: @text_disabled;
}

/* ----- Line Edit ----- */
QLineEdit {
    background-color: @input_background;
    color: @input_foreground;
    border: 1px solid @input_border;
    padding: 4px 8px;
}

QLineEdit:focus {
    border-color: @input_focus_border;
}

/* ----- Scroll Bar ----- */
QScrollBar:vertical {
    background-color: @scrollbar_track;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: @scrollbar_thumb;
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: @scrollbar_thumb_hover;
}

/* ----- Tree View ----- */
QTreeView {
    background-color: @background;
    border: none;
}

QTreeView::item {
    padding: 4px;
}

QTreeView::item:selected {
    background-color: @selection;
}

QTreeView::item:hover:!selected {
    background-color: @background_alt;
}
```

### Variable Substitution

The ThemeFactory replaces `@variable` placeholders with actual colors:

```python
def apply_variables(self, stylesheet: str, colors: dict) -> str:
    """Replace @variables with color values."""
    result = stylesheet
    for key, value in colors.items():
        result = result.replace(f"@{key}", value)
    return result
```

---

## ARGBColorPicker

Interactive color picker with alpha channel support.

### Usage

```python
from widgetsystem.ui import ARGBColorPicker
from PySide6.QtGui import QColor

# Create picker
picker = ARGBColorPicker()

# Connect to changes
picker.colorChanged.connect(on_color_changed)

# Set initial color (with alpha)
picker.set_color(QColor(0, 122, 204, 200))  # #c8007acc

# Get current color
color = picker.get_color()
argb_string = f"#{color.alpha():02x}{color.red():02x}{color.green():02x}{color.blue():02x}"

def on_color_changed(color: QColor) -> None:
    print(f"New color: {color.name(QColor.HexArgb)}")
```

### Features

- RGBA sliders (0-255)
- Hex input (#AARRGGBB)
- Color wheel/picker
- Alpha transparency preview
- Preset color palette
- Recent colors history

---

## ThemeEditor

Live theme editing dialog.

### Usage

```python
from widgetsystem.ui import ThemeEditor
from pathlib import Path

# Create editor
editor = ThemeEditor(config_path=Path("config"), parent=main_window)

# Connect to changes
editor.themeModified.connect(on_theme_modified)

# Show editor
editor.show()

def on_theme_modified(theme_name: str, colors: dict) -> None:
    print(f"Theme {theme_name} modified")
    # Apply changes immediately or save
```

### Features

- Color property editors for all theme colors
- Live preview of changes
- Save/discard changes
- Create new themes
- Export/import themes
- Reset to defaults

---

## Best Practices

1. **Use Standard Keys**: Stick to standard color key names for consistency
2. **Provide Fallbacks**: Always have a fallback for missing colors
3. **Test Transparency**: Test ARGB colors on different backgrounds
4. **Validate QSS**: Test stylesheets thoroughly before deployment
5. **Document Colors**: Comment theme files explaining color usage
6. **Use Variables**: Use `@variable` syntax in QSS for maintainability
7. **Signal Updates**: React to theme signals for dynamic updates
8. **Performance**: Cache processed stylesheets

---

## Troubleshooting

### Colors Not Applying

1. Check color key spelling
2. Verify QSS variable names match
3. Ensure stylesheet is loaded
4. Check widget specificity in QSS

### Transparency Not Working

1. Verify `WA_TranslucentBackground` is set
2. Check platform supports transparency
3. Ensure compositor is running
4. Use proper ARGB format

### Gradients Not Rendering

1. Check gradient syntax in QSS
2. Verify stop positions are 0.0-1.0
3. Test with solid colors first
4. Check Qt version compatibility
