"""Test module for UI dimensions factory functionality."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from widgetsystem.factories.ui_dimensions_factory import (
    CloseButtonDimensions,
    UIDimensions,
    UIDimensionsFactory,
)

if TYPE_CHECKING:
    from pathlib import Path


def reset_factory_state() -> None:
    """Reset cached singleton state for deterministic tests."""
    UIDimensionsFactory._instance = None
    UIDimensionsFactory._dimensions = None


def test_get_instance_returns_singleton_for_same_factory_path(tmp_path: Path) -> None:
    """Test `get_instance()` returns the same singleton instance."""
    reset_factory_state()
    first = UIDimensionsFactory.get_instance(tmp_path)
    second = UIDimensionsFactory.get_instance(tmp_path / "other")

    assert first is second, "Expected singleton factory instance to be reused"
    reset_factory_state()


def test_load_returns_defaults_when_config_file_missing(tmp_path: Path) -> None:
    """Test `load()` returns default dimensions when config file is absent."""
    factory = UIDimensionsFactory(tmp_path)

    dimensions = factory.load()

    assert isinstance(dimensions, UIDimensions)
    assert dimensions.titlebar.collapsed_height == 3, "Expected default titlebar height"
    assert dimensions.tabs.close_button.size == 14, "Expected default close button size"


def test_load_reads_dimensions_from_layout_config(tmp_path: Path) -> None:
    """Test `load()` reads and parses values from `layout_config.json`."""
    config_file = tmp_path / "layout_config.json"
    config_file.write_text(
        json.dumps(
            {
                "titlebar": {
                    "collapsed_height": 8,
                    "collapsed_hit_height": 12,
                    "expanded_height": 44,
                    "animation_duration_ms": 250,
                },
                "toolbar": {
                    "margin": 1,
                    "padding": 2,
                    "spacing": 3,
                    "button_size": 30,
                },
                "tabs": {
                    "padding_vertical": 5,
                    "padding_horizontal": 6,
                    "margin_top": 7,
                    "margin_right": 8,
                    "margin_bottom": 9,
                    "margin_left": 10,
                    "border_radius": 11,
                    "font_size": 12,
                    "max_nesting_depth": 13,
                    "auto_dissolve_empty_folders": False,
                    "close_button": {
                        "size": 20,
                        "margin_top": 21,
                        "margin_right": 22,
                        "margin_bottom": 23,
                        "margin_left": 24,
                        "border_radius": 25,
                    },
                },
                "dock": {
                    "splitter_width": 14,
                    "title_bar_height": 15,
                },
                "window": {
                    "min_width": 1600,
                    "min_height": 900,
                    "default_width": 1920,
                    "default_height": 1080,
                },
            }
        ),
        encoding="utf-8",
    )
    factory = UIDimensionsFactory(tmp_path)

    dimensions = factory.load()

    assert dimensions.titlebar.collapsed_height == 8
    assert dimensions.titlebar.animation_duration_ms == 250
    assert dimensions.toolbar.button_size == 30
    assert dimensions.tabs.max_nesting_depth == 13
    assert dimensions.tabs.auto_dissolve_empty_folders is False
    assert dimensions.tabs.close_button.margin_left == 24
    assert dimensions.dock.title_bar_height == 15
    assert dimensions.window.default_height == 1080


def test_get_caches_loaded_dimensions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test `get()` loads only once and returns cached dimensions afterwards."""
    reset_factory_state()
    factory = UIDimensionsFactory(tmp_path)
    load_calls: list[str] = []
    expected = UIDimensions()

    def fake_load() -> UIDimensions:
        load_calls.append("called")
        return expected

    monkeypatch.setattr(factory, "load", fake_load)

    first = factory.get()
    second = factory.get()

    assert first is expected, "Expected first `get()` to return loaded dimensions"
    assert second is expected, "Expected cached dimensions to be reused"
    assert load_calls == ["called"], "Expected `load()` to be called exactly once"
    reset_factory_state()


def test_load_uses_default_close_button_when_missing(tmp_path: Path) -> None:
    """Test `load()` falls back to default close button dimensions."""
    config_file = tmp_path / "layout_config.json"
    config_file.write_text(
        json.dumps(
            {
                "tabs": {
                    "padding_vertical": 9,
                }
            }
        ),
        encoding="utf-8",
    )
    factory = UIDimensionsFactory(tmp_path)

    dimensions = factory.load()

    assert dimensions.tabs.padding_vertical == 9
    assert dimensions.tabs.close_button == CloseButtonDimensions()


def test_load_supports_empty_data_dictionary(tmp_path: Path) -> None:
    """Test `load()` supports an empty configuration dictionary."""
    config_file = tmp_path / "layout_config.json"
    config_file.write_text("{}", encoding="utf-8")
    factory = UIDimensionsFactory(tmp_path)

    dimensions = factory.load()

    assert dimensions == UIDimensions(), "Expected empty config to produce default dimensions"
