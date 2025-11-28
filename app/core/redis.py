from redis import Redis

redis = Redis(host="192.168.1.200", port=6379, db=0, decode_responses=True)

RATE_LIMIT_SECONDS = 30

def allow_request(key_id: int) -> bool:
    redis_key = f"rate_limit:{key_id}"

    # SETNX = set if not exists
    # возвращает True, если ключ был создан → запрос разрешён
    if redis.setnx(redis_key, "1"):
        redis.expire(redis_key, RATE_LIMIT_SECONDS)
        return True

    # ключ уже существует → лимит ещё не истёк
    return False