from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QMenu,
    QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QAction

class LarpTraitWidget(QWidget):
    """
    Widget for displaying and managing LARP adjective-based traits.
    
    This widget is designed specifically for Mind's Eye Theater traits, which
    are represented as lists of adjectives rather than numeric values.
    """
    
    traitChanged = pyqtSignal(str, list)  # Emitted when traits are modified
    
    def __init__(self, trait_name, trait_list=None, parent=None):
        """
        Initialize the LARP trait widget.
        
        Args:
            trait_name (str): The name of the trait category (e.g. "Physical", "Mental")
            trait_list (list): List of adjective traits (e.g. ["Quick", "Strong"])
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        self.trait_name = trait_name
        self.traits = trait_list or []
        
        self._setup_ui()
        self._populate_traits()
        
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Trait category label
        self.label = QLabel(self.trait_name)
        self.label.setObjectName("trait_category_label")
        layout.addWidget(self.label)
        
        # Trait list widget
        self.trait_list_widget = QListWidget()
        self.trait_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.trait_list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.trait_list_widget)
        
        # Button layout
        btn_layout = QHBoxLayout()
        
        # Add trait button
        self.add_btn = QPushButton("Add Trait")
        self.add_btn.clicked.connect(self._add_trait)
        btn_layout.addWidget(self.add_btn)
        
        # Remove trait button
        self.remove_btn = QPushButton("Remove Trait")
        self.remove_btn.clicked.connect(self._remove_selected_trait)
        btn_layout.addWidget(self.remove_btn)
        
        layout.addLayout(btn_layout)
    
    def _populate_traits(self):
        """Populate the trait list with existing traits."""
        self.trait_list_widget.clear()
        for trait in self.traits:
            item = QListWidgetItem(trait)
            self.trait_list_widget.addItem(item)
    
    def _add_trait(self):
        """Add a new trait through user input."""
        trait, ok = QInputDialog.getText(
            self, 
            f"Add {self.trait_name} Trait", 
            "Enter new trait adjective:"
        )
        
        if ok and trait:
            # Check for duplicates
            if trait in self.traits:
                QMessageBox.warning(
                    self, 
                    "Duplicate Trait", 
                    f"The trait '{trait}' already exists in this category."
                )
                return
            
            # Add to internal list and UI
            self.traits.append(trait)
            self.trait_list_widget.addItem(QListWidgetItem(trait))
            
            # Emit signal for trait change
            self.traitChanged.emit(self.trait_name, self.traits)
    
    def _remove_selected_trait(self):
        """Remove the currently selected trait."""
        current_item = self.trait_list_widget.currentItem()
        if not current_item:
            return
        
        trait = current_item.text()
        row = self.trait_list_widget.currentRow()
        
        # Remove from UI and internal list
        self.trait_list_widget.takeItem(row)
        self.traits.remove(trait)
        
        # Emit signal for trait change
        self.traitChanged.emit(self.trait_name, self.traits)
    
    def _show_context_menu(self, position: QPoint):
        """
        Show a context menu for trait operations.
        
        Args:
            position (QPoint): Position where to show the menu
        """
        item = self.trait_list_widget.itemAt(position)
        if not item:
            return
        
        context_menu = QMenu(self)
        
        # Rename action
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self._rename_trait(item))
        context_menu.addAction(rename_action)
        
        # Mark as spent action
        mark_spent_action = QAction("Mark as Spent", self)
        mark_spent_action.triggered.connect(lambda: self._mark_trait_as_spent(item))
        context_menu.addAction(mark_spent_action)
        
        # Remove action
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(lambda: self._remove_trait(item))
        context_menu.addAction(remove_action)
        
        # Show the menu
        context_menu.exec(self.trait_list_widget.mapToGlobal(position))
    
    def _rename_trait(self, item):
        """
        Rename a trait.
        
        Args:
            item (QListWidgetItem): The item to rename
        """
        old_trait = item.text()
        new_trait, ok = QInputDialog.getText(
            self, 
            f"Rename {self.trait_name} Trait", 
            "Enter new trait name:", 
            text=old_trait
        )
        
        if ok and new_trait and new_trait != old_trait:
            # Check for duplicates
            if new_trait in self.traits:
                QMessageBox.warning(
                    self, 
                    "Duplicate Trait", 
                    f"The trait '{new_trait}' already exists in this category."
                )
                return
            
            # Update internal list and UI
            index = self.traits.index(old_trait)
            self.traits[index] = new_trait
            item.setText(new_trait)
            
            # Emit signal for trait change
            self.traitChanged.emit(self.trait_name, self.traits)
    
    def _mark_trait_as_spent(self, item):
        """
        Mark a trait as spent (crossed out or italicized).
        
        Args:
            item (QListWidgetItem): The item to mark
        """
        # Toggle spent status in appearance
        font = item.font()
        font.setItalic(not font.italic())
        item.setFont(font)
        
        # Visual indicator for spent traits
        if font.italic():
            item.setText(f"{item.text()} (spent)")
        else:
            item.setText(item.text().replace(" (spent)", ""))
        
        # Note: The internal list doesn't change, just the display
    
    def _remove_trait(self, item):
        """
        Remove a trait.
        
        Args:
            item (QListWidgetItem): The item to remove
        """
        trait = item.text()
        # Remove (spent) suffix if present
        if " (spent)" in trait:
            trait = trait.replace(" (spent)", "")
        
        row = self.trait_list_widget.row(item)
        
        # Remove from UI and internal list
        self.trait_list_widget.takeItem(row)
        self.traits.remove(trait)
        
        # Emit signal for trait change
        self.traitChanged.emit(self.trait_name, self.traits)
    
    def get_traits(self):
        """
        Get the current list of traits.
        
        Returns:
            list: The current trait list
        """
        return self.traits.copy()
    
    def set_traits(self, traits):
        """
        Set the trait list and update the UI.
        
        Args:
            traits (list): New list of traits
        """
        self.traits = traits.copy()
        self._populate_traits()
        
    def add_traits(self, traits):
        """
        Add multiple traits to the list.
        
        Args:
            traits (list): Traits to add
        """
        for trait in traits:
            if trait not in self.traits:
                self.traits.append(trait)
        
        self._populate_traits()
        self.traitChanged.emit(self.trait_name, self.traits)
        
class LarpTraitCategoryWidget(QWidget):
    """
    Widget for displaying a category of LARP traits (e.g., Physical, Social, Mental).
    
    This widget contains multiple trait categories and manages them collectively.
    """
    
    categoryChanged = pyqtSignal(str, dict)  # Emitted when any trait in the category changes
    
    def __init__(self, category_name, trait_categories=None, parent=None):
        """
        Initialize the LARP trait category widget.
        
        Args:
            category_name (str): The name of the overall category (e.g. "Attributes")
            trait_categories (dict): Dictionary mapping subcategories to trait lists
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        self.category_name = category_name
        self.trait_categories = trait_categories or {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Category label
        self.label = QLabel(self.category_name)
        self.label.setObjectName("trait_category_header")
        layout.addWidget(self.label)
        
        # Trait widgets container
        self.trait_widgets = {}
        
        # Create trait widgets for each subcategory
        for subcategory, traits in self.trait_categories.items():
            trait_widget = LarpTraitWidget(subcategory, traits)
            trait_widget.traitChanged.connect(self._on_trait_changed)
            layout.addWidget(trait_widget)
            self.trait_widgets[subcategory] = trait_widget
    
    def _on_trait_changed(self, subcategory, traits):
        """
        Handle trait changes in a subcategory.
        
        Args:
            subcategory (str): The subcategory that changed
            traits (list): The updated trait list
        """
        self.trait_categories[subcategory] = traits
        self.categoryChanged.emit(self.category_name, self.trait_categories)
    
    def get_category_traits(self):
        """
        Get all traits in this category.
        
        Returns:
            dict: Dictionary mapping subcategories to trait lists
        """
        return self.trait_categories.copy()
    
    def set_category_traits(self, trait_categories):
        """
        Set all traits in this category.
        
        Args:
            trait_categories (dict): Dictionary mapping subcategories to trait lists
        """
        self.trait_categories = trait_categories.copy()
        
        # Update existing widgets
        for subcategory, traits in trait_categories.items():
            if subcategory in self.trait_widgets:
                self.trait_widgets[subcategory].set_traits(traits)
    
    def add_subcategory(self, subcategory, traits=None):
        """
        Add a new subcategory of traits.
        
        Args:
            subcategory (str): The name of the subcategory
            traits (list): Initial list of traits
        """
        if subcategory in self.trait_widgets:
            return
        
        # Add to internal data
        self.trait_categories[subcategory] = traits or []
        
        # Add widget
        trait_widget = LarpTraitWidget(subcategory, traits)
        trait_widget.traitChanged.connect(self._on_trait_changed)
        self.layout().addWidget(trait_widget)
        self.trait_widgets[subcategory] = trait_widget 