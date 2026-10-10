from . import igdb_client
from .psn_client import resolve_psn_product_id
from .eshop_client import resolve_eshop_id
from .models import Game,Genre,Platform,Theme
from .embeddings import compute_embedding, build_embedding
from django.utils import timezone
from .choices import GameType

def import_game_from_igdb_data(game_data):
    if game_data.get('game_type') == GameType.SEASON:
        return None

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

    themes = []
    for theme_data in game_data.get('themes', []):
        theme, _ = Theme.objects.get_or_create(
            igdb_id = theme_data.get('igdb_id'),
            defaults = {
                'name': theme_data.get('name'),
                'slug' : theme_data.get('slug')
            }
        )
        themes.append(theme)

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

    bundle_ids = game_data.get('bundle_ids')
    bundles = Game.objects.filter(igdb_id__in=bundle_ids)


    game, created = Game.objects.update_or_create(
        igdb_id = game_data['igdb_id'],
        defaults = {
            'title': game_data['title'],
            'cover_url': game_data.get('cover_url'),
            'summary': game_data.get('summary', ''),
            'game_type': game_data.get('game_type'),
            'release_date': game_data.get('release_date'),
            'igdb_rating': game_data.get('igdb_rating'),
            'last_synced': timezone.now()
        }
    )
    game.genres.set(genres)
    game.platforms.set(platforms)
    game.themes.set(themes)
    game.bundles.set(bundles)

    parent_id = game_data.get('parent_game') or game_data.get('version_parent')
    parent = None
    if parent_id:
        parent = Game.objects.filter(igdb_id=parent_id).first() if parent_id else None
        if parent is None:
            parent_results = igdb_client.get_game_by_igdb_id(parent_id)
            if parent_results:
                parent = import_game_from_igdb_data(parent_results)
    game.parent_game = parent


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

    external_ids = igdb_client.get_external_ids(game.igdb_id)
    game.steam_id = external_ids['steam_id']

    if external_ids['psn_id'] is not None:
        game.psn_id = external_ids['psn_id']
        game.psn_product_id = resolve_psn_product_id(str(game.psn_id), game.title)

    eshop_data = resolve_eshop_id(game)
    game.eshop_id = eshop_data['eshop_id']
    game.eshop_verified = eshop_data['eshop_verified']
    game.eshop_url = eshop_data['eshop_url']
    game.save()

    game.embedding = compute_embedding(build_embedding(game))
    game.save(update_fields=['embedding'])
    return game

def search_and_import(query):
    results = igdb_client.search_games(query)
    games = []
    for game_data in results:
        game = import_game_from_igdb_data(game_data)
        if game is not None:
            games.append(game)
    return games

def sync_game(game):
    game_data = igdb_client.get_game_by_igdb_id(game.igdb_id)
    if game_data is None:
        return game
    return import_game_from_igdb_data(game_data)

def sync_existing_games():
    igdb_ids = Game.objects.filter(igdb_id__isnull=False).values_list('igdb_id', flat=True)
    games = igdb_client.get_games_by_igdb_ids(igdb_ids)
    results = []
    for game_data in games:
        game = import_game_from_igdb_data(game_data)
        if game is not None:
            results.append(game)

    return results



