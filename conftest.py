"""
Pytest configuration file.
Sets up SQLite as the default test database for local development.
"""
import os


def pytest_configure(config):
    """Set default TEST_DATABASE_URL to SQLite if not already set."""
    if "TEST_DATABASE_URL" not in os.environ:
        os.environ["TEST_DATABASE_URL"] = "sqlite:///./test_app.db"
