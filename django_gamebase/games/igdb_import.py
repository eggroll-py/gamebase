from . import igdb_client
from .models import Game,Genre,Platform
from django.utils import timezone

def import_game_from_igdb_data(game_data):
    genres = []
    for genre_data in game_data.get('genres', []):
        genre, _ = Genre.objects.get_or_create(
            igdb_id = genre_data.get('igdb_id'),
            defaults = {
                'name' : genre_data.get('name'),
                'slug' : genre_data.get('slug')
            }
        )
        genres.append(genre)

    platforms = []
    for platform_data in game_data.get('platforms', []):
        platform, _ = Platform.objects.get_or_create(
            igdb_id = platform_data.get('igdb_id'),
            defaults = {
                'name': platform_data.get('name'),
                'slug' : platform_data.get('slug')
            }
        )
        platforms.append(platform)


    game, created = Game.objects.update_or_create(
        igdb_id = game_data['igdb_id'],
        defaults = {
            'title': game_data['title'],
            'cover_url': game_data.get('cover_url'),
            'summary': game_data.get('summary', ''),
            'release_date': game_data.get('release_date'),
            'igdb_rating': game_data.get('igdb_rating'),
            'last_synced': timezone.now()
        }
    )
    game.genres.set(genres)
    game.platforms.set(platforms)


    if created or not game.slug:
        from django.utils.text import slugify
        base_slug = slugify(game.title)
        slug = base_slug
        counter = 1
        while Game.objects.filter(slug=slug).exclude(pk=game.pk).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        game.slug = slug
        game.save()

    return game

def search_and_import(query):
    results = igdb_client.search_games(query)
    games = []
    for game_data in results:
        game = import_game_from_igdb_data(game_data)
        games.append(game)
    return games

def sync_game(game):
    game_data = igdb_client.get_game_by_igdb_id(game.igdb_id)
    if game_data is None:
        return game
    return import_game_from_igdb_data(game_data)

