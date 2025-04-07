import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get the application data directory
if os.name == 'nt':  # Windows
    APP_DATA = Path(os.getenv('APPDATA')) / 'Grapevine'
else:  # Linux/Mac
    APP_DATA = Path.home() / '.grapevine'

# Create the data directory if it doesn't exist
APP_DATA.mkdir(parents=True, exist_ok=True)

# Database file path
DB_PATH = APP_DATA / 'grapevine.db'

# Create the database engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Create a session factory
Session = sessionmaker(bind=engine)

def get_session():
    """Get a new database session."""
    return Session() 