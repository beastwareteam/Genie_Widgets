"""Configuration Import/Export system.

Provides functionality for:
- Exporting configurations to various formats (JSON, ZIP archive)
- Importing configurations with validation
- Backup and restore capabilities
- Configuration migration between versions
"""

import json
import logging
import shutil
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


@dataclass
class ExportOptions:
    """Options for configuration export."""

    include_themes: bool = True
    include_layouts: bool = True
    include_panels: bool = True
    include_menus: bool = True
    include_tabs: bool = True
    include_lists: bool = True
    include_i18n: bool = True
    include_profiles: bool = True
    compress: bool = True
    add_metadata: bool = True


@dataclass
class ImportOptions:
    """Options for configuration import."""

    overwrite_existing: bool = False
    merge_configs: bool = True
    validate_before_import: bool = True
    create_backup: bool = True
    skip_invalid: bool = False


@dataclass
class ConfigMetadata:
    """Metadata for exported configuration."""

    version: str = "1.0.0"
    export_date: str = field(default_factory=lambda: datetime.now().isoformat())
    source_app: str = "WidgetSystem"
    description: str = ""
    included_files: list[str] = field(default_factory=list)


class ConfigurationExporter(QObject):
    """Export configuration to files or archives.

    Signals:
        exportStarted: Emitted when export starts (destination)
        exportProgress: Emitted during export (percentage, current_file)
        exportCompleted: Emitted when export completes (destination)
        exportFailed: Emitted on error (error_message)
    """

    exportStarted = Signal(str)
    exportProgress = Signal(int, str)
    exportCompleted = Signal(str)
    exportFailed = Signal(str)

    def __init__(
        self,
        config_path: Path,
        parent: QObject | None = None,
    ) -> None:
        """Initialize configuration exporter.

        Args:
            config_path: Path to configuration directory
            parent: Parent QObject
        """
        super().__init__(parent)
        self.config_path = config_path
        logger.debug(f"ConfigurationExporter initialized for {config_path}")

    def export_to_json(
        self,
        destination: Path,
        options: ExportOptions | None = None,
    ) -> bool:
        """Export configuration to a single JSON file.

        Args:
            destination: Destination file path
            options: Export options

        Returns:
            True if export was successful
        """
        options = options or ExportOptions()
        self.exportStarted.emit(str(destination))

        try:
            export_data: dict[str, Any] = {}

            # Collect files to export
            files_to_export = self._get_files_to_export(options)
            total_files = len(files_to_export)

            for idx, (key, filename) in enumerate(files_to_export):
                file_path = self.config_path / filename
                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            export_data[key] = json.load(f)
                        self.exportProgress.emit(
                            int((idx + 1) / total_files * 100),
                            filename,
                        )
                    except json.JSONDecodeError as exc:
                        logger.warning(f"Skipping invalid JSON: {filename} - {exc}")

            # Add metadata
            if options.add_metadata:
                metadata = ConfigMetadata(
                    included_files=[f[1] for f in files_to_export if (self.config_path / f[1]).exists()],
                )
                export_data["_metadata"] = {
                    "version": metadata.version,
                    "export_date": metadata.export_date,
                    "source_app": metadata.source_app,
                    "included_files": metadata.included_files,
                }

            # Write export file
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.exportCompleted.emit(str(destination))
            logger.info(f"Configuration exported to {destination}")
            return True

        except Exception as exc:
            error_msg = f"Export failed: {exc}"
            logger.exception(error_msg)
            self.exportFailed.emit(error_msg)
            return False

    def export_to_archive(
        self,
        destination: Path,
        options: ExportOptions | None = None,
    ) -> bool:
        """Export configuration to a ZIP archive.

        Args:
            destination: Destination archive path
            options: Export options

        Returns:
            True if export was successful
        """
        options = options or ExportOptions()
        self.exportStarted.emit(str(destination))

        try:
            files_to_export = self._get_files_to_export(options)
            total_files = len(files_to_export)

            destination.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(
                destination,
                "w",
                compression=zipfile.ZIP_DEFLATED if options.compress else zipfile.ZIP_STORED,
            ) as archive:
                for idx, (_, filename) in enumerate(files_to_export):
                    file_path = self.config_path / filename
                    if file_path.exists():
                        archive.write(file_path, filename)
                        self.exportProgress.emit(
                            int((idx + 1) / total_files * 100),
                            filename,
                        )

                # Add profiles directory if included
                if options.include_profiles:
                    profiles_dir = self.config_path / "profiles"
                    if profiles_dir.exists():
                        for profile_file in profiles_dir.glob("*.json"):
                            archive.write(profile_file, f"profiles/{profile_file.name}")

                # Add metadata
                if options.add_metadata:
                    metadata = ConfigMetadata(
                        included_files=[f[1] for f in files_to_export if (self.config_path / f[1]).exists()],
                    )
                    archive.writestr(
                        "_metadata.json",
                        json.dumps(
                            {
                                "version": metadata.version,
                                "export_date": metadata.export_date,
                                "source_app": metadata.source_app,
                                "included_files": metadata.included_files,
                            },
                            indent=2,
                        ),
                    )

            self.exportCompleted.emit(str(destination))
            logger.info(f"Configuration archived to {destination}")
            return True

        except Exception as exc:
            error_msg = f"Archive export failed: {exc}"
            logger.exception(error_msg)
            self.exportFailed.emit(error_msg)
            return False

    def _get_files_to_export(self, options: ExportOptions) -> list[tuple[str, str]]:
        """Get list of files to export based on options.

        Args:
            options: Export options

        Returns:
            List of (key, filename) tuples
        """
        files: list[tuple[str, str]] = []

        if options.include_themes:
            files.append(("themes", "themes.json"))
        if options.include_layouts:
            files.append(("layouts", "layouts.json"))
        if options.include_panels:
            files.append(("panels", "panels.json"))
        if options.include_menus:
            files.append(("menus", "menus.json"))
        if options.include_tabs:
            files.append(("tabs", "tabs.json"))
        if options.include_lists:
            files.append(("lists", "lists.json"))
        if options.include_i18n:
            files.append(("i18n_de", "i18n.de.json"))
            files.append(("i18n_en", "i18n.en.json"))

        return files


