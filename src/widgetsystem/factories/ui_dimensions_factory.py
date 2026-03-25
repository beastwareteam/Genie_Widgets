"""UI Dimensions Factory - Loads UI dimension configuration from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TitlebarDimensions:
    collapsed_height: int = 3
    collapsed_hit_height: int = 6
    expanded_height: int = 36
    animation_duration_ms: int = 160


@dataclass
class ToolbarDimensions:
    margin: int = 0
    padding: int = 0
    spacing: int = 2
    button_size: int = 24


@dataclass
class CloseButtonDimensions:
    size: int = 14
    margin_top: int = 2
    margin_right: int = 2
    margin_bottom: int = 2
    margin_left: int = 2
    border_radius: int = 3


@dataclass
class TabsDimensions:
    padding_vertical: int = 2
    padding_horizontal: int = 4
    margin_top: int = 2
    margin_right: int = 1
    margin_bottom: int = 0
    margin_left: int = 2
    border_radius: int = 4
    font_size: int = 11
    max_nesting_depth: int = 2
    auto_dissolve_empty_folders: bool = True
    close_button: CloseButtonDimensions = field(default_factory=CloseButtonDimensions)


@dataclass
class DockDimensions:
    splitter_width: int = 2
    title_bar_height: int = 26


@dataclass
class WindowDimensions:
    min_width: int = 800
    min_height: int = 600
    default_width: int = 1200
    default_height: int = 800


@dataclass
class UIDimensions:
    titlebar: TitlebarDimensions = field(default_factory=TitlebarDimensions)
    toolbar: ToolbarDimensions = field(default_factory=ToolbarDimensions)
    tabs: TabsDimensions = field(default_factory=TabsDimensions)
    dock: DockDimensions = field(default_factory=DockDimensions)
    window: WindowDimensions = field(default_factory=WindowDimensions)


class UIDimensionsFactory:
    """Factory for loading UI dimension configuration."""

    _instance: UIDimensionsFactory | None = None
    _dimensions: UIDimensions | None = None

    def __init__(self, config_path: Path | str = "config") -> None:
        self._config_path = Path(config_path)

    @classmethod
    def get_instance(cls, config_path: Path | str = "config") -> UIDimensionsFactory:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    def load(self) -> UIDimensions:
        """Load UI dimensions from JSON file."""
        config_file = self._config_path / "layout_config.json"

        if not config_file.exists():
            return UIDimensions()

        with open(config_file, encoding="utf-8") as f:
            data = json.load(f)

        return self._parse(data)

    def get(self) -> UIDimensions:
        """Get cached dimensions or load them."""
        if UIDimensionsFactory._dimensions is None:
            UIDimensionsFactory._dimensions = self.load()
        return UIDimensionsFactory._dimensions

    def _parse(self, data: dict[str, Any]) -> UIDimensions:
        """Parse JSON data into UIDimensions."""
        titlebar_data = data.get("titlebar", {})
        toolbar_data = data.get("toolbar", {})
        tabs_data = data.get("tabs", {})
        dock_data = data.get("dock", {})
        window_data = data.get("window", {})

        close_btn_data = tabs_data.pop("close_button", {})
        close_button = CloseButtonDimensions(**close_btn_data) if close_btn_data else CloseButtonDimensions()

        return UIDimensions(
            titlebar=TitlebarDimensions(**titlebar_data),
            toolbar=ToolbarDimensions(**toolbar_data),
            tabs=TabsDimensions(**tabs_data, close_button=close_button),
            dock=DockDimensions(**dock_data),
            window=WindowDimensions(**window_data),
        )
