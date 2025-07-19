#!/usr/bin/env python3
"""
Comprehensive Test Script for AYRAQ Backend API
Tests all major endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = None  # Will be set after login

def make_request(method, endpoint, data=None, headers=None, params=None):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"

    if headers is None:
        headers = {}

    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None

def print_response(response, test_name):
    """Print formatted response"""
    if response is None:
        print(f"❌ {test_name}: Request failed")
        return False

    print(f"\n📋 {test_name}")
    print(f"Status: {response.status_code}")

    try:
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response.status_code < 400, response_data
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
        return response.status_code < 400, None

def test_authentication():
    """Test authentication endpoints"""
    global AUTH_TOKEN

    print("🔐 Testing Authentication Endpoints")
    print("=" * 50)

    # Test 1: User Registration
    print("\n1️⃣ Testing User Registration...")
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "user_type": "Student",
        "gender": "Male",
        "dob": "1995-01-15"
    }

    response = make_request("POST", "/auth/register", user_data)
    success, data = print_response(response, "User Registration")

    # Test 2: User Login
    print("\n2️⃣ Testing User Login...")
    login_data = {
        "email": "test@example.com",
        "password": "any_password"  # Currently accepts any password
    }

    response = make_request("POST", "/auth/login", login_data)
    success, data = print_response(response, "User Login")

    if success and data and "access_token" in data:
        AUTH_TOKEN = data["access_token"]
        print(f"✅ Authentication token obtained: {AUTH_TOKEN[:20]}...")

    # Test 3: Get Current User
    print("\n3️⃣ Testing Get Current User...")
    response = make_request("GET", "/auth/me")
    print_response(response, "Get Current User")

    return AUTH_TOKEN is not None

def test_connections():
    """Test connection/friend request system"""
    print("\n🤝 Testing Connection System")
    print("=" * 40)

    # First, create another user to connect with
    print("\n1️⃣ Creating second user...")
    user2_data = {
        "name": "Friend User",
        "email": "friend@example.com",
        "phone": "+1234567891",
        "user_type": "Professional",
        "gender": "Female",
        "dob": "1990-05-20"
    }

    response = make_request("POST", "/auth/register", user2_data)
    success, data = print_response(response, "Create Second User")

    if success and data:
        friend_id = data["user"]["id"]

        # Test connection request
        print("\n2️⃣ Sending Connection Request...")
        connection_data = {
            "requested_id": friend_id,
            "message": "Let's connect!"
        }

        response = make_request("POST", "/connections/request", connection_data)
        print_response(response, "Send Connection Request")

        # Test get connection requests
        print("\n3️⃣ Getting Connection Requests...")
        response = make_request("GET", "/connections/requests")
        print_response(response, "Get Connection Requests")

        # Test get connections
        print("\n4️⃣ Getting Connections...")
        response = make_request("GET", "/connections/")
        print_response(response, "Get Connections")

def test_threat_detection():
    """Test threat detection system"""
    print("\n🛡️ Testing Threat Detection System")
    print("=" * 45)

    # Test 1: Analyze threat content
    print("\n1️⃣ Analyzing Threat Content...")
    threat_data = {
        "threat_type": "cyberbullying",
        "content_analyzed": "You are so stupid and ugly, kill yourself!",
        "source_platform": "social_media",
        "source_url": "https://example.com/post/123"
    }

    response = make_request("POST", "/threats/analyze", threat_data)
    success, data = print_response(response, "Analyze Threat Content")

    # Test 2: Get threat detections
    print("\n2️⃣ Getting Threat Detections...")
    response = make_request("GET", "/threats/detections")
    print_response(response, "Get Threat Detections")

    # Test 3: Store evidence
    print("\n3️⃣ Storing Evidence...")
    evidence_data = {
        "evidence_type": "screenshot",
        "file_name": "threat_screenshot.png",
        "file_url": "https://example.com/evidence/screenshot.png",
        "file_size": 1024000,
        "mime_type": "image/png",
        "description": "Screenshot of threatening message"
    }

    response = make_request("POST", "/threats/evidence", evidence_data)
    print_response(response, "Store Evidence")

    # Test 4: Get evidence
    print("\n4️⃣ Getting Evidence...")
    response = make_request("GET", "/threats/evidence")
    print_response(response, "Get Evidence")
    
def test_notifications():
    """Test notification system"""
    print("\n🔔 Testing Notification System")
    print("=" * 40)

    # Test 1: Get notifications
    print("\n1️⃣ Getting Notifications...")
    response = make_request("GET", "/notifications/")
    print_response(response, "Get Notifications")

    # Test 2: Get notification stats
    print("\n2️⃣ Getting Notification Stats...")
    response = make_request("GET", "/notifications/stats")
    print_response(response, "Get Notification Stats")

def test_support_resources():
    """Test support and legal guidance"""
    print("\n🆘 Testing Support Resources")
    print("=" * 40)

    # Test 1: Get legal guidance
    print("\n1️⃣ Getting Legal Guidance...")
    response = make_request("GET", "/support/legal-guidance")
    print_response(response, "Get Legal Guidance")

    # Test 2: Get support resources
    print("\n2️⃣ Getting Support Resources...")
    response = make_request("GET", "/support/resources")
    print_response(response, "Get Support Resources")

    # Test 3: Create emergency contact
    print("\n3️⃣ Creating Emergency Contact...")
    contact_data = {
        "contact_name": "Emergency Contact",
        "contact_phone": "+1234567892",
        "contact_email": "emergency@example.com",
        "relationship": "Family",
        "is_primary": True
    }

    response = make_request("POST", "/support/emergency-contacts", contact_data)
    print_response(response, "Create Emergency Contact")

    # Test 4: Get emergency contacts
    print("\n4️⃣ Getting Emergency Contacts...")
    response = make_request("GET", "/support/emergency-contacts")
    print_response(response, "Get Emergency Contacts")

    # Test 5: Get user settings
    print("\n5️⃣ Getting User Settings...")
    response = make_request("GET", "/support/settings")
    print_response(response, "Get User Settings")

def test_chat_system():
    """Test chat system"""
    print("\n💬 Testing Chat System")
    print("=" * 35)

    # Test 1: Get conversations
    print("\n1️⃣ Getting Conversations...")
    response = make_request("GET", "/chat/conversations")
    print_response(response, "Get Conversations")

def run_comprehensive_tests():
    """Run all tests"""
    print("🧪 AYRAQ Backend API - Comprehensive Test Suite")
    print("=" * 60)
    print(f"🎯 Testing against: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Test authentication first (required for other tests)
    if not test_authentication():
        print("❌ Authentication failed - stopping tests")
        return

    print("\n" + "="*60)

    # Run all other tests
    test_connections()
    test_threat_detection()
    test_notifications()
    test_support_resources()
    test_chat_system()

    print("\n" + "="*60)
    print("✅ Comprehensive testing completed!")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 Check server logs for detailed information")
    print("📚 Visit http://localhost:8000/docs for interactive API documentation")
    print("="*60)

def test_health():
    """Test health endpoints"""
    print("🏥 Testing Health Endpoints")
    print("=" * 30)

    # Test general health
    response = make_request("GET", "/health")
    if response:
        print_response(response, "General Health Check")

    # Test auth health
    response = make_request("GET", "/auth/health")
    if response:
        print_response(response, "Auth Service Health")

if __name__ == "__main__":
    print("🚀 AYRAQ Backend API Test Suite")
    print("Make sure the server is running on http://localhost:8000")
    print("Run: python run.py")

    choice = input("\nChoose test type:\n1. Health Check Only\n2. Comprehensive Tests\nEnter choice (1 or 2): ")

    if choice == "1":
        test_health()
    elif choice == "2":
        run_comprehensive_tests()
    else:
        print("Invalid choice. Running health check...")
        test_health()
