# Coterie Documentation

Welcome to the Coterie documentation. This serves as a central reference point for the conversion of Grapevine 3.01 to the Python-based Coterie application.

## Project Overview

Coterie is a modern Python port of the original Grapevine character and chronicle management system for World of Darkness tabletop roleplaying games. This project converts the original Visual Basic 6.0 codebase to modern Python with SQLAlchemy and PyQt6. The goal is to maintain compatibility with original Grapevine data while enhancing functionality and providing a modern user interface.

## For AI Assistance (Cursor)

### Project Context

We are converting the Grapevine 3.01 Visual Basic application to Python 3.8+. This is a character management system for World of Darkness tabletop roleplaying games. The original VB source code is available in the repository as a reference (`docs/VB-Grapevine-SourceCode.md`).

The project is named "Coterie" and follows a component-based architecture with:
- SQLAlchemy ORM for database management
- PyQt6 for user interface
- Type hints throughout the codebase
- Modern Python practices and patterns

### Current Status

We are in the early stages of development (Phase 1), having completed:
- Project structure and infrastructure
- Basic SQLAlchemy models for characters
- Core UI framework with PyQt6
- Character creation dialog
- Basic application flow

Refer to `docs/status.md` for the complete and current status of the project.

### Development Guidelines

When working on this project:

1. **Follow Python Best Practices**: Adhere to the project's coding style, use type hints, and follow the principles in `.cursor/rules/.cursorrules`
2. **Component-Based Development**: Each component should be self-contained with clear interfaces
3. **Progressive Implementation**: Focus on one component at a time, ensuring it works before moving to the next
4. **Documentation**: Update relevant documentation as you implement new features or make changes
5. **Testing**: Add appropriate tests for new functionality

### Next Development Tasks

See `docs/conversion-checklist.md` and `docs/component-roadmap.md` for the complete task list. Current priorities:

1. Implement the TraitWidget component for displaying character traits
2. Complete the VampireSheet implementation
3. Create the CharacterList view
4. Add validation to the character creation dialog
5. Implement character data loading/saving

### Document Updates

As development progresses, please update:
1. `docs/status.md` with completed items and new progress
2. `docs/conversion-checklist.md` to mark completed tasks
3. `docs/component-roadmap.md` to update component status
4. Other relevant documentation as needed

## Documentation Index

### Project Status and Planning

- [Project Status](status.md) - Current status and progress
- [Conversion Roadmap](conversion-roadmap.md) - Overall plan for the conversion process
- [Conversion Checklist](conversion-checklist.md) - Detailed checklist of tasks
- [Component Roadmap](component-roadmap.md) - Component-specific development plan
- [VB Structure](vb-structure.md) - Original VB codebase structure
- [VB Source Code](VB-Grapevine-SourceCode.md) - Original VB source code reference

### Technical Documentation

- [Architecture Overview](architecture.md) - Application architecture
- [Technical Details](technical.md) - Technical specifications
- [API Documentation](api.md) - API reference
- [Conversion Guide](conversion-guide.md) - Guide for developers working on the conversion

### Development Resources

- [Contributing Guide](contributing.md) - How to contribute to the project
- [Issue Tracking](fixes.md) - Known issues and fixes

## Project Structure

```
coterie/
├── core/           # Business logic
├── database/       # Database configuration and migrations
├── models/         # SQLAlchemy models
├── ui/             # User interface components
│   ├── dialogs/    # Dialog windows
│   ├── sheets/     # Character sheets
│   └── widgets/    # Reusable widgets
└── utils/          # Utility functions
```

## Getting Started

### For Users

The application is in early development and not yet ready for general use. Check back for updates!

### For Developers

1. Review the [Conversion Roadmap](conversion-roadmap.md) to understand the project plan
2. Set up your development environment as described in the [README](../README.md)
3. Explore the [Conversion Guide](conversion-guide.md) for implementation details
4. Check the [Component Roadmap](component-roadmap.md) for priority components
5. Find tasks to work on in the [Conversion Checklist](conversion-checklist.md)

## Key Project Goals

1. **Platform Independence** - Run on Windows, macOS, and Linux
2. **Modern UI** - Clean, intuitive PyQt6-based interface
3. **Data Preservation** - Import legacy Grapevine data
4. **Enhanced Features** - Add new functionality while preserving original features
5. **Code Quality** - Maintainable, testable, and documented codebase

## Project Timeline

- **Phase 1 (Q2 2024)** - Core functionality, Vampire support
- **Phase 2 (Q3 2024)** - Additional character types, experience system
- **Phase 3 (Q4 2024)** - Game tools, advanced features
- **Phase 4 (Q1 2025)** - Release 1.0, additional platforms

## Contact

For questions or assistance, please open an issue on the project's GitHub repository. 