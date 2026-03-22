"""Test TabsFactory - Validates tab configuration functionality."""

from widgetsystem.factories.tabs_factory import Tab


def test_tab_initialization():
    """Test the initialization of the Tab dataclass."""
    tab = Tab(
        id="tab1",
        title_key="tab.tab1.title",
        component="component1",
        closable=False,
        active=True,
        children=[],
    )
    assert tab.id == "tab1"
    assert tab.title_key == "tab.tab1.title"
    assert tab.component == "component1"
    assert tab.closable is False
    assert tab.active is True
    assert tab.children == []
    print("✅ Tab initialization test passed.")
