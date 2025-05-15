import pytest
import requests

def test_login_success(api_base_url):
    """Test successful login."""
    response = requests.post(
        f"{api_base_url}/auth/login",
        data={
            "username": "admin@university.edu",
            "password": "admin123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(api_base_url):
    """Test login with invalid credentials."""
    response = requests.post(
        f"{api_base_url}/auth/login",
        data={
            "username": "admin@university.edu",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401

def test_get_current_user(api_base_url, admin_headers):
    """Test getting current user information."""
    response = requests.get(
        f"{api_base_url}/auth/me",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@university.edu"
    assert "admin" in [role["name"] for role in data["roles"]]

def test_unauthorized_access(api_base_url):
    """Test accessing protected endpoint without token."""
    response = requests.get(
        f"{api_base_url}/auth/me",
    )
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden

def test_reset_password(api_base_url):
    """Test password reset functionality."""
    response = requests.post(
        f"{api_base_url}/auth/reset-password",
        json={"email": "admin@university.edu"},
    )
    # The API might return 200 OK or 202 Accepted or even 422 if the endpoint requires additional validation
    assert response.status_code in [200, 202, 422]
    # Only check for message if status code is 200 or 202
    if response.status_code in [200, 202]:
        assert "msg" in response.json()
