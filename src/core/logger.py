from loguru import logger
from pathlib import Path
from src.core.config import LOG_LEVEL

import sys

# установка кастомных путей для красивого логирования формата services:db_service.py
def patch_record(record):
    file_path = Path(record["file"].path)
    record["extra"]["dir_name"] = file_path.parent.name    
    record["extra"]["file_name"] = file_path.name           

logger.configure(
    patcher=patch_record
)

# удаление дефолтных хендлеров
logger.remove()

# вывод в консоль
#logger.add(sys.stdout, level="INFO")

# файл с ротацией 10 MB и хранением 30 дней
logger.add("logs/full.log", level=LOG_LEVEL, format="[{time:YYYY-MM-DD HH:mm:ss.SSS}] | {level: <5} | [{line}] [{extra[dir_name]}:{extra[file_name]}] - {message}", rotation="10 MB", retention="7 days", compression="zip")
logger.add("logs/error.log", level="ERROR", format="[{time:YYYY-MM-DD HH:mm:ss.SSS}] | {level: <5} | [{line}] [{extra[dir_name]}:{extra[file_name]}] - {message}", rotation="5 MB", retention="7 days", compression="zip")

# пример использования
# logger.info("This is an info message")
