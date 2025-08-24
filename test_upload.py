import requests
import os

def test_image_upload():
    url = "http://localhost:8000/upload-image/"
    
    # 테스트 이미지 파일 경로
    image_path = "static/test_image.jpg"
    
    if not os.path.exists(image_path):
        print(f"이미지 파일이 없습니다: {image_path}")
        return
    
    try:
        # 이미지 파일 업로드
        with open(image_path, "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = requests.post(url, files=files)
        
        print(f"상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== 이미지 분석 결과 ===")
            print(f"이미지 경로: {result.get('image_path')}")
            print(f"주요 색상: {result.get('space_data', {}).get('dominant_colors', [])}")
            print(f"분위기: {result.get('space_data', {}).get('mood', '')}")
            print(f"공간 스타일: {result.get('space_data', {}).get('space_style', '')}")
        else:
            print("업로드 실패!")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_image_upload()
