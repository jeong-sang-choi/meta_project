from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Space, Message
from schemas import UserCreate, SpaceCreate, ImageAnalysisResult
from passlib.context import CryptContext
import cv2
import numpy as np
from PIL import Image
import os
import uuid
from typing import List, Optional
import json

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self):
        self.db = SessionLocal()
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user: UserCreate) -> User:
        hashed_password = self.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

class SpaceService:
    def __init__(self):
        self.db = SessionLocal()
    
    async def create_space(self, space: SpaceCreate) -> Space:
        db_space = Space(**space.dict())
        self.db.add(db_space)
        self.db.commit()
        self.db.refresh(db_space)
        return db_space
    
    async def get_space(self, space_id: int) -> Optional[Space]:
        return self.db.query(Space).filter(Space.id == space_id).first()
    
    async def get_all_spaces(self) -> List[Space]:
        return self.db.query(Space).filter(Space.is_public == True).all()
    
    async def get_user_spaces(self, user_id: int) -> List[Space]:
        return self.db.query(Space).filter(Space.owner_id == user_id).all()
    
    async def update_space(self, space_id: int, space_data: dict) -> Optional[Space]:
        space = await self.get_space(space_id)
        if space:
            for key, value in space_data.items():
                setattr(space, key, value)
            self.db.commit()
            self.db.refresh(space)
        return space

class ImageService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.ensure_upload_dir()
    
    def ensure_upload_dir(self):
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    async def save_image(self, file) -> str:
        # 고유한 파일명 생성
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # 파일 저장
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return file_path
    
    async def analyze_image(self, image_path: str) -> dict:
        """이미지를 분석하여 공간 생성에 필요한 데이터 추출"""
        try:
            # OpenCV로 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("이미지를 로드할 수 없습니다")
            
            # 색상 분석
            dominant_colors = self.extract_dominant_colors(image)
            
            # 분위기 분석
            mood = self.analyze_mood(image)
            
            # 객체 감지 (간단한 버전)
            objects_detected = self.detect_objects(image)
            
            # 공간 스타일 결정
            space_style = self.determine_space_style(dominant_colors, mood)
            
            # 조명 설정
            lighting = self.determine_lighting(mood)
            
            return {
                "dominant_colors": dominant_colors,
                "mood": mood,
                "objects_detected": objects_detected,
                "space_style": space_style,
                "lighting": lighting,
                "space_data": self.generate_space_data(space_style, dominant_colors, lighting)
            }
            
        except Exception as e:
            # 오류 발생 시 기본값 반환
            return {
                "dominant_colors": ["#ffffff", "#000000"],
                "mood": "neutral",
                "objects_detected": [],
                "space_style": "modern",
                "lighting": "bright",
                "space_data": self.generate_default_space_data()
            }
    
    def extract_dominant_colors(self, image: np.ndarray) -> List[str]:
        """이미지에서 주요 색상 추출"""
        # 이미지를 RGB로 변환
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 이미지를 1차원 배열로 변환
        pixels = image_rgb.reshape(-1, 3)
        
        # K-means 클러스터링으로 주요 색상 추출
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(pixels)
        
        # 클러스터 중심을 색상으로 변환
        colors = kmeans.cluster_centers_.astype(int)
        
        # RGB를 HEX로 변환
        hex_colors = []
        for color in colors:
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            hex_colors.append(hex_color)
        
        return hex_colors[:3]  # 상위 3개 색상만 반환
    
    def analyze_mood(self, image: np.ndarray) -> str:
        """이미지 분위기 분석"""
        # 밝기 계산
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # 채도 계산
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv[:, :, 1])
        
        if brightness > 150:
            if saturation > 100:
                return "bright_vibrant"
            else:
                return "bright_calm"
        else:
            if saturation > 100:
                return "dark_vibrant"
            else:
                return "dark_calm"
    
    def detect_objects(self, image: np.ndarray) -> List[str]:
        """간단한 객체 감지 (실제로는 더 정교한 모델 사용)"""
        # 여기서는 간단한 색상 기반 감지
        objects = []
        
        # 파란색 영역 (하늘, 바다 등)
        blue_mask = cv2.inRange(image, (100, 0, 0), (255, 100, 100))
        if np.sum(blue_mask) > 10000:
            objects.append("sky_or_water")
        
        # 녹색 영역 (자연, 식물 등)
        green_mask = cv2.inRange(image, (0, 100, 0), (100, 255, 100))
        if np.sum(green_mask) > 10000:
            objects.append("nature")
        
        return objects
    
    def determine_space_style(self, colors: List[str], mood: str) -> str:
        """색상과 분위기를 바탕으로 공간 스타일 결정"""
        if "bright" in mood:
            if any(self.is_warm_color(color) for color in colors):
                return "modern_warm"
            else:
                return "modern_minimal"
        else:
            if any(self.is_warm_color(color) for color in colors):
                return "cozy_rustic"
            else:
                return "industrial"
    
    def is_warm_color(self, hex_color: str) -> bool:
        """따뜻한 색상인지 판단"""
        # HEX를 RGB로 변환
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # 빨간색과 주황색 성분이 많으면 따뜻한 색상
        return r > g and r > b
    
    def determine_lighting(self, mood: str) -> str:
        """분위기에 따른 조명 설정"""
        if "bright" in mood:
            return "bright"
        else:
            return "dim"
    
    def generate_space_data(self, style: str, colors: List[str], lighting: str) -> dict:
        """공간 스타일에 따른 3D 공간 데이터 생성"""
        base_space = {
            "walls": {
                "material": "concrete",
                "color": colors[0] if colors else "#ffffff"
            },
            "floor": {
                "material": "wood",
                "color": colors[1] if len(colors) > 1 else "#8B4513"
            },
            "ceiling": {
                "material": "concrete",
                "color": "#ffffff"
            },
            "lighting": {
                "type": lighting,
                "intensity": 1.0 if lighting == "bright" else 0.3
            },
            "furniture": []
        }
        
        # 스타일에 따른 가구 추가
        if "modern" in style:
            base_space["furniture"] = [
                {"type": "sofa", "position": [0, 0, -2], "color": colors[0]},
                {"type": "coffee_table", "position": [0, 0, -1], "color": "#8B4513"},
                {"type": "lamp", "position": [2, 1, -2], "color": "#FFD700"}
            ]
        elif "cozy" in style:
            base_space["furniture"] = [
                {"type": "armchair", "position": [0, 0, -2], "color": "#8B4513"},
                {"type": "fireplace", "position": [0, 0, -3], "color": "#696969"},
                {"type": "bookshelf", "position": [3, 0, 0], "color": "#8B4513"}
            ]
        
        return base_space
    
    def generate_default_space_data(self) -> dict:
        """기본 공간 데이터"""
        return {
            "walls": {"material": "concrete", "color": "#ffffff"},
            "floor": {"material": "wood", "color": "#8B4513"},
            "ceiling": {"material": "concrete", "color": "#ffffff"},
            "lighting": {"type": "bright", "intensity": 1.0},
            "furniture": [
                {"type": "sofa", "position": [0, 0, -2], "color": "#87CEEB"},
                {"type": "coffee_table", "position": [0, 0, -1], "color": "#8B4513"}
            ]
        }
