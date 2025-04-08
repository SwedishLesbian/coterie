# Coterie UI Components

This document provides an overview of the UI components used in Coterie, their functionality, and implementation details.

## Main Application Window

The main window (`main_window.py`) serves as the primary container for the application and includes:

- Menu bar with application actions
- Tabbed interface for different views (Characters, Chronicle, etc.)
- Status bar for application state information
- Toolbar for common actions

## Dialogs

### Character Creation Dialog

Located in `ui/dialogs/character_creation.py`, this dialog guides users through creating a new character with:

- Character type selection (Vampire, Werewolf, etc.)
- Basic information input (Name, Player, etc.)
- Character template selection
- Initial attribute assignment

### Import Dialog

Located in `ui/dialogs/import_dialog.py`, this dialog facilitates importing data from the original Grapevine application:

- Supports both Grapevine 3.x character files (.gvc) and exported character files (.gex)
- File selection interface for both formats
- Character selection with filtering options
- Game data import options
- Progress tracking for import operations

### Planned Dialogs

The following dialogs are planned but not yet implemented:

- **Experience Dialog**: For managing character experience points
- **Preferences Dialog**: For application settings
- **About Dialog**: Application information and credits
- **Plot Dialog**: For managing chronicle plots
- **Rumor Dialog**: For managing rumors in a chronicle
- **Chronicle Dialog**: For managing chronicle details

## Character Sheets

Character sheets provide the interface for viewing and editing character information. Each supernatural type has its own specialized sheet:

- **Base Sheet** (`ui/sheets/base_sheet.py`): Common functionality for all sheets
- **Vampire Sheet** (`ui/sheets/vampire_sheet.py`): Vampire-specific sheet

### Planned Sheets

- Werewolf Sheet
- Mage Sheet
- Wraith Sheet
- Changeling Sheet
- Hunter Sheet
- Demon Sheet
- Mortal Sheet

## Custom Widgets

### Trait Widgets

Specialized widgets for displaying and editing character traits:

- **TraitDot**: Individual dot for a trait value
- **TraitWidget**: Complete widget with label and dots
- **TraitTable**: Table of related traits (e.g., Attributes)

### Other Widgets

- **CharacterList**: List of available characters
- **FilterBar**: UI for filtering character lists
- **StatusWidget**: Character status overview

## UI Patterns

The Coterie UI follows these key patterns:

1. **Separation of UI and Logic**: UI components delegate to business logic
2. **Composable Widgets**: Complex UIs built from reusable components
3. **Signal/Slot Pattern**: Qt's event system for communication
4. **Responsive Layout**: Use of layouts for adaptable UI
5. **Consistent Styling**: Unified look and feel

## Widget Hierarchy

```
MainWindow
├── MenuBar
├── TabWidget
│   ├── CharactersTab
│   │   ├── CharacterList
│   │   ├── FilterBar
│   │   └── CharacterSheet (various)
│   ├── ChronicleTab
│   └── GameTab
└── StatusBar
```

## Dialog Implementation

Dialogs follow this standard implementation pattern:

1. Inherit from QDialog
2. Define layout and widgets in `__init__`
3. Connect signals to slots
4. Implement validation methods
5. Create public methods for accessing dialog data
6. Emit custom signals for important events

## Styling

The application uses Qt stylesheets for consistent styling:

- Dark/light theme support
- Consistent colors and fonts
- Custom styling for specialized widgets (e.g., TraitWidget)

## Accessibility

UI components are designed with accessibility in mind:

- Keyboard navigation
- Screen reader compatibility
- Adequate contrast
- Scalable UI elements

## Future UI Enhancements

Planned improvements to the UI:

- Web-based interface option
- Mobile-responsive design
- Customizable themes
- Accessibility improvements
- Localization support 