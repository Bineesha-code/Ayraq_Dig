# AYRAQ Backend API - Complete Documentation

## 🚀 Overview

Complete FastAPI backend for AYRAQ - AI-powered mobile application for women's safety with comprehensive features including user management, threat detection, chat system, and support resources.

## 📋 Base URL
```
http://localhost:8000/api/v1
```

## 🔐 Authentication

All protected endpoints require Bearer token authentication:
```
Authorization: Bearer <your_jwt_token>
```

## 📚 API Endpoints

### 🔑 Authentication (`/auth`)

#### Register User
- **POST** `/auth/register`
- **Body**: `UserRegistration`
- **Response**: User registration success with user details

#### Login User  
- **POST** `/auth/login`
- **Body**: `UserLogin` (email/phone + password)
- **Response**: JWT token + user details

#### Get Current User
- **GET** `/auth/me` 🔒
- **Response**: Current user profile

#### Update Profile
- **PUT** `/auth/me` 🔒
- **Body**: `UserUpdate`
- **Response**: Updated user profile

### 🤝 Connections (`/connections`)

#### Send Connection Request
- **POST** `/connections/request` 🔒
- **Body**: `ConnectionRequest`
- **Response**: Connection request sent

#### Get Connection Requests
- **GET** `/connections/requests` 🔒
- **Query**: `status`, `page`, `limit`
- **Response**: List of connection requests

#### Update Connection Request
- **PUT** `/connections/requests/{connection_id}` 🔒
- **Body**: `ConnectionUpdate` (accept/reject/block)
- **Response**: Request status updated

#### Get Connections (Friends)
- **GET** `/connections/` 🔒
- **Query**: `page`, `limit`
- **Response**: List of accepted connections

### 💬 Chat System (`/chat`)

#### Create Conversation
- **POST** `/chat/conversations` 🔒
- **Body**: `ConversationCreate`
- **Response**: New conversation created

#### Get Conversations
- **GET** `/chat/conversations` 🔒
- **Response**: List of user conversations with unread counts

#### Send Message
- **POST** `/chat/messages` 🔒
- **Body**: `MessageCreate`
- **Response**: Message sent successfully

#### Get Messages
- **GET** `/chat/conversations/{conversation_id}/messages` 🔒
- **Query**: `page`, `limit`
- **Response**: Paginated messages in conversation

### 🛡️ Threat Detection (`/threats`)

#### Analyze Content for Threats
- **POST** `/threats/analyze` 🔒
- **Body**: `ThreatDetectionCreate`
- **Response**: `ThreatAnalysisResult` with AI analysis

#### Get Threat Detections
- **GET** `/threats/detections` 🔒
- **Query**: `threat_type`, `threat_level`, `page`, `limit`
- **Response**: List of threat detections

#### Update Threat Detection
- **PUT** `/threats/detections/{detection_id}` 🔒
- **Body**: `ThreatDetectionUpdate`
- **Response**: Detection updated

#### Store Evidence
- **POST** `/threats/evidence` 🔒
- **Body**: `EvidenceCreate`
- **Response**: Evidence stored with hash verification

#### Get Evidence
- **GET** `/threats/evidence` 🔒
- **Query**: `evidence_type`, `page`, `limit`
- **Response**: List of stored evidence

### 🔔 Notifications (`/notifications`)

#### Get Notifications
- **GET** `/notifications/` 🔒
- **Query**: `notification_type`, `priority`, `is_read`, `page`, `limit`
- **Response**: Paginated notifications with unread count

#### Mark Notification as Read
- **PUT** `/notifications/{notification_id}` 🔒
- **Body**: `NotificationUpdate`
- **Response**: Notification updated

#### Mark All as Read
- **PUT** `/notifications/mark-all-read` 🔒
- **Response**: All notifications marked as read

#### Delete Notification
- **DELETE** `/notifications/{notification_id}` 🔒
- **Response**: Notification deleted

#### Get Notification Stats
- **GET** `/notifications/stats` 🔒
- **Response**: Notification statistics by type and priority

### 🆘 Support & Resources (`/support`)

#### Get Legal Guidance
- **GET** `/support/legal-guidance`
- **Query**: `category`, `jurisdiction`
- **Response**: List of legal guidance resources (public)

#### Get Support Resources
- **GET** `/support/resources`
- **Query**: `resource_type`, `is_emergency`, `country`, `state_province`, `city`
- **Response**: List of support resources (public)

#### Emergency Contacts Management
- **POST** `/support/emergency-contacts` 🔒 - Create contact
- **GET** `/support/emergency-contacts` 🔒 - Get contacts
- **PUT** `/support/emergency-contacts/{contact_id}` 🔒 - Update contact
- **DELETE** `/support/emergency-contacts/{contact_id}` 🔒 - Delete contact

#### User Settings
- **GET** `/support/settings` 🔒 - Get user settings
- **PUT** `/support/settings` 🔒 - Update user settings

## 🎯 Key Features

### ✅ User Management
- Registration with email/phone uniqueness
- JWT-based authentication
- Profile management
- User search functionality

### ✅ Social Features
- Connection/friend request system
- Real-time chat with file support
- User status and activity tracking

### ✅ AI-Powered Safety
- Content threat analysis
- Multiple threat types detection
- Confidence scoring
- Evidence storage with encryption

### ✅ Notification System
- Real-time alerts
- Priority-based notifications
- Type categorization
- Read/unread status

### ✅ Support System
- Legal guidance resources
- Emergency support contacts
- Helpline information
- Location-based resources

### ✅ Privacy & Security
- Row-level security (RLS)
- Encrypted evidence storage
- File integrity verification
- Privacy settings management

## 🔧 Data Models

### User Registration
```json
{
  "name": "string",
  "email": "user@example.com",
  "phone": "+1234567890",
  "user_type": "Student|Professional|Other",
  "gender": "Male|Female|Other",
  "dob": "1995-01-15"
}
```

### Threat Analysis Result
```json
{
  "threat_detected": true,
  "threat_type": "cyberbullying",
  "threat_level": "high",
  "confidence_score": 0.85,
  "explanation": "Detected potential cyberbullying...",
  "recommended_actions": ["Document evidence", "Report to authorities"]
}
```

### Message
```json
{
  "conversation_id": "uuid",
  "message_text": "Hello!",
  "message_type": "text|image|file|location",
  "file_url": "optional_file_url"
}
```

## 🚨 Error Handling

All endpoints return structured error responses:
```json
{
  "message": "Error description",
  "error": "Detailed error message",
  "field": "field_name_if_applicable"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## 🔄 Real-time Features

The API supports real-time notifications through:
- WebSocket connections (can be implemented)
- Polling endpoints for new messages/notifications
- Push notification integration ready

## 📊 Database Schema

The backend uses Supabase PostgreSQL with:
- 12+ tables with proper relationships
- Row Level Security (RLS) policies
- Automatic timestamps and triggers
- JSON support for flexible data
- Full-text search capabilities

## 🧪 Testing

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚀 Deployment Ready

- Environment-based configuration
- Docker support ready
- Logging and monitoring
- Health check endpoints
- CORS configuration for mobile apps
