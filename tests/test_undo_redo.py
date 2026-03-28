"""Tests for the undo/redo system - covers all command types and the manager."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication
import pytest

from widgetsystem.core.undo_redo import (
    CallbackCommand,
    Command,
    CompositeCommand,
    ConfigurationUndoManager,
    DictChangeCommand,
    ListChangeCommand,
    PropertyChangeCommand,
    UndoRedoManager,
)


pytestmark = pytest.mark.isolated


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide QApplication instance for the module."""
    application = QApplication.instance()
    if not isinstance(application, QApplication):
        application = QApplication([])
    assert isinstance(application, QApplication)
    return application


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _SimpleTarget:
    """Simple object for testing PropertyChangeCommand."""

    def __init__(self, value: int = 0) -> None:
        self.value = value


class _ConcreteCommand(Command):
    """Minimal concrete command for testing abstract base class."""

    def __init__(self, log: list[str], description: str = "") -> None:
        super().__init__(description)
        self._log = log

    def execute(self) -> None:
        self._log.append("execute")

    def undo(self) -> None:
        self._log.append("undo")


# ---------------------------------------------------------------------------
# Command base
# ---------------------------------------------------------------------------


def test_command_repr():
    """__repr__ should include class name and description."""
    log: list[str] = []
    cmd = _ConcreteCommand(log, "desc")
    assert "_ConcreteCommand" in repr(cmd)
    assert "desc" in repr(cmd)


def test_command_redo_defaults_to_execute():
    """Default redo() should call execute()."""
    log: list[str] = []
    cmd = _ConcreteCommand(log, "x")
    cmd.redo()
    assert log == ["execute"]


# ---------------------------------------------------------------------------
# PropertyChangeCommand
# ---------------------------------------------------------------------------


def test_property_change_execute_on_object():
    """execute should set the new value on the object attribute."""
    target = _SimpleTarget(10)
    cmd = PropertyChangeCommand(target, "value", old_value=10, new_value=42)
    cmd.execute()
    assert target.value == 42


def test_property_change_undo_on_object():
    """undo should restore the old value on the object attribute."""
    target = _SimpleTarget(10)
    cmd = PropertyChangeCommand(target, "value", old_value=10, new_value=42)
    cmd.execute()
    cmd.undo()
    assert target.value == 10


def test_property_change_execute_on_dict():
    """execute should set the new value in a dict."""
    d: dict[str, int] = {"x": 1}
    cmd = PropertyChangeCommand(d, "x", old_value=1, new_value=99)
    cmd.execute()
    assert d["x"] == 99


def test_property_change_undo_on_dict():
    """undo should restore the old value in a dict."""
    d: dict[str, int] = {"x": 1}
    cmd = PropertyChangeCommand(d, "x", old_value=1, new_value=99)
    cmd.execute()
    cmd.undo()
    assert d["x"] == 1


def test_property_change_auto_description():
    """Auto description should mention the property name."""
    target = _SimpleTarget()
    cmd = PropertyChangeCommand(target, "value", old_value=0, new_value=1)
    assert "value" in cmd.description


# ---------------------------------------------------------------------------
# DictChangeCommand
# ---------------------------------------------------------------------------


def test_dict_change_execute_add():
    """execute should add a new key."""
    d: dict[str, int] = {}
    cmd = DictChangeCommand(d, "k", old_value=None, new_value=7)
    cmd.execute()
    assert d["k"] == 7


def test_dict_change_undo_add():
    """undo should remove the key that was added."""
    d: dict[str, int] = {}
    cmd = DictChangeCommand(d, "k", old_value=None, new_value=7)
    cmd.execute()
    cmd.undo()
    assert "k" not in d


def test_dict_change_execute_remove():
    """execute should remove the key when new_value is None."""
    d: dict[str, int] = {"k": 5}
    cmd = DictChangeCommand(d, "k", old_value=5, new_value=None)
    cmd.execute()
    assert "k" not in d


def test_dict_change_undo_remove():
    """undo should restore the key that was removed."""
    d: dict[str, int] = {"k": 5}
    cmd = DictChangeCommand(d, "k", old_value=5, new_value=None)
    cmd.execute()
    cmd.undo()
    assert d["k"] == 5


