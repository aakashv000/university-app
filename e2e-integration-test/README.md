# E2E Integration Tests for University App

This directory contains end-to-end integration tests for the University App API.

## Overview

The tests verify that all API endpoints work correctly and that the business logic is properly implemented. The tests cover:

- Authentication and authorization
- User management
- Financial management (fees, payments, receipts)

## Running the Tests

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized testing)

### Local Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure the backend API is running and accessible at the URL specified in the `.env` file.

3. Run the tests:
   ```
   python run_tests.py
   ```

### Using Docker

1. Run the tests using Docker Compose:
   ```
   docker-compose -f docker-compose.test.yml up --build
   ```

   This will:
   - Start a PostgreSQL database
   - Start the backend API
   - Run the tests against the API
   - Generate a test report

2. View the test report in the `reports` directory.

## Test Structure

- `conftest.py` - Test fixtures and configuration
- `test_auth.py` - Authentication and authorization tests
- `test_users.py` - User management tests
- `test_finance.py` - Financial management tests

## Environment Variables

The tests use the following environment variables, which can be set in the `.env` file:

- `API_BASE_URL` - The base URL of the API (default: `http://localhost:8000/api`)

## Test Users

The tests use the following predefined users:

- Admin: `admin@university.edu` / `admin123`
- Faculty: `faculty@university.edu` / `faculty123`
- Student: `student1@university.edu` / `student123`
