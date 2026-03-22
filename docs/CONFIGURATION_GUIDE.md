# WidgetSystem Configuration Guide

## Overview

WidgetSystem is entirely configuration-driven. All UI elements, layouts, themes, and behaviors are defined in JSON files located in the `config/` directory. Each configuration file has a corresponding JSON Schema in `schemas/` for validation.

---

## Configuration Files

| File | Purpose | Schema |
|------|---------|--------|
| `layouts.json` | Window layouts and dock arrangement | `layouts.schema.json` |
| `themes.json` | Theme definitions and colors | `themes.schema.json` |
| `panels.json` | Dock panel configurations | `panels.schema.json` |
| `menus.json` | Menu bars and context menus | `menus.schema.json` |
| `tabs.json` | Tab groups and tab settings | `tabs.schema.json` |
| `dnd.json` | Drag and drop settings | `dnd.schema.json` |
| `responsive.json` | Responsive layout breakpoints | `responsive.schema.json` |
| `lists.json` | List widget configurations | - |
| `ui_config.json` | General UI settings | - |
| `i18n.*.json` | Internationalization files | - |
| `profiles/*.json` | Theme color profiles | - |

---

## Layouts Configuration

**File**: `config/layouts.json`

Defines window layouts for the docking system.

```json
{
  "version": "1.0",
  "default_layout": "main",
  "layouts": {
    "main": {
      "name": "Main Layout",
      "description": "Default application layout",
      "areas": [
        {
          "id": "left",
          "type": "dock",
          "position": "left",
          "width": 250,
          "panels": ["explorer", "outline"]
        },
        {
          "id": "center",
          "type": "content",
          "flex": 1
        },
        {
          "id": "right",
          "type": "dock",
          "position": "right",
          "width": 300,
          "panels": ["properties"]
        },
        {
          "id": "bottom",
          "type": "dock",
          "position": "bottom",
          "height": 200,
          "panels": ["terminal", "output"]
        }
      ]
    },
    "minimal": {
      "name": "Minimal Layout",
      "areas": [
        {"id": "center", "type": "content", "flex": 1}
      ]
    }
  }
}
```

### Layout Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique area identifier |
| `type` | string | `"dock"` or `"content"` |
| `position` | string | `"left"`, `"right"`, `"top"`, `"bottom"` |
| `width` | number | Fixed width in pixels |
| `height` | number | Fixed height in pixels |
| `flex` | number | Flexible size factor |
| `panels` | array | Panel IDs to place in this area |

---

## Themes Configuration

**File**: `config/themes.json`

Defines theme colors and stylesheet references.

```json
{
  "version": "1.0",
  "default_theme": "dark",
  "themes": {
    "dark": {
      "name": "Dark Theme",
      "description": "Modern dark color scheme",
      "stylesheet": "dark.qss",
      "colors": {
        "background": "#1e1e1e",
        "background_alt": "#252526",
        "foreground": "#d4d4d4",
        "foreground_muted": "#808080",
        "accent": "#007acc",
        "accent_hover": "#1c97ea",
        "border": "#3c3c3c",
        "selection": "#264f78",
        "error": "#f44747",
        "warning": "#cca700",
        "success": "#4ec9b0"
      }
    },
    "light": {
      "name": "Light Theme",
      "colors": {
        "background": "#ffffff",
        "background_alt": "#f3f3f3",
        "foreground": "#1e1e1e",
        "accent": "#0066cc"
      }
    }
  }
}
```

### ARGB Color Format

Colors support alpha channel using `#AARRGGBB` format:

```json
{
  "colors": {
    "panel_background": "#e01e1e1e",
    "overlay": "#80000000",
    "transparent_accent": "#c0007acc"
  }
}
```

| Alpha Value | Transparency |
|-------------|--------------|
| `FF` | Fully opaque (100%) |
| `C0` | 75% opaque |
| `80` | 50% opaque |
| `40` | 25% opaque |
| `00` | Fully transparent |

---

## Panels Configuration

**File**: `config/panels.json`

Defines dock panel properties.

