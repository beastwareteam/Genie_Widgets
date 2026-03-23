"""DnDController - Drag and Drop rules management.

This controller manages drop zones and movement rules for dock panels.
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from widgetsystem.enums import DockArea


logger = logging.getLogger(__name__)


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
                logger.info("DnD: Registered drop zone '%s' for area '%s'", zone.id, zone.area)

            # Load DnD rules
            dnd_rules = self._dnd_factory.load_dnd_rules()
            for rule in dnd_rules:
                if rule.panel_id not in self._rules:
                    self._rules[rule.panel_id] = {}
                self._rules[rule.panel_id][rule.source_area] = rule.allowed_target_areas
                self.ruleRegistered.emit(rule.id)
                logger.info(
                    "DnD: Registered rule '%s' - %s from %s -> %s",
                    rule.id,
                    rule.panel_id,
                    rule.source_area,
                    rule.allowed_target_areas,
                )

            logger.info(
                "DnD System initialized: %s zones, %s panels",
                len(self._drop_zones),
                len(self._rules),
            )
        except Exception as e:
            logger.warning("Failed to load DnD configuration: %s", e)

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
