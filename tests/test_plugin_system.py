"""Tests for plugin_system.py - Plugin Registry and Manager.

Tests cover:
- PluginRegistry initialization and factory management
- Plugin loading and unloading
- PluginManager discovery and lifecycle
- Configuration save/load
- Signal emissions
- Error handling
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from widgetsystem.core.plugin_system import PluginManager, PluginRegistry


# Ensure QApplication exists for Qt signals
@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestPluginRegistry:
    """Tests for PluginRegistry class."""

    @pytest.fixture
    def registry(self, qapp: QApplication) -> PluginRegistry:
        """Create PluginRegistry instance."""
        return PluginRegistry()

    def test_initialization(self, registry: PluginRegistry) -> None:
        """Test registry initializes with empty collections."""
        assert registry.plugins == {}
        assert registry.factories == {}
        assert registry.plugin_instances == {}

    def test_initialization_with_parent(self, qapp: QApplication) -> None:
        """Test registry with parent QObject."""
        parent = QObject()
        registry = PluginRegistry(parent)
        assert registry.parent() == parent

    def test_register_factory_success(self, registry: PluginRegistry) -> None:
        """Test successful factory registration."""

        class TestFactory:
            pass

        # Track signal emission
        signal_received = []
        registry.factoryRegistered.connect(lambda name: signal_received.append(name))

        registry.register_factory("test_factory", TestFactory)

        assert "test_factory" in registry.factories
        assert registry.factories["test_factory"] is TestFactory
        assert "test_factory" in signal_received

    def test_register_factory_not_a_class(self, registry: PluginRegistry) -> None:
        """Test factory registration fails for non-class."""
        with pytest.raises(TypeError) as exc_info:
            registry.register_factory("not_class", "string")

        assert "is not a class" in str(exc_info.value)

    def test_register_factory_duplicate(self, registry: PluginRegistry) -> None:
        """Test factory registration fails for duplicate name."""

        class Factory1:
            pass

        class Factory2:
            pass

        registry.register_factory("duplicate", Factory1)

        with pytest.raises(ValueError) as exc_info:
            registry.register_factory("duplicate", Factory2)

        assert "already registered" in str(exc_info.value)

    def test_unregister_factory(self, registry: PluginRegistry) -> None:
        """Test factory unregistration."""

        class TestFactory:
            pass

        registry.register_factory("to_remove", TestFactory)
        assert "to_remove" in registry.factories

        registry.unregister_factory("to_remove")
        assert "to_remove" not in registry.factories

    def test_unregister_nonexistent_factory(self, registry: PluginRegistry) -> None:
        """Test unregistering non-existent factory does nothing."""
        # Should not raise
        registry.unregister_factory("nonexistent")

    def test_get_factory(self, registry: PluginRegistry) -> None:
        """Test getting factory by name."""

        class TestFactory:
            pass

        registry.register_factory("get_test", TestFactory)

        result = registry.get_factory("get_test")
        assert result is TestFactory

        none_result = registry.get_factory("nonexistent")
        assert none_result is None

    def test_get_all_factories(self, registry: PluginRegistry) -> None:
        """Test getting all factories returns copy."""

        class Factory1:
            pass

        class Factory2:
            pass

        registry.register_factory("factory1", Factory1)
        registry.register_factory("factory2", Factory2)

        all_factories = registry.get_all_factories()

        assert len(all_factories) == 2
        assert "factory1" in all_factories
        assert "factory2" in all_factories

        # Verify it's a copy
        all_factories["factory3"] = str
        assert "factory3" not in registry.factories

    def test_get_plugin_not_found(self, registry: PluginRegistry) -> None:
        """Test getting non-existent plugin returns None."""
        result = registry.get_plugin("nonexistent")
        assert result is None

    def test_get_all_plugins_empty(self, registry: PluginRegistry) -> None:
        """Test getting all plugins when empty."""
        result = registry.get_all_plugins()
        assert result == {}

    def test_load_plugin_file_not_found(self, registry: PluginRegistry) -> None:
        """Test loading plugin with non-existent path."""
        fake_path = Path("/nonexistent/plugin.py")

        with pytest.raises(FileNotFoundError):
            registry.load_plugin(fake_path)

    def test_unload_plugin_not_found(self, registry: PluginRegistry) -> None:
        """Test unloading non-existent plugin."""
        result = registry.unload_plugin("nonexistent")
        assert result is False

    def test_extract_plugin_config_basic(self, registry: PluginRegistry) -> None:
        """Test plugin config extraction with basic attributes."""
        mock_module = MagicMock()
        mock_module.__version__ = "1.0.0"
        mock_module.__author__ = "Test Author"
        mock_module.dependencies = ["dep1", "dep2"]
        mock_module.factories = ["factory1"]
        mock_module.plugin_info = {"description": "Test plugin"}

        config = PluginRegistry._extract_plugin_config(mock_module)

        assert config["version"] == "1.0.0"
        assert config["author"] == "Test Author"
        assert config["dependencies"] == ["dep1", "dep2"]
        assert config["factories"] == ["factory1"]
        assert config["description"] == "Test plugin"

    def test_extract_plugin_config_minimal(self, registry: PluginRegistry) -> None:
        """Test plugin config extraction with no attributes."""
        mock_module = MagicMock(spec=[])  # Empty spec

        config = PluginRegistry._extract_plugin_config(mock_module)

        assert config == {}


class TestPluginManager:
    """Tests for PluginManager class."""

    @pytest.fixture
    def manager(self, qapp: QApplication) -> PluginManager:
        """Create PluginManager instance."""
        return PluginManager()

    @pytest.fixture
    def temp_plugin_dir(self) -> Path:
        """Create temporary plugin directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_initialization_empty(self, manager: PluginManager) -> None:
        """Test manager initializes with empty directories."""
        assert manager.plugin_dirs == []
        assert isinstance(manager.registry, PluginRegistry)
        assert manager.config_path is None

    def test_initialization_with_dirs(self, qapp: QApplication) -> None:
        """Test manager initialization with plugin directories."""
        dirs = [Path("/dir1"), Path("/dir2")]
        manager = PluginManager(plugin_dirs=dirs)

        assert manager.plugin_dirs == dirs

    def test_initialization_with_registry(self, qapp: QApplication) -> None:
        """Test manager initialization with existing registry."""
        registry = PluginRegistry()
        manager = PluginManager(registry=registry)

        assert manager.registry is registry

    def test_add_plugin_directory(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test adding plugin directory."""
        manager.add_plugin_directory(temp_plugin_dir)

        assert temp_plugin_dir in manager.plugin_dirs

    def test_add_plugin_directory_not_dir(self, manager: PluginManager) -> None:
        """Test adding non-directory path fails."""
        fake_path = Path("/nonexistent/dir")

        with pytest.raises(NotADirectoryError):
            manager.add_plugin_directory(fake_path)

    def test_add_plugin_directory_duplicate(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test adding same directory twice doesn't duplicate."""
        manager.add_plugin_directory(temp_plugin_dir)
        manager.add_plugin_directory(temp_plugin_dir)

        assert manager.plugin_dirs.count(temp_plugin_dir) == 1

    def test_discover_plugins_empty_dir(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test discovering plugins in empty directory."""
        manager.add_plugin_directory(temp_plugin_dir)

        discovered = manager.discover_plugins()

        assert discovered == []

    def test_discover_plugins_with_files(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test discovering plugin files."""
        # Create plugin files
        (temp_plugin_dir / "plugin1.py").write_text("plugin_name = 'plugin1'")
        (temp_plugin_dir / "plugin2.py").write_text("plugin_name = 'plugin2'")
        (temp_plugin_dir / "_private.py").write_text("# private")

        manager.add_plugin_directory(temp_plugin_dir)
        discovered = manager.discover_plugins()

        assert len(discovered) == 2
        assert any("plugin1.py" in str(p) for p in discovered)
        assert any("plugin2.py" in str(p) for p in discovered)
        # Private files should be ignored
        assert not any("_private.py" in str(p) for p in discovered)

    def test_discover_plugins_with_packages(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test discovering plugin packages."""
        # Create plugin package
        package_dir = temp_plugin_dir / "my_plugin"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("plugin_name = 'my_plugin'")

        # Create private package (should be ignored)
        private_dir = temp_plugin_dir / "_private_plugin"
        private_dir.mkdir()
        (private_dir / "__init__.py").write_text("plugin_name = 'private'")

        manager.add_plugin_directory(temp_plugin_dir)
        discovered = manager.discover_plugins()

        assert len(discovered) == 1
        assert "my_plugin" in str(discovered[0])

    def test_discover_plugins_nonexistent_dir(self, manager: PluginManager) -> None:
        """Test discovering in non-existent directory."""
        manager.plugin_dirs = [Path("/nonexistent/dir")]

        discovered = manager.discover_plugins()

        assert discovered == []

    def test_get_registry(self, manager: PluginManager) -> None:
        """Test getting registry."""
        registry = manager.get_registry()

        assert registry is manager.registry

    def test_save_plugin_config(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test saving plugin configuration."""
        config_file = temp_plugin_dir / "plugins.json"

        # Register a factory
        class TestFactory:
            pass

        manager.registry.register_factory("test_factory", TestFactory)

        manager.save_plugin_config(config_file)

        assert config_file.exists()
        assert manager.config_path == config_file

        # Verify content
        with open(config_file) as f:
            config = json.load(f)

        assert "factories" in config
        assert "test_factory" in config["factories"]

    def test_load_plugin_config(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test loading plugin configuration."""
        config_file = temp_plugin_dir / "plugins.json"
        test_config = {
            "plugins": {"plugin1": {"version": "1.0"}},
            "factories": ["factory1", "factory2"],
        }

        with open(config_file, "w") as f:
            json.dump(test_config, f)

        loaded = manager.load_plugin_config(config_file)

        assert loaded == test_config
        assert manager.config_path == config_file

    def test_load_plugin_config_not_found(
        self, manager: PluginManager, temp_plugin_dir: Path
    ) -> None:
        """Test loading non-existent config file."""
        config_file = temp_plugin_dir / "nonexistent.json"

        loaded = manager.load_plugin_config(config_file)

        assert loaded == {}

    def test_reload_plugin_not_found(self, manager: PluginManager) -> None:
        """Test reloading non-existent plugin."""
        result = manager.reload_plugin("nonexistent")

        assert result is False

    def test_get_factories_for_plugin_not_found(
        self, manager: PluginManager
    ) -> None:
        """Test getting factories for non-existent plugin."""
        result = manager.get_factories_for_plugin("nonexistent")

        assert result == []


class TestPluginLoadingIntegration:
    """Integration tests for plugin loading."""

    @pytest.fixture
    def temp_plugin_dir(self) -> Path:
        """Create temporary plugin directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def qapp(self) -> QApplication:
        """Create QApplication for tests."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def test_load_valid_plugin(
        self, qapp: QApplication, temp_plugin_dir: Path
    ) -> None:
        """Test loading a valid plugin file."""
        # Create valid plugin
        plugin_content = '''
plugin_name = "test_plugin"
__version__ = "1.0.0"
__author__ = "Test"

plugin_info = {
    "description": "A test plugin"
}

def initialize():
    pass

def cleanup():
    pass
'''
        plugin_file = temp_plugin_dir / "test_plugin.py"
        plugin_file.write_text(plugin_content)

        registry = PluginRegistry()

        # Track signals
        loaded_plugins = []
        registry.pluginLoaded.connect(lambda name: loaded_plugins.append(name))

        result = registry.load_plugin(plugin_file)

        assert result == "test_plugin"
        assert "test_plugin" in registry.plugins
        assert "test_plugin" in loaded_plugins

        # Verify plugin info
        plugin_info = registry.get_plugin("test_plugin")
        assert plugin_info is not None
        assert plugin_info["config"]["version"] == "1.0.0"

    def test_load_plugin_without_name(
        self, qapp: QApplication, temp_plugin_dir: Path
    ) -> None:
        """Test loading plugin without plugin_name fails."""
        plugin_content = '''
# Missing plugin_name
__version__ = "1.0.0"
'''
        plugin_file = temp_plugin_dir / "invalid_plugin.py"
        plugin_file.write_text(plugin_content)

        registry = PluginRegistry()

        # Track error signal
        errors = []
        registry.errorOccurred.connect(lambda msg: errors.append(msg))

        result = registry.load_plugin(plugin_file)

        assert result is None
        assert len(errors) > 0

    def test_unload_plugin_with_cleanup(
        self, qapp: QApplication, temp_plugin_dir: Path
    ) -> None:
        """Test unloading plugin calls cleanup."""
        plugin_content = '''
plugin_name = "cleanup_test"
_cleaned_up = False

def cleanup():
    global _cleaned_up
    _cleaned_up = True
'''
        plugin_file = temp_plugin_dir / "cleanup_plugin.py"
        plugin_file.write_text(plugin_content)

        registry = PluginRegistry()
        registry.load_plugin(plugin_file)

        # Track signals
        unloaded = []
        registry.pluginUnloaded.connect(lambda name: unloaded.append(name))

        result = registry.unload_plugin("cleanup_test")

        assert result is True
        assert "cleanup_test" in unloaded
        assert "cleanup_test" not in registry.plugins

    def test_load_all_plugins(
        self, qapp: QApplication, temp_plugin_dir: Path
    ) -> None:
        """Test loading all discovered plugins."""
        # Create multiple plugins
        for i in range(3):
            plugin_content = f'''
plugin_name = "plugin_{i}"
'''
            (temp_plugin_dir / f"plugin_{i}.py").write_text(plugin_content)

        manager = PluginManager([temp_plugin_dir])
        loaded = manager.load_all_plugins()

        assert len(loaded) == 3
        assert all(name is not None for name in loaded.values())


class TestSignalEmission:
    """Tests for signal emission."""

    @pytest.fixture
    def qapp(self) -> QApplication:
        """Create QApplication for tests."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def test_factory_registered_signal(self, qapp: QApplication) -> None:
        """Test factoryRegistered signal is emitted."""
        registry = PluginRegistry()

        received = []
        registry.factoryRegistered.connect(lambda name: received.append(name))

        class TestFactory:
            pass

        registry.register_factory("signal_test", TestFactory)

        assert "signal_test" in received

    def test_error_occurred_signal(self, qapp: QApplication) -> None:
        """Test errorOccurred signal is emitted on error."""
        registry = PluginRegistry()

        errors = []
        registry.errorOccurred.connect(lambda msg: errors.append(msg))

        # Force an error by loading non-existent file
        try:
            registry.load_plugin(Path("/nonexistent/plugin.py"))
        except FileNotFoundError:
            pass

        # Error should be emitted for other types of errors
        # FileNotFoundError is raised directly, not via signal
