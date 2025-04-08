# Coterie Conversion Guide

This guide provides detailed instructions and best practices for developers working on the conversion of Grapevine from Visual Basic to Python.

## Conversion Approach

### Principles

1. **Progressive Conversion**
   - Convert one component at a time
   - Ensure each component works before moving to the next
   - Focus on core functionality first, then edge cases

2. **Architectural Improvements**
   - Don't simply translate VB to Python
   - Improve architecture where appropriate
   - Use modern Python patterns and features

3. **Documentation First**
   - Document the VB component behavior before conversion
   - Define the Python component interface
   - Update documentation as you convert

## Step-by-Step Conversion Process

### 1. Component Analysis

For each VB component:

1. **Identify Purpose**
   - What does this component do?
   - What business logic does it implement?
   - What UI elements does it contain?

2. **Identify Dependencies**
   - What other components does it use?
   - What global state does it access?
   - What events does it handle?

3. **Identify Data Flow**
   - How does data enter the component?
   - How does the component transform data?
   - How does data exit the component?

### 2. Architecture Design

1. **Model Design**
   - Design SQLAlchemy models to replace VB classes
   - Define relationships between models
   - Implement type hints

2. **UI Component Design**
   - Design PyQt components to replace VB forms
   - Define component hierarchy
   - Define signals and slots (to replace VB events)

3. **Business Logic Design**
   - Design service classes to replace VB business logic
   - Define clear interfaces
   - Separate concerns

### 3. Implementation

1. **Create Model Classes**
   - Implement SQLAlchemy models
   - Add validation
   - Write unit tests

2. **Create UI Components**
   - Implement PyQt components
   - Connect signals and slots
   - Test with mock data

3. **Implement Business Logic**
   - Create service classes
   - Connect to models and UI
   - Test end-to-end

### 4. Testing and Refinement

1. **Test Against VB Version**
   - Compare behavior with original VB version
   - Verify data compatibility
   - Document differences

2. **Refine Implementation**
   - Fix bugs
   - Improve performance
   - Enhance usability

3. **Document Component**
   - Update API documentation
   - Add usage examples
   - Document design decisions

## VB to Python Mapping

### Form Controls to PyQt Widgets

| VB Control     | PyQt Widget              | Notes                                |
|----------------|--------------------------|--------------------------------------|
| Form           | QWidget/QMainWindow      | Top-level window                     |
| CommandButton  | QPushButton              | Standard button                      |
| TextBox        | QLineEdit/QTextEdit      | Single/multi-line text input         |
| Label          | QLabel                   | Static text                          |
| ComboBox       | QComboBox                | Dropdown list                        |
| ListBox        | QListWidget              | Selectable list                      |
| CheckBox       | QCheckBox                | Boolean option                       |
| OptionButton   | QRadioButton             | Mutually exclusive option            |
| Frame          | QGroupBox/QFrame         | Visual grouping                      |
| TabStrip       | QTabWidget               | Tabbed interface                     |
| ScrollBar      | QScrollBar               | Scrolling control                    |
| PictureBox     | QLabel/QGraphicsView     | Image display                        |
| Timer          | QTimer                   | Timed events                         |
| Menu           | QMenu/QMenuBar           | Application menus                    |
| StatusBar      | QStatusBar               | Status information                   |

### VB Events to PyQt Signals/Slots

| VB Event       | PyQt Signal/Slot         | Notes                                |
|----------------|--------------------------|--------------------------------------|
| Click          | clicked()                | Mouse click                          |
| DblClick       | doubleClicked()          | Mouse double-click                   |
| KeyPress       | keyPressed()             | Keyboard input                       |
| Change         | textChanged()/valueChanged() | Control value changed           |
| Load           | Constructor/showEvent()  | Form initialization                  |
| Unload         | closeEvent()             | Form closing                         |
| GotFocus       | focusInEvent()           | Control received focus               |
| LostFocus      | focusOutEvent()          | Control lost focus                   |
| MouseMove      | mouseMoveEvent()         | Mouse movement                       |
| Resize         | resizeEvent()            | Window resized                       |

### VB Data Types to Python Types

| VB Type        | Python Type             | Notes                                 |
|----------------|-------------------------|---------------------------------------|
| Integer        | int                     | Integer value                         |
| Long           | int                     | Long integer                          |
| Single/Double  | float                   | Floating-point number                 |
| String         | str                     | Text string                           |
| Boolean        | bool                    | True/False value                      |
| Date           | datetime.date/datetime  | Date/time value                       |
| Object         | object                  | Generic object                        |
| Variant        | Any (from typing)       | Type-variable object                  |
| Array          | list/tuple              | Collection of values                  |
| Collection     | list/dict               | Key/value collection                  |

## Examples

### VB Form to PyQt Class

