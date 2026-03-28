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

    # Tabs & Navigation - Unified for Dock Tabs AND QTabBar
    tab_active_bg: str = "#cc3c4043"  # 80% opacity
    tab_active_border: str = "#ff8ab4f8"  # Blue border
    tab_active_text: str = "#ff8ab4f8"  # Blue text
    tab_inactive_bg: str = "#cc2d2e31"  # 80% opacity
    tab_inactive_text: str = "#ffbdc1c6"  # Gray text
    tab_hover_text: str = "#ffE0E0E0"  # Light text on hover
    tab_padding: int = 4
    tab_border_radius: int = 4

    # Tab 3D Gradient Colors (for raised/embossed effect)
    # Inactive tab gradient (top to bottom)
    tab_gradient_top: str = "#ff4E5155"  # Highlight at top
    tab_gradient_upper: str = "#ff45484C"  # Upper section
    tab_gradient_lower: str = "#ff36393D"  # Lower section
    tab_gradient_bottom: str = "#ff2E3134"  # Shadow at bottom

    # Active tab gradient (brighter)
    tab_active_gradient_top: str = "#ff5C6066"
    tab_active_gradient_upper: str = "#ff52565B"
    tab_active_gradient_lower: str = "#ff42464A"
    tab_active_gradient_bottom: str = "#ff3A3D41"

    # Hover tab gradient
    tab_hover_gradient_top: str = "#ff5A5E63"
    tab_hover_gradient_upper: str = "#ff505458"
    tab_hover_gradient_lower: str = "#ff404448"
    tab_hover_gradient_bottom: str = "#ff38393D"

    # Tab border colors (3D effect - light top/left, dark right/bottom)
    tab_border_highlight: str = "#ff5A5D62"  # Top border (light)
    tab_border_left: str = "#ff4A4D52"  # Left border
    tab_border_shadow: str = "#ff28292C"  # Right border (dark)
    tab_active_border_highlight: str = "#ff707580"  # Active top
    tab_active_border_left: str = "#ff5C6065"  # Active left
    tab_active_border_shadow: str = "#ff35383C"  # Active right
    tab_hover_border_highlight: str = "#ff686D73"  # Hover top
    tab_hover_border_left: str = "#ff555A5F"  # Hover left
    tab_hover_border_shadow: str = "#ff303235"  # Hover right

    # Tab bar background (darker than tabs for depth)
    tab_bar_bg_top: str = "#ff1E1F21"
    tab_bar_bg_bottom: str = "#ff252628"
    tab_bar_border: str = "#ff151617"

    # Tab dimensions
    tab_min_height: int = 18
    tab_max_height: int = 18
    tab_font_size: int = 11

    # Titlebars & Buttons
    titlebar_bg: str = "#cc2d2e31"  # 80% opacity
    titlebar_text: str = "#ffe8eaed"  # Light gray
    titlebar_btn_hover: str = "#408ab4f8"  # 25% blue overlay

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

    # Tab Drop Indicator (DnD visual feedback)
    tab_drop_insert_color: str = "#ff5294D6"  # Blue insert line
    tab_drop_nest_border_color: str = "#ff5294D6"  # Blue border for nest zone
    tab_drop_nest_fill_color: str = "#205294D6"  # 12% opacity blue fill
    tab_drop_insert_width: int = 3
    tab_drop_nest_border_width: int = 2


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

        def adjusted_qss_color(
            attr_name: str,
            *,
            lighter_factor: int | None = None,
            darker_factor: int | None = None,
            alpha_scale: float = 1.0,
        ) -> str:
            """Return a transformed theme color for subtle depth effects."""
            color_value = getattr(c, attr_name)
            if not isinstance(color_value, str):
                return str(color_value)

            color = QColor(self.apply_global_transforms(color_value))
            if lighter_factor is not None:
                color = color.lighter(lighter_factor)
            if darker_factor is not None:
                color = color.darker(darker_factor)

            scaled_alpha = max(0, min(255, round(color.alpha() * alpha_scale)))
            color.setAlpha(scaled_alpha)
            rgba_tuple: tuple[int, int, int, int] = color.getRgb()  # type: ignore[assignment]
            red, green, blue, alpha = rgba_tuple
            return f"rgba({red}, {green}, {blue}, {alpha})"

        splitter_width = max(1, c.splitter_width)
        horizontal_bar_height = max(1, splitter_width - 1)

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
    background: {adjusted_qss_color("splitter_handle", alpha_scale=0.92)};
    width: {splitter_width}px;
    height: {splitter_width}px;
    margin: 0px;
    padding: 0px;
    border: none;
}}

