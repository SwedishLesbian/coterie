"""Chronicle edit dialog for Coterie.

This module implements the dialog for editing existing chronicles,
including updating metadata, toggling active status, and deletion.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QDateEdit, QCheckBox,
    QComboBox, QPushButton, QLabel, QMessageBox,
    QWidget, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
from PyQt6.QtGui import QFont

from src.core.engine import get_session
from src.core.models import Chronicle
from src.core.models.player import Player

logger = logging.getLogger(__name__)


class ChronicleEditDialog(QDialog):
    """Dialog for editing an existing chronicle.

    Signals:
        chronicle_updated: Emitted when the chronicle is successfully saved.
            Payload is a dict with the updated fields.
        chronicle_deleted: Emitted when the chronicle is deleted.
            Payload is the chronicle id.
    """

    chronicle_updated = pyqtSignal(dict)
    chronicle_deleted = pyqtSignal(int)

    def __init__(
        self,
        chronicle: Chronicle,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the edit dialog.

        Args:
            chronicle: The Chronicle object to edit.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.chronicle = chronicle
        self.setWindowTitle(f"Edit Chronicle: {chronicle.name}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)

        self._build_ui()
        self._populate_fields()
        self._connect_signals()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the dialog layout."""
        layout = QVBoxLayout(self)

        # -- Header --
        header = QLabel("Edit Chronicle")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # -- Form --
        form_group = QGroupBox("Chronicle Details")
        form_layout = QFormLayout(form_group)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Chronicle name")
        form_layout.addRow("Name:", self.name_edit)

        self.narrator_edit = QLineEdit()
        self.narrator_edit.setPlaceholderText("Head Storyteller name")
        form_layout.addRow("HST:", self.narrator_edit)

        self.storyteller_combo = QComboBox()
        self.storyteller_combo.addItem("-- None --", None)
        self._load_players()
        form_layout.addRow("Storyteller (Player):", self.storyteller_combo)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Chronicle description")
        self.description_edit.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_edit)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Start Date:", self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setSpecialValueText("Not ended")
        form_layout.addRow("End Date:", self.end_date_edit)

        self.is_active_check = QCheckBox("Active")
        form_layout.addRow("Status:", self.is_active_check)

        layout.addWidget(form_group)

        # -- Button row --
        button_layout = QHBoxLayout()

        self.delete_button = QPushButton("Delete Chronicle")
        self.delete_button.setStyleSheet(
            "QPushButton { color: white; background-color: #c0392b; "
            "padding: 6px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #e74c3c; }"
        )
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save")
        self.save_button.setDefault(True)
        self.save_button.setStyleSheet(
            "QPushButton { color: white; background-color: #2980b9; "
            "padding: 6px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3498db; }"
        )
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _load_players(self) -> None:
        """Populate the storyteller combo with Player records."""
        try:
            session = get_session()
            try:
                players = (
                    session.query(Player)
                    .order_by(Player.name)
                    .all()
                )
                for player in players:
                    self.storyteller_combo.addItem(player.name, player.id)
            finally:
                session.close()
        except Exception as exc:
            logger.warning("Could not load players for storyteller dropdown: %s", exc)

    def _populate_fields(self) -> None:
        """Fill the form with the current chronicle data."""
        c = self.chronicle

        self.name_edit.setText(c.name or "")
        self.narrator_edit.setText(c.narrator or "")
        self.description_edit.setPlainText(c.description or "")
        self.is_active_check.setChecked(c.is_active if c.is_active is not None else True)

        # Start date
        if c.start_date:
            self.start_date_edit.setDate(
                QDate(c.start_date.year, c.start_date.month, c.start_date.day)
            )
        else:
            self.start_date_edit.setDate(QDate.currentDate())

        # End date
        if c.end_date:
            self.end_date_edit.setDate(
                QDate(c.end_date.year, c.end_date.month, c.end_date.day)
            )
        else:
            self.end_date_edit.setDate(self.end_date_edit.minimumDate())

        # Storyteller combo
        if c.storyteller_id is not None:
            idx = self.storyteller_combo.findData(c.storyteller_id)
            if idx >= 0:
                self.storyteller_combo.setCurrentIndex(idx)

    def _connect_signals(self) -> None:
        """Wire up button signals."""
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self.reject)
        self.delete_button.clicked.connect(self._on_delete)
        self.name_edit.textChanged.connect(self._validate)
        self._validate()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        """Enable Save only when required fields are filled."""
        self.save_button.setEnabled(bool(self.name_edit.text().strip()))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_save(self) -> None:
        """Collect form data, emit *chronicle_updated*, and close."""
        end_qdate = self.end_date_edit.date()
        end_date = None
        if end_qdate != self.end_date_edit.minimumDate():
            end_date = datetime(
                end_qdate.year(), end_qdate.month(), end_qdate.day()
            )

        start_qdate = self.start_date_edit.date()
        start_date = datetime(
            start_qdate.year(), start_qdate.month(), start_qdate.day()
        )

        storyteller_id = self.storyteller_combo.currentData()

        data: Dict[str, Any] = {
            "id": self.chronicle.id,
            "name": self.name_edit.text().strip(),
            "narrator": self.narrator_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "start_date": start_date,
            "end_date": end_date,
            "is_active": self.is_active_check.isChecked(),
            "storyteller_id": storyteller_id,
            "last_modified": datetime.now(),
        }

        self.chronicle_updated.emit(data)
        self.accept()

    def _on_delete(self) -> None:
        """Confirm and emit *chronicle_deleted*."""
        reply = QMessageBox.warning(
            self,
            "Delete Chronicle",
            f"Are you sure you want to delete '{self.chronicle.name}'?\n\n"
            "All characters, sessions, plots, and rumors associated with "
            "this chronicle will also be removed. This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.chronicle_deleted.emit(self.chronicle.id)
            self.accept()
