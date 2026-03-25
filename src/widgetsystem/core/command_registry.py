"""Command registry for CLI automation.

Provides a central registry for executing tab and UI commands
programmatically. Enables scripting and automation of all UI actions.

Usage:
    registry = CommandRegistry(tab_controller)
    result = registry.execute("nest_tab", source="tab_charts", target="tab_analytics")
    result = registry.execute("move_tab", tab_id="tab_overview", target="main_tabs", index=0)
    result = registry.execute("list_tabs")
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from widgetsystem.controllers.tab_command_controller import TabCommandController


@dataclass
class CommandResult:
    """Result of a command execution."""

    success: bool
    command: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __bool__(self) -> bool:
        return self.success


class CommandRegistry(QObject):
    """Central registry for CLI automation commands.

    Registers and executes commands by name with keyword arguments.
    Provides query commands for introspection.

    Signals:
        commandExecuted: Emitted after successful command (name, result)
        commandFailed: Emitted on command failure (name, error)
    """

    commandExecuted = Signal(str, object)  # command_name, CommandResult
    commandFailed = Signal(str, str)  # command_name, error_message

    def __init__(
        self,
        tab_controller: "TabCommandController",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._tab_controller = tab_controller
        self._commands: dict[str, Callable[..., dict[str, Any]]] = {}
        self._command_help: dict[str, str] = {}
        self._register_commands()

    def _register_commands(self) -> None:
        """Register all available commands."""
        # Tab movement commands
        self._register(
            "move_tab",
            self._cmd_move_tab,
            "Move tab to target container at index. Args: tab_id, target, index=-1",
        )
        self._register(
            "nest_tab",
            self._cmd_nest_tab,
            "Nest source tab inside target tab. Args: source, target",
        )
        self._register(
            "unnest_tab",
            self._cmd_unnest_tab,
            "Unnest tab to parent level. Args: tab_id",
        )
        self._register(
            "float_tab",
            self._cmd_float_tab,
            "Float tab to separate window. Args: tab_id",
        )
        self._register(
            "close_tab",
            self._cmd_close_tab,
            "Close tab. Args: tab_id",
        )
        self._register(
            "activate_tab",
            self._cmd_activate_tab,
            "Activate (switch to) tab. Args: tab_id",
        )

        # Query commands
        self._register(
            "list_tabs",
            self._cmd_list_tabs,
            "List all tabs with their metadata. Args: container_id=None",
        )
        self._register(
            "get_tab_info",
            self._cmd_get_tab_info,
            "Get detailed info about a tab. Args: tab_id",
        )
        self._register(
            "get_active_tab",
            self._cmd_get_active_tab,
            "Get currently active tab ID. Args: container_id=None",
        )
        self._register(
            "list_containers",
            self._cmd_list_containers,
            "List all tab containers. Args: none",
        )

        # Undo/Redo commands
        self._register(
            "undo",
            self._cmd_undo,
            "Undo last tab command. Args: none",
        )
        self._register(
            "redo",
            self._cmd_redo,
            "Redo last undone command. Args: none",
        )

        # Help command
        self._register(
            "help",
            self._cmd_help,
            "Show available commands. Args: command=None",
        )

    def _register(
        self, name: str, func: Callable[..., dict[str, Any]], help_text: str
    ) -> None:
        """Register a command."""
        self._commands[name] = func
        self._command_help[name] = help_text

    def execute(self, command: str, **kwargs: Any) -> CommandResult:
        """Execute a command by name with keyword arguments.

        Args:
            command: Command name
            **kwargs: Command arguments

        Returns:
            CommandResult with success status and data
        """
        if command not in self._commands:
            error = f"Unknown command: {command}. Use 'help' to list commands."
            self.commandFailed.emit(command, error)
            return CommandResult(success=False, command=command, error=error)

        try:
            data = self._commands[command](**kwargs)
            result = CommandResult(success=True, command=command, data=data)
            self.commandExecuted.emit(command, result)
            return result
        except TypeError as e:
            error = f"Invalid arguments for {command}: {e}"
            self.commandFailed.emit(command, error)
            return CommandResult(success=False, command=command, error=error)
        except Exception as e:
            error = f"Command {command} failed: {e}"
            self.commandFailed.emit(command, error)
            return CommandResult(success=False, command=command, error=error)

    def available_commands(self) -> list[str]:
        """Get list of available command names."""
        return sorted(self._commands.keys())

    def get_help(self, command: str | None = None) -> str:
        """Get help text for command(s)."""
        if command:
            return self._command_help.get(command, f"Unknown command: {command}")
        return "\n".join(
            f"  {name}: {help_text}"
            for name, help_text in sorted(self._command_help.items())
        )

    # ------------------------------------------------------------------
    # Tab Movement Commands
    # ------------------------------------------------------------------

    def _cmd_move_tab(
        self, tab_id: str, target: str, index: int = -1
    ) -> dict[str, Any]:
        """Move tab to target container."""
        success = self._tab_controller.move_tab(tab_id, target, index)
        return {"moved": success, "tab_id": tab_id, "target": target, "index": index}

    def _cmd_nest_tab(self, source: str, target: str) -> dict[str, Any]:
        """Nest source tab inside target tab."""
        success = self._tab_controller.nest_tab(source, target)
        return {"nested": success, "source": source, "target": target}

    def _cmd_unnest_tab(self, tab_id: str) -> dict[str, Any]:
        """Unnest tab to parent level."""
        success = self._tab_controller.unnest_tab(tab_id)
        return {"unnested": success, "tab_id": tab_id}

    def _cmd_float_tab(self, tab_id: str) -> dict[str, Any]:
        """Float tab to separate window."""
        dock_id = self._tab_controller.float_tab(tab_id)
        return {"floated": dock_id is not None, "tab_id": tab_id, "dock_id": dock_id}

    def _cmd_close_tab(self, tab_id: str) -> dict[str, Any]:
        """Close tab."""
        success = self._tab_controller.close_tab(tab_id)
        return {"closed": success, "tab_id": tab_id}

    def _cmd_activate_tab(self, tab_id: str) -> dict[str, Any]:
        """Activate tab."""
        success = self._tab_controller.activate_tab(tab_id)
        return {"activated": success, "tab_id": tab_id}

    # ------------------------------------------------------------------
    # Query Commands
    # ------------------------------------------------------------------

    def _cmd_list_tabs(self, container_id: str | None = None) -> dict[str, Any]:
        """List all tabs."""
        tabs = self._tab_controller.list_tabs(container_id)
        return {"tabs": tabs, "count": len(tabs)}

    def _cmd_get_tab_info(self, tab_id: str) -> dict[str, Any]:
        """Get tab info."""
        info = self._tab_controller.get_tab_info(tab_id)
        return {"tab": info} if info else {"error": f"Tab not found: {tab_id}"}

    def _cmd_get_active_tab(self, container_id: str | None = None) -> dict[str, Any]:
        """Get active tab."""
        tab_id = self._tab_controller.get_active_tab_id(container_id)
        return {"active_tab_id": tab_id}

    def _cmd_list_containers(self) -> dict[str, Any]:
        """List tab containers."""
        containers = self._tab_controller.list_containers()
        return {"containers": containers, "count": len(containers)}

    # ------------------------------------------------------------------
    # Undo/Redo Commands
    # ------------------------------------------------------------------

    def _cmd_undo(self) -> dict[str, Any]:
        """Undo last command."""
        success = self._tab_controller.undo()
        return {"undone": success}

    def _cmd_redo(self) -> dict[str, Any]:
        """Redo last undone command."""
        success = self._tab_controller.redo()
        return {"redone": success}

    # ------------------------------------------------------------------
    # Help Command
    # ------------------------------------------------------------------

    def _cmd_help(self, command: str | None = None) -> dict[str, Any]:
        """Show help."""
        if command:
            return {"command": command, "help": self.get_help(command)}
        return {"commands": self.available_commands(), "help": self.get_help()}
