# Coterie Component Roadmap

This document outlines the specific components that need to be developed for the Coterie project, organized by category and priority.

## UI Components

### Core UI Components

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| MainWindow | Application main window | High | Completed | - |
| MenuSystem | Application menus | High | Completed | - |
| ToolBar | Application toolbar | High | Completed | - |
| StatusBar | Status information display | High | Completed | - |
| TabSystem | Tab navigation control | High | Completed | - |

### Character Management UI

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| CharacterList | Character list/grid view | High | Not Started | Character model |
| CharacterCreationDialog | New character dialog | High | Completed | Character models |
| CharacterFilterBar | Character filtering toolbar | Medium | Not Started | CharacterList |
| SearchBar | Character search component | Medium | Not Started | CharacterList |

### Character Sheet UI

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| BaseCharacterSheet | Base character sheet framework | High | Not Started | Character model |
| VampireSheet | Vampire character sheet | High | Not Started | Vampire model, TraitWidget |
| WerewolfSheet | Werewolf character sheet | Medium | Not Started | Werewolf model, TraitWidget |
| MageSheet | Mage character sheet | Medium | Not Started | Mage model, TraitWidget |
| WraithSheet | Wraith character sheet | Low | Not Started | Wraith model, TraitWidget |
| ChangelingSheet | Changeling character sheet | Low | Not Started | Changeling model, TraitWidget |
| HunterSheet | Hunter character sheet | Low | Not Started | Hunter model, TraitWidget |
| MummySheet | Mummy character sheet | Low | Not Started | Mummy model, TraitWidget |
| DemonSheet | Demon character sheet | Low | Not Started | Demon model, TraitWidget |
| MortalSheet | Mortal character sheet | Medium | Not Started | Character model, TraitWidget |

### Common Widgets

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| TraitWidget | Trait dots display/editor | High | Not Started | - |
| TraitGroupWidget | Group of related traits | High | Not Started | TraitWidget |
| NotesWidget | Character notes editor | Medium | Not Started | - |
| XPHistoryWidget | Experience history display | Medium | Not Started | Experience model |
| PathTracker | Path/Road/Humanity tracker | Medium | Not Started | - |
| BloodPoolWidget | Blood pool display (Vampire) | High | Not Started | - |
| RageWidget | Rage tracker (Werewolf) | Medium | Not Started | - |
| GnosisWidget | Gnosis tracker (Werewolf) | Medium | Not Started | - |
| AreteMeter | Arete tracker (Mage) | Medium | Not Started | - |

### Game Tools UI

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| ChronicleManager | Chronicle management UI | Medium | Not Started | Chronicle model |
| PlotManager | Plot management UI | Low | Not Started | Plot model |
| RumorManager | Rumor management UI | Low | Not Started | Rumor model |
| ExperienceDialog | XP management UI | Medium | Not Started | Experience model |
| DiceRoller | Dice rolling utility | Low | Not Started | - |
| RelationshipGraph | Character relationship viewer | Low | Not Started | Relationship model |

### Settings and Utilities

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| PreferencesDialog | Application settings | Medium | Not Started | - |
| ImportExportDialog | Data import/export | Medium | Not Started | - |
| AboutDialog | Application information | Low | Not Started | - |
| BackupManager | Database backup UI | Medium | Not Started | - |

## Data Models

### Core Models

| Model | Description | Priority | Status | Dependencies |
|-------|-------------|----------|--------|--------------|
| Character | Base character model | High | Completed | - |
| Trait | Character trait model | High | Completed | Character |
| Experience | XP tracking model | Medium | Not Started | Character |
| Note | Character notes model | Medium | Not Started | Character |

### Character Type Models

| Model | Description | Priority | Status | Dependencies |
|-------|-------------|----------|--------|--------------|
| Vampire | Vampire character model | High | Completed | Character |
| Werewolf | Werewolf character model | Medium | Not Started | Character |
| Mage | Mage character model | Medium | Not Started | Character |
| Wraith | Wraith character model | Low | Not Started | Character |
| Changeling | Changeling character model | Low | Not Started | Character |
| Hunter | Hunter character model | Low | Not Started | Character |
| Mummy | Mummy character model | Low | Not Started | Character |
| Demon | Demon character model | Low | Not Started | Character |
| Mortal | Mortal character model | Medium | Not Started | Character |

### Game System Models

| Model | Description | Priority | Status | Dependencies |
|-------|-------------|----------|--------|--------------|
| Chronicle | Chronicle management model | Medium | Not Started | - |
| Plot | Plot management model | Low | Not Started | Chronicle |
| Rumor | Rumor management model | Low | Not Started | Chronicle |
| Relationship | Character relationship model | Low | Not Started | Character |

## Business Logic Components

### Core Logic

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| CharacterService | Character CRUD operations | High | Not Started | Character models |
| ValidationService | Data validation | High | Not Started | - |
| ExperienceService | XP calculations | Medium | Not Started | Experience model |
| ImportExportService | Data import/export | Medium | Not Started | All models |

### Game Mechanics

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| DiceService | Dice rolling mechanics | Low | Not Started | - |
| CombatService | Combat resolution | Low | Not Started | Character models |
| RuleService | Game rules enforcement | Low | Not Started | Character models |

## Infrastructure Components

### Data Layer

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| DatabaseEngine | Database connection management | High | Completed | - |
| Repository | Data access patterns | High | Not Started | All models |
| MigrationSystem | Database schema management | High | Completed | - |

### Application Services

| Component | Description | Priority | Status | Dependencies |
|-----------|-------------|----------|--------|--------------|
| ConfigService | Configuration management | Medium | Not Started | - |
| LoggingService | Application logging | Medium | Not Started | - |
| BackupService | Database backup/restore | Medium | Not Started | DatabaseEngine |
| UpdateService | Application updates | Low | Not Started | - |

## Development Phases

### Phase 1: Foundation (Current)
- Core UI framework
- Base character model
- Vampire character model
- Basic character creation

### Phase 2: Basic Functionality
- Character list view
- Vampire character sheet
- Trait widgets
- Data validation
- Character CRUD operations

### Phase 3: Extended Functionality
- Experience system
- Additional character types (Werewolf, Mage)
- Import/Export functionality
- Notes system

### Phase 4: Game Tools
- Chronicle management
- Plot/Rumor system
- Relationship tracking
- Advanced game mechanics

### Phase 5: Advanced Features
- Web interface
- Multi-user support
- Cloud synchronization
- Mobile companion app 