"""Tests for ConfigValidator - comprehensive coverage of all methods and branches."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from widgetsystem.core.config_validator import (
    CONFIG_SCHEMAS,
    ConfigValidationError,
    ConfigValidator,
    get_validator,
)


pytestmark = pytest.mark.isolated


# ---------------------------------------------------------------------------
# ConfigValidationError
# ---------------------------------------------------------------------------


def test_config_validation_error_basic():
    """Error should store message, field, and value."""
    err = ConfigValidationError("bad value", field="id", value="!!!")
    assert str(err) == "bad value"
    assert err.field == "id"
    assert err.value == "!!!"


def test_config_validation_error_no_field():
    """Error without field/value should default to None."""
    err = ConfigValidationError("oops")
    assert err.field is None
    assert err.value is None


# ---------------------------------------------------------------------------
# ConfigValidator.__init__
# ---------------------------------------------------------------------------


def test_init_creates_backup_dir(tmp_path: Path):
    """Constructor should create backup_dir on disk."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    validator = ConfigValidator(cfg_dir)
    assert validator.backup_dir.exists()
    assert validator.backup_dir == cfg_dir / ".backup"


def test_init_custom_backup_dir(tmp_path: Path):
    """Custom backup_dir should be used and created."""
    cfg_dir = tmp_path / "cfg"
    bak_dir = tmp_path / "bak"
    cfg_dir.mkdir()
    validator = ConfigValidator(cfg_dir, bak_dir)
    assert validator.backup_dir == bak_dir
    assert bak_dir.exists()


# ---------------------------------------------------------------------------
# validate_id
# ---------------------------------------------------------------------------


def test_validate_id_valid():
    """Valid ID should be returned sanitized (lowercase)."""
    v = ConfigValidator(Path())
    result = v.validate_id("MyWidget")
    assert result == "mywidget"


def test_validate_id_empty_raises():
    """Empty ID should raise ConfigValidationError."""
    v = ConfigValidator(Path())
    with pytest.raises(ConfigValidationError, match="cannot be empty"):
        v.validate_id("")


def test_validate_id_too_long_raises():
    """ID longer than MAX_ID_LENGTH should raise."""
    v = ConfigValidator(Path())
    long_id = "a" * (ConfigValidator.MAX_ID_LENGTH + 1)
    with pytest.raises(ConfigValidationError, match="too long"):
        v.validate_id(long_id)


def test_validate_id_special_chars_replaced():
    """Special characters should be replaced with underscore."""
    v = ConfigValidator(Path())
    result = v.validate_id("my-widget.id")
    assert "-" not in result
    assert "." not in result


def test_validate_id_starts_with_digit_gets_prefix():
    """ID starting with digit should receive 'id_' prefix."""
    v = ConfigValidator(Path())
    result = v.validate_id("1widget")
    assert result.startswith("id_")


def test_validate_id_reserved_name_gets_prefix():
    """Reserved names should be prefixed with 'custom_'."""
    v = ConfigValidator(Path())
    result = v.validate_id("default")
    assert result.startswith("custom_")


def test_validate_id_custom_field_name_in_error():
    """Error message should include the custom field_name."""
    v = ConfigValidator(Path())
    with pytest.raises(ConfigValidationError, match="my_field"):
        v.validate_id("", field_name="my_field")


# ---------------------------------------------------------------------------
# validate_name
# ---------------------------------------------------------------------------


def test_validate_name_valid():
    """Valid name should be returned stripped."""
    v = ConfigValidator(Path())
    result = v.validate_name("  My Tab  ")
    assert result == "My Tab"


def test_validate_name_empty_raises():
    """Empty name should raise ConfigValidationError."""
    v = ConfigValidator(Path())
    with pytest.raises(ConfigValidationError, match="cannot be empty"):
        v.validate_name("")


def test_validate_name_too_long_raises():
    """Name longer than MAX_NAME_LENGTH should raise."""
    v = ConfigValidator(Path())
    long_name = "a" * (ConfigValidator.MAX_NAME_LENGTH + 1)
    with pytest.raises(ConfigValidationError, match="too long"):
        v.validate_name(long_name)


def test_validate_name_strips_dangerous_chars():
    """Dangerous characters like < > : should be removed."""
    v = ConfigValidator(Path())
    result = v.validate_name("My<Widget>Name")
    assert "<" not in result
    assert ">" not in result


