from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class ConnectionRequest(BaseModel):
    requested_id: str
    message: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if v and len(v) > 500:
            raise ValueError('Message must be less than 500 characters')
        return v

class ConnectionResponse(BaseModel):
    id: str
    requester_id: str
    requested_id: str
    status: str
    message: Optional[str]
    created_at: datetime
    updated_at: datetime
    requester_name: Optional[str] = None
    requester_avatar: Optional[str] = None

class ConnectionUpdate(BaseModel):
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['accepted', 'rejected', 'blocked']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class ConnectionList(BaseModel):
    connections: List[ConnectionResponse]
    total: int
    page: int
    limit: int
