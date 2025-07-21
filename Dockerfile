FROM python:3.10-slim

# Обновление pip и установка зависимостей
RUN pip install --upgrade pip

WORKDIR /seemeego-ai

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Убедись, что папка temp-seemeego существует
RUN mkdir -p /seemeego-ai/temp-seemeego

# Запуск главного скрипта
CMD ["python", "seemeego_main.py"]