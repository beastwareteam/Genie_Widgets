"""Unit tests for Chevron Menu module."""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from widgetsystem.factories.menu_factory import MenuItem
from widgetsystem.ui.chevron_menu import ChevronMenu, ChevronMenuBar




# Mark all tests in this module as isolated (exempt from global coverage requirements)
pytestmark = [pytest.mark.isolated, pytest.mark.usefixtures("qapp")]


@pytest.fixture
def qapp() -> QApplication:
    """Provide QApplication instance."""
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    assert isinstance(application, QApplication)
    return application


def test_chevron_menu_creation() -> None:
    """Test basic ChevronMenu creation."""
    menu = ChevronMenu("Test Menu")
    assert menu.title() == "Test Menu"
    assert menu.isEmpty()


def test_add_simple_action() -> None:
    """Test adding a simple action to menu."""
    menu = ChevronMenu("Test Menu")
    item = MenuItem(
        id="test_action",
        label_key="Test Action",
        type="action",
        action="test",
        shortcut="Ctrl+T",
    )

    menu.add_menu_item(item)

    # Check action was added
    actions = menu.actions()
    assert len(actions) == 1
    assert "Test Action" in actions[0].text()


def test_add_separator() -> None:
    """Test adding a separator."""
    menu = ChevronMenu("Test Menu")
    item = MenuItem(
        id="sep",
        label_key="",
        type="separator",
        action="",
        shortcut="",
    )

    menu.add_menu_item(item)

    actions = menu.actions()
    assert len(actions) == 1
    assert actions[0].isSeparator()


def test_submenu_with_children() -> None:
    """Test submenu with multiple children."""
    menu = ChevronMenu("Main Menu")
    item = MenuItem(
        id="submenu",
        label_key="Submenu",
        type="menu",
        action="",
        shortcut="",
        children=[
            MenuItem(
                id="child1",
                label_key="Child 1",
                type="action",
                action="child1",
                shortcut="",
            ),
            MenuItem(
                id="child2",
                label_key="Child 2",
                type="action",
                action="child2",
                shortcut="",
            ),
        ],
    )

    result = menu.add_menu_item(item)

    # Should return a submenu
    assert result is not None
    assert isinstance(result, ChevronMenu)

    # Main menu should have the submenu action
    actions = menu.actions()
    assert len(actions) == 1


def test_action_callback() -> None:
    """Test action callback mechanism."""
    menu = ChevronMenu("Test Menu")
    callback_called = []

    def test_callback(action_id: str) -> None:
        callback_called.append(action_id)

    item = MenuItem(
        id="callback_test",
        label_key="Callback Test",
        type="action",
        action="callback_test",
        shortcut="",
    )

    menu.add_menu_item(item, callback=test_callback)

    # Get the action and trigger it
    actions = menu.actions()
    assert len(actions) == 1
    actions[0].trigger()

    # Callback should have been called
    assert "callback_test" in callback_called


def test_hierarchy_with_separator() -> None:
    """Test hierarchical menu with separators."""
    menu = ChevronMenu("File Menu")
    items = [
        MenuItem(
            id="new",
            label_key="New",
            type="action",
            action="new",
            shortcut="Ctrl+N",
        ),
        MenuItem(
            id="open",
            label_key="Open",
            type="action",
            action="open",
            shortcut="Ctrl+O",
        ),
        MenuItem(
            id="sep1",
            label_key="",
            type="separator",
            action="",
            shortcut="",
        ),
        MenuItem(
            id="exit",
            label_key="Exit",
            type="action",
            action="exit",
            shortcut="Alt+F4",
        ),
    ]

    for item in items:
        menu.add_menu_item(item)

    actions = menu.actions()
    assert len(actions) == 4
    assert actions[2].isSeparator()


def test_chevron_menu_bar_creation() -> None:
    """Test ChevronMenuBar creation."""
    # Create with sample data instead of loading
    menus = [
        MenuItem(
            id="file",
            label_key="File",
            type="menu",
            action="",
            shortcut="",
            children=[
                MenuItem(
                    id="file_new",
                    label_key="New",
                    type="action",
                    action="new",
                    shortcut="Ctrl+N",
                ),
            ],
        ),
    ]
    config_path = Path(__file__).parent.parent / "config"
    from widgetsystem.factories.menu_factory import MenuFactory

    menu_factory = MenuFactory(config_path)
    menu_bar = ChevronMenuBar(menu_factory)

    # Create menus
    created_menus = menu_bar.create_menu_bar(menus=menus)
    assert len(created_menus) == 1
    assert isinstance(created_menus[0], ChevronMenu)


