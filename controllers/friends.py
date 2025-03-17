from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from models.schemas import UserPublic, FriendRequest

router = APIRouter()

def initialize(friend_service, get_current_user):
    """Initialize controller with required services and dependencies"""
    
    @router.get("/list", response_model=List[UserPublic])
    async def list_friends(current_user: dict = Depends(get_current_user)):
        """List all friends of the current user"""
        return friend_service.get_friends(current_user["username"])

    @router.get("/non-friends", response_model=List[UserPublic])
    async def list_non_friends(current_user: dict = Depends(get_current_user)):
        """List all users who are not friends with the current user"""
        return friend_service.get_non_friends(current_user["username"])

    @router.post("/add", response_model=dict)
    async def add_friend(
        friend_request: FriendRequest,
        current_user: dict = Depends(get_current_user)
    ):
        success, message = friend_service.add_friend(
            current_user["username"],
            friend_request.friend_username
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {"message": message}
    
    return router