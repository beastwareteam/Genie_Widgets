"""Tab drop indicator for visual DnD feedback.

Provides overlay widgets showing drop zones during tab drag operations:
- Insert line (vertical) for BEFORE/AFTER zones
- Border highlight for INTO zone (nesting)
"""

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon
from PySide6.QtWidgets import QWidget


class TabDropIndicator(QWidget):
    """Visual indicator for tab drop zones.

    Shows different visuals based on drop zone type:
    - BEFORE/AFTER: Vertical insert line
    - INTO: Border highlight around target tab
    """

    # Default colors (can be overridden via set_colors)
    DEFAULT_INSERT_COLOR = "#5294D6"  # Blue line for insert
    DEFAULT_NEST_COLOR = "#5294D6"  # Blue border for nest
    # Note: For alpha, use setAlpha() after QColor creation
    DEFAULT_NEST_FILL_ALPHA = 32  # ~12% opacity (0-255)

    # Visual parameters
    INSERT_LINE_WIDTH = 2
    NEST_BORDER_WIDTH = 1


    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize TabDropIndicator."""
        super().__init__(parent)

        # Make transparent overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Current state
        self._zone_type: str = "none"  # "none", "insert", "nest"
        self._highlight_rect: QRect | None = None

        # Colors (created once, reused)
        self._insert_color = QColor(self.DEFAULT_INSERT_COLOR)
        self._nest_border_color = QColor(self.DEFAULT_NEST_COLOR)
        self._nest_fill_color = QColor(self.DEFAULT_NEST_COLOR)
        self._nest_fill_color.setAlpha(self.DEFAULT_NEST_FILL_ALPHA)

        # Pre-allocate drawing objects (avoid per-frame allocations)
        self._pen: QPen = QPen()
        self._top_triangle: QPolygon = QPolygon()
        self._bottom_triangle: QPolygon = QPolygon()

        self.hide()

    def set_colors(
        self,
        insert_color: str | None = None,
        nest_border_color: str | None = None,
        nest_fill_color: str | None = None,
    ) -> None:
        """Set indicator colors.

        Args:
            insert_color: Color for insert line (hex string)
            nest_border_color: Color for nest border (hex string)
            nest_fill_color: Color for nest fill (hex string with alpha)
        """
        if insert_color:
            self._insert_color = QColor(insert_color)
        if nest_border_color:
            self._nest_border_color = QColor(nest_border_color)
        if nest_fill_color:
            # Parse ARGB hex (#AARRGGBB) or RGB hex (#RRGGBB)
            color = QColor(nest_fill_color)
            if len(nest_fill_color) == 9 and nest_fill_color.startswith("#"):
                # 8-digit hex: #AARRGGBB format
                alpha = int(nest_fill_color[1:3], 16)
                color = QColor(f"#{nest_fill_color[3:]}")
                color.setAlpha(alpha)
            self._nest_fill_color = color
        self.update()

    def show_insert_indicator(self, global_rect: QRect) -> None:
        """Show vertical insert line at specified position.

        Args:
            global_rect: Rectangle in global coordinates (narrow vertical line)
        """
        # Skip if already showing same indicator at same position
        if self._zone_type == "insert" and self._highlight_rect == global_rect and self.isVisible():
            return

        self._zone_type = "insert"
        self._highlight_rect = global_rect

        # Position and size the widget
        self.setGeometry(global_rect)
        if not self.isVisible():
            self.show()
            self.raise_()
        self.update()

    def show_nest_indicator(self, global_rect: QRect) -> None:
        """Show border highlight for nest zone.

        Args:
            global_rect: Rectangle in global coordinates (tab bounds)
        """
        # Skip if already showing same indicator at same position
        if self._zone_type == "nest" and self._highlight_rect == global_rect and self.isVisible():
            return

        self._zone_type = "nest"
        self._highlight_rect = global_rect

        # Position and size the widget
        self.setGeometry(global_rect)
        if not self.isVisible():
            self.show()
            self.raise_()
        self.update()

    def hide_indicator(self) -> None:
        """Hide the indicator."""
        self._zone_type = "none"
        self._highlight_rect = None
        self.hide()

    def paintEvent(self, event: object) -> None:
        """Paint the drop indicator."""
        if self._zone_type == "none" or not self._highlight_rect:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        if self._zone_type == "insert":
            # Draw vertical insert line (reuse pen)
            self._pen.setColor(self._insert_color)
            self._pen.setWidth(self.INSERT_LINE_WIDTH)
            painter.setPen(self._pen)

            center_x = rect.width() // 2
            painter.drawLine(center_x, 0, center_x, rect.height())

            # Draw small triangles at top and bottom
            painter.setBrush(self._insert_color)
            painter.setPen(Qt.PenStyle.NoPen)

            # Top triangle (reuse polygon)
            triangle_size = 4
            self._top_triangle.clear()
            self._top_triangle.append(QPoint(center_x - triangle_size, 0))
            self._top_triangle.append(QPoint(center_x + triangle_size, 0))
            self._top_triangle.append(QPoint(center_x, triangle_size))
            painter.drawPolygon(self._top_triangle)

            # Bottom triangle (reuse polygon)
            self._bottom_triangle.clear()
            self._bottom_triangle.append(QPoint(center_x - triangle_size, rect.height()))
            self._bottom_triangle.append(QPoint(center_x + triangle_size, rect.height()))
            self._bottom_triangle.append(QPoint(center_x, rect.height() - triangle_size))
            painter.drawPolygon(self._bottom_triangle)

        elif self._zone_type == "nest":
            # Draw border around tab (reuse pen)
            self._pen.setColor(self._nest_border_color)
            self._pen.setWidth(self.NEST_BORDER_WIDTH)
            painter.setPen(self._pen)

            # Fill with semi-transparent color
            painter.setBrush(self._nest_fill_color)

            # Draw rounded rectangle
            margin = self.NEST_BORDER_WIDTH // 2
            painter.drawRoundedRect(
                margin,
                margin,
                rect.width() - self.NEST_BORDER_WIDTH,
                rect.height() - self.NEST_BORDER_WIDTH,
                4,
                4,
            )

        painter.end()


class TabDropIndicatorController:
    """Controller for managing tab drop indicators.

    Connects to EnhancedTabWidget signals to show/hide indicators.
    """

    def __init__(self, parent_widget: QWidget | None = None) -> None:
        """Initialize controller.

        Args:
            parent_widget: Parent for the indicator widget
        """
        self._indicator = TabDropIndicator(parent_widget)
        self._tab_bar: QWidget | None = None
        self._last_zone: str = "none"
        self._last_index: int = -1

    def set_tab_bar(self, tab_bar: QWidget) -> None:
        """Set the tab bar to track for drop zones."""
        self._tab_bar = tab_bar

    def set_colors(
        self,
        insert_color: str | None = None,
        nest_border_color: str | None = None,
        nest_fill_color: str | None = None,
    ) -> None:
        """Set indicator colors."""
        self._indicator.set_colors(insert_color, nest_border_color, nest_fill_color)

    def on_drop_zone_changed(
        self, zone: str, target_index: int, rect: QRect | None
    ) -> None:
        """Handle drop zone change from tab bar.

        Args:
            zone: Zone type ("none", "before", "into", "after", "end")
            target_index: Target tab index
            rect: Highlight rectangle in tab bar local coordinates
        """
        # Skip if nothing changed (prevents flicker)
        if zone == self._last_zone and target_index == self._last_index:
            return

        self._last_zone = zone
        self._last_index = target_index

        if zone == "none" or rect is None or not self._tab_bar:
            self._indicator.hide_indicator()
            return

        # Convert to global coordinates
        global_pos = self._tab_bar.mapToGlobal(rect.topLeft())
        global_rect = QRect(global_pos, rect.size())

        if zone == "into":
            self._indicator.show_nest_indicator(global_rect)
        elif zone in ("before", "after"):
            self._indicator.show_insert_indicator(global_rect)
        else:
            self._indicator.hide_indicator()

    def hide(self) -> None:
        """Hide the indicator."""
        self._indicator.hide_indicator()

    def cleanup(self) -> None:
        """Clean up resources."""
        self._indicator.hide()
        self._indicator.deleteLater()
        self._indicator = None
        self._tab_bar = None