def test_nested_submenus() -> None:
    """Test deeply nested submenus."""
    menu = ChevronMenu("Main Menu")
    item = MenuItem(
        id="level1",
        label_key="Level 1",
        type="menu",
        action="",
        shortcut="",
        children=[
            MenuItem(
                id="level2",
                label_key="Level 2",
                type="menu",
                action="",
                shortcut="",
                children=[
                    MenuItem(
                        id="level3",
                        label_key="Level 3",
                        type="action",
                        action="level3",
                        shortcut="",
                    ),
                ],
            ),
        ],
    )

    result = menu.add_menu_item(item)

    assert result is not None
    # Level 1 menu should exist
    level1_actions = result.actions()
    assert len(level1_actions) >= 1


def test_action_triggered_signal() -> None:
    """Test action_triggered signal emission."""
    menu = ChevronMenu("Test Menu")
    signal_data = []

    def capture_signal(action_id: str) -> None:
        signal_data.append(action_id)

    menu.action_triggered.connect(capture_signal)

    item = MenuItem(
        id="test_signal",
        label_key="Test Signal",
        type="action",
        action="test",
        shortcut="",
    )

    menu.add_menu_item(item)
    actions = menu.actions()
    assert len(actions) == 1

    # Trigger the action
    actions[0].trigger()

    # Signal should have been emitted
    assert "test_signal" in signal_data


def test_action_with_empty_id() -> None:
    """Test action with no ID (should not emit signal)."""
    menu = ChevronMenu("Test Menu")
    signal_data = []

    def capture_signal(action_id: str) -> None:
        signal_data.append(action_id)

    menu.action_triggered.connect(capture_signal)

    # Add action directly (not through add_menu_item)
    action = menu.addAction("Test Action")
    action.setData(None)  # No ID

    # Trigger should not raise error
    action.trigger()

    # Signal should not be emitted because action_id is None
    assert len(signal_data) == 0


def test_chevron_menu_bar_get_menu() -> None:
    """Test retrieving menus from ChevronMenuBar."""
    config_path = Path(__file__).parent.parent / "config"

    from widgetsystem.factories.menu_factory import MenuFactory
    menu_factory = MenuFactory(config_path)

    menus = [
        MenuItem(
            id="file",
            label_key="File",
            type="menu",
            action="",
            shortcut="",
            children=[
                MenuItem(
                    id="file_new",
                    label_key="New",
                    type="action",
                    action="new",
                    shortcut="Ctrl+N",
                ),
            ],
        ),
    ]

    menu_bar = ChevronMenuBar(menu_factory)
    menu_bar.create_menu_bar(menus=menus)

    # Get existing menu
    file_menu = menu_bar.get_menu("file")
    assert file_menu is not None
    assert isinstance(file_menu, ChevronMenu)

    # Get nonexistent menu
    nonexistent = menu_bar.get_menu("nonexistent")
    assert nonexistent is None


def test_chevron_menu_bar_register_callback() -> None:
    """Test registering action callbacks in ChevronMenuBar."""
    config_path = Path(__file__).parent.parent / "config"

    from widgetsystem.factories.menu_factory import MenuFactory
    menu_factory = MenuFactory(config_path)

    menu_bar = ChevronMenuBar(menu_factory)

    called_ids: list[str] = []

    def test_callback(action_id: str) -> None:
        called_ids.append(action_id)

    # Register callback
    menu_bar.register_action_callback("test_action", test_callback)

    # Verify it was registered
    callbacks = menu_bar.__dict__["_action_callbacks"]
    assert "test_action" in callbacks
    assert callbacks["test_action"] is test_callback
    callbacks["test_action"]("test_action")
    assert called_ids == ["test_action"]


def test_multiple_menus_creation() -> None:
    """Test creating multiple menus from ChevronMenuBar."""
    config_path = Path(__file__).parent.parent / "config"

    from widgetsystem.factories.menu_factory import MenuFactory
    menu_factory = MenuFactory(config_path)

    menus = [
        MenuItem(
            id="file",
            label_key="File",
            type="menu",
            action="",
            shortcut="",
            children=[
                MenuItem(
                    id="file_new",
                    label_key="New",
                    type="action",
                    action="new",
                    shortcut="Ctrl+N",
                ),
            ],
        ),
        MenuItem(
            id="edit",
            label_key="Edit",
            type="menu",
            action="",
            shortcut="",
            children=[
                MenuItem(
                    id="edit_undo",
                    label_key="Undo",
                    type="action",
                    action="undo",
                    shortcut="Ctrl+Z",
                ),
            ],
        ),
        MenuItem(
            id="sep",
            label_key="",
            type="separator",
            action="",
            shortcut="",
        ),
    ]

    menu_bar = ChevronMenuBar(menu_factory)
    created_menus = menu_bar.create_menu_bar(menus=menus)

    # Should create 2 menus (separator is skipped)
    assert len(created_menus) == 2
    assert menu_bar.get_menu("file") is not None
    assert menu_bar.get_menu("edit") is not None
    assert menu_bar.get_menu("sep") is None  # Separator not added


