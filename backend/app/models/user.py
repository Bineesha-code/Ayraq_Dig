from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import phonenumbers
from phonenumbers import NumberParseException

class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    phone: str
    user_type: str  # e.g., "Student", "Professional", etc.
    gender: str     # "Male" or "Female"
    dob: str        # Date of birth as string (YYYY-MM-DD format)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        try:
            # Parse phone number (assuming international format or with country code)
            parsed_number = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('Invalid phone number')
            # Return formatted phone number
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            raise ValueError('Invalid phone number format')
    
    @validator('user_type')
    def validate_user_type(cls, v):
        allowed_types = ['Student', 'Professional', 'Other']
        if v not in allowed_types:
            raise ValueError(f'User type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        allowed_genders = ['Male', 'Female', 'Other']
        if v not in allowed_genders:
            raise ValueError(f'Gender must be one of: {", ".join(allowed_genders)}')
        return v
    
    @validator('dob')
    def validate_dob(cls, v):
        try:
            # Parse date to ensure it's valid
            dob_date = datetime.strptime(v, '%Y-%m-%d').date()
            # Check if user is at least 13 years old
            today = datetime.now().date()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            if age < 13:
                raise ValueError('User must be at least 13 years old')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Date of birth must be in YYYY-MM-DD format')
            raise e

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    user_type: str
    gender: str
    dob: str
    created_at: datetime
    avatar: Optional[str] = None

class UserInDB(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    phone: str
    user_type: str
    gender: str
    dob: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

    @validator('phone')
    def validate_phone_if_provided(cls, v):
        if v:
            try:
                parsed_number = phonenumbers.parse(v, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValueError('Invalid phone number')
                return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            except NumberParseException:
                raise ValueError('Invalid phone number format')
        return v

    @validator('email')
    def validate_login_method(cls, v, values):
        if not v and not values.get('phone'):
            raise ValueError('Either email or phone must be provided')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    user_type: Optional[str] = None
    avatar_url: Optional[str] = None

    @validator('name')
    def validate_name_if_provided(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip() if v else v

    @validator('user_type')
    def validate_user_type_if_provided(cls, v):
        if v:
            allowed_types = ['Student', 'Professional', 'Other']
            if v not in allowed_types:
                raise ValueError(f'User type must be one of: {", ".join(allowed_types)}')
        return v

class UserSearch(BaseModel):
    query: str
    user_type: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

    @validator('limit')
    def validate_limit(cls, v):
        if v and (v < 1 or v > 100):
            raise ValueError('Limit must be between 1 and 100')
        return v

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
