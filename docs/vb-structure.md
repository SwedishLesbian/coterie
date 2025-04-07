# Grapevine 3.01 Visual Basic Source Structure

This document outlines the structure of the original Grapevine 3.01 Visual Basic source code to aid in the conversion process to Python.

## Overview

Grapevine was originally written in Visual Basic 6.0 using a form-based approach with classes for business logic. The application used a proprietary file format rather than a database for data storage.

## File Organization

### Forms (UI)

#### Main Forms
- **frmMain.frm** - Main application window
- **frmNewCharacter.frm** - Character creation dialog
- **frmOptions.frm** - Application options and preferences
- **frmAbout.frm** - About dialog with version information

#### Character Sheets
- **frmVampire.frm** - Vampire: The Masquerade character sheet
- **frmWerewolf.frm** - Werewolf: The Apocalypse character sheet
- **frmMage.frm** - Mage: The Ascension character sheet
- **frmWraith.frm** - Wraith: The Oblivion character sheet
- **frmChangeling.frm** - Changeling: The Dreaming character sheet
- **frmHunter.frm** - Hunter: The Reckoning character sheet
- **frmDemon.frm** - Demon: The Fallen character sheet
- **frmMummy.frm** - Mummy: The Resurrection character sheet
- **frmMortal.frm** - Mortal character sheet

#### Game Tools
- **frmExperience.frm** - Experience point tracking
- **frmChronicle.frm** - Chronicle management
- **frmPlot.frm** - Plot management
- **frmRumor.frm** - Rumor management

### Classes (Business Logic)

#### Character Classes
- **clsCharacter.cls** - Base character class
- **clsVampire.cls** - Vampire character class
- **clsWerewolf.cls** - Werewolf character class
- **clsMage.cls** - Mage character class
- **clsWraith.cls** - Wraith character class
- **clsChangeling.cls** - Changeling character class
- **clsHunter.cls** - Hunter character class
- **clsDemon.cls** - Demon character class
- **clsMummy.cls** - Mummy character class

#### Game Systems
- **clsExperience.cls** - Experience point management
- **clsChronicle.cls** - Chronicle management
- **clsPlot.cls** - Plot management
- **clsRumor.cls** - Rumor management

### Modules (Utilities)

- **modGlobal.bas** - Global variables and constants
- **modUtility.bas** - Utility functions
- **modFileIO.bas** - File input/output operations
- **modDatabase.bas** - Data access functions

## UI Structure

### Main Window
The main window (`frmMain`) was structured with:
- Menu system
- Toolbar
- Status bar
- Character list
- Tab control for character sheets, plots, and rumors

### Character Sheets
Character sheets were individual forms with:
- Attributes section
- Abilities section
- Advantages section
- Character-specific sections (Disciplines for Vampires, Gifts for Werewolves, etc.)
- Backgrounds
- Merits/Flaws
- Notes/History section

## Data Model

### Character
- General information (name, player, etc.)
- Attributes (Physical, Social, Mental)
- Abilities (Talents, Skills, Knowledges)
- Advantages (type-specific)
- Willpower, Health
- Experience points
- Notes, history, etc.

### Type-Specific Data
- **Vampire**: Clan, Generation, Blood Pool, Disciplines, etc.
- **Werewolf**: Breed, Auspice, Tribe, Rage, Gnosis, etc.
- **Mage**: Tradition, Arete, Spheres, Paradox, etc.
- **Wraith**: Guild, Legion, Corpus, Pathos, etc.
- **Changeling**: Kith, Seeming, Glamour, Banality, etc.

### Chronicle
- Name, description
- Storyteller
- Associated characters
- Plots
- Rumors

## File Format

Grapevine used a custom binary file format with:
- Character data
- Chronicle data
- Plot/Rumor data
- Relationships between entities

## Key Challenges for Conversion

1. **Form to Component Translation**:
   - VB forms were self-contained UI units
   - Need to convert to component-based PyQt architecture

2. **Event Handling**:
   - VB used event handlers directly in forms
   - Need to implement proper signal-slot mechanism in PyQt

3. **File Format to Database**:
   - Convert custom binary format to SQLite database
   - Implement migration path for existing files

4. **Global State Management**:
   - VB used global variables extensively
   - Need to implement proper state management

5. **UI Layout Differences**:
   - VB had visual form designer
   - Need to recreate layouts in PyQt

6. **Control Differences**:
   - Many VB controls have no direct PyQt equivalent
   - Custom widgets needed for some components (e.g., trait dots)

7. **Type System**:
   - VB used looser typing
   - Python implementation uses type hints and proper inheritance 