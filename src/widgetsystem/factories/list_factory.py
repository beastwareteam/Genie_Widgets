"""List Factory - reads config/lists.json and provides typed list item definitions with nesting."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, TypedDict, cast


class ListItemDefinition(TypedDict, total=False):
    """Type-safe list item configuration."""

    id: str
    label_key: str
    content_type: str  # "text", "button", "widget", "custom", "nested"
    content: str
    editable: bool
    deletable: bool
    icon: str
    data: dict[str, Any]
    children: list["ListItemDefinition"]


class ListGroupDefinition(TypedDict, total=False):
    """Type-safe list group configuration."""

    id: str
    title_key: str
    list_type: str  # "vertical", "horizontal", "tree", "table"
    dock_panel_id: str
    sortable: bool
    filterable: bool
    searchable: bool
    multi_select: bool
    items: list[ListItemDefinition]


@dataclass
class ListItem:
    """Represents a single list item with optional nested children."""

    id: str
    label_key: str
    content_type: str = "text"
    content: str = ""
    editable: bool = True
    deletable: bool = True
    icon: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    children: list["ListItem"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate list item configuration."""
        valid_types = {"text", "button", "widget", "custom", "nested"}
        if self.content_type not in valid_types:
            raise ValueError(
                f"Invalid content_type '{self.content_type}'. Must be one of {valid_types}",
            )


