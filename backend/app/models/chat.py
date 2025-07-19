from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class MessageCreate(BaseModel):
    conversation_id: str
    message_text: str
    message_type: Optional[str] = "text"
    file_url: Optional[str] = None
    
    @validator('message_text')
    def validate_message_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message text cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message text must be less than 5000 characters')
        return v.strip()
    
    @validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = ['text', 'image', 'file', 'location']
        if v not in allowed_types:
            raise ValueError(f'Message type must be one of: {", ".join(allowed_types)}')
        return v

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    message_text: str
    message_type: str
    file_url: Optional[str]
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None

class ConversationCreate(BaseModel):
    participant_id: str

class ConversationResponse(BaseModel):
    id: str
    participant_1_id: str
    participant_2_id: str
    last_message_at: datetime
    created_at: datetime
    other_participant_name: Optional[str] = None
    other_participant_avatar: Optional[str] = None
    last_message: Optional[str] = None
    unread_count: Optional[int] = 0

class ConversationList(BaseModel):
    conversations: List[ConversationResponse]
    total: int

class MessageList(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    limit: int

class MessageUpdate(BaseModel):
    is_read: bool = True
