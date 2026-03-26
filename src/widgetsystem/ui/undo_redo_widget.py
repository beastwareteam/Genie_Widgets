"""Undo/Redo Widget - UI control for undo/redo operations.

Provides:
- Undo/Redo buttons
- History length configuration
- Status display
- Clear history action
"""

from typing import TYPE_CHECKING, Any, Callable, cast

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QGroupBox,
)

from widgetsystem.core.undo_redo import UndoRedoManager
from widgetsystem.ui.enhanced_tab_widget import EnhancedTabWidget

if TYPE_CHECKING:
    from widgetsystem.factories.i18n_factory import I18nFactory


class UndoRedoWidget(QWidget):
    """Widget for controlling undo/redo operations.

    Provides buttons, status display, and configuration options
    for the undo/redo system.
    """

    # Signals
    settings_changed = Signal(dict)  # Emitted when settings change

    def __init__(
        self,
        manager: UndoRedoManager | None = None,
        parent: QWidget | None = None,
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize UndoRedoWidget.

        Args:
            manager: UndoRedoManager instance (uses shared if None)
            parent: Parent widget
            i18n_factory: Optional i18n factory for UI text translation
        """
        super().__init__(parent)

        self._manager = manager or EnhancedTabWidget.get_undo_manager()
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        self._setup_ui()
        self._connect_signals()
        self._update_status()

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory and refresh labels."""
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()
        self._setup_translated_texts()
        self._update_status()

    def _translate(self, key: str, default: str | None = None, **kwargs: object) -> str:
        """Translate a key with optional interpolation and cache."""
        if not self._i18n_factory or not key:
            text = default or key
            return text.format(**kwargs) if kwargs else text

        cache_key = f"{key}|{sorted(kwargs.items())}" if kwargs else key
        if cache_key in self._translated_cache:
            return self._translated_cache[cache_key]

        translated = self._i18n_factory.translate(key, default=default or key, **kwargs)
        self._translated_cache[cache_key] = translated
        return translated

    def _setup_ui(self) -> None:
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Buttons row
        btn_layout = QHBoxLayout()

        self._undo_btn = QPushButton(self._translate("button.undo", "Undo"))
        self._undo_btn.setToolTip(
            self._translate("undo_redo.tooltip.undo_ctrlz", "Ctrl+Z"),
        )
        self._undo_btn.setEnabled(False)

        self._redo_btn = QPushButton(self._translate("button.redo", "Redo"))
        self._redo_btn.setToolTip(
            self._translate("undo_redo.tooltip.redo_ctrly", "Ctrl+Y"),
        )
        self._redo_btn.setEnabled(False)

        self._clear_btn = QPushButton(self._translate("action.clear", "Clear"))
        self._clear_btn.setToolTip(
            self._translate("undo_redo.tooltip.clear_history", "Clear all history"),
        )

        btn_layout.addWidget(self._undo_btn)
        btn_layout.addWidget(self._redo_btn)
        btn_layout.addWidget(self._clear_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Status group
        self._status_group = QGroupBox(self._translate("config.undo_redo.status", "Status"))
        status_layout = QVBoxLayout(self._status_group)

        self._undo_count_label = QLabel(
            self._translate("undo_redo.label.undo_count", "Undo: {count}", count=0),
        )
        self._redo_count_label = QLabel(
            self._translate("undo_redo.label.redo_count", "Redo: {count}", count=0),
        )
        self._next_undo_label = QLabel(
            self._translate("undo_redo.label.next_undo", "Next Undo: {value}", value="-"),
        )
        self._next_redo_label = QLabel(
            self._translate("undo_redo.label.next_redo", "Next Redo: {value}", value="-"),
        )

        status_layout.addWidget(self._undo_count_label)
        status_layout.addWidget(self._redo_count_label)
        status_layout.addWidget(self._next_undo_label)
        status_layout.addWidget(self._next_redo_label)

        layout.addWidget(self._status_group)

        # Settings group
        self._settings_group = QGroupBox(
            self._translate("settings.general", "Settings"),
        )
        settings_layout = QHBoxLayout(self._settings_group)

        self._max_history_label = QLabel(
            self._translate("undo_redo.label.max_history", "Max History:"),
        )
        settings_layout.addWidget(self._max_history_label)

        self._max_history_spin = QSpinBox()
        self._max_history_spin.setRange(10, 1000)
        self._max_history_spin.setSingleStep(10)
        self._max_history_spin.setValue(self._manager.max_history)

        settings_layout.addWidget(self._max_history_spin)
        settings_layout.addStretch()

        layout.addWidget(self._settings_group)
        layout.addStretch()

    def _setup_translated_texts(self) -> None:
        """Refresh static translated UI texts."""
        self._undo_btn.setText(self._translate("button.undo", "Undo"))
        self._redo_btn.setText(self._translate("button.redo", "Redo"))
        self._clear_btn.setText(self._translate("action.clear", "Clear"))
        self._undo_btn.setToolTip(self._translate("undo_redo.tooltip.undo_ctrlz", "Ctrl+Z"))
        self._redo_btn.setToolTip(self._translate("undo_redo.tooltip.redo_ctrly", "Ctrl+Y"))
        self._clear_btn.setToolTip(
            self._translate("undo_redo.tooltip.clear_history", "Clear all history"),
        )
        self._status_group.setTitle(self._translate("config.undo_redo.status", "Status"))
        self._settings_group.setTitle(self._translate("settings.general", "Settings"))
        self._max_history_label.setText(self._translate("undo_redo.label.max_history", "Max History:"))

    @staticmethod
    def _connect_signal(signal: object, callback: Callable[..., object]) -> None:
        """Connect Qt signal with typed fallback for static analyzers."""
        cast(Any, signal).connect(callback)  # pyright: ignore[reportAttributeAccessIssue]  # pylint: disable=no-member

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Button actions
        self._connect_signal(self._undo_btn.clicked, self._on_undo)
        self._connect_signal(self._redo_btn.clicked, self._on_redo)
        self._connect_signal(self._clear_btn.clicked, self._on_clear)
        self._connect_signal(self._max_history_spin.valueChanged, self._on_max_history_changed)

        # Manager signals
        self._manager.undoAvailable.connect(self._undo_btn.setEnabled)
        self._manager.redoAvailable.connect(self._redo_btn.setEnabled)
        self._manager.stackChanged.connect(self._update_status)

    def _on_undo(self) -> None:
        """Handle undo button click."""
        self._manager.undo()

    def _on_redo(self) -> None:
        """Handle redo button click."""
        self._manager.redo()

    def _on_clear(self) -> None:
        """Handle clear button click."""
        self._manager.clear()
        self._update_status()

    def _on_max_history_changed(self, value: int) -> None:
        """Handle max history change."""
        self._manager.set_max_history(value)
        self.settings_changed.emit({"max_history": value})

    def _update_status(self) -> None:
        """Update status labels."""
        status = self._manager.get_status()

        self._undo_count_label.setText(
            self._translate(
                "undo_redo.label.undo_count",
                "Undo: {count}",
                count=status["undo_count"],
            ),
        )
        self._redo_count_label.setText(
            self._translate(
                "undo_redo.label.redo_count",
                "Redo: {count}",
                count=status["redo_count"],
            ),
        )

        next_undo = status.get("next_undo") or "-"
        next_redo = status.get("next_redo") or "-"

        # Truncate long descriptions
        if len(next_undo) > 30:
            next_undo = next_undo[:27] + "..."
        if len(next_redo) > 30:
            next_redo = next_redo[:27] + "..."

        self._next_undo_label.setText(
            self._translate("undo_redo.label.next_undo", "Next Undo: {value}", value=next_undo),
        )
        self._next_redo_label.setText(
            self._translate("undo_redo.label.next_redo", "Next Redo: {value}", value=next_redo),
        )

        # Update button states
        self._undo_btn.setEnabled(self._manager.can_undo())
        self._redo_btn.setEnabled(self._manager.can_redo())

    def get_settings(self) -> dict:
        """Get current settings.

        Returns:
            Dict with max_history
        """
        return {
            "max_history": self._max_history_spin.value(),
        }

    def set_settings(self, settings: dict) -> None:
        """Apply settings.

        Args:
            settings: Dict with max_history
        """
        if "max_history" in settings:
            self._max_history_spin.setValue(settings["max_history"])


class UndoRedoToolbar(QWidget):
    """Compact toolbar version of undo/redo controls.

    Provides just Undo/Redo buttons for embedding in toolbars.
    """

    def __init__(
        self,
        manager: UndoRedoManager | None = None,
        parent: QWidget | None = None,
        i18n_factory: "I18nFactory | None" = None,
    ) -> None:
        """Initialize UndoRedoToolbar."""
        super().__init__(parent)

        self._manager = manager or EnhancedTabWidget.get_undo_manager()
        self._i18n_factory = i18n_factory
        self._translated_cache: dict[str, str] = {}
        self._setup_ui()
        self._connect_signals()

    def set_i18n_factory(self, i18n_factory: "I18nFactory | None") -> None:
        """Set or update i18n factory and refresh tooltips."""
        self._i18n_factory = i18n_factory
        self._translated_cache.clear()
        self._setup_translated_texts()

    def _translate(self, key: str, default: str | None = None) -> str:
        """Translate a key using i18n factory if available."""
        if not self._i18n_factory or not key:
            return default or key
        if key in self._translated_cache:
            return self._translated_cache[key]
        translated = self._i18n_factory.translate(key, default=default or key)
        self._translated_cache[key] = translated
        return translated

    def _setup_ui(self) -> None:
        """Setup compact UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._undo_btn = QPushButton("↶")
        self._undo_btn.setToolTip(self._translate("undo_redo.tooltip.undo_short", "Undo (Ctrl+Z)"))
        self._undo_btn.setFixedWidth(30)
        self._undo_btn.setEnabled(False)

        self._redo_btn = QPushButton("↷")
        self._redo_btn.setToolTip(self._translate("undo_redo.tooltip.redo_short", "Redo (Ctrl+Y)"))
        self._redo_btn.setFixedWidth(30)
        self._redo_btn.setEnabled(False)

        layout.addWidget(self._undo_btn)
        layout.addWidget(self._redo_btn)

    def _setup_translated_texts(self) -> None:
        """Refresh translated tooltips."""
        self._undo_btn.setToolTip(self._translate("undo_redo.tooltip.undo_short", "Undo (Ctrl+Z)"))
        self._redo_btn.setToolTip(self._translate("undo_redo.tooltip.redo_short", "Redo (Ctrl+Y)"))

    @staticmethod
    def _connect_signal(signal: object, callback: Callable[..., object]) -> None:
        """Connect Qt signal with typed fallback for static analyzers."""
        cast(Any, signal).connect(callback)  # pyright: ignore[reportAttributeAccessIssue]  # pylint: disable=no-member

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._connect_signal(self._undo_btn.clicked, self._manager.undo)
        self._connect_signal(self._redo_btn.clicked, self._manager.redo)
        self._manager.undoAvailable.connect(self._undo_btn.setEnabled)
        self._manager.redoAvailable.connect(self._redo_btn.setEnabled)
