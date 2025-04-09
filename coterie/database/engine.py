import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from coterie.models.base import Base

# Get the application data directory
if os.name == 'nt':  # Windows
    APP_DATA = Path(os.getenv('APPDATA')) / 'Coterie'
else:  # Linux/Mac
    APP_DATA = Path.home() / '.coterie'

# Create the data directory if it doesn't exist
APP_DATA.mkdir(parents=True, exist_ok=True)

# Database file path
DB_PATH = APP_DATA / 'coterie.db'

# Create the database engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Create a session factory
Session = sessionmaker(bind=engine)

def get_session():
    """Get a new database session."""
    return Session()

def init_db():
    """Initialize the database schema."""
    Base.metadata.create_all(engine)
    
    # Run migrations
    run_migrations()
    
def run_migrations():
    """Run any necessary database migrations."""
    session = get_session()
    try:
        # Check if chronicles table exists
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='chronicles'"))
        if result.fetchone() is None:
            # Create chronicles table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS chronicles (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    narrator VARCHAR(100) NOT NULL,
                    start_date DATETIME NOT NULL,
                    last_modified DATETIME NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            """))
            
        # Check if chronicle_id column exists in characters table
        result = session.execute(text("PRAGMA table_info(characters)"))
        columns = [column[1] for column in result.fetchall()]
        
        if 'chronicle_id' not in columns:
            # Add chronicle_id column to characters table
            session.execute(text("""
                ALTER TABLE characters ADD COLUMN chronicle_id INTEGER REFERENCES chronicles(id)
            """))
            
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Migration error: {e}")
    finally:
        session.close() 