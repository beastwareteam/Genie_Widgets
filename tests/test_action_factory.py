"""Tests for ActionFactory."""

import pytest
from pathlib import Path

from widgetsystem.factories.action_factory import ActionConfig, ActionFactory


class TestActionConfig:
    """Tests for ActionConfig dataclass."""

    def test_valid_action_config(self) -> None:
        """Test creating a valid action config."""
        config = ActionConfig(
            id="test_action",
            label_key="action.test",
            action="test",
        )
        assert config.id == "test_action"
        assert config.label_key == "action.test"
        assert config.action == "test"
        assert config.enabled is True
        assert config.category == "general"

    def test_action_config_with_all_fields(self) -> None:
        """Test creating action config with all fields."""
        config = ActionConfig(
            id="full_action",
            label_key="action.full",
            action="full_action",
            tooltip_key="tooltip.full",
            status_tip_key="status.full",
            icon="save",
            shortcut="Ctrl+F",
            enabled=False,
            checkable=True,
            visible=False,
            category="file",
        )
        assert config.tooltip_key == "tooltip.full"
        assert config.icon == "save"
        assert config.shortcut == "Ctrl+F"
        assert config.enabled is False
        assert config.checkable is True
        assert config.visible is False
        assert config.category == "file"

    def test_action_config_requires_id(self) -> None:
        """Test that empty id raises error."""
        with pytest.raises(ValueError, match="'id' must be a non-empty string"):
            ActionConfig(id="", label_key="test", action="test")

    def test_action_config_requires_action(self) -> None:
        """Test that empty action raises error."""
        with pytest.raises(ValueError, match="must have an 'action' value"):
            ActionConfig(id="test", label_key="test", action="")


class TestActionFactory:
    """Tests for ActionFactory."""

    def test_load_actions_from_config(self) -> None:
        """Test loading actions from config file."""
        factory = ActionFactory(Path("config"))
        actions = factory.load_actions()

        assert len(actions) > 0
        assert any(a.id == "action_save_layout" for a in actions)

    def test_get_action_config_by_id(self) -> None:
        """Test getting action by ID."""
        factory = ActionFactory(Path("config"))
        factory.load_actions()

        config = factory.get_action_config("action_save_layout")
        assert config is not None
        assert config.action == "save_layout"
        assert config.shortcut == "Ctrl+S"

    def test_get_nonexistent_action_returns_none(self) -> None:
        """Test getting nonexistent action returns None."""
        factory = ActionFactory(Path("config"))
        factory.load_actions()

        config = factory.get_action_config("nonexistent")
        assert config is None

    def test_get_actions_by_category(self) -> None:
        """Test filtering actions by category."""
        factory = ActionFactory(Path("config"))
        factory.load_actions()

        file_actions = factory.get_actions_by_category("file")
        assert len(file_actions) >= 3  # save, load, reset

        dock_actions = factory.get_actions_by_category("dock")
        assert len(dock_actions) >= 4  # new, float, dock, close

    def test_list_shortcuts(self) -> None:
        """Test listing all shortcuts."""
        factory = ActionFactory(Path("config"))
        factory.load_actions()

        shortcuts = factory.list_shortcuts()
        assert "action_save_layout" in shortcuts
        assert shortcuts["action_save_layout"] == "Ctrl+S"

    def test_list_categories(self) -> None:
        """Test listing all categories."""
        factory = ActionFactory(Path("config"))
        factory.load_actions()

        categories = factory.list_categories()
        assert "file" in categories
        assert "dock" in categories
        assert "tools" in categories

    def test_missing_config_file_returns_empty_list(self) -> None:
        """Test that missing config file returns empty list."""
        factory = ActionFactory(Path("nonexistent"))
        actions = factory.load_actions()
        assert actions == []
