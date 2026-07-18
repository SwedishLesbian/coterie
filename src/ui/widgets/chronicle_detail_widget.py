"""Chronicle detail widget for Coterie.

This module implements the main chronicle detail panel that opens when a
chronicle card is clicked.  It shows a header with chronicle metadata and
a QTabWidget with sub-tabs for Characters, Game Sessions, Plots, Rumors,
and Staff -- all scoped to the selected chronicle.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView, QGroupBox,
    QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from src.core.engine import get_session
from src.core.models import Chronicle, Character
from src.core.models.chronicle import GameSession
from src.core.models.staff import Staff
from src.core.models.player import Player
from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog
from src.ui.dialogs.game_session_dialog import GameSessionDialog
from src.ui.widgets.plots_widget import PlotsWidget
from src.ui.widgets.rumors_widget import RumorsWidget

logger = logging.getLogger(__name__)


class ChronicleDetailWidget(QWidget):
    """Full detail view for a single chronicle.

    Signals:
        chronicle_changed: Emitted when the chronicle is updated or deleted
            so the parent can refresh its list.
        character_selected: Emitted when a character row is double-clicked.
            Payload is the character object.
    """

    chronicle_changed = pyqtSignal()
    character_selected = pyqtSignal(object)

    def __init__(
        self,
        chronicle_id: int,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the detail widget.

        Args:
            chronicle_id: ID of the chronicle to display.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.chronicle_id = chronicle_id
        self.chronicle: Optional[Chronicle] = None

        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the full detail layout."""
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        # -- Header section --
        header_box = QGroupBox()
        header_box.setStyleSheet(
            "QGroupBox { border: 2px solid #555; border-radius: 8px; "
            "padding: 12px; background-color: #f5f5f5; }"
        )
        header_layout = QVBoxLayout(header_box)

        # Top row: name + buttons
        top_row = QHBoxLayout()

        self.name_label = QLabel()
        self.name_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        top_row.addWidget(self.name_label)

        top_row.addStretch()

        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet(
            "QPushButton { padding: 4px 14px; }"
        )
        self.edit_button.clicked.connect(self._on_edit)
        top_row.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(
            "QPushButton { color: white; background-color: #c0392b; "
            "padding: 4px 14px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #e74c3c; }"
        )
        self.delete_button.clicked.connect(self._on_delete)
        top_row.addWidget(self.delete_button)

        header_layout.addLayout(top_row)

        # Meta row
        self.meta_label = QLabel()
        self.meta_label.setStyleSheet("color: #666; font-size: 11pt;")
        header_layout.addWidget(self.meta_label)

        root.addWidget(header_box)

        # -- Tabs --
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # Characters tab
        self.characters_table = self._make_table(
            ["Name", "Type", "Clan", "Player", "Status"]
        )
        self.characters_table.doubleClicked.connect(self._on_character_double_click)
        char_widget = QWidget()
        cl = QVBoxLayout(char_widget)
        cl.addWidget(self.characters_table)
        self.tabs.addTab(char_widget, "Characters")

        # Sessions tab
        sessions_widget = QWidget()
        sl = QVBoxLayout(sessions_widget)

        session_btn_row = QHBoxLayout()
        self.new_session_btn = QPushButton("New Session")
        self.new_session_btn.clicked.connect(self._on_new_session)
        session_btn_row.addWidget(self.new_session_btn)

        self.edit_session_btn = QPushButton("Edit Session")
        self.edit_session_btn.clicked.connect(self._on_edit_session)
        self.edit_session_btn.setEnabled(False)
        session_btn_row.addWidget(self.edit_session_btn)

        self.delete_session_btn = QPushButton("Delete Session")
        self.delete_session_btn.clicked.connect(self._on_delete_session)
        self.delete_session_btn.setEnabled(False)
        session_btn_row.addWidget(self.delete_session_btn)

        session_btn_row.addStretch()
        sl.addLayout(session_btn_row)

        self.sessions_table = self._make_table(
            ["Title", "Date", "Location", "Summary"]
        )
        self.sessions_table.itemSelectionChanged.connect(self._on_session_selection)
        sl.addWidget(self.sessions_table)
        self.tabs.addTab(sessions_widget, "Game Sessions")

        # Plots tab
        self.plots_widget = PlotsWidget()
        self.tabs.addTab(self.plots_widget, "Plots")

        # Rumors tab
        self.rumors_widget = RumorsWidget()
        self.tabs.addTab(self.rumors_widget, "Rumors")

        # Staff tab
        staff_widget = QWidget()
        stl = QVBoxLayout(staff_widget)
        self.staff_table = self._make_table(["Name", "Role"])
        stl.addWidget(self.staff_table)
        self.tabs.addTab(staff_widget, "Staff")

    @staticmethod
    def _make_table(columns: List[str]) -> QTableWidget:
        """Create a styled QTableWidget with the given columns."""
        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        return table

    # ------------------------------------------------------------------
    # Data Loading
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Reload all data from the database."""
        try:
            session = get_session()
            try:
                self.chronicle = (
                    session.query(Chronicle)
                    .filter_by(id=self.chronicle_id)
                    .first()
                )
                if not self.chronicle:
                    logger.error("Chronicle %s not found", self.chronicle_id)
                    return

                self._refresh_header()
                self._refresh_characters(session)
                self._refresh_sessions(session)
                self._refresh_staff(session)

                # Scope plots & rumors to this chronicle
                if hasattr(self.plots_widget, "set_chronicle"):
                    self.plots_widget.set_chronicle(self.chronicle_id)
                if hasattr(self.rumors_widget, "set_chronicle"):
                    self.rumors_widget.set_chronicle(self.chronicle_id)
            finally:
                session.close()
        except Exception as exc:
            logger.error("Failed to refresh chronicle detail: %s", exc)

    def _refresh_header(self) -> None:
        """Update the header labels."""
        c = self.chronicle
        self.name_label.setText(c.name or "Untitled Chronicle")

        parts: list[str] = []
        if c.narrator:
            parts.append(f"HST: {c.narrator}")
        status = "Active" if c.is_active else "Inactive"
        parts.append(f"Status: {status}")
        if c.start_date:
            parts.append(f"Started: {c.start_date.strftime('%Y-%m-%d')}")
        if c.end_date:
            parts.append(f"Ended: {c.end_date.strftime('%Y-%m-%d')}")

        self.meta_label.setText("  |  ".join(parts))

    def _refresh_characters(self, session) -> None:
        """Load characters belonging to this chronicle."""
        characters = (
            session.query(Character)
            .filter(Character.chronicle_id == self.chronicle_id)
            .order_by(Character.name)
            .all()
        )

        self.characters_table.setRowCount(len(characters))
        self._character_objects = []

        for row, char in enumerate(characters):
            # Pre-load attributes to avoid lazy-load issues
            _ = char.id, char.name, char.type, char.status
            player_name = getattr(char, "player_name", "") or ""
            clan = getattr(char, "clan", "") or ""

            self.characters_table.setItem(row, 0, QTableWidgetItem(char.name or ""))
            self.characters_table.setItem(row, 1, QTableWidgetItem(char.type or ""))
            self.characters_table.setItem(row, 2, QTableWidgetItem(clan))
            self.characters_table.setItem(row, 3, QTableWidgetItem(player_name))
            self.characters_table.setItem(row, 4, QTableWidgetItem(char.status or ""))
            self._character_objects.append(char)

        # Update header character count
        count_text = self.meta_label.text()
        if "Characters:" not in count_text:
            self.meta_label.setText(
                f"{count_text}  |  Characters: {len(characters)}"
            )

    def _refresh_sessions(self, session) -> None:
        """Load game sessions for this chronicle."""
        sessions = (
            session.query(GameSession)
            .filter(GameSession.chronicle_id == self.chronicle_id)
            .order_by(GameSession.date.desc())
            .all()
        )

        self.sessions_table.setRowCount(len(sessions))
        self._session_objects = []

        for row, gs in enumerate(sessions):
            self.sessions_table.setItem(row, 0, QTableWidgetItem(gs.title or ""))
            date_str = gs.date.strftime("%Y-%m-%d") if gs.date else ""
            self.sessions_table.setItem(row, 1, QTableWidgetItem(date_str))
            self.sessions_table.setItem(row, 2, QTableWidgetItem(gs.location or ""))
            summary = (gs.summary or "")[:80]
            if len(gs.summary or "") > 80:
                summary += "..."
            self.sessions_table.setItem(row, 3, QTableWidgetItem(summary))
            self._session_objects.append(gs)

    def _refresh_staff(self, session) -> None:
        """Load staff for this chronicle."""
        staff_list = (
            session.query(Staff)
            .filter(Staff.chronicle_id == self.chronicle_id)
            .order_by(Staff.name)
            .all()
        )

        self.staff_table.setRowCount(len(staff_list))
        for row, s in enumerate(staff_list):
            self.staff_table.setItem(row, 0, QTableWidgetItem(s.name or ""))
            self.staff_table.setItem(row, 1, QTableWidgetItem(s.role or ""))

    # ------------------------------------------------------------------
    # Chronicle Actions
    # ------------------------------------------------------------------

    def _on_edit(self) -> None:
        """Open the chronicle edit dialog."""
        if not self.chronicle:
            return

        dialog = ChronicleEditDialog(self.chronicle, self)
        dialog.chronicle_updated.connect(self._apply_chronicle_update)
        dialog.chronicle_deleted.connect(self._apply_chronicle_delete)
        dialog.exec()

    def _apply_chronicle_update(self, data: Dict[str, Any]) -> None:
        """Persist chronicle updates to the database."""
        try:
            session = get_session()
            try:
                chronicle = (
                    session.query(Chronicle)
                    .filter_by(id=data["id"])
                    .first()
                )
                if not chronicle:
                    return

                chronicle.name = data["name"]
                chronicle.narrator = data["narrator"]
                chronicle.description = data["description"]
                chronicle.start_date = data["start_date"]
                chronicle.end_date = data["end_date"]
                chronicle.is_active = data["is_active"]
                chronicle.storyteller_id = data["storyteller_id"]
                chronicle.last_modified = data["last_modified"]

                session.commit()
                self.refresh()
                self.chronicle_changed.emit()
                logger.info("Updated chronicle: %s", data["name"])
            finally:
                session.close()
        except Exception as exc:
            logger.error("Failed to update chronicle: %s", exc)
            QMessageBox.critical(self, "Error", f"Failed to update chronicle: {exc}")

    def _apply_chronicle_delete(self, chronicle_id: int) -> None:
        """Delete the chronicle and all related records."""
        try:
            session = get_session()
            try:
                chronicle = (
                    session.query(Chronicle)
                    .filter_by(id=chronicle_id)
                    .first()
                )
                if chronicle:
                    # Delete related sessions
                    session.query(GameSession).filter_by(
                        chronicle_id=chronicle_id
                    ).delete()
                    # Delete related staff
                    session.query(Staff).filter_by(
                        chronicle_id=chronicle_id
                    ).delete()
                    # Unlink characters (don't delete them)
                    session.query(Character).filter_by(
                        chronicle_id=chronicle_id
                    ).update({"chronicle_id": None})

                    session.delete(chronicle)
                    session.commit()
                    self.chronicle_changed.emit()
                    logger.info("Deleted chronicle %s", chronicle_id)
            finally:
                session.close()
        except Exception as exc:
            logger.error("Failed to delete chronicle: %s", exc)
            QMessageBox.critical(self, "Error", f"Failed to delete chronicle: {exc}")

    def _on_delete(self) -> None:
        """Confirm and delete the chronicle."""
        if not self.chronicle:
            return

        reply = QMessageBox.warning(
            self,
            "Delete Chronicle",
            f"Are you sure you want to delete '{self.chronicle.name}'?\n\n"
            "Sessions and staff records will be removed. "
            "Characters will be unlinked but not deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._apply_chronicle_delete(self.chronicle.id)

    # ------------------------------------------------------------------
    # Character Actions
    # ------------------------------------------------------------------

    def _on_character_double_click(self, index) -> None:
        """Emit character_selected when a row is double-clicked."""
        row = index.row()
        if 0 <= row < len(self._character_objects):
            self.character_selected.emit(self._character_objects[row])

    # ------------------------------------------------------------------
    # Session Actions
    # ------------------------------------------------------------------

    def _on_session_selection(self) -> None:
        """Enable/disable session edit/delete buttons."""
        has_selection = bool(self.sessions_table.selectedItems())
        self.edit_session_btn.setEnabled(has_selection)
        self.delete_session_btn.setEnabled(has_selection)

    def _on_new_session(self) -> None:
        """Open dialog to create a new game session."""
        dialog = GameSessionDialog(self.chronicle_id, parent=self)
        dialog.session_saved.connect(self._save_session)
        dialog.exec()

    def _on_edit_session(self) -> None:
        """Open dialog to edit the selected game session."""
        row = self.sessions_table.currentRow()
        if row < 0 or row >= len(self._session_objects):
            return

        gs = self._session_objects[row]
        data = {
            "id": gs.id,
            "title": gs.title,
            "date": gs.date,
            "location": gs.location,
            "summary": gs.summary,
        }
        dialog = GameSessionDialog(self.chronicle_id, session_data=data, parent=self)
        dialog.session_saved.connect(self._save_session)
        dialog.exec()

    def _save_session(self, data: Dict[str, Any]) -> None:
        """Create or update a game session in the database."""
        try:
            session = get_session()
            try:
                if data.get("id"):
                    # Update existing
                    gs = (
                        session.query(GameSession)
                        .filter_by(id=data["id"])
                        .first()
                    )
                    if gs:
                        gs.title = data["title"]
                        gs.date = data["date"]
                        gs.location = data["location"]
                        gs.summary = data["summary"]
                else:
                    # Create new
                    gs = GameSession(
                        chronicle_id=data["chronicle_id"],
                        title=data["title"],
                        date=data["date"],
                        location=data["location"],
                        summary=data["summary"],
                    )
                    session.add(gs)

                session.commit()
                self.refresh()
                logger.info("Saved session: %s", data["title"])
            finally:
                session.close()
        except Exception as exc:
            logger.error("Failed to save session: %s", exc)
            QMessageBox.critical(self, "Error", f"Failed to save session: {exc}")

    def _on_delete_session(self) -> None:
        """Delete the selected game session."""
        row = self.sessions_table.currentRow()
        if row < 0 or row >= len(self._session_objects):
            return

        gs = self._session_objects[row]
        reply = QMessageBox.question(
            self,
            "Delete Session",
            f"Delete session '{gs.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            session = get_session()
            try:
                obj = session.query(GameSession).filter_by(id=gs.id).first()
                if obj:
                    session.delete(obj)
                    session.commit()
                self.refresh()
                logger.info("Deleted session: %s", gs.title)
            finally:
                session.close()
        except Exception as exc:
            logger.error("Failed to delete session: %s", exc)
            QMessageBox.critical(self, "Error", f"Failed to delete session: {exc}")
