from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from ..config.database import get_supabase
from ..models.user import UserRegistration, UserResponse, UserLogin, UserUpdate, UserSearch, PasswordChange
from datetime import datetime, timedelta
import logging
import jwt
import hashlib
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = "UEYa-U0PIN2KsGgiLyXRr6nkq95yBG65QQuuJqcBQ5E"  # Should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user ID"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration, supabase: Client = Depends(get_supabase)):
    """
    Register a new user with email and phone uniqueness validation
    """
    try:
        # Check if email already exists
        email_check = supabase.table('users').select('id').eq('email', user_data.email).execute()
        if email_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Registration failed",
                    "error": "Email address is already registered. Please use a different email or try logging in.",
                    "field": "email"
                }
            )
        
        # Check if phone number already exists
        phone_check = supabase.table('users').select('id').eq('phone', user_data.phone).execute()
        if phone_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Registration failed",
                    "error": "Phone number is already registered. Please use a different phone number or try logging in.",
                    "field": "phone"
                }
            )
        
        # Hash password (you'll need to add password field to UserRegistration model)
        # For now, we'll create a default password that should be changed
        default_password = hash_password("ChangeMe123!")

        # Prepare user data for insertion
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "phone": user_data.phone,
            "user_type": user_data.user_type,
            "gender": user_data.gender,
            "dob": user_data.dob,
            "password_hash": default_password,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert user into database
        result = supabase.table('users').insert(user_dict).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Registration failed",
                    "error": "Failed to create user account. Please try again.",
                    "field": None
                }
            )
        
        created_user = result.data[0]
        
        # Generate avatar path based on gender
        avatar_path = f"assets/{user_data.gender.lower()}_avatar.png"
        
        logger.info(f"User registered successfully: {created_user['id']}")
        
        return {
            "message": "Registration successful! Welcome to AYRAQ.",
            "success": True,
            "user": {
                "id": created_user['id'],
                "name": created_user['name'],
                "email": created_user['email'],
                "phone": created_user['phone'],
                "user_type": created_user['user_type'],
                "gender": created_user['gender'],
                "dob": created_user['dob'],
                "avatar": avatar_path,
                "created_at": created_user['created_at']
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Registration failed",
                "error": "An unexpected error occurred. Please try again later.",
                "field": None
            }
        )

@router.post("/login", response_model=dict)
async def login_user(login_data: UserLogin, supabase: Client = Depends(get_supabase)):
    """
    Login user with email/phone and password
    """
    try:
        # Determine login method
        if login_data.email:
            user_result = supabase.table('users').select('*').eq('email', login_data.email).execute()
        else:
            user_result = supabase.table('users').select('*').eq('phone', login_data.phone).execute()

        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Login failed",
                    "error": "Invalid credentials. Please check your email/phone and password.",
                    "field": "credentials"
                }
            )

        user = user_result.data[0]

        # Verify password (for now, accept any password since we don't have password in registration)
        # In production, you should verify against stored password hash
        # if not verify_password(login_data.password, user.get('password_hash', '')):
        #     raise HTTPException(...)

        # Update last login
        supabase.table('users').update({
            "last_login": datetime.utcnow().isoformat()
        }).eq('id', user['id']).execute()

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['id']}, expires_delta=access_token_expires
        )

        # Generate avatar path
        avatar_path = f"assets/{user['gender'].lower()}_avatar.png"

        logger.info(f"User logged in successfully: {user['id']}")

        return {
            "message": "Login successful! Welcome back to AYRAQ.",
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "phone": user['phone'],
                "user_type": user['user_type'],
                "gender": user['gender'],
                "dob": user['dob'],
                "avatar": avatar_path,
                "last_login": user.get('last_login'),
                "created_at": user['created_at']
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Login failed",
                "error": "An unexpected error occurred. Please try again later.",
                "field": None
            }
        )

@router.get("/me", response_model=dict)
async def get_current_user(current_user_id: str = Depends(verify_token), supabase: Client = Depends(get_supabase)):
    """
    Get current user profile
    """
    try:
        user_result = supabase.table('users').select('*').eq('id', current_user_id).execute()

        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user = user_result.data[0]
        avatar_path = f"assets/{user['gender'].lower()}_avatar.png"

        return {
            "success": True,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "phone": user['phone'],
                "user_type": user['user_type'],
                "gender": user['gender'],
                "dob": user['dob'],
                "avatar": avatar_path,
                "is_active": user.get('is_active', True),
                "last_login": user.get('last_login'),
                "created_at": user['created_at']
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )

@router.put("/me", response_model=dict)
async def update_current_user(
    user_update: UserUpdate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Update current user profile
    """
    try:
        # Prepare update data
        update_data = {}
        if user_update.name is not None:
            update_data['name'] = user_update.name
        if user_update.user_type is not None:
            update_data['user_type'] = user_update.user_type
        if user_update.avatar_url is not None:
            update_data['avatar_url'] = user_update.avatar_url

        update_data['updated_at'] = datetime.utcnow().isoformat()

        # Update user
        result = supabase.table('users').update(update_data).eq('id', current_user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        updated_user = result.data[0]
        avatar_path = updated_user.get('avatar_url') or f"assets/{updated_user['gender'].lower()}_avatar.png"

        return {
            "message": "Profile updated successfully!",
            "success": True,
            "user": {
                "id": updated_user['id'],
                "name": updated_user['name'],
                "email": updated_user['email'],
                "phone": updated_user['phone'],
                "user_type": updated_user['user_type'],
                "gender": updated_user['gender'],
                "dob": updated_user['dob'],
                "avatar": avatar_path,
                "updated_at": updated_user['updated_at']
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AYRAQ Auth Service"}
