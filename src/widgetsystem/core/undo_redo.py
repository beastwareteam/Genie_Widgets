"""Undo/Redo system for configuration editors.

Provides a command-based undo/redo implementation with:
- Command pattern for reversible operations
- Action history with configurable depth
- Signal-based notifications
- Serialization support for persistence
"""

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable
import copy
from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from pathlib import Path
from typing import Any, TypeVar

from PySide6.QtCore import QObject, Signal


logger = logging.getLogger(__name__)

T = TypeVar("T")


class Command(ABC):
    """Abstract base class for undoable commands.

    Commands encapsulate an action that can be executed and reversed.
    Each command stores the state needed to undo the operation.
    """

    def __init__(self, description: str = "") -> None:
        """Initialize command.

        Args:
            description: Human-readable description of the command
        """
        self.description = description
        self.timestamp = datetime.now(tz=UTC)

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""

    def redo(self) -> None:
        """Redo the command (default: re-execute)."""
        self.execute()

    def __repr__(self) -> str:
        """Return string representation of the command."""
        return f"{self.__class__.__name__}({self.description!r})"


@dataclass
class PropertyChangeCommand(Command):
    """Command for property value changes."""

    target: Any
    property_name: str
    old_value: Any
    new_value: Any
    description: str = ""

    def __post_init__(self) -> None:
        """Initialize description and timestamp after dataclass construction."""
        if not self.description:
            self.description = f"Change {self.property_name}"
        self.timestamp = datetime.now(tz=UTC)

    def execute(self) -> None:
        """Apply the new value."""
        if hasattr(self.target, self.property_name):
            setattr(self.target, self.property_name, self.new_value)
        elif isinstance(self.target, dict):
            self.target[self.property_name] = self.new_value

    def undo(self) -> None:
        """Restore the old value."""
        if hasattr(self.target, self.property_name):
            setattr(self.target, self.property_name, self.old_value)
        elif isinstance(self.target, dict):
            self.target[self.property_name] = self.old_value


@dataclass
class DictChangeCommand(Command):
    """Command for dictionary changes (add/remove/modify keys)."""

    target_dict: dict[str, Any]
    key: str
    old_value: Any | None
    new_value: Any | None
    description: str = ""

    def __post_init__(self) -> None:
        """Initialize description and timestamp after dataclass construction."""
        if not self.description:
            if self.old_value is None:
                self.description = f"Add key '{self.key}'"
            elif self.new_value is None:
                self.description = f"Remove key '{self.key}'"
            else:
                self.description = f"Modify key '{self.key}'"
        self.timestamp = datetime.now(tz=UTC)

    def execute(self) -> None:
        """Apply the change."""
        if self.new_value is None:
            # Remove key
            self.target_dict.pop(self.key, None)
        else:
            # Add or modify key
            self.target_dict[self.key] = self.new_value

    def undo(self) -> None:
        """Reverse the change."""
        if self.old_value is None:
            # Key was added, remove it
            self.target_dict.pop(self.key, None)
        else:
            # Restore old value
            self.target_dict[self.key] = self.old_value


@dataclass
class ListChangeCommand(Command):
    """Command for list changes (add/remove/modify items)."""

    target_list: list[Any]
    index: int
    old_item: Any | None
    new_item: Any | None
    description: str = ""

    def __post_init__(self) -> None:
        """Initialize description and timestamp after dataclass construction."""
        if not self.description:
            if self.old_item is None:
                self.description = f"Insert item at index {self.index}"
            elif self.new_item is None:
                self.description = f"Remove item at index {self.index}"
            else:
                self.description = f"Modify item at index {self.index}"
        self.timestamp = datetime.now(tz=UTC)

    def execute(self) -> None:
        """Apply the change."""
        if self.old_item is None and self.new_item is not None:
            # Insert new item
            self.target_list.insert(self.index, self.new_item)
        elif self.new_item is None and self.old_item is not None:
            # Remove item
            if self.index < len(self.target_list):
                self.target_list.pop(self.index)
        # Modify item
        elif self.index < len(self.target_list):
            self.target_list[self.index] = self.new_item

    def undo(self) -> None:
        """Reverse the change."""
        if self.old_item is None and self.new_item is not None:
            # Item was inserted, remove it
            if self.index < len(self.target_list):
                self.target_list.pop(self.index)
        elif self.new_item is None and self.old_item is not None:
            # Item was removed, restore it
            self.target_list.insert(self.index, self.old_item)
        # Item was modified, restore old value
        elif self.index < len(self.target_list):
            self.target_list[self.index] = self.old_item


