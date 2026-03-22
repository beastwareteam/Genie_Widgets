# WidgetSystem - Visual Architecture

## System Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                           WIDGETSYSTEM v1.0.0                                 ║
║              Configuration-Driven PySide6 GUI Framework                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                        APPLICATION LAYER                                 │ ║
║  │  ┌─────────────┐  ┌─────────────────┐  ┌────────────────────────────┐  │ ║
║  │  │  VisualApp  │  │ VisualMainWindow│  │   ConfigurationPanel       │  │ ║
║  │  │  (Entry)    │──│  (Main Window)  │──│   (Runtime Config)         │  │ ║
║  │  └─────────────┘  └─────────────────┘  └────────────────────────────┘  │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                      │                                        ║
║                                      ▼                                        ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                         UI COMPONENTS (27)                               │ ║
║  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │ ║
║  │  │InlayTitleBar │ │ ThemeEditor  │ │ARGBColorPick │ │WidgetEditor  │   │ ║
║  │  │  3px → 35px  │ │  Live Edit   │ │  #AARRGGBB   │ │  Properties  │   │ ║
║  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │ ║
║  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │ ║
║  │  │FloatingTitle │ │ TabSelector  │ │ TabColor     │ │ FloatingState│   │ ║
║  │  │    Bar       │ │  Monitor     │ │ Controller   │ │   Tracker    │   │ ║
║  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                      │                                        ║
║                                      ▼                                        ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                       FACTORY SYSTEM (10)                                │ ║
║  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                │ ║
║  │  │ Layout │ │ Theme  │ │ Panel  │ │  Menu  │ │  Tabs  │                │ ║
║  │  │Factory │ │Factory │ │Factory │ │Factory │ │Factory │                │ ║
║  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘                │ ║
║  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                │ ║
║  │  │  DnD   │ │Respons.│ │  I18n  │ │  List  │ │UIConfig│                │ ║
║  │  │Factory │ │Factory │ │Factory │ │Factory │ │Factory │                │ ║
║  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘                │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                      │                                        ║
║                                      ▼                                        ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                         CORE SYSTEMS (6)                                 │ ║
║  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                     │ ║
║  │  │PluginSystem  │ │  Undo/Redo   │ │ Config I/O   │                     │ ║
║  │  │ Hot-Reload   │ │  Command     │ │Import/Export │                     │ ║
║  │  │ Registry     │ │  Pattern     │ │   Backup     │                     │ ║
║  │  └──────────────┘ └──────────────┘ └──────────────┘                     │ ║
║  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                     │ ║
║  │  │TemplateSystem│ │ ThemeManager │ │GradientSystem│                     │ ║
║  │  │ 5 Built-in   │ │ ARGB Colors  │ │  Dynamic     │                     │ ║
║  │  │ Templates    │ │   Signals    │ │  Rendering   │                     │ ║
║  │  └──────────────┘ └──────────────┘ └──────────────┘                     │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                      │                                        ║
║                                      ▼                                        ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                      CONFIGURATION (JSON)                                │ ║
║  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │ ║
║  │  │layouts │ │themes  │ │panels  │ │ menus  │ │  tabs  │ │  dnd   │    │ ║
║  │  │ .json  │ │ .json  │ │ .json  │ │ .json  │ │ .json  │ │ .json  │    │ ║
║  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘    │ ║
║  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────────────────────┐  │ ║
║  │  │respons.│ │ i18n.* │ │ lists  │ │        ui_config.json          │  │ ║
║  │  │ .json  │ │ .json  │ │ .json  │ │     (General Settings)         │  │ ║
║  │  └────────┘ └────────┘ └────────┘ └────────────────────────────────┘  │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                      │                                        ║
║                                      ▼                                        ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │                    FOUNDATION (PySide6 + QtAds)                          │ ║
║  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐   │ ║
║  │  │ PySide6.QtCore  │ │PySide6.QtWidgets│ │  PySide6-QtAds          │   │ ║
║  │  │    Signals      │ │    Widgets      │ │  Advanced Docking       │   │ ║
║  │  └─────────────────┘ └─────────────────┘ └─────────────────────────┘   │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Data Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│    JSON      │      │   Factory    │      │   Widget     │      │    User      │
│   Config     │─────▶│    Class     │─────▶│   Instance   │─────▶│ Interaction  │
│   Files      │      │              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
       │                     │                     │                     │
       │                     │                     │                     │
       ▼                     ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│    Schema    │      │   Plugin     │      │   Signal     │      │   Undo/Redo  │
