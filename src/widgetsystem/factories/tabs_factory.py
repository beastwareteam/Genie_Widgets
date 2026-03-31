"""Tabs Factory - liest config/tabs.json und stellt typisierte Tab-Definitionen mit Verschachtelung bereit.

Features:
- MAX_NESTING_DEPTH (50) begrenzt sichere Rekursionstiefe
- Thread-Safety via threading.Lock auf dem Cache
- Lazy Loading mit _ensure_cache(), reload() und force_reload-Parameter
- Spezifische Fehlerklassen für alle Fehlerfälle (keine bool-Rückgaben)
- Logging für Typwarnungen statt stiller Fallbacks
- Duplikat-Erkennung beim Laden (DuplicateIdError)
- PanelConfigurable als abstrakte Basisklasse direkt integriert
- Keine toten TypedDict-Klassen oder redundanten cast()-Aufrufe
"""

from __future__ import annotations

import json
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Maximale Verschachtelungstiefe für Tab-Children.
# Wert 50 liegt weit unter dem Python-Rekursionslimit (default 1000)
# und deckt jede realistische UI-Konfiguration ab.
MAX_NESTING_DEPTH: int = 50


# ---------------------------------------------------------------------------
# Fehlerklassen
# ---------------------------------------------------------------------------

class TabsFactoryError(Exception):
    """Basisklasse für alle TabsFactory-Fehler."""


class ConfigNotFoundError(TabsFactoryError):
    """Konfigurationsdatei nicht gefunden."""


class ConfigParseError(TabsFactoryError):
    """Fehler beim Parsen der Konfiguration."""


class DuplicateIdError(TabsFactoryError):
    """Doppelte ID in der Konfiguration gefunden."""


class PersistenceError(TabsFactoryError):
    """Fehler beim Schreiben der Konfigurationsdatei."""


class NestingDepthExceededError(TabsFactoryError):
    """Maximale Verschachtelungstiefe überschritten."""


# ---------------------------------------------------------------------------
# Abstrakte Basisklasse
# ---------------------------------------------------------------------------

class PanelConfigurable(ABC):
    """Schnittstelle für Klassen, die Panel-Konfigurationen liefern können."""

    @abstractmethod
    def get_panel_config(self, panel_id: str) -> dict[str, Any]:
        """Gibt die vollständige Panel-Konfiguration für eine gegebene ID zurück.

        Args:
            panel_id: Eindeutige ID des Panels (entspricht einer TabGroup-ID).

        Returns:
            Dictionary mit allen Konfigurationsfeldern inkl. verschachtelter Tabs.
            Gibt ein leeres Dict zurück, wenn die ID nicht existiert.
        """


# ---------------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------------

@dataclass
class Tab:
    """Repräsentiert einen einzelnen Tab mit optionalen verschachtelten Kindelementen."""

    id: str
    title_key: str
    component: str = ""
    closable: bool = True
    active: bool = False
    icon: str = ""
    tooltip: str = ""
    context_menu: str = ""
    children: list[Tab] = field(default_factory=list)


