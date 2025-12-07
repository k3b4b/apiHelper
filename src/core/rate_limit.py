from fastapi import HTTPException, Path
from redis import Redis
from src.core.logger import logger

#прокинуть всё в енв
RATE_LIMIT_SECONDS = 10
red = Redis(host="192.168.1.200", port=6379, db=0, decode_responses=True)

# проверка на рейтлимит, простое ограничение - 1 запрос по эндпоинту на RATE_LIMIT_SECONDS секунд
def request_is_limited(request_type: str, key_id: int) -> bool:
    red_key = f"rate_limit: {key_id}|{request_type}"
    if red.setnx(red_key, "1"):
        red.expire(red_key, RATE_LIMIT_SECONDS)
        return False
    logger.warning(f"Request {request_type} is limited due to rate limiting.")
    return True
