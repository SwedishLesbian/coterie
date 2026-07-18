"""Character creation dialog for Coterie.

This module implements the character creation interface, allowing users to create
new characters of various World of Darkness types with LARP trait support.
"""

import json
import os
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QSpinBox,
    QPushButton, QFormLayout, QGroupBox,
    QDialogButtonBox, QTabWidget, QScrollArea,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.utils.trait_converter import TraitConverter
from src.ui.widgets.larp_trait_widget import LarpTraitWidget, LarpTraitCategoryWidget
from src.ui.widgets.merit_widget import MeritWidget


def load_trait_adjectives() -> Dict[str, Any]:
    """Load trait adjectives from the data file."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    adjectives_file = os.path.join(data_dir, 'trait_adjectives.json')
    
    try:
        with open(adjectives_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading trait adjectives: {e}")
        return {}

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

        # Backgrounds tab
        backgrounds_tab = QWidget()
        self.tabs.addTab(backgrounds_tab, "Backgrounds")
        backgrounds_scroll = QScrollArea()
        backgrounds_scroll.setWidgetResizable(True)
        backgrounds_layout_tab = QVBoxLayout(backgrounds_tab)
        backgrounds_layout_tab.addWidget(backgrounds_scroll)
        backgrounds_content = QWidget()
        backgrounds_scroll_layout = QVBoxLayout(backgrounds_content)
        backgrounds_scroll.setWidget(backgrounds_content)
        self._create_backgrounds_section(backgrounds_scroll_layout)

        # Merits & Flaws tab
        merits_flaws_tab = QWidget()
        self.tabs.addTab(merits_flaws_tab, "Merits & Flaws")
        merits_flaws_scroll = QScrollArea()
        merits_flaws_scroll.setWidgetResizable(True)
        merits_flaws_layout_tab = QVBoxLayout(merits_flaws_tab)
        merits_flaws_layout_tab.addWidget(merits_flaws_scroll)
        merits_flaws_content = QWidget()
        merits_flaws_scroll_layout = QVBoxLayout(merits_flaws_content)
        merits_flaws_scroll.setWidget(merits_flaws_content)
        self._create_merits_flaws_section(merits_flaws_scroll_layout)

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
        # Fix B (Bug 3): valid Vampire generations are 4-16 per LotN Revised.
        self.generation.setRange(4, 16)
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
        # Load trait adjectives from data file
        trait_adjectives = load_trait_adjectives()
        
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
        
        # Set available traits for each attribute category
        if "physical" in trait_adjectives:
            self.attributes.trait_widgets.get("Physical", None).set_available_traits(trait_adjectives["physical"])
        if "social" in trait_adjectives:
            self.attributes.trait_widgets.get("Social", None).set_available_traits(trait_adjectives["social"])
        if "mental" in trait_adjectives:
            self.attributes.trait_widgets.get("Mental", None).set_available_traits(trait_adjectives["mental"])
            
        attributes_layout.addWidget(self.attributes)
        
        # Negative Traits section
        neg_traits_group = QGroupBox("Negative Traits")
        neg_traits_layout = QVBoxLayout(neg_traits_group)
        parent_layout.addWidget(neg_traits_group)
        
        neg_instr = QLabel(
            "Negative traits represent weaknesses. Each negative trait grants additional Free Traits. "
            "A character may have up to 7 Negative Traits."
        )
        neg_instr.setWordWrap(True)
        neg_traits_layout.addWidget(neg_instr)
        
        initial_negative = {
            "Negative Physical": [],
            "Negative Social": [],
            "Negative Mental": []
        }
        
        self.negative_traits = LarpTraitCategoryWidget(
            category_name="Negative Traits",
            trait_categories=initial_negative
        )
        
        if "negative" in trait_adjectives:
            neg_data = trait_adjectives["negative"]
            if "physical" in neg_data:
                self.negative_traits.trait_widgets.get("Negative Physical", None).set_available_traits(neg_data["physical"])
            if "social" in neg_data:
                self.negative_traits.trait_widgets.get("Negative Social", None).set_available_traits(neg_data["social"])
            if "mental" in neg_data:
                self.negative_traits.trait_widgets.get("Negative Mental", None).set_available_traits(neg_data["mental"])
                
        neg_traits_layout.addWidget(self.negative_traits)
        
        # Abilities section
        abilities_group = QGroupBox("Abilities")
        abilities_layout = QVBoxLayout(abilities_group)
        parent_layout.addWidget(abilities_group)

        abilities_instr = QLabel(
            "Select your character's abilities. Each ability can be taken multiple times "
            "to represent higher levels of expertise."
        )
        abilities_instr.setWordWrap(True)
        abilities_layout.addWidget(abilities_instr)

        # Single flat list for all abilities (MET doesn't split into Talents/Skills/Knowledge)
        self.abilities = LarpTraitWidget("Abilities")
        
        # Set available abilities from the data file
        all_abilities = []
        if "talents" in trait_adjectives:
            all_abilities.extend(trait_adjectives["talents"].keys())
        if "skills" in trait_adjectives:
            all_abilities.extend(trait_adjectives["skills"].keys())
        if "knowledges" in trait_adjectives:
            all_abilities.extend(trait_adjectives["knowledges"].keys())
        self.abilities.set_available_traits(sorted(all_abilities))
        
        abilities_layout.addWidget(self.abilities)

        # Single button for common abilities
        abilities_button = QPushButton("Add Common Abilities")
        abilities_button.clicked.connect(self._add_common_abilities_flat)
        abilities_layout.addWidget(abilities_button)
        
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
        
    def _on_type_changed(self, index: int) -> None:
        """Handle character type selection changes.
        
        Args:
            index: Index of the selected character type
        """
        # Show/hide type-specific groups
        self.vampire_group.setVisible(index == 0)  # Vampire selected
        
        # Enable/disable vampire-specific tabs or sections
        # For future expansion with other character types
        
    def _add_common_abilities_flat(self) -> None:
        """Add common MET abilities from the Laws of the Night rulebook."""
        common_abilities = [
            "Academics", "Alertness", "Animal Ken", "Athletics", "Brawl",
            "Computer", "Crafts", "Dodge", "Drive", "Empathy",
            "Etiquette", "Expression", "Finance", "Firearms",
            "Intimidation", "Investigation", "Law", "Leadership",
            "Linguistics", "Medicine", "Melee", "Occult",
            "Performance", "Politics", "Science", "Security",
            "Stealth", "Streetwise", "Subterfuge", "Survival"
        ]
        self.abilities.set_traits(common_abilities)
        
    def _create_backgrounds_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the backgrounds section."""
        backgrounds_group = QGroupBox("Backgrounds")
        bg_layout = QVBoxLayout(backgrounds_group)
        parent_layout.addWidget(backgrounds_group)

        backgrounds_instr = QLabel(
            "Backgrounds represent social connections and resources. "
            "You may take five Background Traits."
        )
        backgrounds_instr.setWordWrap(True)
        bg_layout.addWidget(backgrounds_instr)

        self.backgrounds = LarpTraitWidget("Backgrounds")
        bg_layout.addWidget(self.backgrounds)

        suggest_bg_button = QPushButton("Add Common Backgrounds")
        suggest_bg_button.clicked.connect(self._add_common_backgrounds)
        bg_layout.addWidget(suggest_bg_button)

    def _create_merits_flaws_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the merits and flaws section."""
        merits_group = QGroupBox("Merits")
        merits_layout = QVBoxLayout(merits_group)
        parent_layout.addWidget(merits_group)

        merits_instr = QLabel("Merits are special advantages purchased with Free Traits.")
        merits_instr.setWordWrap(True)
        merits_layout.addWidget(merits_instr)

        self.merits = MeritWidget("Merits")
        
        # Load merits from the powers data file
        powers_data = self._load_powers_data()
        if "merits" in powers_data:
            self.merits.set_available_merits(powers_data["merits"])
            
        merits_layout.addWidget(self.merits)

        flaws_group = QGroupBox("Flaws")
        flaws_layout = QVBoxLayout(flaws_group)
        parent_layout.addWidget(flaws_group)

        flaws_instr = QLabel(
            "Flaws represent specific deficiencies. Each Flaw grants additional Free Traits. "
            "A character may total up to seven Traits of Flaws."
        )
        flaws_instr.setWordWrap(True)
        flaws_layout.addWidget(flaws_instr)

        self.flaws = LarpTraitWidget("Flaws")
        
        # Load flaws from the powers data file
        if "flaws" in powers_data:
            # Flatten the flaws dictionary into a single list
            all_flaws = []
            for category, flaw_list in powers_data["flaws"].items():
                for flaw in flaw_list:
                    all_flaws.append(flaw.get('name', ''))
            self.flaws.set_available_traits(all_flaws)
            
        flaws_layout.addWidget(self.flaws)

    def _load_powers_data(self) -> Dict[str, Any]:
        """Load powers data from the JSON file.
        
        Returns:
            Dictionary containing powers data (merits, flaws, etc.)
        """
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'powers')
        powers_file = os.path.join(data_dir, 'laws_of_the_night_revised.json')
        
        try:
            with open(powers_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading powers data: {e}")
            return {}

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
        
        # Add abilities (flat list in MET)
        larp_traits["abilities"] = self.abilities.get_traits()
        
        # Add disciplines and backgrounds
        larp_traits["disciplines"] = self.disciplines.get_traits()
        larp_traits["backgrounds"] = self.backgrounds.get_traits()
        larp_traits["merits"] = self.merits.get_merits()
        larp_traits["flaws"] = self.flaws.get_traits()
        
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