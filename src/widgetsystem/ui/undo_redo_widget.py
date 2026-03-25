"""Undo/Redo Widget - UI control for undo/redo operations.

Provides:
- Undo/Redo buttons
- History length configuration
- Status display
- Clear history action
"""

from PySide6.QtCore import Qt, Signal
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
    ) -> None:
        """Initialize UndoRedoWidget.

        Args:
            manager: UndoRedoManager instance (uses shared if None)
            parent: Parent widget
        """
        super().__init__(parent)

        self._manager = manager or EnhancedTabWidget.get_undo_manager()
        self._setup_ui()
        self._connect_signals()
        self._update_status()

    def _setup_ui(self) -> None:
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Buttons row
        btn_layout = QHBoxLayout()

        self._undo_btn = QPushButton("Undo")
        self._undo_btn.setToolTip("Ctrl+Z")
        self._undo_btn.setEnabled(False)

        self._redo_btn = QPushButton("Redo")
        self._redo_btn.setToolTip("Ctrl+Y")
        self._redo_btn.setEnabled(False)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setToolTip("Clear all history")

        btn_layout.addWidget(self._undo_btn)
        btn_layout.addWidget(self._redo_btn)
        btn_layout.addWidget(self._clear_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self._undo_count_label = QLabel("Undo: 0")
        self._redo_count_label = QLabel("Redo: 0")
        self._next_undo_label = QLabel("Next Undo: -")
        self._next_redo_label = QLabel("Next Redo: -")

        status_layout.addWidget(self._undo_count_label)
        status_layout.addWidget(self._redo_count_label)
        status_layout.addWidget(self._next_undo_label)
        status_layout.addWidget(self._next_redo_label)

        layout.addWidget(status_group)

        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QHBoxLayout(settings_group)

        settings_layout.addWidget(QLabel("Max History:"))

        self._max_history_spin = QSpinBox()
        self._max_history_spin.setRange(10, 1000)
        self._max_history_spin.setSingleStep(10)
        self._max_history_spin.setValue(self._manager.max_history)

        settings_layout.addWidget(self._max_history_spin)
        settings_layout.addStretch()

        layout.addWidget(settings_group)
        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Button actions
        self._undo_btn.clicked.connect(self._on_undo)
        self._redo_btn.clicked.connect(self._on_redo)
        self._clear_btn.clicked.connect(self._on_clear)
        self._max_history_spin.valueChanged.connect(self._on_max_history_changed)

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

        self._undo_count_label.setText(f"Undo: {status['undo_count']}")
        self._redo_count_label.setText(f"Redo: {status['redo_count']}")

        next_undo = status.get("next_undo") or "-"
        next_redo = status.get("next_redo") or "-"

        # Truncate long descriptions
        if len(next_undo) > 30:
            next_undo = next_undo[:27] + "..."
        if len(next_redo) > 30:
            next_redo = next_redo[:27] + "..."

        self._next_undo_label.setText(f"Next Undo: {next_undo}")
        self._next_redo_label.setText(f"Next Redo: {next_redo}")

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
    ) -> None:
        """Initialize UndoRedoToolbar."""
        super().__init__(parent)

        self._manager = manager or EnhancedTabWidget.get_undo_manager()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup compact UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._undo_btn = QPushButton("↶")
        self._undo_btn.setToolTip("Undo (Ctrl+Z)")
        self._undo_btn.setFixedWidth(30)
        self._undo_btn.setEnabled(False)

        self._redo_btn = QPushButton("↷")
        self._redo_btn.setToolTip("Redo (Ctrl+Y)")
        self._redo_btn.setFixedWidth(30)
        self._redo_btn.setEnabled(False)

        layout.addWidget(self._undo_btn)
        layout.addWidget(self._redo_btn)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._undo_btn.clicked.connect(self._manager.undo)
        self._redo_btn.clicked.connect(self._manager.redo)
        self._manager.undoAvailable.connect(self._undo_btn.setEnabled)
        self._manager.redoAvailable.connect(self._redo_btn.setEnabled)
