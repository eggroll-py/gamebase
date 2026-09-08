import pytest
import requests
from app.price_clients import get_steam_price, get_psn_price, get_eshop_price



@pytest.mark.live
def test_steam_contract():
    response = requests.get('https://store.steampowered.com/api/appdetails',
                            params={'appids': 220, 'cc':'de', 'filters':'price_overview'})

    raw = response.json()
    game_data = raw['220']
    assert 'success' in game_data
    assert 'data' in game_data
    price_overview = game_data['data'] ['price_overview']
    assert 'final' in price_overview
    assert 'initial' in price_overview
    assert 'discount_percent' in price_overview
    assert 'currency' in price_overview

@pytest.mark.live
def test_psn_price_contract():
    response = requests.get("https://web.np.playstation.com/api/graphql/v1/op",
                            params={
        "operationName": "productRetrieveForCtasWithPrice",
        "variables": '{"productId":"EP4484-PPSA03711_00-3235764131417729"}',
        "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"1f0ca607e170abbfb7d67bd76c9bbc97f21fe2e807be49e5fe764e14566cb605"}}'}, headers={'apollo-require-preflight':'true'})

    raw = response.json()
    assert 'data' in raw
    product = raw['data']['productRetrieve']

    assert 'webctas' in product
    ctas = product['webctas']
    specific_cta = ctas[0]
    assert 'price' in specific_cta
    price_data = specific_cta['price']
    assert 'basePriceValue' in price_data
    assert 'currencyCode' in price_data
    assert 'discountedValue' in price_data

@pytest.mark.live
def test_eshop_price_contract():
    response = requests.get("https://wb.lp1.savanna.srv.nintendo.net/graphql",
        params={
        "operationName": "ItemUserPrices",
        "variables": '{"country":"DE","language":"en","nsUids":[70010000033132],"shopId":3}',
        "extensions": '{"persistedQuery":{"sha256Hash":"6d4a1cbb290cd40b333c65f6dbe4c986dde65b17ce9ce83659ffff915a08245e","version":1}}',
    }, headers={
        "x-nintendo-savanna-client-id": "042e4bd1f0eec144167dbc0c63f1d17876e7b9ec322713b613614214e3675df9",
        'apollo-require-preflight': 'true'
    })

    raw = response.json()
    assert 'data' in raw
    data = raw['data']
    assert 'prices' in data
    prices = data['prices'][0]
    assert 'regularPrice' in prices
    assert 'discountPrice' in prices