def test_action_with_callback_and_signal() -> None:
    """Test action with both callback and signal."""
    menu = ChevronMenu("Test Menu")
    callback_data = []
    signal_data = []

    def test_callback(action_id: str) -> None:
        callback_data.append(action_id)

    def capture_signal(action_id: str) -> None:
        signal_data.append(action_id)

    menu.action_triggered.connect(capture_signal)

    item = MenuItem(
        id="dual_test",
        label_key="Dual Test",
        type="action",
        action="dual",
        shortcut="Ctrl+D",
    )

    menu.add_menu_item(item, callback=test_callback)
    actions = menu.actions()
    assert len(actions) == 1

    # Trigger the action
    actions[0].trigger()

    # Both callback and signal should have fired
    assert "dual_test" in callback_data
    assert "dual_test" in signal_data


def test_submenu_without_chevron_indicator() -> None:
    """Test submenu creation without chevron indicators."""
    menu = ChevronMenu("Main Menu")
    item = MenuItem(
        id="sub1",
        label_key="Submenu 1",
        type="action",  # type is action but has children
        action="",
        shortcut="",
        children=[
            MenuItem(
                id="sub1_child",
                label_key="Child 1",
                type="action",
                action="child1",
                shortcut="",
            ),
        ],
    )

    result = menu.add_menu_item(item)

    # Should still create a submenu
    assert result is not None
    assert isinstance(result, ChevronMenu)


def test_action_shortcut_applied() -> None:
    """Test that shortcuts are properly applied to actions."""
    menu = ChevronMenu("Test Menu")

    item = MenuItem(
        id="shortcut_test",
        label_key="Shortcut Test",
        type="action",
        action="shortcut",
        shortcut="Ctrl+Shift+S",
    )

    menu.add_menu_item(item)
    actions = menu.actions()
    assert len(actions) == 1
    assert actions[0].shortcut().toString() == "Ctrl+Shift+S"


def test_action_without_shortcut() -> None:
    """Test action without shortcut."""
    menu = ChevronMenu("Test Menu")

    item = MenuItem(
        id="no_shortcut",
        label_key="No Shortcut",
        type="action",
        action="nosshortcut",
        shortcut="",  # Empty shortcut
    )

    menu.add_menu_item(item)
    actions = menu.actions()
    assert len(actions) == 1
    # Shortcut should be empty
    assert actions[0].shortcut().toString() == ""


def test_submenu_when_add_menu_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test submenu branch when Qt does not return a menu action."""
    menu = ChevronMenu("Main Menu")

    captured: dict[str, ChevronMenu] = {}

    def fake_add_menu(self: ChevronMenu, submenu: ChevronMenu) -> None:
        del self
        captured["submenu"] = submenu

    monkeypatch.setattr(ChevronMenu, "addMenu", fake_add_menu)

    item = MenuItem(
        id="submenu_none",
        label_key="Submenu None",
        type="menu",
        children=[],
    )

    result = menu.add_menu_item(item)

    assert result is not None
    assert result.title() == "Submenu None"
    assert captured["submenu"].title() == "Submenu None"


def test_add_menu_item_unknown_type_returns_none() -> None:
    """Test fallback branch for unsupported item-like objects."""

    class UnknownItem:
        """Minimal item-like object for fallback coverage."""

        def __init__(self) -> None:
            self.type = "unknown"
            self.children: list[MenuItem] = []
            self.label_key = "Unknown"
            self.id = "unknown"
            self.shortcut = ""

    menu = ChevronMenu("Main Menu")

    result = menu.add_menu_item(UnknownItem())  # type: ignore[arg-type]

    assert result is None


def test_create_menu_bar_loads_from_factory_and_callback() -> None:
    """Test default factory loading path and callback wiring."""
    from widgetsystem.factories.menu_factory import MenuFactory

    callback_calls: list[str] = []

    def handle_action(action_id: str) -> None:
        callback_calls.append(action_id)

    config_path = Path(__file__).parent.parent / "config"
    menu_factory = MenuFactory(config_path)
    menu_bar = ChevronMenuBar(menu_factory)
    menus = [
        MenuItem(
            id="factory_menu",
            label_key="Factory",
            type="menu",
            children=[
                MenuItem(
                    id="factory_action",
                    label_key="Factory Action",
                    type="action",
                    action="factory_action",
                ),
            ],
        ),
    ]

    def fake_load_menus() -> list[MenuItem]:
        return menus

    menu_factory.load_menus = fake_load_menus

    created_menus = menu_bar.create_menu_bar(callback=handle_action)

    assert len(created_menus) == 1
    created_menus[0].actions()[0].trigger()
    assert callback_calls == ["factory_action", "factory_action"]
