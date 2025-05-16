# University Web Application

A web application for university management with authentication and financial management features.

## Features

### 1. User Authentication & Authorization
- Student, Faculty, Admin login portals
- Role-based access control
- Password reset functionality

### 2. Academic Structure
- Multi-institute university organization
- Course management across institutes
- Flexible semester/year-based academic periods
- Student enrollment in multiple courses

### 3. Financial Management
- Tuition fees payment portal
- Course and semester-specific fee assignment
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

## Data Schema Documentation

### Academic Structure Schemas

#### Institute
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the institute |
| name | String | Full name of the institute |
| code | String | Short code for the institute (e.g., 'ENG', 'BUS') |
| description | String | Description of the institute |
| created_at | DateTime | When the institute record was created |
| updated_at | DateTime | When the institute record was last updated |
| courses | Array of Course | List of courses offered by this institute |

#### Course
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the course |
| institute_id | Integer | Reference to the institute offering this course |
| name | String | Full name of the course (e.g., 'Bachelor of Computer Science') |
| code | String | Course code (e.g., 'BCS') |
| duration_years | Integer | Standard duration of the course in years |
| description | String | Description of the course |
| is_active | Boolean | Whether the course is currently active |
| created_at | DateTime | When the course record was created |
| updated_at | DateTime | When the course record was last updated |
| institute | Institute | The associated institute object |
| semesters | Array of Semester | List of semesters/years in this course |
| students | Array of User | List of students enrolled in this course |

### User Management Schemas

#### Role
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the role |
| name | String | Role name (e.g., 'admin', 'faculty', 'student') |
| description | String | Description of the role's permissions and responsibilities |

#### User
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the user |
| email | String | User's email address (used for login) |
| full_name | String | User's full name |
| is_active | Boolean | Whether the user account is active |
| hashed_password | String | Securely hashed password (not exposed in API) |
| created_at | DateTime | When the user account was created |
| updated_at | DateTime | When the user account was last updated |
| roles | Array of Role | List of roles assigned to the user |
| courses | Array of Course | List of courses the user is enrolled in (for students) |

#### Token
| Field | Type | Description |
|-------|------|-------------|
| access_token | String | JWT token for authentication |
| token_type | String | Type of token (typically 'bearer') |

### Financial Management Schemas

#### Semester
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the semester |
| course_id | Integer | Reference to the course this semester belongs to |
| name | String | Semester name (e.g., 'Fall 2025', '1st Year') |
| type | String | Type of academic period ('semester' or 'year') |
| order_in_course | Integer | Order of this semester/year in the course (e.g., 1, 2, 3) |
| start_date | DateTime | Start date of the semester |
| end_date | DateTime | End date of the semester |
| course | Course | The associated course object |

#### FeeStructure
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the fee structure |
| semester_id | Integer | Reference to the semester this fee applies to |
| name | String | Name of the fee (e.g., 'Tuition Fee', 'Library Fee') |
| amount | Float | Amount of the fee |
| description | String | Description of what the fee covers |
| created_at | DateTime | When the fee structure was created |
| updated_at | DateTime | When the fee structure was last updated |
| semester | Semester | The associated semester object |

#### StudentFee
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the student fee |
| student_id | Integer | Reference to the student this fee is assigned to |
| course_id | Integer | Reference to the course this fee is for |
| semester_id | Integer | Reference to the semester this fee applies to |
| amount | Float | Amount of the fee for this student |
| description | String | Description or notes about this student's fee |
| created_at | DateTime | When the student fee was created |
| updated_at | DateTime | When the student fee was last updated |
| course | Course | The associated course object |
| semester | Semester | The associated semester object |

#### Payment
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the payment |
| student_id | Integer | Reference to the student making the payment |
| student_fee_id | Integer | Reference to the fee being paid |
| amount | Float | Amount of the payment |
| payment_date | DateTime | When the payment was made |
| payment_method | String | Method of payment (e.g., 'Credit Card', 'Bank Transfer') |
| transaction_id | String | External transaction identifier (if applicable) |
| notes | String | Additional notes about the payment |
| student_fee | StudentFee | The associated student fee object |

#### Receipt
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique identifier for the receipt |
| payment_id | Integer | Reference to the payment this receipt is for |
| receipt_number | String | Unique receipt number (format: RCPT-{payment.id}-{course_code}-{semester_code}-{timestamp}) |
| generated_at | DateTime | When the receipt was generated |
| pdf_path | String | Path to the PDF file of the receipt |

### Combined Response Schemas

#### PaymentWithReceipt
| Field | Type | Description |
|-------|------|-------------|
| ... | ... | All fields from Payment schema |
| receipt | Receipt | The associated receipt object (if available) |
| student_fee | StudentFee | The associated student fee object with semester information |

#### StudentFeeWithPayments
| Field | Type | Description |
|-------|------|-------------|
| ... | ... | All fields from StudentFee schema |
| payments | Array of PaymentWithReceipt | List of payments made for this fee |


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
