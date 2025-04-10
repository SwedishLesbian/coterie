from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QTextEdit, QTabWidget, QScrollArea,
    QFrame, QGridLayout
)
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
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Main info tab
        main_info_tab = QWidget()
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
        
        main_info_tab.setLayout(main_info_layout)
        tab_widget.addTab(main_info_tab, "Character")
        
        # Notes tab
        notes_tab = QWidget()
        notes_layout = QVBoxLayout()
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter character notes here...")
        if self.character and self.character.notes:
            self.notes_edit.setPlainText(self.character.notes)
        self.notes_edit.textChanged.connect(self.on_notes_changed)
        
        notes_layout.addWidget(self.notes_edit)
        notes_tab.setLayout(notes_layout)
        tab_widget.addTab(notes_tab, "Notes")
        
        main_layout.addWidget(tab_widget)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_character)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
    def on_notes_changed(self):
        """Handle changes to the notes text."""
        if self.character:
            self.character.notes = self.notes_edit.toPlainText()
            
    def save_character(self):
        """Save the character to the database."""
        if not self.character:
            self.character = Character()
            self.session.add(self.character)
        
        # Save character data here
        self.character.notes = self.notes_edit.toPlainText()
        
        self.session.commit() 