│  Validation  │      │  Registry    │      │  Emissions   │      │   Command    │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

---

## Component Relationships

```
                              ┌─────────────────┐
                              │   ThemeManager  │
                              │    (Signals)    │
                              └────────┬────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
   │  ThemeFactory   │      │   ThemeEditor   │      │  All UI Widgets │
   │  (Load/Save)    │      │  (Live Edit)    │      │  (Apply Style)  │
   └─────────────────┘      └─────────────────┘      └─────────────────┘


                              ┌─────────────────┐
                              │  PluginRegistry │
                              │   (Factories)   │
                              └────────┬────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
   │ PluginManager   │      │ 10 Factories    │      │  Custom Plugins │
   │  (Discovery)    │      │  (Registered)   │      │   (Hot-Reload)  │
   └─────────────────┘      └─────────────────┘      └─────────────────┘


                              ┌─────────────────┐
                              │ UndoRedoManager │
                              │   (Commands)    │
                              └────────┬────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
   │ PropertyChange  │      │  DictChange     │      │  ListChange     │
   │    Command      │      │    Command      │      │    Command      │
   └─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## InlayTitleBar Behavior

```
COLLAPSED STATE (3px)                    EXPANDED STATE (35px)
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│      │  Panel Title          [−][□][×]│
└─────────────────────────────────┘      ├─────────────────────────────────┤
         │                               │                                 │
         │  Mouse Hover                  │       Panel Content             │
         └──────────────────────────────▶│                                 │
                                         │                                 │
                                         └─────────────────────────────────┘

Animation: 150ms ease-in-out
Trigger: Mouse enter/leave
Actions: Minimize, Maximize, Close, Custom
```

---

## ARGB Color System

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ARGB Color Format                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│     #AARRGGBB                                                        │
│      ││││││││                                                        │
│      ││││││└┴── Blue  (00-FF)                                       │
│      ││││└┴──── Green (00-FF)                                       │
│      ││└┴────── Red   (00-FF)                                       │
│      └┴──────── Alpha (00-FF)                                       │
│                                                                      │
│  Examples:                                                           │
│  ┌────────────┬────────────┬─────────────────────────────────────┐  │
│  │   Color    │   Alpha    │            Description              │  │
│  ├────────────┼────────────┼─────────────────────────────────────┤  │
│  │ #FF007ACC  │    100%    │  Fully opaque blue                  │  │
│  │ #C0007ACC  │     75%    │  75% opaque blue                    │  │
│  │ #80007ACC  │     50%    │  50% opaque blue (semi-transparent) │  │
│  │ #40007ACC  │     25%    │  25% opaque blue                    │  │
│  │ #00007ACC  │      0%    │  Fully transparent                  │  │
│  └────────────┴────────────┴─────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Signal Flow

```
┌──────────────┐     themeChanged      ┌──────────────┐
│ ThemeManager │────────────────────▶  │   Widgets    │
└──────────────┘                       └──────────────┘
       │
       │  colorsUpdated
       ▼
┌──────────────┐     undoAvailable     ┌──────────────┐
│UndoRedoMgr   │────────────────────▶  │  UI Buttons  │
└──────────────┘                       └──────────────┘
       │
       │  commandExecuted
       ▼
┌──────────────┐     pluginLoaded      ┌──────────────┐
│PluginRegistry│────────────────────▶  │   Logger     │
└──────────────┘                       └──────────────┘
       │
       │  factoryRegistered
       ▼
