# Coterie

A modern Python port of the Grapevine character and chronicle management system for Mind's Eye Theater LARP.

## Overview

Coterie is a modern, cross-platform reimplementation of the Grapevine character management system. It is built with Python, SQLAlchemy, and PyQt6, offering a fresh and maintainable codebase while preserving the functionality of the original application.

### Key Features

- **Modern UI** - Clean, intuitive PyQt6-based interface
- **Cross-Platform** - Runs on Windows, macOS, and Linux
- **Data Preservation** - Import from original Grapevine files (.gvc and .gex)
- **Enhanced Features** - Modern improvements while preserving original functionality
- **Type Safety** - Fully type-hinted Python codebase

## Current Status

Coterie is in early development (Phase 1). Currently implemented:

- Core application framework
- Database models for characters
- Character creation dialog
- Import dialog for Grapevine 3.x (.gvc) and exported (.gex) files
- Vampire character sheet
- Trait widgets

See `docs/status.md` for complete details on project status.

## Installation

### Requirements

- Python 3.8 or higher
- PyQt6
- SQLAlchemy
- Other dependencies as listed in requirements.txt

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/coterie.git
   cd coterie
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python -m coterie
   ```

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- `docs/index.md` - Documentation index and overview
- `docs/status.md` - Current project status
- `docs/development-session-summary.md` - Latest development details
- `docs/architecture.md` - Technical architecture
- `docs/ui-components.md` - UI component documentation

## Contributing

Contributions are welcome! Please see `docs/contributing.md` for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original Grapevine developers for creating the foundation
- Mind's Eye Theater by White Wolf Publishing
- Contributors and supporters of this project
