# AYRAQ Backend API - Complete Solution

🚀 **Comprehensive FastAPI backend for AYRAQ** - AI-powered mobile application for women's safety with complete feature set including user management, threat detection, chat system, and support resources.

## 🎯 Complete Features

### 🔐 Authentication & User Management
- ✅ User registration with email/phone uniqueness validation
- ✅ JWT-based authentication system
- ✅ Profile management and updates
- ✅ User search functionality
- ✅ Password hashing and security

### 🤝 Social Features
- ✅ Connection/friend request system
- ✅ Accept/reject/block connection requests
- ✅ Real-time chat system with conversations
- ✅ Message types: text, image, file, location
- ✅ Unread message tracking

### 🛡️ AI-Powered Safety Features
- ✅ Content threat analysis with AI
- ✅ Multiple threat types: cyberbullying, harassment, stalking, phishing
- ✅ Confidence scoring and threat levels
- ✅ Evidence storage with encryption
- ✅ File integrity verification with hash values

### 🔔 Notification System
- ✅ Real-time notifications with priorities
- ✅ Type categorization (threat alerts, messages, etc.)
- ✅ Read/unread status management
- ✅ Notification statistics and analytics

### 🆘 Support & Legal Resources
- ✅ Legal guidance database with categories
- ✅ Support resources (helplines, counseling, legal aid)
- ✅ Emergency contact management
- ✅ Location-based resource filtering

### ⚙️ User Settings & Privacy
- ✅ Comprehensive user settings management
- ✅ Privacy controls and preferences
- ✅ Notification preferences
- ✅ Threat detection toggles

### 🔒 Security & Privacy
- ✅ Row Level Security (RLS) with Supabase
- ✅ Encrypted evidence storage
- ✅ JWT token authentication
- ✅ CORS configuration for mobile apps
- ✅ Input validation and sanitization

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your Supabase credentials:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
DEBUG=True
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Database Setup

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the SQL commands from `database_schema.sql` to create the required tables

### 4. Run the Server

```bash
python run.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `GET /api/v1/auth/health` - Auth service health check

### General

- `GET /` - Root endpoint
- `GET /health` - Application health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## User Registration

### Endpoint: `POST /api/v1/auth/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "user_type": "Student",
  "gender": "Male",
  "dob": "1995-01-15"
}
```

**Success Response (201):**
```json
{
  "message": "Registration successful! Welcome to AYRAQ.",
  "success": true,
  "user": {
    "id": "uuid-here",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "user_type": "Student",
    "gender": "Male",
    "dob": "1995-01-15",
    "avatar": "assets/male_avatar.png",
    "created_at": "2025-01-19T10:30:00Z"
  }
}
```

**Error Responses:**

Email already exists (400):
```json
{
  "message": "Registration failed",
  "error": "Email address is already registered. Please use a different email or try logging in.",
  "field": "email"
}
```

Phone already exists (400):
```json
{
  "message": "Registration failed",
  "error": "Phone number is already registered. Please use a different phone number or try logging in.",
  "field": "phone"
}
```

## Validation Rules

- **Name**: Minimum 2 characters
- **Email**: Valid email format
- **Phone**: Valid international phone number format
- **User Type**: Must be one of: Student, Professional, Other
- **Gender**: Must be one of: Male, Female, Other
- **Date of Birth**: YYYY-MM-DD format, user must be at least 13 years old

## Development

### Project Structure
```
backend/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── __init__.py
│   └── main.py
├── .env.example
├── requirements.txt
├── run.py
├── database_schema.sql
└── README.md
```

### Testing

You can test the API using:
- Interactive docs at `http://localhost:8000/docs`
- curl commands
- Postman or similar API testing tools

Example curl command:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test User",
       "email": "test@example.com",
       "phone": "+1234567890",
       "user_type": "Student",
       "gender": "Male",
       "dob": "1995-01-15"
     }'
```
