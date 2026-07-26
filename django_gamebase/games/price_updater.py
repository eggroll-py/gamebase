from games import price_clients
from .models import PriceEntry, Game
from django.utils import timezone

def update_prices_for_game(game):
    updated = []
    if game.steam_id is not None:
        price_data = price_clients.get_steam_price(game.steam_id)
        if price_data is not None:
            entry, _ = PriceEntry.objects.update_or_create(game=game, store='steam', defaults={
                'price': price_data['price'],
                'original_price': price_data.get('original_price'),
                'url': price_data['url'],
                'is_on_sale': price_data['on_sale'],
                'fetched_at': timezone.now()
            })
            updated.append(entry)

    if game.itad_slug is not None:
        for price_data in price_clients.get_itad_prices(game.itad_slug):
            entry, _ = PriceEntry.objects.update_or_create(game=game, store=price_data['store'], defaults={
                'price': price_data['price'],
                'original_price': price_data.get('original_price'),
                'url': price_data['url'],
                'is_on_sale': price_data['on_sale'],
                'fetched_at': timezone.now()
            })
            updated.append(entry)
    return updated

