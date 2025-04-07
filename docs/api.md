# Grapevine 4.0 API Documentation

## Core Modules

### Database Models

#### Character Base Class
```python
class Character:
    """Base class for all character types."""
    id: int  # Primary key
    name: str  # Character name
    player: str  # Player name
    status: str  # Character status (Active/Inactive)
```

#### Vampire Character
```python
class Vampire(Character):
    """Vampire: The Masquerade character type."""
    clan: str  # Character's clan
    generation: int  # Vampire generation (1-15)
    blood_pool: int  # Current blood pool
    willpower: int  # Current willpower
```

### Data Access Layer

#### Database Session
```python
def get_session() -> Session:
    """Get a database session."""
    return Session()

def commit_session(session: Session) -> None:
    """Commit and close a database session."""
    session.commit()
```

#### Character Repository
```python
class CharacterRepository:
    """Repository for character data access."""
    def get_character(id: int) -> Character:
        """Get character by ID."""
        
    def save_character(character: Character) -> None:
        """Save or update character."""
        
    def delete_character(id: int) -> None:
        """Delete character by ID."""
```

### UI Components

#### Trait Widget
```python
class TraitWidget(QWidget):
    """Widget for displaying and editing character traits."""
    value_changed = Signal(int)  # Emitted when trait value changes
    
    def __init__(self, name: str, max_value: int = 5):
        """Initialize trait widget."""
        
    def get_value(self) -> int:
        """Get current trait value."""
        
    def set_value(self, value: int) -> None:
        """Set trait value."""
```

#### Character Sheet
```python
class CharacterSheet(QWidget):
    """Base class for character sheets."""
    modified = Signal()  # Emitted when sheet is modified
    
    def load_character(self, character: Character) -> None:
        """Load character data into sheet."""
        
    def save_character(self) -> None:
        """Save sheet data to character."""
```

#### Vampire Sheet
```python
class VampireSheet(CharacterSheet):
    """Vampire character sheet."""
    def __init__(self):
        """Initialize vampire sheet."""
        
    def load_vampire(self, vampire: Vampire) -> None:
        """Load vampire data into sheet."""
        
    def save_vampire(self) -> None:
        """Save sheet data to vampire."""
```

## Event System

### Signals
- `character_created(character_id: int)`
- `character_modified(character_id: int)`
- `character_deleted(character_id: int)`
- `trait_changed(character_id: int, trait_name: str, value: int)`

### Event Handlers
```python
def on_character_modified(character_id: int) -> None:
    """Handle character modification events."""
    
def on_trait_changed(character_id: int, trait_name: str, value: int) -> None:
    """Handle trait change events."""
```

## Configuration

### Database Configuration
```python
class DatabaseConfig:
    """Database configuration."""
    path: str  # Database file path
    pool_size: int  # Connection pool size
    debug: bool  # Enable SQL debugging
```

### Application Configuration
```python
class AppConfig:
    """Application configuration."""
    theme: str  # UI theme (light/dark)
    window_size: tuple  # Default window size
    auto_save: bool  # Enable auto-save
```

## Utility Functions

### Data Validation
```python
def validate_character(character: Character) -> List[str]:
    """Validate character data."""
    return []  # List of validation errors

def validate_vampire(vampire: Vampire) -> List[str]:
    """Validate vampire data."""
    return []  # List of validation errors
```

### Data Import/Export
```python
def export_character(character: Character, format: str) -> str:
    """Export character data."""
    return ""  # Exported data

def import_character(data: str, format: str) -> Character:
    """Import character data."""
    return Character()
```

## Error Handling

### Custom Exceptions
```python
class CharacterError(Exception):
    """Base class for character-related errors."""
    pass

class ValidationError(CharacterError):
    """Validation error."""
    pass

class DatabaseError(CharacterError):
    """Database operation error."""
    pass
```

## Type Definitions

### Common Types
```python
Trait = Dict[str, int]  # Trait name to value mapping
Stats = Dict[str, int]  # Stat name to value mapping
Abilities = Dict[str, int]  # Ability name to value mapping
```

## Usage Examples

### Creating a Character
```python
# Create new vampire
vampire = Vampire(
    name="Marcus",
    player="John",
    clan="Ventrue",
    generation=12
)

# Save to database
repo = CharacterRepository()
repo.save_character(vampire)
```

### Displaying Character Sheet
```python
# Create and show sheet
sheet = VampireSheet()
sheet.load_vampire(vampire)
sheet.show()
```

### Handling Events
```python
# Connect to signals
sheet.modified.connect(on_character_modified)
sheet.trait_changed.connect(on_trait_changed)
``` 