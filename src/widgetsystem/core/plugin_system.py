"""Plugin system for dynamic factory loading and management.

Provides:
- Dynamic plugin discovery and loading
- Factory registration and lifecycle management
- Hot-reload capabilities
- Plugin configuration and validation
"""

import importlib
import importlib.util
import inspect
import json
import logging
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class PluginRegistry(QObject):
    """Registry for managing plugins and factories.

    Signals:
        pluginLoaded: Emitted when plugin is loaded (plugin_name)
        pluginUnloaded: Emitted when plugin is unloaded (plugin_name)
        factoryRegistered: Emitted when factory is registered (factory_name)
        errorOccurred: Emitted on error (error_message)
    """

    pluginLoaded = Signal(str)
    pluginUnloaded = Signal(str)
    factoryRegistered = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize plugin registry.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.plugins: dict[str, dict[str, Any]] = {}
        self.factories: dict[str, type[Any]] = {}
        self.plugin_instances: dict[str, Any] = {}
        logger.debug("PluginRegistry initialized")

    def register_factory(self, factory_name: str, factory_class: type[Any]) -> None:
        """Register a factory class.

        Args:
            factory_name: Name to register factory under
            factory_class: Factory class to register

        Raises:
            TypeError: If factory_class is not a class
            ValueError: If factory already registered
        """
        if not inspect.isclass(factory_class):
            raise TypeError(f"{factory_class} is not a class")

        if factory_name in self.factories:
            raise ValueError(f"Factory {factory_name} already registered")

        self.factories[factory_name] = factory_class
        self.factoryRegistered.emit(factory_name)
        logger.info(f"Factory registered: {factory_name}")

    def unregister_factory(self, factory_name: str) -> None:
        """Unregister a factory.

        Args:
            factory_name: Name of factory to unregister
        """
        if factory_name in self.factories:
            del self.factories[factory_name]
            logger.info(f"Factory unregistered: {factory_name}")

    def get_factory(self, factory_name: str) -> type[Any] | None:
        """Get registered factory.

        Args:
            factory_name: Name of factory to retrieve

        Returns:
            Factory class or None if not found
        """
        return self.factories.get(factory_name)

    def get_all_factories(self) -> dict[str, type[Any]]:
        """Get all registered factories.

        Returns:
            Dictionary of factory_name -> factory_class
        """
        return self.factories.copy()

    def load_plugin(self, plugin_path: Path) -> str | None:
        """Load a plugin from path.

        Args:
            plugin_path: Path to plugin module or package

        Returns:
            Plugin name or None if loading failed

        Raises:
            FileNotFoundError: If plugin_path does not exist
        """
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin path not found: {plugin_path}")

        try:
            module_name = plugin_path.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)

            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load spec for {plugin_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Check for plugin definition
            if not hasattr(module, "plugin_name"):
                raise ValueError("Plugin must define 'plugin_name'")

            plugin_name = module.plugin_name
            plugin_config = self._extract_plugin_config(module)

            self.plugins[plugin_name] = {
                "module": module,
                "path": plugin_path,
                "config": plugin_config,
            }
            self.plugin_instances[plugin_name] = module

            self.pluginLoaded.emit(plugin_name)
            logger.info(f"Plugin loaded: {plugin_name} from {plugin_path}")

            return plugin_name

        except Exception as exc:
            error_msg = f"Failed to load plugin {plugin_path}: {exc}"
            logger.exception(error_msg)
            self.errorOccurred.emit(error_msg)
            return None

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            Success status
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not found: {plugin_name}")
            return False

        try:
            plugin_info = self.plugins[plugin_name]
            module = plugin_info["module"]

            # Call cleanup if available
            if hasattr(module, "cleanup"):
                module.cleanup()

            # Remove from sys.modules
            module_name = module.__name__
            if module_name in sys.modules:
                del sys.modules[module_name]

            # Remove from registries
            del self.plugins[plugin_name]
            if plugin_name in self.plugin_instances:
                del self.plugin_instances[plugin_name]

            self.pluginUnloaded.emit(plugin_name)
            logger.info(f"Plugin unloaded: {plugin_name}")

            return True

        except Exception as exc:
            error_msg = f"Error unloading plugin {plugin_name}: {exc}"
            logger.exception(error_msg)
            self.errorOccurred.emit(error_msg)
            return False

    def get_plugin(self, plugin_name: str) -> dict[str, Any] | None:
        """Get plugin information.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin info dictionary or None
        """
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> dict[str, dict[str, Any]]:
        """Get all loaded plugins.

        Returns:
            Dictionary of plugin_name -> plugin_info
        """
        return self.plugins.copy()

    @staticmethod
    def _extract_plugin_config(module: Any) -> dict[str, Any]:
        """Extract plugin configuration from module.

        Args:
            module: Plugin module

        Returns:
            Plugin configuration dictionary
        """
        config: dict[str, Any] = {}

        if hasattr(module, "plugin_info"):
            config.update(module.plugin_info)

        # Extract basic info
        if hasattr(module, "__version__"):
            config["version"] = module.__version__

        if hasattr(module, "__author__"):
            config["author"] = module.__author__

        if hasattr(module, "dependencies"):
            config["dependencies"] = module.dependencies

        if hasattr(module, "factories"):
            config["factories"] = module.factories

        return config


class PluginManager:
    """Manager for plugin discovery and lifecycle.

    Handles:
    - Plugin discovery from directories
    - Plugin loading and unloading
    - Configuration management
    """

    def __init__(
        self,
        plugin_dirs: list[Path] | None = None,
        registry: PluginRegistry | None = None,
    ) -> None:
        """Initialize Plugin Manager.

        Args:
            plugin_dirs: List of directories to search for plugins
            registry: Optional existing PluginRegistry to use
        """
        self.plugin_dirs = plugin_dirs or []
        self.registry = registry or PluginRegistry()
        self.config_path: Path | None = None
        logger.debug(f"PluginManager initialized with {len(self.plugin_dirs)} dirs")

    def add_plugin_directory(self, plugin_dir: Path) -> None:
        """Add plugin directory.

        Args:
            plugin_dir: Directory to add

        Raises:
            NotADirectoryError: If path is not a directory
        """
        if not plugin_dir.is_dir():
            raise NotADirectoryError(f"{plugin_dir} is not a directory")

        if plugin_dir not in self.plugin_dirs:
            self.plugin_dirs.append(plugin_dir)
            logger.info(f"Plugin directory added: {plugin_dir}")

    def discover_plugins(self) -> list[Path]:
        """Discover plugins in configured directories.

        Returns:
            List of discovered plugin paths
        """
        plugins: list[Path] = []

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue

            # Find .py files
            for plugin_file in plugin_dir.glob("*.py"):
                if not plugin_file.name.startswith("_"):
                    plugins.append(plugin_file)

            # Find package directories with __init__.py
            for subdir in plugin_dir.iterdir():
                if subdir.is_dir() and not subdir.name.startswith("_"):
                    init_file = subdir / "__init__.py"
                    if init_file.exists():
                        plugins.append(init_file)

        logger.debug(f"Discovered {len(plugins)} plugins")
        return plugins

    def load_all_plugins(self) -> dict[str, str | None]:
        """Load all discovered plugins.

        Returns:
            Dictionary of plugin_path -> plugin_name
        """
        discovered = self.discover_plugins()
        loaded: dict[str, str | None] = {}

        for plugin_path in discovered:
            try:
                plugin_name = self.registry.load_plugin(plugin_path)
                loaded[str(plugin_path)] = plugin_name
            except Exception as exc:
                logger.error(f"Failed to load {plugin_path}: {exc}")
                loaded[str(plugin_path)] = None

        return loaded

    def save_plugin_config(self, config_path: Path) -> None:
        """Save plugin configuration to file.

        Args:
            config_path: Path to save config to
        """
        self.config_path = config_path

        try:
            config = {
                "plugins": {
                    name: info["config"]
                    for name, info in self.registry.get_all_plugins().items()
                },
                "factories": list(self.registry.get_all_factories().keys()),
            }

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"Plugin configuration saved to {config_path}")

        except Exception as exc:
            logger.exception(f"Error saving plugin config: {exc}")

    def load_plugin_config(self, config_path: Path) -> dict[str, Any]:
        """Load plugin configuration from file.

        Args:
            config_path: Path to load config from

        Returns:
            Configuration dictionary
        """
        self.config_path = config_path

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            logger.info(f"Plugin configuration loaded from {config_path}")
            return config

        except Exception as exc:
            logger.exception(f"Error loading plugin config: {exc}")
            return {}

    def reload_plugin(self, plugin_name: str) -> bool:
        """Hot-reload a plugin.

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            Success status
        """
        plugin_info = self.registry.get_plugin(plugin_name)
        if not plugin_info:
            logger.warning(f"Plugin not found for reload: {plugin_name}")
            return False

        plugin_path = plugin_info["path"]

        # Unload
        if not self.registry.unload_plugin(plugin_name):
            return False

        # Reload
        try:
            new_name = self.registry.load_plugin(plugin_path)
            success = new_name is not None
            if success:
                logger.info(f"Plugin reloaded: {plugin_name}")
            return success
        except Exception as exc:
            logger.exception(f"Error reloading plugin {plugin_name}: {exc}")
            return False

    def get_registry(self) -> PluginRegistry:
        """Get plugin registry.

        Returns:
            PluginRegistry instance
        """
        return self.registry

    def get_factories_for_plugin(self, plugin_name: str) -> list[str]:
        """Get factories associated with plugin.

        Args:
            plugin_name: Name of plugin

        Returns:
            List of factory names
        """
        plugin_info = self.registry.get_plugin(plugin_name)
        if not plugin_info:
            return []

        config = plugin_info.get("config", {})
        return config.get("factories", [])