def test_validate_name_only_invalid_chars_raises():
    """Name containing only invalid characters should raise."""
    v = ConfigValidator(Path())
    with pytest.raises(ConfigValidationError, match="only invalid"):
        v.validate_name("<>:/\\")


# ---------------------------------------------------------------------------
# validate_structure
# ---------------------------------------------------------------------------


def test_validate_structure_required_field_missing():
    """Missing required field should produce an error."""
    v = ConfigValidator(Path())
    schema = {"required": {"id": {"type": "string"}}, "optional": {}}
    errors = v.validate_structure({"title": "X"}, schema)
    assert any("id" in e for e in errors)


def test_validate_structure_optional_field_present():
    """Optional field present and valid should produce no errors."""
    v = ConfigValidator(Path())
    schema = {
        "required": {"id": {"type": "string"}},
        "optional": {"closable": {"type": "boolean"}},
    }
    errors = v.validate_structure({"id": "a", "closable": True}, schema)
    assert errors == []


def test_validate_structure_unknown_field_reported():
    """Unknown field in strict schema should be reported."""
    v = ConfigValidator(Path())
    schema = {"required": {}, "optional": {}, "allow_extra": False}
    errors = v.validate_structure({"unknown_key": 1}, schema)
    assert any("Unknown field" in e for e in errors)


def test_validate_structure_allow_extra_suppresses_unknown():
    """allow_extra=True should suppress unknown field errors."""
    v = ConfigValidator(Path())
    schema = {"required": {}, "optional": {}, "allow_extra": True}
    errors = v.validate_structure({"anything": "goes"}, schema)
    assert errors == []


def test_validate_structure_depth_exceeded():
    """Exceeding MAX_NESTING_DEPTH should return a depth error."""
    v = ConfigValidator(Path())
    errors = v.validate_structure(
        {}, {"required": {}}, path="root", depth=ConfigValidator.MAX_NESTING_DEPTH + 1
    )
    assert any("depth" in e.lower() for e in errors)


def test_validate_structure_list_items():
    """List items should be validated individually."""
    v = ConfigValidator(Path())
    schema: dict = {"items": {"type": "string"}}
    errors = v.validate_structure(["ok", 42], schema)
    assert any("Expected string" in e for e in errors)


# ---------------------------------------------------------------------------
# _validate_field - type branches
# ---------------------------------------------------------------------------


def test_validate_field_string_wrong_type():
    """Non-string value for string field should produce error."""
    v = ConfigValidator(Path())
    errors = v._validate_field(42, {"type": "string"}, "path.field", 0)
    assert any("Expected string" in e for e in errors)


def test_validate_field_string_id_format():
    """String field with id_format=True should validate via validate_id."""
    v = ConfigValidator(Path())
    # "1bad" starts with digit → sanitized to "id_1bad" → valid
    errors = v._validate_field("ValidID", {"type": "string", "id_format": True}, "f", 0)
    assert errors == []


def test_validate_field_string_name_format_invalid():
    """String field with name_format and only-invalid chars should error."""
    v = ConfigValidator(Path())
    errors = v._validate_field("<>", {"type": "string", "name_format": True}, "f", 0)
    assert errors  # should have at least one error


def test_validate_field_number_ok():
    """Valid number within range should produce no errors."""
    v = ConfigValidator(Path())
    errors = v._validate_field(5, {"type": "number", "min": 0, "max": 10}, "f", 0)
    assert errors == []


def test_validate_field_number_below_min():
    """Number below min should produce error."""
    v = ConfigValidator(Path())
    errors = v._validate_field(-1, {"type": "number", "min": 0}, "f", 0)
    assert any("minimum" in e for e in errors)


def test_validate_field_number_above_max():
    """Number above max should produce error."""
    v = ConfigValidator(Path())
    errors = v._validate_field(11, {"type": "number", "max": 10}, "f", 0)
    assert any("maximum" in e for e in errors)


def test_validate_field_number_wrong_type():
    """String value for number field should produce error."""
    v = ConfigValidator(Path())
    errors = v._validate_field("hello", {"type": "number"}, "f", 0)
    assert any("Expected number" in e for e in errors)


