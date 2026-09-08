import redis
import json
from decimal import Decimal
from app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

CACHE_TTL_SECONDS = 60 * 60 * 24 * 5

def get_cached_price(store: str, identifier: str) -> dict | None:
    key = f'{store}:{identifier}'
    cached = redis_client.get(key)
    if cached is None:
        return None

    data = json.loads(cached)
    data['price'] = Decimal(data['price'])
    if data['original_price'] is not None:
        data['original_price'] = Decimal(data['original_price'])
    return data

def set_cached_price(store: str, identifier: str, price_data: dict) -> None:
    key = f'{store}:{identifier}'
    serializable = {
        **price_data,
        'price': str(price_data['price']),
        'original_price': str(price_data['original_price']) if price_data['original_price'] is not None else None,
    }
    redis_client.set(key, json.dumps(serializable), ex=CACHE_TTL_SECONDS)




