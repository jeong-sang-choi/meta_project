from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json
import os
from typing import List, Dict
import asyncio

from database import engine, Base
from models import User, Space
from schemas import UserCreate, UserResponse, SpaceCreate, SpaceResponse
from services import UserService, SpaceService, ImageService
from websocket_manager import ConnectionManager

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyMetaVerse", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket 연결 관리자
manager = ConnectionManager()

# 서비스 인스턴스
user_service = UserService()
space_service = SpaceService()
image_service = ImageService()

@app.get("/")
async def root():
    return {"message": "Welcome to MyMetaVerse API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 사용자 관련 엔드포인트
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    return await user_service.create_user(user)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return await user_service.get_user(user_id)

# 공간 관련 엔드포인트
@app.post("/spaces/", response_model=SpaceResponse)
async def create_space(space: SpaceCreate):
    return await space_service.create_space(space)

@app.get("/spaces/{space_id}", response_model=SpaceResponse)
async def get_space(space_id: int):
    return await space_service.get_space(space_id)

@app.get("/spaces/", response_model=List[SpaceResponse])
async def get_all_spaces():
    return await space_service.get_all_spaces()

# 이미지 업로드 및 공간 생성
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # 이미지 저장 및 분석
    image_path = await image_service.save_image(file)
    space_data = await image_service.analyze_image(image_path)
    
    return {
        "image_path": image_path,
        "space_data": space_data,
        "message": "Image uploaded and analyzed successfully"
    }

# WebSocket 연결
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 메시지 타입에 따른 처리
            if message["type"] == "join_space":
                await manager.join_space(user_id, message["space_id"])
            elif message["type"] == "chat":
                await manager.broadcast_to_space(
                    message["space_id"], 
                    {"type": "chat", "user_id": user_id, "message": message["message"]}
                )
            elif message["type"] == "move":
                await manager.broadcast_to_space(
                    message["space_id"],
                    {"type": "move", "user_id": user_id, "position": message["position"]}
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
