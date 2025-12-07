# Базовый образ
FROM python:3.11-slim

# Отключаем буферизацию логов
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем python зависимости
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Порт, который будет слушать контейнер
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "src.main:apiHelper", "--host", "0.0.0.0", "--port", "8000"]
