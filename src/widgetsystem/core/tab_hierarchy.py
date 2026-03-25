"""Tab hierarchy validation and utilities.

Provides safety checks and utilities for nested tab operations:
- Circular nesting prevention
- Maximum depth enforcement
- Ancestor chain traversal
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from widgetsystem.ui.enhanced_tab_widget import EnhancedTabWidget


class TabHierarchyValidator:
    """Validates tab hierarchy operations to prevent invalid states.

    Enforces:
    - No circular nesting (A -> B -> A)
    - Maximum nesting depth (default: 3)
    - Valid parent-child relationships
    """

    DEFAULT_MAX_DEPTH = 3

    def __init__(self, max_depth: int = DEFAULT_MAX_DEPTH) -> None:
        """Initialize validator.

        Args:
            max_depth: Maximum allowed nesting depth (1 = no nesting)
        """
        self.max_depth = max_depth
        # Registry: tab_id -> parent_tab_id (None if root)
        self._parent_map: dict[str, str | None] = {}
        # Registry: tab_id -> EnhancedTabWidget containing it
        self._container_map: dict[str, EnhancedTabWidget] = {}

    def register_tab(
        self,
        tab_id: str,
        parent_id: str | None,
        container: EnhancedTabWidget,
    ) -> None:
        """Register a tab in the hierarchy.

        Args:
            tab_id: Unique tab identifier
            parent_id: Parent tab ID (None if root level)
            container: The EnhancedTabWidget containing this tab
        """
        self._parent_map[tab_id] = parent_id
        self._container_map[tab_id] = container

    def unregister_tab(self, tab_id: str) -> None:
        """Remove a tab from the hierarchy registry.

        Args:
            tab_id: Tab identifier to remove
        """
        self._parent_map.pop(tab_id, None)
        self._container_map.pop(tab_id, None)

    def validate_nesting(self, source_id: str, target_id: str) -> tuple[bool, str]:
        """Check if nesting source into target is valid.

        Args:
            source_id: Tab to be nested
            target_id: Tab to nest into

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Self-nesting check
        if source_id == target_id:
            return False, "Cannot nest a tab into itself"

        # Circular nesting check: target cannot be a descendant of source
        if self._is_descendant_of(target_id, source_id):
            return False, f"Circular nesting detected: {target_id} is inside {source_id}"

        # Depth check: calculate resulting depth
        target_depth = self.get_nesting_depth(target_id)
        source_subtree_depth = self._get_subtree_depth(source_id)
        resulting_depth = target_depth + 1 + source_subtree_depth

        if resulting_depth > self.max_depth:
            return False, f"Max nesting depth ({self.max_depth}) exceeded: would be {resulting_depth}"

        return True, ""

    def get_nesting_depth(self, tab_id: str) -> int:
        """Get the nesting depth of a tab (0 = root level).

        Args:
            tab_id: Tab identifier

        Returns:
            Depth level (0 for root, 1 for first nesting level, etc.)
        """
        depth = 0
        current = tab_id

        while current in self._parent_map:
            parent = self._parent_map[current]
            if parent is None:
                break
            depth += 1
            current = parent

            # Safety: prevent infinite loop if data is corrupted
            if depth > 100:
                break

        return depth

    def get_ancestor_chain(self, tab_id: str) -> list[str]:
        """Get all ancestor tab IDs from immediate parent to root.

        Args:
            tab_id: Tab identifier

        Returns:
            List of ancestor IDs, nearest first (empty if root)
        """
        ancestors = []
        current = tab_id

        while current in self._parent_map:
            parent = self._parent_map[current]
            if parent is None:
                break
            ancestors.append(parent)
            current = parent

            # Safety: prevent infinite loop
            if len(ancestors) > 100:
                break

        return ancestors

    def get_children(self, tab_id: str) -> list[str]:
        """Get immediate children of a tab.

        Args:
            tab_id: Parent tab identifier

        Returns:
            List of child tab IDs
        """
        return [
            child_id
            for child_id, parent_id in self._parent_map.items()
            if parent_id == tab_id
        ]

    def get_all_descendants(self, tab_id: str) -> list[str]:
        """Get all descendants (children, grandchildren, etc.) of a tab.

        Args:
            tab_id: Root tab identifier

        Returns:
            List of all descendant tab IDs
        """
        descendants = []
        to_process = self.get_children(tab_id)

        while to_process:
            child = to_process.pop(0)
            descendants.append(child)
            to_process.extend(self.get_children(child))

        return descendants

    def _is_descendant_of(self, potential_descendant: str, potential_ancestor: str) -> bool:
        """Check if one tab is a descendant of another.

        Args:
            potential_descendant: Tab that might be inside ancestor
            potential_ancestor: Tab that might contain descendant

        Returns:
            True if descendant is inside ancestor's subtree
        """
        ancestors = self.get_ancestor_chain(potential_descendant)
        return potential_ancestor in ancestors

    def _get_subtree_depth(self, tab_id: str) -> int:
        """Get the maximum depth of the subtree rooted at tab_id.

        Args:
            tab_id: Root of subtree

        Returns:
            Maximum depth of descendants (0 if no children)
        """
        children = self.get_children(tab_id)
        if not children:
            return 0

        max_child_depth = 0
        for child in children:
            child_depth = 1 + self._get_subtree_depth(child)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def update_parent(self, tab_id: str, new_parent_id: str | None) -> None:
        """Update a tab's parent after nesting/unnesting.

        Args:
            tab_id: Tab whose parent changed
            new_parent_id: New parent ID (None if moved to root)
        """
        self._parent_map[tab_id] = new_parent_id

    def clear(self) -> None:
        """Clear all registry data."""
        self._parent_map.clear()
        self._container_map.clear()

    def get_container(self, tab_id: str) -> EnhancedTabWidget | None:
        """Get the container widget for a tab.

        Args:
            tab_id: Tab identifier

        Returns:
            EnhancedTabWidget containing the tab, or None
        """
        return self._container_map.get(tab_id)

    def debug_dump(self) -> dict:
        """Return debug information about the hierarchy.

        Returns:
            Dict with parent_map and depth info
        """
        return {
            "parent_map": dict(self._parent_map),
            "depths": {
                tab_id: self.get_nesting_depth(tab_id)
                for tab_id in self._parent_map
            },
        }


# Global singleton for easy access
_global_validator: TabHierarchyValidator | None = None


def get_hierarchy_validator() -> TabHierarchyValidator:
    """Get the global tab hierarchy validator instance.

    Returns:
        The singleton TabHierarchyValidator
    """
    global _global_validator
    if _global_validator is None:
        _global_validator = TabHierarchyValidator()
    return _global_validator


def reset_hierarchy_validator() -> None:
    """Reset the global validator (for testing)."""
    global _global_validator
    if _global_validator is not None:
        _global_validator.clear()
    _global_validator = None
