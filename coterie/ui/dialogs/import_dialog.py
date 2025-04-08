"""Dialog for importing data from the original Grapevine application."""

import os
import json
import re
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QCheckBox, QComboBox, QProgressBar,
    QTabWidget, QWidget, QGroupBox, QFormLayout,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication

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
        header_label = QLabel("Import data from Grapevine")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)
        
        description_label = QLabel(
            "This tool allows you to import data from Grapevine into Coterie. "
            "You can import from Grapevine 3.x (.gvc) files or exported character (.gex) files."
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
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
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
        self.gvc_files = []
        self.gex_files = []
        self.import_mode = "gvc"  # Default mode
        
    def _create_character_tab(self, parent: QTabWidget) -> None:
        """Create the character import tab.
        
        Args:
            parent: Parent tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Import mode selection
        mode_group = QGroupBox("Import Mode")
        mode_layout = QVBoxLayout(mode_group)
        layout.addWidget(mode_group)
        
        self.mode_buttons = QButtonGroup()
        
        self.gvc_radio = QRadioButton("Import Grapevine 3.x Character Files (.gvc)")
        self.gvc_radio.setChecked(True)
        self.gvc_radio.toggled.connect(lambda checked: self._toggle_import_mode("gvc" if checked else "gex"))
        self.mode_buttons.addButton(self.gvc_radio)
        mode_layout.addWidget(self.gvc_radio)
        
        self.gex_radio = QRadioButton("Import Grapevine Exported Character Files (.gex)")
        self.mode_buttons.addButton(self.gex_radio)
        mode_layout.addWidget(self.gex_radio)
        
        # GVC files selection
        self.gvc_group = QGroupBox("GVC Files")
        self.gvc_layout = QVBoxLayout(self.gvc_group)
        layout.addWidget(self.gvc_group)
        
        gvc_desc = QLabel(
            "Select .gvc files to import. These are Grapevine 3.x character files."
        )
        gvc_desc.setWordWrap(True)
        self.gvc_layout.addWidget(gvc_desc)
        
        gvc_button_layout = QHBoxLayout()
        self.gvc_layout.addLayout(gvc_button_layout)
        
        self.gvc_files_label = QLabel("No files selected")
        gvc_button_layout.addWidget(self.gvc_files_label)
        
        gvc_button_layout.addStretch()
        
        self.gvc_browse_button = QPushButton("Browse...")
        self.gvc_browse_button.clicked.connect(self._browse_gvc_files)
        gvc_button_layout.addWidget(self.gvc_browse_button)
        
        # GEX files selection
        self.gex_group = QGroupBox("GEX Files")
        self.gex_layout = QVBoxLayout(self.gex_group)
        layout.addWidget(self.gex_group)
        self.gex_group.setVisible(False)
        
        gex_desc = QLabel(
            "Select .gex files to import. These are Grapevine exported character files, "
            "which are in XML format and contain complete character information."
        )
        gex_desc.setWordWrap(True)
        self.gex_layout.addWidget(gex_desc)
        
        gex_button_layout = QHBoxLayout()
        self.gex_layout.addLayout(gex_button_layout)
        
        self.gex_files_label = QLabel("No files selected")
        gex_button_layout.addWidget(self.gex_files_label)
        
        gex_button_layout.addStretch()
        
        self.gex_browse_button = QPushButton("Browse...")
        self.gex_browse_button.clicked.connect(self._browse_gex_files)
        gex_button_layout.addWidget(self.gex_browse_button)
        
        # Character selection tree (shared between modes)
        character_group = QGroupBox("Characters")
        character_layout = QVBoxLayout(character_group)
        layout.addWidget(character_group)
        
        character_desc = QLabel(
            "Select the characters you want to import."
        )
        character_desc.setWordWrap(True)
        character_layout.addWidget(character_desc)
        
        self.character_tree = QTreeWidget()
        self.character_tree.setHeaderLabels(["Name", "Type", "Player", "Format"])
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
        
    def _toggle_import_mode(self, mode: str) -> None:
        """Toggle between GVC and GEX import modes.
        
        Args:
            mode: Import mode ("gvc" or "gex")
        """
        self.import_mode = mode
        
        # Toggle visibility of the appropriate groups
        self.gvc_group.setVisible(mode == "gvc")
        self.gex_group.setVisible(mode == "gex")
        
        # Clear the character tree
        self.character_tree.clear()
        
    def _browse_gvc_files(self) -> None:
        """Browse for .gvc files to import."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Grapevine Character Files",
            "",
            "Grapevine Character Files (*.gvc)"
        )
        
        if not files:
            return
            
        # Update UI
        self.gvc_files_label.setText(f"{len(files)} files selected")
        
        # Store selected files
        self.gvc_files = files
        
        # Load characters from these files
        self._load_characters_from_gvc()
        
    def _browse_gex_files(self) -> None:
        """Browse for .gex files to import."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Grapevine Export Files",
            "",
            "Grapevine Export Files (*.gex)"
        )
        
        if not files:
            return
            
        # Update UI
        self.gex_files_label.setText(f"{len(files)} files selected")
        
        # Store selected files
        self.gex_files = files
        
        # Load characters from these files
        self._load_characters_from_gex()
        
    def _load_characters_from_gvc(self) -> None:
        """Load characters from selected .gvc files."""
        if not self.gvc_files:
            return
            
        # Clear tree
        self.character_tree.clear()
        
        # Populate tree
        for file_path in self.gvc_files:
            # Try to extract basic info
            try:
                character_data, format_type = DataLoader.extract_character_info(file_path)
                
                # Create tree item
                item = QTreeWidgetItem([
                    character_data.get("name", "Unknown"),
                    character_data.get("type", "Unknown"),
                    character_data.get("player", "Unknown"),
                    "GV3 (.gvc)"
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                
                self.character_tree.addTopLevelItem(item)
                
            except Exception as e:
                print(f"Error loading character from {file_path}: {str(e)}")
                
        # Update columns
        for i in range(4):
            self.character_tree.resizeColumnToContents(i)
            
    def _load_characters_from_gex(self) -> None:
        """Load characters from selected .gex files."""
        if not self.gex_files:
            return
            
        # Clear tree
        self.character_tree.clear()
        
        # Populate tree
        for file_path in self.gex_files:
            try:
                character_data, format_type = DataLoader.extract_character_info(file_path)
                
                # Create tree item
                item = QTreeWidgetItem([
                    character_data.get("name", "Unknown"),
                    character_data.get("type", "Unknown"),
                    character_data.get("player", "Unknown"),
                    "GEX (.gex)"
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                
                self.character_tree.addTopLevelItem(item)
                
            except Exception as e:
                print(f"Error loading character from {file_path}: {str(e)}")
                
        # Update columns
        for i in range(4):
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
        # Check if data source is set
        if self.import_mode == "gvc" and not self.gvc_files:
            QMessageBox.warning(
                self,
                "No GVC Files",
                "Please select at least one .gvc file to import."
            )
            return
        elif self.import_mode == "gex" and not self.gex_files:
            QMessageBox.warning(
                self,
                "No GEX Files",
                "Please select at least one .gex file to import."
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
        self.progress_bar.setRange(0, len(selected_characters))
        self.progress_bar.setValue(0)
        
        imported_files = []
        
        # Import selected characters
        for i, file_path in enumerate(selected_characters):
            try:
                # Update progress
                self.progress_bar.setValue(i + 1)
                self.status_label.setText(f"Importing {os.path.basename(file_path)}...")
                QApplication.processEvents()  # Allow GUI updates
                
                # Import character
                imported_file = self._import_character_with_larp_traits(file_path)
                imported_files.append(imported_file)
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Import Error",
                    f"Error importing {os.path.basename(file_path)}: {str(e)}"
                )
        
        # Import game data if selected
        if (import_traits or import_disciplines or import_backgrounds or 
            import_merits_flaws or import_natures):
            # TODO: Implement game data import
            pass
                
        # Hide progress and status message
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        
        # Show success message
        if imported_files:
            QMessageBox.information(
                self,
                "Import Complete",
                f"Successfully imported {len(imported_files)} characters."
            )
            
            # Emit completion signal
            self.import_completed.emit(True)
        else:
            QMessageBox.warning(
                self,
                "Import Warning",
                "No characters were imported."
            )
            
            # Emit completion signal with failure
            self.import_completed.emit(False)
    
    def _import_character_with_larp_traits(self, file_path: str) -> str:
        """Import a character file with proper LARP trait handling.
        
        Args:
            file_path: Path to the character file
            
        Returns:
            The imported file path
        
        Raises:
            Exception: If there was an error during import
        """
        # Import based on file type
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == ".gvc":
            # Update status
            self.status_label.setText(f"Reading GVC data from {os.path.basename(file_path)}...")
            QApplication.processEvents()  # Allow GUI updates
            
            # Import .gvc file
            character_data = DataLoader.load_grapevine_character(file_path)
            
            # Extract LARP traits
            self.status_label.setText("Converting dot ratings to LARP trait adjectives...")
            QApplication.processEvents()  # Allow GUI updates
            
            # Ensure larp_traits are in the character data
            if 'larp_traits' not in character_data:
                # Convert traditional traits to LARP traits if needed
                character_data['larp_traits'] = DataLoader._extract_grapevine_larp_traits(
                    DataLoader._extract_raw_grapevine_data(file_path)
                )
            
        elif file_extension == ".gex":
            # Update status
            self.status_label.setText(f"Parsing XML data from {os.path.basename(file_path)}...")
            QApplication.processEvents()  # Allow GUI updates
            
            # Import .gex file
            character_data = DataLoader.load_grapevine_xml_character(file_path)
            
            # Extract LARP traits
            self.status_label.setText("Converting traits to LARP format...")
            QApplication.processEvents()  # Allow GUI updates
            
            # Ensure larp_traits are in the character data
            if 'larp_traits' not in character_data:
                # Get raw XML data
                raw_data = DataLoader._extract_raw_grapevine_xml_data(file_path)
                # Convert traditional traits to LARP traits
                character_data['larp_traits'] = DataLoader._extract_xml_larp_traits(raw_data)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Save the character to the database
        self.status_label.setText("Saving character to database...")
        QApplication.processEvents()  # Allow GUI updates
        
        # Create and save the character
        vampire = DataLoader.create_vampire_from_dict(character_data)
        
        # Update status
        self.status_label.setText(f"Successfully imported {vampire.name}")
        
        return file_path 