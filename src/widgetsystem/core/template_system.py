"""Template System for configuration management.

Provides functionality for:
- Creating and managing configuration templates
- Applying templates to create new configurations
- Template inheritance and composition
- Built-in templates for common use cases
"""

import copy
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


@dataclass
class TemplateMetadata:
    """Metadata for a configuration template."""

    id: str
    name: str
    description: str = ""
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    author: str = ""
    version: str = "1.0.0"
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    parent_template: str | None = None
    is_builtin: bool = False


@dataclass
class ConfigurationTemplate:
    """A configuration template with metadata and content."""

    metadata: TemplateMetadata
    content: dict[str, Any]
    variables: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "metadata": {
                "id": self.metadata.id,
                "name": self.metadata.name,
                "description": self.metadata.description,
                "category": self.metadata.category,
                "tags": self.metadata.tags,
                "author": self.metadata.author,
                "version": self.metadata.version,
                "created_date": self.metadata.created_date,
                "modified_date": self.metadata.modified_date,
                "parent_template": self.metadata.parent_template,
                "is_builtin": self.metadata.is_builtin,
            },
            "content": self.content,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConfigurationTemplate":
        """Create template from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            ConfigurationTemplate instance
        """
        metadata_data = data.get("metadata", {})
        metadata = TemplateMetadata(
            id=metadata_data.get("id", "unknown"),
            name=metadata_data.get("name", "Unknown"),
            description=metadata_data.get("description", ""),
            category=metadata_data.get("category", "general"),
            tags=metadata_data.get("tags", []),
            author=metadata_data.get("author", ""),
            version=metadata_data.get("version", "1.0.0"),
            created_date=metadata_data.get("created_date", datetime.now().isoformat()),
            modified_date=metadata_data.get("modified_date", datetime.now().isoformat()),
            parent_template=metadata_data.get("parent_template"),
            is_builtin=metadata_data.get("is_builtin", False),
        )
        return cls(
            metadata=metadata,
            content=data.get("content", {}),
            variables=data.get("variables", {}),
        )


