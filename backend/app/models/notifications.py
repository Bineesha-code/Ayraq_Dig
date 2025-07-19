from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class NotificationCreate(BaseModel):
    notification_type: str
    title: str
    message: str
    priority: Optional[str] = "normal"
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('notification_type')
    def validate_notification_type(cls, v):
        allowed_types = ['threat_alert', 'connection_request', 'message', 'system_update', 'legal_guidance', 'support_resource']
        if v not in allowed_types:
            raise ValueError(f'Notification type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) > 255:
            raise ValueError('Title must be less than 255 characters')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        if len(v) > 1000:
            raise ValueError('Message must be less than 1000 characters')
        return v

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    notification_type: str
    title: str
    message: str
    priority: str
    is_read: bool
    action_url: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

class NotificationUpdate(BaseModel):
    is_read: bool = True

class NotificationList(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    limit: int

class NotificationStats(BaseModel):
    total_notifications: int
    unread_count: int
    priority_counts: Dict[str, int]
    type_counts: Dict[str, int]
