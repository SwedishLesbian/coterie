"""Coterie main application entry point.

This module initializes the database, sets up logging, and starts the PyQt6 application.
It serves as the main entry point when running the package as a module.
"""

import sys
import logging
import argparse
from pathlib import Path
from typing import NoReturn, Optional, List

from PyQt6.QtWidgets import QApplication
from sqlalchemy.orm import Session

from coterie.database.engine import engine, APP_DATA, session_factory
from coterie.models.base import Base
from coterie.ui.main_window import MainWindow
from coterie.utils.menu_importer import MenuImporter


def setup_logging() -> None:
    """Configure application logging.
    
    Creates a log file in the application data directory and sets up console logging.
    """
    log_file = APP_DATA / 'coterie.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def init_database() -> None:
    """Initialize the database schema.
    
    Creates all tables defined in the SQLAlchemy models if they don't exist.
    """
    Base.metadata.create_all(engine)

def import_menus(menu_path: str, session: Session, specific_menus: Optional[List[str]] = None, interactive: bool = True) -> bool:
    """
    Import Grapevine menu files.
    
    Args:
        menu_path: Path to a .gvm file or directory containing .gvm files
        session: Database session
        specific_menus: Optional list of specific menu names to import
        interactive: Whether to show conflict resolution dialogs
        
    Returns:
        True if import was successful, False if any errors occurred
    """
    importer = MenuImporter(session)
    path = Path(menu_path)
    
    if specific_menus:
        if not path.is_dir():
            logging.error("Menu path must be a directory when importing specific menus")
            return False
        results = importer.import_specific_menus(specific_menus, str(path))
        return all(results.values())
    elif path.is_file():
        return importer.import_menu_file(str(path), interactive)
    elif path.is_dir():
        results = importer.import_directory(str(path), interactive=interactive)
        return all(results.values())
    else:
        logging.error(f"Menu path not found: {menu_path}")
        return False

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Coterie - Mind's Eye Theater LARP Character Manager")
    parser.add_argument('--import-menus', type=str, help='Import Grapevine menu files from file or directory')
    parser.add_argument('--menu-names', type=str, nargs='+', help='Specific menu names to import')
    parser.add_argument('--non-interactive', action='store_true', help='Import without showing conflict resolution dialogs')
    return parser.parse_args()

def main() -> NoReturn:
    """Main application entry point.
    
    Sets up logging, initializes the database, and starts the PyQt6 application.
    """
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Coterie v0.1")
    
    # Parse command line arguments
    args = parse_args()
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Handle menu import if requested
    if args.import_menus:
        with session_factory() as session:
            if import_menus(args.import_menus, session, args.menu_names, not args.non_interactive):
                logger.info("Menu import completed successfully")
                if not any(sys.argv[1:]) or '--import-menus' in sys.argv:
                    sys.exit(0)
            else:
                logger.error("Menu import failed")
                sys.exit(1)
    
    # Start Qt application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()