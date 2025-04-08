# LARP Trait System Implementation Tasks

This document outlines the tasks needed to fully implement the Mind's Eye Theater LARP trait system in Coterie.

## Completed Tasks

1. ✅ **Technical Documentation**
   - Added a comprehensive section to `docs/technical.md` explaining the Mind's Eye Theater LARP trait system
   - Documented the differences between LARP and tabletop trait systems
   - Outlined implementation approach in Coterie

2. ✅ **UI Components**
   - Created `LarpTraitWidget` for displaying and managing adjective-based traits
   - Implemented `LarpTraitCategoryWidget` to manage trait categories
   - Added proper trait management functionality (add, remove, mark as spent)

3. ✅ **Data Models**
   - Created `LarpTrait` model for adjective-based traits
   - Implemented `TraitCategory` model for trait categorization
   - Added many-to-many relationship between traits and categories
   - Updated `Character` base model to support LARP traits

4. ✅ **Trait Conversion**
   - Created `TraitConverter` utility for converting between systems
   - Added methods to convert dot ratings to adjectives
   - Implemented trait adjective mappings

5. ✅ **Data Files**
   - Created `trait_adjectives.json` with standard trait adjectives

## Remaining Tasks

1. **Data Loader Updates**
   - Update `DataLoader` class to handle LARP traits
   - Add methods to extract LARP traits from Grapevine files
   - Implement conversion methods for imported data

2. **Character Sheet Updates**
   - Update `VampireSheet` to use the new `LarpTraitWidget`
   - Replace dot-based trait displays with adjective lists
   - Modify methods for loading and saving character data

3. **Import Dialog Enhancements**
   - Modify `ImportDialog` to correctly handle LARP traits
   - Update import progress tracking for trait conversion
   - Add validation for imported traits

4. **Character Creation Updates**
   - Update `CharacterCreationDialog` to use LARP trait system
   - Modify trait selection interfaces
   - Add adjective-based trait management

5. **Database Migration**
   - Create alembic migration for new table structure
   - Add data migration code to convert existing characters

6. **Testing**
   - Test LARP trait widgets with various data
   - Verify import/export functionality
   - Test character creation and editing

## Implementation Details

### DataLoader Updates

The `DataLoader` class should be updated to:

1. Extract adjective-based traits from Grapevine files
2. Create `LarpTrait` objects from extracted data
3. Associate traits with appropriate categories
4. Add methods for converting between trait systems

### Character Sheet Updates

The `VampireSheet` class needs to:

1. Replace `TraitWidget` instances with `LarpTraitWidget`
2. Update methods for loading character data to use LARP traits
3. Modify saving methods to preserve adjective-based traits

### Database Configuration

For proper LARP trait storage:

1. Create the trait_category_association table
2. Create the trait_categories table
3. Create the larp_traits table
4. Add foreign key relationships

## Technical Considerations

- Store traits as adjectives rather than numeric values
- Track trait spending in the UI and database
- Support negative traits (flaws)
- Allow custom traits to be added
- Category organization should match Mind's Eye Theater structure 