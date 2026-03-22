"""Extended tests for I18nFactory - Coverage improvement tests."""

from pathlib import Path

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory


class TestI18nFactoryBasics:
    """Test basic I18nFactory functionality."""

    def test_initialization_with_config_path(self) -> None:
        """Test initialization with different config path types."""
        # Test with string path
        factory = I18nFactory(config_path="config", locale="en")
        assert factory.locale == "en"
        assert isinstance(factory.config_path, Path)
        assert factory.config_path == Path("config")

        # Test with Path object
        factory2 = I18nFactory(config_path=Path("config"), locale="de")
        assert factory2.locale == "de"
        assert factory2.config_path == Path("config")

    def test_initialization_with_invalid_locale(self) -> None:
        """Test initialization with unsupported locale."""
        with pytest.raises(ValueError, match="Unsupported locale"):
            I18nFactory(config_path="config", locale="invalid")


class TestTranslation:
    """Test translation functionality."""

    def test_translate_existing_key(self) -> None:
        """Test translating an existing key."""
        factory = I18nFactory(config_path="config", locale="en")
        # The actual translations are in flat dot notation
        result = factory.translate("menu.view")
        assert result == "View"

    def test_translate_nested_key(self) -> None:
        """Test translating a nested key."""
        factory = I18nFactory(config_path="config", locale="en")
        # Using existing keys from i18n.en.json
        result = factory.translate("menu.tools.config")
        assert result == "Configuration"

    def test_translate_missing_key_returns_key(self) -> None:
        """Test that missing keys return the key itself."""
        factory = I18nFactory(config_path="config", locale="en")
        result = factory.translate("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translate_with_default(self) -> None:
        """Test translate with default value for missing key."""
        factory = I18nFactory(config_path="config", locale="en")
        result = factory.translate("missing.key", default="Default Value")
        assert result == "Default Value"

    def test_translate_existing_key_ignores_default(self) -> None:
        """Test that existing keys ignore default value."""
        factory = I18nFactory(config_path="config", locale="en")
        result = factory.translate("menu.view", default="Ignored")
        assert result == "View"  # Should return actual value, not default

    def test_translate_with_interpolation(self) -> None:
        """Test translate with variable interpolation."""
        factory = I18nFactory(config_path="config", locale="en")
        # Using actual key that has interpolation
        result = factory.translate("message.layout_loaded", name="TestLayout")
        assert result == "Layout loaded: TestLayout"

    def test_translate_with_multiple_interpolations(self) -> None:
        """Test translate with multiple variable interpolations."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {
            "message": "{user} sent {count} messages at {time}",
        }

        result = factory.translate("message", user="Alice", count=10, time="3:00 PM")
        assert result == "Alice sent 10 messages at 3:00 PM"


class TestGetNestedValue:
    """Test _get_nested_value method."""

    def test_get_nested_value_simple(self) -> None:
        """Test getting a simple nested value."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {"key": "value"}
        result = factory._get_nested_value("key")
        assert result == "value"

    def test_get_nested_value_deep(self) -> None:
        """Test getting a deeply nested value."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {
            "level1": {"level2": {"level3": "deep value"}},
        }
        result = factory._get_nested_value("level1.level2.level3")
        assert result == "deep value"

    def test_get_nested_value_missing_returns_key(self) -> None:
        """Test that missing nested keys return the key itself."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {"key": "value"}
        result = factory._get_nested_value("missing.nested.key")
        assert result == "missing.nested.key"

    def test_get_nested_value_partial_path(self) -> None:
        """Test getting nested value with partial path mismatch."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {"level1": {"level2": "value"}}
        result = factory._get_nested_value("level1.level2.level3")
        assert result == "level1.level2.level3"  # Path doesn't exist

    def test_get_nested_value_non_dict_intermediate(self) -> None:
        """Test nested value access when intermediate value is not a dict."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {"level1": "string value"}
        result = factory._get_nested_value("level1.level2")
        assert result == "level1.level2"  # Can't traverse further

    def test_get_nested_value_with_interpolation(self) -> None:
        """Test nested value access with interpolation."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {
            "messages": {"greeting": "Hello {name}"},
        }
        result = factory._get_nested_value("messages.greeting", name="Bob")
        assert result == "Hello Bob"


class TestInterpolation:
    """Test _interpolate method."""

    def test_interpolate_single_variable(self) -> None:
        """Test interpolating a single variable."""
        result = I18nFactory._interpolate("Hello {name}", name="World")
        assert result == "Hello World"

    def test_interpolate_multiple_variables(self) -> None:
        """Test interpolating multiple variables."""
        result = I18nFactory._interpolate(
            "{greeting} {name}!",
            greeting="Hello",
            name="Alice",
        )
        assert result == "Hello Alice!"

    def test_interpolate_no_variables(self) -> None:
        """Test interpolating text without variables."""
        result = I18nFactory._interpolate("Plain text")
        assert result == "Plain text"

    def test_interpolate_missing_variable(self) -> None:
        """Test interpolating with missing variable (should leave placeholder)."""
        result = I18nFactory._interpolate("Hello {name}", other="value")
        assert result == "Hello {name}"  # Placeholder remains


class TestShorthandMethods:
    """Test shorthand and helper methods."""

    def test_t_shorthand(self) -> None:
        """Test t() as shorthand for translate()."""
        factory = I18nFactory(config_path="config", locale="en")
        result1 = factory.t("menu.view")
        result2 = factory.translate("menu.view")
        assert result1 == result2

    def test_t_with_default(self) -> None:
        """Test t() with default value."""
        factory = I18nFactory(config_path="config", locale="en")
        result = factory.t("missing.key", default="Default")
        assert result == "Default"

    def test_t_with_kwargs(self) -> None:
        """Test t() with interpolation kwargs."""
        factory = I18nFactory(config_path="config", locale="en")
        result = factory.t("message.layout_loaded", name="Charlie")
        assert result == "Layout loaded: Charlie"

    def test_get_translator(self) -> None:
        """Test getting a translator function."""
        factory = I18nFactory(config_path="config", locale="en")
        translator = factory.get_translator()
        result = translator("menu.view")
        assert result == "View"


class TestKeyChecking:
    """Test key existence checking."""

    def test_has_key_existing(self) -> None:
        """Test has_key with existing keys."""
        factory = I18nFactory(config_path="config", locale="en")
        assert factory.has_key("menu.view") is True

    def test_has_key_missing(self) -> None:
        """Test has_key with missing keys."""
        factory = I18nFactory(config_path="config", locale="en")
        assert factory.has_key("nonexistent.key") is False

    def test_has_key_nested(self) -> None:
        """Test has_key with nested keys."""
        factory = I18nFactory(config_path="config", locale="en")
        assert factory.has_key("menu.tools.config") is True

    def test_has_key_partial_path(self) -> None:
        """Test has_key with partial path (non-string leaf)."""
        factory = I18nFactory(config_path="config", locale="en")
        # "menu.file" is a dict, not a string, so has_key should return False
        # Actually, checking the implementation, has_key checks if the final value is a string
        factory._translations_cache = {"menu": {"file": {"save": "Save"}}}
        assert factory.has_key("menu.file") is False  # Not a string leaf

    def test_has_key_non_dict_intermediate(self) -> None:
        """Test has_key when intermediate value is not a dict."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {"key": "value"}
        assert factory.has_key("key.nested") is False


class TestGetAllKeys:
    """Test getting all available translation keys."""

    def test_get_all_keys(self) -> None:
        """Test getting all keys without prefix."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {
            "key1": "value1",
            "key2": "value2",
            "nested": {"key3": "value3"},
        }
        keys = factory.get_all_keys()
        assert "key1" in keys
        assert "key2" in keys
        assert "nested.key3" in keys
        assert len(keys) == 3

    def test_get_all_keys_with_prefix(self) -> None:
        """Test getting keys with prefix filter."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {
            "menu.file": "File",
            "menu.edit": "Edit",
            "action.save": "Save",
        }
        keys = factory.get_all_keys(prefix="menu")
        assert "menu.file" in keys
        assert "menu.edit" in keys
        assert "action.save" not in keys

    def test_get_all_keys_nested(self) -> None:
        """Test getting keys from deeply nested structure."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {
            "level1": {
                "level2": {
                    "key1": "value1",
                    "key2": "value2",
                },
                "key3": "value3",
            },
        }
        keys = factory.get_all_keys()
        assert "level1.level2.key1" in keys
        assert "level1.level2.key2" in keys
        assert "level1.key3" in keys

    def test_get_all_keys_empty_cache(self) -> None:
        """Test getting keys from empty cache."""
        factory = I18nFactory(config_path="config", locale="en")
        factory._translations_cache = {}
        keys = factory.get_all_keys()
        assert keys == []


class TestSetLocale:
    """Test locale switching."""

    def test_set_locale_valid(self) -> None:
        """Test setting a valid locale."""
        factory = I18nFactory(config_path="config", locale="en")
        factory.set_locale("de")
        assert factory.locale == "de"

    def test_set_locale_invalid(self) -> None:
        """Test setting an invalid locale."""
        factory = I18nFactory(config_path="config", locale="en")
        with pytest.raises(ValueError, match="Unsupported locale"):
            factory.set_locale("invalid")

    def test_set_locale_reloads_translations(self) -> None:
        """Test that setting locale reloads translations."""
        factory = I18nFactory(config_path="config", locale="en")
        en_value = factory.translate("menu.view")
        assert en_value == "View"

        factory.set_locale("de")
        de_value = factory.translate("menu.view")
        assert de_value == "Ansicht"  # German translation


class TestLoadLocale:
    """Test _load_locale method and error handling."""

    def test_load_locale_missing_file(self) -> None:
        """Test loading a locale with missing file."""
        with pytest.raises(ValueError, match="Unsupported locale"):
            I18nFactory(config_path="config", locale="nonexistent")

    def test_load_locale_invalid_json_structure(self) -> None:
        """Test error handling for invalid JSON structure in memory."""
        factory = I18nFactory(config_path="config", locale="en")
        # Manually break the cache to test error handling
        factory._translations_cache = []  # type: ignore[assignment]
        # This won't raise an error, but will return the key itself
        result = factory.translate("some.key")
        assert result == "some.key"

    def test_load_locale_cache_structure(self) -> None:
        """Test that loaded locale has correct cache structure."""
        factory = I18nFactory(config_path="config", locale="en")
        # Cache should be a dictionary
        assert isinstance(factory._translations_cache, dict)
        # Should contain some translations
        assert len(factory._translations_cache) > 0
        # Check that at least one expected key exists
        assert "menu.view" in factory._translations_cache
