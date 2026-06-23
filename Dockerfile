FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание папок для изображений
RUN mkdir -p static/images/products static/images/banners static/images/team

# Открываем порт
EXPOSE 5000

# Запуск приложения
CMD ["python", "app.py"]