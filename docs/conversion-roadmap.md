# Coterie Conversion Roadmap

## Overview

This document outlines the process and progress of converting the original Visual Basic Grapevine application (version 3.01) to the modern Python-based Coterie application. It serves as a guide for the conversion process, tracking completed work and identifying upcoming tasks.

## Conversion Strategy

1. **Platform and Technology Selection**
   - Python 3.8+ as the base language (✓ Completed)
   - SQLAlchemy for database management (✓ Completed)
   - PyQt6 for the user interface (✓ Completed)
   - Alembic for database migrations (✓ Completed)

2. **Architectural Changes**
   - Implement proper layered architecture (✓ Started)
   - Move from form-based design to component-based design (✓ Started)
   - Implement ORM pattern for data access (✓ Completed)
   - Add type hints throughout the codebase (✓ Started)

3. **Data Model Conversion**
   - Base character model (✓ Completed)
   - Vampire character model (✓ Completed)
   - Trait system (✓ Completed)
   - Remaining character types (⏳ Not Started)
   - Chronicle model (⏳ Not Started)
   - Plot and rumor models (⏳ Not Started)

## Current Progress

### Completed Components

1. **Project Setup**
   - Project structure and organization (✓)
   - Development environment configuration (✓)
   - Package management (✓)
   - Database configuration (✓)

2. **Data Layer**
   - SQLAlchemy integration (✓)
   - Base character model (✓)
   - Vampire character model (✓)
   - Trait system foundation (✓)

3. **UI Components**
   - Main window implementation (✓)
   - Character creation dialog (✓)
   - Basic tab interface (✓)

### In Progress

1. **UI Components**
   - Character sheet implementation (⏳)
   - Trait widgets (⏳)
   - Experience point tracking (⏳)

2. **Business Logic**
   - Character creation workflow (⏳)
   - Data validation (⏳)

### Not Started

1. **Data Layer**
   - Additional character types (Werewolf, Mage, etc.)
   - Chronicle management
   - Plot/Rumor systems
   - Relationships between entities

2. **UI Components**
   - Character sheets for non-Vampire types
   - Chronicle interface
   - Plot/Rumor interface
   - Settings dialog
   - Import/Export functionality

3. **Business Logic**
   - Experience point calculations
   - Game mechanics implementation
   - Chronicle management
   - Plot/Rumor management

## File Conversion Progress

| Original VB File | Python Implementation | Status | Notes |
|-----------------|---------------------|--------|-------|
| frmMain.frm | main_window.py | ✓ | Basic structure implemented |
| frmNewCharacter.frm | character_creation.py | ✓ | Basic implementation complete |
| frmVampire.frm | sheets/vampire.py | ⏳ | In progress |
| clsCharacter.cls | models/base.py | ✓ | Implemented with SQLAlchemy |
| clsVampire.cls | models/vampire.py | ✓ | Implemented with SQLAlchemy |
| modDatabase.bas | database/engine.py | ✓ | Reimplemented with SQLAlchemy |
| frmOptions.frm | - | ❌ | Not started |
| frmAbout.frm | - | ❌ | Not started |
| frmExperience.frm | - | ❌ | Not started |
| frmChronicle.frm | - | ❌ | Not started |
| frmPlot.frm | - | ❌ | Not started |
| frmRumor.frm | - | ❌ | Not started |

## Next Steps

### Short Term (Next Sprint)
1. Complete the Vampire character sheet implementation
2. Implement trait widgets for character attributes
3. Add validation to character creation
4. Implement experience point tracking

### Medium Term
1. Implement other character types (Werewolf, Mage)
2. Add chronicle management functionality
3. Create plot/rumor system
4. Improve UI styling and user experience

### Long Term
1. Develop web interface
2. Add multi-user support
3. Implement cloud synchronization
4. Create mobile companion app

## Technical Debt and Known Issues

1. Need proper error handling system
2. Missing comprehensive testing
3. UI needs styling consistency
4. Documentation requires expansion

## Implementation Notes

### Data Model Differences
- Using SQLAlchemy ORM instead of direct database access
- JSON for flexible data storage where appropriate
- Database migrations using Alembic

### UI Implementation Differences
- Component-based design vs Form-based design
- PyQt6 instead of VB forms
- Tabbed interface for main navigation
- Custom widgets for trait display

## Testing Strategy

1. Unit tests for core business logic
2. Integration tests for database operations
3. UI tests for critical workflows
4. Manual testing for UI components

## Documentation Strategy

1. User documentation
   - Installation guide
   - User manual
   - Quick start guide

2. Developer documentation
   - Architecture overview
   - API documentation
   - Contributing guide 