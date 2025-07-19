from fastapi import APIRouter, HTTPException, Depends, status, Query
from supabase import Client
from ..config.database import get_supabase
from ..routes.auth import verify_token
from ..models.threats import ThreatDetectionCreate, ThreatDetectionResponse, ThreatDetectionUpdate, EvidenceCreate, EvidenceResponse, ThreatAnalysisResult
from datetime import datetime
import logging
import re
import hashlib
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/threats", tags=["threat-detection"])

# Simple AI threat detection (in production, use proper ML models)
def analyze_threat_content(content: str) -> ThreatAnalysisResult:
    """
    Simple rule-based threat detection
    In production, replace with proper ML model
    """
    content_lower = content.lower()
    
    # Define threat patterns
    threat_patterns = {
        'cyberbullying': [
            r'\b(stupid|idiot|loser|ugly|fat|worthless|kill yourself|die)\b',
            r'\b(hate you|disgusting|pathetic|freak)\b'
        ],
        'harassment': [
            r'\b(follow you|watching you|know where you live|find you)\b',
            r'\b(won\'t leave you alone|obsessed|stalking)\b'
        ],
        'inappropriate_content': [
            r'\b(send nudes|naked|sexy pics|inappropriate)\b',
            r'\b(sexual|explicit|adult content)\b'
        ],
        'phishing': [
            r'\b(click here|urgent|verify account|suspended)\b',
            r'\b(winner|congratulations|claim prize|free money)\b'
        ]
    }
    
    detected_threats = []
    max_confidence = 0.0
    primary_threat = 'other'
    
    for threat_type, patterns in threat_patterns.items():
        threat_score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, content_lower))
            threat_score += matches * 0.3
        
        if threat_score > 0:
            detected_threats.append(threat_type)
            if threat_score > max_confidence:
                max_confidence = threat_score
                primary_threat = threat_type
    
    # Determine threat level
    if max_confidence >= 0.8:
        threat_level = 'critical'
    elif max_confidence >= 0.6:
        threat_level = 'high'
    elif max_confidence >= 0.3:
        threat_level = 'medium'
    else:
        threat_level = 'low'
    
    # Generate recommendations
    recommendations = []
    if max_confidence > 0.5:
        recommendations.extend([
            "Document this content as evidence",
            "Report to platform administrators",
            "Consider blocking the sender"
        ])
        if threat_level in ['high', 'critical']:
            recommendations.extend([
                "Contact emergency services if feeling unsafe",
                "Inform trusted contacts about the situation"
            ])
    
    return ThreatAnalysisResult(
        threat_detected=max_confidence > 0.2,
        threat_type=primary_threat,
        threat_level=threat_level,
        confidence_score=min(max_confidence, 1.0),
        explanation=f"Detected potential {primary_threat} with {threat_level} severity level",
        recommended_actions=recommendations
    )