┌──────────────┐     exportProgress    ┌──────────────┐
│ConfigExporter│────────────────────▶  │ProgressDialog│
└──────────────┘                       └──────────────┘
```

---

## Directory Structure

```
WidgetSystem/
├── 📁 src/widgetsystem/           # Source Code (41 modules)
│   ├── 📁 core/                   # Core Systems
│   │   ├── plugin_system.py       #   Plugin Registry & Manager
│   │   ├── undo_redo.py           #   Command Pattern
│   │   ├── config_io.py           #   Import/Export
│   │   ├── template_system.py     #   Configuration Templates
│   │   ├── theme_manager.py       #   Theme State Management
│   │   ├── theme_profile.py       #   ARGB Color Profiles
│   │   └── gradient_system.py     #   Dynamic Gradients
│   │
│   ├── 📁 factories/              # Factory Classes (10)
│   │   ├── layout_factory.py      #   Window Layouts
│   │   ├── theme_factory.py       #   Themes & Stylesheets
│   │   ├── panel_factory.py       #   Dock Panels
│   │   ├── menu_factory.py        #   Menu Configurations
│   │   ├── tabs_factory.py        #   Tab Groups
│   │   ├── dnd_factory.py         #   Drag & Drop
│   │   ├── responsive_factory.py  #   Breakpoints
│   │   ├── i18n_factory.py        #   Internationalization
│   │   ├── list_factory.py        #   Nested Lists
│   │   └── ui_config_factory.py   #   General UI Config
│   │
│   └── 📁 ui/                     # UI Components (27)
│       ├── inlay_titlebar.py      #   Collapsible Titlebar
│       ├── floating_titlebar.py   #   Floating Windows
│       ├── theme_editor.py        #   Live Theme Editing
│       ├── argb_color_picker.py   #   Color Selection
│       ├── widget_features_editor.py  # Property Editor
│       ├── config_panel.py        #   Runtime Config
│       └── ...                    #   + 21 more components
│
├── 📁 config/                     # JSON Configuration
│   ├── layouts.json               #   Window Layouts
│   ├── themes.json                #   Theme Definitions
│   ├── panels.json                #   Panel Config
│   ├── menus.json                 #   Menu Structure
│   ├── tabs.json                  #   Tab Groups
│   ├── dnd.json                   #   Drag & Drop
│   ├── responsive.json            #   Breakpoints
│   ├── i18n.en.json               #   English
│   ├── i18n.de.json               #   Deutsch
│   ├── lists.json                 #   List Widgets
│   ├── ui_config.json             #   General Settings
│   └── 📁 profiles/               #   Theme Profiles
│       ├── dark.json
│       ├── light.json
│       └── transparent.json
│
├── 📁 schemas/                    # JSON Schemas (10)
│   ├── layouts.schema.json
│   ├── themes.schema.json
│   ├── panels.schema.json
│   ├── menus.schema.json
│   ├── tabs.schema.json
│   ├── dnd.schema.json
│   ├── responsive.schema.json
│   ├── i18n.schema.json
│   ├── lists.schema.json
│   └── ui_config.schema.json
│
├── 📁 themes/                     # QSS Stylesheets
│   ├── dark.qss
│   ├── light.qss
│   └── transparent.qss
│
├── 📁 tests/                      # Test Suite (49 modules)
│
├── 📁 docs/                       # Documentation
│   ├── README.md                  #   Index
│   ├── QUICK_START.md             #   Getting Started
│   ├── ARCHITECTURE.md            #   System Design
│   ├── API_REFERENCE.md           #   Full API Docs
│   ├── FACTORY_SYSTEM.md          #   Factory Pattern
│   ├── THEME_SYSTEM.md            #   Theming Guide
│   ├── PLUGIN_DEVELOPMENT.md      #   Plugin Guide
│   ├── CONFIGURATION_GUIDE.md     #   JSON Config
│   ├── UI_COMPONENTS.md           #   UI Reference
│   ├── SIGNALS_EVENTS.md          #   Qt Signals
│   └── VISUAL_ARCHITECTURE.md     #   This File
│
└── 📁 examples/                   # Demo Applications
    ├── complete_demo.py
    └── demo_inlay_titlebar.py
```

---

## Statistics

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PROJECT STATISTICS                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Source Modules    │████████████████████████████████████████│  41   │
│  Test Modules      │█████████████████████████████████████████████│49│
│  Factory Classes   │██████████│                              │  10   │
│  UI Components     │███████████████████████████│              │  27   │
│  Core Systems      │██████│                                  │   6   │
│  JSON Configs      │███████████│                             │  11   │
│  JSON Schemas      │██████████│                              │  10   │
│  QSS Themes        │███│                                     │   3   │
│                                                                      │
│  Lines of Code     ~13,800 LOC                                       │
│  Type Coverage     100%                                              │
│  Python Version    3.10+                                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Built-in Templates

```
┌─────────────────────────────────────────────────────────────────────┐
│                      BUILT-IN TEMPLATES                              │
├──────────────────┬──────────────────┬───────────────────────────────┤
│       ID         │      Name        │         Description           │
├──────────────────┼──────────────────┼───────────────────────────────┤
│ builtin_minimal  │ Minimal Layout   │ Single content area           │
│ builtin_developer│ Developer Layout │ Explorer + Editor + Terminal  │
│ builtin_dashboard│ Dashboard Layout │ Multi-panel overview          │
│ builtin_dark     │ Dark Theme       │ Modern dark color scheme      │
│ builtin_light    │ Light Theme      │ Clean light color scheme      │
└──────────────────┴──────────────────┴───────────────────────────────┘
```