class CompositeCommand(Command):
    """Command that groups multiple commands together."""

    def __init__(self, commands: list[Command], description: str = "") -> None:
        """Initialize composite command.

        Args:
            commands: List of commands to group
            description: Description of the composite action
        """
        super().__init__(description or "Multiple changes")
        self.commands = commands

    def execute(self) -> None:
        """Execute all commands in order."""
        for cmd in self.commands:
            cmd.execute()

    def undo(self) -> None:
        """Undo all commands in reverse order."""
        for cmd in reversed(self.commands):
            cmd.undo()


class CallbackCommand(Command):
    """Command using callbacks for execute and undo."""

    def __init__(
        self,
        execute_fn: Callable[[], None],
        undo_fn: Callable[[], None],
        description: str = "",
    ) -> None:
        """Initialize callback command.

        Args:
            execute_fn: Function to execute
            undo_fn: Function to undo
            description: Command description
        """
        super().__init__(description)
        self._execute_fn = execute_fn
        self._undo_fn = undo_fn

    def execute(self) -> None:
        """Call execute function."""
        self._execute_fn()

    def undo(self) -> None:
        """Call undo function."""
        self._undo_fn()


class UndoRedoManager(QObject):
    """Manager for undo/redo operations with Qt signals.

    Signals:
        undoAvailable: Emitted when undo becomes available/unavailable (bool)
        redoAvailable: Emitted when redo becomes available/unavailable (bool)
        commandExecuted: Emitted when a command is executed (description)
        commandUndone: Emitted when a command is undone (description)
        commandRedone: Emitted when a command is redone (description)
        stackChanged: Emitted when the command stack changes
    """

    undoAvailable = Signal(bool)
    redoAvailable = Signal(bool)
    commandExecuted = Signal(str)
    commandUndone = Signal(str)
    commandRedone = Signal(str)
    stackChanged = Signal()

    def __init__(
        self,
        max_history: int = 100,
        parent: QObject | None = None,
    ) -> None:
        """Initialize undo/redo manager.

        Args:
            max_history: Maximum number of commands to keep in history
            parent: Parent QObject
        """
        super().__init__(parent)
        self.max_history = max_history
        self._undo_stack: deque[Command] = deque(maxlen=max_history)
        self._redo_stack: deque[Command] = deque(maxlen=max_history)
        self._is_undoing = False
        self._is_redoing = False
        logger.debug("UndoRedoManager initialized with max_history=%s", max_history)

    def execute(self, command: Command) -> None:
        """Execute a command and add it to the undo stack.

        Args:
            command: Command to execute
        """
        try:
            command.execute()
            self._undo_stack.append(command)

            # Clear redo stack when new command is executed
            if not self._is_undoing and not self._is_redoing:
                self._redo_stack.clear()

            self._emit_availability_signals()
            self.commandExecuted.emit(command.description)
            self.stackChanged.emit()

            logger.debug("Command executed: %s", command.description)

        except Exception as exc:
            logger.exception("Error executing command")

    def undo(self) -> bool:
        """Undo the last command.

        Returns:
            True if undo was successful
        """
        if not self.can_undo():
            return False

        try:
            self._is_undoing = True
            command = self._undo_stack.pop()
            command.undo()
            self._redo_stack.append(command)

            self._emit_availability_signals()
            self.commandUndone.emit(command.description)
            self.stackChanged.emit()

            logger.debug("Command undone: %s", command.description)
            return True

        except Exception as exc:
            logger.exception("Error undoing command")
            return False

        finally:
            self._is_undoing = False

    def redo(self) -> bool:
        """Redo the last undone command.

        Returns:
            True if redo was successful
        """
        if not self.can_redo():
            return False

        try:
            self._is_redoing = True
            command = self._redo_stack.pop()
            command.redo()
            self._undo_stack.append(command)

            self._emit_availability_signals()
            self.commandRedone.emit(command.description)
            self.stackChanged.emit()

            logger.debug("Command redone: %s", command.description)
            return True

        except Exception as exc:
            logger.exception("Error redoing command")
            return False

        finally:
            self._is_redoing = False

    def can_undo(self) -> bool:
        """Check if undo is available.

        Returns:
            True if there are commands to undo
        """
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available.

        Returns:
            True if there are commands to redo
        """
        return len(self._redo_stack) > 0

    def clear(self) -> None:
        """Clear all command history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._emit_availability_signals()
        self.stackChanged.emit()
        logger.debug("Command history cleared")

    def get_undo_description(self) -> str | None:
        """Get description of the next command to undo.

        Returns:
            Command description or None
        """
        if self._undo_stack:
            return self._undo_stack[-1].description
        return None

    def get_redo_description(self) -> str | None:
        """Get description of the next command to redo.

        Returns:
            Command description or None
        """
        if self._redo_stack:
            return self._redo_stack[-1].description
        return None

    def get_undo_history(self) -> list[str]:
        """Get list of undo command descriptions.

        Returns:
            List of descriptions (most recent first)
        """
        return [cmd.description for cmd in reversed(self._undo_stack)]

    def get_redo_history(self) -> list[str]:
        """Get list of redo command descriptions.

        Returns:
            List of descriptions (most recent first)
        """
        return [cmd.description for cmd in reversed(self._redo_stack)]

    def undo_count(self) -> int:
        """Get number of commands that can be undone.

        Returns:
            Number of undo commands
        """
        return len(self._undo_stack)

    def redo_count(self) -> int:
        """Get number of commands that can be redone.

        Returns:
            Number of redo commands
        """
        return len(self._redo_stack)

    def _emit_availability_signals(self) -> None:
        """Emit availability signals."""
        self.undoAvailable.emit(self.can_undo())
        self.redoAvailable.emit(self.can_redo())


