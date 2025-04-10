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
    QPushButton, QLabel, QMessageBox, QApplication, QSizePolicy,
    QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from coterie.database.engine import get_session, init_db
from coterie.models.base import Character
from coterie.models.vampire import Vampire
from coterie.models.chronicle import Chronicle
from coterie.ui.dialogs.character_creation import CharacterCreationDialog
from coterie.ui.dialogs.chronicle_creation import ChronicleCreationDialog
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
        
        # Initialize database schema
        init_db()
        
        # Create the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Character sheet references
        self.open_character_sheets = {}  # id -> tab index
        
        # Active chronicle
        self.active_chronicle = None
        
        # Create UI components
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_main_interface()
        
        # Connect signals for File menu
        self.new_char_action.triggered.connect(self._on_new_character)
        self.exit_action.triggered.connect(self.close)
        
        # Connect signals for Data menu
        self.data_manager_action.triggered.connect(self._show_data_manager)
        
        # Connect signals for Chronicle menu
        self.new_chronicle_action.triggered.connect(self._on_new_chronicle)
        
        # Connect signals for toolbar
        self.refresh_action.triggered.connect(self._refresh_characters)
        
        # Initial load of chronicles and characters
        self._refresh_chronicles()
        self._refresh_characters()
        
        # Update window title with active chronicle
        self._update_window_title()
        
    def _update_window_title(self) -> None:
        """Update the window title to include the active chronicle."""
        base_title = "Coterie v0.1"
        if self.active_chronicle:
            self.setWindowTitle(f"{base_title} - {self.active_chronicle.name}")
        else:
            self.setWindowTitle(base_title)
        
    def _create_menu_bar(self) -> None:
        """Create and populate the main menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        self.new_char_action = QAction("&New Character", self)
        file_menu.addAction(self.new_char_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        self.preferences_action = QAction("&Preferences", self)
        edit_menu.addAction(self.preferences_action)
        
        # Data menu
        data_menu = menubar.addMenu("&Data")
        
        self.data_manager_action = QAction("&Data Manager", self)
        data_menu.addAction(self.data_manager_action)
        
        # Game menu - Add Character List option here
        game_menu = menubar.addMenu("&Game")
        
        # Characters tab option
        self.show_characters_action = QAction("&Characters", self)
        self.show_characters_action.triggered.connect(self._toggle_characters_tab)
        game_menu.addAction(self.show_characters_action)
        
        # People menu (formerly Players)
        people_menu = menubar.addMenu("Peo&ple")
        
        # Staff management
        self.staff_manager_action = QAction("&Staff Manager", self)
        self.staff_manager_action.triggered.connect(self._show_staff_manager)
        people_menu.addAction(self.staff_manager_action)
        
        # Player management
        self.player_manager_action = QAction("&Player Manager", self)
        self.player_manager_action.triggered.connect(self._show_player_manager)
        people_menu.addAction(self.player_manager_action)
        
        # World menu
        world_menu = menubar.addMenu("&World")
        
        # Plots tab option
        self.show_plots_action = QAction("&Plots", self)
        self.show_plots_action.triggered.connect(self._toggle_plots_tab)
        world_menu.addAction(self.show_plots_action)
        
        # Rumors tab option
        self.show_rumors_action = QAction("&Rumors", self)
        self.show_rumors_action.triggered.connect(self._toggle_rumors_tab)
        world_menu.addAction(self.show_rumors_action)
        
        self.locations_action = QAction("&Locations", self)
        world_menu.addAction(self.locations_action)
        
        # Chronicle menu
        chronicle_menu = menubar.addMenu("&Chronicle")
        
        # All Chronicles option
        self.all_chronicles_action = QAction("&All Chronicles", self)
        self.all_chronicles_action.triggered.connect(self._show_all_chronicles)
        chronicle_menu.addAction(self.all_chronicles_action)
        
        chronicle_menu.addSeparator()
        
        # Chronicle tab option
        self.show_chronicle_action = QAction("&Chronicle Manager", self)
        self.show_chronicle_action.triggered.connect(self._toggle_chronicle_tab)
        chronicle_menu.addAction(self.show_chronicle_action)
        
        self.new_chronicle_action = QAction("&New Chronicle", self)
        self.new_chronicle_action.triggered.connect(self._on_new_chronicle)
        chronicle_menu.addAction(self.new_chronicle_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        self.experience_action = QAction("&Experience Points", self)
        tools_menu.addAction(self.experience_action)
        
        # Sheets and Reports menu
        reports_menu = menubar.addMenu("&Sheets && Reports")
        
        self.character_sheet_action = QAction("&Character Sheet", self)
        reports_menu.addAction(self.character_sheet_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self._show_about)
        help_menu.addAction(self.about_action)
        
    def _create_tool_bar(self) -> None:
        """Create the application toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add toolbar actions
        self.refresh_action = QAction("Refresh", self)
        self.refresh_action.setToolTip("Refresh the character list")
        toolbar.addAction(self.refresh_action)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
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
        
        # Create the Characters widget
        self._create_characters_widget()
        
        # Create the Chronicle widget and add it as the default tab
        self._create_chronicle_widget()
        self.tabs.addTab(self.chronicle_widget, "Chronicle")
        
        # Create other tabs that can be added later
        self._create_plots_widget()
        self._create_rumors_widget()
        
    def _create_characters_widget(self) -> None:
        """Create the Characters tab widget."""
        self.characters_widget = QWidget()
        self.characters_layout = QVBoxLayout(self.characters_widget)
        
        # Use the character list widget
        self.character_list = CharacterListWidget()
        self.character_list.character_selected.connect(self._open_character)
        self.character_list.character_deleted.connect(self._delete_character)
        self.character_list.new_button.clicked.connect(self._on_new_character)
        self.characters_layout.addWidget(self.character_list)
        
    def _create_chronicle_widget(self) -> None:
        """Create the Chronicle tab widget."""
        self.chronicle_widget = QWidget()
        self.chronicle_layout = QVBoxLayout(self.chronicle_widget)
        
        # Add a heading
        heading_label = QLabel("Chronicle Management")
        heading_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.chronicle_layout.addWidget(heading_label)
        
        # Create a list widget for chronicles
        self.chronicle_list = QListWidget()
        self.chronicle_list.setMinimumHeight(200)
        self.chronicle_list.itemDoubleClicked.connect(self._set_active_chronicle)
        self.chronicle_layout.addWidget(self.chronicle_list)
        
        # Add placeholder for chronicle list when empty
        self.chronicles_placeholder = QLabel("No Chronicles Found")
        self.chronicles_placeholder.setStyleSheet("color: gray; margin-top: 20px;")
        self.chronicles_placeholder.setVisible(False)
        self.chronicle_layout.addWidget(self.chronicles_placeholder)
        
        # Add button for creating a new chronicle
        new_chronicle_button = QPushButton("Create New Chronicle")
        new_chronicle_button.setMinimumHeight(40)
        new_chronicle_button.clicked.connect(self._on_new_chronicle)
        self.chronicle_layout.addWidget(new_chronicle_button)
        
        # Add stretch to push everything up
        self.chronicle_layout.addStretch()
        
    def _refresh_chronicles(self) -> None:
        """Refresh the list of chronicles."""
        try:
            session = get_session()
            try:
                # Fetch all chronicles
                chronicles = session.query(Chronicle).all()
                
                # Clear the list
                self.chronicle_list.clear()
                
                # Add chronicles to the list
                for chronicle in chronicles:
                    item = QListWidgetItem(f"{chronicle.name} (Narrator: {chronicle.narrator})")
                    item.setData(Qt.ItemDataRole.UserRole, chronicle.id)
                    
                    # Make active chronicle bold
                    if self.active_chronicle and self.active_chronicle.id == chronicle.id:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        
                    self.chronicle_list.addItem(item)
                
                # Show placeholder if no chronicles
                if not chronicles:
                    self.chronicles_placeholder.setVisible(True)
                    self.chronicle_list.setVisible(False)
                else:
                    self.chronicles_placeholder.setVisible(False)
                    self.chronicle_list.setVisible(True)
                    
                self.status_bar.showMessage(f"Loaded {len(chronicles)} chronicles")
            finally:
                session.close()
        except Exception as e:
            error_msg = f"Failed to load chronicles: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
        
    def _on_new_chronicle(self) -> None:
        """Show the dialog for creating a new chronicle."""
        dialog = ChronicleCreationDialog(self)
        dialog.chronicle_created.connect(self._create_chronicle)
        dialog.exec()
        
    def _create_chronicle(self, data: Dict[str, Any]) -> None:
        """Create a new chronicle in the database.
        
        Args:
            data: Dictionary containing chronicle data
        """
        try:
            session = get_session()
            
            # Create a new Chronicle object
            chronicle = Chronicle(
                name=data["name"],
                narrator=data["narrator"],
                description=data.get("description", ""),
                start_date=data["start_date"],
                last_modified=data["last_modified"],
                is_active=data["is_active"]
            )
            
            # Add to database
            session.add(chronicle)
            session.commit()
            
            # Set as active chronicle
            self.active_chronicle = chronicle
            
            # Refresh the chronicle list
            self._refresh_chronicles()
            
            # Show success message
            self.status_bar.showMessage(f"Created new chronicle: {data['name']}")
            logger.info(f"Created new chronicle: {data['name']}")
            
        except Exception as e:
            error_msg = f"Failed to create chronicle: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            if session:
                session.rollback()
        finally:
            session.close()
            
    def _set_active_chronicle(self, item: QListWidgetItem) -> None:
        """Set the active chronicle.
        
        Args:
            item: The QListWidgetItem for the chronicle
        """
        chronicle_id = item.data(Qt.ItemDataRole.UserRole)
        
        try:
            session = get_session()
            
            # Fetch the chronicle
            chronicle = session.query(Chronicle).filter_by(id=chronicle_id).first()
            
            if not chronicle:
                QMessageBox.warning(self, "Warning", "Chronicle not found.")
                return
                
            # Set as active chronicle
            self.active_chronicle = chronicle
            
            # Update window title
            self._update_window_title()
            
            # Refresh the chronicle list to update display
            session.close()
            self._refresh_chronicles()
            
            # Show success message
            self.status_bar.showMessage(f"Active chronicle: {chronicle.name}")
            logger.info(f"Set active chronicle: {chronicle.name}")
            
        except Exception as e:
            error_msg = f"Failed to set active chronicle: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
        finally:
            if session:
                session.close()
    
    def _create_plots_widget(self) -> None:
        """Create the Plots tab widget."""
        self.plots_widget = QWidget()
        self.plots_layout = QVBoxLayout(self.plots_widget)
        
        # Add a heading
        heading_label = QLabel("Plots Management")
        heading_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.plots_layout.addWidget(heading_label)
        
        # Add explanation label
        info_label = QLabel(
            "Plots are story elements that drive your chronicle forward. "
            "Create and manage plots to track your chronicle's storylines."
        )
        info_label.setWordWrap(True)
        self.plots_layout.addWidget(info_label)
        
        # Add button for creating a new plot
        new_plot_button = QPushButton("Create New Plot")
        new_plot_button.setMinimumHeight(40)
        self.plots_layout.addWidget(new_plot_button)
        
        # Add placeholder for plot list
        self.plots_layout.addWidget(QLabel("No plots available yet"))
        
        # Add stretch to push everything up
        self.plots_layout.addStretch()
        
    def _create_rumors_widget(self) -> None:
        """Create the Rumors tab widget."""
        self.rumors_widget = QWidget()
        self.rumors_layout = QVBoxLayout(self.rumors_widget)
        
        # Add a heading
        heading_label = QLabel("Rumors Management")
        heading_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.rumors_layout.addWidget(heading_label)
        
        # Add explanation label
        info_label = QLabel(
            "Rumors are pieces of information that characters can learn in the game. "
            "Create and manage rumors to enhance your chronicle's intrigue."
        )
        info_label.setWordWrap(True)
        self.rumors_layout.addWidget(info_label)
        
        # Add button for creating a new rumor
        new_rumor_button = QPushButton("Create New Rumor")
        new_rumor_button.setMinimumHeight(40)
        self.rumors_layout.addWidget(new_rumor_button)
        
        # Add placeholder for rumor list
        self.rumors_layout.addWidget(QLabel("No rumors available yet"))
        
        # Add stretch to push everything up
        self.rumors_layout.addStretch()
        
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
                
                # Assign to active chronicle if available
                if self.active_chronicle:
                    character.chronicle_id = self.active_chronicle.id
                
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
                
                # Create status message
                message = f"Created new Vampire character: {data['name']}"
                if self.active_chronicle:
                    message += f" in chronicle {self.active_chronicle.name}"
                    
                self.status_bar.showMessage(message)
                logger.info(message)
                
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
                
                # Update tab indices for other character sheets
                for other_id, other_index in list(self.open_character_sheets.items()):
                    if other_index > index:
                        self.open_character_sheets[other_id] = other_index - 1
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
                
    def _toggle_characters_tab(self) -> None:
        """Toggle the visibility of the characters tab."""
        if self._is_tab_open(self.characters_widget):
            # If already open, close it
            index = self.tabs.indexOf(self.characters_widget)
            self.tabs.removeTab(index)
        else:
            # Add the tab
            index = self.tabs.addTab(self.characters_widget, "Characters")
            self.tabs.setCurrentIndex(index)
            
            # Refresh the character list when showing the tab
            self._refresh_characters()
                
    def _toggle_chronicle_tab(self) -> None:
        """Toggle the visibility of the chronicle tab."""
        if self._is_tab_open(self.chronicle_widget):
            # If already open, close it
            index = self.tabs.indexOf(self.chronicle_widget)
            self.tabs.removeTab(index)
        else:
            # Add the tab
            index = self.tabs.addTab(self.chronicle_widget, "Chronicle")
            self.tabs.setCurrentIndex(index)
                
    def _toggle_plots_tab(self) -> None:
        """Toggle the visibility of the plots tab."""
        if self._is_tab_open(self.plots_widget):
            # If already open, close it
            index = self.tabs.indexOf(self.plots_widget)
            self.tabs.removeTab(index)
        else:
            # Add the tab
            index = self.tabs.addTab(self.plots_widget, "Plots")
            self.tabs.setCurrentIndex(index)
                
    def _toggle_rumors_tab(self) -> None:
        """Toggle the visibility of the rumors tab."""
        if self._is_tab_open(self.rumors_widget):
            # If already open, close it
            index = self.tabs.indexOf(self.rumors_widget)
            self.tabs.removeTab(index)
        else:
            # Add the tab
            index = self.tabs.addTab(self.rumors_widget, "Rumors")
            self.tabs.setCurrentIndex(index)
                
    def _is_tab_open(self, widget: QWidget) -> bool:
        """Check if a tab containing the given widget is open.
        
        Args:
            widget: Widget to check for
            
        Returns:
            True if the tab is open, False otherwise
        """
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == widget:
                return True
        return False
        
    def _count_main_tabs(self) -> int:
        """Count the number of main application tabs (not character sheets).
        
        Returns:
            Number of main tabs
        """
        main_widgets = [
            self.characters_widget,
            self.chronicle_widget,
            self.plots_widget,
            self.rumors_widget
        ]
        
        count = 0
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) in main_widgets:
                count += 1
                
        return count
        
    def _show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.information(
            self,
            "About Coterie",
            "Coterie v0.1\n\nA character and chronicle management system for Mind's Eye Theater LARP."
        )

    def _show_all_chronicles(self) -> None:
        """Show the All Chronicles view with global character and player lists."""
        # Create All Chronicles dialog/window
        from PyQt6.QtWidgets import QDialog, QTabWidget, QVBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("All Chronicles")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Characters tab
        characters_widget = QWidget()
        characters_layout = QVBoxLayout(characters_widget)
        character_list = CharacterListWidget(show_all=True)  # Modified to show all characters
        characters_layout.addWidget(character_list)
        tabs.addTab(characters_widget, "All Characters")
        
        # Players tab
        players_widget = QWidget()
        players_layout = QVBoxLayout(players_widget)
        # TODO: Add player list widget
        tabs.addTab(players_widget, "All Players")
        
        # Staff tab
        staff_widget = QWidget()
        staff_layout = QVBoxLayout(staff_widget)
        # TODO: Add staff list widget
        tabs.addTab(staff_widget, "All Staff")
        
        dialog.exec() 