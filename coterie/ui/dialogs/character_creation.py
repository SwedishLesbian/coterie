"""Character creation dialog for Coterie.

This module implements the character creation interface, allowing users to create
new characters of various World of Darkness types with LARP trait support.
"""

from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QSpinBox,
    QPushButton, QFormLayout, QGroupBox,
    QDialogButtonBox, QTabWidget, QScrollArea,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from coterie.utils.trait_converter import TraitConverter
from coterie.ui.widgets.larp_trait_widget import LarpTraitWidget, LarpTraitCategoryWidget

class CharacterCreationDialog(QDialog):
    """Dialog for creating new World of Darkness characters with LARP trait support."""
    
    character_created = pyqtSignal(dict)  # Emitted when a character is created
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the character creation dialog.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Create New Character")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Create the layout
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Basic information tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        self.tabs.addTab(basic_tab, "Basic Info")
        
        # Create basic information section
        self._create_basic_info_section(basic_layout)
        
        # Traits tab
        traits_tab = QWidget()
        self.tabs.addTab(traits_tab, "Traits")
        
        # Create a scroll area for the traits
        traits_scroll = QScrollArea()
        traits_scroll.setWidgetResizable(True)
        traits_layout = QVBoxLayout(traits_tab)
        traits_layout.addWidget(traits_scroll)
        
        traits_content = QWidget()
        traits_scroll_layout = QVBoxLayout(traits_content)
        traits_scroll.setWidget(traits_content)
        
        # Create trait sections
        self._create_trait_sections(traits_scroll_layout)
        
        # Advantages tab for disciplines, backgrounds, etc.
        advantages_tab = QWidget()
        self.tabs.addTab(advantages_tab, "Advantages")
        
        # Create a scroll area for the advantages
        advantages_scroll = QScrollArea()
        advantages_scroll.setWidgetResizable(True)
        advantages_layout = QVBoxLayout(advantages_tab)
        advantages_layout.addWidget(advantages_scroll)
        
        advantages_content = QWidget()
        advantages_scroll_layout = QVBoxLayout(advantages_content)
        advantages_scroll.setWidget(advantages_content)
        
        # Create advantage sections
        self._create_advantage_sections(advantages_scroll_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def _create_basic_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the basic information section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        parent_layout.addWidget(basic_group)
        
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
        
        # Player field
        self.player_name = QLineEdit()
        basic_layout.addRow("&Player:", self.player_name)
        
        # Nature and Demeanor
        self.nature = QLineEdit()
        basic_layout.addRow("&Nature:", self.nature)
        
        self.demeanor = QLineEdit()
        basic_layout.addRow("&Demeanor:", self.demeanor)
        
        # Player information
        self.narrator = QLineEdit()
        basic_layout.addRow("&Narrator:", self.narrator)
        
        # Vampire-specific group
        self.vampire_group = QGroupBox("Vampire Details")
        vampire_layout = QFormLayout(self.vampire_group)
        parent_layout.addWidget(self.vampire_group)
        
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
        
    def _create_trait_sections(self, parent_layout: QVBoxLayout) -> None:
        """Create the trait sections (attributes, abilities).
        
        Args:
            parent_layout: Parent layout to add to
        """
        # Attributes section
        attributes_group = QGroupBox("Attributes")
        attributes_layout = QVBoxLayout(attributes_group)
        parent_layout.addWidget(attributes_group)
        
        # Instruction label
        attributes_instr = QLabel(
            "Select your character's attributes. In Mind's Eye Theater, attributes are "
            "represented as adjectives rather than numeric values."
        )
        attributes_instr.setWordWrap(True)
        attributes_layout.addWidget(attributes_instr)
        
        # Create LARP trait category widget for attributes
        # Initialize with some default traits from TraitConverter
        initial_attributes = {
            "Physical": TraitConverter.get_random_trait_adjectives("physical", 3),
            "Social": TraitConverter.get_random_trait_adjectives("social", 3),
            "Mental": TraitConverter.get_random_trait_adjectives("mental", 3)
        }
        
        self.attributes = LarpTraitCategoryWidget(
            category_name="Attributes",
            trait_categories=initial_attributes
        )
        attributes_layout.addWidget(self.attributes)
        
        # Abilities section
        abilities_group = QGroupBox("Abilities")
        abilities_layout = QVBoxLayout(abilities_group)
        parent_layout.addWidget(abilities_group)
        
        # Instruction label
        abilities_instr = QLabel(
            "Select your character's abilities. These represent what your character knows how to do."
        )
        abilities_instr.setWordWrap(True)
        abilities_layout.addWidget(abilities_instr)
        
        # Create LARP trait category widget for abilities
        # Initialize with empty categories
        self.abilities = LarpTraitCategoryWidget(
            category_name="Abilities",
            trait_categories={
                "Talents": [],
                "Skills": [],
                "Knowledges": []
            }
        )
        abilities_layout.addWidget(self.abilities)
        
        # Add some helper buttons for quick ability selection
        talents_button = QPushButton("Add Common Talents")
        talents_button.clicked.connect(lambda: self._add_common_abilities("talents"))
        abilities_layout.addWidget(talents_button)
        
        skills_button = QPushButton("Add Common Skills")
        skills_button.clicked.connect(lambda: self._add_common_abilities("skills"))
        abilities_layout.addWidget(skills_button)
        
        knowledges_button = QPushButton("Add Common Knowledges")
        knowledges_button.clicked.connect(lambda: self._add_common_abilities("knowledges"))
        abilities_layout.addWidget(knowledges_button)
        
    def _create_advantage_sections(self, parent_layout: QVBoxLayout) -> None:
        """Create the advantage sections (disciplines, backgrounds, etc.).
        
        Args:
            parent_layout: Parent layout to add to
        """
        # Disciplines section
        disciplines_group = QGroupBox("Disciplines")
        disciplines_layout = QVBoxLayout(disciplines_group)
        parent_layout.addWidget(disciplines_group)
        
        # Instruction label
        disciplines_instr = QLabel(
            "Add your character's disciplines. These are vampire-specific powers."
        )
        disciplines_instr.setWordWrap(True)
        disciplines_layout.addWidget(disciplines_instr)
        
        # Create LARP trait widget for disciplines
        self.disciplines = LarpTraitWidget("Disciplines")
        disciplines_layout.addWidget(self.disciplines)
        
        # Add discipline suggestions based on clan selection
        suggest_button = QPushButton("Suggest Clan Disciplines")
        suggest_button.clicked.connect(self._suggest_clan_disciplines)
        disciplines_layout.addWidget(suggest_button)
        
        # Backgrounds section
        backgrounds_group = QGroupBox("Backgrounds")
        backgrounds_layout = QVBoxLayout(backgrounds_group)
        parent_layout.addWidget(backgrounds_group)
        
        # Instruction label
        backgrounds_instr = QLabel(
            "Add your character's backgrounds. These represent social connections and resources."
        )
        backgrounds_instr.setWordWrap(True)
        backgrounds_layout.addWidget(backgrounds_instr)
        
        # Create LARP trait widget for backgrounds
        self.backgrounds = LarpTraitWidget("Backgrounds")
        backgrounds_layout.addWidget(self.backgrounds)
        
        # Add some common backgrounds
        suggest_bg_button = QPushButton("Add Common Backgrounds")
        suggest_bg_button.clicked.connect(self._add_common_backgrounds)
        backgrounds_layout.addWidget(suggest_bg_button)
        
    def _on_type_changed(self, index: int) -> None:
        """Handle character type selection changes.
        
        Args:
            index: Index of the selected character type
        """
        # Show/hide type-specific groups
        self.vampire_group.setVisible(index == 0)  # Vampire selected
        
        # Enable/disable vampire-specific tabs or sections
        # For future expansion with other character types
        
    def _add_common_abilities(self, ability_type: str) -> None:
        """Add common abilities of a specific type.
        
        Args:
            ability_type: Type of abilities to add (talents, skills, knowledges)
        """
        trait_categories = self.abilities.get_category_traits()
        
        if ability_type == "talents":
            # Add common talents
            common_talents = [
                "Alert", "Athletic", "Brawny", "Charming", "Creative",
                "Empathic", "Expressive", "Intimidating", "Persuasive", "Streetwise"
            ]
            trait_categories["Talents"] = common_talents
            
        elif ability_type == "skills":
            # Add common skills
            common_skills = [
                "Animal Ken", "Crafty", "Driving", "Etiquette", "Firearms",
                "Melee", "Performance", "Stealthy", "Survival", "Technical"
            ]
            trait_categories["Skills"] = common_skills
            
        elif ability_type == "knowledges":
            # Add common knowledges
            common_knowledges = [
                "Academic", "Computer", "Finance", "Investigation", "Law",
                "Linguistics", "Medicine", "Occult", "Politics", "Science"
            ]
            trait_categories["Knowledges"] = common_knowledges
            
        # Update the widget
        self.abilities.set_category_traits(trait_categories)
        
    def _suggest_clan_disciplines(self) -> None:
        """Suggest disciplines based on clan selection."""
        clan = self.clan.currentText()
        disciplines = []
        
        # Add clan-specific disciplines
        if clan == "Brujah":
            disciplines = ["Celerity", "Potence", "Presence"]
        elif clan == "Gangrel":
            disciplines = ["Animalism", "Fortitude", "Protean"]
        elif clan == "Malkavian":
            disciplines = ["Auspex", "Dementation", "Obfuscate"]
        elif clan == "Nosferatu":
            disciplines = ["Animalism", "Obfuscate", "Potence"]
        elif clan == "Toreador":
            disciplines = ["Auspex", "Celerity", "Presence"]
        elif clan == "Tremere":
            disciplines = ["Auspex", "Dominate", "Thaumaturgy"]
        elif clan == "Ventrue":
            disciplines = ["Dominate", "Fortitude", "Presence"]
        elif clan == "Assamite":
            disciplines = ["Celerity", "Obfuscate", "Quietus"]
        elif clan == "Followers of Set":
            disciplines = ["Obfuscate", "Presence", "Serpentis"]
        elif clan == "Giovanni":
            disciplines = ["Dominate", "Necromancy", "Potence"]
        elif clan == "Lasombra":
            disciplines = ["Dominate", "Obtenebration", "Potence"]
        elif clan == "Ravnos":
            disciplines = ["Animalism", "Chimerstry", "Fortitude"]
        elif clan == "Tzimisce":
            disciplines = ["Animalism", "Auspex", "Vicissitude"]
        # Add format like "Discipline 1" for actual gameplay
        formatted_disciplines = []
        for discipline in disciplines:
            formatted_disciplines.append(f"{discipline} 1")
        
        # Update the disciplines widget
        self.disciplines.set_traits(formatted_disciplines)
        
    def _add_common_backgrounds(self) -> None:
        """Add common backgrounds."""
        common_backgrounds = [
            "Allies 1", 
            "Contacts 1", 
            "Fame 1", 
            "Herd 1", 
            "Influence 1",
            "Mentor 1", 
            "Resources 1", 
            "Retainers 1", 
            "Status 1"
        ]
        
        # Update the backgrounds widget
        self.backgrounds.set_traits(common_backgrounds)
        
    def get_character_data(self) -> Dict[str, Any]:
        """Get the entered character data.
        
        Returns:
            Dictionary containing the character data
        """
        data = {
            "type": self.char_type.currentText(),
            "name": self.name.text(),
            "nature": self.nature.text(),
            "demeanor": self.demeanor.text(),
            "player": self.player_name.text(),
            "narrator": self.narrator.text()
        }
        
        # Add vampire-specific data if applicable
        if self.char_type.currentIndex() == 0:
            data.update({
                "clan": self.clan.currentText(),
                "generation": self.generation.value(),
                "sect": self.sect.currentText()
            })
        
        # Add LARP traits
        larp_traits = {}
        
        # Add attributes
        attribute_traits = self.attributes.get_category_traits()
        for category, traits in attribute_traits.items():
            larp_traits[category.lower()] = traits
        
        # Add abilities
        ability_traits = self.abilities.get_category_traits()
        for category, traits in ability_traits.items():
            larp_traits[category.lower()] = traits
        
        # Add disciplines and backgrounds
        larp_traits["disciplines"] = self.disciplines.get_traits()
        larp_traits["backgrounds"] = self.backgrounds.get_traits()
        
        # Add to data
        data["larp_traits"] = larp_traits
            
        return data
    
    def accept(self) -> None:
        """Handle dialog acceptance."""
        # Emit the character data
        self.character_created.emit(self.get_character_data())
        super().accept()

    def _validate_data(self) -> bool:
        """Validate the form data."""
        if not self.name.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter a character name.")
            return False
            
        if not self.player_name.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter a player name.")
            return False
            
        if not self.nature.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter a nature.")
            return False
            
        if not self.demeanor.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter a demeanor.")
            return False
            
        return True 