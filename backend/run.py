#!/usr/bin/env python3
"""
AYRAQ Backend Server Startup Script
Complete backend for AI-powered women's safety application
"""

import uvicorn
import sys
import os
from app.config.settings import settings
from app.config.database import supabase_client

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment configuration...")

    try:
        settings.validate_settings()
        print("✅ Environment configuration is valid")
        return True
    except ValueError as e:
        print(f"❌ Environment configuration error: {e}")
        print("📝 Please check your .env file and ensure all required variables are set")
        return False

def test_database_connection():
    """Test database connection"""
    print("🔗 Testing database connection...")

    try:
        if supabase_client.test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            print("📝 Please check your Supabase credentials and ensure the database schema is created")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def display_startup_info():
    """Display startup information"""
    print("\n" + "="*60)
    print("🎯 AYRAQ Backend API Server")
    print("   AI-Powered Women's Safety Application")
    print("="*60)
    print(f"📍 Server URL: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"📖 ReDoc: http://{settings.HOST}:{settings.PORT}/redoc")
    print(f"🔧 Debug Mode: {'ON' if settings.DEBUG else 'OFF'}")
    print(f"🗄️  Database: Supabase")
    print("\n🚀 Available Features:")
    print("   • User Authentication & Management")
    print("   • Connection/Friend Request System")
    print("   • Real-time Chat System")
    print("   • AI-Powered Threat Detection")
    print("   • Evidence Storage & Management")
    print("   • Notification System")
    print("   • Legal Guidance Resources")
    print("   • Emergency Support Contacts")
    print("   • User Settings & Privacy Controls")
    print("\n📱 Mobile App Integration Ready")
    print("🔒 Security: JWT Authentication + RLS")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Starting AYRAQ Backend API Server...")

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Test database connection
    if not test_database_connection():
        print("⚠️  Warning: Database connection failed, but starting server anyway...")
        print("   Some features may not work properly until database is configured.")

    # Display startup information
    display_startup_info()

    print("\n🎬 Starting server...")

    try:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
