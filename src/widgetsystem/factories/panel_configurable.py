"""
PanelConfigurable: Interface für Factories mit Panel-Konfigurationsunterstützung.

Dieses Interface kann von Factories wie TabsFactory implementiert werden, um Panel-Konfigurationen bereitzustellen.
"""

from typing import Protocol, Any

class PanelConfigurable(Protocol):
    """Interface für Factories, die Panel-Konfigurationen liefern können."""
    def get_panel_config(self, panel_id: str) -> dict[str, Any]:
        """Gibt die Panel-Konfiguration für eine gegebene Panel-ID zurück."""
        ...
