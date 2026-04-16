"""
Database helpers used across the codebase.

This module exists to provide a stable import path (`app.core.database`) for
dependencies like `get_db`, while keeping the actual SQLAlchemy setup in
`app.db.session`.
"""

from app.db.session import SessionLocal, engine, get_db

__all__ = ["SessionLocal", "engine", "get_db"]