```json
{
  "version": "1.0",
  "panels": {
    "explorer": {
      "title": "Explorer",
      "icon": "folder-open",
      "closable": true,
      "movable": true,
      "floatable": true,
      "default_area": "left",
      "min_width": 150,
      "max_width": 500,
      "features": ["tree_view", "search", "context_menu"],
      "toolbar": {
        "actions": ["new_file", "new_folder", "refresh", "collapse_all"]
      }
    },
    "properties": {
      "title": "Properties",
      "icon": "settings",
      "closable": true,
      "default_area": "right",
      "min_width": 200
    },
    "terminal": {
      "title": "Terminal",
      "icon": "terminal",
      "closable": true,
      "default_area": "bottom",
      "min_height": 100,
      "max_height": 400
    }
  }
}
```

### Panel Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | string | required | Panel title text |
| `icon` | string | none | Icon name |
| `closable` | boolean | true | Can be closed |
| `movable` | boolean | true | Can be moved/docked |
| `floatable` | boolean | true | Can be floated |
| `default_area` | string | none | Initial dock position |
| `min_width` | number | 0 | Minimum width |
| `max_width` | number | none | Maximum width |
| `min_height` | number | 0 | Minimum height |
| `max_height` | number | none | Maximum height |
| `features` | array | [] | Enabled features |

---

## Menus Configuration

**File**: `config/menus.json`

Defines menu bars and context menus.

```json
{
  "version": "1.0",
  "menubar": {
    "menus": ["file", "edit", "view", "help"]
  },
  "menus": {
    "file": {
      "title": "&File",
      "items": [
        {
          "action": "new",
          "text": "&New",
          "shortcut": "Ctrl+N",
          "icon": "file-new"
        },
        {
          "action": "open",
          "text": "&Open...",
          "shortcut": "Ctrl+O",
          "icon": "folder-open"
        },
        {"type": "separator"},
        {
          "action": "save",
          "text": "&Save",
          "shortcut": "Ctrl+S",
          "icon": "save",
          "enabled_when": "document.modified"
        },
        {
          "action": "save_as",
          "text": "Save &As...",
          "shortcut": "Ctrl+Shift+S"
        },
        {"type": "separator"},
        {
          "submenu": "recent_files",
          "text": "Recent Files"
        },
        {"type": "separator"},
        {
          "action": "exit",
          "text": "E&xit",
          "shortcut": "Alt+F4"
        }
      ]
    },
    "edit": {
      "title": "&Edit",
      "items": [
        {"action": "undo", "text": "&Undo", "shortcut": "Ctrl+Z"},
        {"action": "redo", "text": "&Redo", "shortcut": "Ctrl+Y"},
        {"type": "separator"},
        {"action": "cut", "text": "Cu&t", "shortcut": "Ctrl+X"},
        {"action": "copy", "text": "&Copy", "shortcut": "Ctrl+C"},
        {"action": "paste", "text": "&Paste", "shortcut": "Ctrl+V"}
      ]
    },
    "view": {
      "title": "&View",
      "items": [
        {
          "action": "toggle_panel",
          "text": "Explorer",
          "checkable": true,
          "checked": true,
          "panel": "explorer"
        },
        {
          "action": "toggle_panel",
          "text": "Properties",
          "checkable": true,
          "checked": true,
          "panel": "properties"
        }
      ]
    }
  },
  "context_menus": {
    "editor": {
      "items": [
        {"action": "cut", "text": "Cut"},
        {"action": "copy", "text": "Copy"},
        {"action": "paste", "text": "Paste"},
        {"type": "separator"},
        {"action": "select_all", "text": "Select All"}
      ]
    }
  }
}
```

### Menu Item Properties

| Property | Type | Description |
|----------|------|-------------|
| `action` | string | Action identifier to trigger |
| `text` | string | Menu item text (& for accelerator) |
| `shortcut` | string | Keyboard shortcut |
| `icon` | string | Icon name |
| `enabled_when` | string | Condition for enabling |
| `checkable` | boolean | Item can be checked |
| `checked` | boolean | Initial check state |
| `submenu` | string | Reference to submenu |
| `type` | string | `"separator"` for divider |

---

## Tabs Configuration

**File**: `config/tabs.json`

Defines tab group configurations.

