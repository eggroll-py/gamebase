from unittest.mock import patch
from decimal import Decimal
from app.models import Game, PriceEntry, PriceHistory
from app.price_service import update_price_for_game

STEAM_PRICE = {
    'store': 'steam', 'price': Decimal('9.75'), 'original_price': None,
    'on_sale': False, 'currency': 'EUR', 'url': 'https://store.steampowered.com/app/220/'
}

@patch('app.price_service.get_cached_price', return_value=None)
@patch('app.price_service.update_price_for_game', return_value=STEAM_PRICE)
class TestPriceServiceNewEntry:
    def test_update_price_for_game_creates_new_entry(self, mock_steam, mock_cache, db_session):
        game = Game(id=1, title='Half-Life 2', steam_id=220)
        db_session.add(game)
        db_session.commit()

        update_price_for_game(game, db_session)

        entries = db_session.query(PriceEntry).filter(PriceEntry.game_id == 1).all()
        history = db_session.query(PriceHistory).filter(PriceHistory.game_id == 1).all()

        assert len(entries) == 1
        assert len(history) == 1
        assert entries[0].price == Decimal('9.75')

    def test_update_price_for_existing_updates_price(self, mock_steam, mock_cache, db_session):
        game = Game(id=1, title='Half-Life 2', steam_id=220)
        old_entry = PriceEntry(game=game, store='steam', price=Decimal('19.99'), currency='EUR')

        db_session.add(game)
        db_session.add(old_entry)
        db_session.commit()

        update_price_for_game(game, db_session)

        entries = db_session.query(PriceEntry).filter(PriceEntry.game_id == 1).all()
        history = db_session.query(PriceHistory).filter(PriceHistory.game_id == 1).all()

        assert len(entries) == 1
        assert len(history) == 1
        assert entries[0].price == Decimal('9.75')


