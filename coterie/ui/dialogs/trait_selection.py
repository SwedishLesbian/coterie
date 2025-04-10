from typing import List, Optional, Set
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from sqlalchemy.orm import Session

from ...models.menu import MenuItem, MenuCategory
from ...utils.menu_importer import MenuImporter

class TraitSelectionDialog(QDialog):
    """Dialog for selecting traits from menus."""
    
    trait_selected = pyqtSignal(MenuItem)  # Emitted when a trait is selected
    
    def __init__(self, session: Session, category_filter: Optional[str] = None, parent=None):
        """
        Initialize the trait selection dialog.
        
        Args:
            session: Database session
            category_filter: Optional category name to filter traits by
            parent: Parent widget
        """
        super().__init__(parent)
        self.session = session
        self.category_filter = category_filter
        self.importer = MenuImporter(session)
        
        self.setWindowTitle("Select Trait")
        self.setup_ui()
        self.load_traits()
        
    def setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout()
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter_traits)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Trait tree
        self.trait_tree = QTreeWidget()
        self.trait_tree.setHeaderLabels(["Name", "Cost", "Note"])
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
        
    def load_traits(self):
        """Load traits from the database into the tree widget."""
        self.trait_tree.clear()
        
        # Get all categories or filter by specified category
        query = self.session.query(MenuCategory)
        if self.category_filter:
            query = query.filter(MenuCategory.name == self.category_filter)
        categories = query.all()
        
        # Create category nodes
        for category in sorted(categories, key=lambda c: (c.display_order or 0, c.name)):
            category_item = QTreeWidgetItem(self.trait_tree)
            category_item.setText(0, category.name)
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            # Add traits to category
            for trait in sorted(category.items, key=lambda t: t.name):
                trait_item = QTreeWidgetItem(category_item)
                trait_item.setText(0, trait.name)
                trait_item.setText(1, str(trait.cost) if trait.cost is not None else "")
                trait_item.setText(2, trait.note or "")
                trait_item.setData(0, Qt.ItemDataRole.UserRole, trait)
        
        self.trait_tree.expandAll()
        
    def filter_traits(self):
        """Filter traits based on search text."""
        search_text = self.search_box.text().lower()
        
        def update_visibility(item: QTreeWidgetItem) -> bool:
            """Update item visibility based on search text. Returns True if item or any children are visible."""
            # If it's a trait item (has no children)
            if item.childCount() == 0:
                visible = search_text in item.text(0).lower()
                item.setHidden(not visible)
                return visible
            
            # If it's a category item
            visible_children = False
            for i in range(item.childCount()):
                if update_visibility(item.child(i)):
                    visible_children = True
            
            item.setHidden(not visible_children)
            return visible_children
        
        # Update visibility of all top-level items
        for i in range(self.trait_tree.topLevelItemCount()):
            update_visibility(self.trait_tree.topLevelItem(i))
    
    def handle_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on a trait item."""
        trait = item.data(0, Qt.ItemDataRole.UserRole)
        if trait:
            self.trait_selected.emit(trait)
            self.accept()
    
    def handle_selection(self):
        """Handle clicking the Select button."""
        current_item = self.trait_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a trait.")
            return
            
        trait = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not trait:
            QMessageBox.warning(self, "Invalid Selection", "Please select a trait, not a category.")
            return
            
        self.trait_selected.emit(trait)
        self.accept()
    
    @classmethod
    def select_trait(cls, session: Session, category: Optional[str] = None, parent=None) -> Optional[MenuItem]:
        """
        Show the dialog and return the selected trait.
        
        Args:
            session: Database session
            category: Optional category to filter by
            parent: Parent widget
            
        Returns:
            Selected MenuItem or None if cancelled
        """
        dialog = cls(session, category, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selected_trait
        return None 