```json
{
  "version": "1.0",
  "tab_groups": {
    "main_tabs": {
      "position": "top",
      "movable": true,
      "closable": true,
      "document_mode": true,
      "elide_mode": "right",
      "tabs": [
        {
          "id": "welcome",
          "title": "Welcome",
          "icon": "home",
          "closable": false
        },
        {
          "id": "editor",
          "title": "Editor",
          "icon": "code"
        }
      ]
    },
    "output_tabs": {
      "position": "bottom",
      "movable": false,
      "tabs": [
        {"id": "output", "title": "Output"},
        {"id": "problems", "title": "Problems"},
        {"id": "terminal", "title": "Terminal"}
      ]
    }
  }
}
```

### Tab Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `position` | string | "top" | `"top"`, `"bottom"`, `"left"`, `"right"` |
| `movable` | boolean | true | Tabs can be reordered |
| `closable` | boolean | true | Tabs can be closed |
| `document_mode` | boolean | false | Document-style tabs |
| `elide_mode` | string | "none" | Text elision: `"left"`, `"right"`, `"middle"` |

---

## Drag and Drop Configuration

**File**: `config/dnd.json`

Configures drag and drop behavior.

```json
{
  "version": "1.0",
  "drag_drop": {
    "enabled": true,
    "mime_types": [
      "text/plain",
      "text/uri-list",
      "application/json"
    ],
    "drop_actions": ["copy", "move", "link"],
    "default_action": "copy",
    "visual_feedback": true,
    "feedback_style": {
      "highlight_color": "#007acc",
      "highlight_width": 2
    }
  },
  "sources": {
    "explorer": {
      "enabled": true,
      "mime_type": "text/uri-list"
    },
    "palette": {
      "enabled": true,
      "mime_type": "application/x-widget"
    }
  },
  "targets": {
    "editor": {
      "accepts": ["text/plain", "text/uri-list"]
    },
    "canvas": {
      "accepts": ["application/x-widget"]
    }
  }
}
```

---

## Responsive Configuration

**File**: `config/responsive.json`

Defines responsive layout breakpoints.

```json
{
  "version": "1.0",
  "breakpoints": {
    "xs": {"max_width": 575},
    "sm": {"min_width": 576, "max_width": 767},
    "md": {"min_width": 768, "max_width": 991},
    "lg": {"min_width": 992, "max_width": 1199},
    "xl": {"min_width": 1200}
  },
  "rules": {
    "sidebar": {
      "xs": {"visible": false},
      "sm": {"visible": true, "width": 200, "collapsible": true},
      "md": {"visible": true, "width": 250},
      "lg": {"visible": true, "width": 300},
      "xl": {"visible": true, "width": 350}
    },
    "toolbar": {
      "xs": {"mode": "compact"},
      "sm": {"mode": "compact"},
      "md": {"mode": "normal"},
      "lg": {"mode": "expanded"}
    }
  }
}
```

---

## Internationalization

**Files**: `config/i18n.*.json` (one per language)

### English (`i18n.en.json`)

```json
{
  "language": "en",
  "name": "English",
  "translations": {
    "menu.file": "File",
    "menu.edit": "Edit",
    "menu.view": "View",
    "menu.help": "Help",
    "action.new": "New",
    "action.open": "Open",
    "action.save": "Save",
    "action.close": "Close",
    "button.ok": "OK",
    "button.cancel": "Cancel",
    "button.apply": "Apply",
    "dialog.save_changes": "Do you want to save changes?",
    "dialog.unsaved_title": "Unsaved Changes"
  }
}
```

### German (`i18n.de.json`)

```json
{
  "language": "de",
  "name": "Deutsch",
  "translations": {
    "menu.file": "Datei",
    "menu.edit": "Bearbeiten",
    "menu.view": "Ansicht",
    "menu.help": "Hilfe",
    "action.new": "Neu",
    "action.open": "Öffnen",
    "action.save": "Speichern",
    "action.close": "Schließen",
    "button.ok": "OK",
    "button.cancel": "Abbrechen",
    "button.apply": "Anwenden",
    "dialog.save_changes": "Möchten Sie die Änderungen speichern?",
    "dialog.unsaved_title": "Ungespeicherte Änderungen"
  }
}
```

### Translation Key Format

Use dot-notation for hierarchical keys:

```
category.subcategory.key
```