@dataclass
class TabGroup:
    """Repräsentiert eine Gruppe von Tabs in einem Dock-Bereich."""

    id: str
    title_key: str
    dock_area: str
    orientation: str
    tabs: list[Tab] = field(default_factory=list)

    _VALID_AREAS = frozenset({"left", "right", "bottom", "center"})
    _VALID_ORIENTATIONS = frozenset({"horizontal", "vertical"})

    def __post_init__(self) -> None:
        """Validiert dock_area und orientation nach der Initialisierung."""
        if self.dock_area not in self._VALID_AREAS:
            raise ConfigParseError(
                f"Ungültiger dock_area-Wert '{self.dock_area}'. "
                f"Erlaubt: {sorted(self._VALID_AREAS)}"
            )
        if self.orientation not in self._VALID_ORIENTATIONS:
            raise ConfigParseError(
                f"Ungültige orientation '{self.orientation}'. "
                f"Erlaubt: {sorted(self._VALID_ORIENTATIONS)}"
            )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TabsFactory(PanelConfigurable):
    """Factory zum Laden und Verwalten von Tab-Konfigurationen.

    Unterstützt beliebig tiefe Verschachtelung (bis MAX_NESTING_DEPTH),
    ist thread-sicher und implementiert PanelConfigurable.
    """

    def __init__(self, config_path: str | Path = "config") -> None:
        """Initialisiert die TabsFactory.

        Args:
            config_path: Verzeichnis, das die tabs.json enthält.
        """
        self.config_path = Path(config_path)
        self.tabs_file = self.config_path / "tabs.json"
        self._tab_groups_cache: dict[str, TabGroup] | None = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # PanelConfigurable-Implementierung
    # ------------------------------------------------------------------

    def get_panel_config(self, panel_id: str) -> dict[str, Any]:
        """Gibt die vollständige Panel-Konfiguration für eine TabGroup zurück.

        Args:
            panel_id: ID der gewünschten TabGroup.

        Returns:
            Dictionary mit allen Feldern der TabGroup inkl. rekursiver Tabs.
            Leeres Dict, wenn die Gruppe nicht existiert.
        """
        group = self.get_tab_group(panel_id)
        if not group:
            return {}
        return self._tab_group_to_dict(group)

    # ------------------------------------------------------------------
    # Öffentliche Lade- und Abfragemethoden
    # ------------------------------------------------------------------

    def load_tab_groups(self) -> list[TabGroup]:
        """Lädt und parst alle TabGroups aus der Konfigurationsdatei.

        Returns:
            Liste aller geladenen TabGroup-Objekte.

        Raises:
            ConfigNotFoundError: Wenn tabs.json nicht existiert.
            ConfigParseError: Bei ungültigem JSON oder fehlerhaften Feldern.
            DuplicateIdError: Wenn zwei TabGroups dieselbe ID haben.
        """
        if not self.tabs_file.exists():
            raise ConfigNotFoundError(
                f"Konfigurationsdatei nicht gefunden: {self.tabs_file}"
            )

        with open(self.tabs_file, encoding="utf-8") as f:
            try:
                raw: Any = json.load(f)
            except json.JSONDecodeError as exc:
                raise ConfigParseError(
                    f"Ungültiges JSON in {self.tabs_file}: {exc}"
                ) from exc

        if not isinstance(raw, dict):
            raise ConfigParseError("Tabs-Konfiguration muss ein JSON-Objekt sein.")

        raw_groups: Any = raw.get("tab_groups", [])
        if not isinstance(raw_groups, list):
            raise ConfigParseError("'tab_groups' muss ein Array sein.")

        new_cache: dict[str, TabGroup] = {}
        for item in raw_groups:
            if not isinstance(item, dict):
                logger.warning("TabGroup-Eintrag übersprungen (kein Objekt): %r", item)
                continue
            tab_group = self._parse_tab_group(item)
            if tab_group.id in new_cache:
                raise DuplicateIdError(
                    f"Doppelte TabGroup-ID gefunden: '{tab_group.id}'. "
                    "Jede ID muss eindeutig sein."
                )
            new_cache[tab_group.id] = tab_group

        with self._lock:
            self._tab_groups_cache = new_cache

        return list(new_cache.values())

    def reload(self) -> list[TabGroup]:
        """Erzwingt ein erneutes Laden der Konfigurationsdatei.

        Nützlich wenn tabs.json extern verändert wurde.

        Returns:
            Aktualisierte Liste aller TabGroup-Objekte.
        """
        with self._lock:
            self._tab_groups_cache = None
        return self.load_tab_groups()

    def get_tab_group(
        self, group_id: str, *, force_reload: bool = False
    ) -> TabGroup | None:
        """Gibt eine TabGroup anhand ihrer ID zurück.

        Args:
            group_id: Die gesuchte TabGroup-ID.
            force_reload: Bei True wird der Cache vor der Suche neu geladen.

        Returns:
            Die TabGroup oder None, falls nicht gefunden.
        """
        if force_reload:
            self.reload()
        self._ensure_cache()
        with self._lock:
            return self._tab_groups_cache.get(group_id)  # type: ignore[union-attr]

    def get_tab_groups_by_area(
        self, dock_area: str, *, force_reload: bool = False
    ) -> list[TabGroup]:
        """Gibt alle TabGroups eines bestimmten Dock-Bereichs zurück.

        Args:
            dock_area: Einer von 'left', 'right', 'bottom', 'center'.
            force_reload: Bei True wird der Cache neu geladen.

        Returns:
            Liste der passenden TabGroups (leer wenn keine gefunden).
        """
        if force_reload:
            self.reload()
        self._ensure_cache()
        with self._lock:
            return [
                g for g in self._tab_groups_cache.values()  # type: ignore[union-attr]
                if g.dock_area == dock_area
            ]

    def find_tab_by_id(
        self, tab_id: str, *, force_reload: bool = False
    ) -> Tab | None:
        """Sucht einen Tab anhand seiner ID (rekursiv durch alle Children).

        Args:
            tab_id: Die gesuchte Tab-ID.
            force_reload: Bei True wird der Cache neu geladen.

        Returns:
            Den gefundenen Tab oder None.
        """
        if force_reload:
            self.reload()
        self._ensure_cache()
        with self._lock:
            groups = list(self._tab_groups_cache.values())  # type: ignore[union-attr]

        for tab_group in groups:
            result = self._find_tab_recursive(tab_group.tabs, tab_id)
            if result is not None:
                return result
        return None

    def list_tab_group_ids(self) -> list[str]:
        """Gibt alle TabGroup-IDs zurück."""
        self._ensure_cache()
        with self._lock:
            return list(self._tab_groups_cache.keys())  # type: ignore[union-attr]

    def get_flat_tab_list(self, group_id: str) -> list[Tab]:
        """Gibt eine flache Liste aller Tabs einer Gruppe zurück (inklusive Children).

        Args:
            group_id: ID der TabGroup.

        Returns:
            Flache Liste aller Tabs, leer wenn Gruppe nicht existiert.
        """
        tab_group = self.get_tab_group(group_id)
        if not tab_group:
            return []

        result: list[Tab] = []

        def flatten(tabs: list[Tab]) -> None:
            for tab in tabs:
                result.append(tab)
                if tab.children:
                    flatten(tab.children)

        flatten(tab_group.tabs)
        return result

    # ------------------------------------------------------------------
    # Schreibmethoden
    # ------------------------------------------------------------------

    def add_tab_group(
        self,
        group_id: str,
        title_key: str,
        dock_area: str = "center",
        orientation: str = "horizontal",
    ) -> TabGroup:
        """Erstellt eine neue TabGroup und speichert sie in der Datei.

        Args:
            group_id: Eindeutige ID der neuen Gruppe.
            title_key: Übersetzungsschlüssel für den Titel.
            dock_area: Dock-Bereich ('left', 'right', 'bottom', 'center').
            orientation: Ausrichtung ('horizontal', 'vertical').

        Returns:
            Die neu erstellte TabGroup.

        Raises:
            DuplicateIdError: Wenn group_id bereits existiert.
            ConfigParseError: Bei ungültigen dock_area/orientation-Werten.
            PersistenceError: Wenn die Datei nicht gespeichert werden kann.
        """
        self._ensure_cache()

        with self._lock:
            if group_id in self._tab_groups_cache:  # type: ignore[operator]
                raise DuplicateIdError(
                    f"TabGroup mit ID '{group_id}' existiert bereits."
                )

        # ConfigParseError wird ggf. von TabGroup.__post_init__ geworfen
        new_group = TabGroup(
            id=group_id,
            title_key=title_key,
            dock_area=dock_area,
            orientation=orientation,
            tabs=[],
        )

        with self._lock:
            self._tab_groups_cache[group_id] = new_group  # type: ignore[index]

        self.save_to_file()
        return new_group

    def save_to_file(self) -> None:
        """Serialisiert den Cache und schreibt ihn in die Datei.

        Raises:
            PersistenceError: Wenn der Cache leer ist oder das Schreiben fehlschlägt.
        """
        with self._lock:
            if self._tab_groups_cache is None:
                raise PersistenceError(
                    "Nichts zu speichern: Cache wurde noch nicht geladen."
                )
            data: dict[str, Any] = {
                "tab_groups": [
                    self._tab_group_to_dict(group)
                    for group in self._tab_groups_cache.values()
                ]
            }

        try:
            self.tabs_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tabs_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            raise PersistenceError(
                f"Fehler beim Schreiben von {self.tabs_file}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Interne Hilfsmethoden
    # ------------------------------------------------------------------

    def _ensure_cache(self) -> None:
        """Stellt sicher, dass der Cache befüllt ist (Lazy Loading, thread-sicher)."""
        with self._lock:
            cache_is_empty = self._tab_groups_cache is None
        if cache_is_empty:
            self.load_tab_groups()

    @staticmethod
    def _parse_tab(tab_dict: dict[str, Any], *, _depth: int = 0) -> Tab:
        """Parst und validiert eine einzelne Tab-Definition.

        Args:
            tab_dict: Rohes Dictionary aus der JSON-Datei.
            _depth: Aktuelle Rekursionstiefe (intern, nicht von außen setzen).

        Raises:
            ConfigParseError: Bei fehlender oder ungültiger 'id'.
            NestingDepthExceededError: Wenn MAX_NESTING_DEPTH überschritten wird.
        """
        if _depth > MAX_NESTING_DEPTH:
            raise NestingDepthExceededError(
                f"Maximale Tab-Verschachtelungstiefe von {MAX_NESTING_DEPTH} überschritten. "
                "Bitte die tabs.json-Konfiguration überprüfen."
            )

        tab_id: Any = tab_dict.get("id")
        if not isinstance(tab_id, str) or not tab_id:
            raise ConfigParseError(
                f"Tab 'id' muss ein nicht-leerer String sein, erhalten: {tab_id!r}"
            )

        title_key: Any = tab_dict.get("title_key", "")
        if not isinstance(title_key, str):
            logger.warning(
                "Tab '%s': 'title_key' ist kein String (%r), verwende ''.", tab_id, title_key
            )
            title_key = ""

        component: Any = tab_dict.get("component", "")
        if not isinstance(component, str):
            logger.warning(
                "Tab '%s': 'component' ist kein String (%r), verwende ''.", tab_id, component
            )
            component = ""

        closable: Any = tab_dict.get("closable", True)
        active: Any = tab_dict.get("active", False)

        icon: Any = tab_dict.get("icon", "")
        if not isinstance(icon, str):
            icon = ""

        tooltip: Any = tab_dict.get("tooltip", "")
        if not isinstance(tooltip, str):
            tooltip = ""

        context_menu: Any = tab_dict.get("context_menu", "")
        if not isinstance(context_menu, str):
            context_menu = ""

        children: list[Tab] = []
        children_raw: Any = tab_dict.get("children", [])
        if isinstance(children_raw, list):
            for child in children_raw:
                if isinstance(child, dict):
                    children.append(TabsFactory._parse_tab(child, _depth=_depth + 1))
        elif children_raw:
            logger.warning(
                "Tab '%s': 'children' ist kein Array (%r), wird ignoriert.", tab_id, children_raw
            )

        return Tab(
            id=tab_id,
            title_key=title_key,
            component=component,
            closable=bool(closable),
            active=bool(active),
            icon=icon,
            tooltip=tooltip,
            context_menu=context_menu,
            children=children,
        )

    @staticmethod
    def _parse_tab_group(group_dict: dict[str, Any]) -> TabGroup:
        """Parst und validiert eine einzelne TabGroup-Definition.

        Raises:
            ConfigParseError: Bei fehlender oder ungültiger 'id' bzw. Pflichtfeldern.
        """
        group_id: Any = group_dict.get("id")
        if not isinstance(group_id, str) or not group_id:
            raise ConfigParseError(
                f"TabGroup 'id' muss ein nicht-leerer String sein, erhalten: {group_id!r}"
            )

        title_key: Any = group_dict.get("title_key", "")
        if not isinstance(title_key, str):
            logger.warning(
                "TabGroup '%s': 'title_key' ist kein String (%r), verwende ''.",
                group_id, title_key,
            )
            title_key = ""

        dock_area: Any = group_dict.get("dock_area", "center")
        if not isinstance(dock_area, str):
            raise ConfigParseError(
                f"TabGroup '{group_id}': 'dock_area' muss ein String sein, "
                f"erhalten: {dock_area!r}"
            )

        orientation: Any = group_dict.get("orientation", "horizontal")
        if not isinstance(orientation, str):
            raise ConfigParseError(
                f"TabGroup '{group_id}': 'orientation' muss ein String sein, "
                f"erhalten: {orientation!r}"
            )

        tabs: list[Tab] = []
        tabs_raw: Any = group_dict.get("tabs", [])
        if isinstance(tabs_raw, list):
            for tab_dict in tabs_raw:
                if isinstance(tab_dict, dict):
                    tabs.append(TabsFactory._parse_tab(tab_dict))
        elif tabs_raw:
            logger.warning(
                "TabGroup '%s': 'tabs' ist kein Array (%r), wird ignoriert.",
                group_id, tabs_raw,
            )

        # ConfigParseError wird ggf. von __post_init__ geworfen
        return TabGroup(
            id=group_id,
            title_key=title_key,
            dock_area=dock_area,
            orientation=orientation,
            tabs=tabs,
        )

    @staticmethod
    def _find_tab_recursive(tabs: list[Tab], tab_id: str) -> Tab | None:
        """Sucht rekursiv nach einem Tab in einer Liste (inklusive Children)."""
        for tab in tabs:
            if tab.id == tab_id:
                return tab
            if tab.children:
                result = TabsFactory._find_tab_recursive(tab.children, tab_id)
                if result is not None:
                    return result
        return None

    @staticmethod
    def _tab_group_to_dict(group: TabGroup) -> dict[str, Any]:
        """Konvertiert eine TabGroup in ein serialisierbares Dictionary."""
        return {
            "id": group.id,
            "title_key": group.title_key,
            "dock_area": group.dock_area,
            "orientation": group.orientation,
            "tabs": [TabsFactory._tab_to_dict(tab) for tab in group.tabs],
        }

    @staticmethod
    def _tab_to_dict(tab: Tab) -> dict[str, Any]:
        """Konvertiert einen Tab in ein serialisierbares Dictionary."""
        result: dict[str, Any] = {
            "id": tab.id,
            "title_key": tab.title_key,
            "component": tab.component,
            "closable": tab.closable,
            "active": tab.active,
            "icon": tab.icon,
            "tooltip": tab.tooltip,
            "context_menu": tab.context_menu,
        }
        if tab.children:
            result["children"] = [TabsFactory._tab_to_dict(child) for child in tab.children]
        return result