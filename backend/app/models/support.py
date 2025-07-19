from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class LegalGuidanceResponse(BaseModel):
    id: str
    title: str
    category: str
    content: str
    jurisdiction: Optional[str]
    is_active: bool
    priority_order: int
    created_at: datetime
    updated_at: datetime

class SupportResourceResponse(BaseModel):
    id: str
    name: str
    resource_type: str
    description: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    website_url: Optional[str]
    address: Optional[str]
    availability: Optional[str]
    is_emergency: bool
    country: Optional[str]
    state_province: Optional[str]
    city: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class EmergencyContactCreate(BaseModel):
    contact_name: str
    contact_phone: str
    contact_email: Optional[str] = None
    relationship: Optional[str] = None
    is_primary: Optional[bool] = False
    
    @validator('contact_name')
    def validate_contact_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Contact name must be at least 2 characters long')
        return v.strip()
    
    @validator('contact_phone')
    def validate_contact_phone(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Contact phone must be at least 10 characters long')
        return v.strip()

class EmergencyContactResponse(BaseModel):
    id: str
    user_id: str
    contact_name: str
    contact_phone: str
    contact_email: Optional[str]
    relationship: Optional[str]
    is_primary: bool
    created_at: datetime
    updated_at: datetime

class EmergencyContactUpdate(BaseModel):
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    relationship: Optional[str] = None
    is_primary: Optional[bool] = None
    
    @validator('contact_name')
    def validate_contact_name_if_provided(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Contact name must be at least 2 characters long')
        return v.strip() if v else v
    
    @validator('contact_phone')
    def validate_contact_phone_if_provided(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Contact phone must be at least 10 characters long')
        return v.strip() if v else v

class UserSettingsResponse(BaseModel):
    id: str
    user_id: str
    threat_detection_enabled: bool
    notification_preferences: dict
    privacy_settings: dict
    emergency_contacts: list
    auto_screenshot: bool
    overlay_enabled: bool
    created_at: datetime
    updated_at: datetime

class UserSettingsUpdate(BaseModel):
    threat_detection_enabled: Optional[bool] = None
    notification_preferences: Optional[dict] = None
    privacy_settings: Optional[dict] = None
    auto_screenshot: Optional[bool] = None
    overlay_enabled: Optional[bool] = None
