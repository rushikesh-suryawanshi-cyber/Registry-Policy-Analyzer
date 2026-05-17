import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger("admx_parser")

class DatabaseContext:
    """Context manager for SQLite database connections."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None

    def __enter__(self) -> sqlite3.Connection:
        self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
        # Enable foreign keys constraint enforcement
        self._connection.execute("PRAGMA foreign_keys = ON;")
        self._connection.row_factory = sqlite3.Row
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            if exc_type is not None:
                self._connection.rollback()
                logger.error(f"Database transaction rolled back due to error: {exc_val}")
            else:
                self._connection.commit()
            self._connection.close()

def init_db(db_path: str, schema_path: str) -> bool:
    """Initializes the database using the provided schema file."""
    if not Path(schema_path).exists():
        logger.error(f"Schema file not found: {schema_path}")
        return False
        
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_script = f.read()
            
        with DatabaseContext(db_path) as conn:
            conn.executescript(schema_script)
            
        logger.info(f"Successfully initialized database at {db_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False
