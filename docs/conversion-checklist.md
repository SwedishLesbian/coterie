# Conversion Checklist

This document tracks the progress of converting features from Grapevine 3.x to Coterie.

## Core Infrastructure

- [x] Project structure
- [x] Database design
- [x] Basic UI framework
- [x] Settings system
- [ ] Plugin architecture

## Character Management

- [x] Character creation dialog
- [x] Basic character model
- [ ] Character sheet UI base
- [x] Import dialog for Grapevine 3.x (.gvc) and .gex files
- [ ] Export functionality
- [ ] Character list view

## Data Models

### Base Models
- [x] Character base class
- [x] Trait system
- [ ] XP tracking system
- [ ] Notes system

### Character Types
- [x] Vampire model
- [ ] Werewolf model
- [ ] Mage model
- [ ] Wraith model
- [ ] Changeling model
- [ ] Hunter model
- [ ] Demon model
- [ ] Mummy model
- [ ] Mortal model

### Game Systems
- [ ] Chronicle model
- [ ] Plot model
- [ ] Rumor model
- [ ] Relationship model

## User Interface Components

### Core UI
- [x] Main window
- [x] Menu system
- [x] Toolbar
- [x] Status bar
- [x] Tab system

### Dialogs
- [x] Character creation dialog
- [ ] Experience dialog
- [ ] Preferences dialog
- [ ] About dialog
- [ ] Plot dialog
- [ ] Rumor dialog
- [ ] Chronicle dialog
- [x] Import dialog

### Character Sheets
- [x] Vampire sheet
- [ ] Werewolf sheet
- [ ] Mage sheet
- [ ] Wraith sheet
- [ ] Changeling sheet
- [ ] Hunter sheet
- [ ] Demon sheet
- [ ] Mummy sheet
- [ ] Mortal sheet

### Widgets
- [x] Trait dot widget
- [x] Trait group widget
- [ ] Character list widget
- [ ] XP history widget
- [ ] Notes widget
- [ ] Discipline path widget

## Features

### Character Management
- [x] Basic character creation
- [ ] Character deletion
- [ ] Character editing
- [ ] Character sheet printing
- [ ] Character import/export

### Experience System
- [ ] XP tracking
- [ ] XP spending
- [ ] XP history

### Chronicle System
- [ ] Chronicle creation
- [ ] Chronicle management
- [ ] Character association

### Game Tools
- [ ] Plot management
- [ ] Rumor system
- [ ] Relationship tracking
- [ ] NPC management

## Testing

- [ ] Unit test framework
- [ ] Model tests
- [ ] UI tests
- [ ] Integration tests

## Documentation

### User Documentation
- [ ] Installation guide
- [ ] User manual
- [ ] Quick start guide
- [ ] FAQ

### Developer Documentation
- [x] Architecture overview
- [x] API documentation
- [x] Contributing guide
- [x] Conversion guide
- [x] JSON data structure documentation

## Distribution

- [ ] Package creation
- [ ] Windows installer
- [ ] macOS package
- [ ] Linux package

## Specific VB Form Conversions

### Main Screens
- [x] frmMain.frm → ui/main_window.py
- [x] frmNewCharacter.frm → dialogs/character_creation.py
- [x] frmVampire.frm → sheets/vampire_sheet.py
- [ ] frmWerewolf.frm → sheets/werewolf_sheet.py
- [ ] frmMage.frm → sheets/mage_sheet.py
- [ ] frmWraith.frm → sheets/wraith_sheet.py
- [ ] frmChangeling.frm → sheets/changeling_sheet.py
- [ ] frmHunter.frm → sheets/hunter_sheet.py
- [ ] frmDemon.frm → sheets/demon_sheet.py
- [ ] frmMortal.frm → sheets/mortal_sheet.py

### Utility Screens
- [ ] frmExperience.frm → dialogs/experience.py
- [ ] frmChronicle.frm → dialogs/chronicle.py
- [ ] frmPlot.frm → dialogs/plot.py
- [ ] frmRumor.frm → dialogs/rumor.py
- [ ] frmOptions.frm → dialogs/preferences.py
- [ ] frmAbout.frm → dialogs/about.py

