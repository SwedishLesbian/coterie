# Coterie Documentation

Welcome to the Coterie documentation. This serves as a central reference point for the conversion of Grapevine 3.01 to the Python-based Coterie application.

## Project Overview

Coterie is a modern Python port of the original Grapevine character and chronicle management system for Mind's Eye Theater LARP. This project converts the original Visual Basic 6.0 codebase to modern Python with SQLAlchemy and PyQt6. The goal is to maintain compatibility with original Grapevine data while enhancing functionality and providing a modern user interface.

### Key Features

- Character creation and management
- Chronicle organization and tracking
- Staff management with role-based organization
- Player tracking with status management
- Multi-format character notes (Plaintext, Markdown, HTML)
- LARP trait system with adjective-based mechanics
- Modern, intuitive user interface
- Database-backed storage with SQLAlchemy
- Cross-platform compatibility

## For AI Assistance (Cursor)

### Project Context

We are converting the Grapevine 3.01 Visual Basic application to Python 3.8+. This is a character management system for Mind's Eye Theater LARP (Live Action Role-Playing) based on White Wolf's World of Darkness setting. The original VB source code is available in the repository archives as a reference.

The project is named "Coterie" and follows a component-based architecture with:
- SQLAlchemy ORM for database management
- PyQt6 for user interface
- Type hints throughout the codebase
- Modern Python practices and patterns

### Current Status

We have completed several major features:
- Project structure and infrastructure
- Basic SQLAlchemy models for characters, staff, and players
- Core UI framework with PyQt6
- Character creation dialog
- Basic application flow
- Import dialog for both .gvc and .gex files
- LARP trait widget implementation
- Database models for adjective-based traits
- Chronicle management system
- Active chronicle display in title bar
- People menu with staff/player management
- All Chronicles view with global lists
- Multi-format character notes support

Current focus areas:
- Enhancing staff and player management features
- Implementing role-based permissions
- Adding challenge resolution mechanics
- Extending support to other character types

Refer to `docs/status.md` for the complete and current status of the project. For the most recent development session details and to pick up where we left off, see `docs/development-session-summary.md`.

### Development Guidelines

When working on this project:

1. **Follow Python Best Practices**: Adhere to the project's coding style, use type hints, and follow the principles in `.cursor/rules/.cursorrules`
2. **Component-Based Development**: Each component should be self-contained with clear interfaces
3. **Progressive Implementation**: Focus on one component at a time, ensuring it works before moving to the next
4. **Documentation**: Update relevant documentation as you implement new features or make changes
5. **Testing**: Add appropriate tests for new functionality

### Next Development Tasks

See `docs/conversion-checklist.md` and `docs/component-roadmap.md` for the complete task list. Current priorities:

1. Complete the staff and player management interfaces
2. Implement the Challenge Resolution System for LARP play
3. Extend support to other character types (Werewolf, Mage, etc.)
4. Complete character import/export cycle
5. Add validation to the character creation dialog

### Document Updates

As development progresses, please update:
1. `docs/status.md` with completed items and new progress
2. `docs/conversion-checklist.md` to mark completed tasks
3. `docs/component-roadmap.md` to update component status
4. `docs/development-session-summary.md` to document session outcomes
5. Other relevant documentation as needed

## Documentation Index

### Project Status and Planning

- [Project Status](status.md) - Current status and progress
- [Development Session Summary](development-session-summary.md) - Details of recent development work
- [Conversion Roadmap](conversion-roadmap.md) - Overall plan for the conversion process
- [Conversion Checklist](conversion-checklist.md) - Detailed checklist of tasks
- [Component Roadmap](component-roadmap.md) - Component-specific development plan
- [VB Structure](vb-structure.md) - Original VB codebase structure

### Technical Documentation

- [Architecture Overview](architecture.md) - Application architecture
- [Technical Details](technical.md) - Technical specifications
- [UI Components](ui-components.md) - UI component details
- [API Documentation](api.md) - API reference
- [Conversion Guide](conversion-guide.md) - Guide for developers working on the conversion
- [LARP Trait System](larp-trait-system.md) - Documentation of the Mind's Eye Theater trait system

### Development Resources

- [Contributing Guide](contributing.md) - How to contribute to the project
- [Issue Tracking](fixes.md) - Known issues and fixes

### User Documentation

- [Installation Guide](user/installation.md) - How to install the application
- [Quick Start Guide](user/quickstart.md) - Getting started with Coterie
- [FAQ](user/faq.md) - Frequently asked questions

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
6. Review the [Development Session Summary](development-session-summary.md) to pick up where we left off

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