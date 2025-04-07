"""Vampire character sheet display for Coterie.

This module implements the character sheet interface for Vampire: The Masquerade
characters, displaying all relevant attributes, abilities, and other traits.
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QGroupBox,
    QScrollArea, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from coterie.models.vampire import Vampire, Discipline, Ritual, Bond
from coterie.models.base import Trait

class TraitTable(QTableWidget):
    """Table widget for displaying character traits."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the trait table.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(0, 2, parent)  # 0 rows, 2 columns (Name, Value)
        
        # Set up the table
        self.setHorizontalHeaderLabels(["Trait", "Rating"])
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(60)  # Width of Rating column
        
        # Style
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
    def set_traits(self, traits: List[Trait]) -> None:
        """Set the traits to display in the table.
        
        Args:
            traits: List of traits to display
        """
        self.setRowCount(len(traits))
        
        for i, trait in enumerate(traits):
            name_item = QTableWidgetItem(trait.name)
            value_item = QTableWidgetItem("●" * trait.value)
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.setItem(i, 0, name_item)
            self.setItem(i, 1, value_item)

class VampireSheet(QWidget):
    """Character sheet display for Vampire: The Masquerade characters."""
    
    modified = pyqtSignal()  # Emitted when the character is modified
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the vampire character sheet.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        # Create the layout
        layout = QVBoxLayout(self)
        
        # Create a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Create the main content widget
        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        
        # Header section
        header = QGroupBox("Character Information")
        header_layout = QFormLayout(header)
        content_layout.addWidget(header)
        
        # Basic information
        self.name = QLineEdit()
        header_layout.addRow("Name:", self.name)
        
        self.player = QLineEdit()
        header_layout.addRow("Player:", self.player)
        
        self.nature = QLineEdit()
        header_layout.addRow("Nature:", self.nature)
        
        self.demeanor = QLineEdit()
        header_layout.addRow("Demeanor:", self.demeanor)
        
        # Vampire-specific information
        self.clan = QLineEdit()
        header_layout.addRow("Clan:", self.clan)
        
        self.generation = QSpinBox()
        self.generation.setRange(4, 15)
        header_layout.addRow("Generation:", self.generation)
        
        self.sect = QLineEdit()
        header_layout.addRow("Sect:", self.sect)
        
        # Attributes section
        attributes = QGroupBox("Attributes")
        attributes_layout = QHBoxLayout(attributes)
        content_layout.addWidget(attributes)
        
        # Physical attributes
        physical = QGroupBox("Physical")
        physical_layout = QVBoxLayout(physical)
        self.physical_table = TraitTable()
        physical_layout.addWidget(self.physical_table)
        attributes_layout.addWidget(physical)
        
        # Social attributes
        social = QGroupBox("Social")
        social_layout = QVBoxLayout(social)
        self.social_table = TraitTable()
        social_layout.addWidget(self.social_table)
        attributes_layout.addWidget(social)
        
        # Mental attributes
        mental = QGroupBox("Mental")
        mental_layout = QVBoxLayout(mental)
        self.mental_table = TraitTable()
        mental_layout.addWidget(self.mental_table)
        attributes_layout.addWidget(mental)
        
        # Abilities section
        abilities = QGroupBox("Abilities")
        abilities_layout = QVBoxLayout(abilities)
        self.abilities_table = TraitTable()
        abilities_layout.addWidget(self.abilities_table)
        content_layout.addWidget(abilities)
        
        # Disciplines section
        disciplines = QGroupBox("Disciplines")
        disciplines_layout = QVBoxLayout(disciplines)
        self.disciplines_table = TraitTable()
        disciplines_layout.addWidget(self.disciplines_table)
        content_layout.addWidget(disciplines)
        
        # Backgrounds section
        backgrounds = QGroupBox("Backgrounds")
        backgrounds_layout = QVBoxLayout(backgrounds)
        self.backgrounds_table = TraitTable()
        backgrounds_layout.addWidget(self.backgrounds_table)
        content_layout.addWidget(backgrounds)
        
        # Virtues section
        virtues = QGroupBox("Virtues")
        virtues_layout = QFormLayout(virtues)
        content_layout.addWidget(virtues)
        
        self.conscience = QSpinBox()
        self.conscience.setRange(0, 5)
        virtues_layout.addRow("Conscience:", self.conscience)
        
        self.self_control = QSpinBox()
        self.self_control.setRange(0, 5)
        virtues_layout.addRow("Self-Control:", self.self_control)
        
        self.courage = QSpinBox()
        self.courage.setRange(0, 5)
        virtues_layout.addRow("Courage:", self.courage)
        
        # Path/Humanity
        path = QGroupBox("Path of Enlightenment")
        path_layout = QFormLayout(path)
        content_layout.addWidget(path)
        
        self.path = QLineEdit()
        path_layout.addRow("Path:", self.path)
        
        self.path_rating = QSpinBox()
        self.path_rating.setRange(0, 10)
        path_layout.addRow("Rating:", self.path_rating)
        
        # Willpower and Blood Pool
        stats = QGroupBox("Stats")
        stats_layout = QFormLayout(stats)
        content_layout.addWidget(stats)
        
        self.willpower = QSpinBox()
        self.willpower.setRange(0, 10)
        stats_layout.addRow("Willpower:", self.willpower)
        
        self.blood = QSpinBox()
        self.blood.setRange(0, 20)
        stats_layout.addRow("Blood Pool:", self.blood)
        
    def load_character(self, character: Vampire) -> None:
        """Load a vampire character into the sheet.
        
        Args:
            character: The vampire character to display
        """
        # Basic information
        self.name.setText(character.name)
        self.player.setText(character.player)
        self.nature.setText(character.nature)
        self.demeanor.setText(character.demeanor)
        
        # Vampire-specific information
        self.clan.setText(character.clan)
        self.generation.setValue(character.generation)
        self.sect.setText(character.sect)
        
        # Load traits
        physical_traits = [t for t in character.traits if t.category == "physical"]
        social_traits = [t for t in character.traits if t.category == "social"]
        mental_traits = [t for t in character.traits if t.category == "mental"]
        abilities = [t for t in character.traits if t.type == "ability"]
        disciplines = [t for t in character.traits if isinstance(t, Discipline)]
        backgrounds = [t for t in character.traits if t.type == "background"]
        
        self.physical_table.set_traits(physical_traits)
        self.social_table.set_traits(social_traits)
        self.mental_table.set_traits(mental_traits)
        self.abilities_table.set_traits(abilities)
        self.disciplines_table.set_traits(disciplines)
        self.backgrounds_table.set_traits(backgrounds)
        
        # Virtues and Path
        self.conscience.setValue(character.conscience)
        self.self_control.setValue(character.self_control)
        self.courage.setValue(character.courage)
        self.path.setText(character.path)
        self.path_rating.setValue(character.path_traits)
        
        # Stats
        self.willpower.setValue(character.willpower)
        self.blood.setValue(character.blood) 