"""Vampire character sheet display for Coterie.

This module implements the character sheet interface for Vampire: The Masquerade
characters, displaying all relevant attributes, abilities, and other traits using
the Mind's Eye Theater LARP adjective-based trait system.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QGroupBox,
    QScrollArea, QPushButton, QTabWidget, QFrame, QGridLayout,
    QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from coterie.models.vampire import Vampire
from coterie.models.larp_trait import LarpTrait, TraitCategory
from coterie.utils.data_loader import (
    load_data, get_category, get_descriptions,
    get_item_description, clear_cache, load_character,
    prepare_character_for_ui
)
from coterie.ui.widgets.larp_trait_widget import LarpTraitWidget, LarpTraitCategoryWidget

class VampireSheet(QWidget):
    """Character sheet display for Vampire: The Masquerade LARP characters."""
    
    modified = pyqtSignal()
    character_changed = pyqtSignal()
    
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
        
        # Create tabs
        self.tabs = QTabWidget()
        self.content_layout.addWidget(self.tabs)
        
        # Create basic info tab
        self.basic_tab = QWidget()
        self.basic_layout = QFormLayout(self.basic_tab)
        self.tabs.addTab(self.basic_tab, "Basic Info")
        
        # Add basic info fields
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(lambda: self.modified.emit())
        self.basic_layout.addRow("Name:", self.name_edit)
        
        self.player_edit = QLineEdit()
        self.player_edit.textChanged.connect(lambda: self.modified.emit())
        self.basic_layout.addRow("Player:", self.player_edit)
        
        self.chronicle_edit = QLineEdit()
        self.chronicle_edit.setReadOnly(True)  # Chronicle name is read-only
        self.basic_layout.addRow("Chronicle:", self.chronicle_edit)
        
        self.clan_combo = QComboBox()
        self.clan_combo.addItems(get_category("clans", "clans"))
        self.clan_combo.currentTextChanged.connect(lambda: self.modified.emit())
        self.basic_layout.addRow("Clan:", self.clan_combo)
        
        self.generation_spin = QSpinBox()
        self.generation_spin.setRange(4, 15)
        self.generation_spin.setValue(13)
        self.generation_spin.valueChanged.connect(lambda: self.modified.emit())
        self.basic_layout.addRow("Generation:", self.generation_spin)
        
        self.nature_combo = QComboBox()
        self.nature_combo.addItems(get_category("natures", "natures"))
        self.nature_combo.currentTextChanged.connect(lambda: self.modified.emit())
        self.basic_layout.addRow("Nature:", self.nature_combo)
        
        self.demeanor_combo = QComboBox()
        self.demeanor_combo.addItems(get_category("demeanors", "demeanors"))
        self.demeanor_combo.currentTextChanged.connect(lambda: self.modified.emit())
        self.basic_layout.addRow("Demeanor:", self.demeanor_combo)
        
        # Create traits tab
        self.traits_tab = QWidget()
        self.traits_layout = QVBoxLayout(self.traits_tab)
        self.tabs.addTab(self.traits_tab, "Traits")
        
        # Add trait categories
        for category in ["Physical", "Social", "Mental", "Skills", "Knowledges"]:
            group = QGroupBox(category)
            group_layout = QVBoxLayout(group)
            
            widget = LarpTraitCategoryWidget(category)
            widget.categoryChanged.connect(lambda c, t: self.modified.emit())
            group_layout.addWidget(widget)
            
            self.traits_layout.addWidget(group)
        
        # Create disciplines tab
        self.disciplines_tab = QWidget()
        self.disciplines_layout = QVBoxLayout(self.disciplines_tab)
        self.tabs.addTab(self.disciplines_tab, "Disciplines")
        
        # Add discipline widgets
        self.disciplines_group = QGroupBox("Disciplines")
        self.disciplines_group_layout = QVBoxLayout(self.disciplines_group)
        
        for discipline in get_category("disciplines", "disciplines"):
            widget = LarpTraitWidget(discipline)
            widget.traitChanged.connect(lambda n, t: self.modified.emit())
            self.disciplines_group_layout.addWidget(widget)
            
        self.disciplines_layout.addWidget(self.disciplines_group)
        
        # Create backgrounds tab
        self.backgrounds_tab = QWidget()
        self.backgrounds_layout = QVBoxLayout(self.backgrounds_tab)
        self.tabs.addTab(self.backgrounds_tab, "Backgrounds")
        
        # Add background widgets
        self.backgrounds_group = QGroupBox("Backgrounds")
        self.backgrounds_group_layout = QVBoxLayout(self.backgrounds_group)
        
        for background in get_category("backgrounds", "backgrounds"):
            widget = LarpTraitWidget(background)
            widget.traitChanged.connect(lambda n, t: self.modified.emit())
            self.backgrounds_group_layout.addWidget(widget)
            
        self.backgrounds_layout.addWidget(self.backgrounds_group)
        
        # Create notes tab
        self.notes_tab = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_tab)
        self.tabs.addTab(self.notes_tab, "Notes")
        
        # Add notes editor
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter character notes here...")
        self.notes_layout.addWidget(self.notes_edit)
        
        # Add save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_character)
        self.main_layout.addWidget(self.save_button)
        
        # Store character ID
        self.character_id = None
        
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
        self.player_name = QLineEdit()
        self.player_name.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("Player:", self.player_name)
        
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
        
        # HST (formerly Storyteller)
        self.storyteller = QLineEdit()
        self.storyteller.textChanged.connect(lambda: self.modified.emit())
        info_layout.addRow("HST:", self.storyteller)
        
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
                    # Store current traits before assignment
                    current_traits = self.character.larp_traits if hasattr(self.character, 'larp_traits') else []
                    
                    # Update chronicle
                    self.character.chronicle_id = chronicle_id
                    
                    # Ensure traits are preserved
                    if hasattr(self.character, 'larp_traits'):
                        self.character.larp_traits = current_traits
                    
                    session.add(self.character)
                    session.commit()
                    
                    # Update the displayed chronicle name
                    chronicle = session.query(Chronicle).filter_by(id=chronicle_id).first()
                    if chronicle:
                        self.chronicle_name.setText(chronicle.name)
                        
                    self.modified.emit()
                finally:
                    session.close()
        
    def load_character(self, character_id: int) -> None:
        """Load a character by ID."""
        try:
            # Load character
            character = load_character(character_id)
            
            if not character:
                QMessageBox.critical(
                    self,
                    "Load Error",
                    f"Failed to load character {character_id}"
                )
                return
                
            # Store character ID
            self.character_id = character_id
            
            # Update basic info
            self.name_edit.setText(character.name)
            self.player_edit.setText(character.player_name)
            self.chronicle_edit.setText(character.chronicle.name if character.chronicle else "")
            
            if hasattr(character, "clan"):
                index = self.clan_combo.findText(character.clan)
                if index >= 0:
                    self.clan_combo.setCurrentIndex(index)
                    
            if hasattr(character, "generation"):
                self.generation_spin.setValue(character.generation)
                
            if hasattr(character, "nature"):
                index = self.nature_combo.findText(character.nature)
                if index >= 0:
                    self.nature_combo.setCurrentIndex(index)
                    
            if hasattr(character, "demeanor"):
                index = self.demeanor_combo.findText(character.demeanor)
                if index >= 0:
                    self.demeanor_combo.setCurrentIndex(index)
                    
            # Update notes
            if hasattr(character, "notes"):
                self.notes_edit.setText(character.notes)
                
            # Update traits
            self._load_larp_traits(character)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Error loading character: {str(e)}"
            )
    
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
        
        virtue_traits = {
            "Conscience": [],
            "Self-Control": [],
            "Courage": []
        }
        
        discipline_traits = []
        background_traits = []
        path_traits = []
        willpower_traits = []
        blood_traits = []
        
        # Process all LARP traits if available
        if hasattr(character, 'larp_traits') and character.larp_traits:
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
                    
                    # Handle virtues
                    elif category_name == "conscience":
                        virtue_traits["Conscience"].append(trait.display_name)
                    elif category_name == "self-control":
                        virtue_traits["Self-Control"].append(trait.display_name)
                    elif category_name == "courage":
                        virtue_traits["Courage"].append(trait.display_name)
                    
                    # Handle other types
                    elif category_name == "disciplines":
                        discipline_traits.append(trait.display_name)
                    elif category_name == "backgrounds":
                        background_traits.append(trait.display_name)
                    elif category_name == "path":
                        path_traits.append(trait.display_name)
                    elif category_name == "willpower":
                        willpower_traits.append(trait.display_name)
                    elif category_name == "blood":
                        blood_traits.append(trait.display_name)
        
        # Update widgets with collected traits
        self.attributes.set_category_traits(attribute_traits)
        self.abilities.set_category_traits(ability_traits)
        self.virtues.set_category_traits(virtue_traits)
        self.disciplines.set_traits(discipline_traits)
        self.backgrounds.set_traits(background_traits)
        self.path_traits.set_traits(path_traits)
        self.willpower.set_traits(willpower_traits)
        self.blood.set_traits(blood_traits)
        
    def save_character(self) -> None:
        """Save the current character."""
        if not self.character_id:
            return
            
        try:
            # Load character
            character = load_character(self.character_id)
            
            if not character:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to load character {self.character_id}"
                )
                return
                
            # Update basic info
            character.name = self.name_edit.text()
            character.player_name = self.player_edit.text()
            # TODO: Update chronicle
            
            if hasattr(character, "clan"):
                character.clan = self.clan_combo.currentText()
                
            if hasattr(character, "generation"):
                character.generation = self.generation_spin.value()
                
            if hasattr(character, "nature"):
                character.nature = self.nature_combo.currentText()
                
            if hasattr(character, "demeanor"):
                character.demeanor = self.demeanor_combo.currentText()
                
            # Update notes
            if hasattr(character, "notes"):
                character.notes = self.notes_edit.toPlainText()
                
            # Update traits
            # TODO: Implement trait saving
            
            # Save character
            character.save()
            
            # Emit change signal
            self.character_changed.emit()
            
            QMessageBox.information(
                self,
                "Save Success",
                "Character saved successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Error saving character: {str(e)}"
            )
        
    def get_character_data(self) -> Dict:
        """Get the character data from the sheet.
        
        Returns:
            Dictionary of character data
        """
        # Basic information
        data = {
            "name": self.name_edit.text(),
            "player_name": self.player_edit.text(),
            "narrator": self.storyteller.text(),  # Store as narrator in db
            "nature": self.nature_combo.currentText(),
            "demeanor": self.demeanor_combo.currentText(),
            "clan": self.clan_combo.currentText(),
            "generation": self.generation_spin.value(),
            "sect": self.sect.text(),
            "concept": self.concept.text(),
            "sire": self.sire.text(),
            "title": self.title.text(),
            
            # Chronicle information
            "chronicle_id": self.character.chronicle_id if hasattr(self.character, 'chronicle_id') else None,
            
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
            
        # Get virtues
        virtue_traits = self.virtues.get_category_traits()
        for subcategory, traits in virtue_traits.items():
            larp_traits[subcategory.lower()] = traits
        
        # Get other trait types
        larp_traits["disciplines"] = self.disciplines.get_traits()
        larp_traits["backgrounds"] = self.backgrounds.get_traits()
        larp_traits["path"] = self.path_traits.get_traits()
        larp_traits["willpower"] = self.willpower.get_traits()
        larp_traits["blood"] = self.blood.get_traits()
        
        return larp_traits 