import requests


ALGOLIA_URL = "https://uls2j1qb99-dsn.algolia.net/1/indexes/*/queries"
ALGOLIA_HEADERS = {
        "x-algolia-api-key": "2e55cc92d08f358ca67f949b47022d94",
        "x-algolia-application-id": "ULS2J1QB99"
}

def resolve_psn_product_id(psn_id: str, title: str) -> str:
    payload = {"requests": [{
                "indexName": "crawler_en-bg",
                "query": "hades",
                "params": "hitsPerPage=30&filters=pageType:game"
            }]}

    response = requests.post(ALGOLIA_URL, headers=ALGOLIA_HEADERS, json=payload)
    response.raise_for_status()

    data = response.json()
    hits = data['results'][0]['hits']
    match = next((h for h in hits if h.get('conceptId') == psn_id), None)


    if not match or not match.get('skuIds'):
        return None

    sku_id = match['skuIds'][0]
    return sku_id.rsplit('-', 1)[0]

