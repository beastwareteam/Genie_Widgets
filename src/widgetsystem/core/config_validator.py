"""Config Validator - Validates, sanitizes, and backs up configuration files.

Provides:
- JSON schema validation
- Sanitization of names and special characters
- Automatic backup before modifications
- Failsafe loading from backup on corruption
- Data structure integrity checks
"""

import json
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Raised when config validation fails."""

    def __init__(self, message: str, field: str | None = None, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(message)


class ConfigValidator:
    """Validates and sanitizes configuration files.

    Features:
    - Automatic backup creation
    - Failsafe loading from backup
    - Name/ID sanitization
    - Structure validation
    - Special character prevention
    """

    # Allowed characters in IDs and names
    ALLOWED_ID_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    ALLOWED_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\s\.]+$')

    # Reserved names that cannot be used
    RESERVED_NAMES = frozenset({
        'none', 'null', 'undefined', 'true', 'false',
        'default', 'system', 'root', 'admin', 'config',
    })

    # Max lengths
    MAX_ID_LENGTH = 64
    MAX_NAME_LENGTH = 128
    MAX_NESTING_DEPTH = 5

    def __init__(self, config_dir: Path, backup_dir: Path | None = None):
        """Initialize ConfigValidator.

        Args:
            config_dir: Directory containing config files
            backup_dir: Directory for backups (default: config_dir/.backup)
        """
        self.config_dir = Path(config_dir)
        self.backup_dir = backup_dir or (self.config_dir / ".backup")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def validate_id(self, value: str, field_name: str = "id") -> str:
        """Validate and sanitize an ID field.

        Args:
            value: The ID value to validate
            field_name: Name of the field (for error messages)

        Returns:
            Sanitized ID

        Raises:
            ConfigValidationError: If ID is invalid
        """
        if not value:
            raise ConfigValidationError(f"{field_name} cannot be empty", field_name, value)

        if len(value) > self.MAX_ID_LENGTH:
            raise ConfigValidationError(
                f"{field_name} too long (max {self.MAX_ID_LENGTH})",
                field_name, value
            )

        # Sanitize: lowercase, replace invalid chars with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', value.lower())

        # Ensure starts with letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'id_' + sanitized

        # Check reserved names
        if sanitized in self.RESERVED_NAMES:
            sanitized = f"custom_{sanitized}"

        if not self.ALLOWED_ID_PATTERN.match(sanitized):
            raise ConfigValidationError(
                f"{field_name} contains invalid characters",
                field_name, value
            )

        return sanitized

    def validate_name(self, value: str, field_name: str = "name") -> str:
        """Validate and sanitize a display name.

        Args:
            value: The name to validate
            field_name: Name of the field (for error messages)

        Returns:
            Sanitized name

        Raises:
            ConfigValidationError: If name is invalid
        """
        if not value:
            raise ConfigValidationError(f"{field_name} cannot be empty", field_name, value)

        if len(value) > self.MAX_NAME_LENGTH:
            raise ConfigValidationError(
                f"{field_name} too long (max {self.MAX_NAME_LENGTH})",
                field_name, value
            )

        # Remove dangerous characters but keep spaces, hyphens, underscores
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', value)
        sanitized = sanitized.strip()

        if not sanitized:
            raise ConfigValidationError(
                f"{field_name} contains only invalid characters",
                field_name, value
            )

        return sanitized

    def validate_structure(
        self,
        data: dict | list,
        schema: dict,
        path: str = "",
        depth: int = 0,
    ) -> list[str]:
        """Validate data structure against schema.

        Args:
            data: Data to validate
            schema: Schema definition
            path: Current path (for error messages)
            depth: Current nesting depth

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if depth > self.MAX_NESTING_DEPTH:
            errors.append(f"{path}: Maximum nesting depth ({self.MAX_NESTING_DEPTH}) exceeded")
            return errors

        if isinstance(data, dict):
            # Check required fields
            for field, field_schema in schema.get("required", {}).items():
                if field not in data:
                    errors.append(f"{path}.{field}: Required field missing")
                else:
                    errors.extend(self._validate_field(
                        data[field], field_schema, f"{path}.{field}", depth
                    ))

            # Check optional fields
            for field, field_schema in schema.get("optional", {}).items():
                if field in data:
                    errors.extend(self._validate_field(
                        data[field], field_schema, f"{path}.{field}", depth
                    ))

            # Check for unknown fields
            known_fields = set(schema.get("required", {}).keys()) | set(schema.get("optional", {}).keys())
            for field in data:
                if field not in known_fields and not schema.get("allow_extra", False):
                    errors.append(f"{path}.{field}: Unknown field")

        elif isinstance(data, list):
            item_schema = schema.get("items", {})
            for i, item in enumerate(data):
                errors.extend(self._validate_field(
                    item, item_schema, f"{path}[{i}]", depth + 1
                ))

        return errors

    def _validate_field(
        self,
        value: Any,
        schema: dict,
        path: str,
        depth: int,
    ) -> list[str]:
        """Validate a single field against its schema."""
        errors = []
        expected_type = schema.get("type")

        if expected_type == "string":
            if not isinstance(value, str):
                errors.append(f"{path}: Expected string, got {type(value).__name__}")
            elif schema.get("id_format"):
                try:
                    self.validate_id(value, path)
                except ConfigValidationError as e:
                    errors.append(str(e))
            elif schema.get("name_format"):
                try:
                    self.validate_name(value, path)
                except ConfigValidationError as e:
                    errors.append(str(e))

        elif expected_type == "number":
            if not isinstance(value, (int, float)):
                errors.append(f"{path}: Expected number, got {type(value).__name__}")
            else:
                if "min" in schema and value < schema["min"]:
                    errors.append(f"{path}: Value {value} below minimum {schema['min']}")
                if "max" in schema and value > schema["max"]:
                    errors.append(f"{path}: Value {value} above maximum {schema['max']}")

        elif expected_type == "boolean":
            if not isinstance(value, bool):
                errors.append(f"{path}: Expected boolean, got {type(value).__name__}")

        elif expected_type == "array":
            if not isinstance(value, list):
                errors.append(f"{path}: Expected array, got {type(value).__name__}")
            else:
                errors.extend(self.validate_structure(
                    value, {"items": schema.get("items", {})}, path, depth
                ))

        elif expected_type == "object":
            if not isinstance(value, dict):
                errors.append(f"{path}: Expected object, got {type(value).__name__}")
            else:
                errors.extend(self.validate_structure(
                    value, schema, path, depth + 1
                ))

        return errors

    def create_backup(self, config_file: Path) -> Path:
        """Create a backup of a config file.

        Args:
            config_file: Path to config file

        Returns:
            Path to backup file
        """
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{config_file.stem}_{timestamp}{config_file.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(config_file, backup_path)
        logger.info(f"Created backup: {backup_path}")

        # Keep only last N backups
        self._cleanup_old_backups(config_file.stem, max_backups=5)

        return backup_path

    def _cleanup_old_backups(self, prefix: str, max_backups: int = 5) -> None:
        """Remove old backups keeping only the most recent ones."""
        pattern = f"{prefix}_*.json"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)

        for old_backup in backups[max_backups:]:
            old_backup.unlink()
            logger.debug(f"Removed old backup: {old_backup}")

    def get_latest_backup(self, config_name: str) -> Path | None:
        """Get the most recent backup for a config file.

        Args:
            config_name: Name of config file (without extension)

        Returns:
            Path to latest backup or None
        """
        pattern = f"{config_name}_*.json"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)
        return backups[0] if backups else None

    def load_with_failsafe(self, config_file: Path) -> dict:
        """Load config file with automatic failsafe to backup.

        Args:
            config_file: Path to config file

        Returns:
            Loaded config data

        Raises:
            ConfigValidationError: If both main and backup fail
        """
        # Try loading main config
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded config: {config_file}")
            return data

        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Failed to load {config_file}: {e}")

            # Try loading from backup
            backup = self.get_latest_backup(config_file.stem)
            if backup:
                try:
                    with open(backup, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    logger.info(f"Loaded from backup: {backup}")

                    # Restore backup to main file
                    shutil.copy2(backup, config_file)
                    logger.info(f"Restored {config_file} from backup")

                    return data

                except (json.JSONDecodeError, FileNotFoundError) as backup_e:
                    logger.error(f"Backup also failed: {backup_e}")

            raise ConfigValidationError(
                f"Failed to load config and no valid backup available: {config_file}"
            )

    def save_with_backup(
        self,
        config_file: Path,
        data: dict,
        validate: bool = True,
        schema: dict | None = None,
    ) -> None:
        """Save config file with automatic backup.

        Args:
            config_file: Path to config file
            data: Data to save
            validate: Whether to validate before saving
            schema: Optional schema for validation
        """
        # Create backup of existing file
        if config_file.exists():
            self.create_backup(config_file)

        # Validate if requested
        if validate and schema:
            errors = self.validate_structure(data, schema)
            if errors:
                raise ConfigValidationError(
                    f"Validation failed: {'; '.join(errors[:5])}"
                )

        # Save
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved config: {config_file}")

    def sanitize_config(self, data: dict, config_type: str) -> dict:
        """Sanitize all IDs and names in a config structure.

        Args:
            data: Config data to sanitize
            config_type: Type of config (tabs, panels, etc.)

        Returns:
            Sanitized config data
        """
        return self._sanitize_recursive(data, config_type)

    def _sanitize_recursive(self, obj: Any, config_type: str, depth: int = 0) -> Any:
        """Recursively sanitize config data."""
        if depth > self.MAX_NESTING_DEPTH:
            return obj

        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                # Sanitize ID fields
                if key == "id" and isinstance(value, str):
                    result[key] = self.validate_id(value, key)
                # Sanitize title/name fields
                elif key in ("title", "name", "label") and isinstance(value, str):
                    result[key] = self.validate_name(value, key)
                else:
                    result[key] = self._sanitize_recursive(value, config_type, depth + 1)
            return result

        elif isinstance(obj, list):
            return [self._sanitize_recursive(item, config_type, depth + 1) for item in obj]

        return obj


# Pre-defined schemas for common config types
CONFIG_SCHEMAS = {
    "tabs": {
        "required": {},
        "optional": {
            "tabs": {"type": "array", "items": {
                "type": "object",
                "required": {
                    "id": {"type": "string", "id_format": True},
                },
                "optional": {
                    "title_key": {"type": "string"},
                    "closable": {"type": "boolean"},
                    "movable": {"type": "boolean"},
                    "floatable": {"type": "boolean"},
                    "children": {"type": "array"},
                    "component": {"type": "string"},
                },
                "allow_extra": True,
            }},
        },
        "allow_extra": True,
    },
    "panels": {
        "required": {},
        "optional": {
            "panels": {"type": "array", "items": {
                "type": "object",
                "required": {
                    "id": {"type": "string", "id_format": True},
                },
                "optional": {
                    "title_key": {"type": "string"},
                    "area": {"type": "string"},
                    "closable": {"type": "boolean"},
                    "movable": {"type": "boolean"},
                    "floatable": {"type": "boolean"},
                    "dnd_enabled": {"type": "boolean"},
                },
                "allow_extra": True,
            }},
        },
        "allow_extra": True,
    },
    "dnd": {
        "required": {},
        "optional": {
            "drop_zones": {"type": "array"},
            "movement_rules": {"type": "array"},
            "global_settings": {"type": "object"},
        },
        "allow_extra": True,
    },
}


def get_validator(config_dir: Path | str) -> ConfigValidator:
    """Get a ConfigValidator instance for the given directory.

    Args:
        config_dir: Path to config directory

    Returns:
        ConfigValidator instance
    """
    return ConfigValidator(Path(config_dir))
