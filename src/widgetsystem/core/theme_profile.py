"""Theme Profile - categorized ARGB colors with global transformations."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from PySide6.QtGui import QColor


@dataclass
class ThemeColors:
    """Categorized theme colors with ARGB hex format support.

    ARGB Format: #AARRGGBB where AA is alpha channel (00=transparent, FF=opaque)
    Example: #cc3c4043 = 80% opacity, RGB(60, 64, 67)
    """

    # Core & Main Window
    window_bg: str = "#00202124"  # Fully transparent
    splitter_handle: str = "#ff3c4043"  # Solid gray
    splitter_width: int = 2

    # Tabs & Navigation
    tab_active_bg: str = "#cc3c4043"  # 80% opacity
    tab_active_border: str = "#ff8ab4f8"  # Blue border
    tab_active_text: str = "#ff8ab4f8"  # Blue text
    tab_inactive_bg: str = "#cc2d2e31"  # 80% opacity
    tab_inactive_text: str = "#ffbdc1c6"  # Gray text
    tab_hover_bg: str = "#40ffffff"  # Hover overlay
    tab_padding: int = 4
    tab_border_radius: int = 0

    # Titlebars & Buttons
    titlebar_bg: str = "#cc2d2e31"  # 80% opacity
    titlebar_text: str = "#ffe8eaed"  # Light gray
    titlebar_btn_hover: str = "#408ab4f8"  # 25% blue overlay
    titlebar_btn_pressed: str = "#60ffffff"  # Pressed state

    # Window Management / Decorations
    btn_bg: str = "#40ffffff"  # 25% opacity white
    btn_icon: str = "#ffe8eaed"  # Light gray
    floating_border: str = "#ff3c4043"  # Solid gray

    # Auto-Hide (Sidebars)
    autohide_sidebar_bg: str = "#cc202124"  # 80% opacity
    autohide_tab_bg: str = "#cc2d2e31"  # 80% opacity
    autohide_container_bg: str = "#cc202124"  # 80% opacity
    autohide_container_border: str = "#ff8ab4f8"  # Blue border

    # Overlays (Drag & Drop)
    overlay_base_color: str = "#808ab4f8"  # 50% opacity blue
    overlay_cross_color: str = "#ff8ab4f8"  # Solid blue
    overlay_border_color: str = "#ff8ab4f8"  # Solid blue
    overlay_border_width: int = 2

    # Toolbar
    toolbar_bg: str = "#cc2d2e31"  # Same as titlebar
    toolbar_separator: str = "#ff4c4c4c"  # Separator color
    toolbar_button_bg: str = "#00000000"  # Transparent
    toolbar_button_hover: str = "#40ffffff"  # Hover overlay
    toolbar_button_pressed: str = "#60ffffff"  # Pressed state

    # Push Buttons
    pushbutton_bg: str = "#ff3c4043"  # Button background
    pushbutton_text: str = "#ffe8eaed"  # Button text
    pushbutton_border: str = "#ff5c5c5c"  # Button border
    pushbutton_hover_bg: str = "#ff4c5054"  # Hover background
    pushbutton_pressed_bg: str = "#ff5c6064"  # Pressed background

    # Input Widgets
    input_bg: str = "#ff2d2e31"  # Input background
    input_text: str = "#ffe8eaed"  # Input text
    input_border: str = "#ff3c4043"  # Input border
    input_focus_border: str = "#ff8ab4f8"  # Focus border
    input_selection_bg: str = "#ff1565c0"  # Selection background
    input_selection_text: str = "#ffffffff"  # Selection text

    # Dropdown/ComboBox
    combobox_bg: str = "#ff2d2e31"  # ComboBox background
    combobox_text: str = "#ffe8eaed"  # ComboBox text
    combobox_border: str = "#ff3c4043"  # ComboBox border
    combobox_dropdown_bg: str = "#ff3c4043"  # Dropdown background

    # ScrollBar
    scrollbar_bg: str = "#ff1a1a1a"  # ScrollBar background
    scrollbar_handle: str = "#ff4c4c4c"  # ScrollBar handle
    scrollbar_handle_hover: str = "#ff8ab4f8"  # Handle hover

    # Menu
    menu_bg: str = "#ff2d2e31"  # Menu background
    menu_text: str = "#ffe8eaed"  # Menu text
    menu_border: str = "#ff3c4043"  # Menu border
    menu_item_selected_bg: str = "#cc3c4043"  # Selected item background
    menu_item_selected_text: str = "#ff8ab4f8"  # Selected item text


class ThemeProfile:
    """Theme profile with ARGB colors and global color transformations.

    Supports:
    - ARGB hex colors with alpha channel
    - Global hue/saturation/brightness adjustments
    - QSS generation from profile
    - JSON import/export
    """

    def __init__(self, name: str = "Custom Profile") -> None:
        """Initialize theme profile.

        Args:
            name: Display name for profile
        """
        self.name = name
        self.colors = ThemeColors()
        self.global_hue: int = 0  # 0-360 degrees
        self.global_saturation: float = 1.0  # 0.0-2.0 multiplier
        self.global_brightness: float = 1.0  # 0.0-2.0 multiplier

    def as_qss_color(self, color_hex: str) -> str:
        """Convert ARGB hex to rgba(r, g, b, a) for QSS compatibility.

        Args:
            color_hex: ARGB hex color (e.g., "#cc3c4043")

        Returns:
            QSS rgba string (e.g., "rgba(60, 64, 67, 204)")
        """
        transformed = self.apply_global_transforms(color_hex)
        color = QColor(transformed)
        rgba_tuple: tuple[int, int, int, int] = color.getRgb()  # type: ignore[assignment]
        r, g, b, a = rgba_tuple
        return f"rgba({r}, {g}, {b}, {a})"

    def apply_global_transforms(self, color_hex: str) -> str:
        """Apply global hue, saturation, brightness shifts to color.

        Args:
            color_hex: ARGB hex color

        Returns:
            Transformed ARGB hex color
        """
        # Short-circuit: if all transforms are neutral, return original color
        # This prevents color drift from HSV conversion roundtrip
        if self.global_hue == 0 and self.global_saturation == 1.0 and self.global_brightness == 1.0:
            return color_hex
        
        color = QColor(color_hex)
        hsva_tuple: tuple[float, float, float, float] = color.getHsvF()  # type: ignore[assignment]
        h, s, v, a = hsva_tuple

        # Apply transforms
        h = (h + self.global_hue / 360.0) % 1.0
        s = max(0.0, min(1.0, s * self.global_saturation))
        v = max(0.0, min(1.0, v * self.global_brightness))

        new_color = QColor.fromHsvF(h, s, v, a)
        return new_color.name(QColor.NameFormat.HexArgb)

    def generate_qss(self) -> str:
        """Generate complete QSS stylesheet from profile colors.

        Returns:
            QSS stylesheet string
        """
        c = self.colors

        # Helper function for color conversion
        def qss_color(attr_name: str) -> str:
            color_value = getattr(c, attr_name)
            if isinstance(color_value, str):
                return self.as_qss_color(color_value)
            return str(color_value)

        return f"""
/* ============================================================================
   {self.name} - Generated Theme Profile
   ============================================================================ */

/* 1. Core & Main Window */
QMainWindow {{
    background: {qss_color("window_bg")};
    color: {qss_color("titlebar_text")};
}}

QWidget {{
    background: {qss_color("window_bg")};
    color: {qss_color("titlebar_text")};
}}

/* 2. Dock System Core */
ads--CDockManager {{
    background: {qss_color("window_bg")};
}}

ads--CDockContainerWidget {{
    background: {qss_color("window_bg")};
}}

ads--CDockWidget {{
    background: {qss_color("window_bg")};
    border: 1px solid {qss_color("splitter_handle")};
}}

ads--CDockAreaWidget {{
    background: {qss_color("window_bg")};
    border: 1px solid {qss_color("splitter_handle")};
}}

/* 3. Splitters */
ads--CDockSplitter::handle {{
    background: {qss_color("splitter_handle")};
    width: {c.splitter_width}px;
    height: {c.splitter_width}px;
    margin: 0px;
    padding: 0px;
    border: none;
}}

ads--CDockSplitter {{
    margin: 0px;
    padding: 0px;
}}

/* 4. Tabs */
ads--CDockWidgetTab {{
    background: {qss_color("tab_inactive_bg")};
    color: {qss_color("tab_inactive_text")};
    padding: {c.tab_padding}px;
    border: 1px solid {qss_color("splitter_handle")};
    border-bottom: none;
    border-radius: {c.tab_border_radius}px {c.tab_border_radius}px 0 0;
    margin-right: 2px;
}}

ads--CDockWidgetTab[activeTab="true"] {{
    background: {qss_color("tab_active_bg")};
    color: {qss_color("tab_active_text")};
    border-bottom: 2px solid {qss_color("tab_active_border")};
    font-weight: bold;
}}

