"""Game session dialog for Coterie.

This module implements the dialog for creating and editing game sessions
within a chronicle. Each session records a date, title, location, and
summary of what happened during the game.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QDateEdit,
    QPushButton, QLabel, QWidget, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class GameSessionDialog(QDialog):
    """Dialog for creating or editing a game session.

    Signals:
        session_saved: Emitted when the session is saved.
            Payload is a dict with session fields.
    """

    session_saved = pyqtSignal(dict)

    def __init__(
        self,
        chronicle_id: int,
        session_data: Optional[Dict[str, Any]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the session dialog.

        Args:
            chronicle_id: ID of the parent chronicle.
            session_data: Optional dict of existing session data for editing.
                          Keys: id, title, date, location, summary.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.chronicle_id = chronicle_id
        self.session_data = session_data
        self._editing = session_data is not None

        title = "Edit Game Session" if self._editing else "New Game Session"
        self.setWindowTitle(title)
        self.setMinimumWidth(480)
        self.setMinimumHeight(400)

        self._build_ui()
        if self._editing:
            self._populate_fields()
        self._connect_signals()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the dialog layout."""
        layout = QVBoxLayout(self)

        header_text = "Edit Game Session" if self._editing else "New Game Session"
        header = QLabel(header_text)
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        form_group = QGroupBox("Session Details")
        form_layout = QFormLayout(form_group)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Session title (e.g. \"Gathering of Clans\")")
        form_layout.addRow("Title:", self.title_edit)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)

        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Game location")
        form_layout.addRow("Location:", self.location_edit)

        self.summary_edit = QTextEdit()
        self.summary_edit.setPlaceholderText(
            "Summary of what happened during this session..."
        )
        self.summary_edit.setMinimumHeight(120)
        form_layout.addRow("Summary:", self.summary_edit)

        layout.addWidget(form_group)

        # -- Buttons --
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)

        save_label = "Save" if self._editing else "Create"
        self.save_button = QPushButton(save_label)
        self.save_button.setDefault(True)
        self.save_button.setStyleSheet(
            "QPushButton { color: white; background-color: #2980b9; "
            "padding: 6px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3498db; }"
        )
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _populate_fields(self) -> None:
        """Fill the form with existing session data."""
        if not self.session_data:
            return

        self.title_edit.setText(self.session_data.get("title", ""))
        self.location_edit.setText(self.session_data.get("location", ""))
        self.summary_edit.setPlainText(self.session_data.get("summary", ""))

        session_date = self.session_data.get("date")
        if session_date and isinstance(session_date, datetime):
            self.date_edit.setDate(
                QDate(session_date.year, session_date.month, session_date.day)
            )

    def _connect_signals(self) -> None:
        """Wire up button signals."""
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self.reject)
        self.title_edit.textChanged.connect(self._validate)
        self._validate()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        """Enable Save only when title is provided."""
        self.save_button.setEnabled(bool(self.title_edit.text().strip()))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_save(self) -> None:
        """Collect form data, emit *session_saved*, and close."""
        qdate = self.date_edit.date()
        session_date = datetime(qdate.year(), qdate.month(), qdate.day())

        data: Dict[str, Any] = {
            "chronicle_id": self.chronicle_id,
            "title": self.title_edit.text().strip(),
            "date": session_date,
            "location": self.location_edit.text().strip(),
            "summary": self.summary_edit.toPlainText().strip(),
        }

        # Carry forward the id when editing
        if self._editing and self.session_data:
            data["id"] = self.session_data.get("id")

        self.session_saved.emit(data)
        self.accept()
