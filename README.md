# MyMetaVerse

사용자가 사진을 업로드하면 AI가 분석하여 개인화된 3D 메타버스 공간을 생성하는 프로젝트입니다.

## 주요 기능

- 🖼️ **이미지 업로드 및 분석**: 사진을 업로드하면 AI가 색상, 분위기, 객체를 분석
- 🏠 **자동 공간 생성**: 분석 결과를 바탕으로 개인화된 3D 공간 자동 생성
- 👥 **실시간 멀티플레이어**: WebSocket을 통한 실시간 사용자 간 상호작용
- 💬 **실시간 채팅**: 같은 공간에 있는 사용자들과 실시간 채팅
- 🎨 **공간 커스터마이징**: 가구 배치, 색상 변경 등 공간 개인화

## 기술 스택

### 백엔드
- **FastAPI**: 고성능 웹 API 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **SQLite**: 개발용 데이터베이스 (PostgreSQL로 확장 가능)
- **WebSocket**: 실시간 통신

### AI/ML
- **OpenCV**: 이미지 처리 및 분석
- **scikit-learn**: 색상 클러스터링
- **Pillow**: 이미지 조작

### 프론트엔드 (향후 구현 예정)
- **Three.js**: 3D 렌더링
- **React**: 사용자 인터페이스
- **WebRTC**: 실시간 통신

## 설치 및 실행

### 1. 가상환경 활성화
```bash
# Windows
.\Scripts\Activate.ps1

# 또는 CMD
Scripts\activate.bat
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 사용자 관리
- `POST /users/`: 새 사용자 생성
- `GET /users/{user_id}`: 사용자 정보 조회

### 공간 관리
- `POST /spaces/`: 새 공간 생성
- `GET /spaces/{space_id}`: 공간 정보 조회
- `GET /spaces/`: 모든 공개 공간 목록

### 이미지 업로드
- `POST /upload-image/`: 이미지 업로드 및 분석

### WebSocket
- `WS /ws/{user_id}`: 실시간 통신

## 프로젝트 구조

```
mymeta_bus/
├── main.py              # FastAPI 메인 애플리케이션
├── database.py          # 데이터베이스 설정
├── models.py            # SQLAlchemy 모델
├── schemas.py           # Pydantic 스키마
├── services.py          # 비즈니스 로직
├── websocket_manager.py # WebSocket 연결 관리
├── requirements.txt     # Python 의존성
├── README.md           # 프로젝트 문서
├── uploads/            # 업로드된 이미지 저장소
└── static/             # 정적 파일 (향후 추가)
```

## 개발 단계

### Phase 1: 기본 구조 ✅
- [x] FastAPI 서버 설정
- [x] 데이터베이스 모델 정의
- [x] 기본 API 엔드포인트
- [x] WebSocket 연결 관리

### Phase 2: 이미지 분석 및 공간 생성 ✅
- [x] 이미지 업로드 기능
- [x] 색상 분석
- [x] 분위기 분석
- [x] 공간 데이터 생성

### Phase 3: 3D 렌더링 (진행 예정)
- [ ] Three.js 연동
- [ ] 3D 공간 렌더링
- [ ] 사용자 아바타

### Phase 4: 고급 기능 (계획)
- [ ] AI 기반 객체 감지
- [ ] 음성 채팅
- [ ] 모바일 앱
- [ ] AR/VR 지원

## 사용 예시

### 1. 사용자 생성
```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### 2. 이미지 업로드
```bash
curl -X POST "http://localhost:8000/upload-image/" \
     -F "file=@your_image.jpg"
```

### 3. WebSocket 연결
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/1');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 연락처

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.