def test_dict_change_execute_modify():
    """execute should overwrite the existing value."""
    d: dict[str, int] = {"k": 1}
    cmd = DictChangeCommand(d, "k", old_value=1, new_value=2)
    cmd.execute()
    assert d["k"] == 2


def test_dict_change_undo_modify():
    """undo should restore the previous value."""
    d: dict[str, int] = {"k": 1}
    cmd = DictChangeCommand(d, "k", old_value=1, new_value=2)
    cmd.execute()
    cmd.undo()
    assert d["k"] == 1


def test_dict_change_description_add():
    """Auto description for add should mention 'Add'."""
    cmd = DictChangeCommand({}, "k", old_value=None, new_value=1)
    assert "Add" in cmd.description


def test_dict_change_description_remove():
    """Auto description for remove should mention 'Remove'."""
    cmd = DictChangeCommand({"k": 1}, "k", old_value=1, new_value=None)
    assert "Remove" in cmd.description


def test_dict_change_description_modify():
    """Auto description for modify should mention 'Modify'."""
    cmd = DictChangeCommand({"k": 1}, "k", old_value=1, new_value=2)
    assert "Modify" in cmd.description


# ---------------------------------------------------------------------------
# ListChangeCommand
# ---------------------------------------------------------------------------


def test_list_change_execute_insert():
    """execute should insert item at given index."""
    lst = [1, 3]
    cmd = ListChangeCommand(lst, 1, old_item=None, new_item=2)
    cmd.execute()
    assert lst == [1, 2, 3]


def test_list_change_undo_insert():
    """undo should remove the inserted item."""
    lst = [1, 3]
    cmd = ListChangeCommand(lst, 1, old_item=None, new_item=2)
    cmd.execute()
    cmd.undo()
    assert lst == [1, 3]


def test_list_change_execute_remove():
    """execute should remove item at given index."""
    lst = [1, 2, 3]
    cmd = ListChangeCommand(lst, 1, old_item=2, new_item=None)
    cmd.execute()
    assert lst == [1, 3]


def test_list_change_undo_remove():
    """undo should restore the removed item."""
    lst = [1, 2, 3]
    cmd = ListChangeCommand(lst, 1, old_item=2, new_item=None)
    cmd.execute()
    cmd.undo()
    assert lst == [1, 2, 3]


def test_list_change_execute_modify():
    """execute should replace item at given index."""
    lst = [1, 2, 3]
    cmd = ListChangeCommand(lst, 1, old_item=2, new_item=99)
    cmd.execute()
    assert lst[1] == 99


def test_list_change_undo_modify():
    """undo should restore previous item at given index."""
    lst = [1, 2, 3]
    cmd = ListChangeCommand(lst, 1, old_item=2, new_item=99)
    cmd.execute()
    cmd.undo()
    assert lst[1] == 2


def test_list_change_remove_out_of_bounds_noop():
    """execute to remove item at out-of-bounds index should be a no-op."""
    lst = [1, 2]
    cmd = ListChangeCommand(lst, 5, old_item=99, new_item=None)
    cmd.execute()
    assert lst == [1, 2]


def test_list_change_description_insert():
    """Auto description for insert should mention index."""
    cmd = ListChangeCommand([], 3, old_item=None, new_item=1)
    assert "3" in cmd.description


def test_list_change_description_remove():
    """Auto description for remove should mention 'Remove'."""
    cmd = ListChangeCommand([1], 0, old_item=1, new_item=None)
    assert "Remove" in cmd.description


# ---------------------------------------------------------------------------
# CompositeCommand
# ---------------------------------------------------------------------------


def test_composite_execute_all_in_order():
    """execute should call all sub-commands in order."""
    log: list[str] = []
    cmds: list[Command] = [_ConcreteCommand(log, f"cmd{i}") for i in range(3)]
    composite = CompositeCommand(cmds, "batch")
    composite.execute()
    assert log == ["execute", "execute", "execute"]


def test_composite_undo_reverse_order():
    """undo should call sub-commands in reverse order."""
    log: list[str] = []
    composite = CompositeCommand(
        [_ConcreteCommand(log, f"c{i}") for i in range(3)],
        "batch",
    )
    composite.execute()
    log.clear()
    composite.undo()
    assert log == ["undo", "undo", "undo"]


def test_composite_default_description():
    """Default description should be 'Multiple changes'."""
    c = CompositeCommand([])
    assert c.description == "Multiple changes"