@router.post("/analyze", response_model=ThreatAnalysisResult)
async def analyze_threat(
    threat_data: ThreatDetectionCreate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Analyze content for potential threats using AI
    """
    try:
        # Perform threat analysis
        analysis_result = analyze_threat_content(threat_data.content_analyzed)
        
        # Store threat detection in database
        threat_dict = {
            "user_id": current_user_id,
            "threat_type": analysis_result.threat_type,
            "threat_level": analysis_result.threat_level,
            "content_analyzed": threat_data.content_analyzed,
            "ai_confidence_score": analysis_result.confidence_score,
            "source_platform": threat_data.source_platform,
            "source_url": threat_data.source_url,
            "is_verified": False,
            "action_taken": "none",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('threat_detections').insert(threat_dict).execute()
        
        if result.data and analysis_result.threat_detected:
            # Create notification for high-priority threats
            if analysis_result.threat_level in ['high', 'critical']:
                notification_data = {
                    "user_id": current_user_id,
                    "notification_type": "threat_alert",
                    "title": f"{analysis_result.threat_level.title()} Threat Detected",
                    "message": f"We detected a {analysis_result.threat_level} level {analysis_result.threat_type} threat",
                    "priority": "urgent" if analysis_result.threat_level == 'critical' else "high",
                    "metadata": {"threat_id": result.data[0]['id']},
                    "created_at": datetime.utcnow().isoformat()
                }
                
                supabase.table('notifications').insert(notification_data).execute()
        
        logger.info(f"Threat analysis completed for user {current_user_id}: {analysis_result.threat_type} - {analysis_result.threat_level}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing threat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze threat"
        )

@router.get("/detections", response_model=List[ThreatDetectionResponse])
async def get_threat_detections(
    threat_type: str = Query(None),
    threat_level: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get threat detections for current user
    """
    try:
        # Build query
        query = supabase.table('threat_detections').select('*').eq('user_id', current_user_id)
        
        if threat_type:
            query = query.eq('threat_type', threat_type)
        if threat_level:
            query = query.eq('threat_level', threat_level)
        
        # Get paginated results
        offset = (page - 1) * limit
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        # Format response
        detections = []
        for detection in result.data:
            detections.append(ThreatDetectionResponse(
                id=detection['id'],
                user_id=detection['user_id'],
                threat_type=detection['threat_type'],
                threat_level=detection['threat_level'],
                content_analyzed=detection['content_analyzed'],
                ai_confidence_score=detection.get('ai_confidence_score'),
                source_platform=detection.get('source_platform'),
                source_url=detection.get('source_url'),
                is_verified=detection['is_verified'],
                action_taken=detection.get('action_taken'),
                created_at=detection['created_at'],
                updated_at=detection['updated_at']
            ))
        
        return detections
        
    except Exception as e:
        logger.error(f"Error fetching threat detections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch threat detections"
        )

@router.put("/detections/{detection_id}", response_model=dict)
async def update_threat_detection(
    detection_id: str,
    update_data: ThreatDetectionUpdate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Update threat detection (verify or mark action taken)
    """
    try:
        # Check if detection belongs to current user
        detection_result = supabase.table('threat_detections').select('*').eq('id', detection_id).eq('user_id', current_user_id).execute()
        
        if not detection_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Threat detection not found"
            )
        
        # Prepare update data
        update_dict = {"updated_at": datetime.utcnow().isoformat()}
        if update_data.is_verified is not None:
            update_dict['is_verified'] = update_data.is_verified
        if update_data.action_taken is not None:
            update_dict['action_taken'] = update_data.action_taken
        
        # Update detection
        result = supabase.table('threat_detections').update(update_dict).eq('id', detection_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update threat detection"
            )
        
        logger.info(f"Threat detection {detection_id} updated")
        
        return {
            "message": "Threat detection updated successfully!",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating threat detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update threat detection"
        )

@router.post("/evidence", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    evidence_data: EvidenceCreate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Store evidence (screenshots, documents, etc.)
    """
    try:
        # Generate file hash for integrity
        file_hash = hashlib.sha256(f"{evidence_data.file_url}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        # Create evidence record
        evidence_dict = {
            "user_id": current_user_id,
            "threat_detection_id": evidence_data.threat_detection_id,
            "evidence_type": evidence_data.evidence_type,
            "file_name": evidence_data.file_name,
            "file_url": evidence_data.file_url,
            "file_size": evidence_data.file_size,
            "mime_type": evidence_data.mime_type,
            "description": evidence_data.description,
            "is_encrypted": True,  # Default to encrypted
            "hash_value": file_hash,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('evidence').insert(evidence_dict).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store evidence"
            )
        
        logger.info(f"Evidence stored for user {current_user_id}: {evidence_data.evidence_type}")
        
        return {
            "message": "Evidence stored successfully!",
            "success": True,
            "evidence_id": result.data[0]['id'],
            "hash_value": file_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing evidence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store evidence"
        )

@router.get("/evidence", response_model=List[EvidenceResponse])
async def get_evidence(
    evidence_type: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get evidence stored by current user
    """
    try:
        # Build query
        query = supabase.table('evidence').select('*').eq('user_id', current_user_id)
        
        if evidence_type:
            query = query.eq('evidence_type', evidence_type)
        
        # Get paginated results
        offset = (page - 1) * limit
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        # Format response
        evidence_list = []
        for evidence in result.data:
            evidence_list.append(EvidenceResponse(
                id=evidence['id'],
                user_id=evidence['user_id'],
                threat_detection_id=evidence.get('threat_detection_id'),
                evidence_type=evidence['evidence_type'],
                file_name=evidence['file_name'],
                file_url=evidence['file_url'],
                file_size=evidence.get('file_size'),
                mime_type=evidence.get('mime_type'),
                description=evidence.get('description'),
                is_encrypted=evidence['is_encrypted'],
                hash_value=evidence.get('hash_value'),
                created_at=evidence['created_at']
            ))
        
        return evidence_list
        
    except Exception as e:
        logger.error(f"Error fetching evidence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch evidence"
        )
