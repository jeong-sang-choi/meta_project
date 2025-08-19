from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # 사용자별 WebSocket 연결
        self.active_connections: Dict[int, WebSocket] = {}
        
        # 공간별 접속한 사용자들
        self.space_users: Dict[int, Set[int]] = {}
        
        # 사용자가 접속한 공간
        self.user_spaces: Dict[int, int] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """사용자 연결"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # 연결 확인 메시지 전송
        await self.send_personal_message(
            {"type": "connection_established", "user_id": user_id}, 
            user_id
        )
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """사용자 연결 해제"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # 사용자가 접속한 공간에서 제거
        if user_id in self.user_spaces:
            space_id = self.user_spaces[user_id]
            if space_id in self.space_users:
                self.space_users[space_id].discard(user_id)
            del self.user_spaces[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """특정 사용자에게 메시지 전송"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                # 연결이 끊어진 경우 정리
                if user_id in self.active_connections:
                    del self.active_connections[user_id]
    
    async def broadcast_to_space(self, space_id: int, message: dict):
        """특정 공간의 모든 사용자에게 메시지 브로드캐스트"""
        if space_id in self.space_users:
            disconnected_users = []
            
            for user_id in self.space_users[space_id]:
                try:
                    await self.send_personal_message(message, user_id)
                except Exception as e:
                    print(f"Error broadcasting to user {user_id}: {e}")
                    disconnected_users.append(user_id)
            
            # 연결이 끊어진 사용자들 정리
            for user_id in disconnected_users:
                self.space_users[space_id].discard(user_id)
                if user_id in self.user_spaces:
                    del self.user_spaces[user_id]
    
    async def join_space(self, user_id: int, space_id: int):
        """사용자가 공간에 입장"""
        # 이전 공간에서 나가기
        if user_id in self.user_spaces:
            old_space_id = self.user_spaces[user_id]
            if old_space_id in self.space_users:
                self.space_users[old_space_id].discard(user_id)
        
        # 새 공간에 입장
        if space_id not in self.space_users:
            self.space_users[space_id] = set()
        
        self.space_users[space_id].add(user_id)
        self.user_spaces[user_id] = space_id
        
        # 입장 메시지 브로드캐스트
        join_message = {
            "type": "user_joined",
            "user_id": user_id,
            "space_id": space_id,
            "users_in_space": list(self.space_users[space_id])
        }
        
        await self.broadcast_to_space(space_id, join_message)
        
        # 입장한 사용자에게 현재 공간 정보 전송
        await self.send_personal_message({
            "type": "space_info",
            "space_id": space_id,
            "users_in_space": list(self.space_users[space_id])
        }, user_id)
    
    async def leave_space(self, user_id: int):
        """사용자가 공간에서 나감"""
        if user_id in self.user_spaces:
            space_id = self.user_spaces[user_id]
            
            if space_id in self.space_users:
                self.space_users[space_id].discard(user_id)
            
            del self.user_spaces[user_id]
            
            # 나감 메시지 브로드캐스트
            leave_message = {
                "type": "user_left",
                "user_id": user_id,
                "space_id": space_id,
                "users_in_space": list(self.space_users.get(space_id, set()))
            }
            
            await self.broadcast_to_space(space_id, leave_message)
    
    def get_users_in_space(self, space_id: int) -> List[int]:
        """공간에 있는 사용자 목록 반환"""
        return list(self.space_users.get(space_id, set()))
    
    def get_user_space(self, user_id: int) -> int:
        """사용자가 접속한 공간 ID 반환"""
        return self.user_spaces.get(user_id, None)
    
    def get_connection_count(self) -> int:
        """현재 연결된 사용자 수 반환"""
        return len(self.active_connections)
