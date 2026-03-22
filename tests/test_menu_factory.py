"""Test MenuFactory - Validates menu configuration functionality."""

import pytest

from widgetsystem.factories.menu_factory import MenuItem


def test_menu_item_initialization():
    """Test the initialization of the MenuItem dataclass."""
    menu_item = MenuItem(
        id="item1",
        label_key="menu.item1.label",
        type="action",
        action="do_something",
        shortcut="Ctrl+S",
        visible=True,
        children=[],
    )
    assert menu_item.id == "item1"
    assert menu_item.label_key == "menu.item1.label"
    assert menu_item.type == "action"
    assert menu_item.action == "do_something"
    assert menu_item.shortcut == "Ctrl+S"
    assert menu_item.visible is True
    assert menu_item.children == []
    print("✅ MenuItem initialization test passed.")


def test_menu_item_invalid_type():
    """Test MenuItem with an invalid type."""
    with pytest.raises(ValueError) as excinfo:
        MenuItem(id="item2", type="invalid_type")
    assert "Invalid type 'invalid_type'" in str(excinfo.value)
    print("✅ MenuItem invalid type test passed.")