# ---------------------------------------------------------------------------
# CallbackCommand
# ---------------------------------------------------------------------------


def test_callback_command_execute_calls_fn():
    """execute should call the execute function."""
    called: list[bool] = []
    cmd = CallbackCommand(lambda: called.append(True), lambda: None, "cb")
    cmd.execute()
    assert called == [True]


def test_callback_command_undo_calls_fn():
    """undo should call the undo function."""
    called: list[bool] = []
    cmd = CallbackCommand(lambda: None, lambda: called.append(True), "cb")
    cmd.undo()
    assert called == [True]


def test_callback_command_redo_calls_execute():
    """redo should call execute function (default behavior)."""
    log: list[str] = []
    cmd = CallbackCommand(lambda: log.append("exec"), lambda: log.append("undo"))
    cmd.redo()
    assert "exec" in log


# ---------------------------------------------------------------------------
# UndoRedoManager
# ---------------------------------------------------------------------------


@pytest.fixture
def manager(qapp: QApplication) -> UndoRedoManager:  # noqa: ARG001
    """Fresh UndoRedoManager per test."""
    return UndoRedoManager()


def test_manager_initial_state(manager: UndoRedoManager):
    """Initial manager should have empty stacks."""
    assert not manager.can_undo()
    assert not manager.can_redo()
    assert manager.undo_count() == 0
    assert manager.redo_count() == 0


def test_manager_execute_command(manager: UndoRedoManager):
    """Executing a command makes undo available."""
    log: list[str] = []
    manager.execute(_ConcreteCommand(log))
    assert manager.can_undo()
    assert not manager.can_redo()
    assert manager.undo_count() == 1


def test_manager_undo_restores_state(manager: UndoRedoManager):
    """Undo should reverse the command and make redo available."""
    d: dict[str, int] = {"x": 1}
    cmd = DictChangeCommand(d, "x", old_value=1, new_value=42)
    manager.execute(cmd)
    assert d["x"] == 42

    result = manager.undo()
    assert result is True
    assert d["x"] == 1
    assert manager.can_redo()
    assert not manager.can_undo()


def test_manager_redo_reapplies_command(manager: UndoRedoManager):
    """Redo should reapply the undone command."""
    d: dict[str, int] = {"x": 1}
    manager.execute(DictChangeCommand(d, "x", old_value=1, new_value=42))
    manager.undo()
    result = manager.redo()
    assert result is True
    assert d["x"] == 42


def test_manager_undo_returns_false_when_empty(manager: UndoRedoManager):
    """undo on empty stack returns False."""
    assert manager.undo() is False


def test_manager_redo_returns_false_when_empty(manager: UndoRedoManager):
    """redo on empty stack returns False."""
    assert manager.redo() is False


def test_manager_execute_clears_redo_stack(manager: UndoRedoManager):
    """Executing a new command should clear the redo stack."""
    log: list[str] = []
    manager.execute(_ConcreteCommand(log))
    manager.undo()
    assert manager.can_redo()
    manager.execute(_ConcreteCommand(log))
    assert not manager.can_redo()


def test_manager_clear(manager: UndoRedoManager):
    """clear should empty both stacks."""
    log: list[str] = []
    manager.execute(_ConcreteCommand(log))
    manager.clear()
    assert not manager.can_undo()
    assert not manager.can_redo()


def test_manager_get_undo_description(manager: UndoRedoManager):
    """get_undo_description should return last command description."""
    log: list[str] = []
    manager.execute(_ConcreteCommand(log, "my command"))
    assert manager.get_undo_description() == "my command"


def test_manager_get_redo_description(manager: UndoRedoManager):
    """get_redo_description should return description after undo."""
    log: list[str] = []
    manager.execute(_ConcreteCommand(log, "x"))
    manager.undo()
    assert manager.get_redo_description() == "x"


def test_manager_get_undo_description_empty(manager: UndoRedoManager):
    """get_undo_description returns None when stack is empty."""
    assert manager.get_undo_description() is None


def test_manager_get_redo_description_empty(manager: UndoRedoManager):
    """get_redo_description returns None when stack is empty."""
    assert manager.get_redo_description() is None


def test_manager_get_undo_history(manager: UndoRedoManager):
    """get_undo_history should return descriptions most-recent-first."""
    log: list[str] = []
    manager.execute(_ConcreteCommand(log, "first"))
    manager.execute(_ConcreteCommand(log, "second"))
    history = manager.get_undo_history()
    assert history[0] == "second"
    assert history[1] == "first"


