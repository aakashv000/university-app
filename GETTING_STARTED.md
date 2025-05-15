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

## Next Steps

1. **Customize the application** to fit your specific university needs
2. **Add more features** such as:
   - Course registration
   - Attendance tracking
   - Grading system
   - Library management
3. **Enhance security** for production deployment
4. **Set up CI/CD** for automated testing and deployment
