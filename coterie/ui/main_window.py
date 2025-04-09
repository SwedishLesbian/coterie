"""Main application window for Coterie.

This module implements the main window interface, providing access to character management,
chronicle tools, and other core functionality.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QMenuBar, QStatusBar, QToolBar,
    QPushButton, QLabel, QMessageBox, QApplication
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from coterie.database.engine import get_session
from coterie.models.base import Character
from coterie.models.vampire import Vampire
from coterie.ui.dialogs.character_creation import CharacterCreationDialog
from coterie.ui.dialogs.data_manager_dialog import DataManagerDialog
from coterie.ui.widgets.character_list_widget import CharacterListWidget
from coterie.ui.sheets.vampire_sheet import VampireSheet
from coterie.utils.data_loader import DataLoader

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window providing access to all Coterie functionality."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the main window.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Coterie v0.1")
        self.setMinimumSize(1024, 768)
        
        # Create the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Character sheet references
        self.open_character_sheets = {}  # id -> tab index
        
        # Create UI components
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_main_interface()
        
        # Connect signals
        self.new_char_action.triggered.connect(self._on_new_character)
        self.refresh_action.triggered.connect(self._refresh_characters)
        self.data_manager_action.triggered.connect(self._show_data_manager)
        
        # Initial load of characters
        self._refresh_characters()
        
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
        
        self.export_action = QAction("&Export Character", self)
        file_menu.addAction(self.export_action)
        
        self.import_action = QAction("&Import Character", self)
        file_menu.addAction(self.import_action)
        
        file_menu.addSeparator()
        
        self.refresh_action = QAction("&Refresh", self)
        self.refresh_action.setShortcut("F5")
        file_menu.addAction(self.refresh_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Alt+F4")
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        self.preferences_action = QAction("&Preferences", self)
        edit_menu.addAction(self.preferences_action)
        
        # Data menu (new)
        data_menu = menubar.addMenu("&Data")
        
        self.data_manager_action = QAction("&Data Manager", self)
        data_menu.addAction(self.data_manager_action)
        
        # Game menu (new)
        game_menu = menubar.addMenu("&Game")
        
        self.dice_roller_action = QAction("&Dice Roller", self)
        game_menu.addAction(self.dice_roller_action)
        
        self.combat_tracker_action = QAction("&Combat Tracker", self)
        game_menu.addAction(self.combat_tracker_action)
        
        # Players menu (new)
        players_menu = menubar.addMenu("&Players")
        
        self.player_manager_action = QAction("&Player Manager", self)
        players_menu.addAction(self.player_manager_action)
        
        self.player_notes_action = QAction("Player &Notes", self)
        players_menu.addAction(self.player_notes_action)
        
        # World menu (new)
        world_menu = menubar.addMenu("&World")
        
        self.locations_action = QAction("&Locations", self)
        world_menu.addAction(self.locations_action)
        
        self.npcs_action = QAction("&NPCs", self)
        world_menu.addAction(self.npcs_action)
        
        self.factions_action = QAction("&Factions", self)
        world_menu.addAction(self.factions_action)
        
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
        
        # Sheets and Reports menu (new)
        reports_menu = menubar.addMenu("&Sheets && Reports")
        
        self.character_sheet_action = QAction("&Character Sheet", self)
        reports_menu.addAction(self.character_sheet_action)
        
        self.experience_report_action = QAction("&Experience Report", self)
        reports_menu.addAction(self.experience_report_action)
        
        self.chronicle_report_action = QAction("&Chronicle Report", self)
        reports_menu.addAction(self.chronicle_report_action)
        
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
        
        toolbar.addSeparator()
        
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._refresh_characters)
        toolbar.addWidget(refresh)
        
    def _create_status_bar(self) -> None:
        """Create and configure the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def _create_main_interface(self) -> None:
        """Create the main interface with tabs for different views."""
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.layout.addWidget(self.tabs)
        
        # Characters tab
        self.characters_widget = QWidget()
        self.characters_layout = QVBoxLayout(self.characters_widget)
        
        # Use the character list widget
        self.character_list = CharacterListWidget()
        self.character_list.character_selected.connect(self._open_character)
        self.character_list.character_deleted.connect(self._delete_character)
        self.character_list.new_button.clicked.connect(self._on_new_character)
        self.characters_layout.addWidget(self.character_list)
        
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
        
    def _refresh_characters(self) -> None:
        """Refresh the character list."""
        try:
            session = get_session()
            try:
                # Use safer query approach with explicit column loading
                characters = session.query(Character).all()
                
                # Use detached copies to avoid session issues
                detached_characters = []
                for character in characters:
                    # Ensure essential attributes are loaded/accessed before
                    # passing to UI components to prevent lazy loading errors
                    _ = character.id
                    _ = character.name
                    _ = character.type
                    _ = character.player
                    _ = character.status
                    detached_characters.append(character)
                
                # Update character list with detached copies
                self.character_list.set_characters(detached_characters)
                
                # Update status bar
                self.status_bar.showMessage(f"Loaded {len(characters)} characters")
            finally:
                session.close()
            
        except Exception as e:
            error_msg = f"Failed to load characters: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            
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
                
                # Add to database and commit
                session.add(character)
                session.commit()
                
                # Prepare the character for UI by preloading all attributes
                # This prevents lazy loading issues when the session is closed
                prepared_character = DataLoader.prepare_character_for_ui(character)
                
                # Refresh character list
                self._refresh_characters()
                
                # Open the new character using the prepared object
                self._open_character(prepared_character, use_existing_object=True)
                
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
            
    def _open_character(self, character: Character, use_existing_object: bool = False) -> None:
        """Open a character sheet in a new tab.
        
        Args:
            character: Character to open
            use_existing_object: Whether to use the existing character object
        """
        # Check if character is already open
        if character.id in self.open_character_sheets:
            # Switch to the existing tab
            self.tabs.setCurrentIndex(self.open_character_sheets[character.id])
            return
            
        try:
            # Use the character object directly if specified, otherwise load from DB
            if not use_existing_object:
                # Use DataLoader to safely load character with proper session handling
                character = DataLoader.load_character(character.id)
                
                if not character:
                    raise ValueError(f"Character with ID {character.id} not found")
            
            # Create appropriate sheet based on character type
            if isinstance(character, Vampire):
                sheet = VampireSheet()
                sheet.load_character(character)
                sheet.modified.connect(lambda: self._save_character(character.id))
                
                # Add a new tab
                tab_index = self.tabs.addTab(sheet, f"{character.name} - Vampire")
                
                # Store reference
                self.open_character_sheets[character.id] = tab_index
                
                # Switch to the new tab
                self.tabs.setCurrentIndex(tab_index)
                
                self.status_bar.showMessage(f"Opened character: {character.name}")
                
            else:
                # Handle other character types
                QMessageBox.information(
                    self,
                    "Not Implemented",
                    f"Viewing {character.type} characters is not yet implemented."
                )
                
        except Exception as e:
            error_msg = f"Failed to open character: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            
    def _close_tab(self, index: int) -> None:
        """Close a tab.
        
        Args:
            index: Index of the tab to close
        """
        # Check if this is a character sheet tab
        for character_id, tab_index in list(self.open_character_sheets.items()):
            if tab_index == index:
                # Remove reference
                del self.open_character_sheets[character_id]
                break
                
        # Close the tab
        self.tabs.removeTab(index)
        
    def _delete_character(self, character_id: int) -> None:
        """Delete a character.
        
        Args:
            character_id: ID of the character to delete
        """
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this character? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
            
        try:
            session = get_session()
            
            # Get character
            character = session.query(Character).filter_by(id=character_id).first()
            
            if not character:
                QMessageBox.warning(self, "Warning", "Character not found.")
                return
                
            # Store name for message
            name = character.name
                
            # Delete character
            session.delete(character)
            session.commit()
            
            # Close character sheet if open
            if character_id in self.open_character_sheets:
                tab_index = self.open_character_sheets[character_id]
                self.tabs.removeTab(tab_index)
                del self.open_character_sheets[character_id]
                
                # Update tab indices for other character sheets
                for other_id, other_index in list(self.open_character_sheets.items()):
                    if other_index > tab_index:
                        self.open_character_sheets[other_id] = other_index - 1
                
            # Refresh character list
            self._refresh_characters()
            
            self.status_bar.showMessage(f"Deleted character: {name}")
            logger.info(f"Deleted character: {name}")
            
        except Exception as e:
            error_msg = f"Failed to delete character: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            if session:
                session.rollback()
        finally:
            session.close()
            
    def _save_character(self, character_id: int) -> None:
        """Save changes to a character.
        
        Args:
            character_id: ID of the character to save
        """
        try:
            # Get character sheet
            if character_id not in self.open_character_sheets:
                return
                
            tab_index = self.open_character_sheets[character_id]
            sheet = self.tabs.widget(tab_index)
            
            if not hasattr(sheet, 'get_character_data'):
                return
                
            # Get updated data
            data = sheet.get_character_data()
            
            # Save to database
            session = get_session()
            
            # Get character using DataLoader for proper session handling
            character = DataLoader.load_character(character_id)
            
            if not character:
                QMessageBox.warning(self, "Warning", "Character not found.")
                return
                
            # Update character based on type
            if isinstance(character, Vampire) and isinstance(sheet, VampireSheet):
                # Update basic information
                character.name = data["name"]
                character.player = data["player"]
                character.nature = data["nature"]
                character.demeanor = data["demeanor"]
                
                # Update vampire-specific information
                character.clan = data["clan"]
                character.generation = data["generation"]
                character.sect = data["sect"]
                
                # Update virtues and path
                character.conscience = data["conscience"]
                character.temp_conscience = data["temp_conscience"]
                character.self_control = data["self_control"]
                character.temp_self_control = data["temp_self_control"]
                character.courage = data["courage"]
                character.temp_courage = data["temp_courage"]
                character.path = data["path"]
                character.path_traits = data["path_traits"]
                character.temp_path_traits = data["temp_path_traits"]
                
                # Update stats
                character.willpower = data["willpower"]
                character.temp_willpower = data["temp_willpower"]
                character.blood = data["blood"]
                character.temp_blood = data["temp_blood"]
                
                # Update last modified
                character.last_modified = datetime.now()
                
                # TODO: Handle traits
                
            session.add(character)  # Make sure the character is attached to this session
            session.commit()
            
            self.status_bar.showMessage(f"Saved character: {character.name}")
            logger.info(f"Saved character: {character.name}")
            
        except Exception as e:
            error_msg = f"Failed to save character: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            if session:
                session.rollback()
        finally:
            session.close()
            
    def _show_data_manager(self) -> None:
        """Show the data manager dialog."""
        dialog = DataManagerDialog(self)
        dialog.exec()
        
        # Refresh any open character sheets
        for tab_index in range(self.tabs.count()):
            widget = self.tabs.widget(tab_index)
            if hasattr(widget, 'refresh'):
                widget.refresh() 