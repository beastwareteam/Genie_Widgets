"""LayoutController - Layout persistence management.

This controller encapsulates all layout-related operations:
- Save/Load layouts to/from files
- Named layout management
- Layout reset with proper state cleanup
- CDockManager flag configuration
"""

import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QByteArray, QObject, Signal
import PySide6QtAds as QtAds


logger = logging.getLogger(__name__)


class LayoutController(QObject):
    """Controller for layout persistence.

    Manages saving, loading, and resetting dock layouts.
    Provides a single source of truth for CDockManager configuration.

    Signals:
        layoutSaved: Emitted when layout is saved (path)
        layoutLoaded: Emitted when layout is loaded successfully (path)
        layoutLoadFailed: Emitted when layout load fails (path, error)
        layoutReset: Emitted when layout is reset
    """

    layoutSaved = Signal(str)  # path
    layoutLoaded = Signal(str)  # path
    layoutLoadFailed = Signal(str, str)  # path, error
    layoutReset = Signal()

    def __init__(
        self,
        dock_manager: Any,
        layout_factory: Any,
        i18n_factory: Any,
        parent: QObject | None = None,
    ) -> None:
        """Initialize LayoutController.

        Args:
            dock_manager: The CDockManager instance
            layout_factory: LayoutFactory for layout configurations
            i18n_factory: I18nFactory for translations
            parent: Parent QObject
        """
        super().__init__(parent)

        self._dock_manager = dock_manager
        self._layout_factory = layout_factory
        self._i18n_factory = i18n_factory

        # Resolve default layout file
        self._layout_file = self._resolve_default_layout_file()

    @property
    def layout_file(self) -> Path:
        """Get the current layout file path."""
        return self._layout_file

    @layout_file.setter
    def layout_file(self, path: Path) -> None:
        """Set the layout file path."""
        self._layout_file = path

    @property
    def dock_manager(self) -> Any:
        """Get the associated dock manager."""
        return self._dock_manager

    @dock_manager.setter
    def dock_manager(self, manager: Any) -> None:
        """Set the dock manager (used after reset)."""
        self._dock_manager = manager

    def _resolve_default_layout_file(self) -> Path:
        """Resolve default layout file path from LayoutFactory configuration."""
        default_layout_id = self._layout_factory.get_default_layout_id()
        if default_layout_id:
            for layout in self._layout_factory.list_layouts():
                if layout.layout_id == default_layout_id:
                        return layout.file_path  # type: ignore[no-any-return]

        return (Path.cwd() / "data" / "layout.xml").resolve()

    @staticmethod
    def configure_dock_flags() -> None:
        """Configure CDockManager flags.

        This is the SINGLE source of truth for dock manager configuration.
        Called before creating a new CDockManager instance.
        """
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.OpaqueSplitterResize, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.XmlCompressionEnabled, False
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.AllTabsHaveCloseButton, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DockAreaHasCloseButton, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.DockAreaHasUndockButton, True
        )
        # Use Qt custom title bar for floating containers
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerForceNativeTitleBar, False
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerForceQWidgetTitleBar, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerHasWidgetTitle, True
        )
        QtAds.CDockManager.setConfigFlag(
            QtAds.CDockManager.eConfigFlag.FloatingContainerHasWidgetIcon, True
        )

    def save(self, path: Path | None = None) -> bool:
        """Save current layout to file.

        Args:
            path: Optional path override. Uses default if not provided.

        Returns:
            True if save succeeded, False otherwise
        """
        target_path = path or self._layout_file

        try:
            state: QByteArray = self._dock_manager.saveState()
            logger.debug("State size: %s bytes", len(state.data()))

            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(state.data())

            written_size = target_path.stat().st_size
            logger.debug("Written to %s", target_path)
            logger.debug("Actual file size: %s bytes", written_size)
            logger.debug("Save completed successfully")

            self.layoutSaved.emit(str(target_path))
            return True

        except Exception as exc:
            logger.exception("Error")
            return False

    def load(self, path: Path | None = None) -> bool:
        """Load layout from file.

        Args:
            path: Optional path override. Uses default if not provided.

        Returns:
            True if load succeeded, False otherwise
        """
        target_path = path or self._layout_file

        try:
            logger.debug("Attempting to load from %s", target_path)

            if not target_path.exists():
                logger.warning("File does not exist")
                self.layoutLoadFailed.emit(str(target_path), "File not found")
                return False

            data = target_path.read_bytes()
            logger.debug("Read %s bytes from file", len(data))

            restored = self._dock_manager.restoreState(QByteArray(data))
            logger.debug("restoreState returned: %s", restored)

            if not restored:
                logger.error("restoreState failed")
                self.layoutLoadFailed.emit(str(target_path), "restoreState failed")
                return False

            logger.debug("Layout restored successfully")
            self.layoutLoaded.emit(str(target_path))
            return True

        except Exception as exc:
            logger.exception("Exception")
            self.layoutLoadFailed.emit(str(target_path), str(exc))
            return False

    def load_on_startup(self) -> bool:
        """Load layout silently on startup.

        Returns:
            True if load succeeded, False otherwise
        """
        logger.debug("Starting layout restoration")

        try:
            logger.debug("Checking %s", self._layout_file)

            if not self._layout_file.exists():
                logger.warning("File does not exist, skipping restore")
                return False

            logger.debug("File exists, attempting restore")
            data = self._layout_file.read_bytes()
            logger.debug("Read %s bytes", len(data))

            restored = self._dock_manager.restoreState(QByteArray(data))
            logger.debug("restoreState returned: %s", restored)

            if not restored:
                logger.warning("restoreState failed")
                return False

            logger.debug("Restored successfully")
            return True

        except Exception as exc:
            logger.exception("Exception")
            return False

    def load_named(self, layout: Any) -> bool:
        """Load a named layout from LayoutFactory.

        Args:
            layout: LayoutDefinition object with file_path

        Returns:
            True if load succeeded, False otherwise
        """
        try:
            if not layout.file_path.exists():
                self.layoutLoadFailed.emit(
                    str(layout.file_path), "File not found"
                )
                return False

            data = layout.file_path.read_bytes()
            restored = self._dock_manager.restoreState(QByteArray(data))

            if not restored:
                self.layoutLoadFailed.emit(
                    str(layout.file_path), "restoreState failed"
                )
                return False

            self.layoutLoaded.emit(str(layout.file_path))
            return True

        except Exception as exc:
            self.layoutLoadFailed.emit(str(layout.file_path), str(exc))
            return False

    def list_layouts(self) -> list[Any]:
        """Get list of available layouts.

        Returns:
            List of LayoutDefinition objects
        """
        return self._layout_factory.list_layouts()  # type: ignore[no-any-return]

    def get_default_layout_id(self) -> str | None:
        """Get the default layout ID.

        Returns:
            Default layout ID or None
        """
        return self._layout_factory.get_default_layout_id()  # type: ignore[no-any-return]
