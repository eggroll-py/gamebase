import requests
from decouple import config

response = requests.post("https://api.igdb.com/v4/games",
headers = {"Client-ID": config("IGDB_CLIENT_ID"),
           "Authorization": f"Bearer {config('IGDB_ACCESS_TOKEN')}"},
data = 'fields id, name, rating; search "Witcher 3"; limit 3;')

print(response.status_code)
print(response.json())