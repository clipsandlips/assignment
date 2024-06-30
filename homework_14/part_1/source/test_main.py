import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="module")
def test_client():
    """
    Create a FastAPI test client using `TestClient` with module scope.
    """
    with TestClient(app) as client:
        yield client

def test_create_user(test_client):
    """
    Test the POST /users/ endpoint.
    """
    # Prepare test data
    test_user = {
        "username": "testuser",
        "email": "testuser@example.com",
        "is_verified": True,
        "avatar_url": "string",        
        "password": "testpassword"
    
    
    }


    # Make request to the endpoint
    response = test_client.post("/users/", json=test_user)

    # Check the response status code
    assert response.status_code == 201

    # Check the response content
    response_json = response.json()
    assert response_json["username"] == test_user["username"]
    assert response_json["email"] == test_user["email"]
    # Add more assertions as needed

def test_create_user_duplicate_username(test_client):
    """
    Test case for creating a user with a duplicate username.
    """
    # Prepare test data with a username that already exists
    test_user = {
        "username": "testuser",
        "email": "anotheruser@example.com",
        "is_verified": True,
        "avatar_url": "string",        
        "password": "testpassword"
    }

    # Make request to the endpoint
    response = test_client.post("/users/", json=test_user)

    # Check the response status code
    assert response.status_code == 400
    assert "Username already registered" in response.text

def test_create_user_duplicate_email(test_client):
    """
    Test case for creating a user with a duplicate email.
    """
    # Prepare test data with an email that already exists
    test_user = {
        "username": "anotheruser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }

    # Make request to the endpoint
    response = test_client.post("/users/", json=test_user)

    # Check the response status code
    assert response.status_code == 409
    assert "Email already registered" in response.text

def test_login_for_access_token(test_client):
    """
    Test the POST /token endpoint.
    """
    # Prepare test data
    form_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    # Mock the authenticate_user function to return a user
    with patch("main.authenticate_user") as mock_authenticate_user:
        mock_authenticate_user.return_value = MagicMock(username="testuser")

        # Make request to the endpoint
        response = test_client.post("/token", data=form_data)

        # Check the response status code
        assert response.status_code == 200

        # Check the response content
        response_json = response.json()
        assert "access_token" in response_json
        assert "refresh_token" in response_json

def test_login_invalid_credentials(test_client):
    """
    Test case for logging in with invalid credentials.
    """
    # Prepare test data with incorrect password
    form_data = {
        "username": "testuser",
        "password": "invalidpassword"
    }

    # Make request to the endpoint
    response = test_client.post("/token", data=form_data)

    # Check the response status code
    assert response.status_code == 401
    assert "Incorrect username or password" in response.text
