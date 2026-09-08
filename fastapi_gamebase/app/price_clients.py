import requests
from decimal import Decimal


STEAM_URL = 'https://store.steampowered.com/api/appdetails'
def get_steam_price(steam_id: int) -> dict | None:
    response = requests.get(STEAM_URL, params={'appids': steam_id, 'cc':'de', 'filters':'price_overview'})

    response.raise_for_status()
    raw = response.json()


    game_data = raw.get(str(steam_id), {})
    if not game_data['success']:
        return None

    data = game_data['data']
    if not data:
        return {
            'store': 'steam',
            'price': Decimal(0),
            'original_price': None,
            'on_sale': False,
            'url': f"https://store.steampowered.com/app/{steam_id}/",
            'currency': '-'
        }
    price_overview = data.get('price_overview')
    price = price_overview['final']
    original_price = price_overview['initial']
    discount = price_overview['discount_percent']

    return {
        'store': 'steam',
        'price': Decimal(price) / 100,
        'original_price': Decimal(original_price) / 100 if discount > 0 else None,
        'on_sale': discount > 0,
        'currency': price_overview['currency'],
        'url': f"https://store.steampowered.com/app/{steam_id}/"
    }

PSN_URL = "https://web.np.playstation.com/api/graphql/v1/op"
PSN_PRICE_HASH = "1f0ca607e170abbfb7d67bd76c9bbc97f21fe2e807be49e5fe764e14566cb605"
def get_psn_price(product_id: str) -> dict | None:
    params = {
        "operationName": "productRetrieveForCtasWithPrice",
        "variables": f'{{"productId":"{product_id}"}}',
        "extensions": f'{{"persistedQuery":{{"version":1,"sha256Hash":"{PSN_PRICE_HASH}"}}}}'
    }
    headers = {'apollo-require-preflight':'true'}

    response = requests.get(PSN_URL, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    product = data.get('data',{}).get('productRetrieve')
    if not product:
        return None
    ctas = product.get('webctas', [])
    if not ctas:
        return None
    price_data = ctas[0].get('price')
    if not price_data:
        return None

    base = price_data['basePriceValue']
    discounted = price_data['discountedValue']
    on_sale = discounted < base

    return {
        'store': 'psn',
        'price': Decimal(discounted) / 100,
        'original_price': Decimal(base) / 100 if on_sale else None,
        'on_sale': on_sale,
        'currency': price_data['currencyCode'],
        'url': f"https://store.playstation.com/product/{product_id}"
    }

ESHOP_URL = "https://wb.lp1.savanna.srv.nintendo.net/graphql"
ESHOP_PRICE_HASH = "6d4a1cbb290cd40b333c65f6dbe4c986dde65b17ce9ce83659ffff915a08245e"
ESHOP_REGION = 'DE'
def get_eshop_price(eshop_id: str, eshop_url: str) -> dict:
    params = {
        "operationName": "ItemUserPrices",
        "variables": f'{{"country":"{ESHOP_REGION}","language":"en","nsUids":[{int(eshop_id)}],"shopId":3}}',
        "extensions": f'{{"persistedQuery":{{"sha256Hash":"{ESHOP_PRICE_HASH}","version":1}}}}',
    }
    headers = {
        "x-nintendo-savanna-client-id": "042e4bd1f0eec144167dbc0c63f1d17876e7b9ec322713b613614214e3675df9",
        'apollo-require-preflight': 'true'
    }
    response = requests.get(ESHOP_URL, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    prices = data.get('data', {}).get('prices', [])
    if not prices:
        return None

    price_info = prices[0]
    regular = price_info.get('regularPrice')
    if not regular:
        return None

    discount = price_info.get('discountPrice')
    on_sale = discount is not None

    return {
        'store': 'eshop',
        'price': Decimal(discount['rawValue']) if discount else Decimal(regular['rawValue']),
        'original_price': Decimal(regular['rawValue']) if on_sale else None,
        'on_sale': on_sale,
        'currency': regular['currency'],
        'url': eshop_url
    }








