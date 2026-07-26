from django.core.management import BaseCommand
from games.price_updater import update_prices_for_game
from games.models import Game

class Command(BaseCommand):
    help = 'Fetch prices for all games with known store IDs'

    def handle(self, *args, **options):
        games = Game.objects.filter(steam_id__isnull=False).all()
        self.stdout.write(f'Fetching prices for {games.count()} games')
        total_updated = 0

        for game in games:
            try:
                entries = update_prices_for_game(game)
                self.stdout.write(f'{game.title}: {len(entries)} price entries updated.')
                total_updated += len(entries)
            except Exception as e:
                self.stderr.write(f'ERROR: failed to fetch prices for {game.title}: {e}')

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {total_updated} price entries'))