@dataclass
class ListGroup:
    """Represents a group of list items in a panel."""

    id: str
    title_key: str
    list_type: str
    dock_panel_id: str
    sortable: bool = False
    filterable: bool = False
    searchable: bool = False
    multi_select: bool = False
    items: list[ListItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate list group configuration."""
        valid_types = {"vertical", "horizontal", "tree", "table"}
        if self.list_type not in valid_types:
            raise ValueError(f"Invalid list_type '{self.list_type}'. Must be one of {valid_types}")


class ListFactory:
    """Factory for loading and managing list configurations with nesting support."""

    def __init__(self, config_path: str | Path = "config") -> None:
        """Initialize ListFactory."""
        self.config_path = Path(config_path)
        self.lists_file = self.config_path / "lists.json"
        self._list_groups_cache: dict[str, ListGroup] | None = None

    def load_list_groups(self) -> list[ListGroup]:
        """Load and parse all list groups from config."""
        if not self.lists_file.exists():
            raise FileNotFoundError(f"Lists configuration file not found: {self.lists_file}")

        with open(self.lists_file, encoding="utf-8") as f:
            raw_data_temp: Any = json.load(f)

        if not isinstance(raw_data_temp, dict):
            raise ValueError("Lists configuration must be a JSON object")
        raw_data = cast("dict[str, Any]", raw_data_temp)

        list_groups_raw: Any = raw_data.get("list_groups", [])
        if not isinstance(list_groups_raw, list):
            raise ValueError("'list_groups' must be an array")
        list_groups_list: list[Any] = list_groups_raw

        list_groups: list[ListGroup] = []
        for item in list_groups_list:
            if not isinstance(item, dict):
                continue
            item_dict = cast("dict[str, Any]", item)
            list_group = self._parse_list_group(item_dict)
            list_groups.append(list_group)

        self._list_groups_cache = {lg.id: lg for lg in list_groups}
        return list_groups

    def _parse_list_group(self, data: dict[str, Any]) -> ListGroup:
        """Parse a list group from raw configuration data."""
        list_id: Any = data.get("id")
        title_key: Any = data.get("title_key")
        list_type: Any = data.get("list_type")
        panel_id: Any = data.get("dock_panel_id")
        sortable: Any = data.get("sortable", False)
        filterable: Any = data.get("filterable", False)
        searchable: Any = data.get("searchable", False)
        multi_select: Any = data.get("multi_select", False)

        if not isinstance(list_id, str):
            raise ValueError("List group 'id' must be a string")
        if not isinstance(title_key, str):
            raise ValueError("List group 'title_key' must be a string")
        if not isinstance(list_type, str):
            raise ValueError("List group 'list_type' must be a string")
        if not isinstance(panel_id, str):
            raise ValueError("List group 'dock_panel_id' must be a string")

        items_raw: Any = data.get("items", [])
        if not isinstance(items_raw, list):
            raise ValueError("List group 'items' must be an array")
        items_list: list[Any] = items_raw

        items: list[ListItem] = []
        for item_data in items_list:
            if isinstance(item_data, dict):
                item = self._parse_list_item(cast("dict[str, Any]", item_data))
                items.append(item)

        return ListGroup(
            id=list_id,
            title_key=title_key,
            list_type=list_type,
            dock_panel_id=panel_id,
            sortable=bool(sortable),
            filterable=bool(filterable),
            searchable=bool(searchable),
            multi_select=bool(multi_select),
            items=items,
        )

    def _parse_list_item(self, data: dict[str, Any]) -> ListItem:
        """Recursively parse a list item from raw configuration data."""
        item_id: Any = data.get("id")
        label_key: Any = data.get("label_key")
        content_type: Any = data.get("content_type", "text")
        content: Any = data.get("content", "")
        editable: Any = data.get("editable", True)
        deletable: Any = data.get("deletable", True)
        icon: Any = data.get("icon", "")
        item_data: Any = data.get("data", {})

        if not isinstance(item_id, str):
            raise ValueError("List item 'id' must be a string")
        if not isinstance(label_key, str):
            raise ValueError("List item 'label_key' must be a string")

        children_raw: Any = data.get("children", [])
        if not isinstance(children_raw, list):
            children_raw = []
        children_list: list[Any] = children_raw

        children: list[ListItem] = []
        for child_data in children_list:
            if isinstance(child_data, dict):
                child = self._parse_list_item(cast("dict[str, Any]", child_data))
                children.append(child)

        return ListItem(
            id=item_id,
            label_key=label_key,
            content_type=str(content_type),
            content=str(content),
            editable=bool(editable),
            deletable=bool(deletable),
            icon=str(icon),
            data=dict(item_data) if isinstance(item_data, dict) else {},
            children=children,
        )

    def get_list_group_by_id(self, group_id: str) -> ListGroup | None:
        """Get a list group by ID."""
        if self._list_groups_cache is None:
            try:
                self.load_list_groups()
            except (FileNotFoundError, ValueError, json.JSONDecodeError):
                return None

        return self._list_groups_cache.get(group_id) if self._list_groups_cache else None

    def add_list_group(self, group_id: str, title_key: str, list_type: str, panel_id: str) -> bool:
        """Create and add a new list group, save to file."""
        if self._list_groups_cache is None:
            try:
                self.load_list_groups()
            except (FileNotFoundError, ValueError, json.JSONDecodeError):
                self._list_groups_cache = {}

        new_group = ListGroup(
            id=group_id,
            title_key=title_key,
            list_type=list_type,
            dock_panel_id=panel_id,
            items=[],
        )

        if self._list_groups_cache:
            self._list_groups_cache[group_id] = new_group
        return self.save_to_file()

    def add_item_to_group(
        self,
        group_id: str,
        item: ListItem,
        parent_id: str | None = None,
    ) -> bool:
        """Add a new item to a list group (runtime modification)."""
        group = self.get_list_group_by_id(group_id)
        if not group:
            return False

        if parent_id is None:
            group.items.append(item)
            return True

        # Find parent and add to its children
        def find_and_add_recursive(items: list[ListItem]) -> bool:
            for existing_item in items:
                if existing_item.id == parent_id:
                    existing_item.children.append(item)
                    return True
                if find_and_add_recursive(existing_item.children):
                    return True
            return False

        return find_and_add_recursive(group.items)

    def remove_item_from_group(self, group_id: str, item_id: str) -> bool:
        """Remove an item from a list group (runtime modification)."""
        group = self.get_list_group_by_id(group_id)
        if not group:
            return False

        def find_and_remove_recursive(items: list[ListItem]) -> bool:
            for i, item in enumerate(items):
                if item.id == item_id:
                    items.pop(i)
                    return True
                if find_and_remove_recursive(item.children):
                    return True
            return False

        return find_and_remove_recursive(group.items)

    def save_to_file(self) -> bool:
        """Save current configuration to lists.json file."""
        try:
            if self._list_groups_cache is None:
                return False

            list_groups_data: list[dict[str, Any]] = []
            for group in self._list_groups_cache.values():
                list_groups_data.append(self._serialize_list_group(group))

            output_data: dict[str, Any] = {"list_groups": list_groups_data}
            json_content = json.dumps(output_data, indent=2, ensure_ascii=False)
            self.lists_file.write_text(json_content, encoding="utf-8")
            return True
        except (OSError, ValueError):
            return False

    def _serialize_list_group(self, group: ListGroup) -> dict[str, Any]:
        """Serialize a list group to JSON-compatible dict."""
        return {
            "id": group.id,
            "title_key": group.title_key,
            "list_type": group.list_type,
            "dock_panel_id": group.dock_panel_id,
            "sortable": group.sortable,
            "filterable": group.filterable,
            "searchable": group.searchable,
            "multi_select": group.multi_select,
            "items": [self._serialize_list_item(item) for item in group.items],
        }

    def _serialize_list_item(self, item: ListItem) -> dict[str, Any]:
        """Serialize a list item to JSON-compatible dict."""
        return {
            "id": item.id,
            "label_key": item.label_key,
            "content_type": item.content_type,
            "content": item.content,
            "editable": item.editable,
            "deletable": item.deletable,
            "icon": item.icon,
            "data": item.data,
            "children": [self._serialize_list_item(child) for child in item.children],
        }
