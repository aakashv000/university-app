# Getting Started with University App

This guide will help you run the University Web Application on both Windows (using Docker) and Linux environments.

## Prerequisites

### Windows
- Docker Desktop installed and running
- Git (optional, for cloning the repository)

### Linux
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Git (optional, for cloning the repository)

## Running the Application

### Using Docker (Recommended for Windows)

1. **Start the application using Docker Compose:**

   ```bash
   docker-compose up --build
   ```

   This will:
   - Build and start the backend API (FastAPI)
   - Build and start the frontend (React)
   - Start a PostgreSQL database
   - Initialize the database with sample data

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Stop the application:**

   ```bash
   docker-compose down
   ```

### Running Locally

#### Backend (Python/FastAPI)

1. **Set up a virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   cd backend
   pip install -r ../requirements.txt
   ```

3. **Set up PostgreSQL:**
   
   Make sure PostgreSQL is running and create a database:
   
   ```bash
   # Linux
   sudo -u postgres createdb university_app
   ```

   Update the `.env` file in the `backend` directory with your database credentials.

4. **Initialize the database:**

   ```bash
   cd backend
   python -m app.db.init_db
   python initial_data.py
   ```

5. **Start the backend server:**

   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend (React)

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**

   ```bash
   cd frontend
   npm start
   ```

3. **Access the frontend:**
   
   Open http://localhost:3000 in your browser.

### Using the Helper Script

We've included a helper script to run both the backend and frontend:

```bash
# Run both backend and frontend
python run_local.py

# Run only the backend
python run_local.py --backend-only

# Run only the frontend
python run_local.py --frontend-only
```

## Demo Accounts

The application is pre-configured with the following demo accounts:

| Role     | Email                   | Password   |
|----------|-------------------------|------------|
| Admin    | admin@university.edu    | admin123   |
| Faculty  | faculty@university.edu  | faculty123 |
| Student  | student1@university.edu | student123 |
| Student  | student2@university.edu | student123 |

## Running Tests

To run the E2E integration tests:

```bash
cd e2e-integration-test
pip install -r requirements.txt
python run_tests.py
```

Or using Docker:

```bash
cd e2e-integration-test
docker-compose -f docker-compose.test.yml up --build
```

## Project Structure

```
university-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Core functionality
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── main.py              # Application entry point
│   └── initial_data.py      # Sample data initialization
├── frontend/                # React frontend
│   ├── public/              # Static files
│   └── src/                 # React components and logic
├── e2e-integration-test/    # End-to-end API tests
├── docker-compose.yml       # Docker Compose configuration
└── run_local.py             # Helper script to run locally
```

## Development Commands and Key Points

### Docker Commands (Windows PowerShell)

#### Starting the Application
```powershell
# Start all services
docker-compose up -d

# Start only specific services
docker-compose up -d backend frontend

# Start with database only
docker-compose -f docker-compose-db.yml up -d
```

#### Restarting Services
```powershell
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

#### Rebuilding Services
```powershell
# Rebuild and restart a service after code changes
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

#### Viewing Logs
```powershell
# View logs from all services
docker-compose logs

# View logs from specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines of logs
docker logs university-app-backend-1 --tail 100
```

#### Stopping Services
```powershell
# Stop all services
docker-compose down

# Stop all services and remove volumes
docker-compose down -v
```

### API Testing

#### Authentication
```powershell
# Login and get token
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body "username=admin@university.edu&password=admin123"
$token = $response.access_token

# Use token for authenticated requests
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Method Get -Headers @{Authorization = "Bearer $token"}
```

#### Testing Receipt Downloads
```powershell
# Get all receipts for a student
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body "username=student1@university.edu&password=student123").access_token
Invoke-RestMethod -Uri "http://localhost:8000/api/finance/students/3/receipts" -Method Get -Headers @{Authorization = "Bearer $token"}

# Download a receipt
Invoke-WebRequest -Uri "http://localhost:8000/api/finance/receipts/1/download" -Method Get -Headers @{Authorization = "Bearer $token"} -OutFile "receipt.pdf"
```

### Key Development Points

1. **Database Migrations**
   - Alembic migrations are in `backend/alembic/`
   - Run migrations automatically when the backend starts
   - For manual migrations: `docker-compose exec backend alembic upgrade head`

2. **Environment Variables**
   - Backend environment variables are in `backend/.env`
   - Frontend environment variables are in `frontend/.env`
   - Docker environment variables are in `docker-compose.yml`

3. **Authentication Flow**
   - JWT tokens are used for authentication
   - Tokens expire after 30 minutes by default
   - Role-based access control is implemented

4. **Common Issues and Solutions**
   - If login doesn't work, check backend logs for authentication errors
   - If receipts can't be downloaded, ensure the receipts directory exists
   - For CORS issues, check the allowed origins in `backend/app/core/config.py`
   - For database connection issues, verify PostgreSQL is running and credentials are correct

5. **Type Safety**
   - Frontend uses TypeScript with strict mode enabled
   - Backend uses Pydantic models for request/response validation
   - Always maintain type safety when making changes

## Next Steps

1. **Customize the application** to fit your specific university needs
2. **Add more features** such as:
   - Course registration
   - Attendance tracking
   - Grading system
   - Library management
3. **Enhance security** for production deployment
4. **Set up CI/CD** for automated testing and deployment
