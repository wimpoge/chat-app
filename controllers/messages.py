from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from models.schemas import Message, MessageResponse

router = APIRouter()

def initialize(message_service, get_current_user):
    """Initialize controller with required services and dependencies"""
    
    @router.post("/send", response_model=MessageResponse)
    async def send_message(
        message: Message,
        current_user: dict = Depends(get_current_user)
    ):
        sent_message = message_service.send_message(
            current_user["username"],
            message.recipient,
            message.content
        )
        
        if not sent_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        
        return MessageResponse(
            sender=sent_message["sender"],
            recipient=sent_message["recipient"],
            content=sent_message["content"],
            timestamp=sent_message["timestamp"]
        )

    @router.get("/{friend_username}", response_model=List[MessageResponse])
    async def get_conversation(
        friend_username: str,
        current_user: dict = Depends(get_current_user)
    ):
        messages = message_service.get_conversation(current_user["username"], friend_username)
        
        if messages is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return [
            MessageResponse(
                sender=msg["sender"],
                recipient=msg["recipient"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in messages
        ]
    
    return router