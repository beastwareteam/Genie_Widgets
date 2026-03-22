"""Test ListFactory - Validates list configuration functionality."""

from widgetsystem.factories.list_factory import ListItem


def test_list_item_initialization():
    """Test the initialization of the ListItem dataclass."""
    list_item = ListItem(
        id="item1",
        label_key="list.item1.label",
        content_type="text",
        content="Sample Content",
        editable=True,
        deletable=False,
        icon="icon.png",
        data={"key": "value"},
        children=[],
    )
    assert list_item.id == "item1"
    assert list_item.label_key == "list.item1.label"
    assert list_item.content_type == "text"
    assert list_item.content == "Sample Content"
    assert list_item.editable is True
    assert list_item.deletable is False
    assert list_item.icon == "icon.png"
    assert list_item.data == {"key": "value"}
    assert list_item.children == []
    print("✅ ListItem initialization test passed.")
