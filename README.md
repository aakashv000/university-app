# University Web Application

A web application for university management with authentication and financial management features.

## Features

### 1. User Authentication & Authorization
- Student, Faculty, Admin login portals
- Role-based access control
- Password reset functionality

### 2. Financial Management
- Tuition fees payment portal
- Custom fee assignment on a per-semester basis
- On-the-fly receipt generation and printing
- Financial reporting with filtering and sorting capabilities

## Tech Stack

### Backend
- Python with FastAPI
- PostgreSQL database
- SQLAlchemy ORM
- JWT Authentication

### Frontend
- React with TypeScript
- Material-UI for components
- Redux Toolkit for state management

### Development & Deployment
- Docker for local development on Windows
- Native deployment on Linux
- E2E integration tests

## Getting Started

### Local Development (Windows with Docker)

1. Install Docker Desktop
2. Clone this repository
3. Run `docker-compose up` to start all services
4. Access the application at http://localhost:3000

### Production Deployment (Linux)

1. Install required dependencies:
   ```
   sudo apt update
   sudo apt install python3 python3-pip postgresql nginx
   ```
2. Set up PostgreSQL database
3. Configure environment variables
4. Run the backend using Gunicorn
5. Serve the frontend using Nginx

## Testing

Run E2E integration tests:
```
cd e2e-integration-test
pytest
```
