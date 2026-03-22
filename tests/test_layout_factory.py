"""Test LayoutFactory - Validates layout configuration functionality."""

from pathlib import Path

import pytest

from widgetsystem.factories.layout_factory import LayoutFactory


def test_layout_factory_initialization():
    """Test the initialization of LayoutFactory."""
    factory = LayoutFactory(config_path="config")
    assert factory.config_path == Path("config")
    assert factory.layouts_file == Path("config/layouts.json")
    print("✅ LayoutFactory initialization test passed.")


def test_layout_factory_missing_file():
    """Test LayoutFactory with a missing layouts.json file."""
    factory = LayoutFactory(config_path="nonexistent_config")
    with pytest.raises(FileNotFoundError) as excinfo:
        factory.list_layouts()
    assert "Layout configuration file not found" in str(excinfo.value)
    print("✅ LayoutFactory missing file test passed.")
