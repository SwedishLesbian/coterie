"""Player manager dialog for managing players in the game."""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session

from ...models.player import Player

class PlayerManagerDialog(QDialog):
    """Dialog for managing players."""
    
    def __init__(self, session: Session, chronicle: Optional[Chronicle], parent: Optional[QWidget] = None):
        """Initialize the player manager dialog.
        
        Args:
            session: Database session
            chronicle: Current chronicle or None for all chronicles
            parent: Parent widget
        """
        super().__init__(parent)
        self.session = session
        self.chronicle = chronicle
        
        self.setWindowTitle("Player Manager")
        self.setModal(True)
        self.resize(600, 400)
        
        self._setup_ui()
        self._load_players()
        
    def _setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout(self)
        
        # Player list
        list_layout = QHBoxLayout()
        
        self.player_list = QListWidget()
        self.player_list.itemSelectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self.player_list)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.add_button = QPushButton("Add Player")
        self.add_button.clicked.connect(self._add_player)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self._edit_player)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._remove_player)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addLayout(list_layout)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
    def _load_players(self):
        """Load players from the database."""
        self.player_list.clear()
        
        query = self.session.query(Player)
        if self.chronicle:
            query = query.filter(Player.chronicle_id == self.chronicle.id)
            
        for player in query.all():
            item = QListWidgetItem(f"{player.name} - {player.status}")
            item.setData(Qt.ItemDataRole.UserRole, player)
            self.player_list.addItem(item)
            
    def _on_selection_changed(self):
        """Handle selection changes in the player list."""
        has_selection = bool(self.player_list.selectedItems())
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)
        
    def _add_player(self):
        """Add a new player."""
        dialog = PlayerEditDialog(self.session, self.chronicle, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_players()
            
    def _edit_player(self):
        """Edit the selected player."""
        selected = self.player_list.selectedItems()
        if not selected:
            return
            
        player = selected[0].data(Qt.ItemDataRole.UserRole)
        dialog = PlayerEditDialog(self.session, self.chronicle, player, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_players()
            
    def _remove_player(self):
        """Remove the selected player."""
        selected = self.player_list.selectedItems()
        if not selected:
            return
            
        player = selected[0].data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove {player.name} from players?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.session.delete(player)
            self.session.commit()
            self._load_players()
            
class PlayerEditDialog(QDialog):
    """Dialog for editing player details."""
    
    def __init__(self, session: Session, chronicle: Optional[Chronicle], player: Optional[Player] = None, parent: Optional[QWidget] = None):
        """Initialize the player edit dialog.
        
        Args:
            session: Database session
            chronicle: Current chronicle or None for all chronicles
            player: Player to edit or None for new player
            parent: Parent widget
        """
        super().__init__(parent)
        self.session = session
        self.chronicle = chronicle
        self.player = player
        
        self.setWindowTitle("Edit Player" if player else "Add Player")
        self.setModal(True)
        
        self._setup_ui()
        if player:
            self._load_player_data()
            
    def _setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QFormLayout(self)
        
        # Name field
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        # Email field
        self.email_edit = QLineEdit()
        layout.addRow("Email:", self.email_edit)
        
        # Status selector
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Suspended"])
        layout.addRow("Status:", self.status_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save_player)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addRow("", button_layout)
        
    def _load_player_data(self):
        """Load existing player data into the form."""
        self.name_edit.setText(self.player.name)
        self.email_edit.setText(self.player.email)
        index = self.status_combo.findText(self.player.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
            
    def _save_player(self):
        """Save the player data."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a name.")
            return
            
        if not self.player:
            self.player = Player()
            self.session.add(self.player)
            
        self.player.name = name
        self.player.email = self.email_edit.text().strip()
        self.player.status = self.status_combo.currentText()
        if self.chronicle:
            self.player.chronicle_id = self.chronicle.id
            
        try:
            self.session.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save player: {str(e)}")
            self.session.rollback() 