"""Widget for displaying and editing groups of related traits."""

from typing import Dict, List, Optional, Tuple, Union, Callable
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QPushButton, QComboBox,
    QScrollArea, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from coterie.models.base import Trait
from .trait_widget import TraitWidget

class TraitGroupWidget(QWidget):
    """Widget for displaying and managing a group of related traits."""
    
    trait_changed = pyqtSignal(str, int)  # Trait name, new value
    trait_added = pyqtSignal(str, int)    # Trait name, initial value
    trait_removed = pyqtSignal(str)       # Trait name
    
    def __init__(
        self,
        title: str,
        traits: Union[List[Trait], Dict[str, int]] = None,
        max_value: int = 5,
        editable: bool = True,
        show_temp: bool = False,
        allow_custom: bool = False,
        data_file: Optional[str] = None,
        category: Optional[str] = None,
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the trait group widget.
        
        Args:
            title: Title for the group
            traits: List of Trait objects or dictionary of trait names and values
            max_value: Maximum value for traits (default: 5)
            editable: Whether traits can be edited (default: True)
            show_temp: Whether to show temporary values (default: False)
            allow_custom: Whether to allow adding custom traits (default: False)
            data_file: Optional JSON data file to load available traits from
            category: Optional category within the data file to use
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.title = title
        self.max_value = max_value
        self.editable = editable
        self.show_temp = show_temp
        self.allow_custom = allow_custom
        self.data_file = data_file
        self.category = category
        
        # Set up available traits if data file provided
        self.available_traits = []
        self.trait_descriptions = {}
        if data_file:
            self._load_data_from_file()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create group box
        group_box = QGroupBox(title)
        group_layout = QVBoxLayout(group_box)
        layout.addWidget(group_box)
        
        # Add scroll area for traits
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        group_layout.addWidget(scroll)
        
        # Create container for traits
        self.trait_container = QWidget()
        self.trait_layout = QVBoxLayout(self.trait_container)
        self.trait_layout.setContentsMargins(0, 0, 0, 0)
        self.trait_layout.setSpacing(2)
        scroll.setWidget(self.trait_container)
        
        # Add controls for adding traits if editable and allowed
        if editable and (allow_custom or (data_file and category)):
            controls_layout = QHBoxLayout()
            group_layout.addLayout(controls_layout)
            
            # Add trait selector
            self.trait_selector = QComboBox()
            if self.available_traits:
                self.trait_selector.addItems(self.available_traits)
            else:
                self.trait_selector.setEditable(True)
                self.trait_selector.setPlaceholderText("Custom trait...")
            controls_layout.addWidget(self.trait_selector)
            
            # Add button
            add_button = QPushButton("Add")
            add_button.clicked.connect(self._add_trait_from_selector)
            controls_layout.addWidget(add_button)
        
        # Dictionary to store trait widgets
        self.trait_widgets: Dict[str, TraitWidget] = {}
        
        # Add initial traits
        if traits:
            self.set_traits(traits)
    
    def _load_data_from_file(self) -> None:
        """Load available traits from JSON data file."""
        if not self.data_file or not os.path.exists(self.data_file):
            return
            
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Get traits from specified category if provided
            if self.category and self.category in data:
                self.available_traits = data[self.category]
            # Or use all traits if no category specified
            elif not self.category:
                # Flatten all categories
                self.available_traits = []
                for category, traits in data.items():
                    if isinstance(traits, list):
                        self.available_traits.extend(traits)
            
            # Get descriptions if available
            if "descriptions" in data:
                self.trait_descriptions = data["descriptions"]
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data file {self.data_file}: {e}")
    
    def _add_trait_from_selector(self) -> None:
        """Add a trait from the trait selector."""
        trait_name = self.trait_selector.currentText()
        if not trait_name or trait_name in self.trait_widgets:
            return
            
        # Get description if available
        note = self.trait_descriptions.get(trait_name, "")
        
        # Add the trait
        self.add_trait(trait_name, 1, note=note)
        
        # Reset the selector if editable
        if self.trait_selector.isEditable():
            self.trait_selector.setCurrentText("")
            
    def _on_trait_value_changed(self, trait_name: str, value: int) -> None:
        """Handle value changes in a trait widget.
        
        Args:
            trait_name: Name of the trait
            value: New value of the trait
        """
        self.trait_changed.emit(trait_name, value)
        
    def _on_remove_trait(self, trait_name: str) -> None:
        """Remove a trait from the group.
        
        Args:
            trait_name: Name of the trait to remove
        """
        if trait_name in self.trait_widgets:
            # Remove the widget
            widget = self.trait_widgets.pop(trait_name)
            self.trait_layout.removeWidget(widget)
            widget.deleteLater()
            
            # Emit signal
            self.trait_removed.emit(trait_name)
    
    def add_trait(
        self, 
        name: str, 
        value: int = 0, 
        temp_value: Optional[int] = None,
        note: str = ""
    ) -> Optional[TraitWidget]:
        """Add a trait to the group.
        
        Args:
            name: Name of the trait
            value: Initial value of the trait
            temp_value: Initial temporary value (default: None, uses value)
            note: Optional note for the trait
            
        Returns:
            TraitWidget instance or None if trait already exists
        """
        # Check if trait already exists
        if name in self.trait_widgets:
            return None
            
        # Create trait widget
        widget = TraitWidget(
            name=name,
            value=value,
            temp_value=temp_value,
            max_value=self.max_value,
            editable=self.editable,
            show_temp=self.show_temp,
            note=note,
            category=self.title.lower() if self.title else ""
        )
        
        # Connect signals
        widget.value_changed.connect(lambda v: self._on_trait_value_changed(name, v))
        
        # Add remove button if editable
        if self.editable and self.allow_custom:
            # Replace the layout
            old_layout = widget.layout()
            new_layout = QHBoxLayout(widget)
            new_layout.setContentsMargins(0, 0, 0, 0)
            
            # Move existing widgets to new layout
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    new_layout.addWidget(item.widget())
            
            # Add remove button
            remove_button = QPushButton("✕")
            remove_button.setFixedSize(20, 20)
            remove_button.clicked.connect(lambda: self._on_remove_trait(name))
            new_layout.addWidget(remove_button)
        
        # Add widget to layout
        self.trait_layout.addWidget(widget)
        self.trait_widgets[name] = widget
        
        # Emit signal
        self.trait_added.emit(name, value)
        
        return widget
    
    def get_trait(self, name: str) -> Optional[TraitWidget]:
        """Get a trait widget by name.
        
        Args:
            name: Name of the trait
            
        Returns:
            TraitWidget instance or None if not found
        """
        return self.trait_widgets.get(name)
    
    def get_trait_value(self, name: str) -> int:
        """Get the value of a trait.
        
        Args:
            name: Name of the trait
            
        Returns:
            Value of the trait or 0 if not found
        """
        widget = self.get_trait(name)
        return widget.get_value() if widget else 0
    
    def get_trait_values(self) -> Dict[str, Tuple[int, int]]:
        """Get all trait values.
        
        Returns:
            Dictionary of trait names to (value, temp_value) tuples
        """
        return {name: widget.get_values() for name, widget in self.trait_widgets.items()}
    
    def set_traits(self, traits: Union[List[Trait], Dict[str, int]]) -> None:
        """Set the traits to display.
        
        Args:
            traits: List of Trait objects or dictionary of trait names and values
        """
        # Clear existing traits
        for widget in self.trait_widgets.values():
            widget.deleteLater()
        self.trait_widgets.clear()
        
        # Add new traits
        if isinstance(traits, list):
            # Handle Trait objects
            for trait in traits:
                self.add_trait(
                    trait.name, 
                    trait.value, 
                    getattr(trait, 'temp_value', None),
                    getattr(trait, 'note', "")
                )
        elif isinstance(traits, dict):
            # Handle dictionary of name -> value
            for name, value in traits.items():
                if isinstance(value, tuple) and len(value) >= 2:
                    # Handle (value, temp_value) tuples
                    self.add_trait(name, value[0], value[1])
                else:
                    # Handle simple value
                    self.add_trait(name, value)
    
    def set_editable(self, editable: bool) -> None:
        """Set whether the traits can be edited.
        
        Args:
            editable: Whether traits can be edited
        """
        self.editable = editable
        for widget in self.trait_widgets.values():
            widget.set_enabled(editable)
    
    def set_show_temp(self, show_temp: bool) -> None:
        """Set whether to show temporary values.
        
        Args:
            show_temp: Whether to show temporary values
        """
        self.show_temp = show_temp
        for widget in self.trait_widgets.values():
            widget.set_show_temp(show_temp)
            
    def set_trait_value(self, name: str, value: int) -> None:
        """Set the value of a trait.
        
        Args:
            name: Name of the trait
            value: New value for the trait
        """
        widget = self.get_trait(name)
        if widget:
            widget.set_value(value)
            
    def set_trait_temp_value(self, name: str, temp_value: int) -> None:
        """Set the temporary value of a trait.
        
        Args:
            name: Name of the trait
            temp_value: New temporary value for the trait
        """
        widget = self.get_trait(name)
        if widget:
            widget.set_temp_value(temp_value) 