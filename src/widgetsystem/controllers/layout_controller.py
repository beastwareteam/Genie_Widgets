"""LayoutController - Layout persistence management.

This controller encapsulates all layout-related operations:
- Save/Load layouts to/from files
- Named layout management
- Layout reset with proper state cleanup
- CDockManager flag configuration
"""

from pathlib import Path
from typing import Any

import PySide6QtAds as QtAds
from PySide6.QtCore import QByteArray, QObject, Signal


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
                    return layout.file_path

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
            print(f"[SAVE] State size: {len(state.data())} bytes")

            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(state.data())

            written_size = target_path.stat().st_size
            print(f"[SAVE] Written to {target_path}")
            print(f"[SAVE] Actual file size: {written_size} bytes")
            print("[SAVE] [+] Save completed successfully")

            self.layoutSaved.emit(str(target_path))
            return True

        except Exception as exc:
            print(f"[SAVE] [X] Error: {exc}")
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
            print(f"[LOAD] Attempting to load from {target_path}")

            if not target_path.exists():
                print("[LOAD] [X] File does not exist")
                self.layoutLoadFailed.emit(str(target_path), "File not found")
                return False

            data = target_path.read_bytes()
            print(f"[LOAD] Read {len(data)} bytes from file")

            restored = self._dock_manager.restoreState(QByteArray(data))
            print(f"[LOAD] restoreState returned: {restored}")

            if not restored:
                print("[LOAD] [X] restoreState failed")
                self.layoutLoadFailed.emit(str(target_path), "restoreState failed")
                return False

            print("[LOAD] [+] Layout restored successfully")
            self.layoutLoaded.emit(str(target_path))
            return True

        except Exception as exc:
            print(f"[LOAD] [X] Exception: {exc}")
            self.layoutLoadFailed.emit(str(target_path), str(exc))
            return False

    def load_on_startup(self) -> bool:
        """Load layout silently on startup.

        Returns:
            True if load succeeded, False otherwise
        """
        print("[STARTUP_LOAD] Starting layout restoration")

        try:
            print(f"[STARTUP_LOAD] Checking {self._layout_file}")

            if not self._layout_file.exists():
                print("[STARTUP_LOAD] [!] File does not exist, skipping restore")
                return False

            print("[STARTUP_LOAD] File exists, attempting restore")
            data = self._layout_file.read_bytes()
            print(f"[STARTUP_LOAD] Read {len(data)} bytes")

            restored = self._dock_manager.restoreState(QByteArray(data))
            print(f"[STARTUP_LOAD] restoreState returned: {restored}")

            if not restored:
                print("[STARTUP_LOAD] [!] restoreState failed")
                return False

            print("[STARTUP_LOAD] [+] Restored successfully")
            return True

        except Exception as exc:
            print(f"[STARTUP_LOAD] [X] Exception: {exc}")
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
        return self._layout_factory.list_layouts()

    def get_default_layout_id(self) -> str | None:
        """Get the default layout ID.

        Returns:
            Default layout ID or None
        """
        return self._layout_factory.get_default_layout_id()
