"""Trait widget for displaying character traits with dot ratings."""

from typing import Optional, Callable, Tuple
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSpinBox,
    QToolTip, QPushButton, QMenu, QAction
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QMouseEvent, QContextMenuEvent

class TraitWidget(QWidget):
    """Widget for displaying a trait with dot rating in World of Darkness style."""
    
    value_changed = pyqtSignal(int)
    temp_value_changed = pyqtSignal(int)
    
    def __init__(
        self, 
        name: str, 
        max_value: int = 5,
        value: int = 0,
        temp_value: Optional[int] = None,
        category: str = "",
        note: str = "",
        editable: bool = True,
        show_temp: bool = False,
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the trait widget.
        
        Args:
            name: Name of the trait
            max_value: Maximum value for the trait (default: 5)
            value: Initial value of the trait (default: 0)
            temp_value: Initial temporary value (default: None, uses value)
            category: Category of the trait (physical, social, mental, etc.)
            note: Note or description for the trait
            editable: Whether the trait can be edited (default: True)
            show_temp: Whether to show temporary values (default: False)
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.name = name
        self.max_value = max_value
        self._value = value
        self._temp_value = value if temp_value is None else temp_value
        self.category = category
        self.note = note
        self.editable = editable
        self.show_temp = show_temp
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create widgets
        self.name_label = QLabel(name)
        self.name_label.setMinimumWidth(100)
        self.value_spin = QSpinBox()
        self.value_spin.setRange(0, max_value)
        self.value_spin.setValue(value)
        self.dots_label = QLabel()
        self.dots_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dots_label.setMouseTracking(True)
        
        # Add widgets to layout
        layout.addWidget(self.name_label)
        if editable:
            layout.addWidget(self.value_spin)
        layout.addWidget(self.dots_label)
        layout.addStretch()
        
        # Connect signals
        self.value_spin.valueChanged.connect(self._on_value_changed)
        self.dots_label.mousePressEvent = self._on_dots_clicked
        self.dots_label.mouseReleaseEvent = self._on_dots_released
        self.dots_label.mouseMoveEvent = self._on_dots_hover
        self.dots_label.contextMenuEvent = self._on_context_menu
        
        # Initial update
        self._update_dots()
        
    def _on_value_changed(self, value: int) -> None:
        """Handle value spin box changes.
        
        Args:
            value: New trait value
        """
        self._value = value
        self._update_dots()
        self.value_changed.emit(value)
        
    def _on_dots_clicked(self, event: QMouseEvent) -> None:
        """Handle clicks on the dots display.
        
        Args:
            event: Mouse event
        """
        if not self.editable:
            return
            
        # Calculate which dot was clicked
        width = self.dots_label.width()
        dot_width = width / self.max_value
        position = event.position().x()
        dot_index = int(position / dot_width) + 1
        
        # Handle left click (permanent) or right click (temporary)
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle: If clicked on current value, decrease by 1
            if dot_index == self._value:
                self.set_value(dot_index - 1)
            else:
                self.set_value(dot_index)
        elif event.button() == Qt.MouseButton.RightButton and self.show_temp:
            # Set temporary value
            self.set_temp_value(dot_index)
    
    def _on_dots_released(self, event: QMouseEvent) -> None:
        """Handle mouse release on dots display.
        
        Args:
            event: Mouse event
        """
        # Placeholder for potential future functionality
        pass
        
    def _on_dots_hover(self, event: QMouseEvent) -> None:
        """Handle mouse hover on dots display.
        
        Args:
            event: Mouse event
        """
        if not self.editable:
            return
            
        # Show tooltip with trait information
        tooltip = f"{self.name}: {self._value}/{self.max_value}"
        if self.note:
            tooltip += f"\n{self.note}"
        if self.show_temp and self._temp_value != self._value:
            tooltip += f"\nTemporary: {self._temp_value}/{self.max_value}"
            
        QToolTip.showText(event.globalPosition().toPoint(), tooltip, self.dots_label)
    
    def _on_context_menu(self, event: QContextMenuEvent) -> None:
        """Handle context menu request.
        
        Args:
            event: Context menu event
        """
        if not self.editable:
            return
            
        menu = QMenu(self)
        
        # Reset action
        reset_action = QAction("Reset to Zero", self)
        reset_action.triggered.connect(lambda: self.set_value(0))
        menu.addAction(reset_action)
        
        # Maximize action
        max_action = QAction(f"Set to Maximum ({self.max_value})", self)
        max_action.triggered.connect(lambda: self.set_value(self.max_value))
        menu.addAction(max_action)
        
        if self.show_temp:
            # Separator
            menu.addSeparator()
            
            # Reset temp action
            reset_temp_action = QAction("Reset Temporary", self)
            reset_temp_action.triggered.connect(lambda: self.set_temp_value(self._value))
            menu.addAction(reset_temp_action)
            
            # Synchronize action
            sync_action = QAction("Set Permanent to Temporary", self)
            sync_action.triggered.connect(lambda: self.set_value(self._temp_value))
            menu.addAction(sync_action)
        
        menu.exec(event.globalPos())
        
    def _update_dots(self) -> None:
        """Update the dots display based on current values."""
        # Update spinner if available
        if self.editable and self.value_spin.value() != self._value:
            self.value_spin.setValue(self._value)
        
        # Create the dot display text
        if self.show_temp and self._temp_value != self._value:
            # Show both permanent and temporary values
            perm_dots = "●" * self._value + "○" * (self.max_value - self._value)
            temp_dots = "◐" * self._temp_value + "○" * (self.max_value - self._temp_value)
            self.dots_label.setText(f"{perm_dots} ({temp_dots})")
        else:
            # Show only permanent values
            dots = "●" * self._value + "○" * (self.max_value - self._value)
            self.dots_label.setText(dots)
        
    def get_values(self) -> Tuple[int, int]:
        """Get the current trait values.
        
        Returns:
            Tuple containing (permanent_value, temporary_value)
        """
        return (self._value, self._temp_value)
    
    def get_value(self) -> int:
        """Get the current permanent trait value.
        
        Returns:
            Current value of the trait
        """
        return self._value
    
    def get_temp_value(self) -> int:
        """Get the current temporary trait value.
        
        Returns:
            Current temporary value of the trait
        """
        return self._temp_value
    
    def set_value(self, value: int) -> None:
        """Set the permanent trait value.
        
        Args:
            value: New value for the trait
        """
        value = max(0, min(value, self.max_value))
        if value != self._value:
            self._value = value
            self._update_dots()
            self.value_changed.emit(value)
        
    def set_temp_value(self, value: int) -> None:
        """Set the temporary trait value.
        
        Args:
            value: New temporary value for the trait
        """
        value = max(0, min(value, self.max_value))
        if value != self._temp_value:
            self._temp_value = value
            self._update_dots()
            self.temp_value_changed.emit(value)
            
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the trait widget.
        
        Args:
            enabled: Whether the widget should be enabled
        """
        self.editable = enabled
        if hasattr(self, 'value_spin'):
            self.value_spin.setEnabled(enabled) 
            
    def set_show_temp(self, show_temp: bool) -> None:
        """Set whether to show temporary values.
        
        Args:
            show_temp: Whether to show temporary values
        """
        self.show_temp = show_temp
        self._update_dots()
        
    def set_name(self, name: str) -> None:
        """Set the trait name.
        
        Args:
            name: New name for the trait
        """
        self.name = name
        self.name_label.setText(name)
        
    def set_note(self, note: str) -> None:
        """Set the trait note/description.
        
        Args:
            note: New note for the trait
        """
        self.note = note 