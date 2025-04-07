"""Grapevine main application entry point.

This module initializes the database, sets up logging, and starts the PyQt6 application.
It serves as the main entry point when running the package as a module.
"""

import sys
import logging
from typing import NoReturn

from PyQt6.QtWidgets import QApplication

from grapevine.database.engine import engine, APP_DATA
from grapevine.models.base import Base
from grapevine.ui.main_window import MainWindow


def setup_logging() -> None:
    """Configure application logging.
    
    Creates a log file in the application data directory and sets up console logging.
    """
    log_file = APP_DATA / 'grapevine.log'
    
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

def main() -> NoReturn:
    """Main application entry point.
    
    Sets up logging, initializes the database, and starts the PyQt6 application.
    """
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Grapevine")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Start Qt application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()