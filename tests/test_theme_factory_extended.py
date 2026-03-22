"""Extended tests for ThemeFactory - Coverage improvement tests."""

import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from widgetsystem.factories.theme_factory import ThemeDefinition, ThemeFactory


class TestThemeDefinitionDataclass:
    """Test ThemeDefinition dataclass."""

    def test_theme_definition_initialization(self) -> None:
        """Test ThemeDefinition initialization with all fields."""
        theme = ThemeDefinition(
            theme_id="dark",
            name="Dark Theme",
            file_path=Path("themes/dark.qss"),
            tab_active_color="#FF0000",
            tab_inactive_color="#00FF00",
        )
        assert theme.theme_id == "dark"
        assert theme.name == "Dark Theme"
        assert theme.file_path == Path("themes/dark.qss")
        assert theme.tab_active_color == "#FF0000"
        assert theme.tab_inactive_color == "#00FF00"

    def test_theme_definition_with_defaults(self) -> None:
        """Test ThemeDefinition with default tab colors."""
        theme = ThemeDefinition(
            theme_id="test",
            name="Test Theme",
            file_path=Path("test.qss"),
        )
        assert theme.theme_id == "test"
        assert theme.tab_active_color == "#E0E0E0"
        assert theme.tab_inactive_color == "#BDBDBD"


class TestThemeFactoryBasics:
    """Test basic ThemeFactory functionality."""

    def test_initialization(self) -> None:
        """Test ThemeFactory initialization."""
        factory = ThemeFactory(config_path="config")
        assert factory.config_path == Path("config")
        assert factory.themes_file == Path("config/themes.json")

    def test_initialization_with_path_object(self) -> None:
        """Test initialization with Path object."""
        factory = ThemeFactory(config_path=Path("config"))
        assert factory.config_path == Path("config")


