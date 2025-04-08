# Coterie Technical Documentation

## Development Environment

### Requirements
- Python 3.8 or higher
- pip/virtualenv
- Git
- SQLite 3

### Setup
1. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Initialize database:
   ```bash
   python -m coterie
   ```

## Code Style & Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Black for code formatting
- Flake8 for linting
- Maximum line length: 88 characters (Black default)

### Documentation
- Docstrings follow PEP 257
- Google docstring style
- Module-level docstrings required
- Function/method docstrings required for public APIs

### Naming Conventions
- Classes: PascalCase
- Functions/Methods: snake_case
- Variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Private members: _leading_underscore

## Design Patterns

### Model-View Separation
- Models (`models/`): Data structures and business logic
- Views (`ui/`): User interface components
- Controllers: UI event handlers and business logic coordination

### Database Patterns
- Repository pattern for data access
- Unit of Work pattern via SQLAlchemy sessions
- Identity Map pattern (provided by SQLAlchemy)

### UI Patterns
- Composite pattern for UI components
- Observer pattern for event handling
- Factory pattern for character creation
- Strategy pattern for character type-specific behavior

## Data Files

### JSON Data Structure
Static game data is stored in JSON files in the `data/` directory. This includes:

- `attributes.json`: Physical, social, and mental attributes
- `abilities.json`: Talents, skills, and knowledges
- `backgrounds.json`: Character backgrounds
- `disciplines.json`: Vampire disciplines and clan associations
- `clans.json`: Vampire clans
- `natures.json`: Character natures
- `demeanors.json`: Character demeanors
- `paths.json`: Paths of enlightenment

### JSON Format
Each data file follows a consistent structure:
```json
{
    "category1": [
        "Item1",
        "Item2"
    ],
    "category2": [
        "Item3",
        "Item4"
    ],
    "descriptions": {
        "Item1": "Description for Item1",
        "Item2": "Description for Item2"
    }
}
```

### Data Loading
Data from JSON files is loaded at application startup and cached for performance. Changes to these files require an application restart to take effect.

## Database Schema

### Core Tables
- characters
- traits
- disciplines
- rituals
- bonds
- chronicles
- plots
- rumors

### Relationships
- One-to-many: Character -> Traits
- One-to-many: Character -> Disciplines
- Many-to-many: Character <-> Chronicles

## UI Component Library

### Custom Widgets
- TraitWidget: Displays trait with dots
- TraitTable: Table of character traits
- CharacterSheet: Base character sheet
- VampireSheet: Vampire-specific sheet

### Dialog Windows
- CharacterCreationDialog
- ImportDialog
- ExperienceDialog
- PlotDialog
- RumorDialog

## Testing

### Test Structure
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- UI tests in `tests/ui/`

### Test Tools
- pytest for test running
- pytest-qt for UI testing
- pytest-cov for coverage
- pytest-mock for mocking

### Test Guidelines
- Test all public APIs
- Mock external dependencies
- Aim for 80%+ coverage
- Include regression tests

## Error Handling

### Exception Hierarchy
```python
CoterieError
├── DatabaseError
├── ValidationError
├── CharacterError
└── UIError
```

### Logging
- Use Python's logging module
- Log levels:
  - DEBUG: Development info
  - INFO: Normal operations
  - WARNING: Potential issues
  - ERROR: Operation failures
  - CRITICAL: Application failures

## Performance Considerations

### Database
- Lazy loading relationships
- Batch operations where possible
- Index frequently queried columns
- Regular VACUUM operations

### UI
- Lazy widget creation
- Resource cleanup
- Background processing for long operations
- Pagination for large datasets

## Security

### Data Protection
- SQLite database in user's app directory
- File permissions set appropriately
- No sensitive data in logs
- Secure deletion of temporary files

### Input Validation
- Sanitize all user input
- Validate data types and ranges
- Prevent SQL injection via ORM
- Handle file paths securely

## Deployment

### Application Structure
```
<user_app_data>/
└── Coterie/
    ├── coterie.db
    ├── coterie.log
    └── backups/
```

### Distribution
- PyPI package
- Windows installer
- Linux package
- macOS package

## Version Control