**VB Form (frmExample.frm):**
```vb
' Form declaration
Begin VB.Form frmExample
   Caption         =   "Example Form"
   ClientHeight    =   3600
   ClientWidth     =   4800
   Begin VB.CommandButton cmdOK
      Caption         =   "OK"
      Height          =   375
      Left            =   3600
      TabIndex        =   1
      Top             =   3120
      Width           =   1095
   End
   Begin VB.TextBox txtName
      Height          =   375
      Left            =   1200
      TabIndex        =   0
      Top             =   360
      Width           =   3495
   End
   Begin VB.Label lblName
      Caption         =   "Name:"
      Height          =   255
      Left            =   120
      TabIndex        =   2
      Top             =   360
      Width           =   975
   End
End

' Event handlers
Private Sub cmdOK_Click()
    MsgBox "Hello, " & txtName.Text & "!"
End Sub

Private Sub Form_Load()
    txtName.Text = "World"
End Sub
```

**Python PyQt Equivalent:**
```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt

class ExampleDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("Example Form")
        self.resize(480, 360)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Name input
        name_layout = QHBoxLayout()
        self.lbl_name = QLabel("Name:")
        self.txt_name = QLineEdit("World")  # Initial value like Form_Load
        name_layout.addWidget(self.lbl_name)
        name_layout.addWidget(self.txt_name)
        layout.addLayout(name_layout)
        
        # Add stretch to push button to bottom
        layout.addStretch()
        
        # OK button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.on_ok_clicked)  # Connect signal to slot
        button_layout.addWidget(self.btn_ok)
        layout.addLayout(button_layout)
    
    def on_ok_clicked(self):
        # Equivalent to cmdOK_Click
        QMessageBox.information(
            self, 
            "Greeting", 
            f"Hello, {self.txt_name.text()}!"
        )
```

### VB Class to Python SQLAlchemy Model

**VB Class (clsExample.cls):**
```vb
' Class declaration
Option Explicit

' Properties
Private m_ID As Long
Private m_Name As String
Private m_Value As Double

' Property accessors
Public Property Get ID() As Long
    ID = m_ID
End Property

Public Property Let ID(ByVal newID As Long)
    m_ID = newID
End Property

Public Property Get Name() As String
    Name = m_Name
End Property

Public Property Let Name(ByVal newName As String)
    m_Name = newName
End Property

Public Property Get Value() As Double
    Value = m_Value
End Property

Public Property Let Value(ByVal newValue As Double)
    m_Value = newValue
End Property

' Methods
Public Sub Save()
    ' Save to database
End Sub

Public Sub Load(ByVal ID As Long)
    ' Load from database
End Sub
```

**Python SQLAlchemy Equivalent:**
```python
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class Example(Base):
    """Example model equivalent to clsExample in VB."""
    __tablename__ = "examples"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    
    def __init__(self, name: str = "", value: float = 0.0):
        """Initialize example with optional values."""
        self.name = name
        self.value = value
    
    @classmethod
    def load(cls, session, id: int) -> "Example":
        """Load example by ID."""
        return session.query(cls).filter(cls.id == id).first()
    
    def save(self, session) -> None:
        """Save example to database."""
        session.add(self)
        session.commit()
```

## Common Conversion Challenges

### 1. UI Layout Conversion

VB forms used absolute positioning while PyQt uses layouts. Convert VB forms to PyQt by:

1. Identify logical groupings of controls
2. Create layout containers for each group
3. Arrange layouts hierarchically
4. Use spacers and stretches for alignment

### 2. Event Model Conversion

VB used direct event handlers while PyQt uses signals and slots. Convert by:

1. Identify VB events
2. Find equivalent PyQt signals
3. Create slot methods
4. Connect signals to slots

### 3. Data Binding Conversion

VB often bound controls directly to data. Convert by:

1. Create properties/methods to access model data
2. Update UI from model in load methods
3. Update model from UI in save methods
4. Implement validation

### 4. Global State Conversion

VB often used global variables. Convert by:

1. Identify global state
2. Create appropriate service classes
3. Use dependency injection
4. Consider application-level state management

## Tips and Best Practices

1. **Start with Core Models**
   - Convert data models first
   - Focus on database schema and ORM models
   - Test thoroughly before UI conversion

2. **Use Python Idioms**
   - Don't write VB-style code in Python
   - Use list comprehensions, generators, etc.
   - Use proper Python naming conventions

3. **Leverage Type Hints**
   - Add type hints to all functions and methods
   - Use mypy for static type checking
   - Document parameter and return types

4. **Build UI Incrementally**
   - Start with basic layouts
   - Add functionality one component at a time
   - Test with real data frequently

5. **Document Decisions**
   - Document why you made each conversion choice
   - Note deviations from the original design
   - Update documentation as you progress 