"""ResponsiveController - Responsive design and breakpoint management.

This controller manages window width breakpoints and applies
panel visibility rules based on current breakpoint.
"""

from typing import Any

from PySide6.QtCore import QObject, Signal

from widgetsystem.enums import ResponsiveAction


class ResponsiveController(QObject):
    """Controller for responsive design.

    Manages breakpoints and applies panel visibility rules.

    Signals:
        breakpointChanged: Emitted when breakpoint changes (old_bp, new_bp)
        ruleApplied: Emitted when a rule is applied (rule_id)
    """

    breakpointChanged = Signal(str, str)  # old_breakpoint, new_breakpoint
    ruleApplied = Signal(str)  # rule_id

    def __init__(
        self,
        responsive_factory: Any,
        dock_controller: Any,
        parent: QObject | None = None,
    ) -> None:
        """Initialize ResponsiveController.

        Args:
            responsive_factory: ResponsiveFactory for configurations
            dock_controller: DockController for dock operations
            parent: Parent QObject
        """
        super().__init__(parent)

        self._responsive_factory = responsive_factory
        self._dock_controller = dock_controller

        # State
        self._width_ranges: dict[str, tuple[int, int]] = {}
        self._current_breakpoint: str | None = None
        self._applied_rules: set[str] = set()

    @property
    def current_breakpoint(self) -> str | None:
        """Get current breakpoint ID."""
        return self._current_breakpoint

    @property
    def applied_rules(self) -> set[str]:
        """Get set of applied rule IDs."""
        return set(self._applied_rules)

    def initialize(self) -> None:
        """Initialize responsive system from factory configuration."""
        try:
            breakpoints = self._responsive_factory.load_breakpoints()
            for bp in breakpoints:
                self._width_ranges[bp.id] = (bp.min_width, bp.max_width)
                print(
                    f"Responsive: Registered breakpoint '{bp.id}' "
                    f"({bp.min_width}-{bp.max_width}px)"
                )

            rules = self._responsive_factory.load_responsive_rules()
            print(
                f"[+] Responsive System initialized: "
                f"{len(breakpoints)} breakpoints, {len(rules)} rules"
            )
        except Exception as e:
            print(f"[!] Warning: Failed to load responsive configuration: {e}")

    def get_breakpoint_for_width(self, width: int) -> str | None:
        """Determine breakpoint for a given width.

        Args:
            width: Window width in pixels

        Returns:
            Breakpoint ID or None
        """
        for bp_id, (min_width, max_width) in self._width_ranges.items():
            if min_width <= width <= max_width:
                return bp_id
        return None

    def update_for_width(self, width: int) -> None:
        """Update responsive state for new window width.

        Args:
            width: New window width in pixels
        """
        new_breakpoint = self.get_breakpoint_for_width(width)

        if new_breakpoint and new_breakpoint != self._current_breakpoint:
            old_breakpoint = self._current_breakpoint
            print(
                f"Responsive: Breakpoint changed to '{new_breakpoint}' (width={width}px)"
            )

            self._current_breakpoint = new_breakpoint
            self._applied_rules.clear()

            self._apply_rules(new_breakpoint)
            self.breakpointChanged.emit(old_breakpoint or "", new_breakpoint)

    def _apply_rules(self, breakpoint_id: str) -> None:
        """Apply panel visibility rules for a breakpoint.

        Args:
            breakpoint_id: Breakpoint identifier
        """
        try:
            rules = self._responsive_factory.load_responsive_rules()
            for rule in rules:
                if rule.breakpoint != breakpoint_id:
                    continue

                # Find dock with matching panel_id
                dock = self._dock_controller.find_dock_by_title(rule.panel_id)
                if dock is None:
                    dock = self._dock_controller.find_dock(rule.panel_id)
                if dock is None:
                    continue

                # Apply rule action using ResponsiveAction enum
                action = rule.action.lower()
                if action == ResponsiveAction.HIDE.value:
                    dock.toggleView(False)
                elif action == ResponsiveAction.SHOW.value:
                    dock.toggleView(True)
                elif action == ResponsiveAction.COLLAPSE.value:
                    dock.setFloating(False)

                self._applied_rules.add(rule.id)
                self.ruleApplied.emit(rule.id)

        except Exception as e:
            print(f"Warning: Failed to apply responsive rules: {e}")

    def reset(self) -> None:
        """Reset responsive state."""
        self._current_breakpoint = None
        self._applied_rules.clear()
