from fastapi import APIRouter, HTTPException, Depends, status, Query
from supabase import Client
from ..config.database import get_supabase
from ..routes.auth import verify_token
from ..models.chat import MessageCreate, MessageResponse, ConversationCreate, ConversationResponse, ConversationList, MessageList, MessageUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/conversations", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Create a new conversation between current user and another user
    """
    try:
        # Check if users are connected
        connection_check = supabase.table('user_connections').select('*').eq('status', 'accepted').or_(
            f"and(requester_id.eq.{current_user_id},requested_id.eq.{conversation_data.participant_id}),"
            f"and(requester_id.eq.{conversation_data.participant_id},requested_id.eq.{current_user_id})"
        ).execute()
        
        if not connection_check.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only start conversations with connected users"
            )
        
        # Check if conversation already exists
        existing_conversation = supabase.table('conversations').select('*').or_(
            f"and(participant_1_id.eq.{current_user_id},participant_2_id.eq.{conversation_data.participant_id}),"
            f"and(participant_1_id.eq.{conversation_data.participant_id},participant_2_id.eq.{current_user_id})"
        ).execute()
        
        if existing_conversation.data:
            return {
                "message": "Conversation already exists",
                "success": True,
                "conversation_id": existing_conversation.data[0]['id']
            }
        
        # Create new conversation
        conversation_dict = {
            "participant_1_id": current_user_id,
            "participant_2_id": conversation_data.participant_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_message_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('conversations').insert(conversation_dict).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )
        
        logger.info(f"Conversation created between {current_user_id} and {conversation_data.participant_id}")
        
        return {
            "message": "Conversation created successfully!",
            "success": True,
            "conversation_id": result.data[0]['id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

@router.get("/conversations", response_model=ConversationList)
async def get_conversations(
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all conversations for current user
    """
    try:
        # Get conversations with participant details and last message
        result = supabase.table('conversations').select(
            '*, participant_1:users!conversations_participant_1_id_fkey(name, avatar_url, gender), '
            'participant_2:users!conversations_participant_2_id_fkey(name, avatar_url, gender)'
        ).or_(
            f'participant_1_id.eq.{current_user_id},participant_2_id.eq.{current_user_id}'
        ).order('last_message_at', desc=True).execute()
        
        conversations = []
        for conv in result.data:
            # Determine other participant
            if conv['participant_1_id'] == current_user_id:
                other_participant = conv.get('participant_2', {})
            else:
                other_participant = conv.get('participant_1', {})
            
            # Get last message
            last_message_result = supabase.table('messages').select('message_text').eq(
                'conversation_id', conv['id']
            ).order('created_at', desc=True).limit(1).execute()
            
            last_message = last_message_result.data[0]['message_text'] if last_message_result.data else None
            
            # Get unread count
            unread_count_result = supabase.table('messages').select('id', count='exact').eq(
                'conversation_id', conv['id']
            ).neq('sender_id', current_user_id).eq('is_read', False).execute()
            
            unread_count = unread_count_result.count
            
            avatar_path = other_participant.get('avatar_url') or f"assets/{other_participant.get('gender', 'male').lower()}_avatar.png"
            
            conversations.append(ConversationResponse(
                id=conv['id'],
                participant_1_id=conv['participant_1_id'],
                participant_2_id=conv['participant_2_id'],
                last_message_at=conv['last_message_at'],
                created_at=conv['created_at'],
                other_participant_name=other_participant.get('name'),
                other_participant_avatar=avatar_path,
                last_message=last_message,
                unread_count=unread_count
            ))
        
        return ConversationList(
            conversations=conversations,
            total=len(conversations)
        )
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversations"
        )

@router.post("/messages", response_model=dict, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Send a message in a conversation
    """
    try:
        # Verify user is participant in conversation
        conversation_result = supabase.table('conversations').select('*').eq('id', message_data.conversation_id).or_(
            f'participant_1_id.eq.{current_user_id},participant_2_id.eq.{current_user_id}'
        ).execute()
        
        if not conversation_result.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to send messages in this conversation"
            )
        
        # Create message
        message_dict = {
            "conversation_id": message_data.conversation_id,
            "sender_id": current_user_id,
            "message_text": message_data.message_text,
            "message_type": message_data.message_type,
            "file_url": message_data.file_url,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('messages').insert(message_dict).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message"
            )
        
        # Update conversation last_message_at
        supabase.table('conversations').update({
            "last_message_at": datetime.utcnow().isoformat()
        }).eq('id', message_data.conversation_id).execute()
        
        # Create notification for other participant
        conversation = conversation_result.data[0]
        other_participant_id = conversation['participant_2_id'] if conversation['participant_1_id'] == current_user_id else conversation['participant_1_id']
        
        notification_data = {
            "user_id": other_participant_id,
            "notification_type": "message",
            "title": "New Message",
            "message": f"You have a new message",
            "priority": "normal",
            "metadata": {"conversation_id": message_data.conversation_id, "message_id": result.data[0]['id']},
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('notifications').insert(notification_data).execute()
        
        logger.info(f"Message sent in conversation {message_data.conversation_id}")
        
        return {
            "message": "Message sent successfully!",
            "success": True,
            "message_id": result.data[0]['id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )

@router.get("/conversations/{conversation_id}/messages", response_model=MessageList)
async def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user_id: str = Depends(verify_token),
    supabase: Client = Depends(get_supabase)
):
    """
    Get messages in a conversation
    """
    try:
        # Verify user is participant in conversation
        conversation_result = supabase.table('conversations').select('*').eq('id', conversation_id).or_(
            f'participant_1_id.eq.{current_user_id},participant_2_id.eq.{current_user_id}'
        ).execute()
        
        if not conversation_result.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view messages in this conversation"
            )
        
        # Get total count
        count_result = supabase.table('messages').select('id', count='exact').eq('conversation_id', conversation_id).execute()
        total = count_result.count
        
        # Get messages with sender details
        offset = (page - 1) * limit
        result = supabase.table('messages').select(
            '*, sender:users!messages_sender_id_fkey(name, avatar_url, gender)'
        ).eq('conversation_id', conversation_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        # Format messages
        messages = []
        for msg in result.data:
            sender = msg.get('sender', {})
            avatar_path = sender.get('avatar_url') or f"assets/{sender.get('gender', 'male').lower()}_avatar.png"
            
            messages.append(MessageResponse(
                id=msg['id'],
                conversation_id=msg['conversation_id'],
                sender_id=msg['sender_id'],
                message_text=msg['message_text'],
                message_type=msg['message_type'],
                file_url=msg.get('file_url'),
                is_read=msg['is_read'],
                created_at=msg['created_at'],
                sender_name=sender.get('name'),
                sender_avatar=avatar_path
            ))
        
        # Mark messages as read for current user
        supabase.table('messages').update({
            "is_read": True
        }).eq('conversation_id', conversation_id).neq('sender_id', current_user_id).execute()
        
        return MessageList(
            messages=messages,
            total=total,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch messages"
        )
