"""
Database connection and session management for SQLCipher encrypted SQLite.
"""

import logging
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get the database URL, handling SQLCipher encryption."""
    if settings.database_encrypt:
        # Try to use SQLCipher if available, otherwise warn and fall back to regular SQLite
        try:
            import pysqlcipher3  # noqa: F401

            # For SQLCipher, we need to use a special SQLite URL format
            if settings.database_url.startswith("sqlite:///"):
                db_path = settings.database_url.replace("sqlite:///", "")
                return f"sqlite+pysqlcipher://:{settings.database_key}@/{db_path}"
            elif settings.database_url.startswith("sqlite://"):
                db_path = settings.database_url.replace("sqlite://", "")
                return f"sqlite+pysqlcipher://:{settings.database_key}@{db_path}"
        except ImportError:
            logger.warning(
                "SQLCipher encryption requested but pysqlcipher3 not available. "
                "Using regular SQLite. Install pysqlcipher3 for encryption support."
            )

    return settings.database_url


def configure_sqlite_encryption(dbapi_connection, connection_record):
    """Configure SQLCipher encryption for SQLite connections."""
    if settings.database_encrypt:
        try:
            # Check if this is a SQLCipher connection
            cursor = dbapi_connection.cursor()

            # Try to set SQLCipher encryption key
            cursor.execute(f"PRAGMA key = '{settings.database_key}'")

            # Optional: Set cipher settings for better security
            cursor.execute("PRAGMA cipher_page_size = 4096")
            cursor.execute("PRAGMA kdf_iter = 64000")
            cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
            cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

            # Verify the database is accessible
            cursor.execute("SELECT count(*) FROM sqlite_master")
            cursor.fetchone()
            logger.info("SQLCipher encryption configured successfully")

        except Exception as e:
            # If SQLCipher isn't available or configured, log warning but continue
            logger.warning(
                f"SQLCipher encryption setup failed: {e}. Using regular SQLite."
            )
        finally:
            if "cursor" in locals():
                cursor.close()


# Create synchronous engine
database_url = get_database_url()
if "sqlite" in database_url:
    # SQLite-specific configuration
    engine = create_engine(
        database_url,
        echo=settings.database_echo,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
else:
    # Non-SQLite databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(
        database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )

# Add SQLCipher configuration event listener
if "sqlite" in settings.database_url:
    event.listen(engine, "connect", configure_sqlite_encryption)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_tables() -> None:
    """Drop all database tables (useful for testing)."""
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def verify_database_connection() -> bool:
    """
    Verify that the database connection and encryption are working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            # Test basic connectivity
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

            # If using SQLite, test encryption by trying to read schema
            if "sqlite" in settings.database_url:
                result = connection.execute(text("SELECT count(*) FROM sqlite_master"))
                result.fetchone()

            logger.info("Database connection verified successfully")
            return True
    except Exception as e:
        logger.error(f"Database connection verification failed: {e}")
        return False


def get_database_info() -> dict:
    """
    Get information about the database configuration.

    Returns:
        dict: Database configuration information
    """
    database_url = get_database_url()
    # Mask the key in the URL if encryption is enabled
    if settings.database_encrypt and settings.database_key in database_url:
        database_url = database_url.replace(settings.database_key, "***")
    elif settings.database_encrypt:
        # If encryption is requested but not in URL, still indicate masking
        database_url = database_url + " (encryption requested)"

    return {
        "database_url": database_url,
        "encryption_enabled": settings.database_encrypt,
        "echo_queries": settings.database_echo,
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
    }
