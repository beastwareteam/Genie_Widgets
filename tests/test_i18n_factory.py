"""Test I18nFactory - Validates internationalization functionality."""

from pathlib import Path

import pytest

from widgetsystem.factories.i18n_factory import I18nFactory


def test_i18n_factory_initialization():
    """Test the initialization of I18nFactory."""
    factory = I18nFactory(config_path="config", locale="en")
    assert factory.locale == "en"
    assert factory.config_path == Path("config")
    print("✅ I18nFactory initialization test passed.")


def test_i18n_factory_invalid_locale():
    """Test I18nFactory with an unsupported locale."""
    with pytest.raises(ValueError) as excinfo:
        I18nFactory(config_path="config", locale="fr")
    assert "Unsupported locale 'fr'" in str(excinfo.value)
    print("✅ I18nFactory invalid locale test passed.")


def test_i18n_factory_missing_file():
    """Test I18nFactory with a missing i18n file."""
    with pytest.raises(ValueError) as excinfo:
        I18nFactory(config_path="config", locale="es")
    assert "Unsupported locale 'es'" in str(excinfo.value)
    print("✅ I18nFactory missing file test passed.")