class ConfigurationImporter(QObject):
    """Import configuration from files or archives.

    Signals:
        importStarted: Emitted when import starts (source)
        importProgress: Emitted during import (percentage, current_file)
        importCompleted: Emitted when import completes (imported_files_count)
        importFailed: Emitted on error (error_message)
        validationError: Emitted when validation fails (error_details)
    """

    importStarted = Signal(str)
    importProgress = Signal(int, str)
    importCompleted = Signal(int)
    importFailed = Signal(str)
    validationError = Signal(str)

    def __init__(
        self,
        config_path: Path,
        parent: QObject | None = None,
    ) -> None:
        """Initialize configuration importer.

        Args:
            config_path: Path to configuration directory
            parent: Parent QObject
        """
        super().__init__(parent)
        self.config_path = config_path
        logger.debug(f"ConfigurationImporter initialized for {config_path}")

    def import_from_json(
        self,
        source: Path,
        options: ImportOptions | None = None,
    ) -> bool:
        """Import configuration from a JSON file.

        Args:
            source: Source file path
            options: Import options

        Returns:
            True if import was successful
        """
        options = options or ImportOptions()
        self.importStarted.emit(str(source))

        try:
            # Read source file
            with open(source, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            # Validate if required
            if options.validate_before_import:
                if not self._validate_import_data(import_data):
                    return False

            # Create backup if required
            if options.create_backup:
                self._create_backup()

            # Import each configuration
            imported_count = 0
            config_keys = [k for k in import_data.keys() if not k.startswith("_")]
            total_keys = len(config_keys)

            for idx, key in enumerate(config_keys):
                filename = self._key_to_filename(key)
                if filename:
                    dest_path = self.config_path / filename

                    if dest_path.exists() and not options.overwrite_existing:
                        if options.merge_configs:
                            self._merge_config(dest_path, import_data[key])
                        else:
                            logger.info(f"Skipping existing: {filename}")
                            continue
                    else:
                        with open(dest_path, "w", encoding="utf-8") as f:
                            json.dump(import_data[key], f, indent=2, ensure_ascii=False)

                    imported_count += 1
                    self.importProgress.emit(
                        int((idx + 1) / total_keys * 100),
                        filename,
                    )

            self.importCompleted.emit(imported_count)
            logger.info(f"Imported {imported_count} configurations from {source}")
            return True

        except Exception as exc:
            error_msg = f"Import failed: {exc}"
            logger.exception(error_msg)
            self.importFailed.emit(error_msg)
            return False

    def import_from_archive(
        self,
        source: Path,
        options: ImportOptions | None = None,
    ) -> bool:
        """Import configuration from a ZIP archive.

        Args:
            source: Source archive path
            options: Import options

        Returns:
            True if import was successful
        """
        options = options or ImportOptions()
        self.importStarted.emit(str(source))

        try:
            # Create backup if required
            if options.create_backup:
                self._create_backup()

            imported_count = 0

            with zipfile.ZipFile(source, "r") as archive:
                file_list = [
                    f for f in archive.namelist()
                    if f.endswith(".json") and not f.startswith("_")
                ]
                total_files = len(file_list)

                for idx, filename in enumerate(file_list):
                    dest_path = self.config_path / filename

                    if dest_path.exists() and not options.overwrite_existing:
                        if options.merge_configs:
                            # Read and merge
                            content = json.loads(archive.read(filename).decode("utf-8"))
                            self._merge_config(dest_path, content)
                        else:
                            logger.info(f"Skipping existing: {filename}")
                            continue
                    else:
                        # Ensure parent directory exists
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        archive.extract(filename, self.config_path)

                    imported_count += 1
                    self.importProgress.emit(
                        int((idx + 1) / total_files * 100),
                        filename,
                    )

            self.importCompleted.emit(imported_count)
            logger.info(f"Imported {imported_count} files from archive {source}")
            return True

        except Exception as exc:
            error_msg = f"Archive import failed: {exc}"
            logger.exception(error_msg)
            self.importFailed.emit(error_msg)
            return False

    def _validate_import_data(self, data: dict[str, Any]) -> bool:
        """Validate import data structure.

        Args:
            data: Data to validate

        Returns:
            True if valid
        """
        if not isinstance(data, dict):
            self.validationError.emit("Import data must be a JSON object")
            return False

        # Check for required structure
        valid_keys = {
            "themes", "layouts", "panels", "menus", "tabs",
            "lists", "i18n_de", "i18n_en", "_metadata",
        }

        unknown_keys = set(data.keys()) - valid_keys
        if unknown_keys:
            logger.warning(f"Unknown keys in import data: {unknown_keys}")

        return True

    def _create_backup(self) -> Path | None:
        """Create backup of current configuration.

        Returns:
            Path to backup directory or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config_path.parent / f"config_backup_{timestamp}"
            shutil.copytree(self.config_path, backup_dir)
            logger.info(f"Backup created at {backup_dir}")
            return backup_dir
        except Exception as exc:
            logger.warning(f"Failed to create backup: {exc}")
            return None

    def _merge_config(self, dest_path: Path, new_data: Any) -> None:
        """Merge new data with existing configuration.

        Args:
            dest_path: Path to existing config file
            new_data: New data to merge
        """
        try:
            with open(dest_path, "r", encoding="utf-8") as f:
                existing = json.load(f)

            if isinstance(existing, dict) and isinstance(new_data, dict):
                # Deep merge dictionaries
                merged = self._deep_merge(existing, new_data)
            elif isinstance(existing, list) and isinstance(new_data, list):
                # Append new items
                merged = existing + new_data
            else:
                # Replace with new data
                merged = new_data

            with open(dest_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)

            logger.debug(f"Merged configuration: {dest_path}")

        except Exception as exc:
            logger.warning(f"Merge failed for {dest_path}: {exc}")

    def _deep_merge(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        """Deep merge two dictionaries.

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def _key_to_filename(key: str) -> str | None:
        """Convert configuration key to filename.

        Args:
            key: Configuration key

        Returns:
            Filename or None
        """
        mapping = {
            "themes": "themes.json",
            "layouts": "layouts.json",
            "panels": "panels.json",
            "menus": "menus.json",
            "tabs": "tabs.json",
            "lists": "lists.json",
            "i18n_de": "i18n.de.json",
            "i18n_en": "i18n.en.json",
        }
        return mapping.get(key)


class BackupManager:
    """Manage configuration backups."""

    def __init__(self, config_path: Path, max_backups: int = 10) -> None:
        """Initialize backup manager.

        Args:
            config_path: Path to configuration directory
            max_backups: Maximum number of backups to keep
        """
        self.config_path = config_path
        self.max_backups = max_backups
        self.backup_base = config_path.parent

    def create_backup(self, description: str = "") -> Path | None:
        """Create a timestamped backup.

        Args:
            description: Optional description for backup

        Returns:
            Path to backup or None on failure
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}"
            if description:
                backup_name += f"_{description.replace(' ', '_')[:20]}"

            backup_path = self.backup_base / backup_name
            shutil.copytree(self.config_path, backup_path)

            # Cleanup old backups
            self._cleanup_old_backups()

            logger.info(f"Backup created: {backup_path}")
            return backup_path

        except Exception as exc:
            logger.exception(f"Failed to create backup: {exc}")
            return None

    def restore_backup(self, backup_path: Path) -> bool:
        """Restore configuration from backup.

        Args:
            backup_path: Path to backup directory

        Returns:
            True if restore was successful
        """
        try:
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False

            # Create safety backup of current state before restore
            self.create_backup("pre_restore")

            # Remove current config
            shutil.rmtree(self.config_path)

            # Copy backup to config path
            shutil.copytree(backup_path, self.config_path)

            logger.info(f"Configuration restored from {backup_path}")
            return True

        except Exception as exc:
            logger.exception(f"Failed to restore backup: {exc}")
            return False

    def list_backups(self) -> list[Path]:
        """List available backups.

        Returns:
            List of backup directory paths
        """
        pattern = "config_backup_*"
        backups = sorted(
            self.backup_base.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return backups

    def delete_backup(self, backup_path: Path) -> bool:
        """Delete a backup.

        Args:
            backup_path: Path to backup to delete

        Returns:
            True if deletion was successful
        """
        try:
            if backup_path.exists():
                shutil.rmtree(backup_path)
                logger.info(f"Backup deleted: {backup_path}")
                return True
            return False
        except Exception as exc:
            logger.exception(f"Failed to delete backup: {exc}")
            return False

    def _cleanup_old_backups(self) -> None:
        """Remove old backups exceeding max_backups limit."""
        backups = self.list_backups()
        if len(backups) > self.max_backups:
            for old_backup in backups[self.max_backups:]:
                self.delete_backup(old_backup)
