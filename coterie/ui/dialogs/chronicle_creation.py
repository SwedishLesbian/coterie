"""Dialog for creating new chronicles."""

from typing import Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QPushButton, 
    QDialogButtonBox, QLabel, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt

class ChronicleCreationDialog(QDialog):
    """Dialog for creating a new chronicle."""
    
    chronicle_created = pyqtSignal(dict) # Signal emitted when a chronicle is created
    
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """Initialize the chronicle creation dialog.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Create a New Chronicle")
        self.setMinimumWidth(500)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("Create a New Chronicle")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.layout.addWidget(title_label)
        
        description_label = QLabel(
            "A Chronicle is a campaign setting for your game. "
            "All characters, plots, and other elements will be organized within Chronicles."
        )
        description_label.setWordWrap(True)
        self.layout.addWidget(description_label)
        
        # Form for chronicle information
        form_layout = QFormLayout()
        self.layout.addLayout(form_layout)
        
        # Chronicle name
        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter a name for your chronicle")
        form_layout.addRow("Name:", self.name)
        
        # Chronicle HST (renamed from narrator)
        self.narrator = QLineEdit()
        self.narrator.setPlaceholderText("Enter the HST's name")
        form_layout.addRow("HST:", self.narrator)
        
        # Chronicle description
        self.description = QTextEdit()
        self.description.setPlaceholderText("Enter a description for your chronicle")
        self.description.setMinimumHeight(100)
        form_layout.addRow("Description:", self.description)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Create button
        self.create_button = QPushButton("Create Chronicle")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self._create_chronicle)
        button_layout.addWidget(self.create_button)
        
        # Connect signal to enable/disable create button
        self.name.textChanged.connect(self._validate_inputs)
        self.narrator.textChanged.connect(self._validate_inputs)
        
        # Initial validation
        self._validate_inputs()
        
    def _validate_inputs(self) -> None:
        """Enable the create button only if name and narrator are not empty."""
        self.create_button.setEnabled(
            bool(self.name.text().strip()) and 
            bool(self.narrator.text().strip())
        )
        
    def _create_chronicle(self) -> None:
        """Create a chronicle from the form data and emit the chronicle_created signal."""
        # Get form data
        data = {
            "name": self.name.text().strip(),
            "narrator": self.narrator.text().strip(),
            "description": self.description.toPlainText().strip(),
            "start_date": datetime.now(),
            "last_modified": datetime.now(),
            "is_active": True
        }
        
        # Emit the signal
        self.chronicle_created.emit(data)
        
        # Close the dialog
        self.accept() 