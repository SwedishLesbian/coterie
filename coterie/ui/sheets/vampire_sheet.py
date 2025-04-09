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
from coterie.models.larp_trait import LarpTrait, TraitCategory
from coterie.utils.data_loader import DataLoader
from coterie.ui.widgets.trait_group_widget import TraitGroupWidget
from coterie.ui.widgets.trait_widget import TraitWidget
from coterie.ui.widgets.larp_trait_widget import LarpTraitWidget, LarpTraitCategoryWidget
from coterie.utils.trait_converter import TraitConverter

class VampireSheet(QWidget):
    """Character sheet display for Vampire: The Masquerade characters."""
    
    modified = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the vampire character sheet.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create character info header
        self._create_character_info_section()
        
        # Create the main content area with scrolling
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)
        
        # Create content widget for scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        
        # Add trait sections
        self._create_attributes_section(self.content_layout)
        self._create_abilities_section(self.content_layout)
        self._create_disciplines_section(self.content_layout)
        self._create_backgrounds_section(self.content_layout)
        self._create_virtues_section(self.content_layout)
        self._create_stats_section(self.content_layout)
        self._create_description_section(self.content_layout)
        
    def _create_character_info_section(self) -> None:
        """Create the character information section."""
        # Character info group
        info_group = QGroupBox("Character Information")
        info_layout = QFormLayout(info_group)
        self.main_layout.addWidget(info_group)
        
        # Character name
        self.name = QLineEdit()
        self.name.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Name:", self.name)
        
        # Player name
        self.player = QLineEdit()
        self.player.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Player:", self.player)
        
        # Chronicle section
        chronicle_layout = QHBoxLayout()
        self.chronicle_name = QLineEdit()
        self.chronicle_name.setReadOnly(True)  # Chronicle name is read-only
        chronicle_layout.addWidget(self.chronicle_name)
        
        # Add button to assign a chronicle
        self.assign_chronicle_button = QPushButton("Assign")
        self.assign_chronicle_button.clicked.connect(self._on_assign_chronicle)
        chronicle_layout.addWidget(self.assign_chronicle_button)
        
        info_layout.addRow("Chronicle:", chronicle_layout)
        
        # Nature and Demeanor
        self.nature = QLineEdit()
        self.nature.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Nature:", self.nature)
        
        self.demeanor = QLineEdit()
        self.demeanor.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Demeanor:", self.demeanor)
        
        # Clan
        self.clan = QLineEdit()
        self.clan.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Clan:", self.clan)
        
        # Generation
        self.generation = QSpinBox()
        self.generation.setRange(3, 15)
        self.generation.setValue(13)
        self.generation.valueChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Generation:", self.generation)
        
        # Sect
        self.sect = QLineEdit()
        self.sect.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Sect:", self.sect)
        
    def _on_assign_chronicle(self) -> None:
        """Show dialog to assign the character to a chronicle."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel, QListWidgetItem
        from PyQt6.QtCore import Qt
        from coterie.database.engine import get_session
        from coterie.models.chronicle import Chronicle
        
        # Create a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Assign Chronicle")
        dialog.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add label
        layout.addWidget(QLabel("Select a chronicle to assign this character to:"))
        
        # Add list widget
        chronicle_list = QListWidget()
        layout.addWidget(chronicle_list)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Get chronicles from database
        session = get_session()
        try:
            chronicles = session.query(Chronicle).all()
            
            # Add chronicles to list
            for chronicle in chronicles:
                item = QListWidgetItem(f"{chronicle.name} (HST: {chronicle.narrator})")
                item.setData(Qt.ItemDataRole.UserRole, chronicle.id)
                chronicle_list.addItem(item)
                
                # Pre-select the current chronicle if set
                if self.character and self.character.chronicle_id == chronicle.id:
                    chronicle_list.setCurrentItem(item)
                    
        finally:
            session.close()
            
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted and chronicle_list.currentItem():
            chronicle_id = chronicle_list.currentItem().data(Qt.ItemDataRole.UserRole)
            
            # Update the character's chronicle
            if self.character:
                session = get_session()
                try:
                    self.character.chronicle_id = chronicle_id
                    session.add(self.character)
                    session.commit()
                    
                    # Update the displayed chronicle name
                    chronicle = session.query(Chronicle).filter_by(id=chronicle_id).first()
                    if chronicle:
                        self.chronicle_name.setText(chronicle.name)
                        
                    self.modified.emit()
                finally:
                    session.close()
        
    def _create_attributes_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the attributes section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        attributes_group = QGroupBox("Attributes")
        attributes_layout = QVBoxLayout(attributes_group)
        parent_layout.addWidget(attributes_group)
        
        # Create LARP trait category widget for attributes
        self.attributes = LarpTraitCategoryWidget(
            category_name="Attributes",
            trait_categories={
                "Physical": [],
                "Social": [],
                "Mental": []
            }
        )
        self.attributes.categoryChanged.connect(lambda c, t: self.modified.emit())
        attributes_layout.addWidget(self.attributes)
        
    def _create_abilities_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the abilities section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        abilities_group = QGroupBox("Abilities")
        abilities_layout = QVBoxLayout(abilities_group)
        parent_layout.addWidget(abilities_group)
        
        # Create LARP trait category widget for abilities
        self.abilities = LarpTraitCategoryWidget(
            category_name="Abilities",
            trait_categories={
                "Talents": [],
                "Skills": [],
                "Knowledges": []
            }
        )
        self.abilities.categoryChanged.connect(lambda c, t: self.modified.emit())
        abilities_layout.addWidget(self.abilities)
        
    def _create_disciplines_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the disciplines section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        disciplines_group = QGroupBox("Disciplines")
        disciplines_layout = QVBoxLayout(disciplines_group)
        parent_layout.addWidget(disciplines_group)
        
        # Create LARP trait widget for disciplines
        self.disciplines = LarpTraitWidget("Disciplines")
        self.disciplines.traitChanged.connect(lambda n, t: self.modified.emit())
        disciplines_layout.addWidget(self.disciplines)
        
    def _create_backgrounds_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the backgrounds section.
        
        Args:
            parent_layout: Parent layout to add to
        """
        backgrounds_group = QGroupBox("Backgrounds")
        backgrounds_layout = QVBoxLayout(backgrounds_group)
        parent_layout.addWidget(backgrounds_group)
        
        # Create LARP trait widget for backgrounds
        self.backgrounds = LarpTraitWidget("Backgrounds")
        self.backgrounds.traitChanged.connect(lambda n, t: self.modified.emit())
        backgrounds_layout.addWidget(self.backgrounds)
        
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
        # Store reference to the character
        self.character = character
        
        # Basic information
        self.name.setText(character.name)
        self.player.setText(character.player)
        self.nature.setText(character.nature)
        self.demeanor.setText(character.demeanor)
        
        # Chronicle information
        self._load_chronicle_info(character)
        
        # Vampire-specific information
        self.clan.setText(character.clan)
        self.generation.setValue(character.generation)
        self.sect.setText(character.sect)
        
        # Load LARP traits
        self._load_larp_traits(character)
        
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
        
    def _load_chronicle_info(self, character: Vampire) -> None:
        """Load the character's chronicle information.
        
        Args:
            character: Vampire character to load chronicle info from
        """
        if character.chronicle_id:
            # Get the chronicle from the database
            from coterie.database.engine import get_session
            from coterie.models.chronicle import Chronicle
            
            session = get_session()
            try:
                chronicle = session.query(Chronicle).filter_by(id=character.chronicle_id).first()
                if chronicle:
                    self.chronicle_name.setText(chronicle.name)
                else:
                    self.chronicle_name.setText("Unknown Chronicle")
            finally:
                session.close()
        else:
            self.chronicle_name.setText("No Chronicle Assigned")
        
    def _load_larp_traits(self, character: Vampire) -> None:
        """Load LARP traits into appropriate widgets by category.
        
        Args:
            character: Vampire character to load traits from
        """
        # Initialize trait category dictionaries
        attribute_traits = {
            "Physical": [],
            "Social": [],
            "Mental": []
        }
        
        ability_traits = {
            "Talents": [],
            "Skills": [],
            "Knowledges": []
        }
        
        discipline_traits = []
        background_traits = []
        
        # Check if character has LARP traits
        if hasattr(character, 'larp_traits') and character.larp_traits:
            # Process all LARP traits
            for trait in character.larp_traits:
                # Safety check for categories attribute
                if not hasattr(trait, 'categories'):
                    continue
                    
                # Check each trait's categories
                for category in trait.categories:
                    category_name = category.name.lower()
                    
                    # Handle attributes
                    if category_name == "physical":
                        attribute_traits["Physical"].append(trait.display_name)
                    elif category_name == "social":
                        attribute_traits["Social"].append(trait.display_name)
                    elif category_name == "mental":
                        attribute_traits["Mental"].append(trait.display_name)
                    
                    # Handle abilities
                    elif category_name == "talents":
                        ability_traits["Talents"].append(trait.display_name)
                    elif category_name == "skills":
                        ability_traits["Skills"].append(trait.display_name)
                    elif category_name == "knowledges":
                        ability_traits["Knowledges"].append(trait.display_name)
                    
                    # Handle other types
                    elif category_name == "disciplines":
                        discipline_traits.append(trait.display_name)
                    elif category_name == "backgrounds":
                        background_traits.append(trait.display_name)
        else:
            # Old-style character using dot-based traits - convert to LARP traits on-the-fly
            # Process legacy traits if they exist
            if hasattr(character, 'traits'):
                for trait in character.traits:
                    # Convert based on category
                    trait_category = trait.category.lower()
                    trait_name = trait.name.lower()
                    trait_value = trait.value
                    
                    # Handle attributes
                    if trait_category in ["physical", "social", "mental"]:
                        # Convert dot value to adjectives
                        adjectives = TraitConverter.dot_rating_to_adjectives(
                            trait_name, trait_value, trait_category
                        )
                        
                        if trait_category == "physical":
                            attribute_traits["Physical"].extend(adjectives)
                        elif trait_category == "social":
                            attribute_traits["Social"].extend(adjectives)
                        elif trait_category == "mental":
                            attribute_traits["Mental"].extend(adjectives)
                    
                    # Handle abilities
                    elif trait_category in ["talents", "skills", "knowledges"]:
                        # Convert dot value to adjectives
                        adjectives = TraitConverter.dot_rating_to_adjectives(
                            trait_name, trait_value, trait_category
                        )
                        
                        if trait_category == "talents":
                            ability_traits["Talents"].extend(adjectives)
                        elif trait_category == "skills":
                            ability_traits["Skills"].extend(adjectives)
                        elif trait_category == "knowledges":
                            ability_traits["Knowledges"].extend(adjectives)
                    
                    # Handle disciplines
                    elif trait_category == "disciplines":
                        # Use generic adjectives for disciplines
                        adjectives = [f"{trait.name} {i}" for i in range(1, trait_value + 1)]
                        discipline_traits.extend(adjectives)
                    
                    # Handle backgrounds
                    elif trait_category == "backgrounds":
                        # Use generic adjectives for backgrounds
                        adjectives = [f"{trait.name} {i}" for i in range(1, trait_value + 1)]
                        background_traits.extend(adjectives)
        
        # Update widgets with collected traits
        self.attributes.set_category_traits(attribute_traits)
        self.abilities.set_category_traits(ability_traits)
        self.disciplines.set_traits(discipline_traits)
        self.backgrounds.set_traits(background_traits)
        
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
            
            # Chronicle information
            "chronicle_id": self.character.chronicle_id if hasattr(self.character, 'chronicle_id') else None,
            
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
            
            # LARP Traits
            "larp_traits": self._collect_all_larp_traits()
        }
        
        return data
        
    def _collect_all_larp_traits(self) -> Dict:
        """Collect all LARP traits from the sheet.
        
        Returns:
            Dictionary of trait lists by category
        """
        larp_traits = {}
        
        # Get attributes
        attribute_traits = self.attributes.get_category_traits()
        for subcategory, traits in attribute_traits.items():
            larp_traits[subcategory.lower()] = traits
        
        # Get abilities
        ability_traits = self.abilities.get_category_traits()
        for subcategory, traits in ability_traits.items():
            larp_traits[subcategory.lower()] = traits
        
        # Get disciplines and backgrounds
        larp_traits["disciplines"] = self.disciplines.get_traits()
        larp_traits["backgrounds"] = self.backgrounds.get_traits()
        
        return larp_traits 