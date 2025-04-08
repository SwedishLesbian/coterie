"""Dialog for importing data from the original Grapevine application."""

import os
import json
import re
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QCheckBox, QComboBox, QProgressBar,
    QTabWidget, QWidget, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from coterie.utils.data_loader import DataLoader

class ImportDialog(QDialog):
    """Dialog for importing data from the original Grapevine application."""
    
    import_completed = pyqtSignal(bool)  # Success flag
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the import dialog.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Import from Grapevine")
        self.resize(800, 600)
        self.setModal(True)
        
        # Set up layout
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Import data from Grapevine 3.x")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)
        
        description_label = QLabel(
            "This tool allows you to import data from Grapevine 3.x into Coterie. "
            "You can select which types of data to import."
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create tabs
        self._create_character_tab(tab_widget)
        self._create_game_data_tab(tab_widget)
        self._create_chronicle_tab(tab_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self._import_data)
        button_layout.addWidget(self.import_button)
        
        # Data storage
        self.grapevine_path = ""
        self.selected_files = []
        
    def _create_character_tab(self, parent: QTabWidget) -> None:
        """Create the character import tab.
        
        Args:
            parent: Parent tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grapevine path selection
        path_group = QGroupBox("Grapevine Installation")
        path_layout = QVBoxLayout(path_group)
        layout.addWidget(path_group)
        
        path_desc = QLabel(
            "Select the folder containing your Grapevine installation. "
            "This should be the folder containing Grapevine.exe and the Characters folder."
        )
        path_desc.setWordWrap(True)
        path_layout.addWidget(path_desc)
        
        path_button_layout = QHBoxLayout()
        path_layout.addLayout(path_button_layout)
        
        self.path_label = QLabel("No folder selected")
        path_button_layout.addWidget(self.path_label)
        
        path_button_layout.addStretch()
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_grapevine_path)
        path_button_layout.addWidget(self.browse_button)
        
        # Character selection
        character_group = QGroupBox("Characters")
        character_layout = QVBoxLayout(character_group)
        layout.addWidget(character_group)
        
        character_desc = QLabel(
            "Select the characters you want to import. "
            "Only characters from the selected Grapevine installation will be shown."
        )
        character_desc.setWordWrap(True)
        character_layout.addWidget(character_desc)
        
        self.character_tree = QTreeWidget()
        self.character_tree.setHeaderLabels(["Name", "Type", "Player"])
        self.character_tree.setAlternatingRowColors(True)
        character_layout.addWidget(self.character_tree)
        
        # Character options
        options_layout = QHBoxLayout()
        character_layout.addLayout(options_layout)
        
        self.select_all_check = QCheckBox("Select All")
        self.select_all_check.stateChanged.connect(self._toggle_select_all)
        options_layout.addWidget(self.select_all_check)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Types", "Vampire", "Werewolf", "Mage", "Other"])
        self.filter_combo.currentTextChanged.connect(self._filter_characters)
        options_layout.addWidget(self.filter_combo)
        
        # Add tab
        parent.addTab(tab, "Characters")
        
    def _create_game_data_tab(self, parent: QTabWidget) -> None:
        """Create the game data import tab.
        
        Args:
            parent: Parent tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Game data description
        desc_label = QLabel(
            "Import game data from Grapevine, such as traits, disciplines, backgrounds, etc. "
            "This will merge with existing data in Coterie."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Data types
        data_group = QGroupBox("Data Types")
        data_layout = QVBoxLayout(data_group)
        layout.addWidget(data_group)
        
        self.traits_check = QCheckBox("Traits (Attributes, Abilities, etc.)")
        self.traits_check.setChecked(True)
        data_layout.addWidget(self.traits_check)
        
        self.disciplines_check = QCheckBox("Disciplines and Paths")
        self.disciplines_check.setChecked(True)
        data_layout.addWidget(self.disciplines_check)
        
        self.backgrounds_check = QCheckBox("Backgrounds")
        self.backgrounds_check.setChecked(True)
        data_layout.addWidget(self.backgrounds_check)
        
        self.merits_flaws_check = QCheckBox("Merits and Flaws")
        self.merits_flaws_check.setChecked(True)
        data_layout.addWidget(self.merits_flaws_check)
        
        self.natures_check = QCheckBox("Natures and Demeanors")
        self.natures_check.setChecked(True)
        data_layout.addWidget(self.natures_check)
        
        # Add tab
        parent.addTab(tab, "Game Data")
        
    def _create_chronicle_tab(self, parent: QTabWidget) -> None:
        """Create the chronicle import tab.
        
        Args:
            parent: Parent tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Chronicle description
        desc_label = QLabel(
            "Import chronicles, plots, and rumors from Grapevine. "
            "This feature is not yet implemented."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Add tab
        parent.addTab(tab, "Chronicle")
        
    def _browse_grapevine_path(self) -> None:
        """Browse for Grapevine installation folder."""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Grapevine Installation Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder:
            return
            
        # Check if this is a valid Grapevine installation
        characters_folder = os.path.join(folder, "Characters")
        
        if not os.path.exists(characters_folder) or not os.path.isdir(characters_folder):
            QMessageBox.warning(
                self,
                "Invalid Folder",
                "The selected folder does not appear to be a valid Grapevine installation. "
                "Please select a folder containing a 'Characters' subfolder."
            )
            return
            
        # Save path and update UI
        self.grapevine_path = folder
        self.path_label.setText(folder)
        
        # Load characters
        self._load_characters()
        
    def _load_characters(self) -> None:
        """Load characters from Grapevine installation."""
        if not self.grapevine_path:
            return
            
        # Clear tree
        self.character_tree.clear()
        
        characters_folder = os.path.join(self.grapevine_path, "Characters")
        
        # Get character files
        character_files = []
        for root, _, files in os.walk(characters_folder):
            for file in files:
                if file.lower().endswith(".gvc"):
                    character_files.append(os.path.join(root, file))
                    
        # Populate tree
        for file_path in character_files:
            # Try to extract basic info from file name
            file_name = os.path.basename(file_path)
            name_match = re.match(r"(.+)\.gvc", file_name, re.IGNORECASE)
            
            if name_match:
                name = name_match.group(1)
                
                # Guess character type from containing folder
                char_type = "Unknown"
                parent_folder = os.path.basename(os.path.dirname(file_path))
                
                if parent_folder.lower() == "vampire":
                    char_type = "Vampire"
                elif parent_folder.lower() == "werewolf":
                    char_type = "Werewolf"
                elif parent_folder.lower() == "mage":
                    char_type = "Mage"
                elif parent_folder.lower() == "wraith":
                    char_type = "Wraith"
                elif parent_folder.lower() == "changeling":
                    char_type = "Changeling"
                elif parent_folder.lower() == "hunter":
                    char_type = "Hunter"
                elif parent_folder.lower() == "demon":
                    char_type = "Demon"
                elif parent_folder.lower() == "mummy":
                    char_type = "Mummy"
                elif parent_folder.lower() == "mortal":
                    char_type = "Mortal"
                
                # Create tree item
                item = QTreeWidgetItem([name, char_type, "Unknown"])
                item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                
                self.character_tree.addTopLevelItem(item)
                
        # Update columns
        for i in range(3):
            self.character_tree.resizeColumnToContents(i)
            
    def _toggle_select_all(self, state: int) -> None:
        """Toggle selection of all characters.
        
        Args:
            state: Check state
        """
        check_state = Qt.CheckState.Checked if state == Qt.CheckState.Checked.value else Qt.CheckState.Unchecked
        
        for i in range(self.character_tree.topLevelItemCount()):
            item = self.character_tree.topLevelItem(i)
            
            # Skip if filtered out
            if not item.isHidden():
                item.setCheckState(0, check_state)
                
    def _filter_characters(self, filter_text: str) -> None:
        """Filter characters by type.
        
        Args:
            filter_text: Filter text
        """
        for i in range(self.character_tree.topLevelItemCount()):
            item = self.character_tree.topLevelItem(i)
            char_type = item.text(1)
            
            if filter_text == "All Types" or char_type == filter_text:
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def _get_selected_characters(self) -> List[str]:
        """Get paths of selected character files.
        
        Returns:
            List of file paths
        """
        selected = []
        
        for i in range(self.character_tree.topLevelItemCount()):
            item = self.character_tree.topLevelItem(i)
            
            if item.checkState(0) == Qt.CheckState.Checked:
                file_path = item.data(0, Qt.ItemDataRole.UserRole)
                selected.append(file_path)
                
        return selected
        
    def _import_data(self) -> None:
        """Import selected data."""
        # Check if Grapevine path is set
        if not self.grapevine_path:
            QMessageBox.warning(
                self,
                "No Grapevine Installation",
                "Please select a Grapevine installation folder first."
            )
            return
            
        # Get selected characters
        selected_characters = self._get_selected_characters()
        
        # Get selected data types
        import_traits = self.traits_check.isChecked()
        import_disciplines = self.disciplines_check.isChecked()
        import_backgrounds = self.backgrounds_check.isChecked()
        import_merits_flaws = self.merits_flaws_check.isChecked()
        import_natures = self.natures_check.isChecked()
        
        # Check if anything is selected
        if not (selected_characters or 
                import_traits or 
                import_disciplines or 
                import_backgrounds or 
                import_merits_flaws or 
                import_natures):
            QMessageBox.warning(
                self,
                "Nothing Selected",
                "Please select at least one character or data type to import."
            )
            return
            
        # Confirm import
        confirm = QMessageBox.question(
            self,
            "Confirm Import",
            "Are you sure you want to import the selected data? "
            "This will merge with existing data in Coterie.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # TODO: Implement actual import logic
        # For now, just show a message
        QMessageBox.information(
            self,
            "Import Not Implemented",
            "The import functionality is not yet fully implemented. "
            "This is a placeholder for future development."
        )
        
        # Hide progress
        self.progress_bar.setVisible(False)
        
        # Emit completion signal
        self.import_completed.emit(True) 