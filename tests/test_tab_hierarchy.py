"""Tests for tab hierarchy validation and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from widgetsystem.core.tab_hierarchy import (
    TabHierarchyValidator,
    get_hierarchy_validator,
    reset_hierarchy_validator,
)


@dataclass
class DummyContainer:
    """Minimal stand-in for an enhanced tab widget."""

    name: str


def create_container(name: str) -> Any:
    """Create a container object compatible with the validator API."""
    return cast("Any", DummyContainer(name))


def test_validator_loads_default_config_on_exception(monkeypatch) -> None:
    """Test validator falls back to defaults when config loading fails."""

    class FailingFactory:
        """Factory stub that always fails."""

        @staticmethod
        def get_instance() -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "widgetsystem.factories.ui_dimensions_factory.UIDimensionsFactory",
        FailingFactory,
    )

    validator = TabHierarchyValidator()

    assert validator.max_depth == 2
    assert validator.auto_dissolve_empty_folders is True


def test_validator_uses_explicit_init_values() -> None:
    """Test explicit constructor arguments override config values."""
    validator = TabHierarchyValidator(max_depth=5, auto_dissolve=False)

    assert validator.max_depth == 5
    assert validator.auto_dissolve_empty_folders is False


def test_register_get_container_and_unregister() -> None:
    """Test registering and unregistering tabs updates both maps."""
    validator = TabHierarchyValidator(max_depth=4)
    container = create_container("main")

    validator.register_tab("tab_a", None, container)

    assert validator.get_container("tab_a") is container
    assert validator.get_nesting_depth("tab_a") == 0

    validator.unregister_tab("tab_a")

    assert validator.get_container("tab_a") is None
    assert validator.get_children("tab_a") == []


def test_validate_nesting_rejects_self_nesting() -> None:
    """Test self nesting is rejected."""
    validator = TabHierarchyValidator(max_depth=4)

    is_valid, message = validator.validate_nesting("tab_a", "tab_a")

    assert is_valid is False
    assert message == "Cannot nest a tab into itself"


def test_validate_nesting_rejects_circular_nesting() -> None:
    """Test circular nesting is rejected."""
    validator = TabHierarchyValidator(max_depth=5)
    container = create_container("main")
    validator.register_tab("root", None, container)
    validator.register_tab("child", "root", container)
    validator.register_tab("grandchild", "child", container)

    is_valid, message = validator.validate_nesting("root", "grandchild")

    assert is_valid is False
    assert "Circular nesting detected" in message


def test_validate_nesting_rejects_depth_overflow() -> None:
    """Test nesting beyond maximum depth is rejected."""
    validator = TabHierarchyValidator(max_depth=2)
    container = create_container("main")
    validator.register_tab("root", None, container)
    validator.register_tab("target", "root", container)
    validator.register_tab("source", None, container)
    validator.register_tab("source_child", "source", container)

    is_valid, message = validator.validate_nesting("source", "target")

    assert is_valid is False
    assert "Max nesting depth (2) exceeded" in message


def test_validate_nesting_accepts_valid_structure() -> None:
    """Test valid nesting returns success."""
    validator = TabHierarchyValidator(max_depth=4)
    container = create_container("main")
    validator.register_tab("root", None, container)
    validator.register_tab("target", "root", container)
    validator.register_tab("source", None, container)

    is_valid, message = validator.validate_nesting("source", "target")

    assert is_valid is True
    assert message == ""


def test_get_ancestor_chain_children_and_descendants() -> None:
    """Test ancestor, child, and descendant traversal."""
    validator = TabHierarchyValidator(max_depth=5)
    container = create_container("main")
    validator.register_tab("root", None, container)
    validator.register_tab("child_a", "root", container)
    validator.register_tab("child_b", "root", container)
    validator.register_tab("grandchild", "child_a", container)

    assert validator.get_ancestor_chain("grandchild") == ["child_a", "root"]
    assert validator.get_children("root") == ["child_a", "child_b"]
    assert validator.get_all_descendants("root") == ["child_a", "child_b", "grandchild"]


def test_get_depth_and_ancestor_chain_stop_on_corrupted_cycles() -> None:
    """Test traversal stops safely when parent data is corrupted."""
    validator = TabHierarchyValidator(max_depth=5)
    validator.__dict__["_parent_map"] = {"loop": "loop"}

    depth = validator.get_nesting_depth("loop")
    ancestors = validator.get_ancestor_chain("loop")

    assert depth == 101
    assert len(ancestors) == 101
    assert all(ancestor == "loop" for ancestor in ancestors)


def test_update_parent_and_subtree_depth() -> None:
    """Test updating parents changes subtree depth calculations."""
    validator = TabHierarchyValidator(max_depth=5)
    container = create_container("main")
    validator.register_tab("root", None, container)
    validator.register_tab("child", None, container)
    validator.register_tab("grandchild", "child", container)

    validator.update_parent("child", "root")

    assert validator.get_nesting_depth("grandchild") == 2
    assert validator.get_ancestor_chain("grandchild") == ["child", "root"]
    assert validator.get_all_descendants("root") == ["child", "grandchild"]


def test_should_dissolve_folder_and_can_nest_here() -> None:
    """Test dissolve and depth allowance helpers."""
    validator = TabHierarchyValidator(max_depth=3, auto_dissolve=True)
    container = create_container("main")
    validator.register_tab("folder", None, container)
    validator.register_tab("only_child", "folder", container)

    assert validator.should_dissolve_folder("folder") is True
    assert validator.can_nest_here(1) is True
    assert validator.can_nest_here(2) is False

    validator.register_tab("second_child", "folder", container)
    assert validator.should_dissolve_folder("folder") is False


def test_should_dissolve_folder_respects_disabled_flag() -> None:
    """Test dissolve helper respects disabled auto-dissolve configuration."""
    validator = TabHierarchyValidator(max_depth=3, auto_dissolve=False)
    container = create_container("main")
    validator.register_tab("folder", None, container)

    assert validator.should_dissolve_folder("folder") is False


def test_debug_dump_and_clear() -> None:
    """Test debug output reflects hierarchy state and clear resets it."""
    validator = TabHierarchyValidator(max_depth=4)
    container = create_container("main")
    validator.register_tab("root", None, container)
    validator.register_tab("child", "root", container)

    dump = validator.debug_dump()

    assert dump == {
        "parent_map": {"root": None, "child": "root"},
        "depths": {"root": 0, "child": 1},
    }

    validator.clear()

    assert validator.debug_dump() == {"parent_map": {}, "depths": {}}
    assert validator.get_container("root") is None


def test_global_validator_singleton_and_reset() -> None:
    """Test global validator accessor returns singleton and reset replaces it."""
    reset_hierarchy_validator()
    first = get_hierarchy_validator()
    second = get_hierarchy_validator()

    assert first is second

    reset_hierarchy_validator()
    third = get_hierarchy_validator()

    assert third is not first
    reset_hierarchy_validator()