ads--CDockSplitter::handle:horizontal {{
    width: {splitter_width}px;
    background: qlineargradient(
        x1:0,
        y1:0,
        x2:1,
        y2:0,
        stop:0 {adjusted_qss_color("splitter_handle", lighter_factor=142, alpha_scale=0.98)},
        stop:0.38 {adjusted_qss_color("splitter_handle", lighter_factor=112, alpha_scale=0.94)},
        stop:1 {adjusted_qss_color("splitter_handle", darker_factor=155, alpha_scale=0.98)}
    );
}}

ads--CDockSplitter::handle:vertical {{
    height: {horizontal_bar_height}px;
    background: qlineargradient(
        x1:0,
        y1:0,
        x2:0,
        y2:1,
        stop:0 {adjusted_qss_color("splitter_handle", lighter_factor=145, alpha_scale=0.98)},
        stop:0.34 {adjusted_qss_color("splitter_handle", lighter_factor=114, alpha_scale=0.94)},
        stop:1 {adjusted_qss_color("splitter_handle", darker_factor=165, alpha_scale=0.98)}
    );
}}

ads--CDockSplitter::handle:hover {{
    background: qlineargradient(
        x1:0,
        y1:0,
        x2:1,
        y2:1,
        stop:0 {adjusted_qss_color("tab_active_border", lighter_factor=115, alpha_scale=0.72)},
        stop:1 {adjusted_qss_color("splitter_handle", darker_factor=140, alpha_scale=0.92)}
    );
}}

ads--CDockSplitter {{
    margin: 0px;
    padding: 0px;
}}

/* 4. Unified Tab Styling - Dock Tabs AND QTabBar use identical colors */

/* ---- Title Bar Background (container for tabs) ---- */
ads--CDockAreaTitleBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_bar_bg_top")},
                                stop:1 {qss_color("tab_bar_bg_bottom")});
    border: none;
    border-top: 1px solid {qss_color("tab_bar_border")};
    padding: 0px;
    margin: 0px;
    min-height: 26px;
    max-height: 26px;
}}

/* ---- Dock Widget Tabs (QtAds) ---- */
ads--CDockWidgetTab {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_gradient_top")},
                                stop:0.05 {qss_color("tab_gradient_upper")},
                                stop:0.95 {qss_color("tab_gradient_lower")},
                                stop:1 {qss_color("tab_gradient_bottom")});
    color: {qss_color("tab_inactive_text")};
    padding: 3px 10px;
    margin: 3px 3px 0px 0px;
    border-top: 1px solid {qss_color("tab_border_highlight")};
    border-left: 1px solid {qss_color("tab_border_left")};
    border-right: 1px solid {qss_color("tab_border_shadow")};
    border-bottom: none;
    border-top-left-radius: {c.tab_border_radius}px;
    border-top-right-radius: {c.tab_border_radius}px;
    min-height: {c.tab_min_height}px;
    max-height: {c.tab_max_height}px;
}}

ads--CDockWidgetTab:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_hover_gradient_top")},
                                stop:0.05 {qss_color("tab_hover_gradient_upper")},
                                stop:0.95 {qss_color("tab_hover_gradient_lower")},
                                stop:1 {qss_color("tab_hover_gradient_bottom")});
    color: {qss_color("tab_hover_text")};
    border-top: 1px solid {qss_color("tab_hover_border_highlight")};
    border-left: 1px solid {qss_color("tab_hover_border_left")};
    border-right: 1px solid {qss_color("tab_hover_border_shadow")};
}}

