"""Vampire character sheet display for Coterie.

This module implements the character sheet interface for Vampire: The Masquerade
characters, displaying all relevant attributes, abilities, and other traits.
"""

from typing import Optional, List, Dict
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QGroupBox,
    QScrollArea, QPushButton, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from coterie.models.vampire import Vampire, Discipline, Ritual, Bond
from coterie.models.base import Trait
from coterie.utils.data_loader import DataLoader
from coterie.ui.widgets.trait_group_widget import TraitGroupWidget
from coterie.ui.widgets.trait_widget import TraitWidget

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
        
        # Character information section
        self._create_character_info_section(content_layout)
        
        # Create tab widget for different sections
        tabs = QTabWidget()
        content_layout.addWidget(tabs)
        
        # Attributes & Abilities tab
        attributes_tab = QWidget()
        attributes_layout = QVBoxLayout(attributes_tab)
        tabs.addTab(attributes_tab, "Attributes & Abilities")
        
        # Attributes section
        self._create_attributes_section(attributes_layout)
        
        # Abilities section
        self._create_abilities_section(attributes_layout)
        
        # Advantages tab
        advantages_tab = QWidget()
        advantages_layout = QVBoxLayout(advantages_tab)
        tabs.addTab(advantages_tab, "Advantages")
        
        # Disciplines section
        self._create_disciplines_section(advantages_layout)
        
        # Backgrounds section
        self._create_backgrounds_section(advantages_layout)
        
        # Virtues & Path section
        self._create_virtues_section(advantages_layout)
        
        # Character tab
        character_tab = QWidget()
        character_layout = QVBoxLayout(character_tab)
        tabs.addTab(character_tab, "Character")
        
        # Stats section (Willpower, Blood, etc.)
        self._create_stats_section(character_layout)
        
        # Character description section
        self._create_description_section(character_layout)
        
    def _create_character_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the character information section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        header = QGroupBox("Character Information")
        header_layout = QFormLayout(header)
        parent_layout.addWidget(header)
        
        # Basic information
        self.name = QLineEdit()
        self.name.textChanged.connect(lambda: self.modified.emit())
        header_layout.addRow("Name:", self.name)
        
        self.player = QLineEdit()
        self.player.textChanged.connect(lambda: self.modified.emit())
        header_layout.addRow("Player:", self.player)
        
        self.nature = QLineEdit()
        self.nature.textChanged.connect(lambda: self.modified.emit())
        header_layout.addRow("Nature:", self.nature)
        
        self.demeanor = QLineEdit()
        self.demeanor.textChanged.connect(lambda: self.modified.emit())
        header_layout.addRow("Demeanor:", self.demeanor)
        
        # Vampire-specific information
        self.clan = QLineEdit()
        self.clan.textChanged.connect(lambda: self.modified.emit())
        header_layout.addRow("Clan:", self.clan)
        
        self.generation = QSpinBox()
        self.generation.setRange(4, 15)
        self.generation.valueChanged.connect(lambda: self.modified.emit())
        header_layout.addRow("Generation:", self.generation)
        
        self.sect = QLineEdit()
        self.sect.textChanged.connect(lambda: self.modified.emit())
        header_layout.addRow("Sect:", self.sect)
        
    def _create_attributes_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the attributes section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        attributes_group = QGroupBox("Attributes")
        attributes_layout = QHBoxLayout(attributes_group)
        parent_layout.addWidget(attributes_group)
        
        # Data paths for attributes
        attributes_file = DataLoader.get_data_path("attributes.json")
        
        # Physical attributes
        self.physical_attributes = TraitGroupWidget(
            title="Physical",
            max_value=5,
            data_file=attributes_file,
            category="physical",
            editable=True,
            show_temp=True
        )
        self.physical_attributes.trait_changed.connect(lambda n, v: self.modified.emit())
        attributes_layout.addWidget(self.physical_attributes)
        
        # Social attributes
        self.social_attributes = TraitGroupWidget(
            title="Social",
            max_value=5,
            data_file=attributes_file,
            category="social",
            editable=True,
            show_temp=True
        )
        self.social_attributes.trait_changed.connect(lambda n, v: self.modified.emit())
        attributes_layout.addWidget(self.social_attributes)
        
        # Mental attributes
        self.mental_attributes = TraitGroupWidget(
            title="Mental",
            max_value=5,
            data_file=attributes_file,
            category="mental",
            editable=True,
            show_temp=True
        )
        self.mental_attributes.trait_changed.connect(lambda n, v: self.modified.emit())
        attributes_layout.addWidget(self.mental_attributes)
        
    def _create_abilities_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the abilities section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        abilities_group = QGroupBox("Abilities")
        abilities_layout = QHBoxLayout(abilities_group)
        parent_layout.addWidget(abilities_group)
        
        # Data paths for abilities
        abilities_file = DataLoader.get_data_path("abilities.json")
        
        # Talents
        self.talents = TraitGroupWidget(
            title="Talents",
            max_value=5,
            data_file=abilities_file,
            category="talents",
            editable=True,
            allow_custom=True
        )
        self.talents.trait_changed.connect(lambda n, v: self.modified.emit())
        abilities_layout.addWidget(self.talents)
        
        # Skills
        self.skills = TraitGroupWidget(
            title="Skills",
            max_value=5,
            data_file=abilities_file,
            category="skills",
            editable=True,
            allow_custom=True
        )
        self.skills.trait_changed.connect(lambda n, v: self.modified.emit())
        abilities_layout.addWidget(self.skills)
        
        # Knowledges
        self.knowledges = TraitGroupWidget(
            title="Knowledges",
            max_value=5,
            data_file=abilities_file,
            category="knowledges",
            editable=True,
            allow_custom=True
        )
        self.knowledges.trait_changed.connect(lambda n, v: self.modified.emit())
        abilities_layout.addWidget(self.knowledges)
        
    def _create_disciplines_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the disciplines section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        disciplines_file = DataLoader.get_data_path("disciplines.json")
        
        self.disciplines = TraitGroupWidget(
            title="Disciplines",
            max_value=5,
            data_file=disciplines_file,
            category="disciplines",
            editable=True,
            allow_custom=True
        )
        self.disciplines.trait_changed.connect(lambda n, v: self.modified.emit())
        parent_layout.addWidget(self.disciplines)
        
    def _create_backgrounds_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the backgrounds section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        backgrounds_file = DataLoader.get_data_path("backgrounds.json")
        
        self.backgrounds = TraitGroupWidget(
            title="Backgrounds",
            max_value=5,
            data_file=backgrounds_file,
            editable=True,
            allow_custom=True
        )
        self.backgrounds.trait_changed.connect(lambda n, v: self.modified.emit())
        parent_layout.addWidget(self.backgrounds)
        
    def _create_virtues_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the virtues and path section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        # Virtues group
        virtues_group = QGroupBox("Virtues")
        virtues_layout = QVBoxLayout(virtues_group)
        parent_layout.addWidget(virtues_group)
        
        # Create individual trait widgets for virtues
        self.conscience = TraitWidget(
            name="Conscience",
            max_value=5,
            show_temp=True,
            category="virtue"
        )
        self.conscience.value_changed.connect(lambda v: self.modified.emit())
        virtues_layout.addWidget(self.conscience)
        
        self.self_control = TraitWidget(
            name="Self-Control",
            max_value=5,
            show_temp=True,
            category="virtue"
        )
        self.self_control.value_changed.connect(lambda v: self.modified.emit())
        virtues_layout.addWidget(self.self_control)
        
        self.courage = TraitWidget(
            name="Courage",
            max_value=5,
            show_temp=True,
            category="virtue"
        )
        self.courage.value_changed.connect(lambda v: self.modified.emit())
        virtues_layout.addWidget(self.courage)
        
        # Path of Enlightenment
        path_group = QGroupBox("Path of Enlightenment")
        path_layout = QFormLayout(path_group)
        parent_layout.addWidget(path_group)
        
        paths_file = DataLoader.get_data_path("paths.json")
        
        # Path name
        self.path = QLineEdit("Humanity")
        self.path.textChanged.connect(lambda: self.modified.emit())
        path_layout.addRow("Path:", self.path)
        
        # Path rating
        self.path_rating = TraitWidget(
            name="Path Rating",
            max_value=10,
            show_temp=True,
            category="path"
        )
        self.path_rating.value_changed.connect(lambda v: self.modified.emit())
        path_layout.addRow("Rating:", self.path_rating)
        
    def _create_stats_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the stats section (willpower, blood pool).
        
        Args:
            parent_layout: Parent layout to add to
        """
        stats_group = QGroupBox("Stats")
        stats_layout = QVBoxLayout(stats_group)
        parent_layout.addWidget(stats_group)
        
        # Willpower
        self.willpower = TraitWidget(
            name="Willpower",
            max_value=10,
            show_temp=True,
            category="stat"
        )
        self.willpower.value_changed.connect(lambda v: self.modified.emit())
        stats_layout.addWidget(self.willpower)
        
        # Blood Pool
        self.blood = TraitWidget(
            name="Blood Pool",
            max_value=20,
            show_temp=True,
            category="stat"
        )
        self.blood.value_changed.connect(lambda v: self.modified.emit())
        stats_layout.addWidget(self.blood)
        
    def _create_description_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the character description section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        description_group = QGroupBox("Description")
        description_layout = QFormLayout(description_group)
        parent_layout.addWidget(description_group)
        
        # Fields to add: Concept, Chronicle, Sire, Title, etc.
        # These will be implemented in a future update
        
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
        self._load_traits_by_category(character)
        
        # Virtues and Path
        self.conscience.set_value(character.conscience)
        self.conscience.set_temp_value(character.temp_conscience)
        
        self.self_control.set_value(character.self_control)
        self.self_control.set_temp_value(character.temp_self_control)
        
        self.courage.set_value(character.courage)
        self.courage.set_temp_value(character.temp_courage)
        
        self.path.setText(character.path)
        self.path_rating.set_value(character.path_traits)
        self.path_rating.set_temp_value(character.temp_path_traits)
        
        # Stats
        self.willpower.set_value(character.willpower)
        self.willpower.set_temp_value(character.temp_willpower)
        
        self.blood.set_value(character.blood)
        self.blood.set_temp_value(character.temp_blood)
        
    def _load_traits_by_category(self, character: Vampire) -> None:
        """Load character traits into appropriate widgets by category.
        
        Args:
            character: Vampire character to load traits from
        """
        # Clear existing traits
        for trait_group in [
            self.physical_attributes, self.social_attributes, self.mental_attributes,
            self.talents, self.skills, self.knowledges,
            self.disciplines, self.backgrounds
        ]:
            trait_group.set_traits({})
        
        # Process all traits
        for trait in character.traits:
            category = trait.category.lower()
            trait_type = trait.type.lower()
            
            # Handle attributes
            if category == "physical":
                self.physical_attributes.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
            elif category == "social":
                self.social_attributes.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
            elif category == "mental":
                self.mental_attributes.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
            # Handle abilities
            elif trait_type == "talent":
                self.talents.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
            elif trait_type == "skill":
                self.skills.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
            elif trait_type == "knowledge":
                self.knowledges.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
            # Handle disciplines and backgrounds
            elif trait_type == "discipline" or isinstance(trait, Discipline):
                self.disciplines.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
            elif trait_type == "background":
                self.backgrounds.add_trait(
                    trait.name, trait.value, 
                    getattr(trait, 'temp_value', trait.value), 
                    getattr(trait, 'note', "")
                )
                
    def get_character_data(self) -> Dict:
        """Get the character data from the sheet.
        
        Returns:
            Dictionary of character data
        """
        # Basic information
        data = {
            "name": self.name.text(),
            "player": self.player.text(),
            "nature": self.nature.text(),
            "demeanor": self.demeanor.text(),
            "clan": self.clan.text(),
            "generation": self.generation.value(),
            "sect": self.sect.text(),
            
            # Virtues and Path
            "conscience": self.conscience.get_value(),
            "temp_conscience": self.conscience.get_temp_value(),
            "self_control": self.self_control.get_value(),
            "temp_self_control": self.self_control.get_temp_value(),
            "courage": self.courage.get_value(),
            "temp_courage": self.courage.get_temp_value(),
            "path": self.path.text(),
            "path_traits": self.path_rating.get_value(),
            "temp_path_traits": self.path_rating.get_temp_value(),
            
            # Stats
            "willpower": self.willpower.get_value(),
            "temp_willpower": self.willpower.get_temp_value(),
            "blood": self.blood.get_value(),
            "temp_blood": self.blood.get_temp_value(),
            
            # Traits
            "traits": self._collect_all_traits()
        }
        
        return data
        
    def _collect_all_traits(self) -> List[Dict]:
        """Collect all traits from the sheet.
        
        Returns:
            List of trait dictionaries
        """
        traits = []
        
        # Helper function to add traits from a trait group
        def add_traits_from_group(group, category, trait_type):
            for name, (value, temp_value) in group.get_trait_values().items():
                traits.append({
                    "name": name,
                    "value": value,
                    "temp_value": temp_value,
                    "category": category,
                    "type": trait_type
                })
                
        # Add attributes
        add_traits_from_group(self.physical_attributes, "physical", "attribute")
        add_traits_from_group(self.social_attributes, "social", "attribute")
        add_traits_from_group(self.mental_attributes, "mental", "attribute")
        
        # Add abilities
        add_traits_from_group(self.talents, "ability", "talent")
        add_traits_from_group(self.skills, "ability", "skill")
        add_traits_from_group(self.knowledges, "ability", "knowledge")
        
        # Add disciplines and backgrounds
        add_traits_from_group(self.disciplines, "vampire", "discipline")
        add_traits_from_group(self.backgrounds, "general", "background")
        
        return traits 