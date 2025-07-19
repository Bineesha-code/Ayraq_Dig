from fastapi import APIRouter, HTTPException, Depends, status, Query
from supabase import Client
from ..config.database import get_supabase
from ..routes.auth import verify_token
from ..models.connections import ConnectionRequest, ConnectionResponse, ConnectionUpdate, ConnectionList
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connections", tags=["connections"])

@router.post("/request", response_model=dict, status_code=status.HTTP_201_CREATED)
async def send_connection_request(
    request_data: ConnectionRequest,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Send a connection request to another user
    """
    try:
        # Check if user is trying to connect to themselves
        if current_user_id == request_data.requested_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send connection request to yourself"
            )
        
        # Check if requested user exists
        user_check = supabase.table('users').select('id, name').eq('id', request_data.requested_id).execute()
        if not user_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if connection already exists
        existing_connection = supabase.table('user_connections').select('*').or_(
            f"and(requester_id.eq.{current_user_id},requested_id.eq.{request_data.requested_id}),"
            f"and(requester_id.eq.{request_data.requested_id},requested_id.eq.{current_user_id})"
        ).execute()
        
        if existing_connection.data:
            connection = existing_connection.data[0]
            if connection['status'] == 'pending':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Connection request already pending"
                )
            elif connection['status'] == 'accepted':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Users are already connected"
                )
            elif connection['status'] == 'blocked':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot send connection request"
                )
        
        # Create connection request
        connection_data = {
            "requester_id": current_user_id,
            "requested_id": request_data.requested_id,
            "message": request_data.message,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('user_connections').insert(connection_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send connection request"
            )
        
        # Create notification for the requested user
        notification_data = {
            "user_id": request_data.requested_id,
            "notification_type": "connection_request",
            "title": "New Connection Request",
            "message": f"You have a new connection request",
            "priority": "normal",
            "metadata": {"connection_id": result.data[0]['id']},
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('notifications').insert(notification_data).execute()
        
        logger.info(f"Connection request sent from {current_user_id} to {request_data.requested_id}")
        
        return {
            "message": "Connection request sent successfully!",
            "success": True,
            "connection_id": result.data[0]['id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending connection request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send connection request"
        )

@router.get("/requests", response_model=ConnectionList)
async def get_connection_requests(
    status_filter: str = Query("pending", regex="^(pending|accepted|rejected|all)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get connection requests (received by current user)
    """
    try:
        # Build query
        query = supabase.table('user_connections').select(
            '*, requester:users!user_connections_requester_id_fkey(name, avatar_url, gender)'
        ).eq('requested_id', current_user_id)
        
        if status_filter != "all":
            query = query.eq('status', status_filter)
        
        # Get total count
        count_result = supabase.table('user_connections').select('id', count='exact').eq('requested_id', current_user_id)
        if status_filter != "all":
            count_result = count_result.eq('status', status_filter)
        count_result = count_result.execute()
        total = count_result.count
        
        # Get paginated results
        offset = (page - 1) * limit
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        # Format response
        connections = []
        for conn in result.data:
            requester = conn.get('requester', {})
            avatar_path = requester.get('avatar_url') or f"assets/{requester.get('gender', 'male').lower()}_avatar.png"
            
            connections.append(ConnectionResponse(
                id=conn['id'],
                requester_id=conn['requester_id'],
                requested_id=conn['requested_id'],
                status=conn['status'],
                message=conn.get('message'),
                created_at=conn['created_at'],
                updated_at=conn['updated_at'],
                requester_name=requester.get('name'),
                requester_avatar=avatar_path
            ))
        
        return ConnectionList(
            connections=connections,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching connection requests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connection requests"
        )

@router.put("/requests/{connection_id}", response_model=dict)
async def update_connection_request(
    connection_id: str,
    update_data: ConnectionUpdate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Accept, reject, or block a connection request
    """
    try:
        # Check if connection exists and user is the requested party
        connection_result = supabase.table('user_connections').select('*').eq('id', connection_id).eq('requested_id', current_user_id).execute()
        
        if not connection_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection request not found"
            )
        
        connection = connection_result.data[0]
        
        if connection['status'] != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connection request has already been processed"
            )
        
        # Update connection status
        update_result = supabase.table('user_connections').update({
            "status": update_data.status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq('id', connection_id).execute()
        
        if not update_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update connection request"
            )
        
        # Create notification for the requester
        status_messages = {
            "accepted": "Your connection request was accepted!",
            "rejected": "Your connection request was declined.",
            "blocked": "Connection request was blocked."
        }
        
        notification_data = {
            "user_id": connection['requester_id'],
            "notification_type": "connection_request",
            "title": "Connection Request Update",
            "message": status_messages.get(update_data.status, "Connection request updated"),
            "priority": "normal",
            "metadata": {"connection_id": connection_id, "status": update_data.status},
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('notifications').insert(notification_data).execute()
        
        logger.info(f"Connection request {connection_id} updated to {update_data.status}")
        
        return {
            "message": f"Connection request {update_data.status} successfully!",
            "success": True,
            "status": update_data.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating connection request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update connection request"
        )

@router.get("/", response_model=ConnectionList)
async def get_connections(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get accepted connections (friends) of current user
    """
    try:
        # Get connections where current user is either requester or requested and status is accepted
        query = supabase.table('user_connections').select(
            '*, requester:users!user_connections_requester_id_fkey(name, avatar_url, gender), '
            'requested:users!user_connections_requested_id_fkey(name, avatar_url, gender)'
        ).eq('status', 'accepted').or_(
            f'requester_id.eq.{current_user_id},requested_id.eq.{current_user_id}'
        )
        
        # Get total count
        count_result = supabase.table('user_connections').select('id', count='exact').eq('status', 'accepted').or_(
            f'requester_id.eq.{current_user_id},requested_id.eq.{current_user_id}'
        ).execute()
        total = count_result.count
        
        # Get paginated results
        offset = (page - 1) * limit
        result = query.order('updated_at', desc=True).range(offset, offset + limit - 1).execute()
        
        # Format response
        connections = []
        for conn in result.data:
            # Determine which user is the "other" user (not current user)
            if conn['requester_id'] == current_user_id:
                other_user = conn.get('requested', {})
                other_user_id = conn['requested_id']
            else:
                other_user = conn.get('requester', {})
                other_user_id = conn['requester_id']
            
            avatar_path = other_user.get('avatar_url') or f"assets/{other_user.get('gender', 'male').lower()}_avatar.png"
            
            connections.append(ConnectionResponse(
                id=conn['id'],
                requester_id=conn['requester_id'],
                requested_id=conn['requested_id'],
                status=conn['status'],
                message=conn.get('message'),
                created_at=conn['created_at'],
                updated_at=conn['updated_at'],
                requester_name=other_user.get('name'),
                requester_avatar=avatar_path
            ))
        
        return ConnectionList(
            connections=connections,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching connections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connections"
        )
