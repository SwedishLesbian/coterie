"""Dialog for managing game data."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QMessageBox,
    QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal

from coterie.utils.data_loader import (
    load_data, get_category, get_descriptions,
    get_item_description, clear_cache, load_json_file
)

class DataManagerDialog(QDialog):
    """Dialog for managing game data."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Data Manager")
        self.setModal(True)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add list widget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_data)
        button_layout.addWidget(self.import_button)
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_data)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        # Load data
        self.refresh_list()
    
    def refresh_list(self) -> None:
        """Refresh the list of data files."""
        self.list_widget.clear()
        
        # Get data directory
        data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'data'
        
        if not data_dir.exists():
            return
            
        # Add all JSON files
        for file_path in data_dir.glob('*.json'):
            self.list_widget.addItem(file_path.name)
    
    def import_data(self) -> None:
        """Import data from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Data",
            "",
            "JSON files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            # Load the data
            data = load_json_file(file_path)
            
            if not data:
                QMessageBox.warning(
                    self,
                    "Import Error",
                    "Failed to load data from file."
                )
                return
                
            # Get target path
            file_name = os.path.basename(file_path)
            data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'data'
            target_path = data_dir / file_name
            
            # Create data directory if needed
            data_dir.mkdir(exist_ok=True)
            
            # Save the data
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            # Refresh list and notify
            self.refresh_list()
            self.data_changed.emit()
            
            QMessageBox.information(
                self,
                "Import Success",
                "Data imported successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import data: {str(e)}"
            )
    
    def export_data(self) -> None:
        """Export data to a file."""
        current_item = self.list_widget.currentItem()
        
        if not current_item:
            QMessageBox.warning(
                self,
                "Export Error",
                "Please select a data file to export."
            )
            return
            
        file_name = current_item.text()
        
        try:
            # Load the data
            data = load_data(file_name)
            
            # Get export path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Data",
                file_name,
                "JSON files (*.json)"
            )
            
            if not file_path:
                return
                
            # Save the data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            QMessageBox.information(
                self,
                "Export Success",
                "Data exported successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export data: {str(e)}"
            )
    
    def delete_data(self) -> None:
        """Delete a data file."""
        current_item = self.list_widget.currentItem()
        
        if not current_item:
            QMessageBox.warning(
                self,
                "Delete Error",
                "Please select a data file to delete."
            )
            return
            
        file_name = current_item.text()
        
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {file_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result != QMessageBox.StandardButton.Yes:
            return
            
        try:
            # Get file path
            data_dir = Path(__file__).resolve().parent.parent.parent.parent / 'data'
            file_path = data_dir / file_name
            
            # Delete file
            file_path.unlink()
            
            # Clear cache and refresh
            clear_cache()
            self.refresh_list()
            self.data_changed.emit()
            
            QMessageBox.information(
                self,
                "Delete Success",
                "Data file deleted successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Delete Error",
                f"Failed to delete data file: {str(e)}"
            ) 