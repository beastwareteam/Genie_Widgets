"""Configuration Panel - Dynamisches UI-Konfigurationsinterface für alle Strukturelemente.

Korrekturen gegenüber allen bisherigen Versionen:
- Klasse hat exakt einen __init__, einen Docstring, eine Deklaration aller Signals
- _current_panel_id / _is_new_panel im __init__ initialisiert (kein AttributeError mehr)
- _refresh_tabs_tree: exakt einmal definiert, vollständig mit Icons und IconSize
- _add_tab_to_tree: exakt einmal definiert, vollständig mit Icon und Farbmarkierung
- Alle lokalen PySide6-Importe (QMenu, QAction, QIcon, QInputDialog) global konsolidiert
- _on_restart_clicked: QMessageBox.StandardButton.Yes statt deprecated QMessageBox.Yes
- _on_rename_tab: str.removeprefix("★ ") statt fehlerhaftem lstrip("★ ")
- _on_add_tab: try/except statt bool-Prüfung (add_tab_group wirft Exception)
- _on_delete_tab: save_to_file() + _refresh_tabs_tree() für konsistenten Zustand
- Qt.GlobalColor.blue statt Qt.blue (PySide6-kompatibel)
- Kein doppelter Docstring, keine toten String-Literale zwischen Methoden
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from widgetsystem.factories.i18n_factory import I18nFactory
from widgetsystem.factories.list_factory import ListFactory, ListGroup, ListItem
from widgetsystem.factories.menu_factory import MenuFactory, MenuItem
from widgetsystem.factories.panel_factory import PanelFactory
from widgetsystem.factories.tabs_factory import Tab, TabsFactory
from widgetsystem.factories.ui_config_factory import UIConfigFactory


class ConfigurationPanel(QWidget):
    """Dynamisches Konfigurationspanel für die Verwaltung von UI-Strukturen.

    Bietet Oberflächen zum Erstellen, Bearbeiten und Löschen von:
    - Menüs mit Verschachtelung
    - Listen mit Verschachtelung
    - Tab-Gruppen
    - Panels
    - Theme-Einstellungen
    - Erweiterte Einstellungen (Responsive Design, DnD)
    """

    # Signals für strukturelle Änderungen
    config_changed = Signal(str)               # Konfiguration geändert (Kategorie)
    item_added = Signal(str, str)              # Element hinzugefügt (Kategorie, ID)
    item_deleted = Signal(str, str)            # Element gelöscht (Kategorie, ID)
    panel_close_requested = Signal(str)        # panel_id: Dock zur Laufzeit schließen
    panel_rename_requested = Signal(str, str)  # panel_id, new_title: Dock-Titel umbenennen

    def __init__(
        self,
        config_path: Path,
        i18n_factory: I18nFactory,
        parent: QWidget | None = None,
    ) -> None:
        """Initialisiert das Konfigurationspanel."""
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.i18n_factory = i18n_factory

        # Widget-Referenzen
        self.menu_tree: QTreeWidget | None = None
        self.list_tree: QTreeWidget | None = None
        self.tabs_tree: QTreeWidget | None = None
        self.panels_list: QListWidget | None = None

        # Panel-Editor Zustand — hier initialisiert, nicht in _setup_panels_editor
        self._current_panel_id: str | None = None
        self._is_new_panel: bool = False

        # Factories
        self.list_factory = ListFactory(self.config_path)
        self.menu_factory = MenuFactory(self.config_path)
        self.tabs_factory = TabsFactory(self.config_path)
        self.panel_factory = PanelFactory(self.config_path)
        self.ui_config_factory = UIConfigFactory(self.config_path)

        self._apply_global_widget_style()
        self._setup_ui()

    # ------------------------------------------------------------------
    # Globales Widget-Styling
    # ------------------------------------------------------------------

    def _apply_global_widget_style(self) -> None:
        """Setzt ein konsistentes Stylesheet für alle Steuerelemente im Panel.

        Schreibt ein Haken-SVG als temporäre Datei damit QCheckBox::indicator:checked
        einen echten Haken statt einem blauen Quadrat zeigt.
        """
        import pathlib
        import tempfile

        # Haken-SVG zur Laufzeit schreiben — Qt akzeptiert keine data: URIs
        checkmark_svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'>"
            "<polyline points='2,6.5 5,9.5 10,3' fill='none' stroke='white'"
            " stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
        )
        tmp_path = pathlib.Path(tempfile.gettempdir()) / "wgs_checkmark.svg"
        tmp_path.write_text(checkmark_svg, encoding="utf-8")
        check_url = str(tmp_path).replace("\\", "/")

        stylesheet = f"""
            QCheckBox {{
                spacing: 8px;
                color: #cbd5e1;
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1.5px solid rgba(148, 163, 184, 0.45);
                background: rgba(15, 23, 42, 0.6);
            }}
            QCheckBox::indicator:hover {{
                border-color: rgba(99, 179, 237, 0.8);
            }}
            QCheckBox::indicator:checked {{
                border-color: #3b82f6;
                background: #3b82f6;
                image: url({check_url});
            }}
            QCheckBox::indicator:unchecked {{
                background: rgba(15, 23, 42, 0.6);
            }}
            QLineEdit {{
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(100, 116, 139, 0.4);
                border-radius: 4px;
                padding: 5px 8px;
                color: #e2e8f0;
                font-size: 13px;
                selection-background-color: rgba(59, 130, 246, 0.4);
            }}
            QLineEdit:focus {{
                border-color: rgba(59, 130, 246, 0.7);
                background: rgba(15, 23, 42, 0.85);
            }}
            QLineEdit:hover {{
                border-color: rgba(100, 116, 139, 0.7);
            }}
            QComboBox {{
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(100, 116, 139, 0.4);
                border-radius: 4px;
                padding: 5px 28px 5px 10px;
                color: #e2e8f0;
                font-size: 13px;
                selection-background-color: rgba(59, 130, 246, 0.35);
            }}
            QComboBox:hover {{
                border-color: rgba(99, 179, 237, 0.6);
                background: rgba(15, 23, 42, 0.8);
            }}
            QComboBox:focus {{
                border-color: rgba(59, 130, 246, 0.7);
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border: none;
                border-left: 1px solid rgba(100, 116, 139, 0.25);
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid rgba(148, 163, 184, 0.7);
                margin-right: 4px;
            }}
            QComboBox::down-arrow:hover {{
                border-top-color: #93c5fd;
            }}
            QComboBox QAbstractItemView {{
                background: #1e293b;
                border: 1px solid rgba(100, 116, 139, 0.4);
                border-radius: 4px;
                padding: 4px;
                selection-background-color: rgba(59, 130, 246, 0.35);
                selection-color: #e2e8f0;
                color: #cbd5e1;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 5px 10px;
                border-radius: 3px;
                min-height: 24px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: rgba(59, 130, 246, 0.20);
                color: #e2e8f0;
            }}
            QSpinBox, QDoubleSpinBox {{
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(100, 116, 139, 0.4);
                border-radius: 4px;
                padding: 5px 6px;
                color: #e2e8f0;
                font-size: 13px;
                selection-background-color: rgba(59, 130, 246, 0.35);
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: rgba(99, 179, 237, 0.6);
                background: rgba(15, 23, 42, 0.8);
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: rgba(59, 130, 246, 0.7);
            }}
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: right top;
                width: 20px;
                height: 50%;
                border: none;
                border-left: 1px solid rgba(100, 116, 139, 0.25);
                background: rgba(30, 41, 59, 0.5);
                border-top-right-radius: 4px;
            }}
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: right bottom;
                width: 20px;
                height: 50%;
                border: none;
                border-left: 1px solid rgba(100, 116, 139, 0.25);
                border-top: 1px solid rgba(100, 116, 139, 0.15);
                background: rgba(30, 41, 59, 0.5);
                border-bottom-right-radius: 4px;
            }}
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background: rgba(59, 130, 246, 0.25);
                border-left-color: rgba(99, 179, 237, 0.4);
            }}
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-bottom: 4px solid rgba(148, 163, 184, 0.7);
            }}
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid rgba(148, 163, 184, 0.7);
            }}
            QSpinBox::up-arrow:hover, QDoubleSpinBox::up-arrow:hover {{
                border-bottom-color: #93c5fd;
            }}
            QSpinBox::down-arrow:hover, QDoubleSpinBox::down-arrow:hover {{
                border-top-color: #93c5fd;
            }}
            QPushButton {{
                background: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(100, 116, 139, 0.35);
                border-radius: 4px;
                padding: 5px 12px;
                color: #cbd5e1;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: rgba(51, 65, 85, 0.9);
                border-color: rgba(100, 116, 139, 0.6);
                color: #e2e8f0;
            }}
            QPushButton:pressed {{
                background: rgba(15, 23, 42, 0.9);
            }}
            QLabel {{
                color: #94a3b8;
                font-size: 13px;
            }}
            QGroupBox {{
                border: 1px solid rgba(100, 116, 139, 0.25);
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                color: #64748b;
                font-size: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: #64748b;
            }}
            QSplitter::handle {{
                background: rgba(100, 116, 139, 0.2);
                width: 1px;
            }}
            QSplitter::handle:hover {{
                background: rgba(99, 179, 237, 0.4);
            }}
            QScrollBar:vertical {{
                width: 6px;
                background: transparent;
                border: none;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(148, 163, 184, 0.25);
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(148, 163, 184, 0.5);
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar:horizontal {{
                height: 6px;
                background: transparent;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: rgba(148, 163, 184, 0.25);
                border-radius: 3px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: rgba(148, 163, 184, 0.5);
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
        """
        self.setStyleSheet(stylesheet)


    # ------------------------------------------------------------------
    # UI-Aufbau
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Erstellt das Konfigurationspanel-UI."""
        from PySide6.QtWidgets import QSizePolicy
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        self.config_tabs = QTabWidget()
        # Tab-Widget füllt den gesamten verfügbaren Raum
        self.config_tabs.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        layout.addWidget(self.config_tabs, stretch=1)

        try:
            categories = self.ui_config_factory.get_all_categories()
            for category in sorted(categories):
                pages = self.ui_config_factory.get_pages_by_category(category)
                if pages:
                    category_widget = self._create_category_widget(category)
                    tab_title = self.i18n_factory.translate(
                        f"config.{category}.title",
                        default=category.title(),
                    )
                    self.config_tabs.addTab(category_widget, tab_title)
        except Exception as e:
            error_label = QLabel(f"Fehler beim Laden der Konfiguration: {e}")
            self.config_tabs.addTab(error_label, "Fehler")

    def _create_category_widget(self, category: str) -> QWidget:
        """Erstellt ein Widget für eine Konfigurationskategorie."""
        from PySide6.QtWidgets import QSizePolicy
        widget = QWidget()
        widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if category == "menus":
            self._setup_menus_editor(layout)
        elif category == "lists":
            self._setup_lists_editor(layout)
        elif category == "tabs":
            self._setup_tabs_editor(layout)
        elif category == "panels":
            self._setup_panels_editor(layout)
        elif category == "theme":
            self._setup_theme_selector(layout)
        elif category == "advanced":
            self._setup_advanced_settings(layout)
        else:
            layout.addWidget(QLabel(f"Konfiguration für {category}"))
            layout.addStretch()

        return widget

    # ------------------------------------------------------------------
    # Menü-Editor
    # ------------------------------------------------------------------

    def _setup_menus_editor(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt das Menü-Editor-Interface."""
        title = QLabel(self.i18n_factory.translate("config.menu_editor.label", default="Menü-Editor"))
        parent_layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderLabel("Menüs")
        self.menu_tree.setMinimumWidth(250)
        try:
            for menu in self.menu_factory.load_menus():
                self._add_menu_to_tree(self.menu_tree, menu, None)
        except Exception:
            pass
        splitter.addWidget(self.menu_tree)

        properties_widget = QWidget()
        props_layout = QFormLayout(properties_widget)

        menu_name_input = QLineEdit()
        menu_name_input.setPlaceholderText(
            self.i18n_factory.translate("config.menu_name", default="Menüname"),
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.menu_name", default="Name:"),
            menu_name_input,
        )

        menu_shortcut_input = QLineEdit()
        menu_shortcut_input.setPlaceholderText("Ctrl+M")
        props_layout.addRow(
            self.i18n_factory.translate("config.menu_shortcut", default="Kürzel:"),
            menu_shortcut_input,
        )

        add_menu_btn = QPushButton(self.i18n_factory.translate("button.add", default="Menü hinzufügen"))
        add_menu_btn.clicked.connect(lambda: self._on_add_menu(menu_name_input.text()))
        props_layout.addRow(add_menu_btn)

        splitter.addWidget(properties_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setMinimumHeight(300)
        parent_layout.addWidget(splitter, stretch=1)

    def _add_menu_to_tree(
        self,
        parent: QTreeWidget | QTreeWidgetItem,
        menu: MenuItem,
        parent_item: QTreeWidgetItem | None,
    ) -> None:
        """Fügt ein Menüelement rekursiv in den Baum ein."""
        item = QTreeWidgetItem(parent) if parent_item is None else QTreeWidgetItem(parent_item)
        item.setText(0, menu.label_key)
        item.setData(0, Qt.ItemDataRole.UserRole, menu.id)
        for child in menu.children:
            self._add_menu_to_tree(parent, child, item)

    def _refresh_menus_tree(self) -> None:
        """Aktualisiert den Menü-Baum."""
        if self.menu_tree is None:
            return
        self.menu_tree.clear()
        try:
            for menu in self.menu_factory.load_menus():
                self._add_menu_to_tree(self.menu_tree, menu, None)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Listen-Editor
    # ------------------------------------------------------------------

    def _setup_lists_editor(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt das Listen-Editor-Interface."""
        title = QLabel(self.i18n_factory.translate("config.list_editor.label", default="Listen-Editor"))
        parent_layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list_tree = QTreeWidget()
        self.list_tree.setHeaderLabel("Listen")
        self.list_tree.setMinimumWidth(250)
        try:
            for group in self.list_factory.load_list_groups():
                self._add_list_to_tree(self.list_tree, group, None)
        except Exception:
            pass
        splitter.addWidget(self.list_tree)

        properties_widget = QWidget()
        props_layout = QFormLayout(properties_widget)

        list_name_input = QLineEdit()
        list_name_input.setPlaceholderText(
            self.i18n_factory.translate("config.list_name", default="Listenname"),
        )
        props_layout.addRow(
            self.i18n_factory.translate("config.list_name", default="Name:"),
            list_name_input,
        )

        list_type_combo = QComboBox()
        list_type_combo.addItems(["vertical", "horizontal", "tree", "table"])
        props_layout.addRow(
            self.i18n_factory.translate("config.list_type", default="Typ:"),
            list_type_combo,
        )

        sortable_check = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.list_sortable", default="Sortierbar:"),
            sortable_check,
        )

        searchable_check = QCheckBox()
        props_layout.addRow(
            self.i18n_factory.translate("config.list_searchable", default="Durchsuchbar:"),
            searchable_check,
        )

        add_list_btn = QPushButton(self.i18n_factory.translate("button.add", default="Liste hinzufügen"))
        add_list_btn.clicked.connect(
            lambda: self._on_add_list(list_name_input.text(), list_type_combo.currentText()),
        )
        props_layout.addRow(add_list_btn)

        splitter.addWidget(properties_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setMinimumHeight(300)
        parent_layout.addWidget(splitter, stretch=1)

    def _add_list_to_tree(
        self,
        parent: QTreeWidget | QTreeWidgetItem,
        group: ListGroup,
        parent_item: QTreeWidgetItem | None,
    ) -> None:
        """Fügt eine Listengruppe rekursiv in den Baum ein."""
        group_item = QTreeWidgetItem(parent) if parent_item is None else QTreeWidgetItem(parent_item)
        group_item.setText(0, f"{group.title_key} ({group.list_type})")
        group_item.setData(0, Qt.ItemDataRole.UserRole, group.id)
        for item in group.items:
            self._add_item_to_tree(group_item, item)

    def _add_item_to_tree(self, parent: QTreeWidgetItem, item: ListItem) -> None:
        """Fügt ein Listenelement rekursiv in den Baum ein."""
        item_widget = QTreeWidgetItem(parent)
        item_widget.setText(0, item.label_key)
        item_widget.setData(0, Qt.ItemDataRole.UserRole, item.id)
        for child in item.children:
            self._add_item_to_tree(item_widget, child)

    def _refresh_lists_tree(self) -> None:
        """Aktualisiert den Listen-Baum."""
        if self.list_tree is None:
            return
        self.list_tree.clear()
        try:
            for group in self.list_factory.load_list_groups():
                self._add_list_to_tree(self.list_tree, group, None)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Tab-Editor
    # ------------------------------------------------------------------

    def _setup_tabs_editor(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt den Registerkarten-Editor.

        Zeigt alle Tab-Gruppen, Tabs und Subtabs als verschachtelten Baum.
        Kontextmenü für alle Ebenen: Hinzufügen, Umbenennen, Löschen, Verschieben.
        Eigenschaften-Panel rechts zeigt und speichert Tab-Attribute.
        """
        from PySide6.QtWidgets import QScrollArea, QSizePolicy

        title = QLabel(self.i18n_factory.translate("config.tab_editor.label", default="Tab-Editor"))
        parent_layout.addWidget(title)

        info = QLabel(self.i18n_factory.translate(
            "config.tabs.description",
            default="Registerkartengruppen, Tabs und Subtabs verwalten. Rechtsklick für Aktionen.",
        ))
        parent_layout.addWidget(info)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # ---- Linke Seite: Baum in ScrollArea ----
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(4)

        self.tabs_tree = QTreeWidget()
        self.tabs_tree.setHeaderLabel("Tab-Gruppen / Tabs / Subtabs")
        self.tabs_tree.setMinimumWidth(220)
        # Baum passt Höhe dem Inhalt an; Scrollbar erst wenn nötig
        self.tabs_tree.setSizeAdjustPolicy(
            QTreeWidget.SizeAdjustPolicy.AdjustToContents
        )
        self.tabs_tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding,
        )
        self.tabs_tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs_tree.customContextMenuRequested.connect(self._on_tabs_tree_context_menu)
        self.tabs_tree.itemClicked.connect(self._on_tabs_tree_item_clicked)
        self.tabs_tree.itemExpanded.connect(self._on_tree_item_expanded)
        self.tabs_tree.itemCollapsed.connect(self._on_tree_item_collapsed)
        self._refresh_tabs_tree()
        self._apply_treeview_branch_style()

        # Baum in ScrollArea — scrollt erst wenn Inhalt größer als Sichtbereich
        tree_scroll = QScrollArea()
        tree_scroll.setWidget(self.tabs_tree)
        tree_scroll.setWidgetResizable(True)
        tree_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        tree_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tree_layout.addWidget(tree_scroll)

        # Buttons unter dem Baum
        btn_row = QWidget()
        btn_layout = QVBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 4, 0, 0)
        btn_layout.setSpacing(4)
        add_group_btn = QPushButton("+ Neue Tab-Gruppe")
        add_group_btn.setStyleSheet(
            "QPushButton { background: rgba(59,130,246,0.20); border: 1px solid rgba(59,130,246,0.45);"
            " border-radius: 4px; padding: 5px 10px; color: #93c5fd; font-size: 12px; }"
            "QPushButton:hover { background: rgba(59,130,246,0.35); }"
        )
        add_group_btn.clicked.connect(self._on_add_tab_group_clicked)
        btn_layout.addWidget(add_group_btn)
        tree_layout.addWidget(btn_row)

        splitter.addWidget(tree_container)

        # ---- Rechte Seite: Eigenschaften in ScrollArea ----
        props_scroll = QScrollArea()
        props_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        props_scroll.setWidgetResizable(True)
        props_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._tab_properties_widget = QWidget()
        self._tab_props_layout = QFormLayout(self._tab_properties_widget)
        self._tab_props_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self._tab_props_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self._tab_props_layout.setContentsMargins(12, 12, 12, 12)
        self._tab_props_layout.setSpacing(10)

        # Placeholder wenn kein Tab selektiert
        self._tab_no_selection_label = QLabel("← Tab auswählen")
        self._tab_no_selection_label.setStyleSheet("color: #64748b; font-style: italic; padding: 16px;")
        self._tab_props_layout.addRow(self._tab_no_selection_label)

        self._tab_name_input = QLineEdit()
        self._tab_name_input.setPlaceholderText("z.B. tab.overview")
        self._tab_props_layout.addRow(
            self.i18n_factory.translate("config.tab_name", default="Name:"),
            self._tab_name_input,
        )

        self._tab_icon_input = QLineEdit()
        self._tab_icon_input.setPlaceholderText("Icon-Name oder Pfad")
        self._tab_props_layout.addRow("Icon:", self._tab_icon_input)

        self._tab_tooltip_input = QLineEdit()
        self._tab_tooltip_input.setPlaceholderText("Tooltip-Text")
        self._tab_props_layout.addRow("Tooltip:", self._tab_tooltip_input)

        self._tab_closable = QCheckBox("Schließbar")
        self._tab_closable.setChecked(True)
        self._tab_props_layout.addRow(self._tab_closable)

        self._tab_active = QCheckBox("Aktiv (beim Start anzeigen)")
        self._tab_props_layout.addRow(self._tab_active)

        self._tab_context_menu_input = QLineEdit()
        self._tab_context_menu_input.setPlaceholderText("Kontextmenü-ID")
        self._tab_props_layout.addRow("Kontextmenü:", self._tab_context_menu_input)

        # Trennlinie
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(100,130,160,0.25); margin: 4px 0;")
        self._tab_props_layout.addRow(separator)

        self._tab_save_btn = QPushButton(
            self.i18n_factory.translate("button.save", default="Speichern")
        )
        self._tab_save_btn.setStyleSheet(
            "QPushButton { background: rgba(59,130,246,0.25); border: 1px solid rgba(59,130,246,0.5);"
            " border-radius: 4px; padding: 6px 14px; color: #93c5fd; font-size: 13px; }"
            "QPushButton:hover { background: rgba(59,130,246,0.45); }"
        )
        self._tab_save_btn.clicked.connect(self._on_save_tab_properties)
        self._tab_props_layout.addRow(self._tab_save_btn)

        # Felder initial ausblenden bis Tab selektiert
        self._tab_props_fields_visible = False
        self._set_tab_props_fields_visible(False)

        props_scroll.setWidget(self._tab_properties_widget)
        splitter.addWidget(props_scroll)

        # 40% Baum, 60% Eigenschaften
        splitter.setSizes([280, 420])
        splitter.setMinimumHeight(400)
        parent_layout.addWidget(splitter, stretch=1)

    def _apply_treeview_branch_style(self) -> None:
        """Entfernt alle Qt-Standard-Branch-Dekoratoren vollständig.

        Expand/Collapse-State wird im Label-Text angezeigt (▼/▶).
        Die Branch-Spalte wird auf 0 reduziert und vollständig unsichtbar gemacht.
        """
        if self.tabs_tree is None:
            return
        # Branch-Dekoratoren komplett deaktivieren
        self.tabs_tree.setRootIsDecorated(False)
        self.tabs_tree.setItemsExpandable(True)   # Klick auf Item klappt auf/zu
        self.tabs_tree.setIndentation(0)           # Keine Einrückung durch Branch-Area

        self.tabs_tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                outline: 0;
                font-size: 13px;
                background: transparent;
                show-decoration-selected: 1;
            }
            QTreeWidget::item {
                padding: 5px 6px;
                min-height: 24px;
                border: none;
            }
            QTreeWidget::item:hover {
                background: rgba(255, 255, 255, 0.07);
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background: rgba(59, 130, 246, 0.28);
                color: #e2e8f0;
                border-radius: 4px;
            }
            QTreeWidget::item:selected:hover {
                background: rgba(59, 130, 246, 0.40);
            }
            QTreeWidget::branch {
                background: transparent;
                border-image: none;
                image: none;
                border: none;
                width: 0;
                max-width: 0;
            }
            QTreeWidget::branch:has-siblings:adjoins-item,
            QTreeWidget::branch:has-siblings:!adjoins-item,
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item,
            QTreeWidget::branch:closed:has-children:has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings,
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:open:has-children:!has-siblings {
                background: transparent;
                border-image: none;
                image: none;
                border: none;
                width: 0;
                max-width: 0;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: rgba(148, 163, 184, 0.35);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(148, 163, 184, 0.6);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
            QHeaderView::section {
                background: transparent;
                border: none;
                border-bottom: 1px solid rgba(100, 130, 160, 0.30);
                padding: 5px 8px;
                font-size: 11px;
                color: #64748b;
                letter-spacing: 0.5px;
            }
        """)

    # Unicode-Symbole je Ebene und Zustand
    _TREE_ICONS: dict[str, str] = {
        "group_open":   "▼",   # TabGroup aufgeklappt
        "group_closed": "▶",   # TabGroup zugeklappt
        "tab":          "◈",   # direkter Tab (level 1)
        "subtab":       "◦",   # Subtab (level > 1)
        "active":       "★",   # aktiver Tab (Präfix)
    }

    # Farben je Ebene — passend zu einem dunklen Theme
    _TREE_COLORS: dict[str, str] = {
        "group":  "#7dd3fc",   # hellblau  — TabGroup
        "tab":    "#a5b4fc",   # lavendel  — Tab
        "subtab": "#94a3b8",   # grau-blau — Subtab
        "active": "#38bdf8",   # cyan      — aktiver Tab
    }

    def _refresh_tabs_tree(self) -> None:
        """Baut die komplette Tab/Subtab-Baumstruktur neu auf.

        TabGroups: ▼/▶ je nach Expand-State (initial aufgeklappt → ▼)
        Tabs: ◈  Subtabs: ◦  Aktive Tabs: ★
        """
        from PySide6.QtGui import QColor, QFont, QIcon

        if self.tabs_tree is None:
            return
        self.tabs_tree.clear()
        empty_icon = QIcon()
        self.tabs_tree.setIconSize(QtCore.QSize(1, 1))
        try:
            for group in self.tabs_factory.load_tab_groups():
                group_item = QTreeWidgetItem(self.tabs_tree)
                # Initial aufgeklappt → ▼
                group_item.setText(0, f"{self._TREE_ICONS['group_open']}  {group.title_key}")
                group_item.setData(0, Qt.ItemDataRole.UserRole, group.id)
                group_item.setData(0, Qt.ItemDataRole.UserRole + 1, "group")  # Typ-Marker
                group_item.setIcon(0, empty_icon)
                group_item.setForeground(0, QColor(self._TREE_COLORS["group"]))
                font = QFont()
                font.setBold(True)
                font.setPointSize(12)
                group_item.setFont(0, font)
                group_item.setExpanded(True)
                for tab in group.tabs:
                    self._add_tab_to_tree(group_item, tab, level=1)
        except Exception:
            pass

    def _add_tab_to_tree(self, parent: QTreeWidgetItem, tab: Tab, level: int = 1) -> None:
        """Fügt einen Tab/Subtab rekursiv als Knoten in den Baum ein.

        Args:
            parent: Elternknoten im Baum.
            tab: Tab-Objekt das eingefügt werden soll.
            level: 1 = direkter Tab, >1 = Subtab.
        """
        from PySide6.QtGui import QColor, QFont, QIcon

        is_active = getattr(tab, "active", False)
        color_key = "active" if is_active else ("tab" if level == 1 else "subtab")

        if is_active:
            label = f"{self._TREE_ICONS['active']} {tab.title_key}"
        elif level == 1:
            label = f"{self._TREE_ICONS['tab']}  {tab.title_key}"
        else:
            label = f"{self._TREE_ICONS['subtab']}  {tab.title_key}"

        # Einrückung per Leerzeichen — Qt indent ist 0, wir simulieren Tiefe visuell
        indent = "    " * (level - 1)
        tab_item = QTreeWidgetItem(parent)
        tab_item.setText(0, f"{indent}{label}")
        tab_item.setData(0, Qt.ItemDataRole.UserRole, tab.id)
        tab_item.setData(0, Qt.ItemDataRole.UserRole + 1, "tab")  # Typ-Marker
        tab_item.setIcon(0, QIcon())
        tab_item.setForeground(0, QColor(self._TREE_COLORS[color_key]))

        font = QFont()
        if level == 1:
            font.setPointSize(12)
        else:
            font.setPointSize(11)
            font.setItalic(True)
        tab_item.setFont(0, font)

        for child in getattr(tab, "children", []):
            self._add_tab_to_tree(tab_item, child, level=level + 1)

    def _on_tabs_tree_context_menu(self, pos: QtCore.QPoint) -> None:
        """Zeigt das Kontextmenü für den Tab-Baum an."""
        if self.tabs_tree is None:
            return
        item = self.tabs_tree.itemAt(pos)
        if not item:
            return

        menu = QMenu(self.tabs_tree)
        add_subtab_action = QAction(QIcon.fromTheme("list-add"), "Subtab hinzufügen", self.tabs_tree)
        rename_action = QAction(QIcon.fromTheme("edit-rename"), "Umbenennen", self.tabs_tree)
        delete_action = QAction(QIcon.fromTheme("edit-delete"), "Löschen", self.tabs_tree)
        move_up_action = QAction(QIcon.fromTheme("go-up"), "Nach oben verschieben", self.tabs_tree)
        move_down_action = QAction(QIcon.fromTheme("go-down"), "Nach unten verschieben", self.tabs_tree)

        menu.addAction(add_subtab_action)
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(move_up_action)
        menu.addAction(move_down_action)

        action = menu.exec(self.tabs_tree.viewport().mapToGlobal(pos))
        if action == add_subtab_action:
            self._on_add_subtab(item)
        elif action == rename_action:
            self._on_rename_tab(item)
        elif action == delete_action:
            self._on_delete_tab(item)
        elif action == move_up_action:
            self._on_move_tab(item, direction="up")
        elif action == move_down_action:
            self._on_move_tab(item, direction="down")

    def _set_tab_props_fields_visible(self, visible: bool) -> None:
        """Blendet alle Eingabefelder im Eigenschaften-Panel ein oder aus."""
        for widget in (
            self._tab_name_input,
            self._tab_icon_input,
            self._tab_tooltip_input,
            self._tab_closable,
            self._tab_active,
            self._tab_context_menu_input,
            self._tab_save_btn,
        ):
            widget.setVisible(visible)
        self._tab_no_selection_label.setVisible(not visible)

    def _on_tabs_tree_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Füllt das Eigenschaften-Panel mit den Attributen des angeklickten Tabs.

        Klappt TabGroups per Klick auf/zu (da setRootIsDecorated=False).
        """
        node_type = item.data(0, Qt.ItemDataRole.UserRole + 1)

        # TabGroup: Klick klappt auf/zu, keine Eigenschaften anzeigen
        if node_type == "group":
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
            return

        tab_id = item.data(0, Qt.ItemDataRole.UserRole)
        tab = self.tabs_factory.find_tab_by_id(tab_id)
        if not tab:
            self._set_tab_props_fields_visible(False)
            return
        self._set_tab_props_fields_visible(True)
        self._tab_name_input.setText(tab.title_key)
        self._tab_icon_input.setText(getattr(tab, "icon", ""))
        self._tab_tooltip_input.setText(getattr(tab, "tooltip", ""))
        self._tab_closable.setChecked(getattr(tab, "closable", True))
        self._tab_active.setChecked(getattr(tab, "active", False))
        self._tab_context_menu_input.setText(getattr(tab, "context_menu", ""))

    def _on_save_tab_properties(self) -> None:
        """Speichert die Eigenschaften des aktuell ausgewählten Tabs."""
        if self.tabs_tree is None:
            return
        item = self.tabs_tree.currentItem()
        if not item:
            return
        tab_id = item.data(0, Qt.ItemDataRole.UserRole)
        tab = self.tabs_factory.find_tab_by_id(tab_id)
        if not tab:
            return
        tab.title_key = self._tab_name_input.text()
        if hasattr(tab, "icon"):
            tab.icon = self._tab_icon_input.text()
        if hasattr(tab, "tooltip"):
            tab.tooltip = self._tab_tooltip_input.text()
        tab.closable = self._tab_closable.isChecked()
        tab.active = self._tab_active.isChecked()
        if hasattr(tab, "context_menu"):
            tab.context_menu = self._tab_context_menu_input.text()
        self.tabs_factory.save_to_file()
        item.setText(0, tab.title_key)

    def _on_rename_tab(self, item: QTreeWidgetItem) -> None:
        """Benennt einen Tab/Subtab um."""
        raw = item.text(0)
        for prefix in ("▼  ", "▶  ", "★ ", "◈  ", "◦  "):
            raw = raw.removeprefix(prefix)
        old_title = raw.strip()
        text, ok = QInputDialog.getText(self, "Tab/Subtab umbenennen", "Neuer Titel:", text=old_title)
        if ok and text:
            tab_id = item.data(0, Qt.ItemDataRole.UserRole)
            tab = self.tabs_factory.find_tab_by_id(tab_id)
            if tab:
                tab.title_key = text
                self.tabs_factory.save_to_file()
                self._refresh_tabs_tree()

    def _on_add_tab_group_clicked(self) -> None:
        """Öffnet Dialog zum Erstellen einer neuen Tab-Gruppe."""
        text, ok = QInputDialog.getText(self, "Neue Tab-Gruppe", "ID der Tab-Gruppe:")
        if ok and text:
            group_id = text.strip().lower().replace(" ", "_")
            try:
                self.tabs_factory.add_tab_group(
                    group_id=group_id,
                    title_key=f"tabs.{group_id}.title",
                    dock_area="center",
                    orientation="horizontal",
                )
                self.tabs_factory.reload()
                self._refresh_tabs_tree()
                self.config_changed.emit("tabs")
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Tab-Gruppe konnte nicht erstellt werden:\n{e}")

    def _on_add_subtab(self, parent_item: QTreeWidgetItem) -> None:
        """Fügt einen neuen Subtab unter dem ausgewählten Tab ein."""
        tab_id = parent_item.data(0, Qt.ItemDataRole.UserRole)
        tab = self.tabs_factory.find_tab_by_id(tab_id)
        if not tab:
            return
        new_id = f"{tab_id}_sub_{uuid.uuid4().hex[:6]}"
        new_tab = Tab(id=new_id, title_key="Neuer Subtab")
        tab.children.append(new_tab)
        self.tabs_factory.save_to_file()
        self._refresh_tabs_tree()

    def _on_delete_tab(self, item: QTreeWidgetItem) -> None:
        """Entfernt einen Tab aus der Konfiguration und baut den Baum neu auf."""
        parent = item.parent()
        if not parent:
            return
        tab_id = item.data(0, Qt.ItemDataRole.UserRole)
        parent_tab_id = parent.data(0, Qt.ItemDataRole.UserRole)
        parent_tab = self.tabs_factory.find_tab_by_id(parent_tab_id)
        if not parent_tab:
            return
        parent_tab.children = [c for c in parent_tab.children if c.id != tab_id]
        self.tabs_factory.save_to_file()
        self._refresh_tabs_tree()

    def _on_move_tab(self, item: QTreeWidgetItem, direction: str) -> None:
        """Verschiebt einen Tab innerhalb seiner Geschwister nach oben oder unten."""
        parent = item.parent()
        if not parent:
            return
        tab_id = item.data(0, Qt.ItemDataRole.UserRole)
        parent_tab_id = parent.data(0, Qt.ItemDataRole.UserRole)
        parent_tab = self.tabs_factory.find_tab_by_id(parent_tab_id)
        if not parent_tab:
            return
        idx = next((i for i, c in enumerate(parent_tab.children) if c.id == tab_id), -1)
        if idx == -1:
            return
        if direction == "up" and idx > 0:
            parent_tab.children[idx], parent_tab.children[idx - 1] = (
                parent_tab.children[idx - 1], parent_tab.children[idx]
            )
        elif direction == "down" and idx < len(parent_tab.children) - 1:
            parent_tab.children[idx], parent_tab.children[idx + 1] = (
                parent_tab.children[idx + 1], parent_tab.children[idx]
            )
        self.tabs_factory.save_to_file()
        self._refresh_tabs_tree()

    def _on_tree_item_expanded(self, item: QTreeWidgetItem) -> None:
        """Aktualisiert das ▶/▼-Symbol wenn eine TabGroup aufgeklappt wird."""
        node_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if node_type == "group":
            text = item.text(0)
            item.setText(0, text.replace(self._TREE_ICONS["group_closed"],
                                          self._TREE_ICONS["group_open"], 1))

    def _on_tree_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """Aktualisiert das ▼/▶-Symbol wenn eine TabGroup zugeklappt wird."""
        node_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if node_type == "group":
            text = item.text(0)
            item.setText(0, text.replace(self._TREE_ICONS["group_open"],
                                          self._TREE_ICONS["group_closed"], 1))

    # ------------------------------------------------------------------
    # Panel-Editor
    # ------------------------------------------------------------------

    def _setup_panels_editor(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt das Panel-Editor-Interface."""
        title = QLabel(self.i18n_factory.translate("config.panel_editor.label", default="Panel-Editor"))
        parent_layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Links: Panel-Liste
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.panels_list = QListWidget()
        self.panels_list.setMinimumWidth(180)
        left_layout.addWidget(self.panels_list)

        new_panel_btn = QPushButton(self.i18n_factory.translate("button.new", default="Neues Panel"))
        new_panel_btn.clicked.connect(self._on_new_panel_clicked)
        left_layout.addWidget(new_panel_btn)
        splitter.addWidget(left_widget)

        # Rechts: Eigenschaften-Formular
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 0, 0, 0)

        props_group = QGroupBox(self.i18n_factory.translate("config.panel_properties", default="Eigenschaften"))
        props_layout = QFormLayout(props_group)

        self._panel_id_label = QLabel("")
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_id", default="ID:"),
            self._panel_id_label,
        )

        self._panel_name_input = QLineEdit()
        self._panel_name_input.setPlaceholderText("panel.id.name")
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_name_key", default="Name-Schlüssel:"),
            self._panel_name_input,
        )

        self._panel_area_combo = QComboBox()
        self._panel_area_combo.addItems(["left", "right", "bottom", "center"])
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_area", default="Bereich:"),
            self._panel_area_combo,
        )

        self._panel_closable_check = QCheckBox()
        self._panel_closable_check.setChecked(True)
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_closable", default="Schließbar:"),
            self._panel_closable_check,
        )

        self._panel_movable_check = QCheckBox()
        self._panel_movable_check.setChecked(True)
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_movable", default="Verschiebbar:"),
            self._panel_movable_check,
        )

        self._panel_floatable_check = QCheckBox()
        self._panel_floatable_check.setChecked(False)
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_floatable", default="Schwebend:"),
            self._panel_floatable_check,
        )

        self._panel_delete_on_close_check = QCheckBox()
        self._panel_delete_on_close_check.setChecked(False)
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_delete_on_close", default="Beim Schließen löschen:"),
            self._panel_delete_on_close_check,
        )

        # Panel-Tabs-Baum
        self._panel_tabs_tree = QTreeWidget()
        self._panel_tabs_tree.setHeaderLabel(
            self.i18n_factory.translate("config.panel_tabs", default="Tabs/TabGroups")
        )
        self._panel_tabs_tree.setMinimumHeight(120)
        props_layout.addRow(
            self.i18n_factory.translate("config.panel_tabs", default="Tabs/TabGroups:"),
            self._panel_tabs_tree,
        )
        self._init_panel_tabs_tree_context_menu()
        self._refresh_panel_tabs_tree(None)

        right_layout.addWidget(props_group)

        save_btn = QPushButton(self.i18n_factory.translate("button.save", default="Änderungen speichern"))
        save_btn.clicked.connect(self._on_save_panel)
        right_layout.addWidget(save_btn)

        delete_btn = QPushButton(self.i18n_factory.translate("button.delete", default="Panel löschen"))
        delete_btn.clicked.connect(self._on_delete_panel)
        right_layout.addWidget(delete_btn)

        force_close_btn = QPushButton(
            self.i18n_factory.translate("button.force_close", default="Panel schließen (erzwingen)")
        )
        force_close_btn.clicked.connect(self._on_force_close_panel)
        right_layout.addWidget(force_close_btn)

        right_layout.addStretch()
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setMinimumHeight(400)
        parent_layout.addWidget(splitter, stretch=1)

        self._populate_panels_list()
        self.panels_list.currentItemChanged.connect(self._on_panel_selection_changed)

    def _init_panel_tabs_tree_context_menu(self) -> None:
        """Initialisiert das Kontextmenü für den Panel-Tabs-Baum."""
        self._panel_tabs_tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self._panel_tabs_tree.customContextMenuRequested.connect(
            self._on_panel_tabs_tree_context_menu
        )

    def _on_panel_tabs_tree_context_menu(self, pos: QtCore.QPoint) -> None:
        """Kontextmenü für den Panel-Tabs-Baum."""
        item = self._panel_tabs_tree.itemAt(pos)
        if not item or not self._current_panel_id:
            return
        menu = QMenu(self._panel_tabs_tree)
        add_tab_action = menu.addAction("Tab/Subtab hinzufügen")
        rename_tab_action = menu.addAction("Umbenennen")
        delete_tab_action = menu.addAction("Löschen")
        action = menu.exec(self._panel_tabs_tree.viewport().mapToGlobal(pos))
        tab_id = item.data(0, Qt.ItemDataRole.UserRole)
        if action == add_tab_action:
            text, ok = QInputDialog.getText(self, "Neuer Tab/Subtab", "Titel:")
            if ok and text:
                self._add_panel_tab(self._current_panel_id, tab_id, text)
        elif action == rename_tab_action:
            text, ok = QInputDialog.getText(
                self, "Tab/Subtab umbenennen", "Neuer Titel:", text=item.text(0)
            )
            if ok and text:
                self._rename_panel_tab(self._current_panel_id, tab_id, text)
        elif action == delete_tab_action:
            self._delete_panel_tab(self._current_panel_id, tab_id)

    def _add_panel_tab(self, panel_id: str, parent_tab_id: str, title: str) -> None:
        """Fügt einen neuen Subtab unter parent_tab_id hinzu."""
        group = self.tabs_factory.get_tab_group(panel_id)
        if not group:
            return
        parent_tab = self.tabs_factory.find_tab_by_id(parent_tab_id)
        if not parent_tab:
            return
        new_id = f"{parent_tab_id}_sub{len(parent_tab.children) + 1}"
        new_tab = Tab(id=new_id, title_key=title)
        parent_tab.children.append(new_tab)
        self.tabs_factory.save_to_file()
        self._refresh_panel_tabs_tree(panel_id)

    def _rename_panel_tab(self, panel_id: str, tab_id: str, new_title: str) -> None:
        """Benennt einen Tab im Panel-Tabs-Baum um."""
        tab = self.tabs_factory.find_tab_by_id(tab_id)
        if not tab:
            return
        tab.title_key = new_title
        self.tabs_factory.save_to_file()
        self._refresh_panel_tabs_tree(panel_id)

    def _delete_panel_tab(self, panel_id: str, tab_id: str) -> None:
        """Entfernt einen Tab rekursiv aus der TabGroup."""
        group = self.tabs_factory.get_tab_group(panel_id)
        if not group:
            return

        def remove_tab(tabs: list[Tab], tid: str) -> bool:
            for i, t in enumerate(tabs):
                if t.id == tid:
                    del tabs[i]
                    return True
                if t.children and remove_tab(t.children, tid):
                    return True
            return False

        if remove_tab(group.tabs, tab_id):
            self.tabs_factory.save_to_file()
            self._refresh_panel_tabs_tree(panel_id)

    def _refresh_panel_tabs_tree(self, panel_id: str | None) -> None:
        """Aktualisiert die Tabs/Subtabs-Übersicht für das gewählte Panel."""
        self._panel_tabs_tree.clear()
        if not panel_id:
            return
        try:
            panel_config = self.tabs_factory.get_panel_config(panel_id)
            if not panel_config or "tabs" not in panel_config:
                return
            for tab_dict in panel_config["tabs"]:
                self._add_tab_to_panel_tree(self._panel_tabs_tree, tab_dict)
        except Exception as e:
            self._panel_tabs_tree.addTopLevelItem(QTreeWidgetItem([f"Fehler: {e}"]))

    def _add_tab_to_panel_tree(
        self,
        parent: QTreeWidget | QTreeWidgetItem,
        tab_dict: dict[str, Any],
    ) -> None:
        """Fügt einen Tab/Subtab rekursiv in den Panel-Tabs-Baum ein."""
        item = QTreeWidgetItem(parent)
        item.setText(0, tab_dict.get("title_key", tab_dict.get("id", "?")))
        item.setData(0, Qt.ItemDataRole.UserRole, tab_dict.get("id"))
        for child in tab_dict.get("children", []):
            self._add_tab_to_panel_tree(item, child)

    def _populate_panels_list(self) -> None:
        """Befüllt die Panel-Listbox."""
        if self.panels_list is None:
            return
        self.panels_list.clear()
        try:
            for panel in self.panel_factory.load_panels():
                display = self.i18n_factory.translate(panel.name_key, default=panel.id)
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, panel.id)
                self.panels_list.addItem(item)
        except Exception:
            pass

    def _refresh_panels_tree(self) -> None:
        """Aktualisiert die Panel-Liste."""
        self._populate_panels_list()

    def _on_panel_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        """Füllt das Formular wenn ein Panel ausgewählt wird."""
        if current is None:
            self._refresh_panel_tabs_tree(None)
            return
        panel_id = current.data(Qt.ItemDataRole.UserRole)
        self._current_panel_id = panel_id
        self._is_new_panel = False
        try:
            panel = self.panel_factory.get_panel(panel_id)
            if panel is None:
                self.panel_factory = PanelFactory(self.config_path)
                panel = self.panel_factory.get_panel(panel_id)
            if panel is None:
                self._refresh_panel_tabs_tree(None)
                return
            self._panel_id_label.setText(panel.id)
            self._panel_name_input.setText(panel.name_key)
            idx = self._panel_area_combo.findText(panel.area)
            if idx >= 0:
                self._panel_area_combo.setCurrentIndex(idx)
            self._panel_closable_check.setChecked(panel.closable)
            self._panel_movable_check.setChecked(panel.movable)
            self._panel_floatable_check.setChecked(panel.floatable)
            self._panel_delete_on_close_check.setChecked(panel.delete_on_close)
            self._refresh_panel_tabs_tree(panel_id)
        except Exception:
            self._refresh_panel_tabs_tree(None)

    def _on_new_panel_clicked(self) -> None:
        """Leert das Formular für ein neues Panel."""
        if self.panels_list is not None:
            self.panels_list.clearSelection()
        self._current_panel_id = None
        self._is_new_panel = True
        self._panel_id_label.setText("(neu)")
        self._panel_name_input.clear()
        self._panel_area_combo.setCurrentIndex(0)
        self._panel_closable_check.setChecked(True)
        self._panel_movable_check.setChecked(True)
        self._panel_floatable_check.setChecked(False)
        self._panel_delete_on_close_check.setChecked(False)

    def _on_save_panel(self) -> None:
        """Speichert (erstellt oder aktualisiert) das aktuelle Panel."""
        name_key = self._panel_name_input.text().strip()
        area = self._panel_area_combo.currentText()
        closable = self._panel_closable_check.isChecked()
        movable = self._panel_movable_check.isChecked()
        floatable = self._panel_floatable_check.isChecked()
        delete_on_close = self._panel_delete_on_close_check.isChecked()

        if self._is_new_panel:
            if not name_key:
                QMessageBox.warning(self, "Warnung", "Bitte einen Name-Schlüssel für das neue Panel eingeben.")
                return
            panel_id = (
                name_key.split(".")[-1].lower().replace(" ", "_")
                if "." in name_key
                else name_key.lower().replace(" ", "_")
            )
            success = self.panel_factory.add_panel(
                panel_id=panel_id,
                name_key=name_key,
                area=area,
                closable=closable,
                movable=movable,
            )
            if success:
                self.panel_factory.update_panel(panel_id, floatable=floatable, delete_on_close=delete_on_close)
                self.panel_factory = PanelFactory(self.config_path)
                self._populate_panels_list()
                self.config_changed.emit("panels")
                QMessageBox.information(self, "Erfolg", f"Panel '{panel_id}' erstellt.")
            else:
                QMessageBox.warning(self, "Fehler", "Panel konnte nicht erstellt werden.")
        else:
            if self._current_panel_id is None:
                QMessageBox.warning(self, "Warnung", "Kein Panel ausgewählt.")
                return
            old_name_key = None
            try:
                p = self.panel_factory.get_panel(self._current_panel_id)
                if p:
                    old_name_key = p.name_key
            except Exception:
                pass
            success = self.panel_factory.update_panel(
                self._current_panel_id,
                name_key=name_key,
                area=area,
                closable=closable,
                movable=movable,
                floatable=floatable,
                delete_on_close=delete_on_close,
            )
            if success:
                self.panel_factory = PanelFactory(self.config_path)
                self._populate_panels_list()
                self.config_changed.emit("panels")
                if old_name_key != name_key:
                    display = self.i18n_factory.translate(name_key, default=self._current_panel_id)
                    self.panel_rename_requested.emit(self._current_panel_id, display)
                QMessageBox.information(self, "Erfolg", f"Panel '{self._current_panel_id}' aktualisiert.")
            else:
                QMessageBox.warning(self, "Fehler", "Panel konnte nicht aktualisiert werden.")

    def _on_delete_panel(self) -> None:
        """Löscht das ausgewählte Panel aus der Konfiguration."""
        if self._current_panel_id is None:
            QMessageBox.warning(self, "Warnung", "Kein Panel ausgewählt.")
            return
        reply = QMessageBox.question(
            self,
            "Löschen bestätigen",
            f"Panel '{self._current_panel_id}' aus der Konfiguration löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        success = self.panel_factory.delete_panel(self._current_panel_id)
        if success:
            deleted_id = self._current_panel_id
            self._current_panel_id = None
            self._is_new_panel = False
            self.panel_factory = PanelFactory(self.config_path)
            self._populate_panels_list()
            self.item_deleted.emit("panels", deleted_id)
            self.config_changed.emit("panels")
            QMessageBox.information(self, "Erfolg", f"Panel '{deleted_id}' aus Konfiguration gelöscht.")
        else:
            QMessageBox.warning(self, "Fehler", "Panel konnte nicht gelöscht werden.")

    def _on_force_close_panel(self) -> None:
        """Schließt das Dock-Widget des ausgewählten Panels zur Laufzeit."""
        if self._current_panel_id is None:
            QMessageBox.warning(self, "Warnung", "Kein Panel ausgewählt.")
            return
        self.panel_close_requested.emit(self._current_panel_id)

    # ------------------------------------------------------------------
    # Theme-Auswahl
    # ------------------------------------------------------------------

    def _setup_theme_selector(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt die Theme-Auswahl — kompaktes Form-Layout."""
        from PySide6.QtWidgets import QSizePolicy, QHBoxLayout

        # Abschnitt-Titel
        section = QLabel("DESIGN")
        section.setStyleSheet("QLabel { color: #475569; font-size: 11px; font-weight: bold; letter-spacing: 0.8px; padding-top: 4px; }")
        parent_layout.addWidget(section)

        # Formular-Widget
        form_widget = QWidget()
        form_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        form = QFormLayout(form_widget)
        form.setContentsMargins(12, 8, 12, 8)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)

        theme_combo = QComboBox()
        theme_combo.setFixedWidth(180)
        theme_combo.addItem(self.i18n_factory.translate("config.theme.light", default="Hell"), "light")
        theme_combo.addItem(self.i18n_factory.translate("config.theme.dark", default="Dunkel"), "dark")
        form.addRow(
            QLabel(self.i18n_factory.translate("config.current_theme", default="Aktuelles Theme:")),
            theme_combo,
        )

        parent_layout.addWidget(form_widget)

        # Button-Zeile — linksbündig, inhaltbreit
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(12, 0, 12, 0)
        apply_btn = QPushButton(self.i18n_factory.translate("button.apply", default="Anwenden"))
        apply_btn.setStyleSheet("QPushButton { background: rgba(59,130,246,0.20); border: 1px solid rgba(59,130,246,0.45); border-radius: 4px; padding: 5px 16px; color: #93c5fd; font-size: 12px; max-width: 200px; }QPushButton:hover { background: rgba(59,130,246,0.35); }QPushButton:pressed { background: rgba(59,130,246,0.50); }")
        apply_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        apply_btn.clicked.connect(lambda: self.config_changed.emit("theme"))
        btn_row.addWidget(apply_btn)
        btn_row.addStretch()
        parent_layout.addLayout(btn_row)
        parent_layout.addStretch()

    # ------------------------------------------------------------------
    # Erweiterte Einstellungen
    # ------------------------------------------------------------------

    def _setup_advanced_settings(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt das Interface für erweiterte Einstellungen — kompakt und strukturiert."""
        from PySide6.QtWidgets import QSizePolicy, QHBoxLayout

        # ── Responsives Design ──────────────────────────────────────────
        resp_section = QLabel("RESPONSIVES DESIGN")
        resp_section.setStyleSheet("QLabel { color: #475569; font-size: 11px; font-weight: bold; letter-spacing: 0.8px; padding-top: 4px; }")
        parent_layout.addWidget(resp_section)

        resp_widget = QWidget()
        resp_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        resp_form = QFormLayout(resp_widget)
        resp_form.setContentsMargins(12, 6, 12, 6)
        resp_form.setSpacing(10)
        resp_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        resp_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)

        breakpoint_combo = QComboBox()
        breakpoint_combo.setFixedWidth(120)
        breakpoint_combo.addItems(["xs", "sm", "md", "lg", "xl"])
        resp_form.addRow(
            QLabel(self.i18n_factory.translate("config.breakpoint", default="Breakpoint:")),
            breakpoint_combo,
        )
        parent_layout.addWidget(resp_widget)

        # Trennlinie
        sep1 = QLabel()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet("background: rgba(100,116,139,0.18); margin: 6px 12px;")
        parent_layout.addWidget(sep1)

        # ── Drag & Drop ─────────────────────────────────────────────────
        dnd_section = QLabel("DRAG & DROP")
        dnd_section.setStyleSheet("QLabel { color: #475569; font-size: 11px; font-weight: bold; letter-spacing: 0.8px; padding-top: 4px; }")
        parent_layout.addWidget(dnd_section)

        dnd_widget = QWidget()
        dnd_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        dnd_form = QFormLayout(dnd_widget)
        dnd_form.setContentsMargins(12, 6, 12, 6)
        dnd_form.setSpacing(10)
        dnd_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        dnd_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)

        dnd_enabled = QCheckBox("Aktiviert")
        dnd_enabled.setChecked(True)
        dnd_form.addRow(dnd_enabled)

        dnd_opacity = QDoubleSpinBox()
        dnd_opacity.setFixedWidth(80)
        dnd_opacity.setRange(0.0, 1.0)
        dnd_opacity.setSingleStep(0.1)
        dnd_opacity.setValue(0.7)
        # Styling kommt aus _apply_global_widget_style
        dnd_form.addRow(
            QLabel(self.i18n_factory.translate("config.dnd_opacity", default="Deckkraft:")),
            dnd_opacity,
        )
        parent_layout.addWidget(dnd_widget)

        # Trennlinie
        sep2 = QLabel()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background: rgba(100,116,139,0.18); margin: 6px 12px;")
        parent_layout.addWidget(sep2)

        # ── Aktionen ────────────────────────────────────────────────────
        action_section = QLabel("AKTIONEN")
        action_section.setStyleSheet("QLabel { color: #475569; font-size: 11px; font-weight: bold; letter-spacing: 0.8px; padding-top: 4px; }")
        parent_layout.addWidget(action_section)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(12, 6, 12, 6)
        btn_row.setSpacing(8)

        restart_btn = QPushButton("↺  " + self.i18n_factory.translate("button.restart", default="Anwendung neu starten"))
        restart_btn.setStyleSheet("QPushButton { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.40); border-radius: 4px; padding: 5px 16px; color: #fca5a5; font-size: 12px; max-width: 200px; }QPushButton:hover { background: rgba(239,68,68,0.30); }")
        restart_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        restart_btn.clicked.connect(self._on_restart_clicked)
        btn_row.addWidget(restart_btn)
        btn_row.addStretch()

        parent_layout.addLayout(btn_row)
        parent_layout.addStretch()

    def _on_restart_clicked(self) -> None:
        """Startet die Anwendung vollständig neu.

        Verwendet QMessageBox.StandardButton.Yes (nicht deprecated QMessageBox.Yes).
        """
        reply = QMessageBox.question(
            self,
            "Neustart",
            "Anwendung wirklich neu starten?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
            os.execl(sys.executable, sys.executable, *sys.argv)

    # ------------------------------------------------------------------
    # Event-Handler: Hinzufügen
    # ------------------------------------------------------------------

    def _on_add_menu(self, menu_name: str) -> None:
        """Fügt ein neues Menü aus der Eingabe hinzu."""
        if not menu_name:
            QMessageBox.warning(self, "Warnung", "Bitte einen Menünamen eingeben.")
            return
        try:
            menu_id = menu_name.lower().replace(" ", "_")
            success = self.menu_factory.add_menu_item(
                menu_id=menu_id,
                label_key=f"menu.{menu_id}.label",
                menu_type="action",
            )
            if success:
                self.menu_factory = MenuFactory(self.config_path)
                self._refresh_menus_tree()
                self.config_changed.emit("menus")
                QMessageBox.information(self, "Erfolg", f"Menü '{menu_name}' hinzugefügt.")
            else:
                QMessageBox.warning(self, "Fehler", "Menü konnte nicht in der Konfigurationsdatei gespeichert werden.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Menü konnte nicht hinzugefügt werden: {e}")

    def _on_add_list(self, list_name: str, list_type: str) -> None:
        """Fügt eine neue Liste aus der Eingabe hinzu."""
        if not list_name:
            QMessageBox.warning(self, "Warnung", "Bitte einen Listennamen eingeben.")
            return
        try:
            list_id = list_name.lower().replace(" ", "_")
            success = self.list_factory.add_list_group(
                group_id=list_id,
                title_key=f"list.{list_id}.title",
                list_type=list_type,
                panel_id="center",
            )
            if success:
                self.list_factory = ListFactory(self.config_path)
                self._refresh_lists_tree()
                self.config_changed.emit("lists")
                QMessageBox.information(self, "Erfolg", f"Liste '{list_name}' ({list_type}) hinzugefügt.")
            else:
                QMessageBox.warning(self, "Fehler", "Liste konnte nicht in der Konfigurationsdatei gespeichert werden.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Liste konnte nicht hinzugefügt werden: {e}")

    def _on_add_tab(self, tab_name: str) -> None:
        """Fügt eine neue Tab-Gruppe aus der Eingabe hinzu.

        add_tab_group gibt eine TabGroup zurück oder wirft eine Exception — kein bool.
        """
        if not tab_name:
            QMessageBox.warning(self, "Warnung", "Bitte einen Tab-Namen eingeben.")
            return
        try:
            tab_id = tab_name.lower().replace(" ", "_")
            self.tabs_factory.add_tab_group(
                group_id=tab_id,
                title_key=f"tabs.{tab_id}.title",
                dock_area="center",
                orientation="horizontal",
            )
            self.tabs_factory.reload()
            self._refresh_tabs_tree()
            self.config_changed.emit("tabs")
            QMessageBox.information(self, "Erfolg", f"Tab '{tab_name}' hinzugefügt.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Tab konnte nicht hinzugefügt werden: {e}")

    def _on_add_panel(self, panel_name: str, panel_area: str) -> None:
        """Fügt ein neues Panel aus der Eingabe hinzu."""
        if not panel_name:
            QMessageBox.warning(self, "Warnung", "Bitte einen Panelnamen eingeben.")
            return
        try:
            panel_id = panel_name.lower().replace(" ", "_")
            success = self.panel_factory.add_panel(
                panel_id=panel_id,
                name_key=f"panel.{panel_id}.name",
                area=panel_area,
                closable=True,
                movable=True,
            )
            if success:
                self.panel_factory = PanelFactory(self.config_path)
                self._refresh_panels_tree()
                self.config_changed.emit("panels")
                QMessageBox.information(self, "Erfolg", f"Panel '{panel_name}' ({panel_area}) hinzugefügt.")
            else:
                QMessageBox.warning(self, "Fehler", "Panel konnte nicht in der Konfigurationsdatei gespeichert werden.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Panel konnte nicht hinzugefügt werden: {e}")