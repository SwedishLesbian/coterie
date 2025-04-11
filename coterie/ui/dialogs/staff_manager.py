"""Dialog for managing staff members in a chronicle."""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QWidget, QMessageBox,
    QFormLayout, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session
from ...models.chronicle import Chronicle
from ...models.staff import Staff

class StaffManagerDialog(QDialog):
    """Dialog for managing staff members."""
    
    def __init__(self, session: Session, chronicle: Optional[Chronicle], parent: Optional[QWidget] = None):
        """Initialize the staff manager dialog.
        
        Args:
            session: Database session
            chronicle: Current chronicle or None for all chronicles
            parent: Parent widget
        """
        super().__init__(parent)
        self.session = session
        self.chronicle = chronicle
        
        self.setWindowTitle("Staff Manager")
        self.setModal(True)
        self.resize(600, 400)
        
        self._setup_ui()
        self._load_staff()
        
    def _setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout(self)
        
        # Staff list
        list_layout = QHBoxLayout()
        
        self.staff_list = QListWidget()
        self.staff_list.itemSelectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self.staff_list)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.add_button = QPushButton("Add Staff")
        self.add_button.clicked.connect(self._add_staff)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self._edit_staff)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._remove_staff)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addLayout(list_layout)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
    def _load_staff(self):
        """Load staff members from the database."""
        self.staff_list.clear()
        
        query = self.session.query(Staff)
        if self.chronicle:
            query = query.filter(Staff.chronicle_id == self.chronicle.id)
            
        for staff in query.all():
            item = QListWidgetItem(f"{staff.name} - {staff.role}")
            item.setData(Qt.ItemDataRole.UserRole, staff)
            self.staff_list.addItem(item)
            
    def _on_selection_changed(self):
        """Handle selection changes in the staff list."""
        has_selection = bool(self.staff_list.selectedItems())
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)
        
    def _add_staff(self):
        """Add a new staff member."""
        dialog = StaffEditDialog(self.session, self.chronicle, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_staff()
            
    def _edit_staff(self):
        """Edit the selected staff member."""
        selected = self.staff_list.selectedItems()
        if not selected:
            return
            
        staff = selected[0].data(Qt.ItemDataRole.UserRole)
        dialog = StaffEditDialog(self.session, self.chronicle, staff, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_staff()
            
    def _remove_staff(self):
        """Remove the selected staff member."""
        selected = self.staff_list.selectedItems()
        if not selected:
            return
            
        staff = selected[0].data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove {staff.name} from staff?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.session.delete(staff)
            self.session.commit()
            self._load_staff()
            
class StaffEditDialog(QDialog):
    """Dialog for editing staff member details."""
    
    def __init__(self, session: Session, chronicle: Optional[Chronicle], staff: Optional[Staff] = None, parent: Optional[QWidget] = None):
        """Initialize the staff edit dialog.
        
        Args:
            session: Database session
            chronicle: Current chronicle or None for all chronicles
            staff: Staff member to edit or None for new staff
            parent: Parent widget
        """
        super().__init__(parent)
        self.session = session
        self.chronicle = chronicle
        self.staff = staff
        
        self.setWindowTitle("Edit Staff Member" if staff else "Add Staff Member")
        self.setModal(True)
        
        self._setup_ui()
        if staff:
            self._load_staff_data()
            
    def _setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QFormLayout(self)
        
        # Name field
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        # Role selector
        self.role_combo = QComboBox()
        self.role_combo.addItems(["HST", "Assistant HST", "Narrator", "Plot Staff"])
        layout.addRow("Role:", self.role_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save_staff)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addRow("", button_layout)
        
    def _load_staff_data(self):
        """Load existing staff data into the form."""
        self.name_edit.setText(self.staff.name)
        index = self.role_combo.findText(self.staff.role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)
            
    def _save_staff(self):
        """Save the staff member data."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a name.")
            return
            
        if not self.staff:
            self.staff = Staff()
            self.session.add(self.staff)
            
        self.staff.name = name
        self.staff.role = self.role_combo.currentText()
        if self.chronicle:
            self.staff.chronicle_id = self.chronicle.id
            
        try:
            self.session.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save staff member: {str(e)}")
            self.session.rollback() 