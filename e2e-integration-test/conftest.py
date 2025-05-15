import os
import pytest
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Test user credentials
TEST_ADMIN_EMAIL = "admin@university.edu"
TEST_ADMIN_PASSWORD = "admin123"
TEST_FACULTY_EMAIL = "faculty@university.edu"
TEST_FACULTY_PASSWORD = "faculty123"
TEST_STUDENT_EMAIL = "student1@university.edu"
TEST_STUDENT_PASSWORD = "student123"

@pytest.fixture
def api_base_url():
    """Return the API base URL."""
    return API_BASE_URL

@pytest.fixture
def admin_token():
    """Get admin authentication token."""
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={
            "username": TEST_ADMIN_EMAIL,
            "password": TEST_ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def faculty_token():
    """Get faculty authentication token."""
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={
            "username": TEST_FACULTY_EMAIL,
            "password": TEST_FACULTY_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def student_token():
    """Get student authentication token."""
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={
            "username": TEST_STUDENT_EMAIL,
            "password": TEST_STUDENT_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    """Return headers with admin authentication token."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def faculty_headers(faculty_token):
    """Return headers with faculty authentication token."""
    return {"Authorization": f"Bearer {faculty_token}"}

@pytest.fixture
def student_headers(student_token):
    """Return headers with student authentication token."""
    return {"Authorization": f"Bearer {student_token}"}
