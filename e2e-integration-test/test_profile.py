import pytest
import requests
import json
from datetime import datetime

def test_get_user_profile(api_base_url, admin_headers, faculty_headers, student_headers):
    """Test getting user profile information."""
    # Admin should be able to get their profile
    response = requests.get(
        f"{api_base_url}/auth/me",
        headers=admin_headers,
    )
    assert response.status_code == 200
    admin_profile = response.json()
    assert admin_profile["email"] == "admin@university.edu"
    assert "admin" in [role["name"] for role in admin_profile["roles"]]
    
    # Faculty should be able to get their profile
    response = requests.get(
        f"{api_base_url}/auth/me",
        headers=faculty_headers,
    )
    assert response.status_code == 200
    faculty_profile = response.json()
    assert faculty_profile["email"] == "faculty@university.edu"
    assert "faculty" in [role["name"] for role in faculty_profile["roles"]]
    
    # Student should be able to get their profile
    response = requests.get(
        f"{api_base_url}/auth/me",
        headers=student_headers,
    )
    assert response.status_code == 200
    student_profile = response.json()
    assert student_profile["email"] == "student1@university.edu"
    assert "student" in [role["name"] for role in student_profile["roles"]]

def test_update_user_profile(api_base_url, admin_headers, student_headers):
    """Test updating user profile information."""
    # First get the current profile
    response = requests.get(
        f"{api_base_url}/auth/me",
        headers=student_headers,
    )
    assert response.status_code == 200
    original_profile = response.json()
    
    # Update the profile
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    update_data = {
        "full_name": f"Updated Student Name {timestamp}",
        "phone_number": f"555-{timestamp[-6:]}",
        "address": f"123 Test St, Test City {timestamp}"
    }
    
    response = requests.put(
        f"{api_base_url}/users/{original_profile['id']}/profile",
        headers=student_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_profile = response.json()
    
    # Verify the profile was updated
    assert updated_profile["full_name"] == update_data["full_name"]
    if "phone_number" in updated_profile:
        assert updated_profile["phone_number"] == update_data["phone_number"]
    if "address" in updated_profile:
        assert updated_profile["address"] == update_data["address"]
    
    # Verify that a student cannot update another student's profile
    other_user_id = original_profile["id"] + 1  # Assuming sequential IDs
    response = requests.put(
        f"{api_base_url}/users/{other_user_id}/profile",
        headers=student_headers,
        json=update_data,
    )
    assert response.status_code in [401, 403, 404]  # Either unauthorized, forbidden, or not found
    
    # Admin should be able to update any user's profile
    admin_update_data = {
        "full_name": f"Admin Updated Name {timestamp}",
    }
    response = requests.put(
        f"{api_base_url}/users/{original_profile['id']}/profile",
        headers=admin_headers,
        json=admin_update_data,
    )
    assert response.status_code == 200
    admin_updated_profile = response.json()
    assert admin_updated_profile["full_name"] == admin_update_data["full_name"]

def test_change_password(api_base_url, student_headers):
    """Test password change functionality."""
    # Get the current user
    response = requests.get(
        f"{api_base_url}/auth/me",
        headers=student_headers,
    )
    assert response.status_code == 200
    user = response.json()
    
    # Change password
    password_data = {
        "current_password": "student123",  # Current password
        "new_password": "newpassword123",  # New password
    }
    response = requests.post(
        f"{api_base_url}/auth/change-password",
        headers=student_headers,
        json=password_data,
    )
    assert response.status_code == 200
    
    # Try logging in with the new password
    login_data = {
        "username": user["email"],
        "password": "newpassword123",
    }
    response = requests.post(
        f"{api_base_url}/auth/login",
        data=login_data,
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Change the password back for future tests
    new_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    password_data = {
        "current_password": "newpassword123",  # Current password
        "new_password": "student123",  # Original password
    }
    response = requests.post(
        f"{api_base_url}/auth/change-password",
        headers=new_headers,
        json=password_data,
    )
    assert response.status_code == 200