ads--CDockWidgetTab:hover {{
    background: {qss_color("tab_hover_bg")};
}}

/* Ensure tab close button sits 4px from the right edge of the tab */
ads--CDockWidgetTab > QAbstractButton#tabCloseButton {{
    background: transparent;
    border: none;
    border-radius: 3px;
    margin: 0px 4px 0px 0px;
    padding: 1px;
    min-width: 14px;
    min-height: 14px;
    max-width: 14px;
    max-height: 14px;
    subcontrol-origin: padding;
    subcontrol-position: right;
}}

QTabBar {{
    background: {qss_color("window_bg")};
}}

QTabBar::tab {{
    background: {qss_color("tab_inactive_bg")};
    color: {qss_color("tab_inactive_text")};
    padding: 6px 16px;
    margin: 2px 2px 0px 0px;
    border: 1px solid {qss_color("splitter_handle")};
    border-bottom: none;
}}

QTabBar::tab:selected {{
    background: {qss_color("tab_active_bg")};
    color: {qss_color("tab_active_text")};
    border-bottom: 2px solid {qss_color("tab_active_border")};
    font-weight: bold;
}}

QTabBar::tab:hover {{
    background: {qss_color("tab_hover_bg")};
}}

/* 5. Titlebars */
ads--CDockAreaTitleBar {{
    background: {qss_color("titlebar_bg")};
    border-bottom: 1px solid {qss_color("splitter_handle")};
    padding: 0px 4px;
    margin: 0px;
}}

ads--CDockAreaTitleBar ads--CTitleBarButton {{
    padding: 4px 8px;
    margin: 0px;
    border-radius: 2px;
}}

/* 6. Buttons */
ads--CTitleBarButton {{
    background: {qss_color("btn_bg")};
    color: {qss_color("btn_icon")};
    border: none;
    padding: 2px;
    border-radius: 2px;
}}

ads--CTitleBarButton:hover {{
    background: {qss_color("titlebar_btn_hover")};
}}

ads--CTitleBarButton:pressed {{
    background: {qss_color("titlebar_btn_pressed")};
}}

#dockAreaCloseButton, #detachGroupButton, #tabCloseButton, #dockAreaAutoHideButton {{
    background: {qss_color("btn_bg")};
    border-radius: 2px;
    subcontrol-position: right;
}}

#dockAreaCloseButton:hover, #detachGroupButton:hover, 
#tabCloseButton:hover, #dockAreaAutoHideButton:hover {{
    background: {qss_color("titlebar_btn_hover")};
}}

/* 7. Floating Containers */
ads--CFloatingDockContainer {{
    background: {qss_color("window_bg")};
    border: 1px solid {qss_color("floating_border")};
}}

/* 8. Auto-Hide Elements */
ads--CAutoHideSideBar {{
    background: {qss_color("autohide_sidebar_bg")};
    border: 1px solid {qss_color("splitter_handle")};
}}

ads--CAutoHideTab {{
    background: {qss_color("autohide_tab_bg")};
    color: {qss_color("tab_inactive_text")};
    padding: 4px;
    margin: 2px;
}}

ads--CAutoHideTab[activeTab="true"] {{
    background: {qss_color("tab_active_bg")};
    color: {qss_color("tab_active_text")};
}}

ads--CAutoHideDockContainer {{
    background: {qss_color("autohide_container_bg")};
    border: 1px solid {qss_color("autohide_container_border")};
}}

/* 9. Overlays (Drag & Drop) */
ads--CDockOverlay {{
    background-color: {qss_color("overlay_base_color")};
    border: {c.overlay_border_width}px solid {qss_color("overlay_border_color")};
}}

ads--CDockOverlayCross {{
    color: {qss_color("overlay_cross_color")};
}}

/* 10. Content Widget Transparency */
QScrollArea#dockWidgetScrollArea {{
    background: transparent;
    border: none;
}}

QPlainTextEdit, QTreeView, QTableWidget, QListWidget {{
    background: transparent;
    color: {qss_color("titlebar_text")};
    border: none;
}}

/* 11. General Widgets */
QTabWidget {{
    background: {qss_color("window_bg")};
}}

QTabWidget::pane {{
    background: {qss_color("window_bg")};
    border: 1px solid {qss_color("splitter_handle")};
}}

QToolBar {{
    background: {qss_color("toolbar_bg")};
    border: none;
    spacing: 4px;
    padding: 3px;
}}

QToolBar::separator {{
    background: {qss_color("toolbar_separator")};
    width: 2px;
    margin: 0px 4px;
}}

