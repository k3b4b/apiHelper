import os
from dotenv import load_dotenv

load_dotenv()

# основное
APP_NAME = os.getenv("APP_NAME", "api-helper")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# база данных
DB_URL = os.getenv("DB_URL", "sqlite:///./data/data.db")

# ttl и таймауты
TOKEN_TTL = int(os.getenv("TOKEN_TTL", 3600))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", 10))
FERNET_KEY = os.getenv("FERNET_KEY")

# уровень логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_DECODE = os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true"

# auth
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
