from fastapi import APIRouter, HTTPException, Depends, status, Query
from supabase import Client
from ..config.database import get_supabase
from ..routes.auth import verify_token
from ..models.support import (
    LegalGuidanceResponse, SupportResourceResponse, 
    EmergencyContactCreate, EmergencyContactResponse, EmergencyContactUpdate,
    UserSettingsResponse, UserSettingsUpdate
)
from datetime import datetime
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/support", tags=["support"])

@router.get("/legal-guidance", response_model=List[LegalGuidanceResponse])
async def get_legal_guidance(
    category: str = Query(None),
    jurisdiction: str = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """
    Get legal guidance resources (public access)
    """
    try:
        # Build query
        query = supabase.table('legal_guidance').select('*').eq('is_active', True)
        
        if category:
            query = query.eq('category', category)
        if jurisdiction:
            query = query.eq('jurisdiction', jurisdiction)
        
        result = query.order('priority_order', desc=True).order('created_at', desc=True).execute()
        
        # Format response
        guidance_list = []
        for guidance in result.data:
            guidance_list.append(LegalGuidanceResponse(
                id=guidance['id'],
                title=guidance['title'],
                category=guidance['category'],
                content=guidance['content'],
                jurisdiction=guidance.get('jurisdiction'),
                is_active=guidance['is_active'],
                priority_order=guidance['priority_order'],
                created_at=guidance['created_at'],
                updated_at=guidance['updated_at']
            ))
        
        return guidance_list
        
    except Exception as e:
        logger.error(f"Error fetching legal guidance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch legal guidance"
        )

@router.get("/resources", response_model=List[SupportResourceResponse])
async def get_support_resources(
    resource_type: str = Query(None),
    is_emergency: bool = Query(None),
    country: str = Query(None),
    state_province: str = Query(None),
    city: str = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """
    Get support resources (public access)
    """
    try:
        # Build query
        query = supabase.table('support_resources').select('*').eq('is_active', True)
        
        if resource_type:
            query = query.eq('resource_type', resource_type)
        if is_emergency is not None:
            query = query.eq('is_emergency', is_emergency)
        if country:
            query = query.eq('country', country)
        if state_province:
            query = query.eq('state_province', state_province)
        if city:
            query = query.eq('city', city)
        
        result = query.order('is_emergency', desc=True).order('created_at', desc=True).execute()
        
        # Format response
        resources_list = []
        for resource in result.data:
            resources_list.append(SupportResourceResponse(
                id=resource['id'],
                name=resource['name'],
                resource_type=resource['resource_type'],
                description=resource.get('description'),
                contact_phone=resource.get('contact_phone'),
                contact_email=resource.get('contact_email'),
                website_url=resource.get('website_url'),
                address=resource.get('address'),
                availability=resource.get('availability'),
                is_emergency=resource['is_emergency'],
                country=resource.get('country'),
                state_province=resource.get('state_province'),
                city=resource.get('city'),
                is_active=resource['is_active'],
                created_at=resource['created_at'],
                updated_at=resource['updated_at']
            ))
        
        return resources_list
        
    except Exception as e:
        logger.error(f"Error fetching support resources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch support resources"
        )

@router.post("/emergency-contacts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Create emergency contact for current user
    """
    try:
        # If this is set as primary, unset other primary contacts
        if contact_data.is_primary:
            supabase.table('emergency_contacts').update({
                "is_primary": False
            }).eq('user_id', current_user_id).execute()
        
        # Create emergency contact
        contact_dict = {
            "user_id": current_user_id,
            "contact_name": contact_data.contact_name,
            "contact_phone": contact_data.contact_phone,
            "contact_email": contact_data.contact_email,
            "relationship": contact_data.relationship,
            "is_primary": contact_data.is_primary,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('emergency_contacts').insert(contact_dict).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create emergency contact"
            )
        
        logger.info(f"Emergency contact created for user {current_user_id}")
        
        return {
            "message": "Emergency contact created successfully!",
            "success": True,
            "contact_id": result.data[0]['id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating emergency contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create emergency contact"
        )

@router.get("/emergency-contacts", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get emergency contacts for current user
    """
    try:
        result = supabase.table('emergency_contacts').select('*').eq('user_id', current_user_id).order('is_primary', desc=True).order('created_at', desc=True).execute()
        
        # Format response
        contacts_list = []
        for contact in result.data:
            contacts_list.append(EmergencyContactResponse(
                id=contact['id'],
                user_id=contact['user_id'],
                contact_name=contact['contact_name'],
                contact_phone=contact['contact_phone'],
                contact_email=contact.get('contact_email'),
                relationship=contact.get('relationship'),
                is_primary=contact['is_primary'],
                created_at=contact['created_at'],
                updated_at=contact['updated_at']
            ))
        
        return contacts_list
        
    except Exception as e:
        logger.error(f"Error fetching emergency contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch emergency contacts"
        )

@router.put("/emergency-contacts/{contact_id}", response_model=dict)
async def update_emergency_contact(
    contact_id: str,
    update_data: EmergencyContactUpdate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Update emergency contact
    """
    try:
        # Check if contact belongs to current user
        contact_result = supabase.table('emergency_contacts').select('*').eq('id', contact_id).eq('user_id', current_user_id).execute()
        
        if not contact_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        # If setting as primary, unset other primary contacts
        if update_data.is_primary:
            supabase.table('emergency_contacts').update({
                "is_primary": False
            }).eq('user_id', current_user_id).execute()
        
        # Prepare update data
        update_dict = {"updated_at": datetime.utcnow().isoformat()}
        if update_data.contact_name is not None:
            update_dict['contact_name'] = update_data.contact_name
        if update_data.contact_phone is not None:
            update_dict['contact_phone'] = update_data.contact_phone
        if update_data.contact_email is not None:
            update_dict['contact_email'] = update_data.contact_email
        if update_data.relationship is not None:
            update_dict['relationship'] = update_data.relationship
        if update_data.is_primary is not None:
            update_dict['is_primary'] = update_data.is_primary
        
        # Update contact
        result = supabase.table('emergency_contacts').update(update_dict).eq('id', contact_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update emergency contact"
            )
        
        return {
            "message": "Emergency contact updated successfully!",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating emergency contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update emergency contact"
        )

@router.delete("/emergency-contacts/{contact_id}", response_model=dict)
async def delete_emergency_contact(
    contact_id: str,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Delete emergency contact
    """
    try:
        # Check if contact belongs to current user
        contact_result = supabase.table('emergency_contacts').select('*').eq('id', contact_id).eq('user_id', current_user_id).execute()
        
        if not contact_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        # Delete contact
        result = supabase.table('emergency_contacts').delete().eq('id', contact_id).execute()
        
        return {
            "message": "Emergency contact deleted successfully!",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting emergency contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete emergency contact"
        )

@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get user settings
    """
    try:
        result = supabase.table('user_settings').select('*').eq('user_id', current_user_id).execute()
        
        if not result.data:
            # Create default settings if they don't exist
            default_settings = {
                "user_id": current_user_id,
                "threat_detection_enabled": True,
                "notification_preferences": {"threat_alerts": True, "connection_requests": True, "messages": True, "system_updates": False},
                "privacy_settings": {"profile_visibility": "friends", "location_sharing": False, "data_sharing": False},
                "emergency_contacts": [],
                "auto_screenshot": False,
                "overlay_enabled": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            create_result = supabase.table('user_settings').insert(default_settings).execute()
            if create_result.data:
                settings_data = create_result.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create default settings"
                )
        else:
            settings_data = result.data[0]
        
        return UserSettingsResponse(
            id=settings_data['id'],
            user_id=settings_data['user_id'],
            threat_detection_enabled=settings_data['threat_detection_enabled'],
            notification_preferences=settings_data['notification_preferences'],
            privacy_settings=settings_data['privacy_settings'],
            emergency_contacts=settings_data['emergency_contacts'],
            auto_screenshot=settings_data['auto_screenshot'],
            overlay_enabled=settings_data['overlay_enabled'],
            created_at=settings_data['created_at'],
            updated_at=settings_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user settings"
        )

@router.put("/settings", response_model=dict)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Update user settings
    """
    try:
        # Prepare update data
        update_dict = {"updated_at": datetime.utcnow().isoformat()}
        if settings_update.threat_detection_enabled is not None:
            update_dict['threat_detection_enabled'] = settings_update.threat_detection_enabled
        if settings_update.notification_preferences is not None:
            update_dict['notification_preferences'] = settings_update.notification_preferences
        if settings_update.privacy_settings is not None:
            update_dict['privacy_settings'] = settings_update.privacy_settings
        if settings_update.auto_screenshot is not None:
            update_dict['auto_screenshot'] = settings_update.auto_screenshot
        if settings_update.overlay_enabled is not None:
            update_dict['overlay_enabled'] = settings_update.overlay_enabled
        
        # Update settings
        result = supabase.table('user_settings').update(update_dict).eq('user_id', current_user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update settings"
            )
        
        return {
            "message": "Settings updated successfully!",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )
