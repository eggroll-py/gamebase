from app.database import SessionLocal
from app.models import Game, PriceEntry, PriceHistory
from app.price_clients import get_steam_price, get_psn_price, get_eshop_price
from app.cache import get_cached_price, set_cached_price
from datetime import datetime, timezone
from sqlalchemy import or_


def _write_price_entry(game: Game, price_data: dict, db, now ) -> None:
    existing_entry = db.query(PriceEntry).filter(PriceEntry.game_id == game.id, PriceEntry.store == price_data['store']).first()

    if existing_entry:
        existing_entry.price = price_data['price']
        existing_entry.original_price = price_data['original_price']
        existing_entry.on_sale = price_data['on_sale']
        existing_entry.currency = price_data['currency']
        existing_entry.url = price_data['url']
        existing_entry.fetched_at = now

    else:
        new_entry = PriceEntry(
            game_id=game.id,
            store=price_data['store'],
            price=price_data['price'],
            original_price=price_data['original_price'],
            is_on_sale=price_data['on_sale'],
            currency=price_data['currency'],
            url=price_data['url'],
            fetched_at=now
        )
        db.add(new_entry)

    history_row = PriceHistory(
        game_id=game.id,
        store=price_data['store'],
        price=price_data['price'],
        original_price=price_data['original_price'],
        is_on_sale=price_data['on_sale'],
        currency=price_data['currency'],
        recorded_at=now
    )
    db.add(history_row)

def update_price_for_game(game:Game, db) -> list[dict]:
    now = datetime.now(timezone.utc)
    all_prices = []

    steam_price = get_cached_price('steam', str(game.steam_id))

    if steam_price is None:
        steam_price = get_steam_price(game.steam_id)
        if steam_price is not None:
            _write_price_entry(game, steam_price, db, now)
            set_cached_price('steam', str(game.steam_id), steam_price)
    if steam_price is not None:
        all_prices.append(steam_price)


    psn_price = get_cached_price('psn', str(game.psn_product_id)) if game.psn_product_id else None
    if game.psn_product_id and psn_price is None:
        psn_price = get_psn_price(game.psn_product_id)
        if psn_price is not None:
            _write_price_entry(game, psn_price, db, now)
            set_cached_price('psn', game.psn_product_id, psn_price)
    if psn_price is not None:
        all_prices.append(psn_price)

    eshop_price = get_cached_price('eshop', str(game.eshop_id))
    if game.eshop_id and eshop_price is None:
        eshop_price = get_eshop_price(game.eshop_id, game.eshop_url)
        if eshop_price is not None:
            _write_price_entry(game, eshop_price, db, now)
            set_cached_price('eshop', game.eshop_id, eshop_price)
    if eshop_price is not None:
        all_prices.append(eshop_price)


    db.commit()
    return all_prices


def update_all_prices() -> list[dict]:
    db = SessionLocal()
    results = []

    try:
        games = db.query(Game).filter(or_(Game.steam_id.isnot(None), Game.psn_product_id.isnot(None), Game.eshop_id.isnot(None))).all()

        for game in games:
            price_list = update_price_for_game(game, db)

            for price_data in price_list:
                results.append({'game': game.title, **price_data})

    finally:
        db.close()

    return results









