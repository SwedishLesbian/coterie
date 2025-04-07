"""Character creation dialog for Grapevine.

This module implements the character creation interface, allowing users to create
new characters of various World of Darkness types.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QSpinBox,
    QPushButton, QFormLayout, QGroupBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class CharacterCreationDialog(QDialog):
    """Dialog for creating new World of Darkness characters."""
    
    character_created = pyqtSignal(dict)  # Emitted when a character is created
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the character creation dialog.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Create New Character")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        # Create the layout
        layout = QVBoxLayout(self)
        
        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        layout.addWidget(basic_group)
        
        # Character type selection
        self.char_type = QComboBox()
        self.char_type.addItems([
            "Vampire: The Masquerade",
            "Werewolf: The Apocalypse",
            "Mage: The Ascension",
            "Wraith: The Oblivion",
            "Changeling: The Dreaming",
            "Hunter: The Reckoning",
            "Mummy: The Resurrection",
            "Demon: The Fallen",
            "Mortal"
        ])
        basic_layout.addRow("Character &Type:", self.char_type)
        
        # Name field
        self.name = QLineEdit()
        basic_layout.addRow("&Name:", self.name)
        
        # Nature and Demeanor
        self.nature = QComboBox()
        self.nature.setEditable(True)
        nature_items = [
            "Architect", "Autocrat", "Bon Vivant", "Bravo",
            "Caregiver", "Celebrant", "Conformist", "Conniver",
            "Curmudgeon", "Defender", "Deviant", "Director",
            "Fanatic", "Gallant", "Judge", "Loner",
            "Martyr", "Masochist", "Monster", "Pedagogue",
            "Penitent", "Perfectionist", "Rebel", "Rogue",
            "Survivor", "Traditionalist", "Trickster", "Visionary"
        ]
        self.nature.addItems(nature_items)
        basic_layout.addRow("N&ature:", self.nature)
        
        self.demeanor = QComboBox()
        self.demeanor.setEditable(True)
        self.demeanor.addItems(nature_items)
        basic_layout.addRow("&Demeanor:", self.demeanor)
        
        # Player information
        self.player = QLineEdit()
        basic_layout.addRow("&Player:", self.player)
        
        self.narrator = QLineEdit()
        basic_layout.addRow("&Narrator:", self.narrator)
        
        # Vampire-specific group (initially hidden)
        self.vampire_group = QGroupBox("Vampire Details")
        self.vampire_group.setVisible(False)
        vampire_layout = QFormLayout(self.vampire_group)
        layout.addWidget(self.vampire_group)
        
        # Clan selection
        self.clan = QComboBox()
        self.clan.addItems([
            "Assamite", "Brujah", "Followers of Set", "Gangrel",
            "Giovanni", "Lasombra", "Malkavian", "Nosferatu",
            "Ravnos", "Toreador", "Tremere", "Tzimisce",
            "Ventrue", "Caitiff"
        ])
        vampire_layout.addRow("Cl&an:", self.clan)
        
        # Generation
        self.generation = QSpinBox()
        self.generation.setRange(4, 15)
        self.generation.setValue(13)
        vampire_layout.addRow("&Generation:", self.generation)
        
        # Sect
        self.sect = QComboBox()
        self.sect.addItems(["Camarilla", "Sabbat", "Anarch", "Independent", "Autarkis"])
        vampire_layout.addRow("&Sect:", self.sect)
        
        # Connect signals
        self.char_type.currentIndexChanged.connect(self._on_type_changed)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def _on_type_changed(self, index: int) -> None:
        """Handle character type selection changes.
        
        Args:
            index: Index of the selected character type
        """
        # Show/hide type-specific groups
        self.vampire_group.setVisible(index == 0)  # Vampire selected
        
    def get_character_data(self) -> Dict[str, Any]:
        """Get the entered character data.
        
        Returns:
            Dictionary containing the character data
        """
        data = {
            "type": self.char_type.currentText(),
            "name": self.name.text(),
            "nature": self.nature.currentText(),
            "demeanor": self.demeanor.currentText(),
            "player": self.player.text(),
            "narrator": self.narrator.text()
        }
        
        # Add vampire-specific data if applicable
        if self.char_type.currentIndex() == 0:
            data.update({
                "clan": self.clan.currentText(),
                "generation": self.generation.value(),
                "sect": self.sect.currentText()
            })
            
        return data
    
    def accept(self) -> None:
        """Handle dialog acceptance."""
        # Emit the character data
        self.character_created.emit(self.get_character_data())
        super().accept() 