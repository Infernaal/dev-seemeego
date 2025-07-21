import os
import cv2
import random
import string
import tempfile
import requests

# Папка для хранения временных файлов
TEMP_DIR = "temp-seemeego"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def generate_random_filename(length=10):
    """Генерация случайного имени для файла"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + ".jpg"

def extract_frame_from_video(video_url: str, at_second: float = 1.0):
    """Функция для извлечения кадра из видео и сохранения его в папку"""
    # Скачиваем видео во временный файл
    resp = requests.get(video_url, stream=True)
    resp.raise_for_status()
    
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        for chunk in resp.iter_content(1024 * 1024):
            tmp.write(chunk)
        tmp.flush()
        tmp_path = tmp.name

    # Открываем видео и захватываем нужный кадр
    cap = cv2.VideoCapture(tmp_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_number = int(fps * at_second)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()

    # Генерация случайного имени для изображения
    filename = generate_random_filename()
    image_path = os.path.join(TEMP_DIR, filename)
    
    # Сохранение кадра как изображения
    cv2.imwrite(image_path, frame)

    return image_path

def generate_image_url(image_path: str) -> str:
    return f"https://dev-ai.dubadu.com/{image_path}"  # Или путь на сервере
