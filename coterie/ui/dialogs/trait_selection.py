from typing import List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...models.menu import MenuItem, MenuCategory
from sqlalchemy.orm import Session

class TraitSelectionDialog(QDialog):
    """Dialog for selecting traits from menus."""
    
    trait_selected = pyqtSignal(MenuItem)
    
    def __init__(self, session: Session, category_filter: Optional[str] = None, parent=None):
        """
        Initialize the trait selection dialog.
        
        Args:
            session: Database session
            category_filter: Optional category name to filter by
            parent: Parent widget
        """
        super().__init__(parent)
        self.session = session
        self.category_filter = category_filter
        self.selected_trait = None
        
        self.setWindowTitle("Select Trait")
        self.setup_ui()
        self.load_traits()
        
    def setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search traits...")
        self.search_input.textChanged.connect(self.filter_traits)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Trait tree
        self.trait_tree = QTreeWidget()
        self.trait_tree.setHeaderLabels(["Name", "Cost", "Note"])
        self.trait_tree.setColumnWidth(0, 200)
        self.trait_tree.setColumnWidth(1, 50)
        self.trait_tree.itemDoubleClicked.connect(self.handle_double_click)
        layout.addWidget(self.trait_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        select_button = QPushButton("Select")
        select_button.clicked.connect(self.handle_selection)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.resize(500, 600)
        
    def load_traits(self):
        """Load traits from the database into the tree widget."""
        query = self.session.query(MenuCategory)
        if self.category_filter:
            query = query.filter(MenuCategory.name == self.category_filter)
            
        for category in query.all():
            category_item = QTreeWidgetItem(self.trait_tree)
            category_item.setText(0, category.name)
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            for trait in category.items:
                trait_item = QTreeWidgetItem(category_item)
                trait_item.setText(0, trait.name)
                trait_item.setText(1, str(trait.cost) if trait.cost is not None else "")
                trait_item.setText(2, trait.note or "")
                trait_item.setData(0, Qt.ItemDataRole.UserRole, trait)
                
        self.trait_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
        
    def filter_traits(self):
        """Filter traits based on search text."""
        search_text = self.search_input.text().lower()
        
        def match_item(item: QTreeWidgetItem) -> bool:
            """Check if an item matches the search text."""
            if item.childCount() > 0:  # Category
                return any(match_item(item.child(i)) for i in range(item.childCount()))
            else:  # Trait
                return any(
                    search_text in item.text(i).lower()
                    for i in range(item.columnCount())
                )
        
        # Show/hide items based on search
        for i in range(self.trait_tree.topLevelItemCount()):
            category_item = self.trait_tree.topLevelItem(i)
            matches = match_item(category_item)
            category_item.setHidden(not matches)
            
            # Show matching traits, hide non-matching
            for j in range(category_item.childCount()):
                trait_item = category_item.child(j)
                trait_item.setHidden(not match_item(trait_item))
                
    def handle_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on a trait item."""
        trait = item.data(0, Qt.ItemDataRole.UserRole)
        if trait:
            self.selected_trait = trait
            self.accept()
            
    def handle_selection(self):
        """Handle selection button click."""
        selected_items = self.trait_tree.selectedItems()
        if selected_items:
            trait = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            if trait:
                self.selected_trait = trait
                self.accept()
    
    @classmethod
    def select_trait(cls, session: Session, category_filter: Optional[str] = None, parent=None) -> Optional[MenuItem]:
        """
        Show the dialog and return the selected trait.
        
        Args:
            session: Database session
            category_filter: Optional category name to filter by
            parent: Parent widget
            
        Returns:
            Selected MenuItem or None if cancelled
        """
        dialog = cls(session, category_filter, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selected_trait
        return None 