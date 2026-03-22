"""i18n Factory - reads config/i18n.*.json and provides translation services."""

from collections.abc import Callable
import json
from pathlib import Path
from typing import Any, cast


class I18nFactory:
    """Factory for loading and managing internationalization (i18n) configurations."""

    SUPPORTED_LOCALES = {"de", "en"}

    def __init__(self, config_path: str | Path = "config", locale: str = "en") -> None:
        """Initialize I18nFactory."""
        if locale not in self.SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale '{locale}'. Supported: {self.SUPPORTED_LOCALES}")

        self.config_path = Path(config_path)
        self.locale = locale
        self._translations_cache: dict[str, Any] = {}
        self._load_locale(locale)

    def _load_locale(self, locale: str) -> None:
        """Load translations for a specific locale."""
        i18n_file = self.config_path / f"i18n.{locale}.json"

        if not i18n_file.exists():
            raise FileNotFoundError(f"i18n configuration file not found: {i18n_file}")

        with open(i18n_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError(f"i18n configuration for locale '{locale}' must be a JSON object")

        raw_data = cast("dict[str, Any]", raw_data_temp)
        self._translations_cache = raw_data

    def set_locale(self, locale: str) -> None:
        """Switch to a different locale."""
        if locale not in self.SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale '{locale}'. Supported: {self.SUPPORTED_LOCALES}")

        if locale != self.locale:
            self.locale = locale
            self._load_locale(locale)

    def get_locale(self) -> str:
        """Get the currently active locale."""
        return self.locale

    def translate(self, key: str, default: str | None = None, **kwargs: Any) -> str:
        """Translate a key to the current locale with optional interpolation."""
        result = self._get_nested_value(key, **kwargs)
        if result == key and default is not None:
            return default
        return result

    def _get_nested_value(self, key: str, **kwargs: Any) -> str:
        """Get a nested value from translations using dot notation."""
        # First, try direct key lookup (for flat JSON structure like {"menu.file": "File"})
        if key in self._translations_cache:
            value = self._translations_cache[key]
            if isinstance(value, str):
                return self._interpolate(value, **kwargs)

        # Fall back to nested traversal (for hierarchical JSON structure)
        keys = key.split(".")
        current: Any = self._translations_cache

        for k in keys:
            if isinstance(current, dict):
                current_dict: dict[str, Any] = cast("dict[str, Any]", current)
                if k in current_dict:
                    current = current_dict[k]
                else:
                    return key
            else:
                return key

        if isinstance(current, str):
            return self._interpolate(current, **kwargs)

        return key

    @staticmethod
    def _interpolate(text: str, **kwargs: Any) -> str:
        """Interpolate variables in a string."""
        result = text
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def t(self, key: str, default: str | None = None, **kwargs: Any) -> str:
        """Shorthand for translate()."""
        return self.translate(key, default=default, **kwargs)

    def get_translator(self) -> Callable[[str], str]:
        """Get a translator function for the current locale."""
        return lambda key: self.translate(key)

    def has_key(self, key: str) -> bool:
        """Check if a translation key exists."""
        # First, try direct key lookup (for flat JSON structure)
        if key in self._translations_cache:
            return isinstance(self._translations_cache[key], str)

        # Fall back to nested traversal (for hierarchical JSON structure)
        keys = key.split(".")
        current: Any = self._translations_cache

        for k in keys:
            if isinstance(current, dict):
                current_dict: dict[str, Any] = cast("dict[str, Any]", current)
                if k in current_dict:
                    current = current_dict[k]
                else:
                    return False
            else:
                return False

        return isinstance(current, str)

    def get_all_keys(self, prefix: str = "") -> list[str]:
        """Get all available translation keys (optionally filtered by prefix)."""
        keys: list[str] = []

        def collect_keys(obj: Any, path: str = "") -> None:
            if isinstance(obj, dict):
                obj_dict: dict[str, Any] = cast("dict[str, Any]", obj)
                for k, v in obj_dict.items():
                    new_path: str = f"{path}.{k}" if path else k

                    if isinstance(v, str):
                        if not prefix or new_path.startswith(prefix):
                            keys.append(new_path)
                    elif isinstance(v, dict):
                        collect_keys(v, new_path)

        collect_keys(self._translations_cache)
        return keys
