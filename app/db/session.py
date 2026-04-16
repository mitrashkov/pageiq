from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Configure connection pool based on environment
if settings.is_production:
    # Production pool settings
    pool_class = QueuePool
    pool_size = 10
    max_overflow = 20
    pool_timeout = 30
    pool_recycle = 3600  # 1 hour
else:
    # Development pool settings
    pool_class = QueuePool
    pool_size = 5
    max_overflow = 10
    pool_timeout = 30
    pool_recycle = 3600

# Create database engine with optimized connection pooling
engine_kwargs = {
    "poolclass": pool_class,
    "pool_size": pool_size,
    "max_overflow": max_overflow,
    "pool_timeout": pool_timeout,
    "pool_recycle": pool_recycle,
    "pool_pre_ping": True,  # Verify connections before use
    "echo": settings.DEBUG,
}

# SQLite needs special connect args for multithreaded test clients.
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    # Override pool settings for SQLite
    engine_kwargs["poolclass"] = None
elif "postgresql" in settings.DATABASE_URL:
    # PostgreSQL-specific connection args
    engine_kwargs["connect_args"] = {
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000",  # 30 second statement timeout
    }

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    # Enable expire_on_commit for better session management
    expire_on_commit=False
)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_stats():
    """Get database connection pool statistics"""
    pool = engine.pool
    return {
        'pool_size': getattr(pool, 'size', 0),
        'checked_in': getattr(pool, 'checkedin', 0),
        'checked_out': getattr(pool, 'checkedout', 0),
        'overflow': getattr(pool, 'overflow', 0),
        'invalid': getattr(pool, 'invalid', 0),
    }