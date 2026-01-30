import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
    ],
)

# Создаем корневой логгер
logger = logging.getLogger("app")

# Настраиваем логгеры сторонних библиотек
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str = None):
    if name is None:
        return logger

    # Если имя уже содержит 'app.', используем как есть
    if name.startswith("app."):
        return logging.getLogger(name)

    # Иначе добавляем префикс
    return logging.getLogger(f"app.{name}")
