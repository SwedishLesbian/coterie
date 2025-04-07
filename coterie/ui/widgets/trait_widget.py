"""Trait widget for displaying character traits with dot ratings."""

from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSpinBox
)
from PyQt6.QtCore import pyqtSignal

class TraitWidget(QWidget):
    """Widget for displaying a trait with dot rating."""
    
    value_changed = pyqtSignal(int)
    
    def __init__(
        self, 
        name: str, 
        max_value: int = 5, 
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the trait widget.
        
        Args:
            name: Name of the trait
            max_value: Maximum value for the trait (default: 5)
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create widgets
        self.name_label = QLabel(name)
        self.value_spin = QSpinBox()
        self.value_spin.setRange(0, max_value)
        self.dots_label = QLabel()
        
        # Add widgets to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.value_spin)
        layout.addWidget(self.dots_label)
        layout.addStretch()
        
        # Connect signals
        self.value_spin.valueChanged.connect(self._update_dots)
        self.value_spin.valueChanged.connect(self.value_changed)
        
        # Initial update
        self._update_dots(0)
        
    def _update_dots(self, value: int) -> None:
        """Update the dots display.
        
        Args:
            value: Current trait value
        """
        dots = "●" * value + "○" * (self.value_spin.maximum() - value)
        self.dots_label.setText(dots)
        
    def get_value(self) -> int:
        """Get the current trait value.
        
        Returns:
            Current value of the trait
        """
        return self.value_spin.value()
    
    def set_value(self, value: int) -> None:
        """Set the trait value.
        
        Args:
            value: New value for the trait
        """
        self.value_spin.setValue(value)
        
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the trait widget.
        
        Args:
            enabled: Whether the widget should be enabled
        """
        self.value_spin.setEnabled(enabled) 