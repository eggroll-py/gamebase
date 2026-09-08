import json

from app.config import settings
import requests


ITAD_PRICES_URL = 'https://api.isthereanydeal.com/games/prices/v3'

STEAM_ID = 1145350



def inspect_itad(itad_id='018d937f-21e1-728e-86d7-9acb3c59f2bb', country="us"):
    response = requests.post(
        ITAD_PRICES_URL,
        params={
            "key": settings.ITAD_API_KEY,
            "country": country,
        },
        json=[itad_id],
    )

    response.raise_for_status()

    data = response.json()

    print(json.dumps(data, indent=2))

def psn_test():
    url = "https://web.np.playstation.com/api/graphql/v1/op"
    params = {
        "operationName": "productRetrieveForCtasWithPrice",
        "variables": '{"productId":"EP4484-PPSA03711_00-3235764131417729", "country":"DE"}',
        "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"1f0ca607e170abbfb7d67bd76c9bbc97f21fe2e807be49e5fe764e14566cb605"}}'
    }
    headers = {"apollo-require-preflight": "true"}

    response = requests.get(url, params=params, headers=headers)
    print(response.status_code)
    import json
    print(json.dumps(response.json(), indent=2))

def psn_algolia_test():
    algolia_url = "https://uls2j1qb99-dsn.algolia.net/1/indexes/*/queries"
    aloglia_headers = {
        "x-algolia-api-key": "2e55cc92d08f358ca67f949b47022d94",
        "x-algolia-application-id": "ULS2J1QB99",
    }
    payload = {
        "requests": [
            {
                "indexName": "crawler_de-de",
                "query": "hades",
                "params": "hitsPerPage=30&filters=pageType:game"
            }
        ]
    }
    response = requests.post(algolia_url, headers=aloglia_headers, json=payload)
    print(response.status_code)
    data = response.json()
    print(data)
    hits = data['results'][0]['hits']
    match = next((h for h in hits if h.get('conceptId') == '10002648'), None)

    sku_id = match['skuIds'][0]
    product_id = sku_id.rsplit('-', 1)[0]
    print(product_id)

def eshop_test():
    url = "https://wb.lp1.savanna.srv.nintendo.net/graphql"
    params = {
        "operationName": "ItemUserPrices",
        "variables": '{"country":"DE","language":"en","nsUids":[70010000033132, 70010000029236],"shopId":3}',
        "extensions": '{"persistedQuery":{"sha256Hash":"6d4a1cbb290cd40b333c65f6dbe4c986dde65b17ce9ce83659ffff915a08245e","version":1}}',
    }
    headers = {
        "x-nintendo-savanna-client-id": "042e4bd1f0eec144167dbc0c63f1d17876e7b9ec322713b613614214e3675df9",
        'apollo-require-preflight': 'true'


    }

    response = requests.get(url,params=params, headers=headers)
    print(response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

