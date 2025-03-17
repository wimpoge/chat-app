import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List

from models.schemas import User, UserPublic
from config import PROFILE_IMAGES_DIR

router = APIRouter()

def initialize(user_db, get_current_user):
    """Initialize controller with required services and dependencies"""
    
    @router.get("/me", response_model=User)
    async def get_current_user_info(current_user: dict = Depends(get_current_user)):
        return User(
            username=current_user["username"],
            email=current_user["email"],
            created_at=current_user["created_at"],
            last_login=current_user["last_login"],
            profile_image=current_user.get("profile_image"),
            friends=current_user.get("friends", [])
        )

    @router.post("/upload-image", response_model=dict)
    async def upload_profile_image(
        file: UploadFile = File(...),
        current_user: dict = Depends(get_current_user)
    ):
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Create unique filename
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{current_user['username']}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
        file_path = os.path.join(PROFILE_IMAGES_DIR, new_filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Update user profile
        relative_path = f"/uploads/profile_images/{new_filename}"
        user_db.update_user(current_user["username"], {"profile_image": relative_path})
        
        return {"message": "Image uploaded successfully", "image_path": relative_path}

    @router.get("/list", response_model=List[UserPublic])
    async def list_all_users(current_user: dict = Depends(get_current_user)):
        """List all users except the current user"""
        return user_db.get_all_users(exclude_username=current_user["username"])
    
    return router