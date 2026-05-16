from typing import Generator
from fastapi import Request
from admx_parser.db.connection import DatabaseContext
from admx_parser.db.repository import PolicyRepository

def get_db_path() -> str:
    # In a real app, this would come from configuration/environment variables
    return "policies.db"

def get_repository() -> Generator[PolicyRepository, None, None]:
    """Dependency to provide a PolicyRepository with an open connection."""
    with DatabaseContext(get_db_path()) as conn:
        yield PolicyRepository(conn)
