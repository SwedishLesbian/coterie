# Grapevine 4.0 Architecture

## Overview

Grapevine 4.0 is a modern Python port of the original Grapevine character management system. The application follows a layered architecture with clear separation of concerns between the data, business logic, and presentation layers.

## Core Components

### 1. Data Layer

#### Database
- SQLite database using SQLAlchemy ORM
- Located in user's application data directory
- Alembic for database migrations
- Models defined in `grapevine/models/`

#### Data Models
- Base character model with common attributes
- Specialized models for each character type (Vampire, Werewolf, etc.)
- Trait system for character attributes and abilities
- Support models for chronicles, plots, and rumors

### 2. Business Logic Layer

#### Core Logic (`grapevine/core/`)
- Character creation and management
- Experience point calculations
- Game mechanics implementation
- Data validation and business rules

#### Utilities (`grapevine/utils/`)
- Common helper functions
- Data conversion utilities
- Configuration management
- Logging setup

### 3. Presentation Layer

#### User Interface (`grapevine/ui/`)
- Modern PyQt6-based interface
- Main window with tabbed interface
- Character sheets
- Dialog windows
- Custom widgets

Component hierarchy:
```
MainWindow
├── MenuBar
├── ToolBar
├── StatusBar
└── TabWidget
    ├── CharactersTab
    ├── ChronicleTab
    ├── PlotsTab
    └── RumorsTab
```

## Data Flow

1. User interactions trigger UI events
2. UI components call business logic methods
3. Business logic performs operations through data layer
4. Data layer handles persistence
5. Results propagate back through the layers
6. UI updates to reflect changes

## Key Design Decisions

1. **Modern Python Features**
   - Type hints throughout the codebase
   - Dataclasses for data structures
   - Modern Python packaging (pyproject.toml)

2. **Database Design**
   - SQLite for portability
   - SQLAlchemy for ORM
   - Alembic for migrations
   - JSON for flexible data storage

3. **UI Architecture**
   - PyQt6 for modern interface
   - Separation of UI and logic
   - Custom widgets for reusability
   - Responsive design

4. **Future Expansion**
   - Web interface capability
   - API-first design
   - Modular character type system
   - Plugin architecture for house rules

## Directory Structure

```
grapevine/
├── core/           # Business logic
├── database/       # Database configuration and migrations
├── models/         # SQLAlchemy models
├── ui/            # User interface components
│   ├── dialogs/   # Dialog windows
│   ├── sheets/    # Character sheets
│   └── widgets/   # Reusable widgets
└── utils/         # Utility functions
```

## Dependencies

- **Database**: SQLAlchemy, Alembic
- **UI**: PyQt6
- **Utilities**: python-dotenv, PyYAML
- **Development**: mypy, black, flake8

## Security Considerations

1. **Data Storage**
   - SQLite database in user's app data directory
   - No hardcoded credentials
   - Environment variables for configuration

2. **Input Validation**
   - All user input validated
   - SQL injection prevention via ORM
   - Type checking throughout

3. **File Operations**
   - Safe file handling
   - Proper error handling
   - Backup functionality

## Future Considerations

1. **Web Interface**
   - Flask/FastAPI backend
   - Modern frontend (React/Vue)
   - API-first design

2. **Multi-User Support**
   - User authentication
   - Role-based access control
   - Shared chronicles

3. **Data Exchange**
   - Import/Export functionality
   - Standard format support
   - Cloud synchronization 