def test_manager_get_redo_history(manager: UndoRedoManager):
    """get_redo_history should list redoable commands."""
    log: list[str] = []
    manager.execute(_ConcreteCommand(log, "a"))
    manager.execute(_ConcreteCommand(log, "b"))
    manager.undo()
    manager.undo()
    history = manager.get_redo_history()
    assert len(history) == 2


def test_manager_status(manager: UndoRedoManager):
    """get_status should return a complete status dict."""
    status = manager.get_status()
    assert "undo_count" in status
    assert "redo_count" in status
    assert "max_history" in status
    assert "next_undo" in status
    assert "next_redo" in status


def test_manager_set_max_history(manager: UndoRedoManager):
    """set_max_history should update the maxlen of deques."""
    log: list[str] = []
    for i in range(10):
        manager.execute(_ConcreteCommand(log, f"cmd{i}"))
    manager.set_max_history(5)
    assert manager.undo_count() <= 5
    assert manager.max_history == 5


# ---------------------------------------------------------------------------
# ConfigurationUndoManager
# ---------------------------------------------------------------------------


@pytest.fixture
def cfg_manager(qapp: QApplication) -> ConfigurationUndoManager:  # noqa: ARG001
    """Fresh ConfigurationUndoManager per test."""
    return ConfigurationUndoManager()


def test_cfg_manager_initial_save_point(cfg_manager: ConfigurationUndoManager):
    """Initially there should be no unsaved changes (indices match)."""
    cfg_manager.set_save_point()
    assert cfg_manager.is_at_save_point()
    assert not cfg_manager.has_unsaved_changes()


def test_cfg_manager_has_unsaved_after_execute(cfg_manager: ConfigurationUndoManager):
    """has_unsaved_changes should be True after executing a command."""
    cfg_manager.set_save_point()
    log: list[str] = []
    cfg_manager.execute(_ConcreteCommand(log))
    assert cfg_manager.has_unsaved_changes()


def test_cfg_manager_snapshot_create_restore(cfg_manager: ConfigurationUndoManager):
    """Create snapshot then restore should produce a deep copy."""
    original = {"a": 1}
    cfg_manager.create_snapshot("snap1", original)
    original["a"] = 99  # mutate original

    restored = cfg_manager.restore_snapshot("snap1")
    assert restored == {"a": 1}  # snapshot was taken before mutation


def test_cfg_manager_restore_missing_snapshot(cfg_manager: ConfigurationUndoManager):
    """restore_snapshot for unknown name returns None."""
    assert cfg_manager.restore_snapshot("nonexistent") is None


def test_cfg_manager_delete_snapshot(cfg_manager: ConfigurationUndoManager):
    """delete_snapshot should remove the snapshot."""
    cfg_manager.create_snapshot("s", {"x": 1})
    cfg_manager.delete_snapshot("s")
    assert cfg_manager.restore_snapshot("s") is None


def test_cfg_manager_track_config_change(cfg_manager: ConfigurationUndoManager):
    """track_config_change should apply and be undoable."""
    config: dict[str, int] = {"key": 1}
    cfg_manager.track_config_change(config, "key", 42)
    assert config["key"] == 42
    cfg_manager.undo()
    assert config["key"] == 1


def test_cfg_manager_track_list_insert(cfg_manager: ConfigurationUndoManager):
    """track_list_insert should insert and be undoable."""
    lst: list[int] = [1, 3]
    cfg_manager.track_list_insert(lst, 1, 2)
    assert lst == [1, 2, 3]
    cfg_manager.undo()
    assert lst == [1, 3]


def test_cfg_manager_track_list_remove(cfg_manager: ConfigurationUndoManager):
    """track_list_remove should remove and be undoable."""
    lst: list[int] = [1, 2, 3]
    cfg_manager.track_list_remove(lst, 1)
    assert lst == [1, 3]
    cfg_manager.undo()
    assert lst == [1, 2, 3]


def test_cfg_manager_track_list_remove_out_of_bounds(cfg_manager: ConfigurationUndoManager):
    """track_list_remove with out-of-bounds index should not modify list."""
    lst: list[int] = [1, 2]
    cfg_manager.track_list_remove(lst, 5)
    assert lst == [1, 2]
