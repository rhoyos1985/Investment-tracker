# backend/app/core/redis.py
from redis import Redis
import json
from app.infrastructure.settings.api_settings import settings
from typing import Optional, Any

class RedisClient:
    def __init__(self):
        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
    def set_key(self, key: str, value: Any, expire: int = 3600):
        """Almacena valor en Redis con expiración"""
        serialized_value = json.dumps(value)
        self.redis_client.setex(key, expire, serialized_value)
    
    def get_key(self, key: str) -> Optional[Any]:
        """Obtiene valor de Redis"""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def delete_key(self, key: str):
        """Elimina clave de Redis"""
        self.redis_client.delete(key)
    
    def key_exists(self, key: str) -> bool:
        """Verifica si una clave existe"""
        return self.redis_client.exists(key) == 1

# Instancia global
redis_instance = RedisClient()