class TestListThemes:
    """Test theme listing functionality."""

    def test_list_themes_success(self) -> None:
        """Test successfully listing themes from config."""
        factory = ThemeFactory(config_path="config")
        themes = factory.list_themes()
        assert isinstance(themes, list)
        # Config should have at least one theme
        assert len(themes) > 0
        assert all(isinstance(t, ThemeDefinition) for t in themes)

    def test_list_themes_missing_file(self) -> None:
        """Test listing themes when file doesn't exist returns empty list."""
        factory = ThemeFactory(config_path="nonexistent")
        themes = factory.list_themes()
        assert themes == []

    def test_list_themes_invalid_json(self) -> None:
        """Test listing themes with invalid JSON returns empty list."""
        factory = ThemeFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="invalid json")):
            themes = factory.list_themes()
            assert themes == []

    def test_list_themes_not_a_dict(self) -> None:
        """Test listing themes when JSON is not a dict returns empty list."""
        factory = ThemeFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            themes = factory.list_themes()
            assert themes == []

    def test_list_themes_themes_not_array(self) -> None:
        """Test listing themes when 'themes' key is not an array."""
        factory = ThemeFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data='{"themes": "not array"}')):
            themes = factory.list_themes()
            assert themes == []

    def test_list_themes_skips_invalid_entries(self) -> None:
        """Test that invalid theme entries are skipped."""
        factory = ThemeFactory(config_path="config")

        json_data = """{
            "themes": [
                {"id": "theme1", "name": "Theme 1", "file": "theme1.qss"},
                "invalid_entry",
                {"id": "theme2", "name": "Theme 2", "file": "theme2.qss"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                themes = factory.list_themes()
                # Should only get valid entries
                assert len(themes) == 2
                assert themes[0].theme_id == "theme1"
                assert themes[1].theme_id == "theme2"

    def test_list_themes_skips_missing_required_fields(self) -> None:
        """Test that themes with missing required fields are skipped."""
        factory = ThemeFactory(config_path="config")

        json_data = """{
            "themes": [
                {"id": "theme1", "name": "Theme 1"},
                {"id": "theme2", "file": "theme2.qss"},
                {"name": "Theme 3", "file": "theme3.qss"},
                {"id": "theme4", "name": "Theme 4", "file": "theme4.qss"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                themes = factory.list_themes()
                # Only theme4 has all required fields
                assert len(themes) == 1
                assert themes[0].theme_id == "theme4"

    def test_list_themes_resolves_relative_paths(self) -> None:
        """Test that relative theme file paths are resolved."""
        factory = ThemeFactory(config_path="config")

        json_data = """{
            "themes": [
                {"id": "theme1", "name": "Theme 1", "file": "themes/dark.qss"}
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                themes = factory.list_themes()
                assert len(themes) == 1
                # Path should be resolved and absolute
                assert themes[0].file_path.is_absolute()

    def test_list_themes_with_tab_colors(self) -> None:
        """Test parsing themes with tab colors."""
        factory = ThemeFactory(config_path="config")

        json_data = """{
            "themes": [
                {
                    "id": "custom",
                    "name": "Custom Theme",
                    "file": "custom.qss",
                    "tab_colors": {
                        "active": "#FF0000",
                        "inactive": "#00FF00"
                    }
                }
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                themes = factory.list_themes()
                assert len(themes) == 1
                assert themes[0].tab_active_color == "#FF0000"
                assert themes[0].tab_inactive_color == "#00FF00"

    def test_list_themes_with_partial_tab_colors(self) -> None:
        """Test parsing themes with partial tab colors uses defaults."""
        factory = ThemeFactory(config_path="config")

        json_data = """{
            "themes": [
                {
                    "id": "partial",
                    "name": "Partial Theme",
                    "file": "partial.qss",
                    "tab_colors": {
                        "active": "#FF0000"
                    }
                }
            ]
        }"""

        with patch("builtins.open", mock_open(read_data=json_data)):
            with patch("pathlib.Path.exists", return_value=True):
                themes = factory.list_themes()
                assert len(themes) == 1
                assert themes[0].tab_active_color == "#FF0000"
                assert themes[0].tab_inactive_color == "#BDBDBD"  # Default

    def test_list_themes_handles_os_error(self) -> None:
        """Test that OSError during file reading is handled."""
        factory = ThemeFactory(config_path="config")

        with patch("builtins.open", side_effect=OSError("File read error")):
            with patch("pathlib.Path.exists", return_value=True):
                themes = factory.list_themes()
                assert themes == []


class TestDefaultTheme:
    """Test default theme functionality."""

    def test_get_default_theme_id_success(self) -> None:
        """Test getting default theme ID."""
        factory = ThemeFactory(config_path="config")
        default_id = factory.get_default_theme_id()
        assert isinstance(default_id, str)
        assert len(default_id) > 0

    def test_get_default_theme_id_missing_file(self) -> None:
        """Test getting default theme ID when file doesn't exist."""
        factory = ThemeFactory(config_path="nonexistent")
        default_id = factory.get_default_theme_id()
        assert default_id is None

    def test_get_default_theme_id_invalid_json(self) -> None:
        """Test getting default theme ID with invalid JSON."""
        factory = ThemeFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("pathlib.Path.exists", return_value=True):
                default_id = factory.get_default_theme_id()
                assert default_id is None

    def test_get_default_theme_id_not_a_dict(self) -> None:
        """Test getting default theme ID when JSON is not a dict."""
        factory = ThemeFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("pathlib.Path.exists", return_value=True):
                default_id = factory.get_default_theme_id()
                assert default_id is None

    def test_get_default_theme_id_missing_key(self) -> None:
        """Test getting default theme ID when key is missing."""
        factory = ThemeFactory(config_path="config")

        with patch("builtins.open", mock_open(read_data='{"other_key": "value"}')):
            with patch("pathlib.Path.exists", return_value=True):
                default_id = factory.get_default_theme_id()
                assert default_id is None

    def test_get_default_theme(self) -> None:
        """Test getting default theme definition."""
        factory = ThemeFactory(config_path="config")
        theme = factory.get_default_theme()

        if theme:  # May be None if config is not set up
            assert isinstance(theme, ThemeDefinition)
            assert len(theme.theme_id) > 0

    def test_get_default_theme_no_default_id(self) -> None:
        """Test getting default theme when no default ID is set."""
        factory = ThemeFactory(config_path="config")

        with patch.object(factory, "get_default_theme_id", return_value=None):
            theme = factory.get_default_theme()
            assert theme is None

    def test_get_default_theme_id_not_found(self) -> None:
        """Test getting default theme when ID doesn't match any theme."""
        factory = ThemeFactory(config_path="config")

        with patch.object(factory, "get_default_theme_id", return_value="nonexistent"):
            with patch.object(factory, "list_themes", return_value=[]):
                theme = factory.get_default_theme()
                assert theme is None


class TestThemeStylesheet:
    """Test theme stylesheet functionality."""

    def test_get_default_stylesheet(self) -> None:
        """Test getting default theme stylesheet."""
        factory = ThemeFactory(config_path="config")
        stylesheet = factory.get_default_stylesheet()
        assert isinstance(stylesheet, str)

    def test_get_default_stylesheet_no_theme(self) -> None:
        """Test getting stylesheet when no default theme."""
        factory = ThemeFactory(config_path="config")

        with patch.object(factory, "get_default_theme", return_value=None):
            stylesheet = factory.get_default_stylesheet()
            assert stylesheet == ""

    def test_get_default_stylesheet_file_error(self) -> None:
        """Test getting stylesheet when file read fails."""
        factory = ThemeFactory(config_path="config")

        mock_theme = ThemeDefinition(
            theme_id="test",
            name="Test",
            file_path=Path("nonexistent.qss"),
        )

        with patch.object(factory, "get_default_theme", return_value=mock_theme):
            stylesheet = factory.get_default_stylesheet()
            assert stylesheet == ""


class TestTabColors:
    """Test tab colors functionality."""

    def test_get_tab_colors_with_theme(self) -> None:
        """Test getting tab colors from theme."""
        factory = ThemeFactory(config_path="config")

        mock_theme = ThemeDefinition(
            theme_id="test",
            name="Test",
            file_path=Path("test.qss"),
            tab_active_color="#FF0000",
            tab_inactive_color="#00FF00",
        )

        with patch.object(factory, "get_default_theme", return_value=mock_theme):
            active, inactive = factory.get_tab_colors()
            assert active == "#FF0000"
            assert inactive == "#00FF00"

    def test_get_tab_colors_no_theme(self) -> None:
        """Test getting tab colors when no default theme."""
        factory = ThemeFactory(config_path="config")

        with patch.object(factory, "get_default_theme", return_value=None):
            active, inactive = factory.get_tab_colors()
            assert active == "#E0E0E0"  # Default
            assert inactive == "#BDBDBD"  # Default


class TestThemeProfile:
    """Test theme profile functionality."""

    def test_load_profile_placeholder(self) -> None:
        """Test load_profile method exists (placeholder test)."""
        factory = ThemeFactory(config_path="config")
        # Method exists but may not be fully implemented
        assert hasattr(factory, "load_profile")
        assert callable(factory.load_profile)

    def test_load_profile_missing_profiles_dir(self, tmp_path: Path) -> None:
        """Loading profile returns None when profiles dir is missing."""
        factory = ThemeFactory(config_path=tmp_path)
        assert factory.load_profile("missing") is None

    def test_load_profile_missing_profile_file(self, tmp_path: Path) -> None:
        """Loading profile returns None when profile file does not exist."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        factory = ThemeFactory(config_path=tmp_path)
        assert factory.load_profile("missing") is None

    def test_load_profile_success(self, tmp_path: Path) -> None:
        """Loading profile delegates to ThemeProfile.load_from_file."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        (profiles_dir / "profile_a.json").write_text("{}", encoding="utf-8")
        factory = ThemeFactory(config_path=tmp_path)
        sentinel = MagicMock()

        with patch(
            "widgetsystem.factories.theme_factory.ThemeProfile.load_from_file",
            return_value=sentinel,
        ):
            profile = factory.load_profile("profile_a")
            assert profile is sentinel

    def test_load_profile_handles_json_error(self, tmp_path: Path) -> None:
        """Loading profile returns None when parser raises JSON error."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        (profiles_dir / "profile_a.json").write_text("{}", encoding="utf-8")
        factory = ThemeFactory(config_path=tmp_path)

        with patch(
            "widgetsystem.factories.theme_factory.ThemeProfile.load_from_file",
            side_effect=json.JSONDecodeError("x", "{}", 0),
        ):
            assert factory.load_profile("profile_a") is None

    def test_save_profile_success(self, tmp_path: Path) -> None:
        """Saving profile returns True when save succeeds."""
        factory = ThemeFactory(config_path=tmp_path)
        profile = MagicMock()
        assert factory.save_profile(profile, "profile_a") is True
        profile.save_to_file.assert_called_once()

    def test_save_profile_failure(self, tmp_path: Path) -> None:
        """Saving profile returns False when save raises."""
        factory = ThemeFactory(config_path=tmp_path)
        profile = MagicMock()
        profile.save_to_file.side_effect = OSError("write error")
        assert factory.save_profile(profile, "profile_a") is False

    def test_list_profiles_missing_dir(self, tmp_path: Path) -> None:
        """Listing profiles returns empty list when directory is absent."""
        factory = ThemeFactory(config_path=tmp_path)
        assert factory.list_profiles() == []

    def test_list_profiles_returns_stems(self, tmp_path: Path) -> None:
        """Listing profiles returns json file stems."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        (profiles_dir / "dark_transparent.json").write_text("{}", encoding="utf-8")
        (profiles_dir / "light_transparent.json").write_text("{}", encoding="utf-8")

        factory = ThemeFactory(config_path=tmp_path)
        profile_ids = factory.list_profiles()
        assert "dark_transparent" in profile_ids
        assert "light_transparent" in profile_ids

    def test_create_default_profiles_creates_expected_profiles(self, tmp_path: Path) -> None:
        """Default profile generation creates three default profiles."""
        factory = ThemeFactory(config_path=tmp_path)
        saved_ids: list[str] = []

        with patch.object(
            factory,
            "save_profile",
            side_effect=lambda _p, pid: saved_ids.append(pid) or True,
        ):
            factory.create_default_profiles()

        assert "dark_transparent" in saved_ids
        assert "light_transparent" in saved_ids
        assert "solid_dark" in saved_ids

    def test_create_default_profiles_skips_existing_files(self, tmp_path: Path) -> None:
        """Default profile generation skips existing profile files."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        (profiles_dir / "dark_transparent.json").write_text("{}", encoding="utf-8")

        factory = ThemeFactory(config_path=tmp_path)
        saved_ids: list[str] = []
        with patch.object(
            factory,
            "save_profile",
            side_effect=lambda _p, pid: saved_ids.append(pid) or True,
        ):
            factory.create_default_profiles()

        assert "dark_transparent" not in saved_ids
        assert "light_transparent" in saved_ids
        assert "solid_dark" in saved_ids
