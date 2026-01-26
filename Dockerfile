# Базовый образ
FROM python:3.10-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Копируем весь проект
COPY . .

# Открываем порт (для документации, но запуск командой в docker-compose)
EXPOSE 8000
