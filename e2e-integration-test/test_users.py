import pytest
import requests
from datetime import datetime

def test_get_users(api_base_url, admin_headers):
    """Test getting all users."""
    response = requests.get(
        f"{api_base_url}/users",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "id" in data[0]
        assert "email" in data[0]
        assert "full_name" in data[0]
        assert "roles" in data[0]

def test_create_user(api_base_url, admin_headers):
    """Test creating a new user."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    user_data = {
        "email": f"test.user{timestamp}@university.edu",
        "full_name": f"Test User {timestamp}",
        "password": "password123",
        "roles": ["student"],
    }
    response = requests.post(
        f"{api_base_url}/users",
        headers=admin_headers,
        json=user_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert len(data["roles"]) == 1
    assert data["roles"][0]["name"] == "student"

def test_get_user_by_id(api_base_url, admin_headers):
    """Test getting a user by ID."""
    # First get all users
    response = requests.get(
        f"{api_base_url}/users",
        headers=admin_headers,
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0
    
    # Get a specific user
    user_id = users[0]["id"]
    response = requests.get(
        f"{api_base_url}/users/{user_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id

def test_update_user(api_base_url, admin_headers):
    """Test updating a user."""
    # First create a new user
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    user_data = {
        "email": f"update.user{timestamp}@university.edu",
        "full_name": f"Update User {timestamp}",
        "password": "password123",
        "roles": ["student"],
    }
    response = requests.post(
        f"{api_base_url}/users",
        headers=admin_headers,
        json=user_data,
    )
    assert response.status_code == 200
    new_user = response.json()
    
    # Update the user
    update_data = {
        "full_name": f"Updated User {timestamp}",
        "roles": ["student", "faculty"],
    }
    response = requests.put(
        f"{api_base_url}/users/{new_user['id']}",
        headers=admin_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["full_name"] == update_data["full_name"]
    assert len(updated_user["roles"]) == 2
    role_names = [role["name"] for role in updated_user["roles"]]
    assert "student" in role_names
    assert "faculty" in role_names

def test_non_admin_access_restrictions(api_base_url, faculty_headers, student_headers):
    """Test that non-admin users cannot access user management endpoints."""
    # Faculty should not be able to get all users
    response = requests.get(
        f"{api_base_url}/users",
        headers=faculty_headers,
    )
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden
    
    # Student should not be able to get all users
    response = requests.get(
        f"{api_base_url}/users",
        headers=student_headers,
    )
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden
    
    # Faculty should not be able to create users
    user_data = {
        "email": "test@university.edu",
        "full_name": "Test User",
        "password": "password123",
        "roles": ["student"],
    }
    response = requests.post(
        f"{api_base_url}/users",
        headers=faculty_headers,
        json=user_data,
    )
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden
