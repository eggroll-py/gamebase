import requests

ALGOLIA_URL = "https://fmw57f6erv-dsn.algolia.net/1/indexes/*/queries"
ALGOLIA_HEADERS = {
    "x-algolia-api-key": "c8e4e9f60190ef785d167da77ba0b4fe",
    "x-algolia-application-id": "FMW57F6ERV",
}

def resolve_eshop_id(game) -> dict:
    payload = {"requests": [{"indexName": "prod_games", "query": game.title, "hitsPerPage": 8, "page": 0}]}

    response = requests.post(ALGOLIA_URL, headers=ALGOLIA_HEADERS, json=payload)
    response.raise_for_status()
    hits = response.json()['results'][0]['hits']

    platform_list = set(game.platforms.values_list('name', flat=True))

    best_hit = None
    best_score = -1
    best_matching_title = False

    for hit in hits:
        title_match = hit.get('title', '').strip().lower() == game.title.strip().lower()
        platform_match = ('Nintendo Switch' in platform_list and hit.get('console') == 'Nintendo Switch') or ('Nintendo Switch 2' in platform_list and hit.get('console') == 'Nintendo Switch 2')

        date_match = False
        date_tag = hit.get('dateTag')

        if isinstance(date_tag, dict):
            year = date_tag.get('year')
        elif isinstance(date_tag, str):
            try:
                year = int(date_tag)
            except ValueError:
                year = None
        else:
            year = None

        if year is not None and game.release_date:
            date_match = abs(year - game.release_date.year) <= 1

        score = sum([date_match, title_match, platform_match])
        if score > best_score:
            best_hit, best_score, best_matching_title = hit, score, title_match



    if best_hit is None:
        return {'eshop_id': None, 'eshop_verified': False, 'eshop_url': None}

    verified = best_matching_title and best_score == 3
    full_url = best_hit.get('fullURL')
    eshop_url = f"https://www.nintendo.com/au{full_url}" if full_url else None

    return {
        'eshop_id': best_hit.get('nsuid'),
        'eshop_verified': verified,
        'eshop_url': eshop_url}





