"""Test PanelFactory - Validates panel configuration functionality."""

import pytest

from widgetsystem.factories.panel_factory import PanelConfig


def test_panel_config_initialization():
    """Test the initialization of the PanelConfig dataclass."""
    panel_config = PanelConfig(
        id="panel1",
        name_key="panel.panel1.name",
        area="left",
        closable=True,
        movable=False,
        floatable=True,
        delete_on_close=False,
        dnd_enabled=True,
        responsive_hidden_at=["mobile", "tablet"],
    )
    assert panel_config.id == "panel1"
    assert panel_config.name_key == "panel.panel1.name"
    assert panel_config.area == "left"
    assert panel_config.closable is True
    assert panel_config.movable is False
    assert panel_config.floatable is True
    assert panel_config.delete_on_close is False
    assert panel_config.dnd_enabled is True
    assert panel_config.responsive_hidden_at == ["mobile", "tablet"]
    print("✅ PanelConfig initialization test passed.")


def test_panel_config_invalid_area():
    """Test PanelConfig with an invalid area."""
    with pytest.raises(ValueError) as excinfo:
        PanelConfig(id="panel2", name_key="panel.panel2.name", area="invalid_area")
    assert "Invalid area 'invalid_area'" in str(excinfo.value)
    print("✅ PanelConfig invalid area test passed.")
