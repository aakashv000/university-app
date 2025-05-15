import pytest
import requests
import json
from datetime import datetime

def test_receipt_generation_flow(api_base_url, admin_headers):
    """Test the complete flow of generating a receipt."""
    # Step 1: Create a new semester
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
    semester = response.json()
    
    # Step 2: Create a student fee
    fee_data = {
        "student_id": 3,  # Assuming student1 has ID 3
        "semester_id": semester["id"],
        "amount": 1500.00,
        "description": "Tuition Fee for Test Receipt",
    }
    response = requests.post(
        f"{api_base_url}/finance/student-fees",
        headers=admin_headers,
        json=fee_data,
    )
    assert response.status_code == 200
    student_fee = response.json()
    
    # Step 3: Make a payment
    payment_data = {
        "student_id": 3,
        "student_fee_id": student_fee["id"],
        "amount": 750.00,  # Partial payment
        "payment_method": "Credit Card",
        "transaction_id": f"TEST-RECEIPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "notes": "Test payment for receipt generation",
    }
    response = requests.post(
        f"{api_base_url}/finance/payments",
        headers=admin_headers,
        json=payment_data,
    )
    assert response.status_code == 200
    payment = response.json()
    
    # Step 4: Verify receipt was generated
    assert "receipt" in payment
    assert payment["receipt"] is not None
    receipt_id = payment["receipt"]["id"]
    
    # Step 5: Get receipt details
    response = requests.get(
        f"{api_base_url}/finance/receipts/{receipt_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    receipt = response.json()
    assert receipt["id"] == receipt_id
    assert receipt["payment_id"] == payment["id"]
    assert receipt["amount"] == payment_data["amount"]
    
    # Step 6: Download receipt PDF
    response = requests.get(
        f"{api_base_url}/finance/receipts/{receipt_id}/pdf",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert int(response.headers["Content-Length"]) > 0

def test_receipt_access_permissions(api_base_url, admin_headers, faculty_headers, student_headers):
    """Test that receipts can only be accessed by authorized users."""
    # First create a receipt as admin
    # Step 1: Create a semester
    semester_data = {
        "name": f"Perm Test Semester {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-05-31T00:00:00Z",
    }
    response = requests.post(
        f"{api_base_url}/finance/semesters",
        headers=admin_headers,
        json=semester_data,
    )
    semester = response.json()
    
    # Step 2: Create a student fee
    fee_data = {
        "student_id": 3,  # Student 1
        "semester_id": semester["id"],
        "amount": 1000.00,
        "description": "Tuition Fee for Permission Test",
    }
    response = requests.post(
        f"{api_base_url}/finance/student-fees",
        headers=admin_headers,
        json=fee_data,
    )
    student_fee = response.json()
    
    # Step 3: Make a payment and generate receipt
    payment_data = {
        "student_id": 3,
        "student_fee_id": student_fee["id"],
        "amount": 500.00,
        "payment_method": "Cash",
        "transaction_id": f"TEST-PERM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "notes": "Test payment for permission test",
    }
    response = requests.post(
        f"{api_base_url}/finance/payments",
        headers=admin_headers,
        json=payment_data,
    )
    payment = response.json()
    receipt_id = payment["receipt"]["id"]
    
    # Test 1: Admin can access any receipt
    response = requests.get(
        f"{api_base_url}/finance/receipts/{receipt_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    
    # Test 2: Faculty can access any receipt
    response = requests.get(
        f"{api_base_url}/finance/receipts/{receipt_id}",
        headers=faculty_headers,
    )
    assert response.status_code == 200
    
    # Test 3: Student can only access their own receipts
    response = requests.get(
        f"{api_base_url}/finance/receipts/{receipt_id}",
        headers=student_headers,
    )
    assert response.status_code == 200  # This should work since we used student_id 3
    
    # Step 4: Create another receipt for a different student
    fee_data = {
        "student_id": 4,  # Student 2
        "semester_id": semester["id"],
        "amount": 1000.00,
        "description": "Tuition Fee for Student 2",
    }
    response = requests.post(
        f"{api_base_url}/finance/student-fees",
        headers=admin_headers,
        json=fee_data,
    )
    student_fee = response.json()
    
    payment_data = {
        "student_id": 4,
        "student_fee_id": student_fee["id"],
        "amount": 500.00,
        "payment_method": "Cash",
        "transaction_id": f"TEST-PERM2-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "notes": "Test payment for student 2",
    }
    response = requests.post(
        f"{api_base_url}/finance/payments",
        headers=admin_headers,
        json=payment_data,
    )
    payment = response.json()
    receipt_id_student2 = payment["receipt"]["id"]
    
    # Test 4: Student 1 should not be able to access Student 2's receipt
    response = requests.get(
        f"{api_base_url}/finance/receipts/{receipt_id_student2}",
        headers=student_headers,
    )
    assert response.status_code in [401, 403, 404]  # Either unauthorized, forbidden, or not found