### Branch Strategy
- main: Stable releases
- develop: Development branch
- feature/*: Feature branches
- bugfix/*: Bug fix branches
- release/*: Release branches

### Commit Guidelines
- Conventional Commits format
- Include issue references
- Keep commits focused
- Write clear messages

## Maintenance

### Backup Strategy
- Automatic database backups
- User-triggered backups
- Backup rotation
- Backup verification

### Updates
- Check for updates on startup
- Automatic database migrations
- Configuration updates
- Preserve user settings

## Mind's Eye Theater LARP Trait System

Coterie is designed specifically for Mind's Eye Theater LARP character management, which uses a fundamentally different trait system than the tabletop World of Darkness games. Understanding this system is critical for developers working on the project.

### LARP vs. Tabletop Trait Systems

#### LARP Adjective-Based System:
- Characters are defined by collections of **descriptive adjective traits** (e.g., "Ferocious", "Intimidating", "Clever")
- Traits are organized into categories (Physical, Social, Mental, etc.)
- Tests are resolved by comparing appropriate traits between characters or against difficulty challenges
- The number of traits a character possesses in a category represents their overall capability in that area
- Players select specific traits that best describe their character's abilities and weaknesses
- Negative traits represent weaknesses that can be exploited by opponents

#### Tabletop Dot-Based System:
- Characters have attributes, abilities, disciplines, etc. rated from 1-5 dots
- Ratings represent numeric values for character capabilities
- Dice pools are formed based on these ratings
- Tests are resolved by rolling dice equal to the combined value of relevant attributes+abilities

### Implementation in Coterie

For Coterie, we exclusively implement the LARP adjective-based system:

1. **Trait Storage**: 
   - Traits are stored as collections of string adjectives, not numeric ratings
   - Categories (Physical, Social, Mental) each have their own collections of traits
   - Additional trait types include Abilities, Backgrounds, Influences, etc.
   - Negative traits are stored separately but linked to their categories

2. **Trait Selection**:
   - Character creation and advancement allows selection from predefined trait lists
   - Custom traits can be added with Storyteller approval
   - The focus is on which traits are selected, not how many "points" are spent

3. **Trait Testing System**:
   - Implementation of the Mind's Eye Theater challenge resolution system
   - Support for trait bidding, challenges, and retests
   - Proper handling of negating, cancelling, and spending traits

4. **UI Representation**:
   - Traits are displayed as lists of adjectives
   - Simple ways to add/remove/edit traits for character management
   - Clear distinction between permanent, temporary, and spent traits
   - Visual indicators for negative traits

### Technical Considerations

- Trait adjectives must be stored as strings, not numeric values
- Character models need a different data structure to accommodate trait collections
- UI widgets must be optimized for selecting from adjective lists and managing trait collections
- Import/export functionality needs to preserve the specific trait adjectives
- The system must track which traits are spent during gameplay

### Trait Categories

The typical trait organization in Mind's Eye Theater includes:

1. **Physical Traits**: Such as "Athletic", "Nimble", "Swift", "Robust"
2. **Social Traits**: Such as "Charismatic", "Eloquent", "Charming", "Persuasive"
3. **Mental Traits**: Such as "Perceptive", "Intuitive", "Clever", "Analytical"
4. **Negative Traits**: Including "Clumsy", "Repugnant", "Forgetful" for each category
5. **Abilities**: Talents, Skills, and Knowledges with appropriate descriptive traits
6. **Backgrounds**: Represented as descriptive qualities
7. **Disciplines and Powers**: Represented with suitable adjectives for vampire abilities

### Character Testing Mechanics

In Mind's Eye Theater, characters test against each other by:
1. Each player bids a relevant trait
2. The traits are compared or a randomizer (such as rock-paper-scissors) is used
3. The winner succeeds at the action
4. Traits can be spent (used up for the session) for retests or special effects
5. Negative traits can be called by opponents to negate positive traits

## Conversion Guidelines

When importing from .gvc or .gex files that might have used a different system:
- Convert each dot rating to an appropriate number of adjective traits
- Maintain the character's core concept and capabilities
- Follow Mind's Eye Theater conversion rules as outlined in the rulebook 