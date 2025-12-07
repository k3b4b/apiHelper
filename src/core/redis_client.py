from redis import Redis
from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_DECODE

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=REDIS_DECODE
)