"""QSS Factory - Generates stylesheets from templates and config."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from widgetsystem.factories.ui_dimensions_factory import UIDimensionsFactory


class QSSFactory:
    """Factory for generating QSS stylesheets with config values."""

    def __init__(self, themes_path: Path | str = "themes", config_path: Path | str = "config") -> None:
        self._themes_path = Path(themes_path)
        self._config_path = Path(config_path)
        self._dims = UIDimensionsFactory.get_instance(config_path).get()

    def load_theme(self, theme_name: str) -> str:
        """Load and process a theme QSS file."""
        qss_file = self._themes_path / f"{theme_name}.qss"
        if not qss_file.exists():
            return ""

        with open(qss_file, encoding="utf-8") as f:
            qss = f.read()

        return self._substitute_variables(qss)

    def _substitute_variables(self, qss: str) -> str:
        """Substitute config variables in QSS."""
        replacements = self._get_replacements()

        for var, value in replacements.items():
            qss = qss.replace(f"${{{var}}}", str(value))
            qss = qss.replace(f"$({var})", str(value))

        return qss

    def _get_replacements(self) -> dict[str, Any]:
        """Get all config values as replacement dict."""
        tabs = self._dims.tabs
        cb = tabs.close_button

        return {
            "tabs.padding_vertical": tabs.padding_vertical,
            "tabs.padding_horizontal": tabs.padding_horizontal,
            "tabs.margin_top": tabs.margin_top,
            "tabs.margin_right": tabs.margin_right,
            "tabs.margin_bottom": tabs.margin_bottom,
            "tabs.margin_left": tabs.margin_left,
            "tabs.border_radius": tabs.border_radius,
            "tabs.font_size": tabs.font_size,
            "tabs.close_button.size": cb.size,
            "tabs.close_button.margin_top": cb.margin_top,
            "tabs.close_button.margin_right": cb.margin_right,
            "tabs.close_button.margin_bottom": cb.margin_bottom,
            "tabs.close_button.margin_left": cb.margin_left,
            "tabs.close_button.border_radius": cb.border_radius,
            "toolbar.margin": self._dims.toolbar.margin,
            "toolbar.padding": self._dims.toolbar.padding,
            "toolbar.spacing": self._dims.toolbar.spacing,
            "dock.splitter_width": self._dims.dock.splitter_width,
            "dock.title_bar_height": self._dims.dock.title_bar_height,
        }
