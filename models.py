from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    spaces = relationship("Space", back_populates="owner")
    messages = relationship("Message", back_populates="user")

class Space(Base):
    __tablename__ = "spaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    space_data = Column(JSON)  # 3D 공간 데이터
    image_url = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=True)
    max_users = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    owner = relationship("User", back_populates="spaces")
    messages = relationship("Message", back_populates="space")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    space_id = Column(Integer, ForeignKey("spaces.id"))
    content = Column(Text)
    message_type = Column(String(20), default="chat")  # chat, system, move
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="messages")
    space = relationship("Space", back_populates="messages")
