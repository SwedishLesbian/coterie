"""Character sheet UI component."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QTextEdit, QTabWidget, QScrollArea,
    QFrame, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt
from typing import Optional
from sqlalchemy.orm import Session
from ..models.character import Character

class CharacterSheet(QWidget):
    def __init__(self, session: Session, character: Optional[Character] = None, parent=None):
        super().__init__(parent)
        self.session = session
        self.character = character
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the character sheet UI."""
        main_layout = QVBoxLayout()
        
        # Main info tab
        main_info_widget = QWidget()
        main_info_layout = QVBoxLayout()
        
        # Basic information section
        basic_info = QFrame()
        basic_info.setFrameStyle(QFrame.Shape.StyledPanel)
        basic_info_layout = QGridLayout()
        
        # Add basic info widgets here
        basic_info.setLayout(basic_info_layout)
        main_info_layout.addWidget(basic_info)
        
        # Traits section
        traits_frame = QFrame()
        traits_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        traits_layout = QVBoxLayout()
        
        # Add traits widgets here
        traits_frame.setLayout(traits_layout)
        main_info_layout.addWidget(traits_frame)
        
        # Notes section
        notes_frame = QFrame()
        notes_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        notes_layout = QVBoxLayout()
        
        # Notes header with format selector
        notes_header = QHBoxLayout()
        notes_label = QLabel("Character Notes")
        notes_header.addWidget(notes_label)
        
        self.notes_format = QComboBox()
        self.notes_format.addItems(["Plaintext", "Markdown", "HTML"])
        self.notes_format.currentTextChanged.connect(self.on_format_changed)
        notes_header.addWidget(self.notes_format)
        notes_header.addStretch()
        notes_layout.addLayout(notes_header)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter character notes here...")
        self.notes_edit.setMinimumHeight(150)  # Give reasonable default height
        if self.character and self.character.notes:
            self.notes_edit.setPlainText(self.character.notes)
        self.notes_edit.textChanged.connect(self.on_notes_changed)
        
        # Set default to accept plaintext
        self.notes_edit.setAcceptRichText(False)
        
        notes_layout.addWidget(self.notes_edit)
        notes_frame.setLayout(notes_layout)
        main_info_layout.addWidget(notes_frame)
        
        main_info_widget.setLayout(main_info_layout)
        
        # Add main info widget to a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(main_info_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_character)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
    def on_format_changed(self, format_name: str):
        """Handle changes to the notes format."""
        # Store current text
        current_text = self.notes_edit.toPlainText()
        
        # Update editor settings based on format
        if format_name == "HTML":
            self.notes_edit.setAcceptRichText(True)
            self.notes_edit.setPlaceholderText("Enter character notes here using HTML...")
        else:
            self.notes_edit.setAcceptRichText(False)
            placeholder = "Enter character notes here..."
            if format_name == "Markdown":
                placeholder += " using Markdown formatting..."
            self.notes_edit.setPlaceholderText(placeholder)
        
        # Restore text
        self.notes_edit.setPlainText(current_text)
        
    def on_notes_changed(self):
        """Handle changes to the notes text."""
        if self.character:
            if self.notes_format.currentText() == "HTML":
                self.character.notes = self.notes_edit.toHtml()
            else:
                self.character.notes = self.notes_edit.toPlainText()
            
    def save_character(self):
        """Save the character to the database."""
        if not self.character:
            self.character = Character()
            self.session.add(self.character)
        
        # Save character data here
        if self.notes_format.currentText() == "HTML":
            self.character.notes = self.notes_edit.toHtml()
        else:
            self.character.notes = self.notes_edit.toPlainText()
        
        self.session.commit() 