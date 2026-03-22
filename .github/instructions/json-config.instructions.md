---
description: Guidelines for JSON configuration files in WidgetSystem
applyTo: |
  **/config/**/*.json
  **/schemas/**/*.json
---

# JSON Configuration Guidelines

## Configuration Structure

All configuration files in `config/` directory follow consistent patterns.

## File Naming

- **Lowercase with underscores**: `ui_config.json`, `menus.json`
- **Descriptive**: Name should indicate content
- **Consistent**: Use same naming pattern across project

## Common Structure

Most configuration files follow this pattern:

```json
{
  "default_[type]_id": "default_value",
  "[type]s": [
    {
      "id": "unique_identifier",
      "name": "Display Name",
      "properties": {
        "key": "value"
      }
    }
  ]
}
```

## File Paths

**Always use relative paths from workspace root:**

```json
{
  "file": "data/layout.xml",
  "stylesheet": "themes/dark.qss",
  "icon": "icons/app.png"
}
```

**Never use:**
- Absolute paths: `"C:\\Users\\..."`
- Ambiguous paths: `"layout.xml"` (where is it?)
- URLs: `"file:///path"` (use local paths)

## Required Fields

Every configuration item should have:

```json
{
  "id": "unique_id",           // Required: Unique identifier
  "name": "Display Name",      // Required: Human-readable name
  "description": "Optional",   // Optional: Detailed description
  "enabled": true              // Optional: Enable/disable flag
}
```

## Layout Configuration

`config/layouts.json`:

```json
{
  "default_layout_id": "last_saved",
  "layouts": [
    {
      "id": "last_saved",
      "name": "Last Saved",
      "file": "data/layout.xml",
      "description": "Last saved window layout"
    }
  ]
}
```

## Theme Configuration

`config/themes.json`:

```json
{
  "default_theme_id": "light",
  "themes": [
    {
      "id": "light",
      "name": "Light Theme",
      "file": "themes/light.qss",
      "description": "Light color scheme"
    }
  ]
}
```

## Menu Configuration

`config/menus.json`:

```json
{
  "menus": [
    {
      "id": "file_menu",
      "name": "File",
      "items": [
        {
          "id": "new",
          "name": "New",
          "icon": "icons/new.png",
          "shortcut": "Ctrl+N",
          "action": "file_new"
        }
      ]
    }
  ]
}
```

## Panel Configuration

`config/panels.json`:

```json
{
  "panels": [
    {
      "id": "properties",
      "name": "Properties",
      "type": "properties",
      "position": "right",
      "min_width": 200,
      "max_width": 400
    }
  ]
}
```

## List Configuration

`config/lists.json`:

```json
{
  "list_groups": [
    {
      "id": "project_files",
      "name": "Project Files",
      "items": [
        {
          "id": "main_py",
          "name": "main.py",
          "icon": "icons/python.png",
          "metadata": {
            "type": "file",
            "path": "src/main.py"
          }
        }
      ]
    }
  ]
}
```

## Internationalization

`config/i18n.en.json`:

```json
{
  "app": {
    "title": "WidgetSystem",
    "version": "1.0.0"
  },
  "menu": {
    "file": "File",
    "edit": "Edit"
  },
  "messages": {
    "welcome": "Welcome to WidgetSystem"
  }
}
```

## Schema Validation

Every configuration file should have a corresponding schema in `schemas/`:

`schemas/layouts.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["layouts"],
  "properties": {
    "default_layout_id": {
      "type": "string"
    },
    "layouts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "file"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "file": {"type": "string"},
          "description": {"type": "string"}
        }
      }
    }
  }
}
```

## Data Types

Use appropriate JSON types:

```json
{
  "string_value": "text",
  "number_value": 42,
  "float_value": 3.14,
  "boolean_value": true,
  "null_value": null,
  "array_value": [1, 2, 3],
  "object_value": {
    "nested": "value"
  }
}
```

## Formatting

- **Indentation**: 2 spaces
- **Line endings**: LF (Unix-style)
- **Encoding**: UTF-8
- **Final newline**: Yes

Example:
```json
{
  "items": [
    {
      "id": "first",
      "name": "First Item"
    },
    {
      "id": "second",
      "name": "Second Item"
    }
  ]
}
```

## Comments

JSON doesn't support comments. Use:

1. **Description fields** for documentation:
```json
{
  "id": "complex_item",
  "description": "This item configures the main layout panel"
}
```

2. **Separate documentation** in `docs/CONFIG.md`

## Boolean Values

Use lowercase `true`/`false`:

```json
{
  "enabled": true,
  "visible": false
}
```

Not: `"enabled": "true"` (string) or `"enabled": True` (Python)

## Null Values

Use `null` for missing/optional values:

```json
{
  "optional_value": null,
  "required_value": "something"
}
```

## Arrays

Use arrays for lists of items:

```json
{
  "tags": ["python", "gui", "pyside6"],
  "items": [
    {"id": "1"},
    {"id": "2"}
  ]
}
```

## Nested Objects

Use nested objects for complex structures:

```json
{
  "window": {
    "size": {
      "width": 800,
      "height": 600
    },
    "position": {
      "x": 100,
      "y": 100
    }
  }
}
```

## Common Mistakes to Avoid

1. ❌ Trailing commas: `[1, 2, 3,]` (invalid JSON)
2. ❌ Single quotes: `{'key': 'value'}` (use double quotes)
3. ❌ Comments: `// comment` (not allowed in JSON)
4. ❌ Unquoted keys: `{key: "value"}` (keys must be quoted)
5. ❌ Absolute paths: `"C:\\path"` (use relative)
6. ❌ Mixed case booleans: `True`, `FALSE` (use lowercase)
7. ❌ Missing commas between items

## Validation

Validate JSON before committing:

```bash
# Using Python
python -m json.tool config/layouts.json

# Using jq
jq . config/layouts.json
```

## Loading in Python

Factories should load JSON like this:

```python
import json
from pathlib import Path

config_file = Path("config/layouts.json")
config_data = json.loads(
    config_file.read_text(encoding="utf-8")
)
```

## Versioning

Include version in configuration when needed:

```json
{
  "version": "1.0",
  "schema_version": "2.0",
  "items": []
}
```

## Example: Complete Configuration

```json
{
  "version": "1.0",
  "default_theme_id": "dark",
  "themes": [
    {
      "id": "dark",
      "name": "Dark Theme",
      "file": "themes/dark.qss",
      "description": "Dark color scheme for better readability",
      "enabled": true,
      "metadata": {
        "author": "WidgetSystem Team",
        "created": "2026-01-01"
      }
    },
    {
      "id": "light",
      "name": "Light Theme",
      "file": "themes/light.qss",
      "description": "Light color scheme",
      "enabled": true,
      "metadata": {
        "author": "WidgetSystem Team",
        "created": "2026-01-01"
      }
    }
  ]
}
```

## Reference Examples

See existing configuration files:
- `config/layouts.json` - Layout configuration
- `config/themes.json` - Theme configuration
- `config/menus.json` - Menu configuration
- `config/panels.json` - Panel configuration
- `schemas/*.schema.json` - JSON schemas
