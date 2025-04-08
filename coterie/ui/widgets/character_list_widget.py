"""Widget for displaying and managing a list of characters."""

from typing import List, Optional, Dict, Any, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QMenu, QAbstractItemView, QHBoxLayout, QLabel, 
    QPushButton, QComboBox
)
from PyQt6.QtCore import pyqtSignal, Qt

from coterie.models.base import Character
from coterie.models.vampire import Vampire


class CharacterListWidget(QWidget):
    """Widget for displaying and managing a list of characters."""
    
    character_selected = pyqtSignal(Character)
    character_deleted = pyqtSignal(int)  # Character ID
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the character list widget.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create filter controls
        filter_layout = QHBoxLayout()
        layout.addLayout(filter_layout)
        
        # Type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Vampire", "Werewolf", "Mage", "Other"])
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        # Status filter
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Inactive"])
        self.status_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)
        
        # Create buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        
        # New button (handled by parent)
        self.new_button = QPushButton("New Character")
        button_layout.addWidget(self.new_button)
        
        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete_selected)
        button_layout.addWidget(delete_button)
        
        # Store characters
        self.characters: List[Character] = []
        self.filtered_characters: List[Character] = []
        
    def set_characters(self, characters: List[Character]) -> None:
        """Set the characters to display.
        
        Args:
            characters: List of characters
        """
        self.characters = characters
        self._apply_filters()
        
    def add_character(self, character: Character) -> None:
        """Add a character to the list.
        
        Args:
            character: Character to add
        """
        self.characters.append(character)
        self._apply_filters()
        
    def refresh(self) -> None:
        """Refresh the character list."""
        self._apply_filters()
        
    def get_selected_character(self) -> Optional[Character]:
        """Get the currently selected character.
        
        Returns:
            Selected character or None if none selected
        """
        items = self.list_widget.selectedItems()
        if not items:
            return None
            
        item = items[0]
        character_id = item.data(Qt.ItemDataRole.UserRole)
        
        for character in self.filtered_characters:
            if character.id == character_id:
                return character
                
        return None
        
    def _apply_filters(self) -> None:
        """Apply filters to the character list."""
        # Get filter values
        type_filter = self.type_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        # Apply filters
        self.filtered_characters = []
        for character in self.characters:
            # Type filter
            if type_filter != "All":
                if type_filter == "Vampire" and not isinstance(character, Vampire):
                    continue
                # Add other character type checks as they are implemented
                    
            # Status filter
            if status_filter != "All":
                if status_filter == "Active" and character.status != "Active":
                    continue
                if status_filter == "Inactive" and character.status != "Inactive":
                    continue
                    
            self.filtered_characters.append(character)
            
        # Update list widget
        self._update_list_widget()
        
    def _update_list_widget(self) -> None:
        """Update the list widget with filtered characters."""
        self.list_widget.clear()
        
        for character in self.filtered_characters:
            item = QListWidgetItem(character.name)
            
            # Set tooltip with character info
            tooltip = f"Name: {character.name}\n"
            tooltip += f"Type: {character.type.capitalize()}\n"
            tooltip += f"Player: {character.player}\n"
            tooltip += f"Status: {character.status}"
            item.setToolTip(tooltip)
            
            # Store character ID
            item.setData(Qt.ItemDataRole.UserRole, character.id)
            
            self.list_widget.addItem(item)
            
    def _on_selection_changed(self) -> None:
        """Handle selection change in the list widget."""
        character = self.get_selected_character()
        if character:
            self.character_selected.emit(character)
            
    def _show_context_menu(self, position) -> None:
        """Show context menu for character list item.
        
        Args:
            position: Position to show menu
        """
        character = self.get_selected_character()
        if not character:
            return
            
        menu = QMenu()
        
        # Add menu items
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: self.character_selected.emit(character))
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self._delete_character(character))
        
        # Other actions can be added here
        
        menu.exec(self.list_widget.mapToGlobal(position))
        
    def _delete_selected(self) -> None:
        """Delete the selected character."""
        character = self.get_selected_character()
        if character:
            self._delete_character(character)
            
    def _delete_character(self, character: Character) -> None:
        """Delete a character.
        
        Args:
            character: Character to delete
        """
        # Emit signal for parent to handle
        self.character_deleted.emit(character.id)
        
        # Remove from internal lists
        self.characters = [c for c in self.characters if c.id != character.id]
        self.filtered_characters = [c for c in self.filtered_characters if c.id != character.id]
        
        # Update list widget
        self._update_list_widget() 