### Business Logic
- [x] clsCharacter.cls → models/character.py
- [x] clsVampire.cls → models/vampire.py
- [ ] clsWerewolf.cls → models/werewolf.py
- [ ] clsMage.cls → models/mage.py
- [ ] clsWraith.cls → models/wraith.py
- [ ] clsChangeling.cls → models/changeling.py
- [ ] clsHunter.cls → models/hunter.py
- [ ] clsDemon.cls → models/demon.py
- [ ] clsMummy.cls → models/mummy.py
- [ ] clsExperience.cls → models/experience.py
- [ ] clsChronicle.cls → models/chronicle.py
- [ ] clsPlot.cls → models/plot.py
- [ ] clsRumor.cls → models/rumor.py

## Additional Features Not in Original

- [ ] Web interface
- [ ] Multi-user support
- [ ] Cloud synchronization
- [ ] Mobile companion app
- [ ] Dark mode
- [ ] Modern UI themes
- [ ] Rules integration
- [ ] Dice rolling system

### VB to Python File Conversion

- [x] frmMain.frm → ui/main_window.py
- [x] frmNewCharacter.frm → dialogs/character_creation.py
- [ ] frmVampire.frm → sheets/vampire_sheet.py
- [ ] frmWerewolf.frm → sheets/werewolf_sheet.py
- [ ] frmMage.frm → sheets/mage_sheet.py
- [ ] frmWraith.frm → sheets/wraith_sheet.py
- [ ] frmChangeling.frm → sheets/changeling_sheet.py
- [ ] frmHunter.frm → sheets/hunter_sheet.py
- [ ] frmDemon.frm → sheets/demon_sheet.py
- [ ] frmMortal.frm → sheets/mortal_sheet.py
- [ ] clsCharacter.cls → models/character.py
- [ ] clsVampire.cls → models/vampire.py
- [ ] clsWerewolf.cls → models/werewolf.py
- [ ] clsMage.cls → models/mage.py
- [ ] clsWraith.cls → models/wraith.py
- [ ] clsChangeling.cls → models/changeling.py
- [ ] clsHunter.cls → models/hunter.py
- [ ] frmExperience.frm → dialogs/experience.py
- [ ] frmChronicle.frm → dialogs/chronicle.py
- [ ] frmPlot.frm → dialogs/plot.py
- [ ] frmRumor.frm → dialogs/rumor.py
- [ ] frmOptions.frm → dialogs/preferences.py
- [ ] frmAbout.frm → dialogs/about.py
- [x] frmImport.frm → dialogs/import_dialog.py

## Trait System Conversion

- [x] Document Mind's Eye Theater LARP trait system in technical documentation
- [x] Create models for LARP trait system (`LarpTrait` and `TraitCategory`)
- [x] Implement UI widgets for adjective-based traits (`LarpTraitWidget`)
- [x] Create trait adjective data files and utilities
- [ ] Update character sheets to use LARP trait widgets
- [ ] Implement proper trait testing and bidding mechanics
- [ ] Add support for spending traits during gameplay
- [ ] Create proper trait filtering and selection in character creation

## Important Notes

1. **Mind's Eye Theater LARP vs. Tabletop**: Coterie exclusively supports the Mind's Eye Theater LARP system, which uses adjective-based traits rather than numeric ratings. The implementation must reflect this fundamental difference.

2. **Trait Handling**: Traits in LARP are collections of adjectives (not ratings) organized into categories. Proper handling includes:
   - Physical/Social/Mental trait collections
   - Negative traits for each category
   - Abilities as descriptive traits
   - Tracking spent traits during gameplay

3. **Testing System**: The challenge resolution system in LARP is based on trait bidding, not dice rolls. The implementation should allow for:
   - Trait selection during challenges
   - Comparing traits between characters
   - Challenge resolution mechanics
   - Trait retesting options 