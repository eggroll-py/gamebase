import requests
from decouple import config

BASE_URL = "https://api.igdb.com/v4"
CLIENT_ID = config('IGDB_CLIENT_ID')
ACCESS_TOKEN = config('IGDB_ACCESS_TOKEN')

def _get_headers():
    return {'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {ACCESS_TOKEN}'}

def _build_cover_url(url):
    if url is None:
        return None
    url = url.replace('t_thumb', 't_cover_big')
    if url.startswith('//'):
        url = 'https:' + url

    return url

def search_games(query, limit=10):
    query_body = f"""
            fields id, name, summary, cover.url,
               first_release_date, rating,
               genres.id, genres.name, genres.slug,
               platforms.id, platforms.name, platforms.slug;
            search "{query}";
            limit {limit};
            where name != null;
            """

    response = requests.post(f'{BASE_URL}/games',
                             headers=_get_headers(),
                             data=query_body)

    response.raise_for_status()
    raw_games = response.json()


    return [_parse_game(game) for game in raw_games]

def get_game_by_igdb_id(igdb_id):
    query_body = f"""
                fields id, name, summary, cover.url,
               first_release_date, rating,
               genres.id, genres.name, genres.slug,
               platforms.id, platforms.name, platforms.slug;
                
                where id = {igdb_id};
                """
    response = requests.post(f'{BASE_URL}/games',
                             headers=_get_headers(),
                             data=query_body)
    response.raise_for_status()
    results = response.json()

    if results is None:
        return None
    else:
        return _parse_game(results[0])

def get_external_ids(igdb_id):
    query_body = f"""
                fields uid, external_game_source;
                where game = {igdb_id};
                """
    response = requests.post(f'{BASE_URL}/external_games',
                             headers=_get_headers(),
                             data=query_body)
    response.raise_for_status()
    results = {'steam_id': None, 'itad_slug': None}

    for item in response.json():
        if item.get('external_game_source') == 1:
            try:
                results['steam_id'] = int(item['uid'])
            except (ValueError, TypeError):
                pass
    return results



def _parse_game(raw):
    release_date = None

    if raw.get('first_release_date'):
        from datetime import datetime, timezone
        release_date = datetime.fromtimestamp(raw['first_release_date'], tz=timezone.utc).date()

    return {
        'igdb_id': raw['id'],
        'title': raw['name'],
        'summary': raw.get('summary', ""),
        'cover_url': _build_cover_url(raw.get('cover', {}).get('url')),
        'release_date': release_date,
        'igdb_rating': raw.get('rating'),
        'genres': [
            {
                'igdb_id': g['id'],
                'name': g['name'],
                'slug': g['slug']
            }
            for g in raw.get('genres', [])
        ],
        'platforms': [
            {
                'igdb_id': p['id'],
                'name': p['name'],
                'slug': p['slug']
            }
            for p in raw.get('platforms', [])
        ]

    }