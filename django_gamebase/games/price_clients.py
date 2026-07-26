from decouple import config
import requests
from decimal import Decimal

STEAM_URL = 'https://store.steampowered.com/api/appdetails'

def get_steam_price(steam_id):
    response = requests.get(STEAM_URL,
                            params={
                                'appids': steam_id,
                                'cc': 'de',
                                'filters': 'price_overview'
                            })
    response.raise_for_status()
    raw_data = response.json()
    # return raw_data
    game_data = raw_data.get(str(steam_id), {})


    if not game_data['success']:
        return None

    data = game_data['data']
    if not data:
        return {
        'store': 'steam',
        'price': Decimal(0),
        'original_price': None,
        'on_sale': False,
        'url': f"https://store.steampowered.com/app/{steam_id}/"
    }

    price_overview = data.get('price_overview')
    if not price_overview:
        return None

    price = price_overview['final']
    original_price = price_overview['initial']
    discount = price_overview['discount_percent']


    return {
        'store': 'steam',
        'price': Decimal(price) / 100,
        'original_price': Decimal(original_price) / 100 if discount > 0 else None,
        'on_sale': discount > 0,
        'url': f"https://store.steampowered.com/app/{steam_id}/"
    }









def get_itad_prices(itad_slug):
    return []


