from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

from ...models.menu import MenuItem

class TraitConflictDialog(QDialog):
    """Dialog for resolving conflicts between similar traits during import."""
    
    def __init__(self, new_trait: MenuItem, existing_trait: MenuItem, parent=None):
        """
        Initialize the trait conflict resolution dialog.
        
        Args:
            new_trait: The new trait being imported
            existing_trait: The existing similar trait
            parent: Parent widget
        """
        super().__init__(parent)
        self.new_trait = new_trait
        self.existing_trait = existing_trait
        self.selected_trait = None
        
        self.setWindowTitle("Resolve Trait Conflict")
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout()
        
        # Explanation
        layout.addWidget(QLabel("Similar traits found. Please choose how to resolve:"))
        
        # Existing trait info
        existing_group = QGroupBox("Existing Trait")
        existing_layout = QVBoxLayout()
        existing_layout.addWidget(QLabel(f"Name: {self.existing_trait.name}"))
        if self.existing_trait.cost is not None:
            existing_layout.addWidget(QLabel(f"Cost: {self.existing_trait.cost}"))
        if self.existing_trait.note:
            existing_layout.addWidget(QLabel(f"Note: {self.existing_trait.note}"))
        if self.existing_trait.category:
            existing_layout.addWidget(QLabel(f"Category: {self.existing_trait.category.name}"))
        existing_group.setLayout(existing_layout)
        layout.addWidget(existing_group)
        
        # New trait info
        new_group = QGroupBox("New Trait")
        new_layout = QVBoxLayout()
        new_layout.addWidget(QLabel(f"Name: {self.new_trait.name}"))
        if self.new_trait.cost is not None:
            new_layout.addWidget(QLabel(f"Cost: {self.new_trait.cost}"))
        if self.new_trait.note:
            new_layout.addWidget(QLabel(f"Note: {self.new_trait.note}"))
        if self.new_trait.category:
            new_layout.addWidget(QLabel(f"Category: {self.new_trait.category.name}"))
        new_group.setLayout(new_layout)
        layout.addWidget(new_group)
        
        # Options
        self.keep_existing = QRadioButton("Keep existing trait")
        self.keep_existing.setChecked(True)
        self.use_new = QRadioButton("Use new trait")
        self.keep_both = QRadioButton("Keep both traits")
        
        layout.addWidget(self.keep_existing)
        layout.addWidget(self.use_new)
        layout.addWidget(self.keep_both)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.handle_selection)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def handle_selection(self):
        """Handle the user's selection."""
        if self.keep_existing.isChecked():
            self.selected_trait = self.existing_trait
        elif self.use_new.isChecked():
            self.selected_trait = self.new_trait
        else:  # keep both
            self.selected_trait = None
        self.accept()
    
    @classmethod
    def resolve_conflict(cls, new_trait: MenuItem, existing_trait: MenuItem, parent=None) -> Optional[MenuItem]:
        """
        Show the dialog and return the selected resolution.
        
        Args:
            new_trait: The new trait being imported
            existing_trait: The existing similar trait
            parent: Parent widget
            
        Returns:
            Selected MenuItem or None to keep both
        """
        dialog = cls(new_trait, existing_trait, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selected_trait
        return existing_trait  # Default to existing on cancel 