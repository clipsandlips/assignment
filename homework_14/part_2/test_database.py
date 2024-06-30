import pytest
from unittest.mock import patch
from sqlalchemy_utils import database_exists, drop_database
from create_database import create_postgres_database

@pytest.fixture(scope="module")
def mock_settings():
    with patch("settings.settings") as mock_settings:
        mock_settings.postgres_user = "marina_admin"
        mock_settings.postgres_password = "mar123"
        mock_settings.postgres_domain = "localhost"
        mock_settings.postgres_port = "5433"
        mock_settings.postgres_db_name = "homework_14_part_2"
        yield mock_settings

def test_create_postgres_database(mock_settings):
    result = create_postgres_database()
    assert "created successfully" in result.lower()

#def test_create_postgres_database_existing_db(mock_settings):
#    # Create the database first
#    create_postgres_database()

#    # Test creating it again should drop and create
#    result = create_postgres_database()
#    assert "dropped successfully" in result.lower()

#def test_create_postgres_database_missing_settings():
#    with patch("settings.settings") as mock_settings:
#        mock_settings.postgres_user = None
#        result = create_postgres_database()
#        assert "section not found" in result.lower()

#def test_create_postgres_database_exception(mock_settings):
#    # Mock an exception during database creation
#    with patch("main.create_database") as mock_create_database:
#        mock_create_database.side_effect = Exception("Mocked error")
#        result = create_postgres_database()
#        assert "an error occurred" in result.lower()
