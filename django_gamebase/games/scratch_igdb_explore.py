from decouple import config
import json
import requests

CLIENT_ID = config('IGDB_CLIENT_ID')
ACCESS_TOKEN = config('IGDB_ACCESS_TOKEN')

def _get_headers():
    return {'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {ACCESS_TOKEN}'}

def test():
    query_body = f"""
                fields name,
            game_type,
            summary,
            storyline,
            genres.name,
            themes.name,
            keywords.name,
            game_modes.name,
            player_perspectives.name,
            multiplayer_modes.*,
            involved_companies.*,
            involved_companies.company.name,
            parent_game;
                where id = 114143
                ;
                """
    response = requests.post('https://api.igdb.com/v4/games',
                             headers=_get_headers(),
                             data=query_body)
    response.raise_for_status()
    results = response.json()
    print(json.dumps(results, indent=2))

