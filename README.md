# Coterie v0.1

  sSSs    sSSs_sSSs    sdSS_SSSSSSbs    sSSs   .S_sSSs     .S    sSSs
 d%%SP   d%%SP~YS%%b   YSSS~S%SSSSSP   d%%SP  .SS~YS%%b   .SS   d%%SP
d%S'    d%S'     `S%b       S%S       d%S'    S%S   `S%b  S%S  d%S'
S%S     S%S       S%S       S%S       S%S     S%S    S%S  S%S  S%S
S&S     S&S       S&S       S&S       S&S     S%S    d*S  S&S  S&S
S&S     S&S       S&S       S&S       S&S_Ss  S&S   .S*S  S&S  S&S_Ss
S&S     S&S       S&S       S&S       S&S~SP  S&S_sdSSS   S&S  S&S~SP
S&S     S&S       S&S       S&S       S&S     S&S~YSY%b   S&S  S&S
S*b     S*b       d*S       S*S       S*b     S*S   `S%b  S*S  S*b
S*S.    S*S.     .S*S       S*S       S*S.    S*S    S%S  S*S  S*S.
 SSSbs   SSSbs_sdSSS        S*S        SSSbs  S*S    S&S  S*S   SSSbs
  YSSP    YSSP~YSSY         S*S         YSSP  S*S    SSS  S*S    YSSP
                            SP                SP          SP
                            Y                 Y           Y


A modern Python port of Grapevine - A World of Darkness character and chronicle management system. This version is based on the original Grapevine 3.01 by Adam Cerling.

## Features

### Current Features
- Basic character management foundation
- Vampire: The Masquerade character creation
- SQLite database with SQLAlchemy ORM
- Modern PyQt6-based interface

### Planned Features
- Complete character management for various World of Darkness games:
  - Vampire: The Masquerade
  - Werewolf: The Apocalypse
  - Mage: The Ascension
  - Wraith: The Oblivion
  - Changeling: The Dreaming
  - Hunter: The Reckoning
  - Mummy: The Resurrection
  - Demon: The Fallen
  - Mortal
- Chronicle management tools
- Experience point tracking
- Character relationships and histories
- Plot and rumor management
- JSON data format support

## Installation

### Requirements
- Python 3.8+
- Git
- SQLite 3
- PyQt6

### Setup

#### Windows
1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python main.py
   ```

#### Linux/Mac
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e .
   ```
4. Initialize the database:
   ```bash
   alembic upgrade head
   ```
5. Run the application:
   ```bash
   python main.py
   ```

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

## Documentation

For detailed documentation, see the following:

- [Architecture Overview](docs/architecture.md)
- [Technical Specifications](docs/technical.md)
- [API Documentation](docs/api.md)
- [Project Status](docs/status.md)
- [Conversion Roadmap](docs/conversion-roadmap.md)
- [Conversion Checklist](docs/conversion-checklist.md)
- [Contributing Guide](docs/contributing.md)

## License

This project is licensed under Creative Commons Attribution-NonCommercial 2.5.
This is a derivative work based on Grapevine by Adam Cerling.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

For more details, see the [Contributing Guide](docs/contributing.md).

## Acknowledgments

- Original Grapevine by Adam Cerling
- World of Darkness by White Wolf Publishing
