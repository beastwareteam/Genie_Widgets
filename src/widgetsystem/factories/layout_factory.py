"""Layout Factory - reads config/layouts.json and provides layout definitions."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, TypedDict, cast


class LayoutEntry(TypedDict, total=False):
    """Type-safe layout entry configuration."""

    id: str
    name: str
    file: str


class LayoutConfig(TypedDict, total=False):
    """Type-safe layout configuration."""

    default_layout_id: str
    layouts: list[LayoutEntry]


@dataclass(frozen=True)
class LayoutDefinition:
    """Represents a layout definition with resolved file path."""

    layout_id: str
    name: str
    file_path: Path


class LayoutFactory:
    """Factory for loading and managing layout configurations."""

    def __init__(self, config_path: str | Path = "config") -> None:
        """Initialize LayoutFactory."""
        self.config_path = Path(config_path)
        self.layouts_file = self.config_path / "layouts.json"

    def list_layouts(self) -> list[LayoutDefinition]:
        """Load and parse all layouts from config."""
        if not self.layouts_file.exists():
            raise FileNotFoundError(f"Layout configuration file not found: {self.layouts_file}")

        try:
            with open(self.layouts_file, encoding="utf-8") as f:
                raw_data_temp: Any = json.load(f)

            if not isinstance(raw_data_temp, dict):
                return []
            raw_data = cast("dict[str, Any]", raw_data_temp)

            entries_raw: Any = raw_data.get("layouts", [])
            if not isinstance(entries_raw, list):
                return []
            entries: list[Any] = entries_raw

            layouts: list[LayoutDefinition] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue

                entry_dict = cast("dict[str, Any]", entry)
                layout_id: Any = entry_dict.get("id")
                name: Any = entry_dict.get("name")
                file_value: Any = entry_dict.get("file")

                if (
                    not isinstance(layout_id, str)
                    or not isinstance(name, str)
                    or not isinstance(file_value, str)
                ):
                    continue

                # Resolve file path - relative to workspace root
                file_path = Path(file_value)
                if not file_path.is_absolute():
                    file_path = (Path.cwd() / file_path).resolve()

                layouts.append(
                    LayoutDefinition(layout_id=layout_id, name=name, file_path=file_path),
                )

            return layouts
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to load layouts: {e}")
            return []

    def get_default_layout_id(self) -> str | None:
        """Get the default layout ID."""
        try:
            with open(self.layouts_file, encoding="utf-8") as f:
                raw_data_temp: Any = json.load(f)

            if not isinstance(raw_data_temp, dict):
                return None
            raw_data = cast("dict[str, Any]", raw_data_temp)

            default_id: Any = raw_data.get("default_layout_id")
            if isinstance(default_id, str):
                return default_id
            return None
        except (OSError, json.JSONDecodeError):
            return None