QToolButton {{
    background: {qss_color("toolbar_button_bg")};
    color: {qss_color("titlebar_text")};
    border: 1px solid transparent;
    padding: 4px 8px;
    border-radius: 2px;
}}

QToolButton:hover {{
    background: {qss_color("toolbar_button_hover")};
    border: 1px solid {qss_color("splitter_handle")};
}}

QToolButton:pressed,
QToolButton:checked {{
    background: {qss_color("toolbar_button_pressed")};
    border: 1px solid {qss_color("splitter_handle")};
}}

QPushButton {{
    background: {qss_color("pushbutton_bg")};
    color: {qss_color("pushbutton_text")};
    border: 1px solid {qss_color("pushbutton_border")};
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background: {qss_color("pushbutton_hover_bg")};
}}

QPushButton:pressed {{
    background: {qss_color("pushbutton_pressed_bg")};
}}

QLineEdit,
QTextEdit,
QPlainTextEdit {{
    background: {qss_color("input_bg")};
    color: {qss_color("input_text")};
    border: 1px solid {qss_color("input_border")};
    border-radius: 2px;
    padding: 4px 6px;
    selection-background-color: {qss_color("input_selection_bg")};
    selection-color: {qss_color("input_selection_text")};
}}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus {{
    border: 2px solid {qss_color("input_focus_border")};
}}

QComboBox {{
    background: {qss_color("combobox_bg")};
    color: {qss_color("combobox_text")};
    border: 1px solid {qss_color("combobox_border")};
    border-radius: 2px;
    padding: 4px 6px;
}}

QComboBox::drop-down {{
    background: {qss_color("combobox_dropdown_bg")};
    border: none;
}}

QScrollBar:vertical {{
    background: {qss_color("scrollbar_bg")};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background: {qss_color("scrollbar_handle")};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {qss_color("scrollbar_handle_hover")};
}}

QScrollBar:horizontal {{
    background: {qss_color("scrollbar_bg")};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background: {qss_color("scrollbar_handle")};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {qss_color("scrollbar_handle_hover")};
}}

QMenuBar {{
    background: {qss_color("menu_bg")};
    color: {qss_color("menu_text")};
}}

QMenu {{
    background: {qss_color("menu_bg")};
    color: {qss_color("menu_text")};
    border: 1px solid {qss_color("menu_border")};
}}

QMenu::item:selected {{
    background: {qss_color("menu_item_selected_bg")};
    color: {qss_color("menu_item_selected_text")};
}}
"""

    def to_json(self) -> str:
        """Export profile to JSON string.

        Returns:
            JSON representation of profile
        """
        data: dict[str, str | dict[str, int | float] | dict[str, int | str]] = {
            "name": self.name,
            "colors": asdict(self.colors),
            "global": {
                "hue": self.global_hue,
                "saturation": self.global_saturation,
                "brightness": self.global_brightness,
            },
        }
        return json.dumps(data, indent=2)

    def save_to_file(self, file_path: Path) -> None:
        """Save profile to JSON file.

        Args:
            file_path: Path to save JSON file
        """
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_json(cls, json_str: str) -> "ThemeProfile":
        """Import profile from JSON string.

        Args:
            json_str: JSON string to parse

        Returns:
            ThemeProfile instance
        """
        data = json.loads(json_str)
        profile = cls(data.get("name", "Imported Profile"))

        # Load colors
        colors_data = data.get("colors", {})
        for key, value in colors_data.items():
            if hasattr(profile.colors, key):
                setattr(profile.colors, key, value)

        # Load global transforms
        glob = data.get("global", {})
        profile.global_hue = glob.get("hue", 0)
        profile.global_saturation = glob.get("saturation", 1.0)
        profile.global_brightness = glob.get("brightness", 1.0)

        return profile

    @classmethod
    def load_from_file(cls, file_path: Path) -> "ThemeProfile":
        """Load profile from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            ThemeProfile instance
        """
        with open(file_path, encoding="utf-8") as f:
            return cls.from_json(f.read())

    @classmethod
    def load_from_json_file(cls, file_path: Path) -> "ThemeProfile":
        """Alias for load_from_file for factory compatibility.

        Args:
            file_path: Path to JSON file

        Returns:
            ThemeProfile instance
        """
        return cls.load_from_file(file_path)

    def save_to_json_file(self, file_path: Path) -> None:
        """Alias for save_to_file for factory compatibility.

        Args:
            file_path: Path to save JSON file
        """
        self.save_to_file(file_path)
