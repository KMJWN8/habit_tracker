import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Перевод времени логов в UTC
logging.Formatter.converter = time.gmtime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                LOG_DIR / "app.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            ),
        ],
        force=True,
    )

    # Глушим "шумные" библиотеки, чтобы не засорять логи
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)