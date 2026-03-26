"""Tab operation commands with undo/redo support.

Provides Command pattern implementations for all tab operations:
- MoveTabCommand: Move tab to different position/container
- NestTabCommand: Nest tab inside another tab
- UnnestTabCommand: Remove tab from nested position
- FloatTabCommand: Float tab to separate window
- CloseTabCommand: Close tab (reversible)
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from widgetsystem.core.undo_redo import Command

if TYPE_CHECKING:
    from widgetsystem.controllers.tab_command_controller import TabCommandController


@dataclass
class TabState:
    """Serializable state of a tab for undo operations."""

    tab_id: str
    title: str
    container_id: str
    index: int
    closable: bool = True
    movable: bool = True
    floatable: bool = True
    parent_tab_id: str | None = None
    children_ids: list[str] = field(default_factory=list)
    widget_state: dict[str, Any] = field(default_factory=dict)


class MoveTabCommand(Command):
    """Command for moving a tab to a new position or container."""

    def __init__(
        self,
        tab_id: str,
        target_container_id: str,
        target_index: int,
        controller: "TabCommandController",
    ) -> None:
        super().__init__(f"Move tab {tab_id} to {target_container_id}[{target_index}]")
        self.tab_id = tab_id
        self.target_container_id = target_container_id
        self.target_index = target_index
        self._controller = controller

        # Store original position for undo
        self._original_container_id: str | None = None
        self._original_index: int = -1

    def execute(self) -> None:
        """Move tab to new position."""
        # Save original position
        current = self._controller.get_tab_location(self.tab_id)
        if current:
            self._original_container_id = current["container_id"]
            self._original_index = current["index"]

        # Perform move
        self._controller._do_move_tab(
            self.tab_id, self.target_container_id, self.target_index
        )

    def undo(self) -> None:
        """Restore tab to original position."""
        if self._original_container_id is not None:
            self._controller._do_move_tab(
                self.tab_id, self._original_container_id, self._original_index
            )


class NestTabCommand(Command):
    """Command for nesting a tab inside another tab."""

    def __init__(
        self,
        source_tab_id: str,
        target_tab_id: str,
        controller: "TabCommandController",
    ) -> None:
        super().__init__(f"Nest tab {source_tab_id} into {target_tab_id}")
        self.source_tab_id = source_tab_id
        self.target_tab_id = target_tab_id
        self._controller = controller

        # Store original state for undo
        self._original_state: TabState | None = None

    def execute(self) -> None:
        """Nest source tab into target tab."""
        # Save original state
        self._original_state = self._controller.export_tab_state(self.source_tab_id)

        # Perform nesting
        self._controller._do_nest_tab(self.source_tab_id, self.target_tab_id)

    def undo(self) -> None:
        """Restore tab to original position (unnest)."""
        if self._original_state:
            self._controller._do_unnest_tab(self.source_tab_id, self._original_state)


class UnnestTabCommand(Command):
    """Command for removing a tab from nested position to parent level."""

    def __init__(
        self,
        tab_id: str,
        controller: "TabCommandController",
    ) -> None:
        super().__init__(f"Unnest tab {tab_id}")
        self.tab_id = tab_id
        self._controller = controller

        # Store parent info for undo
        self._parent_tab_id: str | None = None
        self._original_index: int = -1

    def execute(self) -> None:
        """Unnest tab to parent level."""
        # Save parent info
        state = self._controller.export_tab_state(self.tab_id)
        if state:
            self._parent_tab_id = state.parent_tab_id
            self._original_index = state.index

        # Perform unnesting
        self._controller._do_unnest_to_parent(self.tab_id)

    def undo(self) -> None:
        """Re-nest tab back into original parent."""
        if self._parent_tab_id:
            self._controller._do_nest_tab(self.tab_id, self._parent_tab_id)


class FloatTabCommand(Command):
    """Command for floating a tab to a separate window."""

    def __init__(
        self,
        tab_id: str,
        controller: "TabCommandController",
    ) -> None:
        super().__init__(f"Float tab {tab_id}")
        self.tab_id = tab_id
        self._controller = controller

        # Store original state for undo
        self._original_state: TabState | None = None
        self._float_dock_id: str | None = None

    def execute(self) -> None:
        """Float tab to separate window."""
        # Save original state
        self._original_state = self._controller.export_tab_state(self.tab_id)

        # Perform float
        self._float_dock_id = self._controller._do_float_tab(self.tab_id)

    def undo(self) -> None:
        """Restore tab to original container."""
        if self._original_state and self._float_dock_id:
            self._controller._do_dock_tab(
                self.tab_id,
                self._float_dock_id,
                self._original_state.container_id,
                self._original_state.index,
            )


class CloseTabCommand(Command):
    """Command for closing a tab (reversible)."""

    def __init__(
        self,
        tab_id: str,
        controller: "TabCommandController",
    ) -> None:
        super().__init__(f"Close tab {tab_id}")
        self.tab_id = tab_id
        self._controller = controller

        # Store full state for undo
        self._saved_state: TabState | None = None

    def execute(self) -> None:
        """Close the tab, saving state for undo."""
        # Save complete tab state
        self._saved_state = self._controller.export_tab_state(self.tab_id)

        # Close tab
        self._controller._do_close_tab(self.tab_id)

    def undo(self) -> None:
        """Restore closed tab from saved state."""
        if self._saved_state:
            self._controller._do_restore_tab(self._saved_state)


class ActivateTabCommand(Command):
    """Command for activating (switching to) a tab."""

    def __init__(
        self,
        tab_id: str,
        controller: "TabCommandController",
    ) -> None:
        super().__init__(f"Activate tab {tab_id}")
        self.tab_id = tab_id
        self._controller = controller

        # Store previously active tab for undo
        self._previous_tab_id: str | None = None

    def execute(self) -> None:
        """Activate the tab."""
        self._previous_tab_id = self._controller.get_active_tab_id()
        self._controller._do_activate_tab(self.tab_id)

    def undo(self) -> None:
        """Restore previous active tab."""
        if self._previous_tab_id:
            self._controller._do_activate_tab(self._previous_tab_id)