def test_validate_field_boolean_ok():
    """Valid boolean should produce no errors."""
    v = ConfigValidator(Path())
    assert v._validate_field(True, {"type": "boolean"}, "f", 0) == []


def test_validate_field_boolean_wrong_type():
    """Non-boolean for boolean field should produce error."""
    v = ConfigValidator(Path())
    errors = v._validate_field(1, {"type": "boolean"}, "f", 0)
    assert any("Expected boolean" in e for e in errors)


def test_validate_field_array_ok():
    """Valid array should produce no errors."""
    v = ConfigValidator(Path())
    errors = v._validate_field([], {"type": "array", "items": {}}, "f", 0)
    assert errors == []


def test_validate_field_array_wrong_type():
    """Dict for array field should produce error."""
    v = ConfigValidator(Path())
    errors = v._validate_field({}, {"type": "array"}, "f", 0)
    assert any("Expected array" in e for e in errors)


def test_validate_field_object_ok():
    """Valid object should produce no errors."""
    v = ConfigValidator(Path())
    schema = {"type": "object", "required": {}, "optional": {}, "allow_extra": True}
    errors = v._validate_field({"x": 1}, schema, "f", 0)
    assert errors == []


def test_validate_field_object_wrong_type():
    """Non-dict for object field should produce error."""
    v = ConfigValidator(Path())
    errors = v._validate_field("not-a-dict", {"type": "object"}, "f", 0)
    assert any("Expected object" in e for e in errors)


# ---------------------------------------------------------------------------
# create_backup / get_latest_backup / _cleanup_old_backups
# ---------------------------------------------------------------------------


def test_create_backup_creates_file(tmp_path: Path):
    """create_backup should produce a .json file in backup_dir."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "tabs.json"
    config_file.write_text('{"tabs": []}', encoding="utf-8")

    v = ConfigValidator(cfg_dir)
    backup_path = v.create_backup(config_file)
    assert backup_path.exists()
    assert backup_path.parent == v.backup_dir


def test_create_backup_missing_file_raises(tmp_path: Path):
    """create_backup on missing file should raise FileNotFoundError."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    v = ConfigValidator(cfg_dir)
    with pytest.raises(FileNotFoundError):
        v.create_backup(cfg_dir / "nonexistent.json")


def test_get_latest_backup_returns_none_when_empty(tmp_path: Path):
    """get_latest_backup should return None when no backups exist."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    v = ConfigValidator(cfg_dir)
    assert v.get_latest_backup("tabs") is None


def test_get_latest_backup_returns_most_recent(tmp_path: Path):
    """get_latest_backup should return the newest backup."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "tabs.json"
    config_file.write_text("{}", encoding="utf-8")

    v = ConfigValidator(cfg_dir)
    v.create_backup(config_file)
    v.create_backup(config_file)

    latest = v.get_latest_backup("tabs")
    assert latest is not None
    assert latest.exists()


def test_cleanup_old_backups_keeps_max(tmp_path: Path):
    """_cleanup_old_backups should keep at most max_backups files."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "panels.json"
    config_file.write_text("{}", encoding="utf-8")

    v = ConfigValidator(cfg_dir)
    # Create 7 backups
    for _ in range(7):
        v.create_backup(config_file)

    remaining = list(v.backup_dir.glob("panels_*.json"))
    assert len(remaining) <= 5


# ---------------------------------------------------------------------------
# load_with_failsafe
# ---------------------------------------------------------------------------


def test_load_with_failsafe_success(tmp_path: Path):
    """load_with_failsafe should return parsed JSON on success."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "tabs.json"
    config_file.write_text('{"tabs": []}', encoding="utf-8")

    v = ConfigValidator(cfg_dir)
    data = v.load_with_failsafe(config_file)
    assert data == {"tabs": []}


def test_load_with_failsafe_corrupt_falls_back_to_backup(tmp_path: Path):
    """load_with_failsafe should restore from backup when main file is invalid JSON."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    good_data = {"tabs": [{"id": "main"}]}
    config_file = cfg_dir / "tabs.json"
    config_file.write_text(json.dumps(good_data), encoding="utf-8")

    v = ConfigValidator(cfg_dir)
    # Create a valid backup first, then corrupt the main file
    v.create_backup(config_file)
    config_file.write_text("{INVALID JSON}", encoding="utf-8")

    data = v.load_with_failsafe(config_file)
    assert data == good_data


def test_load_with_failsafe_no_backup_raises(tmp_path: Path):
    """load_with_failsafe should raise ConfigValidationError when no backup exists."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "tabs.json"
    config_file.write_text("{BAD}", encoding="utf-8")

    v = ConfigValidator(cfg_dir)
    with pytest.raises(ConfigValidationError):
        v.load_with_failsafe(config_file)


