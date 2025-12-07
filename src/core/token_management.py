from typing import Optional
from src.core.redis_client import redis_client as redis 
from src.core.config import TOKEN_TTL
from src.core.logger import logger


def _build_key(key_id: int) -> str:
    return f"auth_token:{key_id}"


def get_token(key_id: int) -> Optional[str]:
    token = redis.get(_build_key(key_id))
    if token:
        logger.debug(f"Token loaded from redis for key_id={key_id}")
    return token


def set_token(key_id: int, token: str) -> None:
    redis.setex(_build_key(key_id), TOKEN_TTL, token)
    logger.debug(f"Token saved to redis for key_id={key_id}")


def delete_token(key_id: int) -> None:
    redis.delete(_build_key(key_id))
    logger.info(f"Token deleted from redis for key_id={key_id}")
