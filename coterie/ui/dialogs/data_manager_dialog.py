"""Dialog for managing game data files."""

import json
import os
from typing import Optional, Dict, List, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QSplitter, QWidget, QTextEdit, QPushButton, 
    QMessageBox, QListWidgetItem, QLabel,
    QComboBox, QLineEdit, QInputDialog, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QSize

from coterie.utils.data_loader import DataLoader


class DataManagerDialog(QDialog):
    """Dialog for managing game data files."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the data manager dialog.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Data Manager")
        self.resize(900, 600)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Header label
        header = QLabel("Manage Game Data")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # Create splitter for file list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)  # 1 = stretch factor
        
        # Left panel for file list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self._on_file_selected)
        left_layout.addWidget(self.file_list)
        
        # Buttons for file operations
        file_buttons = QHBoxLayout()
        left_layout.addLayout(file_buttons)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_file_list)
        file_buttons.addWidget(self.refresh_button)
        
        file_buttons.addStretch()
        
        self.create_button = QPushButton("New File")
        self.create_button.clicked.connect(self._create_new_file)
        file_buttons.addWidget(self.create_button)
        
        # Right panel for editing
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Category selector
        self.category_selector = QComboBox()
        self.category_selector.currentTextChanged.connect(self._on_category_changed)
        right_layout.addWidget(self.category_selector)
        
        # Category editor
        self.editor = QTableWidget()
        self.editor.setColumnCount(2)
        self.editor.setHorizontalHeaderLabels(["Item", "Description"])
        self.editor.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.editor)
        
        # Editor buttons
        editor_buttons = QHBoxLayout()
        right_layout.addLayout(editor_buttons)
        
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self._add_item)
        editor_buttons.addWidget(self.add_item_button)
        
        self.add_category_button = QPushButton("Add Category")
        self.add_category_button.clicked.connect(self._add_category)
        editor_buttons.addWidget(self.add_category_button)
        
        editor_buttons.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_current_file)
        editor_buttons.addWidget(self.save_button)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 700])  # Default sizes
        
        # Bottom buttons
        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        
        buttons.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.close_button)
        
        # Current data
        self.current_file = ""
        self.current_data = {}
        
        # Load file list
        self._load_file_list()
        
    def _load_file_list(self) -> None:
        """Load the list of data files."""
        self.file_list.clear()
        
        # Get path to data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.join(base_dir, "data")
        
        # List JSON files
        for filename in sorted(os.listdir(data_dir)):
            if filename.endswith(".json"):
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, os.path.join(data_dir, filename))
                self.file_list.addItem(item)
                
    def _on_file_selected(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        """Handle file selection.
        
        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if not current:
            return
            
        # Check if there are unsaved changes
        if self.current_file and self._has_unsaved_changes():
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to {os.path.basename(self.current_file)}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if response == QMessageBox.StandardButton.Yes:
                self._save_current_file()
            elif response == QMessageBox.StandardButton.Cancel:
                # Reselect previous item
                self.file_list.setCurrentItem(previous)
                return
        
        # Load selected file
        file_path = current.data(Qt.ItemDataRole.UserRole)
        self._load_file(file_path)
        
    def _load_file(self, file_path: str) -> None:
        """Load a data file.
        
        Args:
            file_path: Path to the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_data = json.load(f)
            
            self.current_file = file_path
            
            # Update category selector
            self.category_selector.clear()
            
            # Add all categories
            for category in self.current_data.keys():
                if category != "descriptions" and isinstance(self.current_data[category], list):
                    self.category_selector.addItem(category)
                    
            # Select first category
            if self.category_selector.count() > 0:
                self.category_selector.setCurrentIndex(0)
                self._on_category_changed(self.category_selector.currentText())
            else:
                self.editor.setRowCount(0)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file: {str(e)}")
            
    def _on_category_changed(self, category: str) -> None:
        """Handle category selection.
        
        Args:
            category: Selected category
        """
        if not category or category not in self.current_data:
            self.editor.setRowCount(0)
            return
            
        # Get items in the category
        items = self.current_data[category]
        
        # Get descriptions
        descriptions = self.current_data.get("descriptions", {})
        
        # Update editor
        self.editor.setRowCount(len(items))
        
        for i, item in enumerate(items):
            # Skip if item is not a string (handles dictionaries or other non-string types)
            if not isinstance(item, str):
                continue
                
            # Item name
            name_item = QTableWidgetItem(item)
            self.editor.setItem(i, 0, name_item)
            
            # Description
            description = descriptions.get(item, "")
            desc_item = QTableWidgetItem(description)
            self.editor.setItem(i, 1, desc_item)
            
    def _save_current_file(self) -> None:
        """Save the current file."""
        if not self.current_file:
            return
            
        try:
            # Update current data from editor
            self._update_data_from_editor()
            
            # Save to file
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=4)
                
            # Clear data loader cache to reflect changes
            DataLoader.clear_cache()
            
            QMessageBox.information(self, "Success", "File saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")
            
    def _update_data_from_editor(self) -> None:
        """Update current data from editor."""
        # Get current category
        category = self.category_selector.currentText()
        if not category or category not in self.current_data:
            return
            
        # Create new category list
        items = []
        
        # Ensure descriptions exists
        if "descriptions" not in self.current_data:
            self.current_data["descriptions"] = {}
            
        # Get current descriptions
        descriptions = self.current_data["descriptions"]
        
        # Update from editor
        for row in range(self.editor.rowCount()):
            # Get item name
            name_item = self.editor.item(row, 0)
            if not name_item or not name_item.text().strip():
                continue
                
            item_name = name_item.text().strip()
            items.append(item_name)
            
            # Get description
            desc_item = self.editor.item(row, 1)
            if desc_item and desc_item.text().strip():
                descriptions[item_name] = desc_item.text().strip()
            elif item_name in descriptions:
                # Remove empty description
                descriptions.pop(item_name)
                
        # Update category
        self.current_data[category] = items
        
    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes.
        
        Returns:
            True if there are unsaved changes
        """
        if not self.current_file:
            return False
            
        # Get current category
        category = self.category_selector.currentText()
        if not category or category not in self.current_data:
            return False
            
        # Check if item count matches
        if len(self.current_data[category]) != self.editor.rowCount():
            return True
            
        # Get current descriptions
        descriptions = self.current_data.get("descriptions", {})
        
        # Check each item
        for row in range(self.editor.rowCount()):
            # Check item name
            name_item = self.editor.item(row, 0)
            if not name_item:
                continue
                
            item_name = name_item.text().strip()
            
            # Check if item is in original list
            if row >= len(self.current_data[category]) or self.current_data[category][row] != item_name:
                return True
                
            # Check description
            desc_item = self.editor.item(row, 1)
            desc = desc_item.text().strip() if desc_item else ""
            
            if desc != descriptions.get(item_name, ""):
                return True
                
        return False
        
    def _add_item(self) -> None:
        """Add a new item to the current category."""
        # Get current category
        category = self.category_selector.currentText()
        if not category or category not in self.current_data:
            return
            
        # Add new row
        row = self.editor.rowCount()
        self.editor.setRowCount(row + 1)
        
        # Set focus to the new item
        self.editor.setItem(row, 0, QTableWidgetItem("New Item"))
        self.editor.setItem(row, 1, QTableWidgetItem(""))
        self.editor.editItem(self.editor.item(row, 0))
        
    def _add_category(self) -> None:
        """Add a new category to the current file."""
        if not self.current_file:
            return
            
        # Get category name
        category, ok = QInputDialog.getText(
            self,
            "Add Category",
            "Enter category name:"
        )
        
        if not ok or not category.strip():
            return
            
        category = category.strip()
        
        # Check if category already exists
        if category in self.current_data:
            QMessageBox.warning(self, "Warning", f"Category '{category}' already exists.")
            return
            
        # Add category
        self.current_data[category] = []
        
        # Update category selector
        self.category_selector.addItem(category)
        self.category_selector.setCurrentText(category)
        
    def _create_new_file(self) -> None:
        """Create a new data file."""
        # Get file name
        file_name, ok = QInputDialog.getText(
            self,
            "New Data File",
            "Enter file name (without .json extension):"
        )
        
        if not ok or not file_name.strip():
            return
            
        file_name = file_name.strip()
        
        # Add extension if missing
        if not file_name.endswith(".json"):
            file_name += ".json"
            
        # Get data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.join(base_dir, "data")
        
        # Check if file already exists
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            QMessageBox.warning(self, "Warning", f"File '{file_name}' already exists.")
            return
            
        # Create empty file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"items": [], "descriptions": {}}, f, indent=4)
                
            # Reload file list
            self._load_file_list()
            
            # Select the new file
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if item.text() == file_name:
                    self.file_list.setCurrentItem(item)
                    break
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating file: {str(e)}")
    
    def accept(self) -> None:
        """Handle dialog acceptance."""
        # Check for unsaved changes
        if self.current_file and self._has_unsaved_changes():
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to {os.path.basename(self.current_file)}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if response == QMessageBox.StandardButton.Yes:
                self._save_current_file()
            elif response == QMessageBox.StandardButton.Cancel:
                return
                
        super().accept() 