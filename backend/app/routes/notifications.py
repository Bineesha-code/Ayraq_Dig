from fastapi import APIRouter, HTTPException, Depends, status, Query
from supabase import Client
from ..config.database import get_supabase
from ..routes.auth import verify_token
from ..models.notifications import NotificationCreate, NotificationResponse, NotificationUpdate, NotificationList, NotificationStats
from datetime import datetime
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=NotificationList)
async def get_notifications(
    notification_type: str = Query(None),
    priority: str = Query(None),
    is_read: bool = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get notifications for current user
    """
    try:
        # Build query
        query = supabase.table('notifications').select('*').eq('user_id', current_user_id)
        
        if notification_type:
            query = query.eq('notification_type', notification_type)
        if priority:
            query = query.eq('priority', priority)
        if is_read is not None:
            query = query.eq('is_read', is_read)
        
        # Get total count
        count_query = supabase.table('notifications').select('id', count='exact').eq('user_id', current_user_id)
        if notification_type:
            count_query = count_query.eq('notification_type', notification_type)
        if priority:
            count_query = count_query.eq('priority', priority)
        if is_read is not None:
            count_query = count_query.eq('is_read', is_read)
        
        count_result = count_query.execute()
        total = count_result.count
        
        # Get unread count
        unread_result = supabase.table('notifications').select('id', count='exact').eq('user_id', current_user_id).eq('is_read', False).execute()
        unread_count = unread_result.count
        
        # Get paginated results
        offset = (page - 1) * limit
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        # Format response
        notifications = []
        for notif in result.data:
            notifications.append(NotificationResponse(
                id=notif['id'],
                user_id=notif['user_id'],
                notification_type=notif['notification_type'],
                title=notif['title'],
                message=notif['message'],
                priority=notif['priority'],
                is_read=notif['is_read'],
                action_url=notif.get('action_url'),
                metadata=notif.get('metadata'),
                created_at=notif['created_at']
            ))
        
        return NotificationList(
            notifications=notifications,
            total=total,
            unread_count=unread_count,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )

@router.put("/{notification_id}", response_model=dict)
async def update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Mark notification as read/unread
    """
    try:
        # Check if notification belongs to current user
        notification_result = supabase.table('notifications').select('*').eq('id', notification_id).eq('user_id', current_user_id).execute()
        
        if not notification_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Update notification
        result = supabase.table('notifications').update({
            "is_read": update_data.is_read
        }).eq('id', notification_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update notification"
            )
        
        return {
            "message": "Notification updated successfully!",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification"
        )

@router.put("/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Mark all notifications as read for current user
    """
    try:
        result = supabase.table('notifications').update({
            "is_read": True
        }).eq('user_id', current_user_id).eq('is_read', False).execute()
        
        return {
            "message": f"All notifications marked as read!",
            "success": True,
            "updated_count": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read"
        )

@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: str,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Delete a notification
    """
    try:
        # Check if notification belongs to current user
        notification_result = supabase.table('notifications').select('*').eq('id', notification_id).eq('user_id', current_user_id).execute()
        
        if not notification_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Delete notification
        result = supabase.table('notifications').delete().eq('id', notification_id).execute()
        
        return {
            "message": "Notification deleted successfully!",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get notification statistics for current user
    """
    try:
        # Get all notifications for user
        result = supabase.table('notifications').select('notification_type, priority, is_read').eq('user_id', current_user_id).execute()
        
        notifications = result.data
        total_notifications = len(notifications)
        unread_count = len([n for n in notifications if not n['is_read']])
        
        # Count by priority
        priority_counts = {}
        for priority in ['low', 'normal', 'high', 'urgent']:
            priority_counts[priority] = len([n for n in notifications if n['priority'] == priority])
        
        # Count by type
        type_counts = {}
        for notif_type in ['threat_alert', 'connection_request', 'message', 'system_update', 'legal_guidance', 'support_resource']:
            type_counts[notif_type] = len([n for n in notifications if n['notification_type'] == notif_type])
        
        return NotificationStats(
            total_notifications=total_notifications,
            unread_count=unread_count,
            priority_counts=priority_counts,
            type_counts=type_counts
        )
        
    except Exception as e:
        logger.error(f"Error fetching notification stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification statistics"
        )

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    target_user_id: str,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Create a notification for another user (admin/system use)
    """
    try:
        # Create notification
        notification_dict = {
            "user_id": target_user_id,
            "notification_type": notification_data.notification_type,
            "title": notification_data.title,
            "message": notification_data.message,
            "priority": notification_data.priority,
            "action_url": notification_data.action_url,
            "metadata": notification_data.metadata,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('notifications').insert(notification_dict).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create notification"
            )
        
        logger.info(f"Notification created for user {target_user_id}")
        
        return {
            "message": "Notification created successfully!",
            "success": True,
            "notification_id": result.data[0]['id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )
