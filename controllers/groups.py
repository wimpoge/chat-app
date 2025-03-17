from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from models.schemas import GroupCreate, GroupResponse, GroupMessage, GroupMessageResponse

router = APIRouter()

def initialize(group_service, get_current_user):
    """Initialize controller with required services and dependencies"""
    
    @router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
    async def create_group(
        group_data: GroupCreate,
        current_user: dict = Depends(get_current_user)
    ):
        """Create a new group"""
        group = group_service.create_group(
            group_data.title,
            current_user["username"],
            group_data.members
        )
        
        # Get full group with member details
        group_with_details = group_service.get_group_with_member_details(group["id"])
        if not group_with_details:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created group"
            )
        
        return {
            "id": group_with_details["id"],
            "title": group_with_details["title"],
            "created_at": group_with_details["created_at"],
            "creator": group_with_details["creator"],
            "members": group_with_details["members_details"]
        }
    
    @router.get("", response_model=List[GroupResponse])
    async def get_user_groups(current_user: dict = Depends(get_current_user)):
        """Get all groups the current user is a member of"""
        groups = group_service.get_user_groups(current_user["username"])
        
        result = []
        for group in groups:
            group_with_details = group_service.get_group_with_member_details(group["id"])
            if group_with_details:
                result.append({
                    "id": group_with_details["id"],
                    "title": group_with_details["title"],
                    "created_at": group_with_details["created_at"],
                    "creator": group_with_details["creator"],
                    "members": group_with_details["members_details"]
                })
        
        return result
    
    @router.get("/{group_id}", response_model=GroupResponse)
    async def get_group(
        group_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Get a specific group by ID"""
        group = group_service.get_group_with_member_details(group_id)
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if user is a member of the group
        if current_user["username"] not in group["members"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group"
            )
        
        return {
            "id": group["id"],
            "title": group["title"],
            "created_at": group["created_at"],
            "creator": group["creator"],
            "members": group["members_details"]
        }
    
    @router.post("/{group_id}/members/{username}", response_model=dict)
    async def add_member_to_group(
        group_id: str,
        username: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Add a member to a group"""
        # Check if user is the group creator
        group = group_service.get_group(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        if group["creator"] != current_user["username"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the group creator can add members"
            )
        
        if not group_service.add_member(group_id, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add member to group"
            )
        
        return {"message": f"Added {username} to the group"}
    
    @router.delete("/{group_id}/members/{username}", response_model=dict)
    async def remove_member_from_group(
        group_id: str,
        username: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Remove a member from a group"""
        # Check if user is the group creator
        group = group_service.get_group(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        if group["creator"] != current_user["username"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the group creator can remove members"
            )
        
        if not group_service.remove_member(group_id, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to remove member from group"
            )
        
        return {"message": f"Removed {username} from the group"}
    
    @router.delete("/{group_id}", response_model=dict)
    async def delete_group(
        group_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Delete a group"""
        success, message = group_service.delete_group(group_id, current_user["username"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {"message": message}
    
    @router.post("/{group_id}/messages", response_model=GroupMessageResponse)
    async def send_group_message(
        group_id: str,
        message: GroupMessage,
        current_user: dict = Depends(get_current_user)
    ):
        """Send a message to a group"""
        sent_message = group_service.send_message(
            group_id,
            current_user["username"],
            message.content
        )
        
        if not sent_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send message to group"
            )
        
        return GroupMessageResponse(
            id=sent_message["id"],
            group_id=sent_message["group_id"],
            sender=sent_message["sender"],
            content=sent_message["content"],
            timestamp=sent_message["timestamp"]
        )
    
    @router.get("/{group_id}/messages", response_model=List[GroupMessageResponse])
    async def get_group_messages(
        group_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Get all messages in a group"""
        messages = group_service.get_group_messages(group_id, current_user["username"])
        
        if messages is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group"
            )
        
        return [
            GroupMessageResponse(
                id=msg["id"],
                group_id=msg["group_id"],
                sender=msg["sender"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in messages
        ]
    
    return router