ads--CDockWidgetTab[activeTab="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_active_gradient_top")},
                                stop:0.05 {qss_color("tab_active_gradient_upper")},
                                stop:0.95 {qss_color("tab_active_gradient_lower")},
                                stop:1 {qss_color("tab_active_gradient_bottom")});
    color: {qss_color("tab_active_text")};
    border-top: 1px solid {qss_color("tab_active_border_highlight")};
    border-left: 1px solid {qss_color("tab_active_border_left")};
    border-right: 1px solid {qss_color("tab_active_border_shadow")};
    border-bottom: 2px solid {qss_color("tab_active_border")};
    font-weight: normal;
}}

/* ---- QTabBar (Nested/Sub Tabs) - Identical styling ---- */
QTabBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_bar_bg_top")},
                                stop:1 {qss_color("tab_bar_bg_bottom")});
    color: {qss_color("tab_inactive_text")};
    border: none;
    border-top: 1px solid {qss_color("tab_bar_border")};
    min-height: 26px;
    max-height: 26px;
}}

QTabBar::tab {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_gradient_top")},
                                stop:0.05 {qss_color("tab_gradient_upper")},
                                stop:0.95 {qss_color("tab_gradient_lower")},
                                stop:1 {qss_color("tab_gradient_bottom")});
    color: {qss_color("tab_inactive_text")};
    padding: 3px 8px 3px 10px;
    margin: 3px 3px 0px 0px;
    border-top: 1px solid {qss_color("tab_border_highlight")};
    border-left: 1px solid {qss_color("tab_border_left")};
    border-right: 1px solid {qss_color("tab_border_shadow")};
    border-bottom: none;
    border-top-left-radius: {c.tab_border_radius}px;
    border-top-right-radius: {c.tab_border_radius}px;
    min-width: 50px;
    min-height: {c.tab_min_height}px;
    max-height: {c.tab_max_height}px;
    font-size: {c.tab_font_size}px;
}}

QTabBar::tab:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_hover_gradient_top")},
                                stop:0.05 {qss_color("tab_hover_gradient_upper")},
                                stop:0.95 {qss_color("tab_hover_gradient_lower")},
                                stop:1 {qss_color("tab_hover_gradient_bottom")});
    color: {qss_color("tab_hover_text")};
    border-top: 1px solid {qss_color("tab_hover_border_highlight")};
    border-left: 1px solid {qss_color("tab_hover_border_left")};
    border-right: 1px solid {qss_color("tab_hover_border_shadow")};
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {qss_color("tab_active_gradient_top")},
                                stop:0.05 {qss_color("tab_active_gradient_upper")},
                                stop:0.95 {qss_color("tab_active_gradient_lower")},
                                stop:1 {qss_color("tab_active_gradient_bottom")});
    color: {qss_color("tab_active_text")};
    border-top: 1px solid {qss_color("tab_active_border_highlight")};
    border-left: 1px solid {qss_color("tab_active_border_left")};
    border-right: 1px solid {qss_color("tab_active_border_shadow")};
    border-bottom: 2px solid {qss_color("tab_active_border")};
    font-weight: normal;
}}

/* 5. Title Bar Buttons */
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
    background: {self.as_qss_color("#60ffffff")};
}}

#dockAreaCloseButton, #detachGroupButton, #tabCloseButton, #dockAreaAutoHideButton {{
    background: {qss_color("btn_bg")};
    border-radius: 2px;
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
    background: {qss_color("titlebar_bg")};
    border: none;
    spacing: 3px;
    padding: 3px;
}}

QMenuBar {{
    background: {qss_color("titlebar_bg")};
    color: {qss_color("titlebar_text")};
}}

QMenu {{
    background: {qss_color("titlebar_bg")};
    color: {qss_color("titlebar_text")};
    border: 1px solid {qss_color("splitter_handle")};
}}

QMenu::item:selected {{
    background: {qss_color("tab_active_bg")};
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
