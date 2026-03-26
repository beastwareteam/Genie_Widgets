"""Pytest configuration for WidgetSystem tests."""

from pathlib import Path


def pytest_configure(config):  # type: ignore
    """Configure pytest with module-specific coverage rules."""
    # Register the 'isolated' marker
    config.addinivalue_line(
        "markers",
        "isolated: marks tests as isolated module tests (not subject to global coverage requirements)",
    )

    cov_sources = getattr(config.option, "cov_source", None)
    if not cov_sources:
        return

    normalized_sources = [Path(source).as_posix() for source in cov_sources]
    specific_sources = [
        source
        for source in normalized_sources
        if source != "src/widgetsystem"
    ]
    if specific_sources:
        config.option.cov_source = specific_sources

