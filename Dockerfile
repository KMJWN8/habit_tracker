FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    TZ=Europe/Moscow

# Системные зависимости для сборки psycopg2 и asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Копируем ТОЛЬКО файл с закрепленными зависимостями для кэширования слоя
COPY requirements/base.txt .

# 2. Устанавливаем production-зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r base.txt

# 3. Копируем весь исходный код (включая requirements/, но они уже не повлияют на pip install)
COPY --chown=appuser:appuser . .

# Создаем и переключаемся на непривилегированного пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Скрипт для миграций перед запуском
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]