from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserPublic(BaseModel):
    username: str
    email: EmailStr
    profile_image: Optional[str] = None
    
class User(UserBase):
    created_at: str
    last_login: Optional[str] = None
    profile_image: Optional[str] = None
    friends: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordChange(BaseModel):
    username: str
    current_password: str
    new_password: str = Field(..., min_length=8)

class FriendRequest(BaseModel):
    friend_username: str

class Message(BaseModel):
    recipient: str
    content: str

class MessageResponse(BaseModel):
    sender: str
    recipient: str
    content: str
    timestamp: str
    
class GroupCreate(BaseModel):
    title: str
    members: List[str]

class Group(BaseModel):
    id: str
    title: str
    created_at: str
    creator: str
    members: List[str]

class GroupResponse(BaseModel):
    id: str
    title: str
    created_at: str
    creator: str
    members: List[UserPublic]

class GroupMessage(BaseModel):
    group_id: str
    content: str

class GroupMessageResponse(BaseModel):
    id: str
    group_id: str
    sender: str
    content: str
    timestamp: str