import requests
from decouple import config
import json

BASE_URL = "https://api.igdb.com/v4"
CLIENT_ID = config('IGDB_CLIENT_ID')
ACCESS_TOKEN = config('IGDB_ACCESS_TOKEN')


def igdb_debug(endpoint, query):
    response = requests.post(f'{BASE_URL}/{endpoint}',
                             headers=_get_headers(),
                             data=query)

    response.raise_for_status()
    data = response.json()
    print(data)

def igdb_new_access_token():
    TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    response = requests.post(TOKEN_URL,
                             data={
                                 'client_id': config('IGDB_CLIENT_ID'),
                                 'client_secret': config('IGDB_CLIENT_SECRET'),
                                 'grant_type': 'client_credentials'
                             })
    print(response.json())


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
               first_release_date, rating, game_type,
               genres.id, genres.name, genres.slug, parent_game,
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
               first_release_date, rating, game_type,
               genres.id, genres.name, genres.slug,
               platforms.id, platforms.name, platforms.slug,
               themes.id, themes.name, themes.slug, parent_game, bundles, version_parent;
                
                where id = {igdb_id};
                """
    response = requests.post(f'{BASE_URL}/games',
                             headers=_get_headers(),
                             data=query_body)
    response.raise_for_status()
    results = response.json()

    if not results:
        return None
    else:
        return _parse_game(results[0])

def get_games_by_igdb_ids(igdb_ids):
    igdb_ids_str = ', '.join(str(igdb_id) for igdb_id in igdb_ids)

    query_body = f"""
                fields id, name, summary, cover.url,
               first_release_date, rating,
               genres.id, genres.name, genres.slug, game_type, 
               platforms.id, platforms.name, platforms.slug,
               themes.id, themes.name, themes.slug, bundles, parent_game, version_parent;
                
                where id = ({igdb_ids_str}); limit 500;
                   """
    response = requests.post(f'{BASE_URL}/games',
                             headers=_get_headers(),
                             data=query_body)
    response.raise_for_status()
    results = response.json()



    return [_parse_game(game) for game in results]

EXTERNAL_SOURCE_MAP = {
    1: 'steam_id',
    5: 'gog_id',
    20: 'amazon_id',
    36: 'psn_id'
}

NUMERIC_FIELDS = {'steam_id'}

def get_external_ids(igdb_id):
    source_ids = tuple(EXTERNAL_SOURCE_MAP.keys())
    query_body = f"""
                fields uid, external_game_source;
                where game = {igdb_id} & external_game_source = {source_ids}; limit 500;
                """
    response = requests.post(f'{BASE_URL}/external_games',
                             headers=_get_headers(),
                             data=query_body)
    response.raise_for_status()
    results = {'steam_id': None, 'psn_id': None}

    for item in response.json():
        source = item.get('external_game_source')
        field_name = EXTERNAL_SOURCE_MAP.get(source)
        if field_name:
            raw_value = item.get('uid')
            if field_name in NUMERIC_FIELDS:
                try:
                    results[field_name] = int(item['uid'])
                except (ValueError, TypeError):
                    pass
            else:
                results[field_name] = raw_value

    return results



def _parse_game(raw):
    release_date = None

    if raw.get('first_release_date'):
        from datetime import datetime, timezone
        release_date = datetime.fromtimestamp(raw['first_release_date'], tz=timezone.utc).date()




    return {
        'igdb_id': raw['id'],
        'title': raw['name'],
        'parent_game': raw.get('parent_game'),
        'version_parent': raw.get('version_parent'),
        'bundle_ids': raw.get('bundles', []),
        'game_type': raw.get('game_type'),
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
        ],'themes': [
            {
                'igdb_id': t['id'],
                'name': t['name'],
                'slug': t['slug']
            }
            for t in raw.get('themes', [])
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