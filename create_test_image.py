from PIL import Image, ImageDraw
import os

# 테스트 이미지 생성
def create_test_image():
    # 400x300 크기의 이미지 생성
    width, height = 400, 300
    
    # 그라데이션 이미지 생성
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 그라데이션 그리기
    for y in range(height):
        r = int(255 * (1 - y / height))
        g = int(128 * (y / height))
        b = int(255 * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 간단한 도형 추가
    draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
    draw.ellipse([200, 100, 300, 200], fill='blue', outline='black')
    
    # 이미지 저장
    if not os.path.exists('static'):
        os.makedirs('static')
    
    image.save('static/test_image.jpg', 'JPEG')
    print("테스트 이미지가 생성되었습니다: static/test_image.jpg")

if __name__ == "__main__":
    create_test_image()
