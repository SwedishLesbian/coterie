"""Main application window for Coterie.

This module implements the main window interface, providing access to character management,
chronicle tools, and other core functionality.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QMenuBar, QStatusBar, QToolBar,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from coterie.database.engine import get_session
from coterie.models.vampire import Vampire
from coterie.ui.dialogs.character_creation import CharacterCreationDialog

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window providing access to all Coterie functionality."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the main window.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Coterie 4.0")
        self.setMinimumSize(1024, 768)
        
        # Create the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create UI components
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_main_interface()
        
        # Connect signals
        self.new_char_action.triggered.connect(self._on_new_character)
        
    def _create_menu_bar(self) -> None:
        """Create and populate the main menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        self.new_char_action = QAction("&New Character", self)
        self.new_char_action.setShortcut("Ctrl+N")
        file_menu.addAction(self.new_char_action)
        
        self.open_char_action = QAction("&Open Character", self)
        self.open_char_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.open_char_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Alt+F4")
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Chronicle menu
        chronicle_menu = menubar.addMenu("&Chronicle")
        
        self.new_chronicle_action = QAction("New &Chronicle", self)
        chronicle_menu.addAction(self.new_chronicle_action)
        
        self.open_chronicle_action = QAction("&Open Chronicle", self)
        chronicle_menu.addAction(self.open_chronicle_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        self.experience_action = QAction("&Experience Points", self)
        tools_menu.addAction(self.experience_action)
        
        self.plots_action = QAction("&Plots", self)
        tools_menu.addAction(self.plots_action)
        
        self.rumors_action = QAction("&Rumors", self)
        tools_menu.addAction(self.rumors_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        self.about_action = QAction("&About", self)
        help_menu.addAction(self.about_action)
        
    def _create_tool_bar(self) -> None:
        """Create and populate the main toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add quick access buttons
        new_char = QPushButton("New Character")
        new_char.clicked.connect(self._on_new_character)
        toolbar.addWidget(new_char)
        
        open_char = QPushButton("Open Character")
        toolbar.addWidget(open_char)
        
        experience = QPushButton("Experience")
        toolbar.addWidget(experience)
        
    def _create_status_bar(self) -> None:
        """Create and configure the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def _create_main_interface(self) -> None:
        """Create the main interface with tabs for different views."""
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Characters tab
        self.characters_widget = QWidget()
        self.characters_layout = QVBoxLayout(self.characters_widget)
        self.characters_label = QLabel("No characters loaded")
        self.characters_layout.addWidget(self.characters_label)
        self.tabs.addTab(self.characters_widget, "Characters")
        
        # Chronicle tab
        self.chronicle_widget = QWidget()
        self.chronicle_layout = QVBoxLayout(self.chronicle_widget)
        self.chronicle_label = QLabel("No chronicle loaded")
        self.chronicle_layout.addWidget(self.chronicle_label)
        self.tabs.addTab(self.chronicle_widget, "Chronicle")
        
        # Plots tab
        self.plots_widget = QWidget()
        self.plots_layout = QVBoxLayout(self.plots_widget)
        self.plots_label = QLabel("No plots available")
        self.plots_layout.addWidget(self.plots_label)
        self.tabs.addTab(self.plots_widget, "Plots")
        
        # Rumors tab
        self.rumors_widget = QWidget()
        self.rumors_layout = QVBoxLayout(self.rumors_widget)
        self.rumors_label = QLabel("No rumors available")
        self.rumors_layout.addWidget(self.rumors_label)
        self.tabs.addTab(self.rumors_widget, "Rumors")
        
    def _on_new_character(self) -> None:
        """Handle new character creation."""
        dialog = CharacterCreationDialog(self)
        dialog.character_created.connect(self._create_character)
        dialog.exec()
        
    def _create_character(self, data: Dict[str, Any]) -> None:
        """Create a new character from the dialog data.
        
        Args:
            data: Dictionary containing character data
        """
        try:
            session = get_session()
            
            if data["type"].startswith("Vampire"):
                # Create a new Vampire character
                character = Vampire(
                    name=data["name"],
                    nature=data["nature"],
                    demeanor=data["demeanor"],
                    player=data["player"],
                    narrator=data["narrator"],
                    clan=data["clan"],
                    generation=data["generation"],
                    sect=data["sect"],
                    status="Active",  # Set default status
                    start_date=datetime.now(),
                    last_modified=datetime.now()
                )
                
                session.add(character)
                session.commit()
                
                self.status_bar.showMessage(f"Created new Vampire character: {data['name']}")
                logger.info(f"Created new Vampire character: {data['name']}")
                
            else:
                # Handle other character types
                QMessageBox.information(
                    self,
                    "Not Implemented",
                    f"Creation of {data['type']} characters is not yet implemented."
                )
                
        except Exception as e:
            error_msg = f"Failed to create character: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            if session:
                session.rollback()
        finally:
            session.close() 