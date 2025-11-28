from loguru import logger
import sys

# Удаляем дефолтные хендлеры
logger.remove()

# Консольный вывод
logger.add(sys.stdout, level="INFO")

# Файл с ротацией 10 MB и хранением 30 дней
logger.add("logs/full.log", rotation="10 MB", retention="7 days", compression="zip")
logger.add("logs/error.log", level="ERROR", rotation="5 MB", retention="7 days", compression="zip")

# Можно вернуть объект, но loguru рекомендует просто импортировать logger напрямую
