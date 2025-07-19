from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ThreatDetectionCreate(BaseModel):
    threat_type: str
    content_analyzed: str
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    
    @validator('threat_type')
    def validate_threat_type(cls, v):
        allowed_types = ['cyberbullying', 'harassment', 'stalking', 'inappropriate_content', 'phishing', 'other']
        if v not in allowed_types:
            raise ValueError(f'Threat type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('content_analyzed')
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Content to analyze cannot be empty')
        if len(v) > 10000:
            raise ValueError('Content must be less than 10000 characters')
        return v.strip()

class ThreatDetectionResponse(BaseModel):
    id: str
    user_id: str
    threat_type: str
    threat_level: str
    content_analyzed: str
    ai_confidence_score: Optional[Decimal]
    source_platform: Optional[str]
    source_url: Optional[str]
    is_verified: bool
    action_taken: Optional[str]
    created_at: datetime
    updated_at: datetime

class ThreatDetectionUpdate(BaseModel):
    is_verified: Optional[bool] = None
    action_taken: Optional[str] = None
    
    @validator('action_taken')
    def validate_action_taken(cls, v):
        if v:
            allowed_actions = ['none', 'reported', 'blocked', 'escalated']
            if v not in allowed_actions:
                raise ValueError(f'Action taken must be one of: {", ".join(allowed_actions)}')
        return v

class EvidenceCreate(BaseModel):
    threat_detection_id: Optional[str] = None
    evidence_type: str
    file_name: str
    file_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None
    
    @validator('evidence_type')
    def validate_evidence_type(cls, v):
        allowed_types = ['screenshot', 'document', 'audio', 'video', 'text']
        if v not in allowed_types:
            raise ValueError(f'Evidence type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must be less than 1000 characters')
        return v

class EvidenceResponse(BaseModel):
    id: str
    user_id: str
    threat_detection_id: Optional[str]
    evidence_type: str
    file_name: str
    file_url: str
    file_size: Optional[int]
    mime_type: Optional[str]
    description: Optional[str]
    is_encrypted: bool
    hash_value: Optional[str]
    created_at: datetime

class ThreatAnalysisResult(BaseModel):
    threat_detected: bool
    threat_type: str
    threat_level: str
    confidence_score: float
    explanation: str
    recommended_actions: List[str]
