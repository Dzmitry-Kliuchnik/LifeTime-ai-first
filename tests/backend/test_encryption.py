"""
Tests for database encryption functionality.
"""

from unittest.mock import MagicMock, patch

from app.core.config import Settings
from app.core.database import configure_sqlite_encryption, get_database_url


class TestDatabaseEncryption:
    """Test database encryption features."""

    def test_encryption_disabled_by_default(self):
        """Test that encryption is disabled by default in test settings."""
        test_settings = Settings()

        with patch("app.core.database.settings", test_settings):
            # Default should be unencrypted
            assert test_settings.database_encrypt is False
            url = get_database_url()
            assert "sqlite+pysqlcipher" not in url

    def test_encryption_fallback_when_no_sqlcipher(self):
        """Test graceful fallback when SQLCipher is not available."""
        test_settings = Settings(
            database_url="sqlite:///./test.db",
            database_encrypt=True,
            database_key="test-encryption-key",
        )

        with patch("app.core.database.settings", test_settings):
            # Should fall back to regular SQLite when pysqlcipher3 is not available
            url = get_database_url()
            # Should not contain sqlcipher since the package isn't available
            assert url == "sqlite:///./test.db"

    def test_encryption_configuration_with_mock_sqlcipher(self):
        """Test encryption configuration with mocked SQLCipher."""
        # Mock successful SQLCipher import
        mock_pysqlcipher = MagicMock()

        test_settings = Settings(
            database_url="sqlite:///./test.db",
            database_encrypt=True,
            database_key="test-encryption-key",
        )

        with patch("app.core.database.settings", test_settings), patch.dict(
            "sys.modules", {"pysqlcipher3": mock_pysqlcipher}
        ):
            # Should now use SQLCipher URL format
            with patch("builtins.__import__", return_value=mock_pysqlcipher):
                url = get_database_url()
                assert "sqlite+pysqlcipher" in url
                assert "test-encryption-key" in url

    def test_sqlite_encryption_setup_graceful_failure(self):
        """Test that encryption setup fails gracefully when SQLCipher commands don't work."""
        # Create mock connection that fails on PRAGMA key
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Make PRAGMA key fail (simulating regular SQLite)
        mock_cursor.execute.side_effect = [
            Exception("no such function: key"),  # PRAGMA key fails
            None,  # Other commands might succeed
        ]

        test_settings = Settings(database_encrypt=True, database_key="test-key")

        with patch("app.core.database.settings", test_settings):
            # Should not raise exception, just log warning
            configure_sqlite_encryption(mock_connection, None)

            # Verify cursor.close() was called
            mock_cursor.close.assert_called()

    def test_database_key_masking_in_info(self):
        """Test that database keys are masked in database info."""
        test_settings = Settings(
            database_url="sqlite:///./test.db",
            database_encrypt=True,
            database_key="super-secret-key",
        )

        with patch("app.core.database.settings", test_settings):
            from app.core.database import get_database_info

            info = get_database_info()

            # Key should be masked or encryption should be indicated
            assert "super-secret-key" not in str(info)
            # When SQLCipher is not available, expect indication of encryption request
            assert (
                "***" in info["database_url"]
                or "encryption requested" in info["database_url"]
            )

    def test_encryption_with_different_url_formats(self):
        """Test encryption URL generation with different SQLite URL formats."""
        test_cases = [
            ("sqlite:///./test.db", "sqlite+pysqlcipher://"),
            ("sqlite://./test.db", "sqlite+pysqlcipher://"),
        ]

        for original_url, expected_prefix in test_cases:
            test_settings = Settings(
                database_url=original_url,
                database_encrypt=True,
                database_key="test-key",
            )

            # Mock successful pysqlcipher3 import
            mock_pysqlcipher = MagicMock()

            with patch("app.core.database.settings", test_settings), patch.dict(
                "sys.modules", {"pysqlcipher3": mock_pysqlcipher}
            ):
                with patch("builtins.__import__", return_value=mock_pysqlcipher):
                    url = get_database_url()
                    assert url.startswith(expected_prefix)