class TemplateManager(QObject):
    """Manager for configuration templates.

    Signals:
        templateCreated: Emitted when template is created (template_id)
        templateDeleted: Emitted when template is deleted (template_id)
        templateApplied: Emitted when template is applied (template_id)
        templateUpdated: Emitted when template is updated (template_id)
    """

    templateCreated = Signal(str)
    templateDeleted = Signal(str)
    templateApplied = Signal(str)
    templateUpdated = Signal(str)

    def __init__(
        self,
        templates_path: Path | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Initialize template manager.

        Args:
            templates_path: Path to templates directory
            parent: Parent QObject
        """
        super().__init__(parent)
        self.templates_path = templates_path or Path("templates")
        self.templates: dict[str, ConfigurationTemplate] = {}
        self._variable_processors: dict[str, Callable[[str, dict], str]] = {}

        # Ensure templates directory exists
        self.templates_path.mkdir(parents=True, exist_ok=True)

        # Load templates
        self._load_templates()
        self._load_builtin_templates()

        logger.debug(f"TemplateManager initialized with {len(self.templates)} templates")

    def _load_templates(self) -> None:
        """Load templates from directory."""
        for template_file in self.templates_path.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    template = ConfigurationTemplate.from_dict(data)
                    self.templates[template.metadata.id] = template
                    logger.debug(f"Loaded template: {template.metadata.name}")
            except Exception as exc:
                logger.warning(f"Failed to load template {template_file}: {exc}")

    def _load_builtin_templates(self) -> None:
        """Load built-in templates."""
        builtin_templates = [
            self._create_minimal_layout_template(),
            self._create_developer_layout_template(),
            self._create_dashboard_layout_template(),
            self._create_dark_theme_template(),
            self._create_light_theme_template(),
        ]

        for template in builtin_templates:
            if template.metadata.id not in self.templates:
                self.templates[template.metadata.id] = template

    def _create_minimal_layout_template(self) -> ConfigurationTemplate:
        """Create minimal layout template."""
        return ConfigurationTemplate(
            metadata=TemplateMetadata(
                id="builtin_minimal",
                name="Minimal Layout",
                description="A clean, minimal layout with essential panels only",
                category="layouts",
                tags=["minimal", "clean", "simple"],
                author="WidgetSystem",
                is_builtin=True,
            ),
            content={
                "panels": [
                    {
                        "id": "main_panel",
                        "name": "{{panel_name}}",
                        "area": "center",
                        "closable": False,
                    },
                ],
                "layout": {
                    "type": "single",
                    "main_area": "center",
                },
            },
            variables={
                "panel_name": "Main Panel",
            },
        )

    def _create_developer_layout_template(self) -> ConfigurationTemplate:
        """Create developer layout template."""
        return ConfigurationTemplate(
            metadata=TemplateMetadata(
                id="builtin_developer",
                name="Developer Layout",
                description="IDE-style layout with file browser, editor, and console",
                category="layouts",
                tags=["developer", "ide", "coding"],
                author="WidgetSystem",
                is_builtin=True,
            ),
            content={
                "panels": [
                    {
                        "id": "file_browser",
                        "name": "{{browser_name}}",
                        "area": "left",
                        "width": 250,
                        "closable": True,
                    },
                    {
                        "id": "editor",
                        "name": "{{editor_name}}",
                        "area": "center",
                        "closable": False,
                    },
                    {
                        "id": "console",
                        "name": "{{console_name}}",
                        "area": "bottom",
                        "height": 200,
                        "closable": True,
                    },
                    {
                        "id": "properties",
                        "name": "{{properties_name}}",
                        "area": "right",
                        "width": 300,
                        "closable": True,
                    },
                ],
                "layout": {
                    "type": "ide",
                    "main_area": "center",
                },
            },
            variables={
                "browser_name": "Files",
                "editor_name": "Editor",
                "console_name": "Console",
                "properties_name": "Properties",
            },
        )

    def _create_dashboard_layout_template(self) -> ConfigurationTemplate:
        """Create dashboard layout template."""
        return ConfigurationTemplate(
            metadata=TemplateMetadata(
                id="builtin_dashboard",
                name="Dashboard Layout",
                description="Multi-panel dashboard with widgets",
                category="layouts",
                tags=["dashboard", "widgets", "overview"],
                author="WidgetSystem",
                is_builtin=True,
            ),
            content={
                "panels": [
                    {
                        "id": "widget_1",
                        "name": "{{widget1_name}}",
                        "area": "left",
                        "width": 400,
                    },
                    {
                        "id": "widget_2",
                        "name": "{{widget2_name}}",
                        "area": "center",
                    },
                    {
                        "id": "widget_3",
                        "name": "{{widget3_name}}",
                        "area": "right",
                        "width": 400,
                    },
                    {
                        "id": "widget_4",
                        "name": "{{widget4_name}}",
                        "area": "bottom",
                        "height": 250,
                    },
                ],
                "layout": {
                    "type": "dashboard",
                    "columns": 3,
                },
            },
            variables={
                "widget1_name": "Widget 1",
                "widget2_name": "Widget 2",
                "widget3_name": "Widget 3",
                "widget4_name": "Widget 4",
            },
        )

    def _create_dark_theme_template(self) -> ConfigurationTemplate:
        """Create dark theme template."""
        return ConfigurationTemplate(
            metadata=TemplateMetadata(
                id="builtin_dark_theme",
                name="Dark Theme",
                description="Modern dark theme with customizable accent color",
                category="themes",
                tags=["dark", "theme", "modern"],
                author="WidgetSystem",
                is_builtin=True,
            ),
            content={
                "id": "custom_dark",
                "name": "{{theme_name}}",
                "colors": {
                    "background": "{{background_color}}",
                    "foreground": "{{foreground_color}}",
                    "accent": "{{accent_color}}",
                    "border": "#404040",
                    "selection": "{{accent_color}}40",
                },
                "font_size": "{{font_size}}",
            },
            variables={
                "theme_name": "Custom Dark",
                "background_color": "#1E1E1E",
                "foreground_color": "#FFFFFF",
                "accent_color": "#0078D4",
                "font_size": 12,
            },
        )

    def _create_light_theme_template(self) -> ConfigurationTemplate:
        """Create light theme template."""
        return ConfigurationTemplate(
            metadata=TemplateMetadata(
                id="builtin_light_theme",
                name="Light Theme",
                description="Clean light theme with customizable accent color",
                category="themes",
                tags=["light", "theme", "clean"],
                author="WidgetSystem",
                is_builtin=True,
            ),
            content={
                "id": "custom_light",
                "name": "{{theme_name}}",
                "colors": {
                    "background": "{{background_color}}",
                    "foreground": "{{foreground_color}}",
                    "accent": "{{accent_color}}",
                    "border": "#E0E0E0",
                    "selection": "{{accent_color}}40",
                },
                "font_size": "{{font_size}}",
            },
            variables={
                "theme_name": "Custom Light",
                "background_color": "#FFFFFF",
                "foreground_color": "#000000",
                "accent_color": "#0078D4",
                "font_size": 12,
            },
        )

    def get_template(self, template_id: str) -> ConfigurationTemplate | None:
        """Get template by ID.

        Args:
            template_id: Template ID

        Returns:
            Template or None if not found
        """
        return self.templates.get(template_id)

    def list_templates(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> list[ConfigurationTemplate]:
        """List templates with optional filtering.

        Args:
            category: Filter by category
            tags: Filter by tags (any match)

        Returns:
            List of matching templates
        """
        result = list(self.templates.values())

        if category:
            result = [t for t in result if t.metadata.category == category]

        if tags:
            result = [
                t for t in result
                if any(tag in t.metadata.tags for tag in tags)
            ]

        return result

    def create_template(
        self,
        template_id: str,
        name: str,
        content: dict[str, Any],
        description: str = "",
        category: str = "general",
        tags: list[str] | None = None,
        variables: dict[str, Any] | None = None,
    ) -> ConfigurationTemplate:
        """Create a new template.

        Args:
            template_id: Unique template ID
            name: Template name
            content: Template content
            description: Template description
            category: Template category
            tags: Template tags
            variables: Template variables

        Returns:
            Created template
        """
        metadata = TemplateMetadata(
            id=template_id,
            name=name,
            description=description,
            category=category,
            tags=tags or [],
        )

        template = ConfigurationTemplate(
            metadata=metadata,
            content=content,
            variables=variables or {},
        )

        self.templates[template_id] = template
        self._save_template(template)
        self.templateCreated.emit(template_id)

        logger.info(f"Created template: {name}")
        return template

    def update_template(
        self,
        template_id: str,
        content: dict[str, Any] | None = None,
        variables: dict[str, Any] | None = None,
        **metadata_updates: Any,
    ) -> bool:
        """Update an existing template.

        Args:
            template_id: Template ID
            content: New content (optional)
            variables: New variables (optional)
            **metadata_updates: Metadata field updates

        Returns:
            True if update was successful
        """
        template = self.templates.get(template_id)
        if not template:
            return False

        if template.metadata.is_builtin:
            logger.warning(f"Cannot modify builtin template: {template_id}")
            return False

        if content is not None:
            template.content = content

        if variables is not None:
            template.variables = variables

        # Update metadata
        for key, value in metadata_updates.items():
            if hasattr(template.metadata, key) and key != "is_builtin":
                setattr(template.metadata, key, value)

        template.metadata.modified_date = datetime.now().isoformat()

        self._save_template(template)
        self.templateUpdated.emit(template_id)

        logger.info(f"Updated template: {template_id}")
        return True

    def delete_template(self, template_id: str) -> bool:
        """Delete a template.

        Args:
            template_id: Template ID

        Returns:
            True if deletion was successful
        """
        template = self.templates.get(template_id)
        if not template:
            return False

        if template.metadata.is_builtin:
            logger.warning(f"Cannot delete builtin template: {template_id}")
            return False

        # Remove from memory
        del self.templates[template_id]

        # Remove file
        template_file = self.templates_path / f"{template_id}.json"
        if template_file.exists():
            template_file.unlink()

        self.templateDeleted.emit(template_id)
        logger.info(f"Deleted template: {template_id}")
        return True

    def apply_template(
        self,
        template_id: str,
        variable_overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Apply a template with variable substitution.

        Args:
            template_id: Template ID
            variable_overrides: Override template variables

        Returns:
            Rendered configuration or None
        """
        template = self.templates.get(template_id)
        if not template:
            logger.warning(f"Template not found: {template_id}")
            return None

        # Merge variables
        variables = {**template.variables, **(variable_overrides or {})}

        # Deep copy content
        content = copy.deepcopy(template.content)

        # Apply variable substitution
        rendered = self._render_content(content, variables)

        self.templateApplied.emit(template_id)
        logger.info(f"Applied template: {template.metadata.name}")

        return rendered

    def create_from_existing(
        self,
        config: dict[str, Any],
        template_id: str,
        name: str,
        description: str = "",
        category: str = "general",
        extract_variables: bool = True,
    ) -> ConfigurationTemplate:
        """Create a template from existing configuration.

        Args:
            config: Existing configuration
            template_id: New template ID
            name: Template name
            description: Template description
            category: Template category
            extract_variables: Auto-extract variables from config

        Returns:
            Created template
        """
        content = copy.deepcopy(config)
        variables: dict[str, Any] = {}

        if extract_variables:
            # Extract common variable candidates
            variables = self._extract_variables(content)
            content = self._replace_with_variables(content, variables)

        return self.create_template(
            template_id=template_id,
            name=name,
            content=content,
            description=description,
            category=category,
            variables=variables,
        )

    def _save_template(self, template: ConfigurationTemplate) -> None:
        """Save template to file.

        Args:
            template: Template to save
        """
        if template.metadata.is_builtin:
            return

        template_file = self.templates_path / f"{template.metadata.id}.json"
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)

    def _render_content(
        self,
        content: Any,
        variables: dict[str, Any],
    ) -> Any:
        """Recursively render content with variable substitution.

        Args:
            content: Content to render
            variables: Variables for substitution

        Returns:
            Rendered content
        """
        if isinstance(content, str):
            # Replace {{variable}} patterns
            for var_name, var_value in variables.items():
                placeholder = "{{" + var_name + "}}"
                if placeholder in content:
                    if content == placeholder:
                        # Entire string is a variable - preserve type
                        return var_value
                    else:
                        # Part of string - convert to string
                        content = content.replace(placeholder, str(var_value))
            return content

        elif isinstance(content, dict):
            return {
                key: self._render_content(value, variables)
                for key, value in content.items()
            }

        elif isinstance(content, list):
            return [self._render_content(item, variables) for item in content]

        else:
            return content

    def _extract_variables(self, config: dict[str, Any]) -> dict[str, Any]:
        """Extract potential variables from configuration.

        Args:
            config: Configuration to analyze

        Returns:
            Extracted variables
        """
        variables: dict[str, Any] = {}

        # Extract common patterns
        if "name" in config:
            variables["name"] = config["name"]

        if "colors" in config and isinstance(config["colors"], dict):
            for color_name, color_value in config["colors"].items():
                variables[f"{color_name}_color"] = color_value

        return variables

    def _replace_with_variables(
        self,
        content: dict[str, Any],
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Replace values with variable placeholders.

        Args:
            content: Content to modify
            variables: Variables to substitute

        Returns:
            Content with placeholders
        """
        result = copy.deepcopy(content)

        for var_name, var_value in variables.items():
            result = self._replace_value(result, var_value, "{{" + var_name + "}}")

        return result

    def _replace_value(
        self,
        content: Any,
        old_value: Any,
        new_value: str,
    ) -> Any:
        """Recursively replace values in content.

        Args:
            content: Content to search
            old_value: Value to replace
            new_value: Replacement string

        Returns:
            Modified content
        """
        if content == old_value:
            return new_value
        elif isinstance(content, dict):
            return {
                key: self._replace_value(value, old_value, new_value)
                for key, value in content.items()
            }
        elif isinstance(content, list):
            return [self._replace_value(item, old_value, new_value) for item in content]
        else:
            return content

    def get_categories(self) -> list[str]:
        """Get list of all template categories.

        Returns:
            List of category names
        """
        return list(set(t.metadata.category for t in self.templates.values()))

    def get_tags(self) -> list[str]:
        """Get list of all template tags.

        Returns:
            List of tag names
        """
        all_tags: set[str] = set()
        for template in self.templates.values():
            all_tags.update(template.metadata.tags)
        return list(all_tags)
