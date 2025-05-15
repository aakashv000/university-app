import pytest
import requests
from datetime import datetime

def test_get_semesters(api_base_url, admin_headers):
    """Test getting all semesters."""
    response = requests.get(
        f"{api_base_url}/finance/semesters",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "id" in data[0]
        assert "name" in data[0]
        assert "start_date" in data[0]
        assert "end_date" in data[0]

def test_create_semester(api_base_url, admin_headers):
    """Test creating a new semester."""
    semester_data = {
        "name": f"Test Semester {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-05-31T00:00:00Z",
    }
    response = requests.post(
        f"{api_base_url}/finance/semesters",
        headers=admin_headers,
        json=semester_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == semester_data["name"]

def test_get_student_fees(api_base_url, admin_headers):
    """Test getting student fees."""
    response = requests.get(
        f"{api_base_url}/finance/student-fees",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_student_fee(api_base_url, admin_headers):
    """Test creating a student fee."""
    # First get a semester
    response = requests.get(
        f"{api_base_url}/finance/semesters",
        headers=admin_headers,
    )
    assert response.status_code == 200
    semesters = response.json()
    assert len(semesters) > 0
    
    # Create a student fee
    fee_data = {
        "student_id": 3,  # Assuming student1 has ID 3
        "semester_id": semesters[0]["id"],
        "amount": 1000.00,
        "description": "Test fee",
    }
    response = requests.post(
        f"{api_base_url}/finance/student-fees",
        headers=admin_headers,
        json=fee_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == fee_data["student_id"]
    assert data["amount"] == fee_data["amount"]

def test_get_payments(api_base_url, admin_headers):
    """Test getting payments."""
    response = requests.get(
        f"{api_base_url}/finance/payments",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_payment_and_receipt(api_base_url, admin_headers):
    """Test creating a payment and generating a receipt."""
    # First get student fees
    response = requests.get(
        f"{api_base_url}/finance/student-fees",
        headers=admin_headers,
    )
    assert response.status_code == 200
    fees = response.json()
    assert len(fees) > 0
    
    # Create a payment
    payment_data = {
        "student_id": fees[0]["student_id"],
        "student_fee_id": fees[0]["id"],
        "amount": fees[0]["amount"] / 2,  # Pay half of the fee
        "payment_method": "Credit Card",
        "transaction_id": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "notes": "Test payment",
    }
    response = requests.post(
        f"{api_base_url}/finance/payments",
        headers=admin_headers,
        json=payment_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == payment_data["student_id"]
    assert data["amount"] == payment_data["amount"]
    assert "receipt" in data
    assert data["receipt"] is not None

def test_get_finance_summary(api_base_url, faculty_headers):
    """Test getting finance summary."""
    response = requests.get(
        f"{api_base_url}/finance/summary",
        headers=faculty_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_fees" in data
    assert "total_paid" in data
    assert "total_pending" in data
    assert "student_count" in data
    assert "payment_count" in data

def test_student_access_restrictions(api_base_url, student_headers):
    """Test that students can only access their own data."""
    # Students should be able to see their own fees
    response = requests.get(
        f"{api_base_url}/finance/student-fees",
        headers=student_headers,
    )
    assert response.status_code == 200
    
    # Students should not be able to create fees
    fee_data = {
        "student_id": 3,
        "semester_id": 1,
        "amount": 1000.00,
        "description": "Test fee",
    }
    response = requests.post(
        f"{api_base_url}/finance/student-fees",
        headers=student_headers,
        json=fee_data,
    )
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden
    
    # Students should not be able to access finance summary
    response = requests.get(
        f"{api_base_url}/finance/summary",
        headers=student_headers,
    )
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden
