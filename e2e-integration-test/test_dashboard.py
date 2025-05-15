import pytest
import requests
import json
from datetime import datetime

def test_dashboard_summary(api_base_url, admin_headers):
    """Test the dashboard summary endpoint."""
    # Get the dashboard summary
    response = requests.get(
        f"{api_base_url}/dashboard/summary",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify the structure of the dashboard summary
    assert "student_count" in data
    assert "faculty_count" in data
    assert "total_fees" in data
    assert "total_paid" in data
    assert "total_pending" in data
    assert "recent_payments" in data
    assert isinstance(data["recent_payments"], list)
    
    # Verify that the counts are reasonable
    assert data["student_count"] >= 0
    assert data["faculty_count"] >= 0
    assert data["total_fees"] >= 0
    assert data["total_paid"] >= 0
    assert data["total_pending"] >= 0

def test_dashboard_access_control(api_base_url, admin_headers, faculty_headers, student_headers):
    """Test access control for dashboard endpoints."""
    # Admin should have access to the dashboard
    response = requests.get(
        f"{api_base_url}/dashboard/summary",
        headers=admin_headers,
    )
    assert response.status_code == 200
    
    # Faculty should have access to the dashboard
    response = requests.get(
        f"{api_base_url}/dashboard/summary",
        headers=faculty_headers,
    )
    assert response.status_code == 200
    
    # Students should have limited access to the dashboard
    response = requests.get(
        f"{api_base_url}/dashboard/summary",
        headers=student_headers,
    )
    # Either they get a filtered view or are denied access
    if response.status_code == 200:
        # If they get access, it should be a filtered view
        data = response.json()
        # Student view should not include sensitive information
        assert "student_count" not in data or data["student_count"] <= 1
        assert "faculty_count" not in data
    else:
        # Or they are denied access
        assert response.status_code in [401, 403]

def test_financial_reporting(api_base_url, admin_headers):
    """Test the financial reporting functionality."""
    # Get the current semester
    response = requests.get(
        f"{api_base_url}/finance/semesters",
        headers=admin_headers,
    )
    assert response.status_code == 200
    semesters = response.json()
    assert len(semesters) > 0
    
    # Get financial summary for the current semester
    semester_id = semesters[0]["id"]
    response = requests.get(
        f"{api_base_url}/finance/summary?semester_id={semester_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify the structure of the financial summary
    assert "total_fees" in data
    assert "total_paid" in data
    assert "total_pending" in data
    assert "student_count" in data
    assert "payment_count" in data
    
    # Create a payment to ensure there's data for reporting
    # First create a student fee if needed
    response = requests.get(
        f"{api_base_url}/finance/student-fees?semester_id={semester_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    fees = response.json()
    
    if not fees:
        # Create a new fee
        fee_data = {
            "student_id": 3,  # Assuming student1 has ID 3
            "semester_id": semester_id,
            "amount": 2000.00,
            "description": "Tuition Fee for Reporting Test",
        }
        response = requests.post(
            f"{api_base_url}/finance/student-fees",
            headers=admin_headers,
            json=fee_data,
        )
        assert response.status_code == 200
        fee = response.json()
    else:
        fee = fees[0]
    
    # Make a payment
    payment_data = {
        "student_id": fee["student_id"],
        "student_fee_id": fee["id"],
        "amount": fee["amount"] / 2,  # Pay half of the fee
        "payment_method": "Bank Transfer",
        "transaction_id": f"TEST-REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "notes": "Test payment for reporting",
    }
    response = requests.post(
        f"{api_base_url}/finance/payments",
        headers=admin_headers,
        json=payment_data,
    )
    assert response.status_code == 200
    
    # Get the updated financial summary
    response = requests.get(
        f"{api_base_url}/finance/summary?semester_id={semester_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    updated_data = response.json()
    
    # Verify that the payment was included in the summary
    assert updated_data["payment_count"] >= 1
    assert updated_data["total_paid"] > 0
