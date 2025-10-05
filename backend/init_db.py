#!/usr/bin/env python3
"""
Database initialization script for LifeTime AI.

This script provides utilities for database setup, migration, and maintenance.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import (
    create_tables,
    drop_tables,
    engine,
    get_database_info,
    verify_database_connection,
)
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


def init_database(drop_existing: bool = False):
    """
    Initialize the database with tables.

    Args:
        drop_existing: Whether to drop existing tables first
    """
    try:
        if drop_existing:
            logger.warning("Dropping existing database tables...")
            drop_tables()

        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


def verify_setup():
    """Verify that the database setup is working correctly."""
    try:
        logger.info("Verifying database setup...")

        # Check connection
        if not verify_database_connection():
            logger.error("Database connection verification failed")
            sys.exit(1)

        # Display database info
        db_info = get_database_info()
        logger.info("Database configuration:")
        for key, value in db_info.items():
            logger.info(f"  {key}: {value}")

        # Check if tables exist
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            logger.warning(
                "No tables found in database. Run 'python init_db.py --init' to create tables."
            )
        else:
            logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")

        logger.info("Database verification completed successfully")

    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        sys.exit(1)


def show_migration_status():
    """Show the current migration status using Alembic."""
    try:
        import os
        import subprocess

        # Change to backend directory for Alembic commands
        backend_dir = Path(__file__).parent
        os.chdir(backend_dir)

        logger.info("Current migration status:")

        # Get current revision
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip():
            logger.info(f"Current revision: {result.stdout.strip()}")
        else:
            logger.info("No migrations applied yet")

        # Get migration history
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "history"],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip():
            logger.info("Migration history:")
            for line in result.stdout.strip().split("\n"):
                logger.info(f"  {line}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get migration status: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error checking migration status: {e}")
        sys.exit(1)


def main():
    """Main function for database initialization script."""
    parser = argparse.ArgumentParser(
        description="Database initialization and management for LifeTime AI"
    )

    parser.add_argument(
        "--init", action="store_true", help="Initialize database tables"
    )

    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before initialization (dangerous!)",
    )

    parser.add_argument(
        "--verify", action="store_true", help="Verify database setup and connection"
    )

    parser.add_argument("--status", action="store_true", help="Show migration status")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        setup_logging()

    # Show configuration
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Encryption enabled: {settings.database_encrypt}")

    if args.init:
        init_database(drop_existing=args.drop)
    elif args.verify:
        verify_setup()
    elif args.status:
        show_migration_status()
    else:
        parser.print_help()
        logger.info("Use --verify to check database status")


if __name__ == "__main__":
    main()
