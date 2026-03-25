"""DnDController - Drag and Drop rules management.

This controller manages drop zones and movement rules for dock panels.
"""

from typing import Any

from PySide6.QtCore import QObject, Signal

from widgetsystem.enums import DockArea


class DnDController(QObject):
    """Controller for drag-and-drop rules.

    Manages drop zones and panel movement restrictions.

    Signals:
        moveBlocked: Emitted when a move is blocked (panel_id, source, target)
        zoneRegistered: Emitted when a drop zone is registered (zone_id)
        ruleRegistered: Emitted when a rule is registered (rule_id)
    """

    moveBlocked = Signal(str, str, str)  # panel_id, source_area, target_area
    zoneRegistered = Signal(str)  # zone_id
    ruleRegistered = Signal(str)  # rule_id

    def __init__(
        self,
        dnd_factory: Any,
        parent: QObject | None = None,
    ) -> None:
        """Initialize DnDController.

        Args:
            dnd_factory: DnDFactory for loading DnD configurations
            parent: Parent QObject
        """
        super().__init__(parent)

        self._dnd_factory = dnd_factory

        # Runtime state
        self._drop_zones: dict[str, Any] = {}  # area -> DropZone
        self._rules: dict[str, dict[str, list[str]]] = {}  # panel_id -> {source -> [targets]}

    @property
    def drop_zones(self) -> dict[str, Any]:
        """Get drop zones map (read-only copy)."""
        return dict(self._drop_zones)

    @property
    def rules(self) -> dict[str, dict[str, list[str]]]:
        """Get rules map (read-only copy)."""
        return {k: dict(v) for k, v in self._rules.items()}

    def initialize(self) -> None:
        """Initialize DnD system from factory configuration."""
        try:
            # Load drop zones
            drop_zones = self._dnd_factory.load_drop_zones()
            for zone in drop_zones:
                self._drop_zones[zone.area] = zone
                self.zoneRegistered.emit(zone.id)
                print(f"DnD: Registered drop zone '{zone.id}' for area '{zone.area}'")

            # Load DnD rules
            dnd_rules = self._dnd_factory.load_dnd_rules()
            for rule in dnd_rules:
                if rule.panel_id not in self._rules:
                    self._rules[rule.panel_id] = {}
                self._rules[rule.panel_id][rule.source_area] = rule.allowed_target_areas
                self.ruleRegistered.emit(rule.id)
                print(
                    f"DnD: Registered rule '{rule.id}' - {rule.panel_id} "
                    f"from {rule.source_area} -> {rule.allowed_target_areas}"
                )

            print(
                f"[+] DnD System initialized: "
                f"{len(self._drop_zones)} zones, {len(self._rules)} panels"
            )
        except Exception as e:
            print(f"[!] Warning: Failed to load DnD configuration: {e}")

    def is_move_allowed(
        self,
        panel_id: str,
        source_area: str | DockArea,
        target_area: str | DockArea,
    ) -> bool:
        """Check if a panel move is allowed.

        Args:
            panel_id: Panel identifier
            source_area: Source dock area
            target_area: Target dock area

        Returns:
            True if move is allowed, False otherwise
        """
        # Convert enums to strings
        if isinstance(source_area, DockArea):
            source_area = source_area.value
        if isinstance(target_area, DockArea):
            target_area = target_area.value

        if panel_id not in self._rules:
            return True  # No restrictions

        panel_rules = self._rules[panel_id]
        if source_area not in panel_rules:
            return True  # No restrictions for this source

        allowed_targets = panel_rules[source_area]
        if not allowed_targets:
            self.moveBlocked.emit(panel_id, source_area, target_area)
            return False  # Explicit block

        allowed = target_area in allowed_targets
        if not allowed:
            self.moveBlocked.emit(panel_id, source_area, target_area)

        return allowed

    def get_allowed_targets(
        self,
        panel_id: str,
        source_area: str | DockArea,
    ) -> list[str]:
        """Get allowed target areas for a panel from a source.

        Args:
            panel_id: Panel identifier
            source_area: Source dock area

        Returns:
            List of allowed target area names
        """
        if isinstance(source_area, DockArea):
            source_area = source_area.value

        if panel_id not in self._rules:
            return [a.value for a in DockArea]  # All areas allowed

        panel_rules = self._rules[panel_id]
        if source_area not in panel_rules:
            return [a.value for a in DockArea]

        return panel_rules[source_area]

    def get_drop_zone(self, area: str | DockArea) -> Any | None:
        """Get drop zone for an area.

        Args:
            area: Dock area

        Returns:
            DropZone object or None
        """
        if isinstance(area, DockArea):
            area = area.value
        return self._drop_zones.get(area)

    def reset(self) -> None:
        """Reset DnD state."""
        self._drop_zones.clear()
        self._rules.clear()

    # ------------------------------------------------------------------
    # Free X/Y Drag Navigation
    # ------------------------------------------------------------------

    def calculate_drop_area_from_position(
        self,
        x: int,
        y: int,
        container_width: int,
        container_height: int,
        edge_threshold: float = 0.2,
    ) -> str:
        """Calculate target dock area from cursor position.

        Divides the container into zones:
        - Edges (20% from each side) → corresponding dock area
        - Center (remaining 60%) → center area

        Args:
            x: Cursor X position
            y: Cursor Y position
            container_width: Container width
            container_height: Container height
            edge_threshold: Edge zone threshold (0.0-0.5)

        Returns:
            Dock area name (left, right, top, bottom, center)
        """
        # Calculate relative position (0.0 to 1.0)
        rel_x = x / container_width if container_width > 0 else 0.5
        rel_y = y / container_height if container_height > 0 else 0.5

        # Check edges (priority: corners go to horizontal)
        if rel_x < edge_threshold:
            return "left"
        elif rel_x > (1.0 - edge_threshold):
            return "right"
        elif rel_y < edge_threshold:
            return "top"
        elif rel_y > (1.0 - edge_threshold):
            return "bottom"
        else:
            return "center"

    def get_drop_zone_rect(
        self,
        area: str,
        container_width: int,
        container_height: int,
        edge_threshold: float = 0.2,
    ) -> tuple[int, int, int, int]:
        """Get rectangle for a drop zone area.

        Args:
            area: Dock area name
            container_width: Container width
            container_height: Container height
            edge_threshold: Edge zone threshold

        Returns:
            Tuple of (x, y, width, height)
        """
        edge_w = int(container_width * edge_threshold)
        edge_h = int(container_height * edge_threshold)

        if area == "left":
            return (0, 0, edge_w, container_height)
        elif area == "right":
            return (container_width - edge_w, 0, edge_w, container_height)
        elif area == "top":
            return (edge_w, 0, container_width - 2 * edge_w, edge_h)
        elif area == "bottom":
            return (edge_w, container_height - edge_h, container_width - 2 * edge_w, edge_h)
        else:  # center
            return (edge_w, edge_h, container_width - 2 * edge_w, container_height - 2 * edge_h)

    def get_all_drop_zone_rects(
        self,
        container_width: int,
        container_height: int,
        edge_threshold: float = 0.2,
    ) -> dict[str, tuple[int, int, int, int]]:
        """Get all drop zone rectangles.

        Args:
            container_width: Container width
            container_height: Container height
            edge_threshold: Edge zone threshold

        Returns:
            Dict mapping area names to (x, y, width, height) tuples
        """
        return {
            area: self.get_drop_zone_rect(area, container_width, container_height, edge_threshold)
            for area in ["left", "right", "top", "bottom", "center"]
        }

    def validate_drop(
        self,
        panel_id: str,
        source_area: str,
        target_x: int,
        target_y: int,
        container_width: int,
        container_height: int,
    ) -> tuple[bool, str]:
        """Validate a drop operation and return target area.

        Args:
            panel_id: Panel being dragged
            source_area: Original dock area
            target_x: Drop X position
            target_y: Drop Y position
            container_width: Container width
            container_height: Container height

        Returns:
            Tuple of (is_valid, target_area)
        """
        target_area = self.calculate_drop_area_from_position(
            target_x, target_y, container_width, container_height
        )

        is_valid = self.is_move_allowed(panel_id, source_area, target_area)

        return (is_valid, target_area)