class ConfigurationUndoManager(UndoRedoManager):
    """Specialized undo/redo manager for configuration editing.

    Provides additional features:
    - Snapshot-based undo for complex configuration changes
    - Automatic save point tracking
    - JSON serialization support
    """

    savePointReached = Signal()

    def __init__(
        self,
        config_path: Path | None = None,
        max_history: int = 100,
        parent: QObject | None = None,
    ) -> None:
        """Initialize configuration undo manager.

        Args:
            config_path: Path to configuration directory
            max_history: Maximum history depth
            parent: Parent QObject
        """
        super().__init__(max_history, parent)
        self.config_path = config_path
        self._save_point_index: int | None = None
        self._snapshots: dict[str, Any] = {}

    def create_snapshot(self, name: str, data: Any) -> None:
        """Create a named snapshot of configuration data.

        Args:
            name: Snapshot name
            data: Data to snapshot (will be deep-copied)
        """
        self._snapshots[name] = copy.deepcopy(data)
        logger.debug("Created snapshot: %s", name)

    def restore_snapshot(self, name: str) -> Any | None:
        """Restore a named snapshot.

        Args:
            name: Snapshot name

        Returns:
            Snapshot data or None if not found
        """
        if name in self._snapshots:
            return copy.deepcopy(self._snapshots[name])
        return None

    def delete_snapshot(self, name: str) -> None:
        """Delete a named snapshot.

        Args:
            name: Snapshot name
        """
        self._snapshots.pop(name, None)

    def set_save_point(self) -> None:
        """Mark current state as save point."""
        self._save_point_index = len(self._undo_stack)
        logger.debug("Save point set at index %s", self._save_point_index)

    def is_at_save_point(self) -> bool:
        """Check if current state matches save point.

        Returns:
            True if at save point
        """
        return self._save_point_index == len(self._undo_stack)

    def has_unsaved_changes(self) -> bool:
        """Check if there are changes since last save point.

        Returns:
            True if there are unsaved changes
        """
        return not self.is_at_save_point()

    def track_config_change(
        self,
        config_dict: dict[str, Any],
        key: str,
        new_value: Any,
        description: str = "",
    ) -> None:
        """Track a configuration change with automatic old value capture.

        Args:
            config_dict: Configuration dictionary
            key: Key being changed
            new_value: New value
            description: Change description
        """
        old_value = config_dict.get(key)
        command = DictChangeCommand(
            target_dict=config_dict,
            key=key,
            old_value=copy.deepcopy(old_value),
            new_value=copy.deepcopy(new_value),
            description=description or f"Change {key}",
        )
        self.execute(command)

    def track_list_insert(
        self,
        target_list: list[Any],
        index: int,
        item: Any,
        description: str = "",
    ) -> None:
        """Track a list insertion.

        Args:
            target_list: Target list
            index: Insertion index
            item: Item to insert
            description: Change description
        """
        command = ListChangeCommand(
            target_list=target_list,
            index=index,
            old_item=None,
            new_item=copy.deepcopy(item),
            description=description or "Insert item",
        )
        self.execute(command)

    def track_list_remove(
        self,
        target_list: list[Any],
        index: int,
        description: str = "",
    ) -> None:
        """Track a list removal.

        Args:
            target_list: Target list
            index: Removal index
            description: Change description
        """
        if index < len(target_list):
            command = ListChangeCommand(
                target_list=target_list,
                index=index,
                old_item=copy.deepcopy(target_list[index]),
                new_item=None,
                description=description or "Remove item",
            )
            self.execute(command)