Examples:
- `menu.file` - Menu category, file item
- `panel.explorer.title` - Panel category, explorer panel, title
- `dialog.confirm.delete` - Dialog category, confirm type, delete action

---

## UI Configuration

**File**: `config/ui_config.json`

General UI settings.

```json
{
  "version": "1.0",
  "window": {
    "title": "WidgetSystem Application",
    "default_width": 1280,
    "default_height": 720,
    "min_width": 800,
    "min_height": 600,
    "remember_position": true,
    "remember_size": true,
    "start_maximized": false,
    "frameless": true
  },
  "appearance": {
    "default_theme": "dark",
    "animations_enabled": true,
    "animation_duration": 200,
    "font_family": "Segoe UI",
    "font_size": 10,
    "icon_theme": "material"
  },
  "editor": {
    "font_family": "Consolas",
    "font_size": 12,
    "tab_size": 4,
    "use_spaces": true,
    "word_wrap": false,
    "line_numbers": true,
    "highlight_current_line": true
  },
  "behavior": {
    "auto_save": true,
    "auto_save_interval": 60000,
    "confirm_exit": true,
    "restore_session": true
  }
}
```

---

## Theme Profiles

**Directory**: `config/profiles/`

Pre-defined theme color profiles.

### Dark Profile (`profiles/dark.json`)

```json
{
  "name": "Dark",
  "base": "dark",
  "colors": {
    "window_background": "#1e1e1e",
    "panel_background": "#252526",
    "titlebar_background": "#323233",
    "menu_background": "#2d2d2d",
    "text_primary": "#d4d4d4",
    "text_secondary": "#808080",
    "accent": "#007acc",
    "accent_hover": "#1c97ea",
    "border": "#3c3c3c",
    "divider": "#454545",
    "scrollbar": "#4a4a4a",
    "scrollbar_hover": "#5a5a5a"
  }
}
```

### Transparent Profile (`profiles/transparent.json`)

```json
{
  "name": "Transparent",
  "base": "dark",
  "transparency": true,
  "colors": {
    "window_background": "#c01e1e1e",
    "panel_background": "#b0252526",
    "titlebar_background": "#a0323233"
  }
}
```

---

## JSON Schema Validation

All configuration files are validated against JSON Schemas in the `schemas/` directory.

### Example Schema (`schemas/panels.schema.json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "panels.schema.json",
  "title": "Panel Configuration Schema",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "panels": {
      "type": "object",
      "additionalProperties": {
        "$ref": "#/$defs/panel"
      }
    }
  },
  "required": ["panels"],
  "$defs": {
    "panel": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "icon": {"type": "string"},
        "closable": {"type": "boolean", "default": true},
        "movable": {"type": "boolean", "default": true},
        "floatable": {"type": "boolean", "default": true},
        "default_area": {
          "type": "string",
          "enum": ["left", "right", "top", "bottom", "center"]
        },
        "min_width": {"type": "integer", "minimum": 0},
        "max_width": {"type": "integer", "minimum": 0},
        "min_height": {"type": "integer", "minimum": 0},
        "max_height": {"type": "integer", "minimum": 0}
      },
      "required": ["title"]
    }
  }
}
```

### Validating Configuration

```python
import json
import jsonschema
from pathlib import Path

def validate_config(config_file: Path, schema_file: Path) -> bool:
    """Validate configuration against schema."""
    with open(config_file) as f:
        config = json.load(f)
    with open(schema_file) as f:
        schema = json.load(f)

    try:
        jsonschema.validate(config, schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e.message}")
        return False

# Example usage
validate_config(
    Path("config/panels.json"),
    Path("schemas/panels.schema.json")
)
```

---

## Configuration Best Practices

1. **Version Field**: Always include a `version` field for migration support
2. **Defaults**: Provide sensible defaults in factories, not just config
3. **Comments**: JSON doesn't support comments; use `_comment` fields if needed
4. **Validation**: Validate against schemas before deployment
5. **Backup**: Use BackupManager before making changes
6. **Environment**: Consider different configs for dev/prod
7. **Security**: Never store secrets in configuration files
8. **Unicode**: Use UTF-8 encoding for all JSON files
9. **Formatting**: Use 2-space indentation for readability
10. **Documentation**: Document custom configuration options
