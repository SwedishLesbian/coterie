"""Dialog for importing character data."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt

from coterie.utils.data_loader import (
    load_grapevine_file, create_vampire_from_dict,
    extract_character_info, import_character
)

class ImportDialog(QDialog):
    """Dialog for importing character data."""
    
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Import Character")
        self.setModal(True)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add label
        label = QLabel("Select a character file to import:")
        layout.addWidget(label)
        
        # Add file selection button
        button_layout = QHBoxLayout()
        
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.file_button)
        
        self.file_label = QLabel("")
        button_layout.addWidget(self.file_label)
        
        layout.addLayout(button_layout)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Add import button
        self.import_button = QPushButton("Import")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_file)
        layout.addWidget(self.import_button)
        
        self.setLayout(layout)
        
        # Store selected file
        self.selected_file = ""
    
    def select_file(self) -> None:
        """Open file dialog to select a character file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Character File",
            "",
            "Character Files (*.gvc *.gex);;All Files (*.*)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.import_button.setEnabled(True)
    
    def import_file(self) -> None:
        """Import the selected character file."""
        if not self.selected_file:
            return
            
        try:
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Extract character info
            self.progress_bar.setValue(25)
            character_data, format_type = extract_character_info(self.selected_file)
            
            # Import character file
            self.progress_bar.setValue(50)
            target_dir = str(Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'characters')
            imported_file = import_character(self.selected_file, target_dir)
            
            # Load character data
            self.progress_bar.setValue(75)
            data = load_grapevine_file(imported_file)
            
            # Create character object
            self.progress_bar.setValue(90)
            character = create_vampire_from_dict(data)
            
            # Complete
            self.progress_bar.setValue(100)
            
            QMessageBox.information(
                self,
                "Import Success",
                f"Character '{character.name}' imported successfully."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import character: {str(e)}"
            )
            
        finally:
            self.progress_bar.setVisible(False) 