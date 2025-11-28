from fastapi import HTTPException, Path
from app.core.redis import allow_request

def limit_api_calls():
    def dependency(key_id: int = Path(...)):
        if not allow_request(key_id):
            raise HTTPException(429, "Слишком частые запросы. Повторите позже.")
    return dependency