# ---------------------------------------------------------------------------
# save_with_backup
# ---------------------------------------------------------------------------


def test_save_with_backup_creates_file(tmp_path: Path):
    """save_with_backup should write data to the config file."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "new.json"

    v = ConfigValidator(cfg_dir)
    v.save_with_backup(config_file, {"key": "value"}, validate=False)
    assert config_file.exists()
    assert json.loads(config_file.read_text(encoding="utf-8")) == {"key": "value"}


def test_save_with_backup_creates_backup_of_existing(tmp_path: Path):
    """save_with_backup should back up the existing file before overwriting."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "tabs.json"
    config_file.write_text('{"old": true}', encoding="utf-8")

    v = ConfigValidator(cfg_dir)
    v.save_with_backup(config_file, {"new": True}, validate=False)

    backups = list(v.backup_dir.glob("tabs_*.json"))
    assert len(backups) == 1


def test_save_with_backup_validation_error_raises(tmp_path: Path):
    """save_with_backup with failing schema should raise ConfigValidationError."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "tabs.json"

    schema = {
        "required": {"id": {"type": "string"}},
        "optional": {},
        "allow_extra": False,
    }
    v = ConfigValidator(cfg_dir)
    with pytest.raises(ConfigValidationError):
        v.save_with_backup(config_file, {"other": "x"}, validate=True, schema=schema)


# ---------------------------------------------------------------------------
# sanitize_config / _sanitize_recursive
# ---------------------------------------------------------------------------


def test_sanitize_config_normalizes_ids():
    """sanitize_config should lowercase IDs."""
    v = ConfigValidator(Path())
    data = {"tabs": [{"id": "MyTab", "title": "Hello World"}]}
    result = v.sanitize_config(data, "tabs")
    assert result["tabs"][0]["id"] == "mytab"


def test_sanitize_config_cleans_title():
    """sanitize_config should strip dangerous chars from titles."""
    v = ConfigValidator(Path())
    data = {"panels": [{"id": "p1", "title": "Good<Title>"}]}
    result = v.sanitize_config(data, "panels")
    assert "<" not in result["panels"][0]["title"]


def test_sanitize_recursive_handles_list():
    """_sanitize_recursive should handle lists of dicts."""
    v = ConfigValidator(Path())
    data = [{"id": "Widget1"}, {"id": "Widget2"}]
    result = v._sanitize_recursive(data, "any")
    assert result[0]["id"] == "widget1"
    assert result[1]["id"] == "widget2"


def test_sanitize_recursive_depth_limit():
    """_sanitize_recursive should stop at MAX_NESTING_DEPTH."""
    v = ConfigValidator(Path())
    # Depth already exceeded — should return object unchanged
    result = v._sanitize_recursive({"id": "UPPER"}, "any", depth=ConfigValidator.MAX_NESTING_DEPTH + 1)
    assert result == {"id": "UPPER"}


def test_sanitize_recursive_passthrough_primitives():
    """_sanitize_recursive should pass through non-dict/list values unchanged."""
    v = ConfigValidator(Path())
    assert v._sanitize_recursive("hello", "any") == "hello"
    assert v._sanitize_recursive(42, "any") == 42


# ---------------------------------------------------------------------------
# CONFIG_SCHEMAS & get_validator
# ---------------------------------------------------------------------------


def test_config_schemas_contains_expected_keys():
    """CONFIG_SCHEMAS should define tabs, panels, dnd schemas."""
    assert "tabs" in CONFIG_SCHEMAS
    assert "panels" in CONFIG_SCHEMAS
    assert "dnd" in CONFIG_SCHEMAS


def test_get_validator_returns_instance(tmp_path: Path):
    """get_validator should return a ConfigValidator for the given path."""
    validator = get_validator(tmp_path)
    assert isinstance(validator, ConfigValidator)
    assert validator.config_dir == tmp_path
