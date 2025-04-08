# Component Roadmap

This document outlines the specific components that need to be developed for Coterie, and their current implementation status.

## Core Components

### Data Models

- ✅ **Base Character Model** - Core character data structure
- ✅ **Trait Models** - Traditional trait handling
- ✅ **LARP Trait Models** - Adjective-based trait handling for Mind's Eye Theater
- ⬜ **Experience System** - Track and spend experience points
- ⬜ **Chronicle Model** - Organize characters into chronicles
- ⬜ **Notes System** - Attach notes to characters

### UI Framework

- ✅ **Main Window** - Application shell and navigation
- ✅ **Dialog Base Classes** - Standard dialog templates
- ✅ **Character Creation Flow** - Guided character creation
- ✅ **Import/Export Systems** - Data interchange with Grapevine
- ⬜ **Settings Dialog** - Application configuration

## Character Sheet Components

### Character Types

- ✅ **Vampire Sheet** - Vampire: The Masquerade character display
- ⬜ **Werewolf Sheet** - Werewolf: The Apocalypse character display
- ⬜ **Mage Sheet** - Mage: The Ascension character display
- ⬜ **Other Character Types** - Additional WoD character types

### Sheet Sections

- ✅ **Basic Info** - Name, nature, demeanor, etc.
- ✅ **Attributes** - Physical, Social, Mental traits
- ✅ **Abilities** - Talents, Skills, Knowledge
- ✅ **Advantages** - Backgrounds, Disciplines, Gifts, etc.
- ⬜ **Health/Damage Tracking** - Track character damage
- ⬜ **Notes Section** - Character-specific notes
- ⬜ **Experience Log** - Track experience gain/spending

### Trait Components

- ✅ **Dot-based Trait Widget** - Traditional trait display
- ✅ **Trait Group Widget** - Group of related traits
- ✅ **LARP Trait Widget** - Adjective-based trait display
- ✅ **LARP Trait Category Widget** - Organized trait categories
- ⬜ **Challenge Resolution Widget** - LARP trait bidding interface

## Game Management Components

- ⬜ **Character List View** - Browse and filter characters
- ⬜ **Chronicle Management** - Organize characters by chronicle
- ⬜ **Relationship Tracker** - Track character relationships
- ⬜ **NPC Generator** - Create quick NPCs
- ⬜ **Experience Calculator** - Calculate and award XP

## Utility Components

- ✅ **Data Loader** - Load JSON and Grapevine data
- ✅ **Trait Converter** - Convert between trait systems
- ⬜ **Dice Roller** - Handle dice rolling for tabletop WoD
- ⬜ **Name Generator** - Generate character names
- ⬜ **Printing System** - Print character sheets

## Mind's Eye Theater LARP Support

- ✅ **Adjective Trait System** - Implement LARP trait system
- ✅ **Trait Category Management** - Organize traits by category
- ✅ **Negative Trait Support** - Support for flaws/negative traits
- ✅ **Trait Spending Tracking** - Track spent traits
- ⬜ **Challenge System** - Implement trait bidding for challenges
- ⬜ **Trait Refresh** - Handle trait refresh mechanics 