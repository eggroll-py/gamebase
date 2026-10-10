from decimal import Decimal, ROUND_HALF_UP
import requests
from django.core.cache import cache


BASE_URL = "https://api.frankfurter.dev/v2/rate/"
RATE_CACHE_TTL = 60 * 60 * 24

def xrate_test():


    response = requests.get(f'{BASE_URL}/EUR/USD')

    response.raise_for_status()

    data = response.json()
    import json
    print(json.dumps(data))


def get_exchange_rate(from_currency: str, to_currency: str) -> Decimal:
    if from_currency == to_currency:
        return Decimal('1')

    cache_key = f'fx_rate:{from_currency}:{to_currency}'
    cached_rate = cache.get(cache_key)
    if cached_rate is not None:
        return Decimal(cached_rate)
    try:
        response = requests.get(f'{BASE_URL}{from_currency}/{to_currency}')
        response.raise_for_status()
        rate = response.json()['rate']
    except (requests.RequestException, KeyError):
        return None

    cache.set(cache_key, str(rate), RATE_CACHE_TTL)
    return Decimal(str(rate))

def convert_price(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    rate = get_exchange_rate(from_currency, to_currency)
    if rate is None:
        return amount
    converted = amount * rate
    return converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)



