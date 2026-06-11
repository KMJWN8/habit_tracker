#!/bin/bash
set -e

echo "Применение миграций Alembic..."
# Запускаем миграции. Если их нет, alembic просто завершится успешно.
alembic upgrade head

echo "Запуск приложения..."
# Передаем управление основной команде из Dockerfile (CMD)
exec "$@"