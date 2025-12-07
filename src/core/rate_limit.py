from fastapi import HTTPException, Path
from src.core.logger import logger
from src.core.config import RATE_LIMIT_SECONDS
from src.core.redis_client import redis_client as redis

# проверка на рейтлимит, простое ограничение - 1 запрос по эндпоинту на RATE_LIMIT_SECONDS секунд
def request_is_limited(request_type: str, key_id: int) -> bool:
    red_key = f"rate_limit:{key_id}:{request_type}"
    if redis.setnx(red_key, "1"):
        redis.expire(red_key, RATE_LIMIT_SECONDS)
        return False
    logger.warning(f"Request {request_type} is limited due to rate limiting.")
    return True
