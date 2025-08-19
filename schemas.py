from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

# User 스키마
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Space 스키마
class SpaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True
    max_users: int = 10

class SpaceCreate(SpaceBase):
    space_data: Dict[str, Any]
    image_url: Optional[str] = None

class SpaceResponse(SpaceBase):
    id: int
    owner_id: int
    space_data: Dict[str, Any]
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Message 스키마
class MessageBase(BaseModel):
    content: str
    message_type: str = "chat"

class MessageCreate(MessageBase):
    space_id: int

class MessageResponse(MessageBase):
    id: int
    user_id: int
    space_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# WebSocket 메시지 스키마
class WebSocketMessage(BaseModel):
    type: str  # join_space, chat, move, leave_space
    data: Dict[str, Any]

# 이미지 분석 결과 스키마
class ImageAnalysisResult(BaseModel):
    dominant_colors: list
    mood: str
    objects_detected: list
    space_style: str
    lighting: str
