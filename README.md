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

## Data Schema Documentation

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
| name | String | Semester name (e.g., 'Fall 2025') |
| start_date | DateTime | Start date of the semester |
| end_date | DateTime | End date of the semester |

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
| semester_id | Integer | Reference to the semester this fee applies to |
| amount | Float | Amount of the fee for this student |
| description | String | Description or notes about this student's fee |
| created_at | DateTime | When the student fee was created |
| updated_at | DateTime | When the student fee was last updated |
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
| receipt_number | String | Unique receipt number (format: RCPT-{payment.id}-{student_fee.id}-{semester_code}-{timestamp}) |
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
