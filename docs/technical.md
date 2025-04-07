# Grapevine 4.0 Technical Documentation

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
   python -m grapevine
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
GrapevineError
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
└── Grapevine/
    ├── grapevine.db
    ├── grapevine.log
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