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
    QListWidget, QListWidgetItem, QScrollArea, QGroupBox, QFileDialog
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from src.core.engine import get_session, init_db
from src.core.models import Character, Chronicle, Vampire
from .dialogs.character_creation import CharacterCreationDialog
from .dialogs.chronicle_creation import ChronicleCreationDialog
from .dialogs.data_manager_dialog import DataManagerDialog
from .widgets.character_list_widget import CharacterListWidget
from .widgets.plots_widget import PlotsWidget
from .widgets.rumors_widget import RumorsWidget
from .widgets.chronicle_detail_widget import ChronicleDetailWidget
from .sheets.vampire_sheet import VampireSheet
from src.utils.data_loader import (
    load_data, get_category, get_descriptions,
    get_item_description, clear_cache, load_character,
    prepare_character_for_ui, load_grapevine_file,
    create_vampire_from_dict
)

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
        
        # Chronicle detail tab references
        self.open_chronicle_tabs = {}  # chronicle_id -> tab index
        
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
        
        self.import_grapevine_action = QAction("&Import from Grapevine...", self)
        self.import_grapevine_action.triggered.connect(self._import_grapevine)
        file_menu.addAction(self.import_grapevine_action)
        
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
        
        # Scroll area for chronicle cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        
        # Container for chronicle cards
        self.chronicle_cards_container = QWidget()
        self.chronicle_cards_layout = QVBoxLayout(self.chronicle_cards_container)
        scroll.setWidget(self.chronicle_cards_container)
        
        self.chronicle_layout.addWidget(scroll)
        
        # Add placeholder for chronicle list when empty
        self.chronicles_placeholder = QLabel("No Chronicles Found\nClick 'Create New Chronicle' to get started.")
        self.chronicles_placeholder.setStyleSheet("color: gray; font-size: 14pt; margin-top: 20px;")
        self.chronicles_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
                
                # Clear existing cards
                while self.chronicle_cards_layout.count():
                    child = self.chronicle_cards_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                
                # Add chronicle cards
                for chronicle in chronicles:
                    # Get character count for this chronicle
                    character_count = session.query(Character).filter(
                        Character.chronicle_id == chronicle.id
                    ).count()
                    
                    # Create card widget
                    card = self._create_chronicle_card(chronicle, character_count)
                    self.chronicle_cards_layout.addWidget(card)
                
                # Add stretch at the end
                self.chronicle_cards_layout.addStretch()
                
                # Show placeholder if no chronicles
                if not chronicles:
                    self.chronicles_placeholder.setVisible(True)
                else:
                    self.chronicles_placeholder.setVisible(False)
                    
                self.status_bar.showMessage(f"Loaded {len(chronicles)} chronicles")
            finally:
                session.close()
        except Exception as e:
            error_msg = f"Failed to load chronicles: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def _create_chronicle_card(self, chronicle, character_count: int) -> QWidget:
        """Create a card widget for a chronicle.
        
        Args:
            chronicle: Chronicle to display
            character_count: Number of characters in the chronicle
            
        Returns:
            QWidget containing the chronicle card
        """
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f5f5f5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Chronicle name
        name_label = QLabel(chronicle.name)
        name_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333;")
        layout.addWidget(name_label)
        
        # HST (Storyteller)
        hst_text = chronicle.narrator or "No HST assigned"
        hst_label = QLabel(f"HST: {hst_text}")
        hst_label.setStyleSheet("font-size: 12pt; color: #666;")
        layout.addWidget(hst_label)
        
        # Character count
        char_label = QLabel(f"Characters: {character_count}")
        char_label.setStyleSheet("font-size: 12pt; color: #666;")
        layout.addWidget(char_label)
        
        # Make the card clickable
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.mousePressEvent = lambda event: self._on_chronicle_card_clicked(chronicle)
        
        return card
    
    def _on_chronicle_card_clicked(self, chronicle) -> None:
        """Handle click on a chronicle card.
        
        Opens a ChronicleDetailWidget in a new tab (or focuses an
        existing one if this chronicle is already open).
        
        Args:
            chronicle: The clicked chronicle
        """
        # If already open, just focus that tab
        if chronicle.id in self.open_chronicle_tabs:
            idx = self.open_chronicle_tabs[chronicle.id]
            if idx < self.tabs.count():
                self.tabs.setCurrentIndex(idx)
                return
            else:
                # Stale reference -- clean up and re-open
                del self.open_chronicle_tabs[chronicle.id]

        # Set as active chronicle
        self.active_chronicle = chronicle
        self._update_window_title()

        # Create detail widget and open as a new tab
        detail = ChronicleDetailWidget(chronicle, parent=self)
        idx = self.tabs.addTab(detail, chronicle.name)
        self.open_chronicle_tabs[chronicle.id] = idx
        self.tabs.setCurrentIndex(idx)

        self.status_bar.showMessage(f"Opened chronicle: {chronicle.name}")
        logger.info(f"Opened chronicle detail tab: {chronicle.name}")
        
    def _on_new_chronicle(self) -> None:
        """Show the dialog for creating a new chronicle."""
        dialog = ChronicleCreationDialog(self)
        dialog.chronicle_created.connect(self._create_chronicle)
        dialog.exec()
        
    def _create_chronicle(self, data: Dict[str, Any]) -> None:
        """Create a new chronicle in the database."""
        try:
            session = get_session()

            from src.core.models.player import Player

            # Find or create a Player record for the HST
            hst_name = data.get("narrator", "").strip()
            storyteller = None
            if hst_name:
                storyteller = session.query(Player).filter(Player.name == hst_name).first()
                if not storyteller:
                    storyteller = Player(name=hst_name, status="Active")
                    session.add(storyteller)
                    session.flush()

            chronicle = Chronicle(
                name=data["name"],
                narrator=hst_name,
                description=data.get("description", ""),
                start_date=data["start_date"],
                last_modified=data.get("last_modified"),
                is_active=data.get("is_active", True),
                storyteller_id=storyteller.id if storyteller else None
            )

            session.add(chronicle)
            session.commit()

            self.active_chronicle = chronicle
            self._refresh_chronicles()

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
            
    def _create_plots_widget(self) -> None:
        """Create the Plots tab widget."""
        self.plots_widget = PlotsWidget()

    def _create_rumors_widget(self) -> None:
        """Create the Rumors tab widget."""
        self.rumors_widget = RumorsWidget()
        
    def _refresh_characters(self) -> None:
        """Refresh the character list, filtered to the active chronicle."""
        try:
            session = get_session()
            try:
                # Filter to active chronicle when one is set
                query = session.query(Character)
                if self.active_chronicle:
                    query = query.filter(
                        Character.chronicle_id == self.active_chronicle.id
                    )
                characters = query.all()
                
                # Use detached copies to avoid session issues
                detached_characters = []
                for character in characters:
                    # Ensure essential attributes are loaded/accessed before
                    # passing to UI components to prevent lazy loading errors
                    _ = character.id
                    _ = character.name
                    _ = character.type
                    _ = character.player_name
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
        """Create a new character from the provided data."""
        session = None
        try:
            session = get_session()

            char_type = data.get("type", "").lower()
            now = datetime.now()

            if "vampire" in char_type:
                character = Vampire(
                    clan=data.get("clan", "Caitiff"),
                    generation=data.get("generation", 13),
                    sect=data.get("sect", ""),
                    sire="",
                    path="Humanity",
                    path_traits=0,
                    temp_path_traits=0,
                    conscience=0,
                    temp_conscience=0,
                    self_control=0,
                    temp_self_control=0,
                    courage=0,
                    temp_courage=0,
                    blood=0,
                    temp_blood=0,
                )
            else:
                character = Character()
                character.type = data["type"].split(":")[0].lower().strip()

            character.name = data.get("name", "")
            character.player_name = data.get("player", data.get("player_name", ""))
            character.nature = data.get("nature", "")
            character.demeanor = data.get("demeanor", "")
            character.status = "Active"
            character.start_date = now
            character.last_modified = now

            if self.active_chronicle:
                character.chronicle_id = self.active_chronicle.id

            session.add(character)
            session.commit()

            character_id = character.id
            session.close()
            session = None

            # Refresh character list
            self._refresh_characters()

            # Load freshly from DB and open
            loaded = load_character(character_id)
            if loaded:
                self._open_character(loaded, use_existing_object=True)

            message = f"Created new character: {data.get('name', '')}"
            if self.active_chronicle:
                message += f" in chronicle {self.active_chronicle.name}"

            self.status_bar.showMessage(message)
            logger.info(message)

        except Exception as e:
            error_msg = f"Failed to create character: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
            
    def _open_character(self, character: Any, use_existing_object: bool = False) -> None:
        """Open a character sheet in a new tab.
        
        Args:
            character: Character to open (can be Character object or character ID)
            use_existing_object: Whether to use the existing character object
        """
        # Handle both int (character ID) and Character object
        character_id = character if isinstance(character, int) else character.id
        
        # Check if character is already open
        if character_id in self.open_character_sheets:
            # Switch to the existing tab
            self.tabs.setCurrentIndex(self.open_character_sheets[character_id])
            return
            
        try:
            # Use the character object directly if specified, otherwise load from DB
            if not use_existing_object:
                # Use DataLoader to safely load character with proper session handling
                character = load_character(character_id)
                
                if not character:
                    raise ValueError(f"Character with ID {character_id} not found")
            
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
        # Remove the closed tab's entry from whichever tracking dict owns it
        for character_id, tab_index in list(self.open_character_sheets.items()):
            if tab_index == index:
                del self.open_character_sheets[character_id]
                break

        for chronicle_id, tab_index in list(self.open_chronicle_tabs.items()):
            if tab_index == index:
                del self.open_chronicle_tabs[chronicle_id]
                break

        # Close the tab
        self.tabs.removeTab(index)

        # Decrement all tracked indices above the removed index
        for cid in list(self.open_character_sheets):
            if self.open_character_sheets[cid] > index:
                self.open_character_sheets[cid] -= 1
        for cid in list(self.open_chronicle_tabs):
            if self.open_chronicle_tabs[cid] > index:
                self.open_chronicle_tabs[cid] -= 1
        
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
        session = None
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
            larp_traits_data = data.get("larp_traits", {})

            # Save to database using a single session
            session = get_session()
            character = session.query(Character).filter(Character.id == character_id).first()

            if not character:
                QMessageBox.warning(self, "Warning", "Character not found.")
                return

            # Update character based on type
            if isinstance(character, Vampire) and isinstance(sheet, VampireSheet):
                # Update basic information
                character.name = data.get("name", character.name)
                character.player_name = data.get("player_name", "")
                character.nature = data.get("nature", "")
                character.demeanor = data.get("demeanor", "")
                character.narrator = data.get("narrator", "")

                # Update vampire-specific information
                character.clan = data.get("clan", character.clan)
                character.generation = data.get("generation", character.generation)
                character.sect = data.get("sect", "")

                # Derive virtue counts from larp_traits lists
                character.conscience = len(larp_traits_data.get("conscience", []))
                character.temp_conscience = character.conscience
                character.self_control = len(larp_traits_data.get("self-control", []))
                character.temp_self_control = character.self_control
                character.courage = len(larp_traits_data.get("courage", []))
                character.temp_courage = character.courage

                # Derive path trait count from larp_traits
                character.path_traits = len(larp_traits_data.get("path", []))
                character.temp_path_traits = character.path_traits

                # Derive stat counts from larp_traits lists
                character.willpower = len(larp_traits_data.get("willpower", []))
                character.temp_willpower = character.willpower
                character.blood = len(larp_traits_data.get("blood", []))
                character.temp_blood = character.blood

                # Update last modified
                character.last_modified = datetime.now()

                # Save LARP traits
                self._save_larp_traits(session, character, larp_traits_data)

            session.add(character)
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
            if session:
                session.close()

    def _save_larp_traits(self, session: Session, character, larp_traits_data: dict) -> None:
        """Replace all LARP traits for a character with the provided data.

        Args:
            session: Active database session
            character: Character model instance
            larp_traits_data: Dict mapping category names to lists of trait name strings
        """
        from src.core.models.larp_trait import LarpTrait, TraitCategory

        # Delete all existing larp_traits for this character
        existing = session.query(LarpTrait).filter(LarpTrait.character_id == character.id).all()
        for trait in existing:
            session.delete(trait)
        session.flush()

        # Recreate larp_traits from data
        for category_name, trait_names in larp_traits_data.items():
            if not trait_names:
                continue

            # Find or create the TraitCategory
            cat = session.query(TraitCategory).filter(
                TraitCategory.name == category_name
            ).first()
            if not cat:
                cat = TraitCategory(name=category_name)
                session.add(cat)
                session.flush()

            # Create a LarpTrait record for each trait name
            for trait_name in trait_names:
                trait = LarpTrait(
                    character_id=character.id,
                    name=trait_name,
                    display_name=trait_name,
                    description=trait_name,
                )
                trait.categories.append(cat)
                session.add(trait)
            
    def _import_grapevine(self) -> None:
        """Import characters from a Grapevine XML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import from Grapevine",
            "",
            "Grapevine Files (*.gv *.gex *.xml);;All Files (*)"
        )
        if not file_path:
            return

        try:
            result = load_grapevine_file(file_path, self.active_chronicle)
            count = result.get("imported", 0) if isinstance(result, dict) else 0
            self._refresh_characters()
            self._refresh_chronicles()
            self.status_bar.showMessage(f"Imported {count} character(s) from Grapevine")
            QMessageBox.information(
                self, "Import Complete",
                f"Successfully imported {count} character(s) from:\n{file_path}"
            )
        except Exception as e:
            error_msg = f"Failed to import Grapevine file: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Import Error", error_msg)

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

    def _show_staff_manager(self) -> None:
        """Show the staff manager dialog."""
        from src.ui.dialogs.staff_manager import StaffManagerDialog
        session = get_session()
        try:
            dialog = StaffManagerDialog(session, self.active_chronicle, self)
            dialog.exec()
            self._refresh_characters()
        except Exception as e:
            logger.error(f"Staff manager error: {e}")
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()

    def _show_player_manager(self) -> None:
        """Show the player manager dialog."""
        from src.ui.dialogs.player_manager import PlayerManagerDialog
        session = get_session()
        try:
            dialog = PlayerManagerDialog(session, self.active_chronicle, self)
            dialog.exec()
            self._refresh_characters()
        except Exception as e:
            logger.error(f"Player manager error: {e}")
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close() 