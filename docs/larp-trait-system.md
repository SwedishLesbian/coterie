# Mind's Eye Theater LARP Trait System

This document explains the implementation of the Mind's Eye Theater (MET) LARP trait system in Coterie, focusing on the adjective-based trait system that differs significantly from the dot-based system used in tabletop World of Darkness games.

## Overview

In Mind's Eye Theater LARP, character traits are represented by collections of adjectives rather than numeric ratings. For example, instead of having "Strength 3," a character might have the physical traits "Strong," "Powerful," and "Tough." This system is designed for live-action play, where traits are "bid" during challenges rather than rolling dice.

## Key Components

Coterie implements the following components to support the LARP trait system:

### Data Models

1. **LarpTrait**
   - Represents a single adjective trait
   - Properties include name, categories, negative status, and spent status
   - Can be associated with multiple categories through a many-to-many relationship

2. **TraitCategory**
   - Represents a trait category (Physical, Social, Mental, etc.)
   - Used to organize traits into logical groupings

### UI Components

1. **LarpTraitWidget**
   - Displays and manages a list of adjective traits
   - Allows adding, removing, and marking traits as spent
   - Supports context menu for trait operations

2. **LarpTraitCategoryWidget**
   - Manages multiple trait categories (e.g., Physical, Social, Mental)
   - Provides a unified interface for working with groups of related traits

### Utility Classes

1. **TraitConverter**
   - Converts between dot ratings and adjective traits
   - Provides methods for generating lists of adjectives based on trait categories
   - Implements `dot_rating_to_adjectives` to convert traditional ratings to LARP traits

## How Trait Conversion Works

When importing characters from traditional Grapevine files, Coterie converts dot-based traits to adjective-based traits:

1. For attributes (Physical, Social, Mental), each dot corresponds to an adjective from a predefined list
   - Example: Strength 3 might become "Strong," "Powerful," and "Tough"

2. For abilities (Talents, Skills, Knowledges), appropriate adjectives are selected based on the ability type
   - Example: Brawl 3 might become "Scrappy," "Combative," and "Fierce"

3. For disciplines and other special traits, generic numbered adjectives are created
   - Example: Potence 2 becomes "Potence 1" and "Potence 2"

The `TraitConverter.dot_rating_to_adjectives` method handles this conversion by:
- Looking up appropriate trait adjectives for the given category
- Selecting adjectives up to the dot rating value
- Falling back to generic numbered adjectives if specific ones aren't available

## Character Creation

The character creation dialog has been enhanced with a tabbed interface that allows players to:

1. Select from predefined adjective traits for attributes
2. Add common or custom traits for abilities
3. Get suggested discipline traits based on clan selection
4. Add common background traits

## Character Sheet Display

The Vampire character sheet now uses:
- `LarpTraitCategoryWidget` to display attributes and abilities
- `LarpTraitWidget` to display disciplines and backgrounds
- Context menus for managing traits (renaming, marking as spent)

## Data Storage

LARP traits are stored in the database with:
- A many-to-many relationship between traits and categories
- Properties for marking traits as negative or spent
- Support for custom traits added by users

## Import/Export

When importing characters:
1. Traditional traits are extracted from Grapevine files
2. The `TraitConverter` converts them to LARP traits
3. `LarpTrait` objects are created and associated with the appropriate categories
4. The character sheet displays these traits in the LARP format

## Future Enhancements

Planned enhancements to the LARP trait system include:

1. **Challenge Resolution System**
   - Interface for trait bidding during challenges
   - Support for retest mechanics
   - Tracking of spent traits during games

2. **Trait Refresh**
   - Mechanics for refreshing spent traits
   - Time-based or rest-based refresh options

3. **Extended Trait Categories**
   - Support for additional character types (Werewolf, Mage, etc.)
   - Custom trait categories for different game types

## Using the LARP Trait System

Players can interact with the LARP trait system by:
1. Creating a new character with adjective traits
2. Importing existing characters, which will be automatically converted
3. Managing traits through the character sheet interface
4. Marking traits as spent during gameplay

This implementation provides a faithful representation of the Mind's Eye Theater LARP experience while maintaining compatibility with existing Grapevine data. 